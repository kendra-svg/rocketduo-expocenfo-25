from dotenv import load_dotenv
import os

load_dotenv()  #Esto carga el archivo .env

#Keys provenientes de archivo .env que es ignorado por github por temas de seguridad
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_ENDPOINT")

#Para usar las keys en otros archivos se deben importar de la siguiente manera (ejemplo): from config import OPENAI_API_KEY
# instalacion de paquetes
