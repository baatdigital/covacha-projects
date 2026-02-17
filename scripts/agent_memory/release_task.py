"""
Libera una tarea completada y guarda learnings en DynamoDB.
Cierra el issue en GitHub y lo mueve a Done en el board.
"""

import click

from config import STATUS_DONE
from dynamo_client import get_task, release_task, save_learning, update_team_status
from github_client import close_issue, move_issue_to_status


def _guardar_learnings(task: str, learnings: tuple[str, ...], team: str) -> int:
    """Persiste cada learning usando el módulo/repo de la tarea como clave."""
    if not learnings:
        return 0
    task_data = get_task(task)
    modulo = (task_data or {}).get("repo", f"ISS-{task}")
    for aprendizaje in learnings:
        save_learning(modulo, aprendizaje, team)
    return len(learnings)


def _sincronizar_github_done(task: str) -> None:
    """Cierra el issue en GitHub y mueve el item del board a Done."""
    task_data = get_task(task)
    if task_data is None:
        return
    repo = task_data.get("repo", "covacha-payment")
    node_id = task_data.get("github_node_id")
    close_issue(int(task), repo)
    if node_id:
        move_issue_to_status(node_id, STATUS_DONE)


def _imprimir_resultado(task: str, status: str, n_learnings: int, github_actualizado: bool) -> None:
    """Imprime el resumen de la liberación."""
    click.echo(f"✓ Task ISS-{task} liberada ({status})")
    click.echo(f"  Learnings guardados: {n_learnings}")
    if github_actualizado:
        click.echo("  Issue cerrado en GitHub")
        click.echo("  Board actualizado → Done")


@click.command()
@click.option("--task", required=True, help="Número del issue (ej: 043)")
@click.option("--status", default="done", type=click.Choice(["done", "blocked", "cancelled"]))
@click.option("--learning", default=None, help="Learning a guardar (puede repetirse)", multiple=True)
@click.option("--team", required=True, help="Nombre del equipo")
@click.option("--machine", required=True, help="Máquina")
def main(task: str, status: str, learning: tuple[str, ...], team: str, machine: str) -> None:
    """Libera una tarea, guarda learnings y actualiza GitHub si status=done."""
    # Eliminar LOCK y actualizar status en META
    release_task(task_id=task, status=status)

    # Persistir aprendizajes si se proveyeron
    n_learnings = _guardar_learnings(task, learning, team)

    # Sincronizar GitHub solo cuando la tarea queda completada
    github_actualizado = False
    if status == "done":
        _sincronizar_github_done(task)
        github_actualizado = True

    # Limpiar estado operativo del equipo
    update_team_status(team, machine, current_task=None)

    _imprimir_resultado(task, status, n_learnings, github_actualizado)


if __name__ == "__main__":
    main()
