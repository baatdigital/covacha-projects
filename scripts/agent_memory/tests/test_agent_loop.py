"""Tests para agent_loop.py — daemon autonomo del swarm."""
from unittest.mock import MagicMock, patch, call

import pytest

from agent_loop import AgentLoop, extract_learnings


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _node_config() -> dict:
    """Retorna un node_config de ejemplo."""
    return {
        "node_id": "test-node-1",
        "auto_switch_workspace": False,
        "workspaces": [{
            "id": "ws-test",
            "repos": [{"path": "/x/covacha-payment", "name": "covacha-payment"}],
            "capabilities": ["backend", "testing"],
        }],
    }


def _sample_task() -> dict:
    """Retorna una tarea de ejemplo."""
    return {
        "number": "043",
        "title": "Implementar SPEI transfer",
        "repo": "covacha-payment",
        "labels": ["backend"],
        "recommended_model": "sonnet",
    }


def _make_loop() -> AgentLoop:
    """Crea un AgentLoop con mocks minimos."""
    return AgentLoop("baatdigital", _node_config(), "ws-test")


# ---------------------------------------------------------------------------
# _iteration
# ---------------------------------------------------------------------------

class TestIteration:
    @patch("agent_loop.time.sleep")
    @patch("agent_loop.find_next_task", return_value=None)
    @patch("agent_loop.get_unread_messages", return_value=[])
    @patch("agent_loop.heartbeat")
    def test_sin_tareas_espera(self, _hb, _msgs, _find, mock_sleep):
        """Debe dormir AGENT_LOOP_POLL_INTERVAL si no hay tareas."""
        loop = _make_loop()
        loop._iteration()

        mock_sleep.assert_called_once()
        interval = mock_sleep.call_args[0][0]
        assert interval > 0

    @patch("agent_loop.AgentLoop._release_and_notify")
    @patch("agent_loop.AgentLoop._run_claude_code")
    @patch("agent_loop.update_node_status")
    @patch("agent_loop.claim_task", return_value=True)
    @patch("agent_loop.find_next_task")
    @patch("agent_loop.get_unread_messages", return_value=[])
    @patch("agent_loop.heartbeat")
    def test_claim_y_ejecuta(
        self, _hb, _msgs, mock_find, mock_claim,
        mock_status, mock_run, mock_release,
    ):
        """Debe claim + ejecutar cuando hay tarea disponible."""
        task = _sample_task()
        mock_find.return_value = task
        mock_run.return_value = {
            "status": "done", "learnings": [], "error": "",
        }

        loop = _make_loop()
        loop._iteration()

        mock_claim.assert_called_once_with("043", "test-node-1", "test-node-1")
        mock_run.assert_called_once_with(task)
        mock_release.assert_called_once()

    @patch("agent_loop.find_next_task")
    @patch("agent_loop.claim_task", return_value=False)
    @patch("agent_loop.get_unread_messages", return_value=[])
    @patch("agent_loop.heartbeat")
    def test_claim_collision_reintenta(
        self, _hb, _msgs, mock_claim, mock_find,
    ):
        """Debe no ejecutar si claim falla (collision)."""
        mock_find.return_value = _sample_task()

        loop = _make_loop()
        loop._iteration()

        mock_claim.assert_called_once()
        # No debe haber ejecucion de Claude Code


# ---------------------------------------------------------------------------
# _execute_task
# ---------------------------------------------------------------------------

