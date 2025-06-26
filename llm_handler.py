import openai
from openai import OpenAI
from config import OPENAI_API_KEY


client = OpenAI(
    api_key=OPENAI_API_KEY
)

PROMPT_INICIAL = """
Actuá como un sistema que convierte frases en lenguaje natural en recordatorios de medicamentos estructurados. 
Devolvé la salida en formato JSON con los siguientes campos:
- hora (formato 24h: HH:MM)
- medicamento (nombre corto, en minúscula)
- mensaje (texto personalizado para el adulto mayor)
- audio_filename (nombre del archivo .mp3 sugerido, sin espacios)

Ejemplo de entrada:
'Mi abuela toma aspirina a las 6 p.m.'

Ejemplo de salida JSON:
{
  "hora": "18:00",
  "medicamento": "aspirina",
  "mensaje": "Abuela, son las seis. Hora de tomar aspirina.",
  "audio_filename": "aspirina_1800.mp3"
}
"""

frase = "Mi abuela toma enapril a las 8:00 am."

def frase_a_json(frase):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=0.2, #determina que tan creativo o arriesgado es el modelo al generar texto. 0.2 corresponde a poco aleatorio, responde de manera confiable y controlada
            messages=[
            {"role": "system", "content": PROMPT_INICIAL},
            {"role": "user", "content": frase},
            ]
        )
        contenido = response.choices[0].message.content.strip()
        return contenido
    except Exception as ex:
        return {"error": str(ex)}

print(frase_a_json(frase))
