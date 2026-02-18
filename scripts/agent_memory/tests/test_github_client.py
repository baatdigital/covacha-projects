"""Tests para github_client.py — mock gh CLI subprocess y requests."""
import json
import pytest
from unittest.mock import MagicMock, patch


def _make_subprocess_result(stdout: str, returncode: int = 0) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    result.returncode = returncode
    return result


# ---------------------------------------------------------------------------
# _gh_token
# ---------------------------------------------------------------------------

class TestGhToken:
    def test_retorna_token_limpio(self):
        from github_client import _gh_token
        with patch("github_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_subprocess_result("ghp_token123\n")
            token = _gh_token()
        assert token == "ghp_token123"


# ---------------------------------------------------------------------------
# run_gh_command
# ---------------------------------------------------------------------------

class TestRunGhCommand:
    def test_retorna_dict_cuando_output_es_json(self):
        from github_client import run_gh_command
        payload = {"number": 42, "state": "open"}
        with patch("github_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_subprocess_result(json.dumps(payload))
            result = run_gh_command(["issue", "view", "42"])
        assert result == payload

    def test_retorna_string_cuando_output_no_es_json(self):
        from github_client import run_gh_command
        with patch("github_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_subprocess_result("feature/ISS-42-algo")
            result = run_gh_command(["api", "..."])
        assert result == "feature/ISS-42-algo"

    def test_retorna_dict_vacio_cuando_output_vacio(self):
        from github_client import run_gh_command
        with patch("github_client.subprocess.run") as mock_run:
            mock_run.return_value = _make_subprocess_result("")
            result = run_gh_command(["issue", "close", "42"])
        assert result == {}


# ---------------------------------------------------------------------------
# _parse_item_node
# ---------------------------------------------------------------------------

class TestParseItemNode:
    def _make_node(self, number=10, title="Test", labels=None, status_name="Todo"):
        from config import GITHUB_STATUS_FIELD_ID
        labels = labels or ["backend"]
        return {
            "id": "node-abc",
            "content": {
                "number": number,
                "title": title,
                "state": "OPEN",
                "labels": {"nodes": [{"name": lbl} for lbl in labels]},
                "assignees": {"nodes": []},
            },
            "fieldValues": {
                "nodes": [
                    {
                        "name": status_name,
                        "field": {"id": GITHUB_STATUS_FIELD_ID},
                    }
                ]
            },
        }

    def test_parsea_numero_y_titulo(self):
        from github_client import _parse_item_node
        node = self._make_node(number=42, title="Mi titulo")
        result = _parse_item_node(node)
        assert result["number"] == 42
        assert result["title"] == "Mi titulo"

    def test_parsea_labels(self):
        from github_client import _parse_item_node
        node = self._make_node(labels=["backend", "mac-1"])
        result = _parse_item_node(node)
        assert "backend" in result["labels"]
        assert "mac-1" in result["labels"]

    def test_parsea_status(self):
        from github_client import _parse_item_node
        node = self._make_node(status_name="In Progress")
        result = _parse_item_node(node)
        assert result["status"] == "In Progress"

    def test_node_id_preservado(self):
        from github_client import _parse_item_node
        node = self._make_node()
        node["id"] = "node-xyz"
        result = _parse_item_node(node)
        assert result["node_id"] == "node-xyz"


# ---------------------------------------------------------------------------
# get_branch_for_issue
# ---------------------------------------------------------------------------

class TestGetBranchForIssue:
    def test_retorna_branch_cuando_existe(self):
        from github_client import get_branch_for_issue
        with patch("github_client.run_gh_command", return_value="feature/ISS-42-cotizaciones"):
            result = get_branch_for_issue(42, "covacha-payment")
        assert result == "feature/ISS-42-cotizaciones"

    def test_retorna_none_cuando_no_existe(self):
        from github_client import get_branch_for_issue
        with patch("github_client.run_gh_command", return_value=""):
            result = get_branch_for_issue(42, "covacha-payment")
        assert result is None

    def test_retorna_none_cuando_output_es_dict_vacio(self):
        from github_client import get_branch_for_issue
        with patch("github_client.run_gh_command", return_value={}):
            result = get_branch_for_issue(42, "covacha-payment")
        assert result is None


# ---------------------------------------------------------------------------
# get_pr_for_issue
# ---------------------------------------------------------------------------

class TestGetPrForIssue:
    def test_retorna_primer_pr_cuando_existe(self):
        from github_client import get_pr_for_issue
        prs = [{"number": 7, "state": "open", "url": "https://github.com/pr/7"}]
        with patch("github_client.run_gh_command", return_value=prs):
            result = get_pr_for_issue(42, "covacha-payment")
        assert result == prs[0]

    def test_retorna_none_cuando_no_hay_prs(self):
        from github_client import get_pr_for_issue
        with patch("github_client.run_gh_command", return_value=[]):
            result = get_pr_for_issue(42, "covacha-payment")
        assert result is None


# ---------------------------------------------------------------------------
# close_issue
# ---------------------------------------------------------------------------

class TestCloseIssue:
    def test_llama_gh_con_reason_completed(self):
        from github_client import close_issue
        with patch("github_client.run_gh_command") as mock_gh:
            mock_gh.return_value = {}
            close_issue(42, "covacha-payment")
        args = mock_gh.call_args[0][0]
        assert "close" in args
        assert "42" in args
        assert "--reason" in args
        assert "completed" in args
