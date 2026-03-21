"""Maneja dependencias entre tareas con prefijo DEP# (multi-tenant).

Permite definir relaciones blocker/blocked entre tareas,
resolver dependencias cuando una tarea se completa,
y detectar ciclos antes de crear dependencias circulares.
"""
import time
from typing import Any

from botocore.exceptions import ClientError

from dynamo_client import get_dynamo_client


def _build_dep_pk(tenant_id: str, workspace_id: str, task_id: str) -> str:
    """Construye el prefijo PK para dependencias."""
    return f"TENANT#{tenant_id}|WS#{workspace_id}|DEP#{task_id}"


def _build_dep_sk(blocker_task: str) -> str:
    """Construye el SK para una dependencia especifica."""
    return f"DEPENDS_ON#{blocker_task}"


def add_dependency(
    tenant_id: str,
    workspace_id: str,
    blocked_task: str,
    blocker_task: str,
) -> None:
    """Crea una dependencia: blocked_task depende de blocker_task.

    Antes de crear, verifica que no exista un ciclo.
    Lanza ValueError si se detecta dependencia circular.
    """
    if detect_circular_dependency(
        tenant_id, workspace_id, blocked_task, blocker_task
    ):
        raise ValueError(
            f"Dependencia circular detectada: "
            f"{blocked_task} -> {blocker_task} crea un ciclo"
        )

    table = get_dynamo_client()
    pk = _build_dep_pk(tenant_id, workspace_id, blocked_task)
    sk = _build_dep_sk(blocker_task)

    try:
        table.put_item(Item={
            "PK": pk,
            "SK": sk,
            "blocker_task": blocker_task,
            "blocker_status": "pending",
            "blocked_task": blocked_task,
            "created_at": int(time.time()),
        })
    except ClientError as exc:
        raise RuntimeError(
            f"Error al crear dependencia {blocked_task}->{blocker_task}: {exc}"
        ) from exc


def get_dependencies(
    tenant_id: str,
    workspace_id: str,
    task_id: str,
) -> list[dict]:
    """Retorna todas las dependencias (blockers) de una tarea."""
    table = get_dynamo_client()
    pk = _build_dep_pk(tenant_id, workspace_id, task_id)

    try:
        response = table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
            ExpressionAttributeValues={
                ":pk": pk,
                ":prefix": "DEPENDS_ON#",
            },
        )
        return response.get("Items", [])
    except ClientError as exc:
        raise RuntimeError(
            f"Error al obtener dependencias de {task_id}: {exc}"
        ) from exc


def resolve_dependency(
    tenant_id: str,
    workspace_id: str,
    completed_task: str,
) -> list[str]:
    """Marca como 'done' todas las refs a completed_task como blocker.

    Retorna lista de task_ids que quedaron potencialmente desbloqueados.
    """
    table = get_dynamo_client()
    prefix = f"TENANT#{tenant_id}|WS#{workspace_id}|DEP#"

    try:
        # Scan por items donde blocker_task == completed_task
        response = table.scan(
            FilterExpression=(
                "begins_with(PK, :prefix) AND blocker_task = :task"
            ),
            ExpressionAttributeValues={
                ":prefix": prefix,
                ":task": completed_task,
            },
        )
        items = response.get("Items", [])

        # Paginar si hay mas resultados
        while "LastEvaluatedKey" in response:
            response = table.scan(
                FilterExpression=(
                    "begins_with(PK, :prefix) AND blocker_task = :task"
                ),
                ExpressionAttributeValues={
                    ":prefix": prefix,
                    ":task": completed_task,
                },
                ExclusiveStartKey=response["LastEvaluatedKey"],
            )
            items.extend(response.get("Items", []))

    except ClientError as exc:
        raise RuntimeError(
            f"Error al resolver dependencia {completed_task}: {exc}"
        ) from exc

    potentially_unblocked: list[str] = []

    for item in items:
        try:
            table.update_item(
                Key={"PK": item["PK"], "SK": item["SK"]},
                UpdateExpression="SET blocker_status = :done",
                ExpressionAttributeValues={":done": "done"},
            )
            potentially_unblocked.append(item["blocked_task"])
        except ClientError as exc:
            raise RuntimeError(
                f"Error al actualizar dep {item['PK']}: {exc}"
            ) from exc

    return list(set(potentially_unblocked))


def is_task_unblocked(
    tenant_id: str,
    workspace_id: str,
    task_id: str,
) -> bool:
    """True si la tarea no tiene deps o TODAS sus deps tienen status 'done'."""
    deps = get_dependencies(tenant_id, workspace_id, task_id)
    if not deps:
        return True
    return all(d.get("blocker_status") == "done" for d in deps)


def _get_blockers_of(
    tenant_id: str,
    workspace_id: str,
    task_id: str,
    table: Any,
) -> list[str]:
    """Retorna los blocker_task IDs de una tarea (helper para DFS)."""
    pk = _build_dep_pk(tenant_id, workspace_id, task_id)
    try:
        response = table.query(
            KeyConditionExpression="PK = :pk AND begins_with(SK, :prefix)",
            ExpressionAttributeValues={
                ":pk": pk,
                ":prefix": "DEPENDS_ON#",
            },
        )
        return [
            item["blocker_task"]
            for item in response.get("Items", [])
        ]
    except ClientError:
        return []


def detect_circular_dependency(
    tenant_id: str,
    workspace_id: str,
    blocked_task: str,
    blocker_task: str,
) -> bool:
    """Detecta si agregar blocked->blocker crearia un ciclo (BFS).

    Retorna True si HAY ciclo, False si es seguro crear la dependencia.
    """
    if blocked_task == blocker_task:
        return True

    table = get_dynamo_client()

    # BFS: desde blocker_task, seguir las dependencias
    # Si llegamos a blocked_task, hay ciclo
    visited: set[str] = set()
    queue: list[str] = [blocker_task]

    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)

        blockers = _get_blockers_of(
            tenant_id, workspace_id, current, table
        )
        for b in blockers:
            if b == blocked_task:
                return True
            if b not in visited:
                queue.append(b)

    return False
