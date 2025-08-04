# rocketduo-expocenfo-25

## Configuración del entorno de desarrollo

1. **Instalar dependencias necesarias**  
   Se utiliza `python-dotenv` para manejar las claves. \
   Se usa `flask` como microframework para crear el backend del proyecto. \
   Se usa `flask-cors` para permitir Cross-Origin-Resource-Sharing entre el backend y frontend. \
   Se utiliza `requests` para realizar solicitudes HTTP, por ejemplo, a la API de Azure Cognitive Services para generar audio. \
   Se usa `openai` para enviar prompts y recibir respuestas de modelos como GPT-3.5 de OpenAI. \
   Ejecutá el siguiente comando en tu entorno virtual o sistema:

   ```bash
   pip install python-dotenv
   pip install flask
   pip install flask-cors
   pip install requests
   pip install openai

2. **Crear archivo de configuración de entorno (.env)** \
Este archivo se utiliza para definir claves privadas como tokens de API.
Por ejemplo:

   ```bash
   OPENAI_API_KEY=clave_de_openai_aqui
   TWILIO_AUTH_TOKEN=token_de_twilio

3. **Crear archivo config.py para cargar las variables**
Este archivo lee las claves del archivo .env y las expone como constantes reutilizables en todo el proyecto:

   ```bash
   from dotenv import load_dotenv
   import os

   load_dotenv()

   OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

  4. **Proteger información sensible** \
  El archivo .env ha sido agregado al archivo .gitignore para evitar que las claves se suban al repositorio público.

## Estructura del Proyecto

```plaintext
rocketduo-expocenfo-25/
├── main.py                   # Punto de entrada del backend Flask
├── llm_handler.py            # Comunicación con OpenAI (LLM)
├── tts_generator.py          # Conversión de texto a audio con Azure
├── twilio_handler.py         # Envío de SMS con Twilio
├── config.py                 # Carga de variables desde .env
├── static/                   # HTML y JS del frontend
│   └── index.html
├── .env                      # Variables de entorno (ignorado por Git)
└── .gitignore                # Archivos que no se subirán al repositorio
```

## Descripción de los módulos
`main.py` \
Define las rutas y coordina los módulos auxiliares.

`llm_handler.py` \
Comunica con OpenAI para transformar frases en JSON.

`tts_generator.py` \
Convierte el mensaje del JSON en un archivo .mp3 con Azure.

`twilio_handler.py` \
Envía mensajes SMS si se presionan botones o se detecta voz.

`config.py` \
Carga las claves desde .env para que el resto de módulos las usen.

`configuracionEstructura.py`

Devuelve la configuración actual del recordatorio que debe utilizar el dispositivo ESP32 para reproducir el mensaje y activar la alarma.

## Componentes funcionales del sistema

### Uso del modelo de lenguaje (LLM)
- Se utiliza `gpt-3.5-turbo` con un prompt diseñado para extraer:
  - hora (`HH:MM`)
  - medicamento
  - mensaje para la persona adulta mayor
  - nombre del archivo `.mp3` generado

- Ejemplo de entrada:
  > Mi abuela toma aspirina a las 6 p.m.

- Ejemplo de salida:
```json
{
  "hora": "18:00",
  "medicamento": "aspirina",
  "mensaje": "Abuela, son las seis. Hora de tomar aspirina.",
  "audio_filename": "aspirina_1800.mp3"
}
```


### Text-to-Speech con Azure

- Se usa `es-CR-MariaNeural` como voz en español femenina.
- Formato de salida: `audio-48khz-192kbitrate-mono-mp3`
- El archivo se guarda con el nombre especificado en el JSON.


### Interfaz de Usuario (HTML)

- Entrada: campo de texto para frase en lenguaje natural.
- Envío: se realiza a través de `fetch('/frase')`.
- Respuesta:
  - Se muestra mensaje de espera
  - Luego mensaje `Audio configurado correctamente...`
- Diseño responsive, simple y accesible.


### Rutas API disponibles

| Método | Ruta             | Descripción                                         |
|--------|------------------|-----------------------------------------------------|
| POST   | `/frase`         | Recibe frase y devuelve JSON + genera audio        |
| GET    | `/configuracion` | Devuelve configuración (mock para ESP32)           |
| POST   | `/evento`        | Recibe eventos desde botones físicos del ESP32     |

### Flujo general del sistema

Este sistema permite transformar una frase escrita por el usuario en un recordatorio automatizado con audio que será reproducido por un dispositivo ESP32. A continuación se describe el flujo completo:

1. **Entrada del usuario**  
   El usuario escribe una frase en lenguaje natural (por ejemplo, “Mi abuela toma aspirina a las 6 p.m.”) desde la interfaz web.


2. **Envío al backend**  
   Esta frase se envía mediante una solicitud `POST` al endpoint `/frase` del backend, desarrollado con Flask.


3. **Procesamiento con LLM (OpenAI)**  
   El backend utiliza el módulo `llm_handler.py` para enviar la frase al modelo `gpt-3.5-turbo`, que genera un objeto JSON estructurado con los siguientes datos:
   - hora
   - medicamento
   - mensaje personalizado
   - nombre del archivo de audio a generar


4. **Generación de audio con Azure TTS**  
   El texto del mensaje es enviado al servicio de Text-to-Speech de Azure mediante el módulo `tts_generator.py`, y se genera un archivo `.mp3`.


5. **Respuesta al usuario**  
   La interfaz muestra un resumen de la configuración exitosa, incluyendo el mensaje, hora, medicamento y nombre del audio generado.


6. **Disponibilidad para el ESP32**  
   La configuración generada queda disponible para ser consultada por el ESP32 a través del endpoint `/configuracion`. El ESP32 descargará los eventos programados, reproducirá el audio a la hora indicada y encenderá luces LED como parte del recordatorio.


7. **Botones de emergencia** *(extra)*  
   Si se presiona alguno de los botones físicos (rojo, azul o amarillo), el ESP32 enviará un evento al backend mediante `/evento`, y el sistema usará `twilio_handler.py` para enviar un mensaje SMS al cuidador correspondiente.

## Componentes ESP32