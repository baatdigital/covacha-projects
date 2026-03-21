"""Tests para role_manager.py — asignacion de roles y acciones."""
import pytest

from role_manager import (
    assign_roles,
    can_perform_action,
    get_role_actions,
    process_message_for_role,
)


# ── assign_roles ─────────────────────────────────────────────

def test_assign_roles_1_nodo_hace_todo() -> None:
    """Con 1 solo nodo, se le asigna developer (default)."""
    nodes = [
        {"node_id": "mac-1", "capabilities": ["backend"], "roles": ["developer"]},
    ]
    result = assign_roles(nodes)
    assert result == {"mac-1": "tech_lead"}


def test_assign_roles_2_nodos_separa_roles() -> None:
    """Con 2 nodos, separa tech_lead y developer."""
    nodes = [
        {"node_id": "mac-1", "capabilities": ["backend"], "roles": ["tech_lead"]},
        {"node_id": "mac-2", "capabilities": ["frontend"], "roles": ["developer"]},
    ]
    result = assign_roles(nodes)
    assert result["mac-1"] == "tech_lead"
    assert result["mac-2"] == "developer"


def test_assign_roles_5_nodos_especializados() -> None:
    """Con 5 nodos, asigna roles especializados correctamente."""
    nodes = [
        {"node_id": "mac-1", "capabilities": ["backend", "architecture"], "roles": ["tech_lead"]},
        {"node_id": "mac-2", "capabilities": ["frontend"], "roles": ["developer"]},
        {"node_id": "mac-3", "capabilities": ["testing", "e2e"], "roles": ["tester"]},
        {"node_id": "mac-4", "capabilities": ["ops"], "roles": ["project_owner"]},
        {"node_id": "mac-5", "capabilities": ["backend"], "roles": ["developer"]},
    ]
    result = assign_roles(nodes)
    assert result["mac-1"] == "tech_lead"
    assert result["mac-4"] == "project_owner"
    assert result["mac-3"] == "tester"
    assert result["mac-2"] == "developer"
    assert result["mac-5"] == "developer"


def test_assign_roles_solo_1_tech_lead() -> None:
    """Solo puede haber 1 tech_lead aunque 2 nodos tengan capabilities."""
    nodes = [
        {"node_id": "mac-1", "capabilities": ["backend"], "roles": ["tech_lead"]},
        {"node_id": "mac-2", "capabilities": ["backend"], "roles": ["tech_lead"]},
        {"node_id": "mac-3", "capabilities": ["frontend"], "roles": []},
    ]
    result = assign_roles(nodes)
    tech_leads = [nid for nid, role in result.items() if role == "tech_lead"]
    assert len(tech_leads) == 1


def test_assign_roles_solo_1_project_owner() -> None:
    """Solo puede haber 1 project_owner."""
    nodes = [
        {"node_id": "mac-1", "capabilities": ["ops"], "roles": ["project_owner"]},
        {"node_id": "mac-2", "capabilities": ["ops"], "roles": ["project_owner"]},
    ]
    result = assign_roles(nodes)
    pos = [nid for nid, role in result.items() if role == "project_owner"]
    assert len(pos) == 1


# ── get_role_actions ─────────────────────────────────────────

def test_get_role_actions_developer() -> None:
    """Developer tiene acciones de implementacion."""
    actions = get_role_actions("developer")
    assert "implement" in actions
    assert "request_contract" in actions
    assert "report_integration_issue" in actions
    assert "update_docs" in actions


def test_get_role_actions_tester() -> None:
    """Tester tiene acciones de evaluacion y testing."""
    actions = get_role_actions("tester")
    assert "evaluate_ticket" in actions
    assert "write_regression_tests" in actions
    assert "run_e2e" in actions
    assert "review_coverage" in actions
    assert "report_bug" in actions


# ── can_perform_action ───────────────────────────────────────

def test_can_perform_action_valido() -> None:
    """Un rol puede hacer sus acciones asignadas."""
    assert can_perform_action("tech_lead", "review_architecture") is True
    assert can_perform_action("developer", "implement") is True
    assert can_perform_action("tester", "evaluate_ticket") is True
    assert can_perform_action("project_owner", "accept_ticket") is True
    assert can_perform_action("reviewer", "review_code") is True


def test_can_perform_action_invalido() -> None:
    """Un rol NO puede hacer acciones de otro rol."""
    assert can_perform_action("developer", "review_architecture") is False
    assert can_perform_action("tester", "implement") is False
    assert can_perform_action("project_owner", "review_code") is False
    assert can_perform_action("nonexistent_role", "anything") is False


# ── process_message_for_role ─────────────────────────────────

def test_process_message_tester_task_completed() -> None:
    """Tester recibe task_completed -> evaluar ticket como QA."""
    msg = {"type": "task_completed", "task_id": "043", "payload": {}}
    result = process_message_for_role("tester", msg)
    assert result is not None
    assert result["action"] == "evaluate_ticket"
    assert result["params"]["task_id"] == "043"
    assert result["params"]["type"] == "qa_review"


def test_process_message_po_qa_approved() -> None:
    """PO recibe qa_approved -> evaluar aceptacion."""
    msg = {"type": "qa_approved", "task_id": "043", "payload": {}}
    result = process_message_for_role("project_owner", msg)
    assert result is not None
    assert result["action"] == "evaluate_ticket"
    assert result["params"]["type"] == "po_acceptance"


def test_process_message_developer_contract_published() -> None:
    """Developer recibe contract_published -> cargar contrato."""
    msg = {
        "type": "contract_published",
        "task_id": "043",
        "payload": {"contract_id": "spei-transfer-v1"},
    }
    result = process_message_for_role("developer", msg)
    assert result is not None
    assert result["action"] == "load_contract"
    assert result["params"]["contract_id"] == "spei-transfer-v1"


def test_process_message_irrelevante_retorna_none() -> None:
    """Mensajes que no aplican al rol retornan None."""
    # Developer no procesa task_completed
    msg = {"type": "task_completed", "task_id": "043", "payload": {}}
    assert process_message_for_role("developer", msg) is None

    # Tester no procesa contract_published
    msg2 = {"type": "contract_published", "task_id": "043", "payload": {}}
    assert process_message_for_role("tester", msg2) is None

    # Rol inexistente
    msg3 = {"type": "task_completed", "task_id": "043", "payload": {}}
    assert process_message_for_role("nonexistent", msg3) is None
