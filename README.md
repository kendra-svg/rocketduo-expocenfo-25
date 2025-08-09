# rocketduo-expocenfo-25

# Configuración del entorno de desarrollo

1. **Instalar dependencias necesarias**  
   Se utiliza `python-dotenv` para manejar las claves. \
   Se usa `flask` como microframework para crear el backend del proyecto. \
   Se usa `flask-cors` para permitir Cross-Origin-Resource-Sharing entre el backend y frontend. \
   Se utiliza `requests` para realizar solicitudes HTTP, por ejemplo, a la API de Azure Cognitive Services para generar audio. \
   Se usa `openai` para enviar prompts y recibir respuestas de modelos como GPT-3.5 de OpenAI. \
   Se usa `twilio` para el envío de notificaciones a través de SMS en respuesta a eventos del ESP32. \
   Ejecutá el siguiente comando en tu entorno virtual o sistema:

   ```bash
   pip install python-dotenv flask flask-cors requests openai

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

# Estructura del Proyecto

```plaintext
rocketduo-expocenfo-25/
├── backend/
│   └── config
│        └── config.py           # Carga de variables desde .env
│   └── service
│        └── llm_handler.py      # Comunicación con OpenAI (LLM)
│        └── twilio_handler.py   # Envío de SMS con Twilio
│   └── utils
│        └── tts_generator.py    # Conversión de texto a audio con Azure
│   └── main.py                  # Punto de entrada del programa
├── esp32/audio
│   └── audio.ino          # Reproduccion de recordatorios via Bluetooth
├── node_modules
│   └── config.js          # Módulos que permiten el funcionamiento del programa.
├── static/                # HTML y JS del frontend
│   └── index.html
├── .env                   # Variables de entorno (ignorado por Git)
└── .gitignore             # Archivos que no se subirán al repositorio
```

# Descripción de los módulos
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

# Componentes funcionales del sistema

## Uso del modelo de lenguaje (LLM)
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


## Text-to-Speech con Azure

- Se usa `es-CR-MariaNeural` como voz en español femenina.
- Formato de salida: `audio-48khz-192kbitrate-mono-mp3`
- El archivo se guarda con el nombre especificado en el JSON.


## Interfaz de Usuario (HTML)

- Entrada: campo de texto para frase en lenguaje natural.
- Envío: se realiza a través de `fetch('/frase')`.
- Respuesta:
  - Se muestra mensaje de espera
  - Luego mensaje `Audio configurado correctamente...`
- Diseño responsive, simple y accesible.


# Rutas API disponibles

| Método | Ruta             | Descripción                                         |
|--------|------------------|-----------------------------------------------------|
| POST   | `/frase`         | Recibe frase y devuelve JSON + genera audio        |


# Flujo general del sistema

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


# Componentes ESP32

Este sistema de asistencia incluye un conjunto de componentes físicos conectados al microcontrolador ESP32. A continuación se detallan los principales elementos involucrados:

## Microcontrolador

- **ESP32 Dev Module**
  - Compatible con Wi-Fi y Bluetooth.
  - Procesamiento eficiente para tareas en tiempo real.
  - Interfaz UART para comunicación serial con la PC.

##  Sensores

- **Sensor de Temperatura y Humedad DHT11 o DHT22**
  - Permite medir el ambiente donde se encuentra la persona adulta mayor.
  - Estos datos pueden ser utilizados para enviar recordatorios como “ponerse un abrigo” o “hidratarse”.

## Actuadores

- **Botones físicos** (tipo push-button)
  - **Amarillo:** Indica que la persona tiene hambre.
  - **Azul:** Indica que se siente sola o triste.
  - **Rojo:** Indica que se siente enferma o necesita ayuda urgente.

  - Cada botón genera un evento que se reporta al backend vía `/evento` y se envía un SMS al cuidador.

- **Tira de LED RGB (por ejemplo, WS2812B o similar)**
  - Se enciende con colores según el evento o recordatorio.
  - Ayuda a captar visualmente la atención de la persona al momento del recordatorio.

##  Reproducción de audio

- **Dispositivo Bluetooth emparejado**
  - El ESP32 se conecta vía Bluetooth a un altavoz inalámbrico o parlante inteligente.
  - Los audios previamente generados (.mp3) se transmiten desde el ESP32 al dispositivo Bluetooth cuando llega la hora programada.
  - Esto evita la necesidad de almacenamiento local en tarjetas SD.

## Fuente de poder

- **Alimentación USB-C o batería LiPo**
  - Requiere una fuente de 5V con al menos 1A de salida estable.
  - Alternativamente puede conectarse a una batería para uso portátil.

---

Este conjunto de componentes convierte al ESP32 en un asistente físico capaz de reproducir recordatorios personalizados, reaccionar a eventos manuales y mantener contacto constante con el sistema backend.

##

# Integración del ESP32 al Sistema

Esta sección describe cómo el microcontrolador ESP32 se comunica con el backend Flask y ejecuta las tareas programadas, como reproducir audios, encender luces LED y enviar alertas por botón.

### Conectividad

- El ESP32 se conecta vía **Wi-Fi** a la red local donde se ejecuta el backend Flask.
- El backend expone rutas accesibles desde la red, como:
  
  ```
  http://<IP_LOCAL_DEL_SERVIDOR>:5000/configuracion
  ```
  
- Estas rutas permiten al ESP32 obtener configuraciones y reportar eventos.

### Comunicación con el Backend

- Al iniciar o cada cierto intervalo, el ESP32 consulta el endpoint:

  ```
  GET /configuracion
  ```

  Para obtener un listado de recordatorios estructurados en formato JSON.

- El ESP32 procesa la respuesta para:
  - Programar alarmas internas.
  - Reproducir audios a la hora indicada (previamente descargados o almacenados).
  - Encender luces LED como refuerzo visual.

- Si se presiona un botón físico (amarillo, azul o rojo), el ESP32 envía un evento al backend mediante:

  ```
  POST /evento
  ```

  El backend interpreta el evento y envía una alerta vía SMS utilizando Twilio.

### Alimentación y Despliegue

- El ESP32 puede alimentarse por:
  - **USB directo** desde una PC o cargador.
  - **Batería recargable Li-Ion** si se desea portabilidad.

- El hardware se puede montar en una caja simple que contenga:
  - El ESP32.
  - Tres botones de colores.
  - Una tira LED.
  - Un pequeño altavoz o módulo de audio.

#  Instalación y Configuración del Sistema

Esta sección detalla cómo preparar el entorno de desarrollo y ejecutar el sistema completo, incluyendo el backend, frontend y la interacción con el ESP32.

##  Requisitos Previos

- Python 3.8+
- pip
- Cuenta en OpenAI
- Cuenta en Azure Cognitive Services (con un recurso de Speech)
- Arduino IDE instalado
- Placa ESP32 DevKit
- Conexión a Internet

## Instalación del entorno Python

1. **Clonar el repositorio**

2. **Instalar dependencias necesarias**

```bash
pip install flask flask-cors python-dotenv openai requests twilio
```

3. **Crear archivo `.env` con las claves de API necesarias**

```bash
OPENAI_API_KEY=tu_clave_openai
AZURE_SPEECH_KEY=tu_clave_azure
AZURE_SPEECH_REGION=eastus2
```

4. **Agregar `.env` al archivo `.gitignore`**

```bash
.env
```

## Ejecutar el servidor Flask

```bash
python main.py
```

El servidor estará disponible por defecto en [http://localhost:5000](http://localhost:5000)

## Probar el frontend

1. Abrí `static/index.html` en tu navegador.

2. Ingresá una frase como:

```
Mi abuela toma aspirina a las 6 p.m.
```

3. Se generará el archivo `.mp3` con el mensaje personalizado y se mostrará el resumen de configuración.

## Preparar el ESP32

1. Abrí el Arduino IDE.
2. Seleccioná la placa: **ESP32 Dev Module**
3. Instalá la biblioteca `WiFi.h` si no está incluida.
4. Usá el monitor serial para ver la salida.
5. Cargá un sketch con conexión a Wi-Fi y solicitud al endpoint `/configuracion`.

## Verificación

Una vez conectado a Wi-Fi, el ESP32 debería poder consumir el endpoint `/configuracion` y mostrar en el monitor serial la configuración recibida.

##

# Consideraciones Técnicas
- El ESP32 actúa como cliente y consulta periódicamente al backend.
- La generación de audio se realiza de forma sincrónica antes de responder al cliente.
- Se usa una arquitectura modular para separar claramente los componentes.

# Recomendaciones de Uso
- **Conexión Wi-Fi:** asegurarse de que el ESP32 esté en la misma red que el backend durante las pruebas.

- **Audios generados:** los archivos .mp3 generados deben estar accesibles para el ESP32 (ya sea descargados o pregrabados).

- **Mensajes SMS:** el número de teléfono del cuidador debe estar configurado en el backend (en twilio_handler.py).

##

# ✅ MediAmigo - Asistente de Medicación listo para utilizar.


