"""Tests para workspace_discovery.py — auto-descubrimiento con mocks de subprocess."""
import json
from unittest.mock import MagicMock, patch, call

import pytest


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------


class TestSlugify:
    def test_slugify_limpia_titulo(self):
        """Debe convertir titulo normal a slug."""
        from workspace_discovery import slugify

        assert slugify("Mi Proyecto 123") == "mi-proyecto-123"

    def test_slugify_caracteres_especiales(self):
        """Debe eliminar caracteres especiales."""
        from workspace_discovery import slugify

        assert slugify("¡Hola! (Mundo) @2024") == "hola-mundo-2024"

    def test_slugify_multiples_espacios(self):
        """Debe colapsar multiples espacios/guiones."""
        from workspace_discovery import slugify

        assert slugify("  foo   bar  ") == "foo-bar"

    def test_slugify_ya_limpio(self):
        """No debe cambiar un slug ya limpio."""
        from workspace_discovery import slugify

        assert slugify("superpago") == "superpago"


# ---------------------------------------------------------------------------
# discover_workspaces
# ---------------------------------------------------------------------------


class TestDiscoverWorkspaces:
    def test_discover_workspaces_parsea_graphql(self):
        """Debe parsear respuesta GraphQL y retornar workspaces."""
        from workspace_discovery import discover_workspaces

        # Mock de la respuesta de listar projects
        projects_response = json.dumps({
            "data": {
                "organization": {
                    "projectsV2": {
                        "nodes": [
                            {
                                "id": "PVT_1",
                                "title": "SuperPago",
                                "number": 1,
                                "items": {"totalCount": 47},
                            },
                            {
                                "id": "PVT_2",
                                "title": "Marketing App",
                                "number": 3,
                                "items": {"totalCount": 12},
                            },
                        ]
                    }
                }
            }
        })

        # Mock de respuesta de fields para cada project
        fields_response = json.dumps({
            "data": {
                "node": {
                    "fields": {
                        "nodes": [
                            {
                                "id": "SF_1",
                                "name": "Status",
                                "options": [
                                    {"id": "opt_todo", "name": "Todo"},
                                    {"id": "opt_ip", "name": "In Progress"},
                                    {"id": "opt_done", "name": "Done"},
                                ],
                            },
                            {"id": "SF_2", "name": "Title"},
                        ]
                    }
                }
            }
        })

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = projects_response

        mock_fields = MagicMock()
        mock_fields.returncode = 0
        mock_fields.stdout = fields_response

        with patch("workspace_discovery.subprocess.run") as mock_run:
            mock_run.side_effect = [mock_result, mock_fields, mock_fields]
            result = discover_workspaces("baatdigital")

        assert len(result) == 2
        assert result[0]["id"] == "superpago"
        assert result[0]["name"] == "SuperPago"
        assert result[0]["github"]["project_number"] == 1
        assert result[0]["github"]["status_field_id"] == "SF_1"
        assert result[0]["github"]["status_options"]["todo"] == "opt_todo"
        assert result[0]["task_count"] == 47
        assert result[1]["id"] == "marketing-app"


# ---------------------------------------------------------------------------
# discover_repos_from_project
# ---------------------------------------------------------------------------


class TestDiscoverReposFromProject:
    def test_discover_repos_from_project(self):
        """Debe extraer repos unicos de items del project."""
        from workspace_discovery import discover_repos_from_project

        response = json.dumps({
            "data": {
                "node": {
                    "items": {
                        "nodes": [
                            {
                                "content": {
                                    "repository": {
                                        "nameWithOwner": "myco/backend"
                                    }
                                }
                            },
                            {
                                "content": {
                                    "repository": {
                                        "nameWithOwner": "myco/frontend"
                                    }
                                }
                            },
                            {
                                "content": {
                                    "repository": {
                                        "nameWithOwner": "myco/backend"
                                    }
                                }
                            },
                            {"content": None},
                        ]
                    }
                }
            }
        })

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = response

        with patch("workspace_discovery.subprocess.run", return_value=mock_result):
            repos = discover_repos_from_project("myco", "PVT_1")

        assert repos == ["myco/backend", "myco/frontend"]


# ---------------------------------------------------------------------------
# auto_setup_workspaces
# ---------------------------------------------------------------------------


class TestAutoSetupWorkspaces:
    def test_auto_setup_crea_workspaces(self):
        """Debe descubrir y crear workspaces en DynamoDB."""
        from workspace_discovery import auto_setup_workspaces

        mock_ws = [
            {
                "id": "superpago",
                "name": "SuperPago",
                "github": {
                    "org": "baatdigital",
                    "project_number": 1,
                    "project_id": "PVT_1",
                    "status_field_id": "SF_1",
                    "status_options": {"todo": "a1"},
                },
                "task_count": 10,
            },
        ]

        fake_workspace_item = {
            "PK": "TENANT#baat", "SK": "WORKSPACE#superpago",
            "workspace_id": "superpago",
        }

        with patch("workspace_discovery.discover_workspaces", return_value=mock_ws), \
             patch("workspace_discovery.discover_repos_from_project", return_value=["baat/repo"]), \
             patch("workspace_discovery.create_workspace", return_value=fake_workspace_item) as mock_create:
            result = auto_setup_workspaces("baat", "baatdigital")

        assert len(result) == 1
        mock_create.assert_called_once()
        kwargs = mock_create.call_args[1]
        assert kwargs["tenant_id"] == "baat"
        assert kwargs["workspace_id"] == "superpago"
        assert kwargs["repos"] == ["baat/repo"]

    def test_auto_setup_filtra_por_ids(self):
        """Debe filtrar workspaces por workspace_ids si se proporcionan."""
        from workspace_discovery import auto_setup_workspaces

        mock_ws = [
            {
                "id": "superpago",
                "name": "SuperPago",
                "github": {
                    "org": "baat", "project_number": 1, "project_id": "PVT_1",
                    "status_field_id": "SF_1", "status_options": {},
                },
                "task_count": 10,
            },
            {
                "id": "marketing",
                "name": "Marketing",
                "github": {
                    "org": "baat", "project_number": 2, "project_id": "PVT_2",
                    "status_field_id": "SF_2", "status_options": {},
                },
                "task_count": 5,
            },
        ]

        with patch("workspace_discovery.discover_workspaces", return_value=mock_ws), \
             patch("workspace_discovery.discover_repos_from_project", return_value=[]), \
             patch("workspace_discovery.create_workspace", return_value={"workspace_id": "superpago"}):
            result = auto_setup_workspaces("baat", "baat", workspace_ids=["superpago"])

        assert len(result) == 1
