from flask import Blueprint, request, jsonify
from service.clothing_service import generar_alerta_y_guardar, obtener_ultima_alerta
from service.cosmos_handler import cosmos_handler
from azure.cosmos import exceptions

# Helpers de borrado (importados del mismo handler)
from service.cosmos_handler import (
    eliminar_alertas as ch_eliminar_alertas,
    eliminar_alerta_por_id as ch_eliminar_alerta_por_id,
)

router = Blueprint("clothing_api", __name__, url_prefix="/api/clothing")


@router.post("/generar")
def generar():
    """
    POST /api/clothing/generar
    Acepta JSON body o query params.
      - 201 si se guardó alerta (viene id_documento).
      - 502 si falló TTS/Blob/Cosmos (viene 'error').
      - 200 si está en rango normal (sin alerta).
    """

    datos = request.get_json(silent=True) or {}
    args = request.args or {}

    def val(key, default=None):
        return datos.get(key, args.get(key, default))

    persona = (val("persona", "sistema") or "sistema").strip()
    promedio_raw = val("promedio")

    try:
        promedio = float(promedio_raw)
    except (TypeError, ValueError):
        return jsonify({"detalle": "El parámetro 'promedio' es requerido y debe ser numérico"}), 400

    try:
        margen = float(val("margen", 4.0))
    except ValueError:
        return jsonify({"detalle": "El parámetro 'margen' debe ser numérico"}), 400

    incluir_raw = val("incluir_temp", False)
    incluir_temp = incluir_raw in (True, "1", "true", "True", 1)

    try:
        lat = float(val("lat", 9.9281))
        lon = float(val("lon", -84.0907))
    except ValueError:
        return jsonify({"detalle": "Parámetros 'lat' y 'lon' deben ser numéricos"}), 400

    data = generar_alerta_y_guardar(
        persona=persona,
        promedio=promedio,
        margen=margen,
        incluir_temp=incluir_temp,
        lat=lat,
        lon=lon,
    )

    if data.get("id_documento"):
        return jsonify(data), 201
    if data.get("error"):
        return jsonify(data), 502
    return jsonify(data), 200


@router.get("/ultimo")
def ultimo():
    """
    GET /api/clothing/ultimo?persona=Gabriel&categoria=frio|calor
    Si no se envía 'categoria', devuelve la última alerta de cualquier tipo.
    """

    persona = request.args.get("persona", type=str)
    categoria = request.args.get("categoria", type=str)  # opcional

    if not persona:
        return jsonify({"detalle": "Falta el parámetro 'persona'"}), 400

    # Validar 'categoria' SOLO si fue enviada
    if categoria and categoria not in ("frio", "calor"):
        return jsonify({"detalle": "El parámetro 'categoria' debe ser 'frio' o 'calor'"}), 400

    data = obtener_ultima_alerta(persona, categoria)  # puede ir None
    if not data:
        return jsonify({"detalle": "No hay alertas para esta persona con ese criterio"}), 404

    return jsonify(data), 200



@router.get("/alertas")
def listar_alertas():
    """
    GET /api/clothing/alertas?persona=Gabriel&categoria=abrigo|calor&limit=20
    Lista alertas tipo 'alerta_clima' (más recientes primero).
    """

    persona = request.args.get("persona", type=str)
    categoria = request.args.get("categoria", type=str)
    limit = request.args.get("limit", default=20, type=int)

    if categoria and categoria not in ("abrigo", "calor"):
        return jsonify({"detalle": "El parámetro 'categoria' debe ser 'abrigo' o 'calor'"}), 400

    try:
        base = "SELECT * FROM c WHERE c.tipo = 'alerta_clima'"
        params = []
        if persona:
            base += " AND c.quien = @quien"
            params.append({"name": "@quien", "value": persona})
        if categoria:
            base += " AND c.categoria = @categoria"
            params.append({"name": "@categoria", "value": categoria})
        base += " ORDER BY c.creado_en DESC"

        items = list(cosmos_handler.container.query_items(
            query=base,
            parameters=params,
            enable_cross_partition_query=True
        ))
        items = items[:max(1, min(limit, 200))]
        resp = [
            {
                "id_documento": d.get("id"),
                "quien": d.get("quien"),
                "categoria": d.get("categoria"),
                "temperatura": d.get("temperatura_actual"),
                "promedio": d.get("promedio"),
                "margen": d.get("margen"),
                "url_audio": d.get("url_audio"),
                "mensaje": d.get("mensaje"),
                "creado_en": d.get("creado_en"),
            }
            for d in items
        ]
        return jsonify({"total": len(resp), "alertas": resp}), 200
    except exceptions.CosmosHttpResponseError as e:
        return jsonify({"error": f"Cosmos: {e}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@router.delete("/alertas")
def borrar_alertas():
    """
    DELETE /api/clothing/alertas?persona=Gabriel&categoria=abrigo|calor
    Elimina alertas para 'persona' (requerido). Si se pasa 'categoria', filtra.
    Devuelve la cantidad de documentos eliminados.
    """

    persona = request.args.get("persona", type=str)
    categoria = request.args.get("categoria", type=str)

    if not persona:
        return jsonify({"detalle": "Falta el parámetro 'persona'"}), 400
    if categoria and categoria not in ("abrigo", "calor"):
        return jsonify({"detalle": "El parámetro 'categoria' debe ser 'abrigo' o 'calor'"}), 400

    try:
        count = ch_eliminar_alertas(cosmos_handler.container, quien=persona, categoria=categoria)
        return jsonify({"eliminados": count}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@router.delete("/alertas/<alerta_id>")
def borrar_alerta_por_id(alerta_id: str):
    """
    DELETE /api/clothing/alertas/<alerta_id>
    Elimina UNA alerta por su id. Descubre internamente el partition key ('quien').
    """
    if not alerta_id:
        return jsonify({"detalle": "Falta 'alerta_id' en la ruta"}), 400

    try:
        ok = ch_eliminar_alerta_por_id(cosmos_handler.container, alerta_id=alerta_id)
        if not ok:
            return jsonify({"detalle": "No se encontró el documento o no se pudo eliminar"}), 404
        return jsonify({"eliminado": True, "id": alerta_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
