"""Tests para dynamo_client.py — mock boto3, test claim/release/lock."""
import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError


def _client_error(code: str) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": "test"}}, "operation")


def _mock_table():
    """Crea un mock del Table de DynamoDB con los métodos necesarios."""
    table = MagicMock()
    table.scan.return_value = {"Items": [], "Count": 0}
    table.get_item.return_value = {}
    table.put_item.return_value = {}
    table.delete_item.return_value = {}
    table.update_item.return_value = {}
    return table


# ---------------------------------------------------------------------------
# get_available_tasks
# ---------------------------------------------------------------------------

class TestGetAvailableTasks:
    def test_retorna_lista_vacia_cuando_no_hay_items(self):
        from dynamo_client import get_available_tasks
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.scan.return_value = {"Items": []}
            result = get_available_tasks()
        assert result == []

    def test_filtra_por_label_cuando_se_indica(self):
        from dynamo_client import get_available_tasks
        items = [
            {"PK": "TASK#1", "SK": "META", "status": "todo", "labels": ["backend"]},
            {"PK": "TASK#2", "SK": "META", "status": "todo", "labels": ["frontend"]},
        ]
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.scan.return_value = {"Items": items}
            result = get_available_tasks(label="backend")
        assert len(result) == 1
        assert result[0]["PK"] == "TASK#1"

    def test_lanza_excepcion_en_error_dynamo(self):
        from dynamo_client import get_available_tasks
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.scan.side_effect = _client_error("ProvisionedThroughputExceededException")
            with pytest.raises(RuntimeError, match="Error al consultar tareas"):
                get_available_tasks()


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------

class TestGetTask:
    def test_retorna_none_cuando_no_existe(self):
        from dynamo_client import get_task
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.get_item.return_value = {}
            assert get_task("999") is None

    def test_retorna_item_cuando_existe(self):
        from dynamo_client import get_task
        item = {"PK": "TASK#42", "SK": "META", "title": "Mi tarea"}
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.get_item.return_value = {"Item": item}
            result = get_task("42")
        assert result == item


# ---------------------------------------------------------------------------
# claim_task — locking atómico
# ---------------------------------------------------------------------------

class TestClaimTask:
    def test_retorna_true_cuando_lock_adquirido(self):
        from dynamo_client import claim_task
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.put_item.return_value = {}
            result = claim_task("42", "backend", "mac-1")
        assert result is True

    def test_retorna_false_cuando_ya_tiene_lock(self):
        from dynamo_client import claim_task
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.put_item.side_effect = _client_error("ConditionalCheckFailedException")
            result = claim_task("42", "frontend", "mac-2")
        assert result is False

    def test_lanza_excepcion_en_error_desconocido(self):
        from dynamo_client import claim_task
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.put_item.side_effect = _client_error("InternalServerError")
            with pytest.raises(RuntimeError, match="Error al reclamar"):
                claim_task("42", "backend", "mac-1")


# ---------------------------------------------------------------------------
# release_task
# ---------------------------------------------------------------------------

class TestReleaseTask:
    def test_elimina_lock_y_actualiza_status(self):
        from dynamo_client import release_task
        table = _mock_table()
        with patch("dynamo_client.get_dynamo_client", return_value=table):
            release_task("42", status="done")
        table.delete_item.assert_called_once_with(Key={"PK": "TASK#42", "SK": "LOCK"})
        table.update_item.assert_called_once()

    def test_lanza_excepcion_en_error_dynamo(self):
        from dynamo_client import release_task
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.delete_item.side_effect = _client_error("ValidationException")
            with pytest.raises(RuntimeError, match="Error al liberar"):
                release_task("42")


# ---------------------------------------------------------------------------
# save_learning
# ---------------------------------------------------------------------------

class TestSaveLearning:
    def test_llama_update_item_con_lista_append(self):
        from dynamo_client import save_learning
        table = _mock_table()
        with patch("dynamo_client.get_dynamo_client", return_value=table):
            save_learning("covacha-payment", "No usar float para montos", "backend")
        table.update_item.assert_called_once()
        call_args = table.update_item.call_args[1]
        assert "LEARNING#covacha-payment" in str(call_args)

    def test_lanza_excepcion_en_error_dynamo(self):
        from dynamo_client import save_learning
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.update_item.side_effect = _client_error("ValidationException")
            with pytest.raises(RuntimeError, match="Error al guardar aprendizaje"):
                save_learning("modulo", "learning", "team")


# ---------------------------------------------------------------------------
# get_learnings
# ---------------------------------------------------------------------------

class TestGetLearnings:
    def test_retorna_dict_vacio_cuando_no_existe(self):
        from dynamo_client import get_learnings
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.get_item.return_value = {}
            result = get_learnings("modulo-inexistente")
        assert result == {}

    def test_retorna_learnings_cuando_existen(self):
        from dynamo_client import get_learnings
        expected = {"gotchas": ["usar Decimal", "no float"]}
        with patch("dynamo_client.get_dynamo_client") as mock_client:
            mock_client.return_value.get_item.return_value = {"Item": expected}
            result = get_learnings("covacha-payment")
        assert result == expected


# ---------------------------------------------------------------------------
# update_team_status
# ---------------------------------------------------------------------------

class TestUpdateTeamStatus:
    def test_guarda_estado_con_tarea_activa(self):
        from dynamo_client import update_team_status
        table = _mock_table()
        with patch("dynamo_client.get_dynamo_client", return_value=table):
            update_team_status("backend", "mac-1", "ISS-42")
        table.put_item.assert_called_once()
        item = table.put_item.call_args[1]["Item"]
        assert item["team"] == "backend"
        assert item["current_task"] == "ISS-42"

    def test_guarda_estado_sin_tarea_activa(self):
        from dynamo_client import update_team_status
        table = _mock_table()
        with patch("dynamo_client.get_dynamo_client", return_value=table):
            update_team_status("frontend", "mac-2", None)
        item = table.put_item.call_args[1]["Item"]
        assert item["current_task"] is None
