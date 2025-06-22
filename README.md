# rocketduo-expocenfo-25

## Configuración del entorno de desarrollo

1. **Instalar dependencias necesarias**  
   De momento solo se requiere `python-dotenv` para manejar las claves.  
   Ejecutá el siguiente comando en tu entorno virtual o sistema:

   ```bash
   pip install python-dotenv

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

1. **Envio SMS a cuidador ejecutado en python**  
    Este módulo permite el envío de mensajes SMS automáticos mediante la plataforma Twilio. La funcionalidad está pensada para ser invocada por otros servicios del backend, por ejemplo, ante un evento crítico detectado por sensores conectados a un microcontrolador (ESP32:

   ```bash
   pip install python-dotenv twilio

2. **Crear archivo de configuración de entorno (.env)** \
Este archivo se utiliza para definir claves privadas como tokens, clave SID de API, numero de cuidador y el numero establecido desde donde sale el mensaje.
Por ejemplo:

   ```bash
   TWILIO_ACCOUNT_SID=**
    TWILIO_AUTH_TOKEN=***
    TWILIO_PHONE_NUMBER=++17629997179
    NUMERO_CUIDADOR=+50688369005

  4. **Proteger información sensible** \
  El archivo .env ha sido agregado al archivo .gitignore para evitar que las claves se suban al repositorio público.
