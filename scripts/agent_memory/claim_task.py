"""
Reclama una tarea para el equipo actual.
Bloquea en DynamoDB (atómico) y mueve el issue a In Progress en GitHub.
"""

import sys

import click

from config import STATUS_IN_PROGRESS
from dynamo_client import claim_task, get_task, update_team_status
from github_client import get_branch_for_issue, move_issue_to_status


def _formatear_rama(task_id: str, task_data: dict | None) -> str:
    """Retorna la rama asociada al issue o 'por crear' si no existe."""
    if task_data is None:
        return "por crear"
    repo = task_data.get("repo", "covacha-payment")
    rama = get_branch_for_issue(int(task_id), repo)
    return rama if rama else "por crear"


def _imprimir_exito(task: str, team: str, machine: str, rama: str) -> None:
    """Imprime el resumen de la operación exitosa."""
    click.echo(f"✓ Task ISS-{task} reclamada por {team}@{machine}")
    click.echo(f"  Branch: {rama}")
    click.echo(f"  Modelo: sonnet")
    click.echo(f"  Siguiente: implementar y luego ejecutar release_task.py")


@click.command()
@click.option("--task", required=True, help="Número del issue (ej: 043)")
@click.option("--team", required=True, help="Nombre del equipo (backend/frontend)")
@click.option("--machine", required=True, help="Máquina (mac-1/mac-2)")
def main(task: str, team: str, machine: str) -> None:
    """Reclama una tarea y la bloquea atómicamente en DynamoDB y GitHub Board."""
    # Intentar adquirir el lock atómico en DynamoDB
    adquirida = claim_task(task_id=task, team=team, machine=machine)
    if not adquirida:
        click.echo(f"✗ Task ISS-{task} ya está bloqueada por otro equipo", err=True)
        sys.exit(1)

    # Obtener metadata de la tarea para github_node_id y repo
    task_data = get_task(task)

    # Mover el issue en el GitHub Project Board a In Progress
    if task_data and task_data.get("github_node_id"):
        move_issue_to_status(task_data["github_node_id"], STATUS_IN_PROGRESS)

    # Registrar el estado operativo del equipo
    update_team_status(team, machine, current_task=task)

    rama = _formatear_rama(task, task_data)
    _imprimir_exito(task, team, machine, rama)


if __name__ == "__main__":
    main()
