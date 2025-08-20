from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from config.config import (
    AZURE_COSMOS_DATABASE_NAME,
    AZURE_COSMOS_DB_CONTAINER_NAME,
    AZURE_COSMOS_KEY,
    AZURE_COSMOS_URL
)
import uuid
from datetime import datetime


class cosmos_handler:
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

def guardar_alerta_clima(container, alerta: dict):
    """
    Inserta una alerta de clima en Cosmos DB.
    Requiere: alerta['quien'], alerta['categoria'] ('abrigo'|'calor'), alerta['mensaje'], alerta['url_audio'].
    Setea: tipo='alerta_clima', activo=true, creado_en=ISO.
    """
    try:
        if "quien" not in alerta or not alerta["quien"]:
            raise ValueError("Campo 'quien' es requerido para la partición.")
        alerta.setdefault("tipo", "alerta_clima")
        alerta.setdefault("activo", True)
        alerta.setdefault("creado_en", datetime.utcnow().isoformat())
        alerta["id"] = str(uuid.uuid4())
        container.create_item(body=alerta)
        return alerta
    except Exception as e:
        print(f"[ERROR] guardar_alerta_clima: {e}")
        raise

def obtener_ultima_alerta(container, quien: str, categoria: str = None):
    """
    Devuelve la última alerta para 'quien' y opcionalmente por 'categoria' ('abrigo'|'calor').
    Ordena por 'creado_en' descendente.
    """
    try:
        query = "SELECT * FROM c WHERE c.quien = @quien AND c.tipo = 'alerta_clima'"
        params = [{"name": "@quien", "value": quien}]
        if categoria:
            query += " AND c.categoria = @categoria"
            params.append({"name": "@categoria", "value": categoria})
        query += " ORDER BY c.creado_en DESC"

        items = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        return items[0] if items else None
    except exceptions.CosmosResourceNotFoundError:
        return None
    except Exception as e:
        print(f"[ERROR] obtener_ultima_alerta: {e}")
        raise

def listar_alertas(container, quien: str = None, categoria: str = None, limit: int = 50):
    """
    Lista alertas tipo='alerta_clima', opcionalmente filtradas por 'quien' y 'categoria'.
    TOP usa literal (no parámetro).
    """
    try:
        limit = max(1, min(int(limit or 50), 200))
        base = f"SELECT TOP {limit} * FROM c WHERE c.tipo = 'alerta_clima'"
        params = []
        if quien:
            base += " AND c.quien = @quien"
            params.append({"name": "@quien", "value": quien})
        if categoria:
            base += " AND c.categoria = @categoria"
            params.append({"name": "@categoria", "value": categoria})
        base += " ORDER BY c.creado_en DESC"

        items = list(container.query_items(
            query=base,
            parameters=params,
            enable_cross_partition_query=True
        ))
        return items
    except Exception as e:
        print(f"[ERROR] listar_alertas: {e}")
        raise

def eliminar_alertas(container, quien: str, categoria: str | None = None) -> int:
    """
    Borra documentos tipo 'alerta_clima' para la persona 'quien'.
    Si se pasa 'categoria' ('abrigo'|'calor'), filtra por ella.
    Devuelve la cantidad de documentos eliminados.
    """
    if not quien:
        raise ValueError("El parámetro 'quien' es requerido para eliminar alertas.")

    # Buscar ids a eliminar
    query = "SELECT c.id FROM c WHERE c.tipo = 'alerta_clima' AND c.quien = @quien"
    params = [{"name": "@quien", "value": quien}]
    if categoria:
        query += " AND c.categoria = @categoria"
        params.append({"name": "@categoria", "value": categoria})

    items = list(container.query_items(
        query=query,
        parameters=params,
        enable_cross_partition_query=True
    ))

    # Borrar uno por uno con PK
    eliminados = 0
    for it in items:
        _id = it.get("id")
        if not _id:
            continue
        try:
            container.delete_item(item=_id, partition_key=quien)
            eliminados += 1
        except exceptions.CosmosHttpResponseError as e:
            print(f"[Cosmos] No se pudo borrar id={_id} (quien={quien}): {e}")
            continue

    return eliminados

def eliminar_alerta_por_id(container, alerta_id: str) -> bool:
    """
    Elimina un documento tipo 'alerta_clima' por su 'id'.
    Descubre el partition key ('quien') mediante una query y luego hace delete_item.
    Devuelve True si se eliminó; False si no se encontró o falló.
    """
    if not alerta_id:
        raise ValueError("El parámetro 'alerta_id' es requerido.")

    try:
        # Buscar el documento para obtener 'quien'
        query = "SELECT TOP 1 c.id, c.quien FROM c WHERE c.id = @id AND c.tipo = 'alerta_clima'"
        params = [{"name": "@id", "value": alerta_id}]
        items = list(container.query_items(
            query=query,
            parameters=params,
            enable_cross_partition_query=True
        ))
        if not items:
            return False

        quien = items[0].get("quien")
        if not quien:
            print(f"[Cosmos] Documento {alerta_id} no tiene 'quien'; no se puede eliminar.")
            return False

        container.delete_item(item=alerta_id, partition_key=quien)
        return True

    except exceptions.CosmosResourceNotFoundError:
        return False
    except exceptions.CosmosHttpResponseError as e:
        print(f"[Cosmos] Error al eliminar id={alerta_id}: {e}")
        return False

# Instancia global para usar en toda la aplicación
cosmos_handler = cosmos_handler()