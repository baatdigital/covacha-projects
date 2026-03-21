"""Tests para node_registry.py — registro de nodos en DynamoDB con mocks."""
import time
from unittest.mock import MagicMock, patch, call

import pytest
from botocore.exceptions import ClientError


def _mock_table() -> MagicMock:
    """Crea un mock del Table de DynamoDB."""
    table = MagicMock()
    table.scan.return_value = {"Items": []}
    table.get_item.return_value = {}
    table.put_item.return_value = {}
    table.delete_item.return_value = {}
    table.update_item.return_value = {}
    return table


def _sample_node_config() -> dict:
    """Retorna un node_config de ejemplo para tests."""
    return {
        "node_id": "test-node-1",
        "capabilities": ["backend", "testing"],
        "repos": [
            {"path": "/x/covacha-payment", "name": "covacha-payment"},
        ],
        "roles": ["developer"],
    }


# ---------------------------------------------------------------------------
# register_node
# ---------------------------------------------------------------------------

class TestRegisterNode:
    def test_register_node_crea_item_correcto(self):
        """Debe crear item con PK=TENANT#...|NODE#..., status=idle, TTL."""
        from node_registry import register_node

        table = _mock_table()
        with patch("node_registry.get_dynamo_client", return_value=table):
            register_node("baatdigital", _sample_node_config())

        table.put_item.assert_called_once()
        item = table.put_item.call_args[1]["Item"]
        assert item["PK"] == "TENANT#baatdigital|NODE#test-node-1"
        assert item["SK"] == "STATUS"
        assert item["status"] == "idle"
        assert item["node_id"] == "test-node-1"
        assert item["capabilities"] == ["backend", "testing"]
        assert item["current_task"] is None
        assert "ttl" in item
        assert "registered_at" in item
        assert "last_heartbeat" in item


# ---------------------------------------------------------------------------
# heartbeat
# ---------------------------------------------------------------------------

class TestHeartbeat:
    def test_heartbeat_actualiza_last_seen_y_ttl(self):
        """Debe actualizar last_heartbeat y renovar TTL."""
        from node_registry import heartbeat

        table = _mock_table()
        with patch("node_registry.get_dynamo_client", return_value=table):
            heartbeat("baatdigital", "test-node-1")

        table.update_item.assert_called_once()
        kwargs = table.update_item.call_args[1]
        assert kwargs["Key"]["PK"] == "TENANT#baatdigital|NODE#test-node-1"
        assert ":now" in kwargs["ExpressionAttributeValues"]
        assert ":ttl" in kwargs["ExpressionAttributeValues"]


# ---------------------------------------------------------------------------
# discover_nodes
# ---------------------------------------------------------------------------