class TestExecuteTask:
    @patch("agent_loop.send_message")
    @patch("agent_loop.resolve_dependency")
    @patch("agent_loop.update_node_status")
    @patch("agent_loop.release_task")
    @patch("agent_loop.save_learning")
    @patch("agent_loop.AgentLoop._run_claude_code")
    @patch("agent_loop.claim_task", return_value=True)
    def test_done_resuelve_deps(
        self, _claim, mock_run, _learn, mock_release,
        mock_status, mock_resolve, mock_msg,
    ):
        """Debe resolver dependencias y enviar msg cuando task done."""
        mock_run.return_value = {
            "status": "done", "learnings": [], "error": "",
        }

        loop = _make_loop()
        loop._execute_task(_sample_task())

        mock_release.assert_called_once_with("043", "done")
        mock_resolve.assert_called_once_with("baatdigital", "ws-test", "043")
        mock_msg.assert_called_once()
        assert mock_msg.call_args[0][3] == "task_completed"

    @patch("agent_loop.send_message")
    @patch("agent_loop.update_node_status")
    @patch("agent_loop.release_task")
    @patch("agent_loop.AgentLoop._run_claude_code")
    @patch("agent_loop.claim_task", return_value=True)
    def test_blocked_envia_msg(
        self, _claim, mock_run, mock_release,
        mock_status, mock_msg,
    ):
        """Debe enviar msg task_blocked cuando la ejecucion falla."""
        mock_run.return_value = {
            "status": "blocked", "learnings": [],
            "error": "Timeout (1h)",
        }

        loop = _make_loop()
        loop._execute_task(_sample_task())

        mock_release.assert_called_once_with("043", "blocked")
        mock_msg.assert_called_once()
        assert mock_msg.call_args[0][3] == "task_blocked"


# ---------------------------------------------------------------------------
# _shutdown
# ---------------------------------------------------------------------------

class TestShutdown:
    @patch("agent_loop.deregister_node")
    @patch("agent_loop.send_message")
    @patch("agent_loop.update_node_status")
    def test_deregistra_nodo(self, mock_status, mock_msg, mock_dereg):
        """Debe actualizar status a leaving y desregistrar."""
        loop = _make_loop()
        loop._shutdown()

        mock_status.assert_called_once_with(
            "baatdigital", "test-node-1", "leaving"
        )
        mock_msg.assert_called_once()
        assert mock_msg.call_args[0][3] == "node_left"
        mock_dereg.assert_called_once_with("baatdigital", "test-node-1")


# ---------------------------------------------------------------------------
# _process_messages
# ---------------------------------------------------------------------------

class TestProcessMessages:
    @patch("agent_loop.mark_as_read")
    @patch("agent_loop.get_unread_messages")
    def test_marca_como_leidas(self, mock_get, mock_mark):
        """Debe marcar cada mensaje como leido."""
        mock_get.return_value = [
            {"PK": "MSG#1-node-2", "type": "task_completed", "from_node": "node-2", "task_id": "042"},
            {"PK": "MSG#2-node-3", "type": "task_blocked", "from_node": "node-3", "task_id": "043"},
        ]

        loop = _make_loop()
        loop._process_messages()

        assert mock_mark.call_count == 2
        mock_mark.assert_any_call("baatdigital", "ws-test", "MSG#1-node-2", "test-node-1")
        mock_mark.assert_any_call("baatdigital", "ws-test", "MSG#2-node-3", "test-node-1")


# ---------------------------------------------------------------------------
# extract_learnings
# ---------------------------------------------------------------------------

class TestExtractLearnings:
    def test_del_output(self):
        """Debe extraer learnings con prefijos conocidos."""
        output = (
            "Linea normal\n"
            "Learning: usar Decimal para montos\n"
            "otra linea\n"
            "Gotcha: CLABE tiene 18 digitos\n"
            "Aprendizaje: validar referencia numerica\n"
        )
        result = extract_learnings(output)

        assert len(result) == 3
        assert "usar Decimal para montos" in result
        assert "CLABE tiene 18 digitos" in result
        assert "validar referencia numerica" in result

    def test_output_vacio(self):
        """Debe retornar lista vacia con output vacio."""
        assert extract_learnings("") == []
        assert extract_learnings(None) == []

    def test_sin_learnings(self):
        """Debe retornar lista vacia si no hay prefijos."""
        assert extract_learnings("solo texto normal\nsin learnings\n") == []
