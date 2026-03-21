"""Tests para task_finder.py — busqueda inteligente de tareas."""
from unittest.mock import MagicMock, patch

import pytest

from task_finder import (
    find_next_across_workspaces,
    find_next_task,
    is_task_compatible,
    score_assignment,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _node_config(
    repos: list[str] | None = None,
    caps: list[str] | None = None,
    status: str = "idle",
    auto_switch: bool = False,
) -> dict:
    """Crea un node_config de prueba."""
    repo_list = [
        {"name": r, "path": f"/x/{r}"} for r in (repos or ["covacha-payment"])
    ]
    return {
        "node_id": "test-node",
        "status": status,
        "auto_switch_workspace": auto_switch,
        "workspaces": [{
            "id": "ws-1",
            "repos": repo_list,
            "capabilities": caps or ["backend", "testing"],
        }],
    }


def _task(
    number: str = "043",
    repo: str = "covacha-payment",
    labels: list[str] | None = None,
    status: str = "todo",
) -> dict:
    """Crea una tarea de prueba."""
    return {
        "number": number,
        "title": f"Task {number}",
        "repo": repo,
        "labels": labels or ["backend", "feature"],
        "status": status,
        "recommended_model": "sonnet",
    }


# ---------------------------------------------------------------------------
# is_task_compatible
# ---------------------------------------------------------------------------

class TestIsTaskCompatible:
    def test_repo_match(self):
        """Debe ser compatible si repo esta en los repos del nodo."""
        t = _task(repo="covacha-payment")
        nc = _node_config(repos=["covacha-payment"], caps=["backend"])
        assert is_task_compatible(t, nc) is True

    def test_no_match_repo(self):
        """No debe ser compatible si repo no esta en los repos del nodo."""
        t = _task(repo="mf-core")
        nc = _node_config(repos=["covacha-payment"], caps=["backend"])
        assert is_task_compatible(t, nc) is False

    def test_no_match_labels(self):
        """No debe ser compatible si labels no matchean capabilities."""
        t = _task(repo="covacha-payment", labels=["frontend", "ui"])
        nc = _node_config(repos=["covacha-payment"], caps=["backend"])
        assert is_task_compatible(t, nc) is False

    def test_compatible_sin_labels(self):
        """Debe ser compatible si la tarea no tiene labels (solo repo match)."""
        t = _task(repo="covacha-payment", labels=[])
        nc = _node_config(repos=["covacha-payment"], caps=["backend"])
        assert is_task_compatible(t, nc) is True


# ---------------------------------------------------------------------------
# score_assignment
# ---------------------------------------------------------------------------

class TestScoreAssignment:
    def test_alto_match_completo(self):
        """Score alto cuando caps, repo y prioridad matchean."""
        t = _task(repo="covacha-payment", labels=["backend", "security"])
        nc = _node_config(
            repos=["covacha-payment"],
            caps=["backend", "security"],
            status="idle",
        )
        score = score_assignment(t, nc)
        # cap_match=0.4, repo=0.3, P1 (security)=0.2, idle=0.1 = 1.0
        assert score == 1.0

    def test_bajo_sin_match(self):
        """Score bajo cuando no hay match de caps ni repo."""
        t = _task(repo="mf-core", labels=["frontend"])
        nc = _node_config(
            repos=["covacha-payment"],
            caps=["backend"],
            status="working",
        )
        score = score_assignment(t, nc)
        # cap=0, repo=0, P2 (frontend)=0.14, idle=0
        assert score == 0.14

    def test_prioridad_p3(self):
        """Score refleja prioridad baja para docs/chore."""
        t = _task(labels=["docs"])
        nc = _node_config(caps=["docs"], status="idle")
        score = score_assignment(t, nc)
        # cap=0.4, repo=0.3, P3=0.08, idle=0.1 = 0.88
        assert score == 0.88


# ---------------------------------------------------------------------------
# find_next_task
# ---------------------------------------------------------------------------

class TestFindNextTask:
    @patch("task_finder.get_available_tasks")
    @patch("task_finder.is_task_unblocked", return_value=True)
    @patch("task_finder._has_lock", return_value=False)
    def test_retorna_mejor_score(self, _lock, _unblocked, mock_tasks):
        """Debe retornar la tarea con mejor score."""
        mock_tasks.return_value = [
            _task("041", labels=["docs"]),      # score bajo
            _task("042", labels=["backend", "security"]),  # score alto
        ]
        nc = _node_config(caps=["backend", "security"])
        result = find_next_task("tenant", "ws-1", nc)

        assert result is not None
        assert result["number"] == "042"

    @patch("task_finder.get_available_tasks")
    @patch("task_finder.is_task_unblocked", return_value=True)
    @patch("task_finder._has_lock", return_value=False)
    def test_filtra_incompatibles(self, _lock, _unblocked, mock_tasks):
        """Debe filtrar tareas de repos no compatibles."""
        mock_tasks.return_value = [
            _task("041", repo="mf-core", labels=["frontend"]),
        ]
        nc = _node_config(repos=["covacha-payment"], caps=["backend"])
        result = find_next_task("tenant", "ws-1", nc)

        assert result is None

    @patch("task_finder.get_available_tasks")
    @patch("task_finder.is_task_unblocked", return_value=False)
    @patch("task_finder._has_lock", return_value=False)
    def test_filtra_bloqueadas_por_deps(self, _lock, mock_unblocked, mock_tasks):
        """Debe filtrar tareas con dependencias no resueltas."""
        mock_tasks.return_value = [_task("043")]
        nc = _node_config()
        result = find_next_task("tenant", "ws-1", nc)

        assert result is None

    @patch("task_finder.get_available_tasks")
    def test_retorna_none_sin_tareas(self, mock_tasks):
        """Debe retornar None si no hay tareas disponibles."""
        mock_tasks.return_value = []
        nc = _node_config()
        result = find_next_task("tenant", "ws-1", nc)

        assert result is None


# ---------------------------------------------------------------------------
# find_next_across_workspaces
# ---------------------------------------------------------------------------

class TestFindAcrossWorkspaces:
    @patch("task_finder.find_next_task")
    def test_encuentra_en_otro_workspace(self, mock_find):
        """Debe encontrar tarea en otro workspace."""
        expected_task = _task("050")
        mock_find.side_effect = [None, expected_task]

        nc = {
            "node_id": "test-node",
            "status": "idle",
            "workspaces": [
                {"id": "ws-1", "repos": [], "capabilities": []},
                {"id": "ws-2", "repos": [{"name": "covacha-payment", "path": "/x/cp"}], "capabilities": ["backend"]},
            ],
        }
        result = find_next_across_workspaces("tenant", nc)

        assert result is not None
        ws_id, task = result
        assert ws_id == "ws-2"
        assert task["number"] == "050"

    @patch("task_finder.find_next_task", return_value=None)
    def test_retorna_none_sin_tareas(self, mock_find):
        """Debe retornar None si ningun workspace tiene tareas."""
        nc = _node_config()
        result = find_next_across_workspaces("tenant", nc)

        assert result is None