class TestDiscoverNodes:
    def test_discover_nodes_filtra_stale(self):
        """Con only_active=True, debe filtrar nodos con heartbeat viejo."""
        from node_registry import discover_nodes

        now = int(time.time())
        nodes = [
            {
                "PK": "TENANT#t|NODE#active",
                "SK": "STATUS",
                "node_id": "active",
                "last_heartbeat": now - 10,
                "status": "idle",
            },
            {
                "PK": "TENANT#t|NODE#stale",
                "SK": "STATUS",
                "node_id": "stale",
                "last_heartbeat": now - 600,
                "status": "working",
            },
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": nodes}

        with patch("node_registry.get_dynamo_client", return_value=table):
            result = discover_nodes("t", only_active=True)

        assert len(result) == 1
        assert result[0]["node_id"] == "active"

    def test_discover_nodes_incluye_todos_sin_filtro(self):
        """Con only_active=False, debe retornar todos los nodos."""
        from node_registry import discover_nodes

        now = int(time.time())
        nodes = [
            {
                "PK": "TENANT#t|NODE#a",
                "SK": "STATUS",
                "node_id": "a",
                "last_heartbeat": now - 10,
                "status": "idle",
            },
            {
                "PK": "TENANT#t|NODE#b",
                "SK": "STATUS",
                "node_id": "b",
                "last_heartbeat": now - 9999,
                "status": "idle",
            },
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": nodes}

        with patch("node_registry.get_dynamo_client", return_value=table):
            result = discover_nodes("t", only_active=False)

        assert len(result) == 2


# ---------------------------------------------------------------------------
# get_node
# ---------------------------------------------------------------------------

class TestGetNode:
    def test_get_node_retorna_none_si_no_existe(self):
        """Debe retornar None si el nodo no existe en DynamoDB."""
        from node_registry import get_node

        table = _mock_table()
        table.get_item.return_value = {}

        with patch("node_registry.get_dynamo_client", return_value=table):
            result = get_node("t", "nonexistent")

        assert result is None

    def test_get_node_retorna_item_si_existe(self):
        """Debe retornar el item si existe."""
        from node_registry import get_node

        item = {"PK": "TENANT#t|NODE#n1", "SK": "STATUS", "node_id": "n1"}
        table = _mock_table()
        table.get_item.return_value = {"Item": item}

        with patch("node_registry.get_dynamo_client", return_value=table):
            result = get_node("t", "n1")

        assert result == item


# ---------------------------------------------------------------------------
# check_stale_nodes
# ---------------------------------------------------------------------------

class TestCheckStaleNodes:
    def test_check_stale_nodes_detecta_nodo_sin_heartbeat(self):
        """Detecta nodos con tarea activa y heartbeat viejo."""
        from node_registry import check_stale_nodes

        now = int(time.time())
        nodes = [
            {
                "PK": "TENANT#t|NODE#stale",
                "SK": "STATUS",
                "node_id": "stale",
                "last_heartbeat": now - 600,
                "status": "working",
                "current_task": "ISS-042",
            },
            {
                "PK": "TENANT#t|NODE#ok",
                "SK": "STATUS",
                "node_id": "ok",
                "last_heartbeat": now - 60,
                "status": "working",
                "current_task": "ISS-043",
            },
            {
                "PK": "TENANT#t|NODE#idle-stale",
                "SK": "STATUS",
                "node_id": "idle-stale",
                "last_heartbeat": now - 600,
                "status": "idle",
                "current_task": None,
            },
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": nodes}

        with patch("node_registry.get_dynamo_client", return_value=table):
            result = check_stale_nodes("t", threshold=300)

        # Solo el nodo stale con tarea asignada
        assert len(result) == 1
        assert result[0]["node_id"] == "stale"


# ---------------------------------------------------------------------------
# update_node_status
# ---------------------------------------------------------------------------

class TestUpdateNodeStatus:
    def test_update_node_status_cambia_a_working(self):
        """Debe actualizar status, current_task y current_workspace."""
        from node_registry import update_node_status

        table = _mock_table()
        with patch("node_registry.get_dynamo_client", return_value=table):
            update_node_status(
                "baatdigital", "node-1", "working",
                current_task="ISS-042",
                current_workspace="superpago",
            )

        table.update_item.assert_called_once()
        kwargs = table.update_item.call_args[1]
        values = kwargs["ExpressionAttributeValues"]
        assert values[":status"] == "working"
        assert values[":task"] == "ISS-042"
        assert values[":ws"] == "superpago"


# ---------------------------------------------------------------------------
# deregister_node
# ---------------------------------------------------------------------------

class TestDeregisterNode:
    def test_deregister_node_borra_item(self):
        """Debe borrar el item NODE# de DynamoDB."""
        from node_registry import deregister_node

        table = _mock_table()
        with patch("node_registry.get_dynamo_client", return_value=table):
            deregister_node("baatdigital", "node-1")

        table.delete_item.assert_called_once_with(
            Key={
                "PK": "TENANT#baatdigital|NODE#node-1",
                "SK": "STATUS",
            }
        )


# ---------------------------------------------------------------------------
# get_swarm_summary
# ---------------------------------------------------------------------------

class TestGetSwarmSummary:
    def test_get_swarm_summary_cuenta_idle_y_busy(self):
        """Debe contar nodos idle, busy y agregar capabilities."""
        from node_registry import get_swarm_summary

        now = int(time.time())
        nodes = [
            {
                "PK": "TENANT#t|NODE#a",
                "SK": "STATUS",
                "node_id": "a",
                "status": "idle",
                "capabilities": ["backend", "testing"],
                "last_heartbeat": now - 10,
            },
            {
                "PK": "TENANT#t|NODE#b",
                "SK": "STATUS",
                "node_id": "b",
                "status": "working",
                "capabilities": ["frontend"],
                "last_heartbeat": now - 10,
            },
            {
                "PK": "TENANT#t|NODE#c",
                "SK": "STATUS",
                "node_id": "c",
                "status": "idle",
                "capabilities": ["backend"],
                "last_heartbeat": now - 10,
            },
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": nodes}

        with patch("node_registry.get_dynamo_client", return_value=table):
            result = get_swarm_summary("t")

        assert result["total_nodes"] == 3
        assert len(result["idle"]) == 2
        assert len(result["busy"]) == 1
        assert result["capabilities"]["backend"] == 2
        assert result["capabilities"]["frontend"] == 1
        assert result["capabilities"]["testing"] == 1
