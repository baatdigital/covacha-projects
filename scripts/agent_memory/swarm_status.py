"""
Muestra el estado actual del swarm de nodos usando node_registry.
Reemplaza a team_status.py (que se mantiene por backward compat).
"""

import time

import click
from tabulate import tabulate

from dynamo_client import get_available_tasks
from model_selector import select_model

# Imports opcionales
try:
    from node_config import load_node_config
except ImportError:
    load_node_config = None  # type: ignore[assignment]

try:
    from node_registry import discover_nodes, get_swarm_summary
except ImportError:
    discover_nodes = None  # type: ignore[assignment]
    get_swarm_summary = None  # type: ignore[assignment]

try:
    from message_bus import get_recent_messages
except ImportError:
    get_recent_messages = None  # type: ignore[assignment]

try:
    from dependency_manager import is_task_unblocked
except ImportError:
    is_task_unblocked = None  # type: ignore[assignment]


def _ping(last_hb: int | None) -> str:
    """Convierte timestamp Unix a texto legible."""
    if not last_hb:
        return "-"
    delta = int(time.time()) - last_hb
    if delta < 60:
        return f"hace {delta}s"
    if delta < 3600:
        return f"hace {delta // 60}min"
    return f"hace {delta // 3600}h"


def _resolve_tenant(tenant: str | None) -> str | None:
    """Resuelve tenant_id desde argumento o auto-detect."""
    if tenant:
        return tenant
    if load_node_config is not None:
        cfg = load_node_config()
        if cfg:
            return cfg.get("tenant", {}).get("id")
    return None


def _filas_nodos(nodes: list[dict]) -> list[list]:
    """Construye filas para la tabla de nodos activos."""
    return [
        [
            n.get("node_id", "?"),
            ", ".join(n.get("capabilities", [])) or "-",
            ", ".join(n.get("roles", [])) or "-",
            n.get("status", "?"),
            n.get("current_task") or "-",
            n.get("current_workspace") or "-",
            _ping(n.get("last_heartbeat")),
        ]
        for n in nodes
    ]


def _mostrar_nodos(tenant_id: str, workspace: str | None) -> None:
    """Muestra tabla de nodos del swarm."""
    click.echo("\n=== Swarm Nodes ===")
    if discover_nodes is None:
        click.echo("  (modulo node_registry no disponible)")
        return

    nodes = discover_nodes(tenant_id, only_active=False)
    if workspace:
        nodes = [
            n for n in nodes
            if n.get("current_workspace") == workspace
        ]

    if nodes:
        click.echo(tabulate(
            _filas_nodos(nodes),
            headers=[
                "Node", "Capabilities", "Role", "Status",
                "Task", "Workspace", "Last HB",
            ],
            tablefmt="plain",
        ))
    else:
        click.echo("  (ningun nodo registrado)")


def _mostrar_mensajes(
    tenant_id: str,
    workspace: str | None,
) -> None:
    """Muestra mensajes recientes del workspace."""
    click.echo("\n=== Mensajes Recientes ===")
    if get_recent_messages is None:
        click.echo("  (modulo message_bus no disponible)")
        return
    ws = workspace or tenant_id
    msgs = get_recent_messages(tenant_id, ws, limit=5)
    if msgs:
        for m in msgs:
            ts = m.get("created_at", 0)
            tipo = m.get("type", "?")
            task = m.get("task_id", "")
            src = m.get("from_node", "?")
            click.echo(f"  [{_ping(ts)}] {tipo} task={task} from={src}")
    else:
        click.echo("  (sin mensajes recientes)")


def _mostrar_tareas_bloqueadas(
    tenant_id: str,
    workspace: str | None,
) -> None:
    """Muestra tareas con dependencias pendientes."""
    click.echo("\n=== Tareas Bloqueadas ===")
    if is_task_unblocked is None:
        click.echo("  (modulo dependency_manager no disponible)")
        return

    ws = workspace or tenant_id
    tasks = get_available_tasks()
    bloqueadas: list[str] = []
    for t in tasks[:20]:
        tid = str(t.get("number", ""))
        if tid and not is_task_unblocked(tenant_id, ws, tid):
            titulo = (t.get("title") or "")[:40]
            bloqueadas.append(f"  ISS-{tid}: {titulo}")

    if bloqueadas:
        for b in bloqueadas:
            click.echo(b)
    else:
        click.echo("  (ninguna tarea bloqueada)")


def _mostrar_tareas(label: str | None) -> None:
    """Muestra tareas disponibles con modelo recomendado."""
    label_desc = f" (label: {label})" if label else ""
    click.echo(f"\n=== Tareas Disponibles{label_desc} ===")
    tasks = get_available_tasks(label=label)
    if tasks:
        filas = []
        for t in tasks:
            numero = t.get("task_id") or t.get("PK", "").replace("TASK#", "")
            titulo = (t.get("title") or "")[:40]
            labels = t.get("labels", [])
            modelo, _ = select_model(labels)
            filas.append([numero, titulo, ", ".join(labels) or "-", modelo])
        click.echo(tabulate(
            filas,
            headers=["ISS#", "Titulo", "Labels", "Modelo rec."],
            tablefmt="plain",
        ))
    else:
        click.echo("  (no hay tareas disponibles)")


@click.command()
@click.option("--tenant", default=None, help="Tenant ID (auto-detect si no se da)")
@click.option("--workspace", default=None, help="Workspace (muestra todos si no se da)")
@click.option("--label", default=None, help="Filtrar tareas por label")
def main(
    tenant: str | None,
    workspace: str | None,
    label: str | None,
) -> None:
    """Dashboard de estado del swarm de nodos y tareas disponibles."""
    tenant_id = _resolve_tenant(tenant)
    if not tenant_id:
        click.echo(
            "No se pudo determinar tenant_id. "
            "Usa --tenant o configura ~/.covacha-node.yml",
            err=True,
        )
        return

    _mostrar_nodos(tenant_id, workspace)
    _mostrar_mensajes(tenant_id, workspace)
    _mostrar_tareas_bloqueadas(tenant_id, workspace)
    _mostrar_tareas(label)
    click.echo()


if __name__ == "__main__":
    main()
