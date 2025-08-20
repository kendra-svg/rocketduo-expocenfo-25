from flask import Blueprint, make_response
from datetime import datetime
from zoneinfo import ZoneInfo
from backend.service.cosmos_handler import cosmos_handler
import pygame
import requests
from io import BytesIO
import time, json, hashlib, threading
from flask import request, jsonify
from service.twilio_handler import enviar_sms

router = Blueprint("esp32_api", __name__, url_prefix="/api/esp32")

# Inicializar pygame para reproducción de audio
try:
    pygame.mixer.init()
    print("🎵 Sistema de audio inicializado correctamente")
except Exception as e:
    print(f"⚠️ Error inicializando audio: {e}")

# Zona horaria CR
TZ_CR = ZoneInfo("America/Costa_Rica")



# === Caché en memoria ===
CACHE_TTL = 60  # segundos (ajusta según necesites)
CONFIG_CACHE = {
    "body": None,   # bytes
    "etag": None,   # str
    "ts": 0.0,      # epoch seconds
}
_CACHE_LOCK = threading.Lock()

def _build_config_body():
    """
    Obtiene recordatorios del origen (p.ej., Cosmos), los normaliza
    y devuelve (body_bytes, etag_str). Usa sort_keys para ETag estable.
    """
    recordatorios = cosmos_handler.obtener_recordatorios_activos()
    payload = [{
        "id": r.get("id"),
        "quien": r.get("quien"),
        "hora": r.get("hora"),
        "medicamento": r.get("medicamento"),
        "mensaje": r.get("mensaje"),
        "audio_url": r.get("audio_url"),
        "activo": r.get("activo", True),
    } for r in recordatorios]

    body = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    etag = hashlib.md5(body).hexdigest()
    return body, etag

def _get_cached_config():
    """
    Devuelve (body, etag) desde caché si está fresca; si no, la regenera.
    Si el origen falla y hay copia, usa la copia vieja; si no hay copia, relanza el error.
    """
    now = time.time()
    with _CACHE_LOCK:
        is_stale = (CONFIG_CACHE["body"] is None) or (now - CONFIG_CACHE["ts"] > CACHE_TTL)
        if not is_stale:
            return CONFIG_CACHE["body"], CONFIG_CACHE["etag"]

        try:
            body, etag = _build_config_body()
            CONFIG_CACHE.update({"body": body, "etag": etag, "ts": now})
            return body, etag
        except Exception as e:
            # Si falla el origen y hay copia, devolvemos la copia vieja
            if CONFIG_CACHE["body"] is not None:
                return CONFIG_CACHE["body"], CONFIG_CACHE["etag"]
            # Si no hay copia previa, no podemos responder
            raise


# Agregar este endpoint al archivo esp32_api.py

