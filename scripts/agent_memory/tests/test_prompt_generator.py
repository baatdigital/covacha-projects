"""Tests para prompt_generator.py — generacion de prompts para Claude Code."""
import pytest

from prompt_generator import (
    generate_implementation_prompt,
    generate_review_prompt,
    generate_task_slug,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _sample_task() -> dict:
    """Retorna una tarea de ejemplo."""
    return {
        "number": "043",
        "title": "Implementar endpoint SPEI transfer",
        "body": "Crear POST /api/v1/spei/transfer con validacion CLABE.",
        "repo": "covacha-payment",
        "labels": ["backend", "feature"],
        "recommended_model": "sonnet",
        "branch": "feature/ISS-043-spei-transfer",
    }


def _sample_node_config() -> dict:
    """Retorna node_config de ejemplo."""
    return {
        "node_id": "test-node-1",
        "workspaces": [{
            "id": "baatdigital",
            "repos": [{"path": "/x/covacha-payment", "name": "covacha-payment"}],
            "capabilities": ["backend", "testing"],
        }],
    }


# ---------------------------------------------------------------------------
# generate_implementation_prompt
# ---------------------------------------------------------------------------

class TestGenerateImplementationPrompt:
    def test_incluye_task_info(self):
        """Debe incluir numero, titulo, branch, repo y labels."""
        task = _sample_task()
        result = generate_implementation_prompt(task, _sample_node_config())

        assert "ISS-043" in result
        assert "Implementar endpoint SPEI transfer" in result
        assert "feature/ISS-043-spei-transfer" in result
        assert "covacha-payment" in result
        assert "backend" in result

    def test_incluye_contracts(self):
        """Debe incluir contratos de API cuando se proveen."""
        task = _sample_task()
        contracts = [{
            "method": "POST",
            "path": "/api/v1/spei/transfer",
            "request_schema": {"clabe": "string"},
            "response_schema": {"success": "boolean"},
        }]
        result = generate_implementation_prompt(
            task, _sample_node_config(), contracts=contracts
        )

        assert "POST /api/v1/spei/transfer" in result
        assert "request_schema" in result.lower() or "Request" in result

    def test_incluye_learnings(self):
        """Debe incluir gotchas del modulo."""
        task = _sample_task()
        learnings = {"gotchas": [
            "Usar Decimal para montos",
            "CLABE tiene 18 digitos",
        ]}
        result = generate_implementation_prompt(
            task, _sample_node_config(), learnings=learnings
        )

        assert "Usar Decimal para montos" in result
        assert "CLABE tiene 18 digitos" in result

    def test_incluye_reglas_obligatorias(self):
        """Debe incluir las reglas de pytest, coverage, ruff, etc."""
        task = _sample_task()
        result = generate_implementation_prompt(task, _sample_node_config())

        assert "pytest -v" in result
        assert "Coverage >= 98%" in result
        assert "ruff check" in result
        assert "Max 1000 lineas" in result

    def test_sin_body_usa_title(self):
        """Si no hay body, usa el titulo como descripcion."""
        task = _sample_task()
        del task["body"]
        result = generate_implementation_prompt(task, _sample_node_config())

        assert "Implementar endpoint SPEI transfer" in result

    def test_sin_branch_genera_automaticamente(self):
        """Si no hay branch, genera uno a partir del titulo."""
        task = _sample_task()
        del task["branch"]
        result = generate_implementation_prompt(task, _sample_node_config())

        assert "feature/ISS-043-" in result

    def test_incluye_mensajes(self):
        """Debe incluir mensajes recientes del equipo."""
        task = _sample_task()
        messages = [
            {"from_node": "mac-2", "type": "task_completed", "task_id": "042"},
        ]
        result = generate_implementation_prompt(
            task, _sample_node_config(), messages=messages
        )

        assert "mac-2" in result
        assert "task_completed" in result


# ---------------------------------------------------------------------------
# generate_task_slug
# ---------------------------------------------------------------------------

class TestGenerateTaskSlug:
    def test_limpia_titulo(self):
        """Debe convertir a kebab-case limpio."""
        assert generate_task_slug("Implementar endpoint SPEI") == "implementar-endpoint-spei"

    def test_max_40_chars(self):
        """Debe truncar a 40 caracteres maximo."""
        titulo = "Este es un titulo muy largo que excede los cuarenta caracteres facilmente"
        slug = generate_task_slug(titulo)
        assert len(slug) <= 40

    def test_remueve_caracteres_especiales(self):
        """Debe remover acentos y caracteres no alfanumericos."""
        assert generate_task_slug("fix: bug #123 (urgent!)") == "fix-bug-123-urgent"

    def test_no_guiones_al_inicio_ni_final(self):
        """No debe tener guiones al inicio o final."""
        slug = generate_task_slug("  --hello--  ")
        assert not slug.startswith("-")
        assert not slug.endswith("-")


# ---------------------------------------------------------------------------
# generate_review_prompt
# ---------------------------------------------------------------------------

class TestGenerateReviewPrompt:
    def test_qa_review(self):
        """Debe generar checklist de QA."""
        task = _sample_task()
        result = generate_review_prompt(
            task,
            "https://github.com/baatdigital/covacha-payment/pull/87",
            "qa_review",
        )

        assert "ISS-043" in result
        assert "qa_review" in result
        assert "pytest -v" in result
        assert "Coverage >= 98%" in result
        assert "pull/87" in result

    def test_code_review(self):
        """Debe generar checklist de code review."""
        task = _sample_task()
        result = generate_review_prompt(
            task,
            "https://github.com/baatdigital/covacha-payment/pull/87",
            "code_review",
        )

        assert "snake_case" in result
        assert "ruff check" in result
        assert "credenciales" in result
