"""Tests para ticket_evaluator.py — usa mocks para subprocess.run."""
import subprocess
from unittest.mock import MagicMock, patch, mock_open

import pytest

from ticket_evaluator import EvalCheck, EvalResult, TicketEvaluator


@pytest.fixture
def evaluator() -> TicketEvaluator:
    return TicketEvaluator()


def _mock_result(
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess:
    """Helper para crear CompletedProcess mock."""
    return subprocess.CompletedProcess(
        args=[], returncode=returncode, stdout=stdout, stderr=stderr
    )


# ── Pre-release: todo pasa ───────────────────────────────────

@patch("ticket_evaluator.os.walk")
@patch("ticket_evaluator.subprocess.run")
def test_evaluate_pre_release_todo_pasa(
    mock_run: MagicMock,
    mock_walk: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """Pre-release con todos los checks pasando."""
    # os.walk no encuentra archivos grandes
    mock_walk.return_value = []

    # Todos los subprocess exitosos
    mock_run.side_effect = [
        # _check_tests_pass: pytest -v --tb=short
        _mock_result(0, "all tests passed"),
        # _check_coverage: pytest --cov
        _mock_result(0, "TOTAL   100   0   100%"),
        # _check_lint: ruff check
        _mock_result(0, ""),
        # _check_no_large_files: os.walk (ya mockeado)
        # _check_no_large_functions: os.walk (ya mockeado)
        # _check_type_hints: git diff --name-only
        _mock_result(0, ""),
        # _check_commit_format: git log -1
        _mock_result(0, "feat(ISS-043): agregar endpoint"),
        # _check_branch_pushed: git status -sb
        _mock_result(0, "## main...origin/main"),
        # _check_no_secrets: git diff --cached --name-only
        _mock_result(0, ""),
    ]

    result = evaluator.evaluate("043", "pre_release", repo_path="/tmp/repo")

    assert result.passed is True
    assert result.evaluation_type == "pre_release"
    assert result.task_id == "043"
    assert len(result.checks) == 9


# ── Pre-release: tests fallan ────────────────────────────────

@patch("ticket_evaluator.os.walk")
@patch("ticket_evaluator.subprocess.run")
def test_evaluate_pre_release_tests_fallan(
    mock_run: MagicMock,
    mock_walk: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """Pre-release falla cuando pytest retorna exit_code != 0."""
    mock_walk.return_value = []

    mock_run.side_effect = [
        # pytest falla
        _mock_result(1, "FAILED test_algo"),
        # coverage
        _mock_result(0, "TOTAL   100   0   100%"),
        # lint
        _mock_result(0, ""),
        # type hints: git diff
        _mock_result(0, ""),
        # commit format
        _mock_result(0, "feat(ISS-043): algo"),
        # branch pushed
        _mock_result(0, "## main"),
        # no secrets
        _mock_result(0, ""),
    ]

    result = evaluator.evaluate("043", "pre_release", repo_path="/tmp/repo")

    assert result.passed is False
    tests_check = next(c for c in result.checks if c.name == "tests_pass")
    assert tests_check.passed is False


# ── Pre-release: coverage baja ───────────────────────────────

@patch("ticket_evaluator.os.walk")
@patch("ticket_evaluator.subprocess.run")
def test_evaluate_pre_release_coverage_baja(
    mock_run: MagicMock,
    mock_walk: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """Pre-release falla cuando coverage < 98%."""
    mock_walk.return_value = []

    mock_run.side_effect = [
        _mock_result(0, "all passed"),
        # coverage 85%
        _mock_result(0, "TOTAL   100   15   85%"),
        _mock_result(0, ""),
        _mock_result(0, ""),
        _mock_result(0, "feat(ISS-043): algo"),
        _mock_result(0, "## main"),
        _mock_result(0, ""),
    ]

    result = evaluator.evaluate("043", "pre_release", repo_path="/tmp/repo")

    assert result.passed is False
    cov_check = next(c for c in result.checks if c.name == "coverage_98")
    assert cov_check.passed is False
    assert "85" in cov_check.detail


# ── Pre-release: lint con errores ────────────────────────────

@patch("ticket_evaluator.os.walk")
@patch("ticket_evaluator.subprocess.run")
def test_evaluate_pre_release_lint_con_errores(
    mock_run: MagicMock,
    mock_walk: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """Pre-release falla cuando ruff check retorna errores."""
    mock_walk.return_value = []

    mock_run.side_effect = [
        _mock_result(0, "all passed"),
        _mock_result(0, "TOTAL   100   0   100%"),
        # lint falla
        _mock_result(1, "E501: line too long"),
        _mock_result(0, ""),
        _mock_result(0, "feat(ISS-043): algo"),
        _mock_result(0, "## main"),
        _mock_result(0, ""),
    ]

    result = evaluator.evaluate("043", "pre_release", repo_path="/tmp/repo")

    assert result.passed is False
    lint_check = next(c for c in result.checks if c.name == "lint_clean")
    assert lint_check.passed is False


# ── Pre-release: archivo grande ──────────────────────────────

@patch("ticket_evaluator.subprocess.run")
@patch("ticket_evaluator.os.walk")
def test_evaluate_pre_release_archivo_grande(
    mock_walk: MagicMock,
    mock_run: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """Pre-release falla cuando hay archivo .py con >1000 lineas."""
    # Simular archivo grande para _check_no_large_files
    mock_walk.return_value = [
        ("/tmp/repo", [], ["big_file.py"]),
    ]

    mock_run.side_effect = [
        _mock_result(0, "all passed"),
        _mock_result(0, "TOTAL   100   0   100%"),
        _mock_result(0, ""),
        # type hints
        _mock_result(0, ""),
        _mock_result(0, "feat(ISS-043): algo"),
        _mock_result(0, "## main"),
        _mock_result(0, ""),
    ]

    # Mock _count_lines para el archivo grande
    with patch.object(
        TicketEvaluator, "_count_lines", return_value=1500
    ):
        result = evaluator.evaluate(
            "043", "pre_release", repo_path="/tmp/repo"
        )

    assert result.passed is False
    large_check = next(
        c for c in result.checks if c.name == "no_large_files"
    )
    assert large_check.passed is False
    assert "1500" in large_check.detail


# ── Pre-release: commit format incorrecto ────────────────────

@patch("ticket_evaluator.os.walk")
@patch("ticket_evaluator.subprocess.run")
def test_evaluate_pre_release_commit_format_incorrecto(
    mock_run: MagicMock,
    mock_walk: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """Pre-release falla cuando commit no sigue formato obligatorio."""
    mock_walk.return_value = []

    mock_run.side_effect = [
        _mock_result(0, "all passed"),
        _mock_result(0, "TOTAL   100   0   100%"),
        _mock_result(0, ""),
        # type hints
        _mock_result(0, ""),
        # commit con formato incorrecto
        _mock_result(0, "added some stuff"),
        _mock_result(0, "## main"),
        _mock_result(0, ""),
    ]

    result = evaluator.evaluate("043", "pre_release", repo_path="/tmp/repo")

    assert result.passed is False
    commit_check = next(
        c for c in result.checks if c.name == "commit_format"
    )
    assert commit_check.passed is False
    assert "added some stuff" in commit_check.detail


# ── Pre-release: secretos detectados ─────────────────────────

@patch("ticket_evaluator.os.walk")
@patch("ticket_evaluator.subprocess.run")
def test_evaluate_pre_release_secretos_detectados(
    mock_run: MagicMock,
    mock_walk: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """Pre-release falla cuando se detectan secrets en archivos staged."""
    mock_walk.return_value = []

    mock_run.side_effect = [
        _mock_result(0, "all passed"),
        _mock_result(0, "TOTAL   100   0   100%"),
        _mock_result(0, ""),
        # type hints
        _mock_result(0, ""),
        _mock_result(0, "feat(ISS-043): algo"),
        _mock_result(0, "## main"),
        # staged files incluyen config con secrets
        _mock_result(0, "config.py\n"),
    ]

    # Mock open para leer el archivo con secret
    file_content = 'API_KEY = "sk-1234567890abcdef"'
    with patch("ticket_evaluator.os.path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data=file_content)):
        result = evaluator.evaluate(
            "043", "pre_release", repo_path="/tmp/repo"
        )

    assert result.passed is False
    secrets_check = next(
        c for c in result.checks if c.name == "no_secrets"
    )
    assert secrets_check.passed is False


# ── QA Review: sin tests ─────────────────────────────────────

@patch("ticket_evaluator.os.walk")
@patch("ticket_evaluator.subprocess.run")
def test_evaluate_qa_review_sin_tests(
    mock_run: MagicMock,
    mock_walk: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """QA review falla cuando no hay archivos de test."""
    # git diff retorna archivos modificados
    mock_run.return_value = _mock_result(0, "service.py\n")
    # os.walk no encuentra test_service.py
    mock_walk.return_value = [
        ("/tmp/repo/src", [], ["service.py"]),
    ]

    result = evaluator.evaluate("043", "qa_review", repo_path="/tmp/repo")

    assert result.passed is False
    test_check = next(
        c for c in result.checks if c.name == "test_files_exist"
    )
    assert test_check.passed is False


# ── QA Review: sin happy path ────────────────────────────────

@patch("ticket_evaluator.os.path.isdir")
@patch("ticket_evaluator.os.walk")
@patch("ticket_evaluator.subprocess.run")
def test_evaluate_qa_review_sin_happy_path(
    mock_run: MagicMock,
    mock_walk: MagicMock,
    mock_isdir: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """QA review falla cuando tests no tienen happy path."""
    # git diff
    mock_run.return_value = _mock_result(0, "\n")

    # Para _check_test_files_exist: archivos sin .py fuera de tests
    # Para _check_happy_path_tests: tests dir existe pero sin patron
    def walk_side_effect(path: str):
        if "tests" in path:
            return [("/tmp/repo/tests", [], ["test_algo.py"])]
        return [("/tmp/repo", [], [])]

    mock_walk.side_effect = walk_side_effect
    mock_isdir.return_value = True

    # Mock open para leer test sin happy path
    test_content = "def test_random_thing():\n    pass\n"
    with patch("builtins.open", mock_open(read_data=test_content)):
        result = evaluator.evaluate(
            "043", "qa_review", repo_path="/tmp/repo"
        )

    happy_check = next(
        c for c in result.checks if c.name == "happy_path_tests"
    )
    assert happy_check.passed is False


# ── PO Acceptance: criterios incompletos ─────────────────────

@patch("ticket_evaluator.subprocess.run")
def test_evaluate_po_acceptance_criterios_incompletos(
    mock_run: MagicMock,
    evaluator: TicketEvaluator,
) -> None:
    """PO acceptance falla cuando checklist tiene items sin marcar."""
    mock_run.side_effect = [
        # gh issue view — body con checklist incompleta
        _mock_result(0, "- [x] Criterio 1\n- [ ] Criterio 2\n- [ ] Criterio 3"),
        # tests pass (pytest en repo_path)
        _mock_result(0, "all passed"),
        # grep TODOs
        _mock_result(1, ""),  # grep no encuentra nada
    ]

    result = evaluator.evaluate("043", "po_acceptance", repo_path="/tmp/repo")

    assert result.passed is False
    checklist = next(
        c for c in result.checks if c.name == "checklist_complete"
    )
    assert checklist.passed is False
    assert "1/3" in checklist.detail


# ── Dispatcher llama metodo correcto ─────────────────────────

def test_evaluate_dispatcher_llama_metodo_correcto(
    evaluator: TicketEvaluator,
) -> None:
    """El dispatcher llama al metodo correcto segun eval_type."""
    with patch.object(
        evaluator, "_eval_pre_release", return_value=EvalResult(
            task_id="1", evaluation_type="pre_release", passed=True
        )
    ) as mock_pre:
        evaluator.evaluate("1", "pre_release", repo_path="/tmp")
        mock_pre.assert_called_once_with(task_id="1", repo_path="/tmp")

    with patch.object(
        evaluator, "_eval_qa_review", return_value=EvalResult(
            task_id="2", evaluation_type="qa_review", passed=True
        )
    ) as mock_qa:
        evaluator.evaluate("2", "qa_review", repo_path="/tmp")
        mock_qa.assert_called_once_with(task_id="2", repo_path="/tmp")

    # Tipo invalido
    result = evaluator.evaluate("3", "invalid_type")
    assert result.passed is False
    assert "invalido" in result.summary
