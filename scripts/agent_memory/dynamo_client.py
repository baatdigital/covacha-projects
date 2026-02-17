"""Cliente DynamoDB para la memoria compartida de Agent Teams.

Single-table design con prefijos: TASK#, LEARNING#, TEAM#, SYNC#
"""
import time
from typing import Any

import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from config import AWS_REGION, DYNAMO_TABLE, LOCK_TTL_SECONDS


def get_dynamo_client() -> Any:
    """Retorna el recurso Table de DynamoDB usando las credenciales del entorno."""
    return boto3.resource("dynamodb", region_name=AWS_REGION).Table(DYNAMO_TABLE)


def _paginate_scan(table: Any, filter_expr: Any) -> list[dict]:
    """Ejecuta un scan paginado y acumula todos los items resultantes."""
    response = table.scan(FilterExpression=filter_expr)
    items: list[dict] = response.get("Items", [])
    while "LastEvaluatedKey" in response:
        response = table.scan(
            FilterExpression=filter_expr,
            ExclusiveStartKey=response["LastEvaluatedKey"],
        )
        items.extend(response.get("Items", []))
    return items


def get_available_tasks(label: str | None = None, status: str = "todo") -> list[dict]:
    """Devuelve tareas con el status indicado, filtrando por label si se provee."""
    table = get_dynamo_client()
    try:
        items = _paginate_scan(table, Attr("SK").eq("META") & Attr("status").eq(status))
    except ClientError as exc:
        raise RuntimeError(f"Error al consultar tareas: {exc}") from exc
    if label:
        items = [t for t in items if label in t.get("labels", [])]
    return items


def get_task(task_id: str) -> dict | None:
    """Obtiene la metadata de una tarea. Retorna None si no existe."""
    table = get_dynamo_client()
    try:
        response = table.get_item(Key={"PK": f"TASK#{task_id}", "SK": "META"})
    except ClientError as exc:
        raise RuntimeError(f"Error al obtener tarea {task_id}: {exc}") from exc
    return response.get("Item")


def claim_task(task_id: str, team: str, machine: str) -> bool:
    """Intenta adquirir el lock de una tarea de forma atómica.

    Usa ConditionExpression para garantizar exclusión mutua.
    Retorna True si el lock fue adquirido, False si ya estaba bloqueada.
    """
    table = get_dynamo_client()
    now = int(time.time())
    try:
        table.put_item(
            Item={
                "PK": f"TASK#{task_id}", "SK": "LOCK",
                "locked_by": team, "locked_at": now,
                "machine": machine, "ttl": now + LOCK_TTL_SECONDS,
            },
            ConditionExpression=Attr("PK").not_exists(),
        )
        return True
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return False
        raise RuntimeError(f"Error al reclamar tarea {task_id}: {exc}") from exc


def release_task(task_id: str, status: str = "done") -> None:
    """Elimina el LOCK de una tarea y actualiza su status en META."""
    table = get_dynamo_client()
    try:
        table.delete_item(Key={"PK": f"TASK#{task_id}", "SK": "LOCK"})
        table.update_item(
            Key={"PK": f"TASK#{task_id}", "SK": "META"},
            UpdateExpression="SET #s = :status",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":status": status},
        )
    except ClientError as exc:
        raise RuntimeError(f"Error al liberar tarea {task_id}: {exc}") from exc


def save_learning(module: str, learning: str, team: str) -> None:
    """Agrega un aprendizaje a gotchas[] del módulo. Inicializa la lista si no existe."""
    table = get_dynamo_client()
    try:
        table.update_item(
            Key={"PK": f"LEARNING#{module}", "SK": "patterns"},
            UpdateExpression=(
                "SET gotchas = list_append(if_not_exists(gotchas, :empty), :new), "
                "updated_by = :team, updated_at = :now"
            ),
            ExpressionAttributeValues={
                ":new": [learning], ":empty": [],
                ":team": team, ":now": int(time.time()),
            },
        )
    except ClientError as exc:
        raise RuntimeError(f"Error al guardar aprendizaje en {module}: {exc}") from exc


def get_learnings(module: str) -> dict:
    """Obtiene los patrones de un módulo. Retorna {} si no existe."""
    table = get_dynamo_client()
    try:
        response = table.get_item(Key={"PK": f"LEARNING#{module}", "SK": "patterns"})
    except ClientError as exc:
        raise RuntimeError(f"Error al obtener aprendizajes de {module}: {exc}") from exc
    return response.get("Item", {})


def update_team_status(team: str, machine: str, current_task: str | None) -> None:
    """Registra o sobreescribe el estado operativo de un equipo/máquina."""
    table = get_dynamo_client()
    try:
        table.put_item(Item={
            "PK": f"TEAM#{team}-{machine}", "SK": "STATUS",
            "team": team, "machine": machine,
            "current_task": current_task, "last_seen": int(time.time()),
        })
    except ClientError as exc:
        raise RuntimeError(f"Error al actualizar estado de {team}: {exc}") from exc


def get_all_team_statuses() -> list[dict]:
    """Devuelve el estado de todos los equipos haciendo scan por SK=STATUS."""
    table = get_dynamo_client()
    try:
        return _paginate_scan(table, Attr("SK").eq("STATUS"))
    except ClientError as exc:
        raise RuntimeError(f"Error al consultar estados de equipos: {exc}") from exc


def update_sync_status(errors: list[str] | None = None) -> None:
    """Registra el timestamp del último sync con GitHub y los errores ocurridos."""
    table = get_dynamo_client()
    try:
        table.put_item(Item={
            "PK": "SYNC#github", "SK": "META",
            "last_sync": int(time.time()), "errors": errors or [],
        })
    except ClientError as exc:
        raise RuntimeError(f"Error al actualizar estado de sync: {exc}") from exc
