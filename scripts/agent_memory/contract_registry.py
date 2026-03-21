"""Maneja contratos de API con prefijo CONTRACT# (multi-tenant).

Permite publicar, buscar y consumir contratos de API
compartidos entre nodos del workspace.
"""
import time
from typing import Any

from botocore.exceptions import ClientError

from dynamo_client import get_dynamo_client


def _build_contract_pk(
    tenant_id: str,
    workspace_id: str,
    name: str,
    version: str,
) -> str:
    """Construye el PK para un contrato."""
    return (
        f"TENANT#{tenant_id}|WS#{workspace_id}"
        f"|CONTRACT#{name}-{version}"
    )


def _contract_prefix(tenant_id: str, workspace_id: str) -> str:
    """Prefijo comun para scan de contratos de un workspace."""
    return f"TENANT#{tenant_id}|WS#{workspace_id}|CONTRACT#"


def publish_contract(
    tenant_id: str,
    workspace_id: str,
    name: str,
    version: str,
    method: str,
    path: str,
    request_schema: dict,
    response_schema: dict,
    published_by: str,
    task_id: str | None = None,
) -> str:
    """Publica un contrato de API en el workspace.

    Retorna el contract_id (PK del item creado).
    """
    table = get_dynamo_client()
    pk = _build_contract_pk(tenant_id, workspace_id, name, version)

    item: dict[str, Any] = {
        "PK": pk,
        "SK": "META",
        "name": name,
        "version": version,
        "method": method,
        "path": path,
        "request_schema": request_schema,
        "response_schema": response_schema,
        "published_by": published_by,
        "task_id": task_id or "",
        "created_at": int(time.time()),
        "consumed_by": [],
    }

    try:
        table.put_item(Item=item)
    except ClientError as exc:
        raise RuntimeError(
            f"Error al publicar contrato {name}-{version}: {exc}"
        ) from exc

    return pk


def get_contract(
    tenant_id: str,
    workspace_id: str,
    contract_id: str,
) -> dict | None:
    """Obtiene un contrato por su ID completo. Retorna None si no existe."""
    table = get_dynamo_client()

    try:
        response = table.get_item(
            Key={"PK": contract_id, "SK": "META"}
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al obtener contrato {contract_id}: {exc}"
        ) from exc

    return response.get("Item")


def search_contracts(
    tenant_id: str,
    workspace_id: str,
    path_pattern: str | None = None,
    method: str | None = None,
) -> list[dict]:
    """Busca contratos del workspace filtrando por path y/o method."""
    table = get_dynamo_client()
    prefix = _contract_prefix(tenant_id, workspace_id)

    try:
        response = table.scan(
            FilterExpression="begins_with(PK, :prefix) AND SK = :meta",
            ExpressionAttributeValues={
                ":prefix": prefix,
                ":meta": "META",
            },
        )
        items = response.get("Items", [])

        while "LastEvaluatedKey" in response:
            response = table.scan(
                FilterExpression=(
                    "begins_with(PK, :prefix) AND SK = :meta"
                ),
                ExpressionAttributeValues={
                    ":prefix": prefix,
                    ":meta": "META",
                },
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))
    except ClientError as exc:
        raise RuntimeError(
            f"Error al buscar contratos: {exc}"
        ) from exc

    return _apply_filters(items, path_pattern, method)


def _apply_filters(
    items: list[dict],
    path_pattern: str | None,
    method: str | None,
) -> list[dict]:
    """Filtra contratos por path (contains) y/o method (exact)."""
    result: list[dict] = []
    for item in items:
        if path_pattern and path_pattern not in item.get("path", ""):
            continue
        if method and item.get("method", "").upper() != method.upper():
            continue
        result.append(item)
    return result


def add_consumer(
    tenant_id: str,
    workspace_id: str,
    contract_id: str,
    consumer_task_id: str,
) -> None:
    """Agrega un consumer_task_id a la lista consumed_by del contrato."""
    table = get_dynamo_client()

    try:
        table.update_item(
            Key={"PK": contract_id, "SK": "META"},
            UpdateExpression=(
                "SET consumed_by = list_append("
                "if_not_exists(consumed_by, :empty), :consumer)"
            ),
            ExpressionAttributeValues={
                ":consumer": [consumer_task_id],
                ":empty": [],
            },
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al agregar consumer a {contract_id}: {exc}"
        ) from exc
