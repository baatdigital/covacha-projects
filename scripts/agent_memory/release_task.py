"""
Libera una tarea completada y guarda learnings en DynamoDB.
Cierra el issue en GitHub y lo mueve a Done en el board.

Soporta el nuevo sistema de nodos dinamicos (--node) con backward
compatibility para --team/--machine.
"""

import json
import warnings

import click

from config import STATUS_DONE
from dynamo_client import get_task, release_task, save_learning, update_team_status
from github_client import close_issue, move_issue_to_status

# Imports opcionales de nuevos modulos
try:
    from node_config import load_node_config
except ImportError:
    load_node_config = None  # type: ignore[assignment]

try:
    from node_registry import update_node_status
except ImportError:
    update_node_status = None  # type: ignore[assignment]

try:
    from dependency_manager import resolve_dependency
except ImportError:
    resolve_dependency = None  # type: ignore[assignment]

try:
    from message_bus import send_message
except ImportError:
    send_message = None  # type: ignore[assignment]

try:
    from contract_registry import publish_contract
except ImportError:
    publish_contract = None  # type: ignore[assignment]


def _resolve_node_id(
    node: str | None,
    team: str | None,
    machine: str | None,
) -> tuple[str | None, str | None]:
    """Resuelve node_id y tenant_id desde argumentos o auto-detect.

    Retorna (node_id, tenant_id).
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

    # Fallback legacy
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


def _guardar_learnings(
    task: str,
    learnings: tuple[str, ...],
    team: str | None,
) -> int:
    """Persiste cada learning usando el modulo/repo de la tarea como clave."""
    if not learnings:
        return 0
    task_data = get_task(task)
    modulo = (task_data or {}).get("repo", f"ISS-{task}")
    owner = team or "unknown"
    for aprendizaje in learnings:
        save_learning(modulo, aprendizaje, owner)
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


def _resolver_dependencias(
    tenant_id: str | None,
    workspace: str | None,
    task_id: str,
) -> list[str]:
    """Resuelve las dependencias de la tarea completada."""
    if resolve_dependency is None or tenant_id is None:
        return []
    ws = workspace or tenant_id
    return resolve_dependency(tenant_id, ws, task_id)


def _notificar_completado(
    tenant_id: str | None,
    workspace: str | None,
    node_id: str | None,
    task_id: str,
) -> None:
    """Envia mensaje de tarea completada al bus."""
    if send_message is None or not tenant_id or not node_id:
        return
    ws = workspace or tenant_id
    send_message(
        tenant_id, ws, node_id,
        msg_type="task_completed",
        task_id=task_id,
    )


def _publicar_contrato(
    tenant_id: str | None,
    workspace: str | None,
    node_id: str | None,
    task_id: str,
    contract_json: str,
) -> None:
    """Publica un contrato de API si se proporciono --contract."""
    if publish_contract is None or not tenant_id or not node_id:
        return
    ws = workspace or tenant_id
    data = json.loads(contract_json)
    publish_contract(
        tenant_id=tenant_id,
        workspace_id=ws,
        name=data.get("name", "unnamed"),
        version=data.get("version", "1.0"),
        method=data.get("method", "GET"),
        path=data.get("path", "/"),
        request_schema=data.get("request_schema", {}),
        response_schema=data.get("response_schema", {}),
        published_by=node_id,
        task_id=task_id,
    )


def _actualizar_nodo_idle(
    tenant_id: str | None,
    node_id: str | None,
) -> None:
    """Marca el nodo como idle sin tarea actual."""
    if update_node_status is None or not tenant_id or not node_id:
        return
    update_node_status(tenant_id, node_id, status="idle", current_task=None)


def _imprimir_resultado(
    task: str,
    status: str,
    n_learnings: int,
    github_actualizado: bool,
    desbloqueadas: list[str],
) -> None:
    """Imprime el resumen de la liberacion."""
    click.echo(f"Task ISS-{task} liberada ({status})")
    click.echo(f"  Learnings guardados: {n_learnings}")
    if github_actualizado:
        click.echo("  Issue cerrado en GitHub")
        click.echo("  Board actualizado -> Done")
    if desbloqueadas:
        click.echo(f"  Tareas desbloqueadas: {', '.join(desbloqueadas)}")


@click.command()
@click.option("--task", required=True, help="Numero del issue (ej: 043)")
@click.option("--status", default="done", type=click.Choice(["done", "blocked", "cancelled"]))
@click.option("--learning", default=None, help="Learning a guardar (puede repetirse)", multiple=True)
@click.option("--team", default=None, help="[DEPRECATED] Nombre del equipo")
@click.option("--machine", default=None, help="[DEPRECATED] Maquina")
@click.option("--node", default=None, help="Node ID del swarm")
@click.option("--tenant", default=None, help="Tenant ID (auto-detect si no se da)")
@click.option("--workspace", default=None, help="Workspace ID (default=tenant)")
@click.option("--contract", default=None, help="JSON string del contrato a publicar")
def main(
    task: str,
    status: str,
    learning: tuple[str, ...],
    team: str | None,
    machine: str | None,
    node: str | None,
    tenant: str | None,
    workspace: str | None,
    contract: str | None,
) -> None:
    """Libera una tarea, guarda learnings y actualiza GitHub si status=done."""
    # Resolver identidad del nodo
    node_id, auto_tenant = _resolve_node_id(node, team, machine)
    tenant_id = tenant or auto_tenant
    ws = workspace or tenant_id

    # Eliminar LOCK y actualizar status en META
    release_task(task_id=task, status=status)

    # Persistir aprendizajes si se proveyeron
    n_learnings = _guardar_learnings(task, learning, team)

    # Sincronizar GitHub solo cuando la tarea queda completada
    github_actualizado = False
    desbloqueadas: list[str] = []

    if status == "done":
        _sincronizar_github_done(task)
        github_actualizado = True

        # Resolver dependencias para desbloquear tareas dependientes
        desbloqueadas = _resolver_dependencias(tenant_id, ws, task)

        # Notificar al bus de mensajes
        _notificar_completado(tenant_id, ws, node_id, task)

        # Publicar contrato si se proporciono
        if contract:
            _publicar_contrato(tenant_id, ws, node_id, task, contract)

    # Actualizar estado del nodo a idle
    _actualizar_nodo_idle(tenant_id, node_id)

    # Limpiar estado legacy del equipo
    if team and machine:
        update_team_status(team, machine, current_task=None)

    _imprimir_resultado(task, status, n_learnings, github_actualizado, desbloqueadas)


if __name__ == "__main__":
    main()
