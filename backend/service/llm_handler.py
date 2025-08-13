from config.config import OPENAI_API_KEY
from openai import OpenAI

client = OpenAI(
    api_key=OPENAI_API_KEY
)

PROMPT_INICIAL = """
Actuá como un sistema que convierte frases en lenguaje natural en recordatorios de medicamentos estructurados.
Devuelve siempre la salida en formato JSON con los siguientes campos:
- quien: nombre o descripción de la persona que debe tomar el medicamento (en el mismo formato que aparece en el texto).
- hora (formato 24h: "HH:MM")
- medicamento (nombre corto, en minúscula)
- mensaje (texto personalizado para el adulto mayor, usando la hora en palabras y el nombre del medicamento)
- audio_filename (nombre del archivo .wav sugerido, en minúsculas, sin espacios, con el formato medicamento_hhmm.mp3)
- frecuencia (texto tal como lo indica el usuario, ej. "dos veces al día", "cada 8 horas")
- dias (lista en minúscula de los días en que debe tomarse, ej. ["lunes","miércoles","viernes"], o ["todos"] si es diario)
- duracion_dias (número entero: si el usuario indica “durante X días” usa ese número; si no hay duración, poner 0)

Reglas para calcular fecha_inicio y fecha_fin:

- Usa la fecha actual del momento en que se procesa.
- Si la hora indicada todavía no ha pasado hoy y hoy está en la lista de dias, fecha_inicio es hoy.
- Si la hora indicada todavía no ha pasado hoy pero hoy no está en dias, busca el próximo día válido en la lista.
- Si la hora indicada ya pasó hoy, busca el siguiente día válido en la lista (puede ser mañana u otro según dias).
- Si duracion_dias > 0, fecha_fin es fecha_inicio + duracion_dias - 1 días.
- Si duracion_dias = 0, significa tratamiento permanente y fecha_fin será 0.

Ejemplos de entrada y salida:

Entrada:
"Mi abuela toma aspirina 100 mg a las 8 a.m., dos veces al día, lunes a viernes."
Salida:

{
  "hora": "08:00",
  "medicamento": "aspirina",
  "mensaje": "Abuela, son las ocho. Hora de tomar aspirina.",
  "audio_filename": "aspirina_0800.wav",
  "frecuencia": "dos veces al día",
  "dias": ["lunes","martes","miércoles","jueves","viernes"],
  "duracion_dias": 0
}

Entrada:
"Olga debe tomar ibuprofeno 500 mg a las 8 a.m., cada 12 horas, durante 4 días."
Salida:

{
  "hora": "08:00",
  "medicamento": "ibuprofeno",
  "mensaje": "Olga, son las ocho. Hora de tomar ibuprofeno.",
  "audio_filename": "ibuprofeno_0800.wav",
  "frecuencia": "cada 12 horas",
  "dias": ["todos"],
  "duracion_dias": 4
}
"""



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


