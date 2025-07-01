"""
main.py
Este archivo contiene las rutas básicas que permiten al ESP32 comunicarse con el backend.

Autor: Steven Delgadillo
Fecha: Junio 2025
Descripción: API REST con dos rutas:
 - GET /configuracion: devuelve datos simulados de configuración.
 - POST /evento: recibe eventos del ESP32 (como presionar un botón).
"""
import json

from flask import Flask, request, jsonify
from llm_handler import frase_a_json
from tts_generator import generar_audio
from flask_cors import CORS

app = Flask(__name__)
CORS(app) #Permite accesar al puerto 5000/frase desde el puerto de origen 63342

# Ruta GET /configuracion con datos mockeados
@app.route('/configuracion', methods=['GET'])
def obtener_configuracion():


    configuracion_mock = {
        "umbral" : 50,
        "modo": "automatico",
        "frecuencia_actualizacion": 5
    }
    return jsonify(configuracion_mock), 200

"""
Devuelve una configuración simulada (mock) para que el ESP32
sepa cómo actuar. Por ejemplo, con qué frecuencia debe actualizar
sus sensores o en qué modo debe operar.
"""

# Ruta POST /evento para recibir datos simulados del ESP32

""""
- Recibe datos en formato JSON (por ejemplo, tipo de evento o botón presionado).
- Imprime esos datos en la consola para pruebas o monitoreo.
- Responde con un mensaje de confirmación.


Ejemplo de JSON esperado:
    {
        "tipo": "boton",
        "color": "rojo"
    }
"""

@app.route('/evento', methods=['POST'])
def recibir_evento():
    datos = request.json
    print("Evento recibido:", datos)
    return jsonify({"mensaje": "Evento recibido correctamente"}), 201


@app.route('/frase', methods=['POST']) #Al ser de tipo post, no se puede acceder a /frase desde el navegador
def procesar_frase():
    datos = request.json
    frase = datos.get("frase")

    json_str = frase_a_json(frase)
    datos_json = json.loads(json_str)

    generar_audio(datos_json["mensaje"], datos_json["audio_filename"])

    return jsonify(datos_json)

# Iniciar el servidor
if __name__ == '__main__':
    app.run(debug=True)