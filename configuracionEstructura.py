from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/configuracion', methods=['GET'])
def obtener_configuracion_mock():
    configuracion_mock = {
        "hora": "18:00",
        "medicamento": "aspirina",
        "mensaje": "Abuela, son las seis. Hora de tomar aspirina.",
        "audio_filename": "aspirina_1800.mp3"
    }
    return jsonify(configuracion_mock)

if __name__ == '__main__':
    app.run(debug=True)
