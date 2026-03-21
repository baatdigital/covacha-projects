"""Registro de nodos en DynamoDB para el Agent Swarm.

Maneja el ciclo de vida de nodos: registro, heartbeat, discovery,
y deregistro. Usa prefijo TENANT#{tenant_id}|NODE#{node_id}|STATUS
para aislamiento multi-tenant.
"""
import platform
import time
from typing import Any

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from config import NODE_TTL_SECONDS, STALE_THRESHOLD
from dynamo_client import get_dynamo_client


def _build_node_pk(tenant_id: str, node_id: str) -> str:
    """Construye la partition key para un nodo."""
    return f"TENANT#{tenant_id}|NODE#{node_id}"


def _node_sk() -> str:
    """Retorna la sort key para registros de nodo."""
    return "STATUS"


def register_node(tenant_id: str, node_config: dict[str, Any]) -> None:
    """Registra o actualiza un nodo en DynamoDB.

    Crea el item con capacidades, repos, roles y estado idle.
    TTL de 24 horas para auto-limpieza si el nodo desaparece.
    """
    table = get_dynamo_client()
    now = int(time.time())
    node_id = node_config["node_id"]
    try:
        table.put_item(Item={
            "PK": _build_node_pk(tenant_id, node_id),
            "SK": _node_sk(),
            "node_id": node_id,
            "capabilities": node_config.get("capabilities", []),
            "repos": node_config.get("repos", []),
            "roles": node_config.get("roles", ["developer"]),
            "status": "idle",
            "current_task": None,
            "current_workspace": None,
            "last_heartbeat": now,
            "registered_at": now,
            "os": platform.system().lower(),
            "ttl": now + NODE_TTL_SECONDS,
        })
    except ClientError as exc:
        raise RuntimeError(
            f"Error al registrar nodo {node_id}: {exc}"
        ) from exc


def heartbeat(tenant_id: str, node_id: str) -> None:
    """Actualiza last_heartbeat y renueva TTL del nodo.

    Debe ejecutarse periodicamente (cada ~2 min) para mantener
    el nodo como activo en el swarm.
    """
    table = get_dynamo_client()
    now = int(time.time())
    try:
        table.update_item(
            Key={
                "PK": _build_node_pk(tenant_id, node_id),
                "SK": _node_sk(),
            },
            UpdateExpression=(
                "SET last_heartbeat = :now, #ttl = :ttl"
            ),
            ExpressionAttributeNames={"#ttl": "ttl"},
            ExpressionAttributeValues={
                ":now": now,
                ":ttl": now + NODE_TTL_SECONDS,
            },
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error en heartbeat de nodo {node_id}: {exc}"
        ) from exc


def update_node_status(
    tenant_id: str,
    node_id: str,
    status: str,
    current_task: str | None = None,
    current_workspace: str | None = None,
) -> None:
    """Actualiza el status del nodo y opcionalmente la tarea/workspace actual."""
    table = get_dynamo_client()
    try:
        table.update_item(
            Key={
                "PK": _build_node_pk(tenant_id, node_id),
                "SK": _node_sk(),
            },
            UpdateExpression=(
                "SET #s = :status, current_task = :task, "
                "current_workspace = :ws"
            ),
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":status": status,
                ":task": current_task,
                ":ws": current_workspace,
            },
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al actualizar status de nodo {node_id}: {exc}"
        ) from exc


def discover_nodes(
    tenant_id: str,
    only_active: bool = True,
    stale_threshold: int = STALE_THRESHOLD,
) -> list[dict[str, Any]]:
    """Descubre todos los nodos registrados para un tenant.

    Si only_active es True, filtra nodos cuyo last_heartbeat
    sea mayor al umbral de staleness (default 5 min).
    """
    table = get_dynamo_client()
    prefix = f"TENANT#{tenant_id}|NODE#"
    try:
        filter_expr = (
            Attr("PK").begins_with(prefix) & Attr("SK").eq("STATUS")
        )
        response = table.scan(FilterExpression=filter_expr)
        nodes: list[dict[str, Any]] = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = table.scan(
                FilterExpression=filter_expr,
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            nodes.extend(response.get("Items", []))
    except ClientError as exc:
        raise RuntimeError(
            f"Error al descubrir nodos del tenant {tenant_id}: {exc}"
        ) from exc

    if only_active:
        now = int(time.time())
        nodes = [
            n for n in nodes
            if (now - n.get("last_heartbeat", 0)) < stale_threshold
        ]
    return nodes


def get_node(
    tenant_id: str, node_id: str
) -> dict[str, Any] | None:
    """Obtiene un nodo especifico por tenant y node_id. Retorna None si no existe."""
    table = get_dynamo_client()
    try:
        response = table.get_item(
            Key={
                "PK": _build_node_pk(tenant_id, node_id),
                "SK": _node_sk(),
            }
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al obtener nodo {node_id}: {exc}"
        ) from exc
    return response.get("Item")


def check_stale_nodes(
    tenant_id: str,
    threshold: int = STALE_THRESHOLD,
) -> list[dict[str, Any]]:
    """Retorna nodos con tarea asignada que no han hecho heartbeat en threshold segundos."""
    all_nodes = discover_nodes(
        tenant_id, only_active=False
    )
    now = int(time.time())
    stale: list[dict[str, Any]] = []
    for node in all_nodes:
        has_task = node.get("current_task") is not None
        elapsed = now - node.get("last_heartbeat", 0)
        if has_task and elapsed >= threshold:
            stale.append(node)
    return stale


def deregister_node(tenant_id: str, node_id: str) -> None:
    """Borra el registro del nodo de DynamoDB (shutdown graceful)."""
    table = get_dynamo_client()
    try:
        table.delete_item(
            Key={
                "PK": _build_node_pk(tenant_id, node_id),
                "SK": _node_sk(),
            }
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al desregistrar nodo {node_id}: {exc}"
        ) from exc


def get_swarm_summary(
    tenant_id: str,
) -> dict[str, Any]:
    """Retorna resumen del swarm: nodos totales, idle, busy, y capabilities agregadas."""
    nodes = discover_nodes(tenant_id, only_active=True)
    idle = [n for n in nodes if n.get("status") == "idle"]
    busy = [n for n in nodes if n.get("status") == "working"]
    # Agregar capabilities unicas
    all_caps: dict[str, int] = {}
    for node in nodes:
        for cap in node.get("capabilities", []):
            all_caps[cap] = all_caps.get(cap, 0) + 1
    return {
        "total_nodes": len(nodes),
        "idle": idle,
        "busy": busy,
        "capabilities": all_caps,
    }
