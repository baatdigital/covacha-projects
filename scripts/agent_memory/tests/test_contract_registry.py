"""Tests para contract_registry.py — mock DynamoDB, test contratos de API."""
import pytest
from unittest.mock import MagicMock, patch

TENANT = "baatdigital"
WS = "superpago"
CONTRACT_PREFIX = f"TENANT#{TENANT}|WS#{WS}|CONTRACT#"


def _mock_table():
    """Crea un mock del Table de DynamoDB."""
    table = MagicMock()
    table.put_item.return_value = {}
    table.get_item.return_value = {}
    table.scan.return_value = {"Items": []}
    table.update_item.return_value = {}
    return table


class TestPublishContract:
    def test_publish_contract_crea_item_correcto(self):
        from contract_registry import publish_contract

        table = _mock_table()
        with patch("contract_registry.get_dynamo_client", return_value=table), \
             patch("contract_registry.time") as mock_time:
            mock_time.time.return_value = 1711036800
            result = publish_contract(
                TENANT, WS,
                name="spei-transfer",
                version="v1",
                method="POST",
                path="/api/v1/spei/transfer",
                request_schema={"clabe": "string"},
                response_schema={"success": "boolean"},
                published_by="node-1",
                task_id="043",
            )

        table.put_item.assert_called_once()
        item = table.put_item.call_args[1]["Item"]
        assert item["PK"] == f"{CONTRACT_PREFIX}spei-transfer-v1"
        assert item["SK"] == "META"
        assert item["name"] == "spei-transfer"
        assert item["version"] == "v1"
        assert item["method"] == "POST"
        assert item["path"] == "/api/v1/spei/transfer"
        assert item["request_schema"] == {"clabe": "string"}
        assert item["response_schema"] == {"success": "boolean"}
        assert item["published_by"] == "node-1"
        assert item["task_id"] == "043"
        assert item["consumed_by"] == []
        assert item["created_at"] == 1711036800
        assert CONTRACT_PREFIX in result


class TestGetContract:
    def test_get_contract_retorna_item(self):
        from contract_registry import get_contract

        table = _mock_table()
        contract_id = f"{CONTRACT_PREFIX}spei-transfer-v1"
        expected = {"PK": contract_id, "SK": "META", "name": "spei-transfer"}
        table.get_item.return_value = {"Item": expected}

        with patch("contract_registry.get_dynamo_client", return_value=table):
            result = get_contract(TENANT, WS, contract_id)

        assert result == expected

    def test_get_contract_retorna_none_si_no_existe(self):
        from contract_registry import get_contract

        table = _mock_table()
        table.get_item.return_value = {}

        with patch("contract_registry.get_dynamo_client", return_value=table):
            result = get_contract(TENANT, WS, "CONTRACT#inexistente")

        assert result is None


class TestSearchContracts:
    def test_search_contracts_por_path(self):
        from contract_registry import search_contracts

        table = _mock_table()
        items = [
            {"PK": f"{CONTRACT_PREFIX}spei-transfer-v1", "SK": "META",
             "path": "/api/v1/spei/transfer", "method": "POST"},
            {"PK": f"{CONTRACT_PREFIX}user-create-v1", "SK": "META",
             "path": "/api/v1/users", "method": "POST"},
        ]
        table.scan.return_value = {"Items": items}

        with patch("contract_registry.get_dynamo_client", return_value=table):
            result = search_contracts(TENANT, WS, path_pattern="spei")

        assert len(result) == 1
        assert "spei" in result[0]["path"]

    def test_search_contracts_por_method(self):
        from contract_registry import search_contracts

        table = _mock_table()
        items = [
            {"PK": f"{CONTRACT_PREFIX}spei-transfer-v1", "SK": "META",
             "path": "/api/v1/spei/transfer", "method": "POST"},
            {"PK": f"{CONTRACT_PREFIX}spei-status-v1", "SK": "META",
             "path": "/api/v1/spei/status", "method": "GET"},
        ]
        table.scan.return_value = {"Items": items}

        with patch("contract_registry.get_dynamo_client", return_value=table):
            result = search_contracts(TENANT, WS, method="GET")

        assert len(result) == 1
        assert result[0]["method"] == "GET"

    def test_search_contracts_sin_filtros(self):
        from contract_registry import search_contracts

        table = _mock_table()
        items = [
            {"PK": f"{CONTRACT_PREFIX}a-v1", "SK": "META",
             "path": "/a", "method": "GET"},
            {"PK": f"{CONTRACT_PREFIX}b-v1", "SK": "META",
             "path": "/b", "method": "POST"},
        ]
        table.scan.return_value = {"Items": items}

        with patch("contract_registry.get_dynamo_client", return_value=table):
            result = search_contracts(TENANT, WS)

        assert len(result) == 2


class TestAddConsumer:
    def test_add_consumer_agrega_a_lista(self):
        from contract_registry import add_consumer

        table = _mock_table()
        contract_id = f"{CONTRACT_PREFIX}spei-transfer-v1"

        with patch("contract_registry.get_dynamo_client", return_value=table):
            add_consumer(TENANT, WS, contract_id, "044")

        table.update_item.assert_called_once()
        update_args = table.update_item.call_args[1]
        assert update_args["Key"] == {"PK": contract_id, "SK": "META"}
        vals = update_args["ExpressionAttributeValues"]
        assert vals[":consumer"] == ["044"]
