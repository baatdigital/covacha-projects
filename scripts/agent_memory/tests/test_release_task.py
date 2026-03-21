"""Tests para release_task.py con soporte de nodos dinamicos."""
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import pytest


def _runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# release con --node
# ---------------------------------------------------------------------------


class TestReleaseConNode:
    def test_release_resuelve_deps(self):
        """Al liberar con status=done, debe resolver dependencias."""
        from release_task import main
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        with patch("release_task.load_node_config", return_value=cfg), \
             patch("release_task.release_task"), \
             patch("release_task.get_task", return_value={"repo": "covacha-payment"}), \
             patch("release_task.close_issue"), \
             patch("release_task.move_issue_to_status"), \
             patch("release_task.resolve_dependency", return_value=["047"]) as mock_rd, \
             patch("release_task.send_message") as mock_sm, \
             patch("release_task.update_node_status") as mock_uns:
            result = _runner().invoke(main, [
                "--task", "046", "--status", "done",
                "--node", "n1", "--tenant", "t1",
            ])
        assert result.exit_code == 0
        mock_rd.assert_called_once_with("t1", "t1", "046")
        assert "047" in result.output

    def test_release_envia_msg(self):
        """Al completar, debe enviar mensaje task_completed."""
        from release_task import main
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        with patch("release_task.load_node_config", return_value=cfg), \
             patch("release_task.release_task"), \
             patch("release_task.get_task", return_value={"repo": "test"}), \
             patch("release_task.close_issue"), \
             patch("release_task.move_issue_to_status"), \
             patch("release_task.resolve_dependency", return_value=[]), \
             patch("release_task.send_message") as mock_sm, \
             patch("release_task.update_node_status"):
            result = _runner().invoke(main, [
                "--task", "047", "--status", "done",
                "--node", "n1", "--tenant", "t1",
            ])
        assert result.exit_code == 0
        mock_sm.assert_called_once_with(
            "t1", "t1", "n1",
            msg_type="task_completed",
            task_id="047",
        )

    def test_release_publica_contract(self):
        """Si --contract se pasa, debe publicar contrato."""
        from release_task import main
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        contract_json = '{"name":"get-users","version":"1.0","method":"GET","path":"/api/users"}'
        with patch("release_task.load_node_config", return_value=cfg), \
             patch("release_task.release_task"), \
             patch("release_task.get_task", return_value={"repo": "test"}), \
             patch("release_task.close_issue"), \
             patch("release_task.move_issue_to_status"), \
             patch("release_task.resolve_dependency", return_value=[]), \
             patch("release_task.send_message"), \
             patch("release_task.update_node_status"), \
             patch("release_task.publish_contract") as mock_pc:
            result = _runner().invoke(main, [
                "--task", "048", "--status", "done",
                "--node", "n1", "--tenant", "t1",
                "--contract", contract_json,
            ])
        assert result.exit_code == 0
        mock_pc.assert_called_once()
        call_kwargs = mock_pc.call_args[1]
        assert call_kwargs["name"] == "get-users"
        assert call_kwargs["method"] == "GET"


# ---------------------------------------------------------------------------
# backward compat
# ---------------------------------------------------------------------------


class TestReleaseBackwardCompat:
    def test_release_legacy_team_machine(self):
        """Release con --team/--machine sigue funcionando."""
        from release_task import main
        with patch("release_task.load_node_config", return_value={}), \
             patch("release_task.release_task"), \
             patch("release_task.get_task", return_value={"repo": "test"}), \
             patch("release_task.save_learning"), \
             patch("release_task.close_issue"), \
             patch("release_task.move_issue_to_status"), \
             patch("release_task.update_team_status") as mock_ts, \
             patch("release_task.update_node_status"), \
             patch("release_task.resolve_dependency", return_value=[]), \
             patch("release_task.send_message"):
            result = _runner().invoke(main, [
                "--task", "049", "--status", "done",
                "--team", "backend", "--machine", "mac-1",
                "--learning", "usar batch writes",
            ])
        assert result.exit_code == 0
        mock_ts.assert_called_once_with("backend", "mac-1", current_task=None)

    def test_release_no_resuelve_deps_si_blocked(self):
        """Con status=blocked, no debe resolver dependencias."""
        from release_task import main
        with patch("release_task.load_node_config", return_value={}), \
             patch("release_task.release_task"), \
             patch("release_task.get_task", return_value=None), \
             patch("release_task.update_team_status"), \
             patch("release_task.update_node_status"), \
             patch("release_task.resolve_dependency") as mock_rd, \
             patch("release_task.send_message"):
            result = _runner().invoke(main, [
                "--task", "050", "--status", "blocked",
                "--team", "backend", "--machine", "mac-1",
            ])
        assert result.exit_code == 0
        mock_rd.assert_not_called()
