"""Tests para tenant_manager.py — gestion de tenants y workspaces con mocks."""
from unittest.mock import MagicMock, patch

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


def _conditional_check_error() -> ClientError:
    """Crea un ClientError de tipo ConditionalCheckFailedException."""
    return ClientError(
        {"Error": {"Code": "ConditionalCheckFailedException", "Message": "exists"}},
        "PutItem",
    )


# ---------------------------------------------------------------------------
# create_tenant
# ---------------------------------------------------------------------------


class TestCreateTenant:
    def test_create_tenant_exitoso(self):
        """Debe crear item con PK=TENANT#..., SK=CONFIG y campos del plan."""
        from tenant_manager import create_tenant

        table = _mock_table()
        with patch("tenant_manager.get_dynamo_client", return_value=table):
            result = create_tenant("myco", "myco-dev", "admin@myco.com", "team")

        table.put_item.assert_called_once()
        assert result["PK"] == "TENANT#myco"
        assert result["SK"] == "CONFIG"
        assert result["github_org"] == "myco-dev"
        assert result["admin_email"] == "admin@myco.com"
        assert result["plan"] == "team"
        assert result["max_nodes"] == 10
        assert result["max_workspaces"] == 5
        assert result["active"] is True
        assert "created_at" in result

    def test_create_tenant_ya_existe_falla(self):
        """Debe lanzar RuntimeError si el tenant ya existe."""
        from tenant_manager import create_tenant

        table = _mock_table()
        table.put_item.side_effect = _conditional_check_error()

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            with pytest.raises(RuntimeError, match="ya existe"):
                create_tenant("myco", "myco-dev", "a@b.com")

    def test_create_tenant_plan_invalido_falla(self):
        """Debe lanzar ValueError si el plan no existe."""
        from tenant_manager import create_tenant

        with pytest.raises(ValueError, match="Plan invalido"):
            create_tenant("myco", "myco-dev", "a@b.com", plan="platinum")


# ---------------------------------------------------------------------------
# get_tenant
# ---------------------------------------------------------------------------


class TestGetTenant:
    def test_get_tenant_retorna_none(self):
        """Debe retornar None si el tenant no existe."""
        from tenant_manager import get_tenant

        table = _mock_table()
        table.get_item.return_value = {}

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            result = get_tenant("nonexistent")

        assert result is None

    def test_get_tenant_retorna_item(self):
        """Debe retornar el item si existe."""
        from tenant_manager import get_tenant

        item = {"PK": "TENANT#myco", "SK": "CONFIG", "plan": "team"}
        table = _mock_table()
        table.get_item.return_value = {"Item": item}

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            result = get_tenant("myco")

        assert result == item


# ---------------------------------------------------------------------------
# list_tenants
# ---------------------------------------------------------------------------


