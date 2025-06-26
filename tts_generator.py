import requests
import os
from config import AZURE_SPEECH_KEY, AZURE_SPEECH_REGION

def generar_audio(texto, nombre_archivo):
    region = "eastus2"
    endpoint_url = "https://" + region + ".tts.speech.microsoft.com/cognitiveservices/v1"

    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-48khz-192kbitrate-mono-mp3" #representa un archivo de tipo wav
    }

    if not texto.strip():
        print("Texto vacío. Cancelando generación.")
        return False

    #Configurar la voz a femenina en español
    ssml = (
        "<speak version='1.0' xml:lang='es-ES'>"
        "<voice xml:lang='es-ES' xml:gender='Female' name='es-CR-MariaNeural'>"
        f"{texto}"
        "</voice></speak>"
    )

    response = requests.post(endpoint_url, headers=headers, data=ssml.encode("utf-8"))

    print("Endpoint cargado:", endpoint_url)
    print("Content-Type recibido:", response.headers.get("Content-Type", "No definido"))

    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("audio/"):
            nombre_archivo_final = nombre_archivo if nombre_archivo.endswith(".mp3") else nombre_archivo + ".mp3"
            with open(nombre_archivo, "wb") as audio_file:
                audio_file.write(response.content)
                print("Audio generado correctamente")
            return True
        else:
            print("Azure respondió con contenido NO de audio. No se guarda el archivo.")
            print("Contenido recibido (primeros 200 caracteres):")
            print(response.text[:200])
            return False
    else:
        print(f"Error generando audio: Respuesta: {response.text}")
        print(f"Error generando audio: Código: {response.status_code}")
        return False