"""Logica de busqueda inteligente de siguiente tarea para un nodo.

Filtra por compatibilidad, dependencias, locks, y ordena
por score de asignacion para encontrar la mejor tarea disponible.
"""
from typing import Any

from dynamo_client import get_available_tasks, get_task
from dependency_manager import is_task_unblocked


# Labels que implican prioridad alta (P1)
_P1_LABELS: set[str] = {"architecture", "security", "critical"}
# Labels de prioridad media (P2)
_P2_LABELS: set[str] = {"feature", "bugfix", "backend", "frontend"}
# Labels de prioridad baja (P3)
_P3_LABELS: set[str] = {"docs", "chore", "tracking", "sync"}


def _get_node_repos(node_config: dict) -> set[str]:
    """Extrae los nombres de repos del node_config."""
    repos: set[str] = set()
    for ws in node_config.get("workspaces", []):
        for repo in ws.get("repos", []):
            name = repo.get("name", "")
            if name:
                repos.add(name)
    return repos


def _get_node_capabilities(node_config: dict) -> set[str]:
    """Extrae las capabilities del node_config."""
    caps: set[str] = set()
    for ws in node_config.get("workspaces", []):
        for cap in ws.get("capabilities", []):
            caps.add(cap)
    return caps


def is_task_compatible(task: dict, node_config: dict) -> bool:
    """Verifica si una tarea es compatible con el nodo.

    Requiere que el repo de la tarea este en los repos del nodo
    y que al menos 1 label de la tarea matchee 1 capability.
    """
    task_repo = task.get("repo", "")
    node_repos = _get_node_repos(node_config)

    if task_repo and task_repo not in node_repos:
        return False

    task_labels = set(task.get("labels", []))
    node_caps = _get_node_capabilities(node_config)

    if not task_labels or not node_caps:
        return bool(not task_repo or task_repo in node_repos)

    return bool(task_labels & node_caps)


def _infer_priority(labels: list[str]) -> float:
    """Infiere score de prioridad a partir de labels."""
    label_set = set(labels)
    if label_set & _P1_LABELS:
        return 0.2
    if label_set & _P2_LABELS:
        return 0.14
    return 0.08


def score_assignment(task: dict, node_config: dict) -> float:
    """Calcula score de asignacion (0.0 a 1.0) para una tarea.

    Componentes:
    - Capability match (0.0-0.4): overlap labels/capabilities
    - Repo locality (0.0-0.3): nodo tiene el repo
    - Priority (0.0-0.2): segun labels
    - Idle bonus (0.0-0.1): nodo esta idle
    """
    score = 0.0

    # Capability match (0.0-0.4)
    task_labels = set(task.get("labels", []))
    node_caps = _get_node_capabilities(node_config)
    if task_labels:
        overlap = len(task_labels & node_caps)
        score += 0.4 * (overlap / len(task_labels))

    # Repo locality (0.0-0.3)
    task_repo = task.get("repo", "")
    node_repos = _get_node_repos(node_config)
    if task_repo and task_repo in node_repos:
        score += 0.3

    # Priority (0.0-0.2)
    score += _infer_priority(task.get("labels", []))

    # Idle bonus (0.0-0.1)
    node_status = node_config.get("status", "idle")
    if node_status == "idle":
        score += 0.1

    return round(score, 4)


def _has_lock(task_id: str) -> bool:
    """Verifica si una tarea tiene lock activo."""
    try:
        item = get_task(str(task_id))
        if not item:
            return False
        lock = get_task(str(task_id))
        # Revisar si existe LOCK SK separado
        from dynamo_client import get_dynamo_client
        table = get_dynamo_client()
        resp = table.get_item(
            Key={"PK": f"TASK#{task_id}", "SK": "LOCK"}
        )
        return "Item" in resp
    except Exception:
        return False


def find_next_task(
    tenant_id: str,
    workspace_id: str,
    node_config: dict,
) -> dict | None:
    """Busca la siguiente mejor tarea disponible para el nodo.

    Filtra por compatibilidad, dependencias resueltas y locks.
    Ordena por score y retorna la mejor, o None si no hay.
    """
    tasks = get_available_tasks(status="todo")

    candidates: list[tuple[float, dict]] = []
    for task in tasks:
        if not is_task_compatible(task, node_config):
            continue

        task_id = str(task.get("number", ""))
        if not task_id:
            continue

        if not is_task_unblocked(tenant_id, workspace_id, task_id):
            continue

        if _has_lock(task_id):
            continue

        s = score_assignment(task, node_config)
        candidates.append((s, task))

    if not candidates:
        return None

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def find_next_across_workspaces(
    tenant_id: str,
    node_config: dict,
) -> tuple[str, dict] | None:
    """Busca tarea en todos los workspaces del nodo.

    Solo se usa cuando auto_switch_workspace=true.
    Retorna (workspace_id, task) o None.
    """
    workspaces = node_config.get("workspaces", [])
    best: tuple[float, str, dict] | None = None

    for ws in workspaces:
        ws_id = ws.get("id", "")
        if not ws_id:
            continue
        task = find_next_task(tenant_id, ws_id, node_config)
        if task:
            s = score_assignment(task, node_config)
            if best is None or s > best[0]:
                best = (s, ws_id, task)

    if best is None:
        return None
    return (best[1], best[2])
