import os

import requests
from config.config import AZURE_SPEECH_KEY


def generar_audio(texto, nombre_archivo):
    region = "eastus2"
    endpoint_url = "https://" + region + ".tts.speech.microsoft.com/cognitiveservices/v1"

    #headers que recibe el API de azure
    headers = {
        "Ocp-Apim-Subscription-Key": AZURE_SPEECH_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm" #representa un archivo de tipo mp3
    }

    #Si el texto está vacío, se cancela la generacion del archivo
    if not texto.strip():
        print("Texto vacío. Cancelando generación.")
        return False

    #Configurar la voz de azure a femenina en español
    ssml = (
        "<speak version='1.0' xml:lang='es-ES'>"
        "<voice xml:lang='es-ES' xml:gender='Female' name='es-CR-MariaNeural'>"
        f"{texto}"
        "</voice></speak>"
    )

    response = requests.post(endpoint_url, headers=headers, data=ssml.encode("utf-8"))

    #Para debuggear el endpoint
    #print("Endpoint cargado:", endpoint_url)
    #print("Content-Type recibido:", response.headers.get("Content-Type", "No definido"))

    #Si azure devuelve 200 (success) se crea el archivo
    if response.status_code == 200:
        content_type = response.headers.get("Content-Type", "")
        if content_type.startswith("audio/"):
            nombre_archivo_final = nombre_archivo if nombre_archivo.endswith(".wav") else nombre_archivo + ".wav"
            with open(nombre_archivo_final, "wb") as audio_file:
                audio_file.write(response.content)
                print("Audio generado correctamente")
            return True
        else:
            print("Azure respondió con contenido NO de audio. No se guarda el archivo.")
            print("Contenido recibido (primeros 200 caracteres):") #Para debuggear el contenido generado por Azure
            print(response.text[:200]) #Imprime los primero 200 caracteres del contenido del archivo
            return False
    #Si azure no devuelve 200 (success), no se genera el archivo y muestra el error para informacion del usuario
    else:
        print(f"Error generando audio: Respuesta: {response.text}")
        print(f"Error generando audio: Código: {response.status_code}")
        return False