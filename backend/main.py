import json
import os

from flask import Flask, Response, jsonify, request, send_file
from flask_cors import CORS
from service.llm_handler import frase_a_json
from utils.tts_generator import generar_audio

app = Flask(__name__)
CORS(app) #Permite accesar al puerto 5000/frase desde el puerto de origen 63342
@app.route('/frase', methods=['POST']) #Al ser de tipo post, no se puede acceder a /frase desde el navegador
def procesar_frase():
    datos = request.json
    frase = datos.get("frase")

    json_str = frase_a_json(frase)
    datos_json = json.loads(json_str)

    generar_audio(datos_json["mensaje"], datos_json["audio_filename"])

    return jsonify(datos_json)


AUDIO_FILE = "C:/Users/ricar/OneDrive/Escritorio/Arduino/rocketduo-expocenfo-25/aspirina_1800.mp3"

@app.route("/audio", methods=["GET"])
def serve_audio():
 
    if os.path.exists(AUDIO_FILE):
        print("Audio encontrado")
        return send_file(AUDIO_FILE, mimetype="audio/mpeg")
    else:
        print("Audio no encontrado")
        return Response("Audio file not found", status=404)
    
print(AUDIO_FILE)

print(os.path.exists("C:/Users/ricar/OneDrive/Escritorio/Arduino/rocketduo-expocenfo-25/aspirina_1800.mp3"))

# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)
