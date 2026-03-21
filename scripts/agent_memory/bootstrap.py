"""
Genera CONTEXT.md con contexto de sesion para un Agent Team.
Lee tareas disponibles, learnings y estado de equipos desde DynamoDB.

Soporta el nuevo sistema de nodos dinamicos (--node) con backward
compatibility para --team/--machine.
"""
import warnings
from datetime import datetime

import click

from dynamo_client import (
    get_available_tasks,
    get_learnings,
    update_team_status,
    get_all_team_statuses,
)
from model_selector import select_model

# Imports opcionales de nuevos modulos
try:
    from node_config import load_node_config
except ImportError:
    load_node_config = None  # type: ignore[assignment]

try:
    from node_registry import register_node, heartbeat, discover_nodes
except ImportError:
    register_node = None  # type: ignore[assignment]
    heartbeat = None  # type: ignore[assignment]
    discover_nodes = None  # type: ignore[assignment]

try:
    from message_bus import get_unread_messages
except ImportError:
    get_unread_messages = None  # type: ignore[assignment]

try:
    from contract_registry import search_contracts
except ImportError:
    search_contracts = None  # type: ignore[assignment]

try:
    from dependency_manager import is_task_unblocked, get_dependencies
except ImportError:
    is_task_unblocked = None  # type: ignore[assignment]
    get_dependencies = None  # type: ignore[assignment]


def _resolve_node_id(
    node: str | None,
    team: str | None,
    machine: str | None,
) -> tuple[str | None, str | None, dict]:
    """Resuelve node_id, tenant_id y node_config.

    Retorna (node_id, tenant_id, node_config_dict).
    """
    if node:
        cfg = _load_config_safe()
        tenant_id = cfg.get("tenant", {}).get("id")
        return node, tenant_id, cfg

    if load_node_config is not None:
        cfg = load_node_config()
        if cfg and cfg.get("node_id"):
            tenant_id = cfg.get("tenant", {}).get("id")
            return cfg["node_id"], tenant_id, cfg

    if team and machine:
        warnings.warn(
            "--team/--machine estan deprecados. Usa --node.",
            DeprecationWarning,
            stacklevel=2,
        )
        return f"{team}-{machine}", None, {}

    return None, None, {}


def _load_config_safe() -> dict:
    """Carga node_config de forma segura, retorna {} si falla."""
    if load_node_config is None:
        return {}
    try:
        return load_node_config()
    except Exception:
        return {}


def _team_table(statuses: list[dict]) -> str:
    """Genera tabla markdown de equipos activos (legacy)."""
    if not statuses:
        return "_No hay equipos activos registrados._"
    em = "\u2014"
    rows = ["| Equipo | Maquina | Tarea actual |", "| --- | --- | --- |"]
    rows += [
        f"| {s.get('team','?')} | {s.get('machine','?')} | {s.get('current_task') or em} |"
        for s in statuses
    ]
    return "\n".join(rows)


def _tasks_list(tasks: list[dict], limit: int = 5) -> str:
    """Genera lista markdown de tareas disponibles."""
    if not tasks:
        return "_Sin tareas disponibles para este equipo/maquina._"
    return "\n".join(
        f"- ISS-{t.get('number')}: {t.get('title','(sin titulo)')} "
        f"`[{', '.join(t.get('labels',[]))}]`"
        for t in tasks[:limit]
    )


def _learnings_section(learnings: dict) -> str:
    """Genera seccion markdown de learnings."""
    gotchas: list[str] = learnings.get("gotchas", [])
    if gotchas:
        return "\n".join(f"- {g}" for g in gotchas)
    return "_Sin learnings registrados aun._"


def _swarm_section(
    tenant_id: str | None,
) -> str:
    """Genera seccion de nodos del swarm usando node_registry."""
    if discover_nodes is None or not tenant_id:
        return "_Swarm no disponible (modulos no instalados)._"
    nodes = discover_nodes(tenant_id, only_active=True)
    if not nodes:
        return "_No hay nodos activos en el swarm._"
    rows = [
        "| Node | Status | Tarea | Capabilities |",
        "| --- | --- | --- | --- |",
    ]
    for n in nodes:
        caps = ", ".join(n.get("capabilities", []))
        task = n.get("current_task") or "---"
        rows.append(
            f"| {n.get('node_id','?')} | {n.get('status','?')} | {task} | {caps} |"
        )
    return "\n".join(rows)


def _messages_section(
    tenant_id: str | None,
    workspace: str | None,
    node_id: str | None,
) -> str:
    """Genera seccion de mensajes pendientes."""
    if get_unread_messages is None or not all([tenant_id, workspace, node_id]):
        return "_Sin mensajes pendientes._"
    msgs = get_unread_messages(tenant_id, workspace, node_id, limit=5)
    if not msgs:
        return "_Sin mensajes pendientes._"
    lines: list[str] = []
    for m in msgs:
        lines.append(
            f"- [{m.get('type','')}] task={m.get('task_id','')} "
            f"from={m.get('from_node','')}"
        )
    return "\n".join(lines)


def _contracts_section(
    tenant_id: str | None,
    workspace: str | None,
) -> str:
    """Genera seccion de contratos disponibles."""
    if search_contracts is None or not tenant_id or not workspace:
        return "_Sin contratos disponibles._"
    contracts = search_contracts(tenant_id, workspace)
    if not contracts:
        return "_Sin contratos disponibles._"
    lines: list[str] = []
    for c in contracts[:10]:
        lines.append(
            f"- {c.get('name','?')} v{c.get('version','?')} "
            f"[{c.get('method','')} {c.get('path','')}]"
        )
    return "\n".join(lines)