class TestListTenants:
    def test_list_tenants_retorna_lista(self):
        """Debe retornar lista de tenants con SK=CONFIG."""
        from tenant_manager import list_tenants

        items = [
            {"PK": "TENANT#a", "SK": "CONFIG"},
            {"PK": "TENANT#b", "SK": "CONFIG"},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            result = list_tenants()

        assert len(result) == 2

    def test_list_tenants_vacia(self):
        """Debe retornar lista vacia si no hay tenants."""
        from tenant_manager import list_tenants

        table = _mock_table()
        with patch("tenant_manager.get_dynamo_client", return_value=table):
            result = list_tenants()

        assert result == []


# ---------------------------------------------------------------------------
# delete_tenant
# ---------------------------------------------------------------------------


class TestDeleteTenant:
    def test_delete_tenant_sin_workspaces(self):
        """Debe eliminar el tenant si no tiene workspaces."""
        from tenant_manager import delete_tenant

        table = _mock_table()
        # list_workspaces retorna vacio (scan default)
        with patch("tenant_manager.get_dynamo_client", return_value=table):
            delete_tenant("myco")

        table.delete_item.assert_called_once_with(
            Key={"PK": "TENANT#myco", "SK": "CONFIG"}
        )

    def test_delete_tenant_con_workspaces_falla(self):
        """Debe lanzar RuntimeError si tiene workspaces activos."""
        from tenant_manager import delete_tenant

        table = _mock_table()
        table.scan.return_value = {
            "Items": [{"PK": "TENANT#myco", "SK": "WORKSPACE#ws1"}]
        }

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            with pytest.raises(RuntimeError, match="workspace"):
                delete_tenant("myco")


# ---------------------------------------------------------------------------
# create_workspace
# ---------------------------------------------------------------------------


class TestCreateWorkspace:
    def test_create_workspace_exitoso(self):
        """Debe crear workspace con github config y repos."""
        from tenant_manager import create_workspace

        table = _mock_table()
        # get_tenant retorna un tenant valido
        tenant_item = {
            "PK": "TENANT#myco", "SK": "CONFIG",
            "max_workspaces": 5, "plan": "team",
        }
        table.get_item.return_value = {"Item": tenant_item}
        # list_workspaces retorna 0 (scan default vacio)

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            result = create_workspace(
                tenant_id="myco",
                workspace_id="main-app",
                workspace_name="Main App",
                github_project_id="PVT_123",
                github_project_number=1,
                status_field_id="SF_456",
                status_options={"todo": "a1", "done": "b2"},
                repos=["myco/backend", "myco/frontend"],
            )

        assert result["PK"] == "TENANT#myco"
        assert result["SK"] == "WORKSPACE#main-app"
        assert result["workspace_id"] == "main-app"
        assert result["workspace_name"] == "Main App"
        assert result["github"]["project_id"] == "PVT_123"
        assert result["github"]["project_number"] == 1
        assert result["repos"] == ["myco/backend", "myco/frontend"]
        assert result["active"] is True

    def test_create_workspace_excede_plan_falla(self):
        """Debe fallar si se excede el limite de workspaces del plan."""
        from tenant_manager import create_workspace

        table = _mock_table()
        tenant_item = {
            "PK": "TENANT#myco", "SK": "CONFIG",
            "max_workspaces": 1, "plan": "free",
        }
        # get_tenant retorna tenant con max_workspaces=1
        table.get_item.return_value = {"Item": tenant_item}
        # list_workspaces retorna 1 workspace existente
        table.scan.return_value = {
            "Items": [{"PK": "TENANT#myco", "SK": "WORKSPACE#existing"}]
        }

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            with pytest.raises(RuntimeError, match="excede el limite"):
                create_workspace(
                    "myco", "ws2", "WS 2", "PVT_1", 1, "SF_1", {}, []
                )

    def test_create_workspace_tenant_no_existe_falla(self):
        """Debe fallar si el tenant no existe."""
        from tenant_manager import create_workspace

        table = _mock_table()
        table.get_item.return_value = {}  # get_tenant retorna None

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            with pytest.raises(RuntimeError, match="no existe"):
                create_workspace(
                    "ghost", "ws1", "WS 1", "PVT_1", 1, "SF_1", {}, []
                )


# ---------------------------------------------------------------------------
# list_workspaces
# ---------------------------------------------------------------------------


class TestListWorkspaces:
    def test_list_workspaces_retorna_lista(self):
        """Debe retornar workspaces del tenant."""
        from tenant_manager import list_workspaces

        items = [
            {"PK": "TENANT#myco", "SK": "WORKSPACE#ws1"},
            {"PK": "TENANT#myco", "SK": "WORKSPACE#ws2"},
        ]
        table = _mock_table()
        table.scan.return_value = {"Items": items}

        with patch("tenant_manager.get_dynamo_client", return_value=table):
            result = list_workspaces("myco")

        assert len(result) == 2


# ---------------------------------------------------------------------------
# delete_workspace
# ---------------------------------------------------------------------------


class TestDeleteWorkspace:
    def test_delete_workspace_exitoso(self):
        """Debe borrar el item del workspace."""
        from tenant_manager import delete_workspace

        table = _mock_table()
        with patch("tenant_manager.get_dynamo_client", return_value=table):
            delete_workspace("myco", "ws1")

        table.delete_item.assert_called_once_with(
            Key={"PK": "TENANT#myco", "SK": "WORKSPACE#ws1"}
        )


# ---------------------------------------------------------------------------
# PLAN_LIMITS
# ---------------------------------------------------------------------------


class TestPlanLimits:
    def test_plan_limits_free_max_2_nodes(self):
        """Plan free debe tener max 2 nodos."""
        from tenant_manager import PLAN_LIMITS

        assert PLAN_LIMITS["free"]["max_nodes"] == 2
        assert PLAN_LIMITS["free"]["max_workspaces"] == 1

    def test_plan_limits_enterprise_ilimitado(self):
        """Plan enterprise debe tener limites altos."""
        from tenant_manager import PLAN_LIMITS

        assert PLAN_LIMITS["enterprise"]["max_nodes"] == 999
        assert PLAN_LIMITS["enterprise"]["max_workspaces"] == 999


# ---------------------------------------------------------------------------
# update_workspace
# ---------------------------------------------------------------------------


class TestUpdateWorkspace:
    def test_update_workspace_cambia_campos(self):
        """Debe construir UpdateExpression dinamico."""
        from tenant_manager import update_workspace

        table = _mock_table()
        with patch("tenant_manager.get_dynamo_client", return_value=table):
            update_workspace("myco", "ws1", active=False, repos=["a/b"])

        table.update_item.assert_called_once()
        kwargs = table.update_item.call_args[1]
        assert "SET" in kwargs["UpdateExpression"]

    def test_update_workspace_sin_kwargs_no_hace_nada(self):
        """No debe llamar a DynamoDB si no hay campos que actualizar."""
        from tenant_manager import update_workspace

        table = _mock_table()
        with patch("tenant_manager.get_dynamo_client", return_value=table):
            update_workspace("myco", "ws1")

        table.update_item.assert_not_called()
