"""Tests para bootstrap.py"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(number=10, title="Mi tarea", labels=None, branch="feature/ISS-10-foo"):
    return {"number": number, "title": title, "labels": labels or ["backend"], "branch": branch}


def _run_generate(team="backend", machine="mac-1", module=None, tasks=None, learnings=None, statuses=None):
    """Ejecuta generate_context con mocks y retorna el contenido del archivo generado."""
    from bootstrap import generate_context
    tasks = tasks if tasks is not None else [_make_task()]
    learnings = learnings or {}
    statuses = statuses or []

    with tempfile.NamedTemporaryFile(mode="r", suffix=".md", delete=False) as f:
        output_path = f.name

    try:
        with patch("bootstrap.get_available_tasks", return_value=tasks), \
             patch("bootstrap.get_all_team_statuses", return_value=statuses), \
             patch("bootstrap.get_learnings", return_value=learnings), \
             patch("bootstrap.update_team_status") as mock_update:
            generate_context(team=team, machine=machine, module=module, output=output_path)
        with open(output_path, "r") as fh:
            content = fh.read()
        return content, mock_update
    finally:
        os.unlink(output_path)


# ---------------------------------------------------------------------------
# _team_table
# ---------------------------------------------------------------------------

class TestTeamTable:
    def test_sin_equipos_retorna_mensaje_vacio(self):
        from bootstrap import _team_table
        assert "_No hay equipos activos registrados._" in _team_table([])

    def test_equipo_presente_aparece_en_tabla(self):
        from bootstrap import _team_table
        result = _team_table([{"team": "backend", "machine": "mac-1", "current_task": "ISS-5"}])
        assert "backend" in result
        assert "ISS-5" in result

    def test_tarea_none_muestra_guion(self):
        from bootstrap import _team_table
        result = _team_table([{"team": "frontend", "machine": "mac-2", "current_task": None}])
        assert "—" in result


# ---------------------------------------------------------------------------
# _learnings_section
# ---------------------------------------------------------------------------

class TestLearningsSection:
    def test_sin_gotchas_retorna_mensaje_por_defecto(self):
        from bootstrap import _learnings_section
        assert "Sin learnings" in _learnings_section({})

    def test_gotchas_listados(self):
        from bootstrap import _learnings_section
        result = _learnings_section({"gotchas": ["Usar batch writes", "Evitar scan completo"]})
        assert "Usar batch writes" in result
        assert "Evitar scan completo" in result


# ---------------------------------------------------------------------------
# _tasks_list
# ---------------------------------------------------------------------------

class TestTasksList:
    def test_lista_vacia_retorna_mensaje(self):
        from bootstrap import _tasks_list
        assert "Sin tareas" in _tasks_list([])

    def test_limita_a_5_tareas(self):
        from bootstrap import _tasks_list
        tasks = [_make_task(number=i, title=f"Tarea {i}") for i in range(10)]
        result = _tasks_list(tasks)
        # Solo deben aparecer los primeros 5 números
        assert "ISS-4" in result
        assert "ISS-5" not in result


# ---------------------------------------------------------------------------
# generate_context — happy path
# ---------------------------------------------------------------------------

class TestGenerateContext:
    def test_genera_archivo_con_encabezado_correcto(self):
        content, _ = _run_generate(team="backend", machine="mac-1", module="covacha-payment")
        assert "## covacha-payment — Contexto" in content

    def test_encabezado_usa_team_cuando_no_hay_modulo(self):
        content, _ = _run_generate(team="frontend", machine="mac-2", module=None)
        assert "## frontend — Contexto" in content

    def test_tarea_recomendada_aparece_en_content(self):
        content, _ = _run_generate(tasks=[_make_task(number=99, title="Test task")])
        assert "ISS-99" in content
        assert "Test task" in content

    def test_sin_tareas_muestra_sin_tarea_disponible(self):
        content, _ = _run_generate(tasks=[])
        assert "Sin tarea disponible" in content

    def test_llama_update_team_status_con_current_task_none(self):
        _, mock_update = _run_generate(team="backend", machine="mac-2")
        mock_update.assert_called_once_with("backend", "mac-2", current_task=None)

    def test_learnings_aparecen_en_content(self):
        learnings = {"gotchas": ["No olvidar el GSI"]}
        content, _ = _run_generate(module="covacha-payment", learnings=learnings)
        assert "No olvidar el GSI" in content

    def test_sin_module_no_llama_get_learnings(self):
        from bootstrap import generate_context
        with tempfile.NamedTemporaryFile(mode="r", suffix=".md", delete=False) as f:
            output_path = f.name
        try:
            with patch("bootstrap.get_available_tasks", return_value=[]), \
                 patch("bootstrap.get_all_team_statuses", return_value=[]), \
                 patch("bootstrap.get_learnings") as mock_learnings, \
                 patch("bootstrap.update_team_status"):
                generate_context(team="backend", machine="mac-1", module=None, output=output_path)
            mock_learnings.assert_not_called()
        finally:
            os.unlink(output_path)

    def test_equipo_activo_aparece_en_content(self):
        statuses = [{"team": "frontend", "machine": "mac-2", "current_task": "ISS-7"}]
        content, _ = _run_generate(statuses=statuses)
        assert "frontend" in content
        assert "ISS-7" in content

    def test_branch_por_crear_cuando_branch_es_none(self):
        task = _make_task(branch=None)
        content, _ = _run_generate(tasks=[task])
        assert "por crear" in content
