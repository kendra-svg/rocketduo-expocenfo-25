from flask import Blueprint, request, jsonify
from twilio_handler import enviar_sms  # ejemplo de importación de tu módulo Twilio

evento_bp = Blueprint('evento', __name__)

@evento_bp.route('/evento', methods=['POST'])
def recibir_evento():
    data = request.json
    color = data.get('color')
    if not color:
        return jsonify({"error": "No se recibió el color"}), 400

    # Lógica para identificar el color y enviar mensaje
    if color.lower() == "rojo":
        enviar_sms("Mensaje para botón rojo")
    elif color.lower() == "azul":
        enviar_sms("Mensaje para botón azul")
    elif color.lower() == "amarillo":
        enviar_sms("Mensaje para botón amarillo")
    else:
        return jsonify({"error": "Color no reconocido"}), 400

    return jsonify({"status": "Mensaje enviado"}), 200
