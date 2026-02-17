"""
Muestra el estado actual de todos los Agent Teams y tareas disponibles.
"""

import time

import click
from tabulate import tabulate

from dynamo_client import get_all_team_statuses, get_available_tasks
from model_selector import select_model


def _ping(last_seen: int | None) -> str:
    """Convierte timestamp Unix a texto legible: 'hace 5min', 'hace 2h'."""
    if not last_seen:
        return "-"
    delta = int(time.time()) - last_seen
    if delta < 60:
        return f"hace {delta}s"
    if delta < 3600:
        return f"hace {delta // 60}min"
    return f"hace {delta // 3600}h"


def _filas_equipos(statuses: list[dict]) -> list[list]:
    """Construye filas para la tabla de equipos activos."""
    return [
        [e.get("team", "?"), e.get("machine", "?"), e.get("current_task") or "-", _ping(e.get("last_seen"))]
        for e in statuses
    ]


def _filas_tareas(tasks: list[dict]) -> list[list]:
    """Construye filas para la tabla de tareas disponibles con modelo recomendado."""
    filas = []
    for tarea in tasks:
        numero = tarea.get("task_id") or tarea.get("PK", "").replace("TASK#", "")
        titulo = (tarea.get("title") or "")[:40]
        labels = tarea.get("labels", [])
        modelo, _ = select_model(labels)
        filas.append([numero, titulo, ", ".join(labels) or "-", modelo])
    return filas


@click.command()
@click.option("--label", default=None, help="Filtrar tareas por label")
def main(label: str | None) -> None:
    """Dashboard de estado de Agent Teams y tareas disponibles en DynamoDB."""
    # Sección de equipos activos
    click.echo("\n=== Estado de Equipos ===")
    statuses = get_all_team_statuses()
    if statuses:
        click.echo(tabulate(
            _filas_equipos(statuses),
            headers=["Team", "Machine", "Tarea actual", "Último ping"],
            tablefmt="plain",
        ))
    else:
        click.echo("  (ningún equipo registrado)")

    # Sección de tareas disponibles
    label_desc = f" (label: {label})" if label else ""
    click.echo(f"\n=== Tareas Disponibles{label_desc} ===")
    tasks = get_available_tasks(label=label)
    if tasks:
        click.echo(tabulate(
            _filas_tareas(tasks),
            headers=["ISS#", "Título", "Labels", "Modelo rec."],
            tablefmt="plain",
        ))
    else:
        click.echo("  (no hay tareas disponibles)")
    click.echo()


if __name__ == "__main__":
    main()
