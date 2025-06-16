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
