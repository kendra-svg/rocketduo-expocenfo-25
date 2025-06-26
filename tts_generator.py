import requests
import os
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION

def generar_audio(texto, nombre_archivo):
    region = "eastus2"
    endpoint_url = "https://" + region + ".api.cognitive.microsoft.com/sts/v1.0/issuetoken"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm" #representa un archivo de tipo wav
    }

    #Configurar la voz a femenina en español
    ssml = f"<speak version='1.0' xml:lang='es-ES'><voice xml:lang='es-ES' xml:gender='Female' name='es-ES-ElviraNeural'>{texto}</voice></speak>"

    response = requests.post(endpoint_url, headers=headers, data=ssml.encode("utf-8"))

    print("Endpoint cargado:", endpoint_url)

    if response.status_code == 200:
        with open(nombre_archivo, "wb") as audio_file:
            audio_file.write(response.content)
            print("Audio generado correctamente")
        return True
    else:
        print(f"Error generando audio: {response.status_code}, {response.text}")
        return False