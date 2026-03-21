"""
Reclama una tarea para el nodo/equipo actual.
Bloquea en DynamoDB (atomico) y mueve el issue a In Progress en GitHub.

Soporta el nuevo sistema de nodos dinamicos (--node) con backward
compatibility para --team/--machine.
"""

import sys
import warnings

import click

from config import STATUS_IN_PROGRESS
from dynamo_client import claim_task, get_task, update_team_status
from github_client import get_branch_for_issue, move_issue_to_status

# Imports opcionales de nuevos modulos (no rompen si faltan)
try:
    from node_config import load_node_config
except ImportError:
    load_node_config = None  # type: ignore[assignment]

try:
    from node_registry import update_node_status, heartbeat
except ImportError:
    update_node_status = None  # type: ignore[assignment]
    heartbeat = None  # type: ignore[assignment]

try:
    from dependency_manager import is_task_unblocked
except ImportError:
    is_task_unblocked = None  # type: ignore[assignment]


def _resolve_node_id(
    node: str | None,
    team: str | None,
    machine: str | None,
) -> tuple[str | None, str | None]:
    """Resuelve el node_id y tenant_id desde argumentos o auto-detect.

    Retorna (node_id, tenant_id). Puede retornar (None, None) si
    no hay forma de determinar el nodo.
    """
    tenant_id = None

    if node:
        return node, _tenant_from_node_config()

    # Auto-detect desde ~/.covacha-node.yml
    if load_node_config is not None:
        cfg = load_node_config()
        if cfg and cfg.get("node_id"):
            tenant_id = cfg.get("tenant", {}).get("id")
            return cfg["node_id"], tenant_id

    # Fallback legacy: generar node_id desde team-machine
    if team and machine:
        warnings.warn(
            "--team/--machine estan deprecados. Usa --node o configura "
            "~/.covacha-node.yml con 'python covacha_cli.py init'",
            DeprecationWarning,
            stacklevel=2,
        )
        return f"{team}-{machine}", None

    return None, None


def _tenant_from_node_config() -> str | None:
    """Extrae el tenant_id del archivo de configuracion del nodo."""
    if load_node_config is None:
        return None
    cfg = load_node_config()
    return cfg.get("tenant", {}).get("id") if cfg else None


def _formatear_rama(task_id: str, task_data: dict | None) -> str:
    """Retorna la rama asociada al issue o 'por crear' si no existe."""
    if task_data is None:
        return "por crear"
    repo = task_data.get("repo", "covacha-payment")
    rama = get_branch_for_issue(int(task_id), repo)
    return rama if rama else "por crear"


def _verificar_dependencias(
    tenant_id: str | None,
    workspace: str | None,
    task_id: str,
) -> bool:
    """Verifica si la tarea esta desbloqueada. Retorna True si se puede reclamar."""
    if is_task_unblocked is None or tenant_id is None:
        return True
    ws = workspace or tenant_id
    return is_task_unblocked(tenant_id, ws, task_id)


def _registrar_nodo(
    tenant_id: str | None,
    node_id: str | None,
    task_id: str,
) -> None:
    """Actualiza el estado del nodo a working y envia heartbeat."""
    if not tenant_id or not node_id:
        return
    if update_node_status is not None:
        update_node_status(tenant_id, node_id, status="working", current_task=task_id)
    if heartbeat is not None:
        heartbeat(tenant_id, node_id)


def _imprimir_exito(
    task: str,
    team: str | None,
    machine: str | None,
    node_id: str | None,
    rama: str,
) -> None:
    """Imprime el resumen de la operacion exitosa."""
    quien = node_id or f"{team}@{machine}"
    click.echo(f"Task ISS-{task} reclamada por {quien}")
    click.echo(f"  Branch: {rama}")
    click.echo(f"  Modelo: sonnet")
    click.echo(f"  Siguiente: implementar y luego ejecutar release_task.py")


@click.command()
@click.option("--task", required=True, help="Numero del issue (ej: 043)")
@click.option("--team", default=None, help="[DEPRECATED] Nombre del equipo")
@click.option("--machine", default=None, help="[DEPRECATED] Maquina")
@click.option("--node", default=None, help="Node ID del swarm")
@click.option("--tenant", default=None, help="Tenant ID (auto-detect si no se da)")
@click.option("--workspace", default=None, help="Workspace ID (default=tenant)")
def main(
    task: str,
    team: str | None,
    machine: str | None,
    node: str | None,
    tenant: str | None,
    workspace: str | None,
) -> None:
    """Reclama una tarea y la bloquea atomicamente en DynamoDB y GitHub Board."""
    # Resolver identidad del nodo
    node_id, auto_tenant = _resolve_node_id(node, team, machine)
    tenant_id = tenant or auto_tenant

    # Verificar que la tarea no tenga dependencias pendientes
    ws = workspace or tenant_id
    if not _verificar_dependencias(tenant_id, ws, task):
        click.echo(
            f"Task ISS-{task} tiene dependencias pendientes. "
            "No se puede reclamar hasta que se resuelvan.",
            err=True,
        )
        sys.exit(1)

    # Resolver team/machine para el lock legacy en DynamoDB
    lock_team = team or (node_id or "unknown")
    lock_machine = machine or "auto"

    # Intentar adquirir el lock atomico en DynamoDB
    adquirida = claim_task(task_id=task, team=lock_team, machine=lock_machine)
    if not adquirida:
        click.echo(
            f"Task ISS-{task} ya esta bloqueada por otro equipo",
            err=True,
        )
        sys.exit(1)

    # Obtener metadata de la tarea para github_node_id y repo
    task_data = get_task(task)

    # Mover el issue en el GitHub Project Board a In Progress
    if task_data and task_data.get("github_node_id"):
        move_issue_to_status(task_data["github_node_id"], STATUS_IN_PROGRESS)

    # Registrar estado del nodo (nuevo sistema)
    _registrar_nodo(tenant_id, node_id, task)

    # Registrar estado legacy del equipo
    if team and machine:
        update_team_status(team, machine, current_task=task)

    rama = _formatear_rama(task, task_data)
    _imprimir_exito(task, team, machine, node_id, rama)


if __name__ == "__main__":
    main()
