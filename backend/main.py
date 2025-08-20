import json
from flask import Flask, jsonify, request
from flask_cors import CORS

# Rutas de negocio
from routes.clothing_api import router as clothing_router
from routes.scheduler_api import scheduler_bp
from routes.esp32_api import router as esp32_router

# Service del scheduler para inicializarlo (no para rutear)
from service.scheduler_service import init_scheduler, CONFIG

# Otros handlers ya existentes
from service.llm_handler import frase_a_json
from utils.audio_exporter import subir_a_blob
from utils.date_calculator import calcular_fechas
from utils.tts_generator import generar_audio

app = Flask(__name__)
CORS(app)

# Blueprints
app.register_blueprint(clothing_router)
app.register_blueprint(scheduler_bp)
app.register_blueprint(esp32_router)

@app.route("/frase", methods=["POST"])
def procesar_frase():
    datos = request.json or {}
    frase = datos.get("frase")

    print("datos:", datos)
    print("frase:", frase)

    json_str = frase_a_json(frase)
    datos_json = json.loads(json_str)

    archivo_wav = datos_json["audio_filename"]
    generar_audio(datos_json["mensaje"], archivo_wav)

    url_audio = subir_a_blob(archivo_wav, archivo_wav)
    datos_json["audio_url"] = url_audio

    fecha_inicio, fecha_fin = calcular_fechas(
        datos_json["hora"],
        datos_json["dias"],
        datos_json["duracion_dias"],
    )
    datos_json["fecha_inicio"] = fecha_inicio
    datos_json["fecha_fin"] = fecha_fin

    print("json_str:", json_str)
    print("datos_json:", datos_json)

    return jsonify(datos_json)


if __name__ == "__main__":
    # Arranca el scheduler (usa ENV o defaults del service)
    init_scheduler(
        app_debug=app.debug,
        # overrides opcionales:
        # every_min=15,
        # persona="Gabriel",
        # promedio=25,
        # margen=3,
        # incluir_temp=True,
        # lat=9.9281,
        # lon=-84.0907,
    )

    # Si el scheduler está activo, desactiva reloader para evitar 'not a socket' en Windows
    use_reloader = not CONFIG["enabled"]
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=use_reloader)
