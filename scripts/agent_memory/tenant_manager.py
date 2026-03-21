"""Gestion de tenants y workspaces en DynamoDB.

Maneja CRUD de tenants (empresas/organizaciones) y workspaces (proyectos/productos)
con aislamiento multi-tenant. Cada tenant tiene un plan que limita nodos y workspaces.
"""
import time
from typing import Any

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from dynamo_client import get_dynamo_client

# Limites por plan
PLAN_LIMITS: dict[str, dict[str, int]] = {
    "free": {"max_nodes": 2, "max_workspaces": 1, "sync_interval": 900},
    "team": {"max_nodes": 10, "max_workspaces": 5, "sync_interval": 300},
    "business": {"max_nodes": 50, "max_workspaces": 20, "sync_interval": 120},
    "enterprise": {"max_nodes": 999, "max_workspaces": 999, "sync_interval": 60},
}


def _tenant_pk(tenant_id: str) -> str:
    """Construye la partition key para un tenant."""
    return f"TENANT#{tenant_id}"


def _config_sk() -> str:
    """Sort key para configuracion de tenant."""
    return "CONFIG"


def _workspace_sk(workspace_id: str) -> str:
    """Sort key para un workspace dentro de un tenant."""
    return f"WORKSPACE#{workspace_id}"


def create_tenant(
    tenant_id: str,
    github_org: str,
    admin_email: str,
    plan: str = "team",
) -> dict[str, Any]:
    """Crea un tenant nuevo en DynamoDB.

    Usa ConditionExpression para no sobreescribir si ya existe.
    Lanza RuntimeError si el tenant ya existe o si el plan es invalido.
    """
    if plan not in PLAN_LIMITS:
        raise ValueError(f"Plan invalido: {plan}. Opciones: {list(PLAN_LIMITS.keys())}")

    limits = PLAN_LIMITS[plan]
    table = get_dynamo_client()
    now = int(time.time())

    item: dict[str, Any] = {
        "PK": _tenant_pk(tenant_id),
        "SK": _config_sk(),
        "org_name": tenant_id,
        "github_org": github_org,
        "admin_email": admin_email,
        "plan": plan,
        "max_nodes": limits["max_nodes"],
        "max_workspaces": limits["max_workspaces"],
        "created_at": now,
        "active": True,
    }

    try:
        table.put_item(
            Item=item,
            ConditionExpression=Attr("PK").not_exists(),
        )
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code == "ConditionalCheckFailedException":
            raise RuntimeError(
                f"Tenant '{tenant_id}' ya existe."
            ) from exc
        raise RuntimeError(
            f"Error al crear tenant {tenant_id}: {exc}"
        ) from exc

    return item


def get_tenant(tenant_id: str) -> dict[str, Any] | None:
    """Obtiene la configuracion de un tenant. Retorna None si no existe."""
    table = get_dynamo_client()
    try:
        response = table.get_item(
            Key={"PK": _tenant_pk(tenant_id), "SK": _config_sk()}
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al obtener tenant {tenant_id}: {exc}"
        ) from exc
    return response.get("Item")


def list_tenants() -> list[dict[str, Any]]:
    """Lista todos los tenants registrados en la tabla."""
    table = get_dynamo_client()
    filter_expr = (
        Attr("SK").eq("CONFIG")
        & Attr("PK").begins_with("TENANT#")
    )
    try:
        response = table.scan(FilterExpression=filter_expr)
        items: list[dict[str, Any]] = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = table.scan(
                FilterExpression=filter_expr,
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))
    except ClientError as exc:
        raise RuntimeError(
            f"Error al listar tenants: {exc}"
        ) from exc
    return items


def delete_tenant(tenant_id: str) -> None:
    """Elimina un tenant si no tiene workspaces activos.

    Lanza RuntimeError si tiene workspaces asociados.
    """
    workspaces = list_workspaces(tenant_id)
    if workspaces:
        raise RuntimeError(
            f"Tenant '{tenant_id}' tiene {len(workspaces)} workspace(s) activos. "
            "Eliminalos primero."
        )
    table = get_dynamo_client()
    try:
        table.delete_item(
            Key={"PK": _tenant_pk(tenant_id), "SK": _config_sk()}
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al eliminar tenant {tenant_id}: {exc}"
        ) from exc


