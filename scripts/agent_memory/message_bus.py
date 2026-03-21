"""Maneja mensajes inter-nodo con prefijo MSG# (multi-tenant).

Soporta mensajes broadcast (a todos los nodos del workspace)
y directos (a un nodo especifico). Incluye TTL de 24h y tracking de lectura.
"""
import time
from typing import Any

from botocore.exceptions import ClientError

from dynamo_client import get_dynamo_client

# Tipos de mensaje validos para el swarm
VALID_MESSAGE_TYPES: set[str] = {
    "task_completed",
    "task_blocked",
    "contract_published",
    "review_requested",
    "qa_approved",
    "qa_rejected",
    "po_accepted",
    "po_rejected",
    "help_needed",
    "bug_found",
    "dependency_resolved",
    "node_joined",
    "node_left",
}

TTL_24H: int = 86400


def _build_msg_pk(
    tenant_id: str,
    workspace_id: str,
    timestamp: int,
    from_node: str,
) -> str:
    """Construye el PK para un mensaje."""
    return (
        f"TENANT#{tenant_id}|WS#{workspace_id}"
        f"|MSG#{timestamp}-{from_node}"
    )


def _msg_prefix(tenant_id: str, workspace_id: str) -> str:
    """Prefijo comun para scan de mensajes de un workspace."""
    return f"TENANT#{tenant_id}|WS#{workspace_id}|MSG#"


def send_message(
    tenant_id: str,
    workspace_id: str,
    from_node: str,
    msg_type: str,
    task_id: str | None = None,
    payload: dict | None = None,
    to_node: str | None = None,
) -> str:
    """Envia un mensaje broadcast o directo al workspace.

    Retorna el message_id (PK del item creado).
    Lanza ValueError si el tipo de mensaje no es valido.
    """
    if msg_type not in VALID_MESSAGE_TYPES:
        raise ValueError(
            f"Tipo de mensaje invalido: '{msg_type}'. "
            f"Validos: {sorted(VALID_MESSAGE_TYPES)}"
        )

    table = get_dynamo_client()
    now = int(time.time())
    pk = _build_msg_pk(tenant_id, workspace_id, now, from_node)
    sk = f"DIRECT#{to_node}" if to_node else "BROADCAST"

    item: dict[str, Any] = {
        "PK": pk,
        "SK": sk,
        "from_node": from_node,
        "type": msg_type,
        "task_id": task_id or "",
        "payload": payload or {},
        "read_by": [],
        "ttl": now + TTL_24H,
        "created_at": now,
    }

    try:
        table.put_item(Item=item)
    except ClientError as exc:
        raise RuntimeError(
            f"Error al enviar mensaje desde {from_node}: {exc}"
        ) from exc

    return pk


def get_unread_messages(
    tenant_id: str,
    workspace_id: str,
    node_id: str,
    limit: int = 20,
) -> list[dict]:
    """Retorna mensajes no leidos por node_id.

    Filtra BROADCAST donde node_id no esta en read_by,
    y DIRECT donde to_node == node_id y no leido.
    Ordena por timestamp descendente.
    """
    table = get_dynamo_client()
    prefix = _msg_prefix(tenant_id, workspace_id)

    try:
        response = table.scan(
            FilterExpression="begins_with(PK, :prefix)",
            ExpressionAttributeValues={":prefix": prefix},
        )
        items = response.get("Items", [])

        while "LastEvaluatedKey" in response:
            response = table.scan(
                FilterExpression="begins_with(PK, :prefix)",
                ExpressionAttributeValues={":prefix": prefix},
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))
    except ClientError as exc:
        raise RuntimeError(
            f"Error al leer mensajes de {workspace_id}: {exc}"
        ) from exc

    filtered = _filter_for_node(items, node_id)

    # Ordenar por created_at descendente
    filtered.sort(key=lambda m: m.get("created_at", 0), reverse=True)
    return filtered[:limit]


def _filter_for_node(items: list[dict], node_id: str) -> list[dict]:
    """Filtra mensajes relevantes y no leidos para un nodo."""
    result: list[dict] = []
    for item in items:
        read_by = item.get("read_by", [])
        if node_id in read_by:
            continue

        sk = item.get("SK", "")
        if sk == "BROADCAST":
            result.append(item)
        elif sk.startswith("DIRECT#"):
            target = sk.replace("DIRECT#", "", 1)
            if target == node_id:
                result.append(item)
    return result


def mark_as_read(
    tenant_id: str,
    workspace_id: str,
    message_pk: str,
    node_id: str,
) -> None:
    """Agrega node_id a la lista read_by del mensaje."""
    table = get_dynamo_client()

    # Determinar SK: necesitamos obtener el item primero
    # o usar un approach mas directo si conocemos el SK
    try:
        # Buscar el item por PK (puede ser BROADCAST o DIRECT)
        response = table.query(
            KeyConditionExpression="PK = :pk",
            ExpressionAttributeValues={":pk": message_pk},
        )
        items = response.get("Items", [])
        if not items:
            return

        for item in items:
            table.update_item(
                Key={"PK": message_pk, "SK": item["SK"]},
                UpdateExpression=(
                    "SET read_by = list_append("
                    "if_not_exists(read_by, :empty), :node)"
                ),
                ExpressionAttributeValues={
                    ":node": [node_id],
                    ":empty": [],
                },
            )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al marcar mensaje como leido: {exc}"
        ) from exc


def get_recent_messages(
    tenant_id: str,
    workspace_id: str,
    limit: int = 10,
) -> list[dict]:
    """Retorna los ultimos N mensajes sin filtro de lectura (para dashboard)."""
    table = get_dynamo_client()
    prefix = _msg_prefix(tenant_id, workspace_id)

    try:
        response = table.scan(
            FilterExpression="begins_with(PK, :prefix)",
            ExpressionAttributeValues={":prefix": prefix},
        )
        items = response.get("Items", [])

        while "LastEvaluatedKey" in response:
            response = table.scan(
                FilterExpression="begins_with(PK, :prefix)",
                ExpressionAttributeValues={":prefix": prefix},
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))
    except ClientError as exc:
        raise RuntimeError(
            f"Error al leer mensajes recientes: {exc}"
        ) from exc

    items.sort(key=lambda m: m.get("created_at", 0), reverse=True)
    return items[:limit]
