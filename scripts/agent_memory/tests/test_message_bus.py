"""Tests para message_bus.py — mock DynamoDB, test mensajes broadcast/direct."""
import pytest
from unittest.mock import MagicMock, patch

TENANT = "baatdigital"
WS = "superpago"
MSG_PREFIX = f"TENANT#{TENANT}|WS#{WS}|MSG#"


def _mock_table():
    """Crea un mock del Table de DynamoDB."""
    table = MagicMock()
    table.put_item.return_value = {}
    table.scan.return_value = {"Items": []}
    table.query.return_value = {"Items": []}
    table.update_item.return_value = {}
    return table


class TestSendMessage:
    def test_send_message_broadcast_crea_item(self):
        from message_bus import send_message

        table = _mock_table()
        with patch("message_bus.get_dynamo_client", return_value=table), \
             patch("message_bus.time") as mock_time:
            mock_time.time.return_value = 1711036800
            result = send_message(
                TENANT, WS, "node-1", "task_completed",
                task_id="043", payload={"branch": "feature/x"}
            )

        table.put_item.assert_called_once()
        item = table.put_item.call_args[1]["Item"]
        assert item["SK"] == "BROADCAST"
        assert item["from_node"] == "node-1"
        assert item["type"] == "task_completed"
        assert item["task_id"] == "043"
        assert item["payload"] == {"branch": "feature/x"}
        assert item["read_by"] == []
        assert item["ttl"] == 1711036800 + 86400
        assert "MSG#" in result

    def test_send_message_direct_crea_con_sk_direct(self):
        from message_bus import send_message

        table = _mock_table()
        with patch("message_bus.get_dynamo_client", return_value=table), \
             patch("message_bus.time") as mock_time:
            mock_time.time.return_value = 1711036800
            result = send_message(
                TENANT, WS, "node-1", "review_requested",
                to_node="node-2"
            )

        item = table.put_item.call_args[1]["Item"]
        assert item["SK"] == "DIRECT#node-2"

    def test_message_tipos_validos(self):
        from message_bus import send_message

        table = _mock_table()
        with patch("message_bus.get_dynamo_client", return_value=table), \
             patch("message_bus.time") as mock_time:
            mock_time.time.return_value = 1711036800

            with pytest.raises(ValueError, match="invalido"):
                send_message(TENANT, WS, "node-1", "tipo_inexistente")

    def test_send_message_sin_payload_usa_defaults(self):
        from message_bus import send_message

        table = _mock_table()
        with patch("message_bus.get_dynamo_client", return_value=table), \
             patch("message_bus.time") as mock_time:
            mock_time.time.return_value = 1711036800
            send_message(TENANT, WS, "node-1", "node_joined")

        item = table.put_item.call_args[1]["Item"]
        assert item["payload"] == {}
        assert item["task_id"] == ""


class TestGetUnreadMessages:
    def test_get_unread_messages_filtra_leidos(self):
        from message_bus import get_unread_messages

        table = _mock_table()
        items = [
            {"PK": f"{MSG_PREFIX}100-node-1", "SK": "BROADCAST",
             "from_node": "node-1", "read_by": [], "created_at": 100},
            {"PK": f"{MSG_PREFIX}200-node-2", "SK": "BROADCAST",
             "from_node": "node-2", "read_by": ["node-3"], "created_at": 200},
        ]
        table.scan.return_value = {"Items": items}

        with patch("message_bus.get_dynamo_client", return_value=table):
            result = get_unread_messages(TENANT, WS, "node-3")

        # node-3 ya leyo el segundo mensaje, solo ve el primero
        assert len(result) == 1
        assert result[0]["from_node"] == "node-1"

    def test_get_unread_messages_respeta_limit(self):
        from message_bus import get_unread_messages

        table = _mock_table()
        items = [
            {"PK": f"{MSG_PREFIX}{i}-node-1", "SK": "BROADCAST",
             "from_node": "node-1", "read_by": [], "created_at": i}
            for i in range(10)
        ]
        table.scan.return_value = {"Items": items}

        with patch("message_bus.get_dynamo_client", return_value=table):
            result = get_unread_messages(TENANT, WS, "node-3", limit=3)

        assert len(result) == 3

    def test_get_unread_messages_direct_solo_destinatario(self):
        from message_bus import get_unread_messages

        table = _mock_table()
        items = [
            {"PK": f"{MSG_PREFIX}100-node-1", "SK": "DIRECT#node-2",
             "from_node": "node-1", "read_by": [], "created_at": 100},
            {"PK": f"{MSG_PREFIX}200-node-1", "SK": "BROADCAST",
             "from_node": "node-1", "read_by": [], "created_at": 200},
        ]
        table.scan.return_value = {"Items": items}

        with patch("message_bus.get_dynamo_client", return_value=table):
            # node-3 NO es destinatario del DIRECT a node-2
            result = get_unread_messages(TENANT, WS, "node-3")

        assert len(result) == 1
        assert result[0]["SK"] == "BROADCAST"

        with patch("message_bus.get_dynamo_client", return_value=table):
            # node-2 SI es destinatario
            result = get_unread_messages(TENANT, WS, "node-2")

        assert len(result) == 2


class TestMarkAsRead:
    def test_mark_as_read_agrega_a_read_by(self):
        from message_bus import mark_as_read

        table = _mock_table()
        msg_pk = f"{MSG_PREFIX}100-node-1"
        table.query.return_value = {
            "Items": [{"PK": msg_pk, "SK": "BROADCAST", "read_by": []}]
        }

        with patch("message_bus.get_dynamo_client", return_value=table):
            mark_as_read(TENANT, WS, msg_pk, "node-3")

        table.update_item.assert_called_once()
        update_args = table.update_item.call_args[1]
        assert update_args["Key"] == {"PK": msg_pk, "SK": "BROADCAST"}
        vals = update_args["ExpressionAttributeValues"]
        assert vals[":node"] == ["node-3"]


class TestGetRecentMessages:
    def test_get_recent_messages_sin_filtro(self):
        from message_bus import get_recent_messages

        table = _mock_table()
        items = [
            {"PK": f"{MSG_PREFIX}100-node-1", "SK": "BROADCAST",
             "read_by": ["node-2"], "created_at": 100},
            {"PK": f"{MSG_PREFIX}200-node-2", "SK": "BROADCAST",
             "read_by": [], "created_at": 200},
        ]
        table.scan.return_value = {"Items": items}

        with patch("message_bus.get_dynamo_client", return_value=table):
            result = get_recent_messages(TENANT, WS, limit=10)

        # Retorna todos, incluso leidos, ordenados desc
        assert len(result) == 2
        assert result[0]["created_at"] == 200
