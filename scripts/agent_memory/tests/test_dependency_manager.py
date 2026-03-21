"""Tests para dependency_manager.py — mock DynamoDB, test dependencias y ciclos."""
import pytest
from unittest.mock import MagicMock, patch, call

TENANT = "baatdigital"
WS = "superpago"
DEP_PREFIX = f"TENANT#{TENANT}|WS#{WS}|DEP#"


def _mock_table():
    """Crea un mock del Table de DynamoDB."""
    table = MagicMock()
    table.put_item.return_value = {}
    table.query.return_value = {"Items": []}
    table.scan.return_value = {"Items": []}
    table.update_item.return_value = {}
    return table


class TestAddDependency:
    def test_add_dependency_crea_item_correcto(self):
        from dependency_manager import add_dependency

        table = _mock_table()
        # Mock detect_circular_dependency para que retorne False
        with patch("dependency_manager.get_dynamo_client", return_value=table), \
             patch("dependency_manager.detect_circular_dependency", return_value=False):
            add_dependency(TENANT, WS, "044", "043")

        table.put_item.assert_called_once()
        item = table.put_item.call_args[1]["Item"]
        assert item["PK"] == f"{DEP_PREFIX}044"
        assert item["SK"] == "DEPENDS_ON#043"
        assert item["blocker_task"] == "043"
        assert item["blocker_status"] == "pending"
        assert item["blocked_task"] == "044"
        assert "created_at" in item

    def test_add_dependency_lanza_error_si_ciclo(self):
        from dependency_manager import add_dependency

        with patch("dependency_manager.detect_circular_dependency", return_value=True):
            with pytest.raises(ValueError, match="circular"):
                add_dependency(TENANT, WS, "044", "043")


class TestGetDependencies:
    def test_get_dependencies_retorna_lista(self):
        from dependency_manager import get_dependencies

        table = _mock_table()
        deps = [
            {"PK": f"{DEP_PREFIX}044", "SK": "DEPENDS_ON#043",
             "blocker_task": "043", "blocker_status": "pending"},
            {"PK": f"{DEP_PREFIX}044", "SK": "DEPENDS_ON#042",
             "blocker_task": "042", "blocker_status": "done"},
        ]
        table.query.return_value = {"Items": deps}

        with patch("dependency_manager.get_dynamo_client", return_value=table):
            result = get_dependencies(TENANT, WS, "044")

        assert len(result) == 2
        assert result[0]["blocker_task"] == "043"

    def test_get_dependencies_retorna_vacio_sin_deps(self):
        from dependency_manager import get_dependencies

        table = _mock_table()
        table.query.return_value = {"Items": []}

        with patch("dependency_manager.get_dynamo_client", return_value=table):
            result = get_dependencies(TENANT, WS, "044")

        assert result == []


class TestResolveDependency:
    def test_resolve_dependency_actualiza_status_done(self):
        from dependency_manager import resolve_dependency

        table = _mock_table()
        items = [
            {"PK": f"{DEP_PREFIX}044", "SK": "DEPENDS_ON#043",
             "blocker_task": "043", "blocked_task": "044"},
        ]
        table.scan.return_value = {"Items": items}

        with patch("dependency_manager.get_dynamo_client", return_value=table):
            resolve_dependency(TENANT, WS, "043")

        table.update_item.assert_called_once()
        update_args = table.update_item.call_args[1]
        assert update_args["UpdateExpression"] == "SET blocker_status = :done"
        assert update_args["ExpressionAttributeValues"][":done"] == "done"

    def test_resolve_dependency_retorna_tareas_desbloqueadas(self):
        from dependency_manager import resolve_dependency

        table = _mock_table()
        items = [
            {"PK": f"{DEP_PREFIX}044", "SK": "DEPENDS_ON#043",
             "blocker_task": "043", "blocked_task": "044"},
            {"PK": f"{DEP_PREFIX}045", "SK": "DEPENDS_ON#043",
             "blocker_task": "043", "blocked_task": "045"},
        ]
        table.scan.return_value = {"Items": items}

        with patch("dependency_manager.get_dynamo_client", return_value=table):
            result = resolve_dependency(TENANT, WS, "043")

        assert sorted(result) == ["044", "045"]


class TestIsTaskUnblocked:
    def test_is_task_unblocked_true_sin_deps(self):
        from dependency_manager import is_task_unblocked

        with patch("dependency_manager.get_dependencies", return_value=[]):
            assert is_task_unblocked(TENANT, WS, "044") is True

    def test_is_task_unblocked_true_todas_done(self):
        from dependency_manager import is_task_unblocked

        deps = [
            {"blocker_status": "done"},
            {"blocker_status": "done"},
        ]
        with patch("dependency_manager.get_dependencies", return_value=deps):
            assert is_task_unblocked(TENANT, WS, "044") is True

    def test_is_task_unblocked_false_con_pending(self):
        from dependency_manager import is_task_unblocked

        deps = [
            {"blocker_status": "done"},
            {"blocker_status": "pending"},
        ]
        with patch("dependency_manager.get_dependencies", return_value=deps):
            assert is_task_unblocked(TENANT, WS, "044") is False


class TestDetectCircularDependency:
    def test_detect_circular_dependency_simple(self):
        """A depende de B, si B depende de A → ciclo."""
        from dependency_manager import detect_circular_dependency

        table = _mock_table()

        def mock_query(**kwargs):
            pk = kwargs["ExpressionAttributeValues"][":pk"]
            # B depende de A (ya existe)
            if "DEP#B" in pk:
                return {"Items": [{"blocker_task": "A"}]}
            return {"Items": []}

        table.query.side_effect = mock_query

        with patch("dependency_manager.get_dynamo_client", return_value=table):
            # Intentar: A depende de B (crearia ciclo A->B->A)
            result = detect_circular_dependency(TENANT, WS, "A", "B")

        assert result is True

    def test_detect_circular_dependency_no_ciclo(self):
        """A depende de B, C depende de A → no hay ciclo al agregar C->A."""
        from dependency_manager import detect_circular_dependency

        table = _mock_table()

        def mock_query(**kwargs):
            pk = kwargs["ExpressionAttributeValues"][":pk"]
            # A depende de B (ya existe)
            if "DEP#A" in pk:
                return {"Items": [{"blocker_task": "B"}]}
            return {"Items": []}

        table.query.side_effect = mock_query

        with patch("dependency_manager.get_dynamo_client", return_value=table):
            # Intentar: C depende de A → no ciclo
            result = detect_circular_dependency(TENANT, WS, "C", "A")

        assert result is False

    def test_detect_circular_dependency_misma_tarea(self):
        """Una tarea no puede depender de si misma."""
        from dependency_manager import detect_circular_dependency

        table = _mock_table()
        with patch("dependency_manager.get_dynamo_client", return_value=table):
            result = detect_circular_dependency(TENANT, WS, "A", "A")

        assert result is True