def _deps_section(
    tenant_id: str | None,
    workspace: str | None,
    tasks: list[dict],
) -> str:
    """Genera seccion de dependencias por tarea disponible."""
    if is_task_unblocked is None or not tenant_id or not workspace:
        return "_Dependencias no disponibles._"
    if not tasks:
        return "_Sin tareas para verificar dependencias._"
    lines: list[str] = []
    for t in tasks[:10]:
        tid = str(t.get("number", ""))
        if not tid:
            continue
        unblocked = is_task_unblocked(tenant_id, workspace, tid)
        estado = "desbloqueada" if unblocked else "BLOQUEADA"
        lines.append(f"- ISS-{tid}: {estado}")
    return "\n".join(lines) if lines else "_Sin dependencias._"


def _registrar_nodo_al_inicio(
    tenant_id: str | None,
    node_id: str | None,
    node_config: dict,
) -> None:
    """Registra el nodo y envia heartbeat al inicio del bootstrap."""
    if not tenant_id or not node_id:
        return
    if register_node is not None and node_config:
        # Preparar config para registro
        ws_list = node_config.get("workspaces", [])
        reg_config = {
            "node_id": node_id,
            "capabilities": ws_list[0].get("capabilities", []) if ws_list else [],
            "repos": ws_list[0].get("repos", []) if ws_list else [],
            "roles": ws_list[0].get("roles", ["developer"]) if ws_list else ["developer"],
        }
        register_node(tenant_id, reg_config)
    if heartbeat is not None:
        heartbeat(tenant_id, node_id)


def generate_context(
    team: str,
    machine: str,
    module: str | None,
    output: str,
    node_id: str | None = None,
    tenant_id: str | None = None,
    workspace: str | None = None,
    node_config: dict | None = None,
) -> None:
    """Lee el estado de DynamoDB y escribe el CONTEXT.md.

    Args:
        team: Nombre del equipo (backend/frontend)
        machine: Maquina desde la que corre el agente
        module: Modulo target para cargar learnings
        output: Path del archivo CONTEXT.md a generar
        node_id: ID del nodo en el swarm (opcional)
        tenant_id: ID del tenant (opcional)
        workspace: ID del workspace (opcional)
        node_config: Config del nodo para registro (opcional)
    """
    # Registrar nodo al inicio
    _registrar_nodo_al_inicio(tenant_id, node_id, node_config or {})

    tasks = get_available_tasks(label=team)
    learnings = get_learnings(module) if module else {}

    rec = tasks[0] if tasks else None
    rec_model, rec_just = select_model(rec.get("labels", []) if rec else [])
    rec_number = rec.get("number", "\u2014") if rec else "\u2014"
    rec_title = rec.get("title", "Sin tarea disponible") if rec else "Sin tarea disponible"
    rec_branch = (rec.get("branch") or "por crear") if rec else "\u2014"
    rec_labels_str = ", ".join(rec.get("labels", [])) if rec else "\u2014"

    ws = workspace or tenant_id

    # Generar secciones nuevas (swarm) o legacy (team table)
    if tenant_id and discover_nodes is not None:
        equipo_section = _swarm_section(tenant_id)
        equipo_title = "Swarm"
    else:
        team_statuses = get_all_team_statuses()
        equipo_section = _team_table(team_statuses)
        equipo_title = "Equipo activo"

    content = f"""## {module or team} \u2014 Contexto [{datetime.now().strftime("%Y-%m-%d")}]
<!-- Generado automaticamente por bootstrap.py. No editar manualmente. -->

### Modelo recomendado
- **{rec_model}** \u2014 {rec_just}

### Tarea recomendada
- ISS-{rec_number}: {rec_title}
- Branch: {rec_branch}
- Labels: {rec_labels_str}

### Learnings activos
{_learnings_section(learnings)}

### {equipo_title}
{equipo_section}

### Mensajes pendientes
{_messages_section(tenant_id, ws, node_id)}

### Contratos disponibles
{_contracts_section(tenant_id, ws)}

### Dependencias
{_deps_section(tenant_id, ws, tasks)}

### Tareas disponibles ({team}/{machine})
{_tasks_list(tasks)}
"""

    with open(output, "w", encoding="utf-8") as fh:
        fh.write(content)

    # Legacy: actualizar team status
    update_team_status(team, machine, current_task=None)
    print(f"CONTEXT.md generado en {output}")


@click.command()
@click.option("--team", default=None, help="[DEPRECATED] Nombre del equipo")
@click.option("--machine", default=None, help="[DEPRECATED] Maquina")
@click.option("--module", default=None, help="Modulo target (ej: covacha-payment)")
@click.option("--output", default="CONTEXT.md", help="Path del archivo generado")
@click.option("--node", default=None, help="Node ID del swarm")
@click.option("--tenant", default=None, help="Tenant ID")
@click.option("--workspace", default=None, help="Workspace ID")
def main(
    team: str | None,
    machine: str | None,
    module: str | None,
    output: str,
    node: str | None,
    tenant: str | None,
    workspace: str | None,
) -> None:
    """Genera CONTEXT.md con contexto de sesion para un Agent Team."""
    node_id, auto_tenant, node_cfg = _resolve_node_id(node, team, machine)
    tenant_id = tenant or auto_tenant

    # Defaults para backward compat
    effective_team = team or "unknown"
    effective_machine = machine or "auto"

    generate_context(
        team=effective_team,
        machine=effective_machine,
        module=module,
        output=output,
        node_id=node_id,
        tenant_id=tenant_id,
        workspace=workspace,
        node_config=node_cfg,
    )


if __name__ == "__main__":
    main()
