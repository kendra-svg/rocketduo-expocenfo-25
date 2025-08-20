import os
import uuid
from datetime import datetime

from service.cosmos_handler import (
    cosmos_handler,
    guardar_alerta_clima as ch_guardar_alerta_clima,
    obtener_ultima_alerta as ch_obtener_ultima_alerta,
)
from utils.weather_service import obtener_temp_actual
from utils.tts_generator import generar_audio  # True/False, escribe WAV
from utils.audio_exporter import subir_a_blob

# === CONFIGURACIÓN DE DIRECTORIOS ===
# Ruta base -> backend/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "esp32", "audio")

# Crear carpeta si no existe
os.makedirs(AUDIO_DIR, exist_ok=True)

LAT_DEFECTO = 9.9281
LON_DEFECTO = -84.0907


def _mensaje_y_archivo(categoria: str, temp: float, incluir_temp: bool) -> tuple[str, str]:
    """Genera el mensaje de alerta y nombre de archivo WAV según categoría."""
    if categoria == "frio":
        mensaje = (
            f"Está haciendo frío, ponte un abrigo. Temperatura actual {temp:.1f}°C."
            if incluir_temp else
            "Está haciendo frío, ponte un abrigo."
        )
        archivo = f"frio_{uuid.uuid4().hex[:6]}.wav"
    else:  # "calor"
        mensaje = (
            f"Está haciendo calor, viste ropa ligera. Temperatura actual {temp:.1f}°C."
            if incluir_temp else
            "Está haciendo calor, viste ropa ligera."
        )
        archivo = f"calor_{uuid.uuid4().hex[:6]}.wav"
    return mensaje, archivo


def generar_alerta_y_guardar(
    persona: str,
    promedio: float,
    margen: float = 4.0,
    incluir_temp: bool = False,
    lat: float = LAT_DEFECTO,
    lon: float = LON_DEFECTO,
) -> dict:
    """
    MODO ESTRICTO:
      - Dentro de (promedio±margen) => SIN alerta (no se guarda nada).
      - Fuera de rango => generar WAV, subir a Blob (ambos obligatorios) y guardar en Cosmos.
      - Si falla TTS o Blob => error (no guarda).
    """
    temp = obtener_temp_actual(lat, lon)

    # Decisión: dentro del margen => no hay alerta
    if (promedio - margen) < temp < (promedio + margen):
        print("[INFO] Sin alerta: la temperatura está dentro del rango normal.")
        return {
            "debe_reproducir": False,
            "estado": "normal",
            "temperatura": float(temp),
            "promedio": float(promedio),
            "margen": float(margen),
        }

    # Fuera del rango => hay alerta
    categoria = "frio" if temp <= (promedio - margen) else "calor"
    mensaje, archivo = _mensaje_y_archivo(categoria, temp, incluir_temp)

    # === Paso 1: Generar audio local (OBLIGATORIO) ===
    local_path = os.path.join(AUDIO_DIR, archivo)
    print(f"[DEBUG] Generando audio en {local_path}")
    ok_audio = generar_audio(mensaje, local_path)
    if not ok_audio:
        print("[ERROR] No se pudo generar el audio TTS. No se guardará alerta.")
        return {
            "error": "ERROR_TTS",
            "detalle": "No se pudo generar el audio de la alerta.",
            "categoria": categoria,
            "temperatura": float(temp),
            "promedio": float(promedio),
            "margen": float(margen),
            "mensaje": mensaje,
        }

    # === Paso 2: Subir a Blob y obtener URL (OBLIGATORIO) ===
    try:
        print(f"[DEBUG] Subiendo {local_path} a Blob Storage.")
        url_audio = subir_a_blob(local_path, archivo)
    except Exception as e:
        print(f"[ERROR] Falló la subida a Blob: {e}")
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
                print(f"[CLEANUP] WAV eliminado tras fallo de subida: {local_path}")
        except Exception as e2:
            print(f"[WARN] No se pudo borrar {local_path}: {e2}")
        return {
            "error": "ERROR_BLOB",
            "detalle": "No se pudo subir el audio a Blob Storage.",
            "categoria": categoria,
            "temperatura": float(temp),
            "promedio": float(promedio),
            "margen": float(margen),
            "mensaje": mensaje,
        }
    finally:
        # Siempre limpiar el WAV local si existe
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
                print(f"[CLEANUP] WAV eliminado: {local_path}")
        except Exception as e:
            print(f"[WARN] No se pudo borrar {local_path}: {e}")

    if not url_audio:
        print("[ERROR] Subida a Blob no devolvió URL. No se guardará alerta.")
        return {
            "error": "ERROR_URL_AUDIO",
            "detalle": "No se obtuvo la URL del audio.",
            "categoria": categoria,
            "temperatura": float(temp),
            "promedio": float(promedio),
            "margen": float(margen),
            "mensaje": mensaje,
        }

    # === Paso 3: Guardar en Cosmos (PK = /quien) con url_audio ===
    alerta_doc = {
        # Importante: el contenedor usa /quien como partition key
        "quien": persona,
        "categoria": categoria,                 # 'frio' | 'calor'
        "temperatura_actual": float(temp),
        "promedio": float(promedio),
        "margen": float(margen),
        "mensaje": mensaje,
        "url_audio": url_audio,                 # obligatorio en modo estricto
        # 'tipo', 'activo', 'creado_en' e 'id' los setea el helper si no vienen
    }
    try:
        saved = ch_guardar_alerta_clima(cosmos_handler.container, alerta_doc)
    except Exception as e:
        print(f"[ERROR] Cosmos guardado falló: {e}")
        return {
            "error": "ERROR_COSMOS",
            "detalle": "No se pudo guardar el documento en CosmosDB.",
            "categoria": categoria,
            "temperatura": float(temp),
            "promedio": float(promedio),
            "margen": float(margen),
            "mensaje": mensaje,
        }

    # Respuesta OK (la API responderá 201 si ve id_documento)
    return {
        "debe_reproducir": True,
        "id_documento": saved.get("id"),
        "categoria": categoria,
        "temperatura": float(temp),
        "promedio": float(promedio),
        "margen": float(margen),
        "mensaje": mensaje,
        "url_audio": url_audio,
        "estado": "alerta_guardada",
    }


def obtener_ultima_alerta(persona: str, categoria: str | None = None) -> dict | None:
    """
    Devuelve la última alerta de clima para 'persona' (quien).
    Si 'categoria' es 'frio' o 'calor', filtra por ella; si None, devuelve la última de cualquier tipo.
    """
    if categoria and categoria not in ("frio", "calor"):
        print(f"[WARN] categoria inválida: {categoria}")
        return None

    try:
        doc = ch_obtener_ultima_alerta(cosmos_handler.container, quien=persona, categoria=categoria)
    except Exception as e:
        print(f"[ERROR] obtener_ultima_alerta helper falló: {e}")
        return None

    if not doc:
        return None

    # Normalización de salida
    return {
        "id_documento": doc.get("id"),
        "quien": doc.get("quien"),
        "categoria": doc.get("categoria"),
        "temperatura": doc.get("temperatura_actual"),
        "promedio": doc.get("promedio"),
        "margen": doc.get("margen"),
        "mensaje": doc.get("mensaje"),
        "url_audio": doc.get("url_audio"),
        "creado_en": doc.get("creado_en"),
    }
