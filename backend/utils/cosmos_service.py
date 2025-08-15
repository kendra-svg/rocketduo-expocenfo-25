from azure.cosmos import CosmosClient, exceptions
from backend.config.config import (
    AZURE_COSMOS_DATABASE_NAME,
    AZURE_COSMOS_DB_CONTAINER_NAME,
    AZURE_COSMOS_KEY,
    AZURE_COSMOS_URL
)
import uuid
from datetime import datetime


class CosmosService:
    def __init__(self):
        self.client = CosmosClient(AZURE_COSMOS_URL, AZURE_COSMOS_KEY)
        self.database = self.client.get_database_client(AZURE_COSMOS_DATABASE_NAME)
        self.container = self.database.get_container_client(AZURE_COSMOS_DB_CONTAINER_NAME)

    def guardar_recordatorio(self, datos_json):
        """
        Guarda un recordatorio en Cosmos DB
        """
        try:
            # Agregar metadatos
            documento = {
                "id": str(uuid.uuid4()),
                "tipo": "recordatorio",
                "fecha_creacion": datetime.now().isoformat(),
                "activo": True,
                **datos_json
            }

            # Crear el item - el partition key se toma automáticamente del campo 'quien'
            response = self.container.create_item(body=documento)

            print(f"Recordatorio guardado con ID: {response['id']}")
            return response['id']

        except exceptions.CosmosHttpResponseError as e:
            print(f"Error guardando recordatorio: {e}")
            return None
        except Exception as e:
            print(f"Error general: {e}")
            return None

    def obtener_recordatorios_activos(self):
        """
        Obtiene todos los recordatorios activos
        """
        try:
            query = "SELECT * FROM c WHERE c.tipo = 'recordatorio' AND c.activo = true"
            recordatorios = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return recordatorios

        except exceptions.CosmosHttpResponseError as e:
            print(f"Error obteniendo recordatorios: {e}")
            return []

    def obtener_recordatorios_por_hora(self, hora):
        """
        Obtiene recordatorios para una hora específica (formato HH:MM)
        """
        try:
            query = "SELECT * FROM c WHERE c.hora = @hora AND c.activo = true AND c.tipo = 'recordatorio'"
            recordatorios = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@hora", "value": hora}],
                enable_cross_partition_query=True
            ))
            return recordatorios

        except exceptions.CosmosHttpResponseError as e:
            print(f"Error obteniendo recordatorios por hora: {e}")
            return []

    def obtener_recordatorios_por_persona(self, quien):
        """
        Obtiene todos los recordatorios de una persona específica
        """
        try:
            query = "SELECT * FROM c WHERE c.quien = @quien AND c.activo = true AND c.tipo = 'recordatorio'"
            recordatorios = list(self.container.query_items(
                query=query,
                parameters=[{"name": "@quien", "value": quien}],
                enable_cross_partition_query=False  # Ya que usamos partition key
            ))
            return recordatorios

        except exceptions.CosmosHttpResponseError as e:
            print(f"Error obteniendo recordatorios por persona: {e}")
            return []

    def desactivar_recordatorio(self, recordatorio_id, quien):
        """
        Marca un recordatorio como inactivo en lugar de eliminarlo
        """
        try:
            # Obtener el documento actual
            documento = self.container.read_item(
                item=recordatorio_id,
                partition_key=quien
            )

            # Marcar como inactivo
            documento['activo'] = False
            documento['fecha_desactivacion'] = datetime.now().isoformat()

            # Actualizar el documento
            response = self.container.replace_item(
                item=recordatorio_id,
                body=documento
            )

            print(f"Recordatorio {recordatorio_id} desactivado")
            return True

        except exceptions.CosmosHttpResponseError as e:
            print(f"Error desactivando recordatorio: {e}")
            return False

    def guardar_evento_boton(self, tipo_boton, quien="sin_especificar"):
        """
        Guarda eventos de botones presionados (rojo, azul, amarillo)
        """
        try:
            evento = {
                "id": str(uuid.uuid4()),
                "tipo": "evento_boton",
                "boton": tipo_boton,
                "quien": quien,
                "timestamp": datetime.now().isoformat(),
                "procesado": False
            }

            response = self.container.create_item(body=evento)

            print(f"Evento de botón guardado: {tipo_boton}")
            return response['id']

        except exceptions.CosmosHttpResponseError as e:
            print(f"Error guardando evento: {e}")
            return None

    def obtener_eventos_pendientes(self):
        """
        Obtiene eventos de botones que no han sido procesados
        """
        try:
            query = "SELECT * FROM c WHERE c.tipo = 'evento_boton' AND c.procesado = false"
            eventos = list(self.container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return eventos

        except exceptions.CosmosHttpResponseError as e:
            print(f"Error obteniendo eventos pendientes: {e}")
            return []

    def marcar_evento_procesado(self, evento_id, quien):
        """
        Marca un evento como procesado después de enviar SMS
        """
        try:
            documento = self.container.read_item(
                item=evento_id,
                partition_key=quien
            )

            documento['procesado'] = True
            documento['fecha_procesado'] = datetime.now().isoformat()

            response = self.container.replace_item(
                item=evento_id,
                body=documento
            )

            return True

        except exceptions.CosmosHttpResponseError as e:
            print(f"Error marcando evento como procesado: {e}")
            return False


# Instancia global para usar en toda la aplicación
cosmos_service = CosmosService()