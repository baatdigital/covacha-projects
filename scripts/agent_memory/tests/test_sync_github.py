"""Tests para sync_github.py"""
import pytest
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_item(number=42, title="Titulo test", labels=None, status="Todo", node_id="node-1"):
    return {
        "number": number,
        "title": title,
        "labels": labels or ["backend"],
        "assignees": [],
        "node_id": node_id,
        "status": status,
    }


# ---------------------------------------------------------------------------
# _infer_repo
# ---------------------------------------------------------------------------

class TestInferRepo:
    def test_backend_label_retorna_covacha_payment(self):
        from sync_github import _infer_repo
        assert _infer_repo(["backend", "feature"]) == "covacha-payment"

    def test_frontend_label_retorna_mf_sp(self):
        from sync_github import _infer_repo
        assert _infer_repo(["frontend"]) == "mf-sp"

    def test_sin_label_conocida_retorna_covacha_projects(self):
        from sync_github import _infer_repo
        assert _infer_repo(["epic", "docs"]) == "covacha-projects"

    def test_lista_vacia_retorna_covacha_projects(self):
        from sync_github import _infer_repo
        assert _infer_repo([]) == "covacha-projects"

    def test_backend_tiene_prioridad_sobre_frontend(self):
        from sync_github import _infer_repo
        # backend aparece primero en la condicion
        assert _infer_repo(["backend", "frontend"]) == "covacha-payment"


# ---------------------------------------------------------------------------
# sync_github — happy path
# ---------------------------------------------------------------------------

class TestSyncGithub:
    def _patch_all(self, items, branch=None, pr=None):
        """Devuelve un dict de patches listos para usar como context managers."""
        return {
            "get_project_items": patch("sync_github.get_project_items", return_value=items),
            "get_dynamo_client": patch("sync_github.get_dynamo_client"),
            "get_branch_for_issue": patch("sync_github.get_branch_for_issue", return_value=branch),
            "get_pr_for_issue": patch("sync_github.get_pr_for_issue", return_value=pr),
            "update_sync_status": patch("sync_github.update_sync_status"),
        }

    def test_sync_exitoso_retorna_conteo_correcto(self):
        from sync_github import sync_github
        item = _make_item()
        patches = self._patch_all([item])
        with patch("sync_github.get_project_items", return_value=[item]), \
             patch("sync_github.get_dynamo_client") as mock_table, \
             patch("sync_github.get_branch_for_issue", return_value=None), \
             patch("sync_github.get_pr_for_issue", return_value=None), \
             patch("sync_github.update_sync_status"):
            mock_table.return_value.put_item = MagicMock()
            result = sync_github()
        assert result["synced"] == 1
        assert result["errors"] == []

    def test_dry_run_no_escribe_en_dynamo(self):
        from sync_github import sync_github
        item = _make_item()
        with patch("sync_github.get_project_items", return_value=[item]), \
             patch("sync_github.get_dynamo_client") as mock_table, \
             patch("sync_github.get_branch_for_issue", return_value=None), \
             patch("sync_github.get_pr_for_issue", return_value=None), \
             patch("sync_github.update_sync_status") as mock_sync:
            mock_put = MagicMock()
            mock_table.return_value.put_item = mock_put
            result = sync_github(dry_run=True)
        mock_put.assert_not_called()
        mock_sync.assert_not_called()
        assert result["synced"] == 1

    def test_item_sin_numero_genera_error(self):
        from sync_github import sync_github
        item_sin_numero = {"number": None, "node_id": "node-x", "labels": [], "title": "", "assignees": [], "status": "Todo"}
        with patch("sync_github.get_project_items", return_value=[item_sin_numero]), \
             patch("sync_github.get_dynamo_client"), \
             patch("sync_github.update_sync_status"):
            result = sync_github()
        assert result["synced"] == 0
        assert len(result["errors"]) == 1
        assert "node-x" in result["errors"][0]

    def test_excepcion_en_enriquecimiento_capturada_como_error(self):
        from sync_github import sync_github
        item = _make_item()
        with patch("sync_github.get_project_items", return_value=[item]), \
             patch("sync_github.get_dynamo_client"), \
             patch("sync_github.get_branch_for_issue", side_effect=RuntimeError("gh fallo")), \
             patch("sync_github.get_pr_for_issue", return_value=None), \
             patch("sync_github.update_sync_status"):
            result = sync_github()
        assert result["synced"] == 0
        assert "ISS-42" in result["errors"][0]

    def test_status_in_progress_se_mapea_correctamente(self):
        from sync_github import sync_github
        item = _make_item(status="In Progress")
        captured = {}
        def fake_put(Item):
            captured["record"] = Item
        with patch("sync_github.get_project_items", return_value=[item]), \
             patch("sync_github.get_dynamo_client") as mock_table, \
             patch("sync_github.get_branch_for_issue", return_value=None), \
             patch("sync_github.get_pr_for_issue", return_value=None), \
             patch("sync_github.update_sync_status"):
            mock_table.return_value.put_item = fake_put
            sync_github()
        assert captured["record"]["status"] == "in_progress"

    def test_pr_enriquece_el_record(self):
        from sync_github import sync_github
        item = _make_item()
        pr = {"number": 7, "url": "https://github.com/pr/7", "state": "open"}
        captured = {}
        def fake_put(Item):
            captured["record"] = Item
        with patch("sync_github.get_project_items", return_value=[item]), \
             patch("sync_github.get_dynamo_client") as mock_table, \
             patch("sync_github.get_branch_for_issue", return_value="feature/ISS-42-algo"), \
             patch("sync_github.get_pr_for_issue", return_value=pr), \
             patch("sync_github.update_sync_status"):
            mock_table.return_value.put_item = fake_put
            sync_github()
        assert captured["record"]["pr_number"] == 7
        assert captured["record"]["branch"] == "feature/ISS-42-algo"

    def test_lista_vacia_retorna_cero_synced(self):
        from sync_github import sync_github
        with patch("sync_github.get_project_items", return_value=[]), \
             patch("sync_github.get_dynamo_client"), \
             patch("sync_github.update_sync_status"):
            result = sync_github()
        assert result == {"synced": 0, "errors": []}