@router.post("/evento")
def recibir_estado_botones():
    """POST /api/esp32/estado - Recibe estado de botones y envía SMS"""
    try:
        datos = request.get_json(silent=True) or {}

        # Obtener datos del botón
        boton = datos.get("boton", "")
        quien = datos.get("quien", "Adulto Mayor")
        timestamp = datos.get("timestamp", datetime.now().isoformat())


        # Enviar SMS según el botón presionado
        if boton == "ROJO" or boton == "EMERGENCIA_MEDICA":
            enviar_sms_boton("EMERGENCIA", quien)
        elif boton == "AZUL" or boton == "TRISTEZA_SOLEDAD":
            enviar_sms_boton("TRISTEZA", quien)
        elif boton == "AMARILLO" or boton == "HAMBRE":
            enviar_sms_boton("HAMBRE", quien)

        return jsonify({
            "status": "received",
            "mensaje": "Estado de botón procesado",
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


def enviar_sms_boton(tipo, quien):
    """Envía SMS según el tipo de botón"""
    try:

        if tipo == "EMERGENCIA":
            mensaje = f"🚨 EMERGENCIA MÉDICA\n{quien} presionó el botón rojo\nVerificar inmediatamente"
        elif tipo == "TRISTEZA":
            mensaje = f"💙 ALERTA EMOCIONAL\n{quien} presionó el botón azul\nNecesita compañía"
        elif tipo == "HAMBRE":
            mensaje = f"🍽️ SOLICITUD DE COMIDA\n{quien} presionó el botón amarillo\nTiene hambre"
        else:
            return

        exito = enviar_sms(mensaje)
        print(f"📱 SMS enviado: {'✅' if exito else '❌'}")

    except Exception as e:
        print(f"❌ Error enviando SMS: {e}")

@router.get("/siguiente-audio")
def siguiente_audio():
    quien = request.args.get("quien")
    hora = request.args.get("hora")  # 'HH:MM'
    if not quien or not hora:
        return jsonify({"detalle": "Faltan parametros 'quien' y/o 'hora'"}), 400

    recordatorios = cosmos_handler.obtener_recordatorios_por_persona(quien)

    candidatos = [
        r for r in recordatorios
        if r.get("activo", True) and r.get("hora") == hora
    ]
    if not candidatos:
        return jsonify({"detalle": "No hay recordatorio para esta hora"}), 404

    def _prio(rec):
        return (rec.get("prioridad", 0), rec.get("fecha_creacion", ""))

    candidatos.sort(key=_prio, reverse=True)
    r = candidatos[0]

    return jsonify({
        "recordatorio_id": r.get("id"),
        "hora": r.get("hora"),
        "audio_url": r.get("audio_url"),
        "mensaje": r.get("mensaje"),
    }), 200


@router.get("/agenda")
def agenda():
    quien = request.args.get("quien")
    if not quien:
        return jsonify({"detalle": "Falta parametro 'quien'"}), 400

    now_cr = datetime.now(TZ_CR)
    hoy_str = now_cr.strftime("%Y-%m-%d")
    hhmm_now = now_cr.strftime("%H:%M")

    recordatorios = cosmos_handler.obtener_recordatorios_por_persona(quien)

    def aplica_hoy(rec) -> bool:
        if not rec.get("activo", True):
            return False
        fi = rec.get("fecha_inicio")
        ff = rec.get("fecha_fin")
        if fi and hoy_str < fi:
            return False
        if ff not in (None, 0) and hoy_str > ff:
            return False
        return True

    futuros = [
        {
            "recordatorio_id": r.get("id"),
            "hora": r.get("hora"),
            "audio_url": r.get("audio_url"),
            "mensaje": r.get("mensaje"),
        }
        for r in recordatorios
        if aplica_hoy(r) and r.get("hora") >= hhmm_now
    ]
    futuros.sort(key=lambda x: x["hora"])
    return jsonify({"recordatorios": futuros}), 200


@router.post("/ack-reproduccion")
def ack_reproduccion():
    data = request.get_json(silent=True) or {}
    recordatorio_id = (data.get("recordatorio_id") or "").strip()
    quien = (data.get("quien") or "").strip()
    timestamp = data.get("timestamp")
    if not recordatorio_id or not quien:
        return jsonify({"detalle": "recordatorio_id y quien son obligatorios"}), 400
    print(f"[ACK] quien={quien} recordatorio_id={recordatorio_id} ts={timestamp}")
    return jsonify({"ok": True}), 200


@router.get("/config")
def get_esp32_config():
    try:
        body, etag = _get_cached_config()
    except Exception as e:
        # Sin caché previa y el origen falló
        return jsonify({"error": f"config unavailable: {e}"}), 500

    inm = request.headers.get("If-None-Match", "")
    if inm == etag:
        resp = make_response("", 304)
    else:
        resp = make_response(body, 200)
        resp.headers["Content-Type"] = "application/json; charset=utf-8"

    # ETag siempre presente
    resp.headers["ETag"] = etag
    # Orientativo para clientes: sirve 60s y permite 30s de revalidación perezosa
    resp.headers["Cache-Control"] = "private, max-age=60, stale-while-revalidate=30"
    return resp



@router.post("/play-audio")
def play_audio_on_server():
    """Recibe comando del ESP32 para reproducir audio en la computadora servidor."""
    try:
        datos = request.get_json(silent=True) or {}
        audio_url = datos.get("audio_url", "").strip()
        mensaje = datos.get("mensaje", "")
        medicamento = datos.get("medicamento", "")
        dispositivo = datos.get("dispositivo", "ESP32_MediAmigo")
        timestamp = datos.get("timestamp", datetime.now().isoformat())

        print("===== COMANDO DE REPRODUCCIÓN RECIBIDO =====")
        print(f"Dispositivo: {dispositivo}")
        print(f"Timestamp: {timestamp}")
        print(f"Medicamento: {medicamento}")
        print(f"Mensaje: {mensaje}")
        print(f"Audio URL: {audio_url[:60]}{'...' if len(audio_url) > 60 else ''}")
        print("=" * 50)

        if not audio_url:
            return jsonify({"error": "URL de audio requerida", "status": "failed"}), 400

        def reproducir_audio_async():
            try:
                print("Iniciando descarga y reproducción...")
                response = requests.get(audio_url, timeout=30)
                response.raise_for_status()
                print(f"Audio descargado: {len(response.content)} bytes")
                audio_data = BytesIO(response.content)
                pygame.mixer.music.load(audio_data)
                pygame.mixer.music.play()
                print("Reproduciendo audio en la computadora...")
                while pygame.mixer.music.get_busy():
                    pygame.time.wait(100)
                print("¡Audio reproducido exitosamente!")
                print(f"Recordatorio completado: {medicamento}")
            except requests.exceptions.RequestException as e:
                print(f"Error descargando audio: {e}")
            except pygame.error as e:
                print(f"Error de pygame: {e}")
            except Exception as e:
                print(f"Error general reproduciendo audio: {e}")

        threading.Thread(target=reproducir_audio_async, daemon=True).start()

        return jsonify({
            "status": "success",
            "message": "Audio enviado para reproducción",
            "dispositivo": dispositivo,
            "medicamento": medicamento,
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        print(f"Error en endpoint play-audio: {e}")
        return jsonify({"error": str(e), "status": "failed"}), 500


@router.get("/test")
def test_connection():
    return jsonify({
        "status": "ok",
        "message": "ESP32 API funcionando correctamente",
        "endpoints": [
            "/api/esp32/config - Obtener recordatorios",
            "/api/esp32/play-audio - Reproducir audio",
            "/api/esp32/siguiente-audio - Próximo recordatorio",
            "/api/esp32/agenda - Agenda del día",
            "/api/esp32/test - Probar conexión"
        ],
        "timestamp": datetime.now().isoformat()
    }), 200
