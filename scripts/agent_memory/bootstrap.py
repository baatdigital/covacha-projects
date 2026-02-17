"""
Genera CONTEXT.md con contexto de sesión para un Agent Team.
Lee tareas disponibles, learnings y estado de equipos desde DynamoDB.
"""
from datetime import datetime

import click

from dynamo_client import get_available_tasks, get_learnings, update_team_status, get_all_team_statuses
from model_selector import select_model


def _team_table(statuses: list[dict]) -> str:
    if not statuses:
        return "_No hay equipos activos registrados._"
    rows = ["| Equipo | Máquina | Tarea actual |", "| --- | --- | --- |"]
    rows += [f"| {s.get('team','?')} | {s.get('machine','?')} | {s.get('current_task') or '—'} |" for s in statuses]
    return "\n".join(rows)


def _tasks_list(tasks: list[dict], limit: int = 5) -> str:
    if not tasks:
        return "_Sin tareas disponibles para este equipo/máquina._"
    return "\n".join(
        f"- ISS-{t.get('number')}: {t.get('title','(sin título)')} `[{', '.join(t.get('labels',[]))}]`"
        for t in tasks[:limit]
    )


def _learnings_section(learnings: dict) -> str:
    gotchas: list[str] = learnings.get("gotchas", [])
    return "\n".join(f"- {g}" for g in gotchas) if gotchas else "_Sin learnings registrados aún._"


def generate_context(team: str, machine: str, module: str | None, output: str) -> None:
    """
    Lee el estado de DynamoDB y escribe el CONTEXT.md para el equipo indicado.

    Args:
        team: Nombre del equipo (backend/frontend)
        machine: Máquina desde la que corre el agente (mac-1/mac-2)
        module: Módulo target para cargar learnings (ej: covacha-payment)
        output: Path del archivo CONTEXT.md a generar
    """
    tasks = get_available_tasks(label=team)
    team_statuses = get_all_team_statuses()
    learnings = get_learnings(module) if module else {}

    rec = tasks[0] if tasks else None
    rec_model, rec_just = select_model(rec.get("labels", []) if rec else [])
    rec_number = rec.get("number", "—") if rec else "—"
    rec_title = rec.get("title", "Sin tarea disponible") if rec else "Sin tarea disponible"
    rec_branch = (rec.get("branch") or "por crear") if rec else "—"
    rec_labels_str = ", ".join(rec.get("labels", [])) if rec else "—"

    content = f"""## {module or team} — Contexto [{datetime.now().strftime("%Y-%m-%d")}]
<!-- Generado automáticamente por bootstrap.py. No editar manualmente. -->

### Modelo recomendado
- **{rec_model}** — {rec_just}

### Tarea recomendada
- ISS-{rec_number}: {rec_title}
- Branch: {rec_branch}
- Labels: {rec_labels_str}

### Learnings activos
{_learnings_section(learnings)}

### Equipo activo
{_team_table(team_statuses)}

### Tareas disponibles ({team}/{machine})
{_tasks_list(tasks)}
"""

    with open(output, "w", encoding="utf-8") as fh:
        fh.write(content)

    update_team_status(team, machine, current_task=None)
    print(f"✓ CONTEXT.md generado en {output}")


@click.command()
@click.option("--team", required=True, help="Nombre del equipo (backend/frontend)")
@click.option("--machine", required=True, help="Máquina (mac-1/mac-2)")
@click.option("--module", default=None, help="Módulo target (ej: covacha-payment)")
@click.option("--output", default="CONTEXT.md", help="Path del archivo generado")
def main(team: str, machine: str, module: str | None, output: str) -> None:
    """Genera CONTEXT.md con contexto de sesión para un Agent Team."""
    generate_context(team=team, machine=machine, module=module, output=output)


if __name__ == "__main__":
    main()
