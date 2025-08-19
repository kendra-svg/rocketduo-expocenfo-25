from flask import Blueprint, request, jsonify
from utils.weather_service import obtener_temp_actual

router = Blueprint("weather_api", __name__, url_prefix="/api/weather")

# San José, Costa Rica (fallback si no pasan lat/lon)
DEFAULT_LAT = 9.9281
DEFAULT_LON = -84.0907

@router.get("/temperatura")
def temperatura():
    """
    GET /api/weather/temperatura?lat=9.9281&lon=-84.0907
    Si no se envían lat/lon, usa San José, CR por defecto.
    Respuesta: { "lat": ..., "lon": ..., "units": "C", "temperatura": <float> }
    """
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if lat is None or lon is None:
        lat, lon = DEFAULT_LAT, DEFAULT_LON

    try:
        temp_c = obtener_temp_actual(lat, lon, unidades="metric", lang="es")
        return jsonify({
            "lat": lat,
            "lon": lon,
            "units": "C",
            "temperatura": temp_c
        }), 200
    except Exception as e:
        # 502: bad gateway (error al consultar servicio externo)
        return jsonify({
            "detalle": "No se pudo obtener la temperatura",
            "error": str(e)
        }), 502
