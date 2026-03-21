"""Gestiona asignacion dinamica de roles y acciones por rol.

Asigna roles a nodos del swarm segun sus capabilities,
define acciones disponibles por rol, y procesa mensajes
segun el rol asignado.
"""
from typing import Any

from config import ROLE_REQUIREMENTS


# Acciones disponibles por rol
ROLE_ACTIONS: dict[str, list[str]] = {
    "tech_lead": [
        "review_architecture",
        "publish_contract",
        "approve_pr",
        "define_dependencies",
        "escalate_blocker",
    ],
    "developer": [
        "implement",
        "request_contract",
        "report_integration_issue",
        "update_docs",
    ],
    "tester": [
        "evaluate_ticket",
        "write_regression_tests",
        "run_e2e",
        "review_coverage",
        "report_bug",
    ],
    "project_owner": [
        "accept_ticket",
        "prioritize_backlog",
        "update_epic_status",
        "generate_report",
        "create_cross_issue",
        "sync_board",
    ],
    "reviewer": [
        "review_code",
        "suggest_improvements",
        "check_security",
    ],
}


def assign_roles(nodes: list[dict[str, Any]]) -> dict[str, str]:
    """Asigna roles dinamicamente segun capabilities del swarm.

    Logica:
    1. Primero asignar roles escasos (max_per_swarm=1): tech_lead, project_owner.
    2. Asignar tester si hay nodos con capability 'testing'.
    3. Resto: developer (default).
    4. Preferir nodos que declaran el rol en su config.
    """
    if not nodes:
        return {}

    assignments: dict[str, str] = {}
    assigned_nodes: set[str] = set()

    # Fase 1: roles escasos (max_per_swarm limitado)
    scarce_roles = _get_scarce_roles()
    for role in scarce_roles:
        _assign_scarce_role(role, nodes, assignments, assigned_nodes)

    # Fase 2: tester
    _assign_tester(nodes, assignments, assigned_nodes)

    # Fase 3: developer para el resto
    for node in nodes:
        node_id = node.get("node_id", "")
        if node_id and node_id not in assigned_nodes:
            assignments[node_id] = "developer"
            assigned_nodes.add(node_id)

    return assignments


def _get_scarce_roles() -> list[str]:
    """Retorna roles con max_per_swarm definido, ordenados por prioridad."""
    scarce: list[str] = []
    for role, reqs in ROLE_REQUIREMENTS.items():
        if reqs.get("max_per_swarm") is not None:
            scarce.append(role)
    return scarce


def _assign_scarce_role(
    role: str,
    nodes: list[dict[str, Any]],
    assignments: dict[str, str],
    assigned_nodes: set[str],
) -> None:
    """Asigna un rol escaso al mejor candidato disponible."""
    reqs = ROLE_REQUIREMENTS.get(role, {})
    required_caps = set(reqs.get("required_caps", []))
    preferred_caps = set(reqs.get("preferred_caps", []))

    best_node: str | None = None
    best_score: int = -1

    for node in nodes:
        node_id = node.get("node_id", "")
        if not node_id or node_id in assigned_nodes:
            continue

        caps = set(node.get("capabilities", []))
        roles_declared = node.get("roles", [])

        # Debe tener caps requeridas
        if required_caps and not required_caps.issubset(caps):
            continue

        score = len(preferred_caps & caps)
        # Bonus si declara el rol en su config
        if role in roles_declared:
            score += 10

        if score > best_score:
            best_score = score
            best_node = node_id

    if best_node is not None:
        assignments[best_node] = role
        assigned_nodes.add(best_node)


def _assign_tester(
    nodes: list[dict[str, Any]],
    assignments: dict[str, str],
    assigned_nodes: set[str],
) -> None:
    """Asigna rol tester a nodos con capability 'testing' no asignados."""
    for node in nodes:
        node_id = node.get("node_id", "")
        if not node_id or node_id in assigned_nodes:
            continue
        caps = set(node.get("capabilities", []))
        roles_declared = node.get("roles", [])
        if "testing" in caps or "tester" in roles_declared:
            assignments[node_id] = "tester"
            assigned_nodes.add(node_id)


def get_role_actions(role: str) -> list[str]:
    """Retorna acciones disponibles para un rol."""
    return ROLE_ACTIONS.get(role, [])


def can_perform_action(role: str, action: str) -> bool:
    """Verifica si un rol puede hacer una accion."""
    actions = ROLE_ACTIONS.get(role, [])
    return action in actions


def process_message_for_role(
    role: str, message: dict[str, Any]
) -> dict[str, Any] | None:
    """Decide que hacer con un mensaje segun el rol.

    Retorna dict con {action, params} o None si no aplica.
    """
    msg_type = message.get("type", "")
    task_id = message.get("task_id", "")
    payload = message.get("payload", {})

    handler = _MESSAGE_HANDLERS.get((role, msg_type))
    if handler is None:
        return None
    return handler(task_id, payload)


def _handle_tester_task_completed(
    task_id: str, payload: dict
) -> dict[str, Any]:
    """Tester recibe task_completed -> evaluar ticket."""
    return {
        "action": "evaluate_ticket",
        "params": {"task_id": task_id, "type": "qa_review"},
    }


def _handle_po_qa_approved(
    task_id: str, payload: dict
) -> dict[str, Any]:
    """PO recibe qa_approved -> evaluar aceptacion."""
    return {
        "action": "evaluate_ticket",
        "params": {"task_id": task_id, "type": "po_acceptance"},
    }


def _handle_tech_lead_bug_found(
    task_id: str, payload: dict
) -> dict[str, Any]:
    """Tech lead recibe bug_found -> crear bugfix."""
    return {
        "action": "create_bugfix",
        "params": {"details": payload},
    }


def _handle_dev_contract_published(
    task_id: str, payload: dict
) -> dict[str, Any]:
    """Developer recibe contract_published -> cargar contrato."""
    return {
        "action": "load_contract",
        "params": {"contract_id": payload.get("contract_id", "")},
    }


def _handle_dev_qa_rejected(
    task_id: str, payload: dict
) -> dict[str, Any]:
    """Developer recibe qa_rejected -> fix issues."""
    return {
        "action": "fix_issues",
        "params": {"task_id": task_id, "details": payload},
    }


# Mapeo (rol, tipo_mensaje) -> handler
_MESSAGE_HANDLERS: dict[
    tuple[str, str],
    Any,
] = {
    ("tester", "task_completed"): _handle_tester_task_completed,
    ("project_owner", "qa_approved"): _handle_po_qa_approved,
    ("tech_lead", "bug_found"): _handle_tech_lead_bug_found,
    ("developer", "contract_published"): _handle_dev_contract_published,
    ("developer", "qa_rejected"): _handle_dev_qa_rejected,
}
