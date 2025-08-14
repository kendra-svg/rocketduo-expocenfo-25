import os

from dotenv import load_dotenv

load_dotenv()  #Esto carga el archivo .env

#Keys provenientes de archivo .env que es ignorado por github por temas de seguridad
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TWILIO_PHONE_NUMBER_TO = os.getenv("TWILIO_PHONE_NUMBER_TO")
AZURE_STORAGE_CONTAINER_NAME = os.getenv("AZURE_STORAGE_CONTAINER_NAME")
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_COSMOS_DB_CONTAINER_NAME= os.getenv("AZURE_COSMOS_DB_CONTAINER_NAME")
AZURE_COSMOS_KEY= os.getenv("AZURE_COSMOS_KEY")
AZURE_COSMOS_URL= os.getenv("AZURE_COSMOS_URL")
AZURE_COSMOS_DATABASE_NAME= os.getenv("AZURE_COSMOS_DATABASE_NAME")


#Para usar las keys en otros archivos se deben importar de la siguiente manera (ejemplo): from config import OPENAI_API_KEY
# instalacion de paquetes
