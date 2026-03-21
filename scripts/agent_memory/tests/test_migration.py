"""Tests para migration.py — migracion de schema viejo a multi-tenant con mocks."""
from unittest.mock import MagicMock, patch

import pytest


def _mock_table() -> MagicMock:
    """Crea un mock del Table de DynamoDB."""
    table = MagicMock()
    table.scan.return_value = {"Items": []}
    table.put_item.return_value = {}
    return table


# ---------------------------------------------------------------------------
# migrate_to_multi_tenant
# ---------------------------------------------------------------------------


class TestMigrateToMultiTenant:
    def test_migrate_task_meta(self):
        """Debe migrar TASK#X|META a TENANT#t|WS#ws|TASK#X|META."""
        from migration import migrate_to_multi_tenant

        items = [
            {"PK": "TASK#043", "SK": "META", "title": "Tarea 43"},
            {"PK": "TASK#043", "SK": "LOCK", "locked_by": "team-1"},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("migration.get_dynamo_client", return_value=table):
            result = migrate_to_multi_tenant("baat", "sp", dry_run=False)

        assert result["migrated"] == 2
        assert result["skipped"] == 0
        assert result["errors"] == []
        # Verificar que se escribieron 2 items
        assert table.put_item.call_count == 2
        # Primer item
        first_item = table.put_item.call_args_list[0][1]["Item"]
        assert first_item["PK"] == "TENANT#baat|WS#sp|TASK#043"
        assert first_item["SK"] == "META"

    def test_migrate_learning(self):
        """Debe migrar LEARNING#module|patterns al nuevo schema."""
        from migration import migrate_to_multi_tenant

        items = [
            {"PK": "LEARNING#covacha-payment", "SK": "patterns", "gotchas": ["tip1"]},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("migration.get_dynamo_client", return_value=table):
            result = migrate_to_multi_tenant("baat", "sp", dry_run=False)

        assert result["migrated"] == 1
        written = table.put_item.call_args[1]["Item"]
        assert written["PK"] == "TENANT#baat|WS#sp|LEARNING#covacha-payment"

    def test_migrate_skip_ya_migrado(self):
        """Debe saltar items que ya tienen prefijo TENANT#."""
        from migration import migrate_to_multi_tenant

        items = [
            {"PK": "TENANT#baat|WS#sp|TASK#043", "SK": "META"},
            {"PK": "TASK#044", "SK": "META", "title": "Nueva"},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("migration.get_dynamo_client", return_value=table):
            result = migrate_to_multi_tenant("baat", "sp", dry_run=False)

        assert result["migrated"] == 1
        assert result["skipped"] == 1

    def test_migrate_skip_team(self):
        """Debe saltar items TEAM# (reemplazados por NODE#)."""
        from migration import migrate_to_multi_tenant

        items = [
            {"PK": "TEAM#backend-mac-1", "SK": "STATUS", "current_task": "043"},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("migration.get_dynamo_client", return_value=table):
            result = migrate_to_multi_tenant("baat", "sp", dry_run=False)

        assert result["migrated"] == 0
        assert result["skipped"] == 1

    def test_migrate_dry_run_no_escribe(self):
        """En dry_run debe contar pero no escribir a DynamoDB."""
        from migration import migrate_to_multi_tenant

        items = [
            {"PK": "TASK#043", "SK": "META"},
            {"PK": "SYNC#github", "SK": "META"},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("migration.get_dynamo_client", return_value=table):
            result = migrate_to_multi_tenant("baat", "sp", dry_run=True)

        assert result["migrated"] == 2
        assert result["dry_run"] is True
        # No debe haber escrito nada
        table.put_item.assert_not_called()

    def test_migrate_sync_meta(self):
        """Debe migrar SYNC#github|META al nuevo schema."""
        from migration import migrate_to_multi_tenant

        items = [
            {"PK": "SYNC#github", "SK": "META", "last_sync": 123},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("migration.get_dynamo_client", return_value=table):
            result = migrate_to_multi_tenant("baat", "sp", dry_run=False)

        assert result["migrated"] == 1
        written = table.put_item.call_args[1]["Item"]
        assert written["PK"] == "TENANT#baat|WS#sp|SYNC#github"


# ---------------------------------------------------------------------------
# verify_migration
# ---------------------------------------------------------------------------


class TestVerifyMigration:
    def test_verify_migration_completa(self):
        """Debe reportar migracion completa cuando todos los items estan migrados."""
        from migration import verify_migration

        items = [
            {"PK": "TENANT#baat|WS#sp|TASK#043", "SK": "META"},
            {"PK": "TENANT#baat|WS#sp|TASK#044", "SK": "META"},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("migration.get_dynamo_client", return_value=table):
            result = verify_migration("baat", "sp")

        assert result["new_schema_items"] == 2
        assert result["old_schema_items"] == 0
        assert result["complete"] is True

    def test_verify_migration_incompleta(self):
        """Debe reportar migracion incompleta si quedan items viejos."""
        from migration import verify_migration

        items = [
            {"PK": "TENANT#baat|WS#sp|TASK#043", "SK": "META"},
            {"PK": "TASK#044", "SK": "META"},
            {"PK": "TASK#045", "SK": "META"},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("migration.get_dynamo_client", return_value=table):
            result = verify_migration("baat", "sp")

        assert result["new_schema_items"] == 1
        assert result["old_schema_items"] == 2
        assert result["complete"] is False