def create_workspace(
    tenant_id: str,
    workspace_id: str,
    workspace_name: str,
    github_project_id: str,
    github_project_number: int,
    status_field_id: str,
    status_options: dict[str, str],
    repos: list[str],
    producto_field_id: str | None = None,
) -> dict[str, Any]:
    """Crea un workspace dentro de un tenant.

    Verifica que el tenant exista y no exceda el limite de workspaces del plan.
    """
    tenant = get_tenant(tenant_id)
    if tenant is None:
        raise RuntimeError(f"Tenant '{tenant_id}' no existe.")

    existing = list_workspaces(tenant_id)
    max_ws = tenant.get("max_workspaces", 1)
    if len(existing) >= max_ws:
        raise RuntimeError(
            f"Tenant '{tenant_id}' excede el limite de {max_ws} workspaces "
            f"(plan: {tenant.get('plan', '?')})."
        )

    table = get_dynamo_client()
    now = int(time.time())

    github_config: dict[str, Any] = {
        "project_id": github_project_id,
        "project_number": github_project_number,
        "status_field_id": status_field_id,
        "status_options": status_options,
    }
    if producto_field_id:
        github_config["producto_field_id"] = producto_field_id

    item: dict[str, Any] = {
        "PK": _tenant_pk(tenant_id),
        "SK": _workspace_sk(workspace_id),
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "github": github_config,
        "repos": repos,
        "active": True,
        "created_at": now,
    }

    try:
        table.put_item(Item=item)
    except ClientError as exc:
        raise RuntimeError(
            f"Error al crear workspace {workspace_id}: {exc}"
        ) from exc

    return item


def get_workspace(
    tenant_id: str, workspace_id: str
) -> dict[str, Any] | None:
    """Obtiene un workspace especifico. Retorna None si no existe."""
    table = get_dynamo_client()
    try:
        response = table.get_item(
            Key={
                "PK": _tenant_pk(tenant_id),
                "SK": _workspace_sk(workspace_id),
            }
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al obtener workspace {workspace_id}: {exc}"
        ) from exc
    return response.get("Item")


def list_workspaces(tenant_id: str) -> list[dict[str, Any]]:
    """Lista todos los workspaces de un tenant."""
    table = get_dynamo_client()
    filter_expr = (
        Attr("PK").eq(_tenant_pk(tenant_id))
        & Attr("SK").begins_with("WORKSPACE#")
    )
    try:
        response = table.scan(FilterExpression=filter_expr)
        items: list[dict[str, Any]] = response.get("Items", [])
        while "LastEvaluatedKey" in response:
            response = table.scan(
                FilterExpression=filter_expr,
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))
    except ClientError as exc:
        raise RuntimeError(
            f"Error al listar workspaces de {tenant_id}: {exc}"
        ) from exc
    return items


def delete_workspace(tenant_id: str, workspace_id: str) -> None:
    """Elimina un workspace. Solo si no hay nodos activos trabajando en el."""
    table = get_dynamo_client()
    try:
        table.delete_item(
            Key={
                "PK": _tenant_pk(tenant_id),
                "SK": _workspace_sk(workspace_id),
            }
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al eliminar workspace {workspace_id}: {exc}"
        ) from exc


def update_workspace(
    tenant_id: str, workspace_id: str, **kwargs: Any
) -> None:
    """Actualiza campos arbitrarios de un workspace existente."""
    if not kwargs:
        return

    table = get_dynamo_client()
    # Construir UpdateExpression dinamico
    expr_parts: list[str] = []
    attr_names: dict[str, str] = {}
    attr_values: dict[str, Any] = {}

    for i, (key, value) in enumerate(kwargs.items()):
        placeholder_name = f"#k{i}"
        placeholder_value = f":v{i}"
        expr_parts.append(f"{placeholder_name} = {placeholder_value}")
        attr_names[placeholder_name] = key
        attr_values[placeholder_value] = value

    update_expr = "SET " + ", ".join(expr_parts)

    try:
        table.update_item(
            Key={
                "PK": _tenant_pk(tenant_id),
                "SK": _workspace_sk(workspace_id),
            },
            UpdateExpression=update_expr,
            ExpressionAttributeNames=attr_names,
            ExpressionAttributeValues=attr_values,
        )
    except ClientError as exc:
        raise RuntimeError(
            f"Error al actualizar workspace {workspace_id}: {exc}"
        ) from exc
