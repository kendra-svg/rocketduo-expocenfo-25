import json
import os

from flask import Flask, Response, jsonify, request, send_file
from flask_cors import CORS
from service.llm_handler import frase_a_json
from utils.audio_exporter import subir_a_blob
from utils.date_calculator import calcular_fechas
from utils.tts_generator import generar_audio

app = Flask(__name__)
CORS(app) #Permite accesar al puerto 5000/frase desde el puerto de origen 63342
@app.route('/frase', methods=['POST']) #Al ser de tipo post, no se puede acceder a /frase desde el navegador
def procesar_frase():
    datos = request.json
    frase = datos.get("frase")
    
    #Para debuggear
    print("datos: " + str(datos))
    print("frase: " + str(frase))

    #Extraer recordatorio con llm_handler
    json_str = frase_a_json(frase)
    datos_json = json.loads(json_str)

    #Generar audio localmente con Azure Text-To-Speech usando tts_generator
    archivo_wav = datos_json["audio_filename"]
    generar_audio(datos_json["mensaje"], datos_json["audio_filename"])

    #Subir wav a Azure blob storage
    url_audio = subir_a_blob(archivo_wav, archivo_wav)
    datos_json["audio_url"] = url_audio  # agregar la URL al JSON

    #Calcular fechas de los recordatorios con date_calculator
    fecha_inicio, fecha_fin = calcular_fechas(
        datos_json["hora"],
        datos_json["dias"],
        datos_json["duracion_dias"]
    )

    datos_json["fecha_inicio"] = fecha_inicio
    datos_json["fecha_fin"] = fecha_fin

    #Para debuggear
    print("json_str" + str(json_str))
    print("datos_json" + str(datos_json))

    return jsonify(datos_json)


# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)
