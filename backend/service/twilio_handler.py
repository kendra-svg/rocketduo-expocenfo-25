from dotenv import load_dotenv
import os
import sys

# Agregar la carpeta raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.config.config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, TWILIO_PHONE_NUMBER_TO
from twilio.rest import Client


def enviar_sms(texto):
    try:
        # Crear cliente de Twilio con tus credenciales
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Crear y enviar el mensaje
        mensaje = client.messages.create(
            body=texto,
            from_=TWILIO_PHONE_NUMBER,
            to=TWILIO_PHONE_NUMBER_TO
        )

        print("Mensaje enviado correctamente. SID:", mensaje.sid)
        return True

    except Exception as e:
        print("Error al enviar el mensaje:", e)
        return False

if __name__ == '__main__':
    texto_de_prueba = "Hola, este es un mensaje de prueba desde Twilio y Python"
    enviar_sms(texto_de_prueba)