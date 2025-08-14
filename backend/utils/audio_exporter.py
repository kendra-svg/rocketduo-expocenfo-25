import os
from config.config import AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_CONTAINER_NAME
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


def subir_a_blob(nombre_local, nombre_blob):

 # Crear cliente del servicio
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
    
    # Crear cliente del contenedor
    container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER_NAME)
    
    # Crear el contenedor si no existe
    try:
        container_client.create_container()
    except Exception:
        pass  # si ya existe, ignorar
    
    # Subir el archivo
    blob_client = container_client.get_blob_client(nombre_blob)
    with open(nombre_local, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)
    
    # Generar la URL pública del blob
    url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER_NAME}/{nombre_blob}"
    return url