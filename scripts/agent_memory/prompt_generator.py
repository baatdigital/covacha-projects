"""Generador de prompts para Claude Code en el Agent Swarm.

Genera prompts markdown estructurados basandose en el contexto
del task, contratos, learnings y mensajes del equipo.
"""
import re
from typing import Any


def generate_task_slug(title: str) -> str:
    """Convierte un titulo a slug kebab-case (max 40 chars, solo alfanumerico y guiones)."""
    slug = title.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    if len(slug) > 40:
        slug = slug[:40].rstrip("-")
    return slug


def _format_contracts_section(contracts: list[dict]) -> str:
    """Formatea la seccion de contratos de API disponibles."""
    if not contracts:
        return "No hay contratos registrados.\n"
    lines: list[str] = []
    for c in contracts:
        method = c.get("method", "?")
        path = c.get("path", "?")
        lines.append(f"- **{method} {path}**")
        req = c.get("request_schema")
        if req:
            lines.append(f"  - Request: `{req}`")
        resp = c.get("response_schema")
        if resp:
            lines.append(f"  - Response: `{resp}`")
    return "\n".join(lines) + "\n"


def _format_learnings_section(learnings: dict | None) -> str:
    """Formatea la seccion de learnings del modulo."""
    if not learnings:
        return "No hay learnings registrados.\n"
    gotchas = learnings.get("gotchas", [])
    if not gotchas:
        return "No hay learnings registrados.\n"
    lines = [f"- {g}" for g in gotchas]
    return "\n".join(lines) + "\n"


def _format_messages_section(messages: list[dict] | None) -> str:
    """Formatea la seccion de mensajes recientes del equipo."""
    if not messages:
        return "No hay mensajes recientes.\n"
    lines: list[str] = []
    for msg in messages:
        from_node = msg.get("from_node", "?")
        msg_type = msg.get("type", "?")
        task_id = msg.get("task_id", "")
        suffix = f" (ISS-{task_id})" if task_id else ""
        lines.append(f"- [{msg_type}] de {from_node}{suffix}")
    return "\n".join(lines) + "\n"


def _infer_branch(task: dict) -> str:
    """Infiere el nombre de branch para la tarea."""
    existing = task.get("branch")
    if existing:
        return existing
    number = task.get("number", "000")
    title = task.get("title", "tarea")
    slug = generate_task_slug(title)
    return f"feature/ISS-{number}-{slug}"


def _format_labels(task: dict) -> str:
    """Formatea labels como string separado por comas."""
    labels = task.get("labels", [])
    if not labels:
        return "sin labels"
    return ", ".join(labels)


def generate_implementation_prompt(
    task: dict,
    node_config: dict,
    contracts: list[dict] | None = None,
    learnings: dict | None = None,
    messages: list[dict] | None = None,
    workspace_id: str | None = None,
) -> str:
    """Genera un prompt markdown completo para implementar una tarea.

    Incluye secciones de contexto, contratos, learnings, mensajes
    y reglas obligatorias para que Claude Code ejecute autonomamente.
    """
    number = task.get("number", "???")
    title = task.get("title", "Sin titulo")
    branch = _infer_branch(task)
    repo = task.get("repo", "desconocido")
    model = task.get("recommended_model", "sonnet")
    labels_str = _format_labels(task)
    description = task.get("body") or title

    contracts_text = _format_contracts_section(contracts or [])
    learnings_text = _format_learnings_section(learnings)
    messages_text = _format_messages_section(messages)

    prompt = f"""## Tarea: ISS-{number} — {title}

**Branch:** {branch} (crear si no existe)
**Repo:** {repo}
**Labels:** {labels_str}
**Modelo recomendado:** {model}

### Descripcion
{description}

### Contratos de API disponibles
{contracts_text}
### Learnings del modulo
{learnings_text}
### Mensajes recientes del equipo
{messages_text}
### Reglas obligatorias
- Ejecutar pytest -v al terminar, todos deben pasar
- Coverage >= 98% en archivos modificados
- ruff check . sin errores
- Commit format: tipo(ISS-{number}): descripcion en español
- Push a la branch (no a main)
- Max 1000 lineas por archivo, 50 por funcion
- Type hints en todas las funciones nuevas

### Al terminar
- Reportar learnings encontrados (prefijo "Learning: ...")
- Si creaste endpoint nuevo, reportar contrato (method, path, schemas)
"""
    return prompt


def _build_review_checklist(role: str) -> str:
    """Genera checklist de review segun el rol."""
    if role == "qa_review":
        return (
            "- [ ] Tests unitarios cubren happy path y error cases\n"
            "- [ ] Coverage >= 98% en archivos modificados\n"
            "- [ ] No hay tests saltados (skip) sin justificacion\n"
            "- [ ] pytest -v pasa sin errores\n"
            "- [ ] Edge cases cubiertos (nulos, vacios, limites)\n"
        )
    # code_review por defecto
    return (
        "- [ ] Codigo sigue convenciones (snake_case, type hints)\n"
        "- [ ] Funciones <= 50 lineas, archivos <= 1000 lineas\n"
        "- [ ] ruff check . sin errores\n"
        "- [ ] No hay credenciales hardcodeadas\n"
        "- [ ] Manejo de errores con excepciones especificas\n"
        "- [ ] Docstrings en funciones publicas\n"
    )


def generate_review_prompt(
    task: dict,
    pr_url: str,
    role: str,
) -> str:
    """Genera prompt para review (QA o code review).

    El rol puede ser 'qa_review' o 'code_review'.
    Incluye checklist especifico segun el rol y las instrucciones
    para ejecutar la revision.
    """
    number = task.get("number", "???")
    title = task.get("title", "Sin titulo")
    checklist = _build_review_checklist(role)

    prompt = f"""## Review: ISS-{number} — {title}
**PR:** {pr_url}
**Rol:** {role}

### Checklist
{checklist}
### Instrucciones
- Clonar la branch y ejecutar tests localmente
- Verificar cada criterio del checklist
- Reportar resultado como: PASS o FAIL con detalles
"""
    return prompt
