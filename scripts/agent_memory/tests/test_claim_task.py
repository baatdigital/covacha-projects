"""Tests para claim_task.py con soporte de nodos dinamicos."""
import warnings
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import pytest


def _runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# _resolve_node_id
# ---------------------------------------------------------------------------


class TestResolveNodeId:
    def test_node_arg_retorna_directo(self):
        """Si --node se pasa, retorna ese node_id."""
        from claim_task import _resolve_node_id
        with patch("claim_task.load_node_config", return_value={"tenant": {"id": "t1"}}):
            nid, tid = _resolve_node_id("my-node", None, None)
        assert nid == "my-node"
        assert tid == "t1"

    def test_auto_detect_desde_config(self):
        """Sin --node, auto-detecta desde ~/.covacha-node.yml."""
        from claim_task import _resolve_node_id
        cfg = {"node_id": "auto-node", "tenant": {"id": "tenant-x"}}
        with patch("claim_task.load_node_config", return_value=cfg):
            nid, tid = _resolve_node_id(None, None, None)
        assert nid == "auto-node"
        assert tid == "tenant-x"

    def test_fallback_legacy_team_machine(self):
        """Con --team/--machine sin config, genera node_id legacy con warning."""
        from claim_task import _resolve_node_id
        with patch("claim_task.load_node_config", return_value={}):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                nid, tid = _resolve_node_id(None, "backend", "mac-1")
        assert nid == "backend-mac-1"
        assert tid is None
        assert len(w) == 1
        assert "deprecados" in str(w[0].message)

    def test_sin_nada_retorna_none(self):
        """Sin argumentos ni config, retorna None."""
        from claim_task import _resolve_node_id
        with patch("claim_task.load_node_config", return_value={}):
            nid, tid = _resolve_node_id(None, None, None)
        assert nid is None
        assert tid is None


# ---------------------------------------------------------------------------
# claim con --node
# ---------------------------------------------------------------------------


class TestClaimConNode:
    def test_claim_con_node_arg(self):
        """Claim con --node debe funcionar y llamar update_node_status."""
        from claim_task import main
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        with patch("claim_task.load_node_config", return_value=cfg), \
             patch("claim_task.claim_task", return_value=True), \
             patch("claim_task.get_task", return_value=None), \
             patch("claim_task.update_node_status") as mock_uns, \
             patch("claim_task.heartbeat") as mock_hb, \
             patch("claim_task.is_task_unblocked", return_value=True), \
             patch("claim_task.get_branch_for_issue", return_value=None):
            result = _runner().invoke(main, ["--task", "042", "--node", "n1", "--tenant", "t1"])
        assert result.exit_code == 0
        mock_uns.assert_called_once()
        mock_hb.assert_called_once()

    def test_claim_auto_detect_node(self):
        """Claim sin --node auto-detecta desde config."""
        from claim_task import main
        cfg = {"node_id": "auto-n", "tenant": {"id": "t2"}}
        with patch("claim_task.load_node_config", return_value=cfg), \
             patch("claim_task.claim_task", return_value=True), \
             patch("claim_task.get_task", return_value=None), \
             patch("claim_task.update_node_status") as mock_uns, \
             patch("claim_task.heartbeat") as mock_hb, \
             patch("claim_task.is_task_unblocked", return_value=True), \
             patch("claim_task.get_branch_for_issue", return_value=None):
            result = _runner().invoke(main, ["--task", "043"])
        assert result.exit_code == 0
        mock_uns.assert_called_once()

    def test_claim_verifica_deps_bloqueada(self):
        """Si la tarea tiene deps pendientes, no se reclama."""
        from claim_task import main
        cfg = {"node_id": "n1", "tenant": {"id": "t1"}}
        with patch("claim_task.load_node_config", return_value=cfg), \
             patch("claim_task.is_task_unblocked", return_value=False), \
             patch("claim_task.claim_task") as mock_claim:
            result = _runner().invoke(main, ["--task", "044", "--node", "n1", "--tenant", "t1"])
        assert result.exit_code != 0
        mock_claim.assert_not_called()


# ---------------------------------------------------------------------------
# backward compat con --team/--machine
# ---------------------------------------------------------------------------


class TestClaimBackwardCompat:
    def test_claim_legacy_team_machine(self):
        """Claim con --team/--machine sigue funcionando."""
        from claim_task import main
        with patch("claim_task.load_node_config", return_value={}), \
             patch("claim_task.claim_task", return_value=True), \
             patch("claim_task.get_task", return_value=None), \
             patch("claim_task.update_team_status") as mock_ts, \
             patch("claim_task.update_node_status"), \
             patch("claim_task.heartbeat"), \
             patch("claim_task.is_task_unblocked", return_value=True), \
             patch("claim_task.get_branch_for_issue", return_value=None):
            result = _runner().invoke(main, [
                "--task", "045", "--team", "backend", "--machine", "mac-1",
            ])
        assert result.exit_code == 0
        mock_ts.assert_called_once_with("backend", "mac-1", current_task="045")

    def test_claim_falla_si_ya_bloqueada(self):
        """Si el lock ya existe, debe fallar con exit code 1."""
        from claim_task import main
        with patch("claim_task.load_node_config", return_value={}), \
             patch("claim_task.claim_task", return_value=False), \
             patch("claim_task.is_task_unblocked", return_value=True):
            result = _runner().invoke(main, [
                "--task", "046", "--team", "backend", "--machine", "mac-1",
            ])
        assert result.exit_code != 0
