"""Tests para swarm_status.py."""
import time
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import pytest


def _runner() -> CliRunner:
    return CliRunner()


# ---------------------------------------------------------------------------
# _ping
# ---------------------------------------------------------------------------


class TestPing:
    def test_ping_none_retorna_guion(self):
        from swarm_status import _ping
        assert _ping(None) == "-"

    def test_ping_reciente_muestra_segundos(self):
        from swarm_status import _ping
        result = _ping(int(time.time()) - 30)
        assert "s" in result

    def test_ping_minutos(self):
        from swarm_status import _ping
        result = _ping(int(time.time()) - 180)
        assert "min" in result


# ---------------------------------------------------------------------------
# _resolve_tenant
# ---------------------------------------------------------------------------


class TestResolveTenant:
    def test_tenant_arg_retorna_directo(self):
        from swarm_status import _resolve_tenant
        assert _resolve_tenant("my-tenant") == "my-tenant"

    def test_auto_detect_desde_config(self):
        from swarm_status import _resolve_tenant
        cfg = {"tenant": {"id": "auto-t"}}
        with patch("swarm_status.load_node_config", return_value=cfg):
            assert _resolve_tenant(None) == "auto-t"

    def test_sin_config_retorna_none(self):
        from swarm_status import _resolve_tenant
        with patch("swarm_status.load_node_config", return_value={}):
            assert _resolve_tenant(None) is None


# ---------------------------------------------------------------------------
# main — muestra nodos activos
# ---------------------------------------------------------------------------


class TestSwarmStatusMain:
    def test_muestra_nodos_activos(self):
        """Debe mostrar nodos del swarm en la salida."""
        from swarm_status import main
        now = int(time.time())
        nodes = [
            {
                "PK": "TENANT#t|NODE#n1",
                "SK": "STATUS",
                "node_id": "n1",
                "capabilities": ["backend"],
                "roles": ["developer"],
                "status": "idle",
                "current_task": None,
                "current_workspace": None,
                "last_heartbeat": now - 10,
            },
        ]
        with patch("swarm_status.load_node_config", return_value={"tenant": {"id": "t"}}), \
             patch("swarm_status.discover_nodes", return_value=nodes), \
             patch("swarm_status.get_recent_messages", return_value=[]), \
             patch("swarm_status.is_task_unblocked", return_value=True), \
             patch("swarm_status.get_available_tasks", return_value=[]):
            result = _runner().invoke(main, ["--tenant", "t"])
        assert result.exit_code == 0
        assert "n1" in result.output
        assert "backend" in result.output

    def test_muestra_mensajes_recientes(self):
        """Debe mostrar mensajes recientes en la salida."""
        from swarm_status import main
        now = int(time.time())
        msgs = [
            {
                "type": "task_completed",
                "task_id": "042",
                "from_node": "n2",
                "created_at": now - 60,
            },
        ]
        with patch("swarm_status.load_node_config", return_value={"tenant": {"id": "t"}}), \
             patch("swarm_status.discover_nodes", return_value=[]), \
             patch("swarm_status.get_recent_messages", return_value=msgs), \
             patch("swarm_status.is_task_unblocked", return_value=True), \
             patch("swarm_status.get_available_tasks", return_value=[]):
            result = _runner().invoke(main, ["--tenant", "t"])
        assert result.exit_code == 0
        assert "task_completed" in result.output
        assert "042" in result.output

    def test_sin_tenant_muestra_error(self):
        """Sin tenant, debe mostrar error."""
        from swarm_status import main
        with patch("swarm_status.load_node_config", return_value={}):
            result = _runner().invoke(main, [])
        assert "No se pudo determinar tenant_id" in result.output
