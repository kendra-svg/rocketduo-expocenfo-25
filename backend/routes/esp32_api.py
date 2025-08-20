from flask import Blueprint, request, jsonify
from datetime import datetime
from zoneinfo import ZoneInfo
from service.cosmos_handler import cosmos_handler

router = Blueprint("esp32_api", __name__, url_prefix="/api/esp32")

# Usamos timezone solo para "hoy" y ordenar; tu lógica sigue siendo naive
TZ_CR = ZoneInfo("America/Costa_Rica")

@router.get("/siguiente-audio")
def siguiente_audio():
    """
    Devuelve el audio a reproducir para una hora exacta.

    Parámetros de consulta:
        quien (str): Identificador de la persona.
        hora (str): Hora en formato 'HH:MM'.

    Respuestas:
        200: JSON con datos del recordatorio.
        400: Faltan parámetros.
        404: No hay recordatorio para esa hora.
    """
    quien = request.args.get("quien")
    hora  = request.args.get("hora")  # 'HH:MM'

    if not quien or not hora:
        return jsonify({"detalle": "Faltan parametros 'quien' y/o 'hora'"}), 400

    # Trae solo la partición de esa persona (rápido)
    recordatorios = cosmos_handler.obtener_recordatorios_por_persona(quien)

    # Coincidencia exacta por hora y activos
    candidatos = [
        r for r in recordatorios
        if r.get("activo", True) and r.get("hora") == hora
    ]

    if not candidatos:
        return jsonify({"detalle": "No hay recordatorio para esta hora"}), 404

    # Si hay varios, prioriza por 'prioridad' (desc) y luego por fecha_creacion (desc)
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
    """
    Devuelve los próximos recordatorios activos del día para una persona.

    Parámetros de consulta:
        quien (str): Identificador de la persona.

    Lógica:
        - Filtra por 'quien'
        - Considera solo recordatorios activos
        - Valida rango de fechas si existen 'fecha_inicio'/'fecha_fin'
        - Devuelve recordatorios desde la hora actual en adelante

    Respuestas:
        200: JSON con lista de recordatorios.
        400: Falta parámetro.
    """
    quien = request.args.get("quien")
    if not quien:
        return jsonify({"detalle": "Falta parametro 'quien'"}), 400

    now_cr = datetime.now(TZ_CR)
    hoy_str = now_cr.strftime("%Y-%m-%d")
    hhmm_now = now_cr.strftime("%H:%M")

    recordatorios = cosmos_handler.obtener_recordatorios_por_persona(quien)

    def aplica_hoy(rec) -> bool:
        """
        Determina si el recordatorio aplica para hoy y está activo.
        """
        if not rec.get("activo", True):
            return False
        fi = rec.get("fecha_inicio")  # "YYYY-MM-DD" o None
        ff = rec.get("fecha_fin")     # "YYYY-MM-DD" o None/0
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

    # Ordenar por hora ascendente
    futuros.sort(key=lambda x: x["hora"])

    return jsonify({"recordatorios": futuros}), 200

@router.post("/ack-reproduccion")
def ack_reproduccion():
    """
    Recibe la confirmación de que un audio fue reproducido (telemetría).

    Body JSON:
        recordatorio_id (str): UUID del recordatorio.
        quien (str): Identificador de la persona.
        timestamp (str, opcional): Fecha/hora de reproducción.

    Respuestas:
        200: Confirmación OK.
        400: Body inválido.

    Nota:
        Actualmente solo registra en consola; no persiste en base de datos.
    """
    data = request.get_json(silent=True) or {}
    recordatorio_id = (data.get("recordatorio_id") or "").strip()
    quien = (data.get("quien") or "").strip()
    timestamp = data.get("timestamp")  # opcional

    if not recordatorio_id or not quien:
        return jsonify({"detalle": "recordatorio_id y quien son obligatorios"}), 400

    print(f"[ACK] quien={quien} recordatorio_id={recordatorio_id} ts={timestamp}")
    return jsonify({"ok": True}), 200