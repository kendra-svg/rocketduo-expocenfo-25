from dotenv import load_dotenv
import os

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
NUMERO_CUIDADOR = os.getenv("NUMERO_CUIDADOR")


from twilio.rest import Client
from config import TWILIO_SID, TWILIO_TOKEN, TWILIO_PHONE_NUMBER, NUMERO_CUIDADOR

def enviar_sms(texto):
    try:
        # Crear cliente de Twilio con tus credenciales
        client = Client(TWILIO_SID, TWILIO_TOKEN)

        # Crear y enviar el mensaje
        mensaje = client.messages.create(
            body=texto,
            from_=TWILIO_PHONE_NUMBER,
            to=NUMERO_CUIDADOR
        )

        print("Mensaje enviado correctamente. SID:", mensaje.sid)
        return True

    except Exception as e:
        print("Error al enviar el mensaje:", e)
        return False

if __name__ == '__main__':
    texto_de_prueba = "Hola, este es un mensaje de prueba desde Twilio y Python"
    enviar_sms(texto_de_prueba)
