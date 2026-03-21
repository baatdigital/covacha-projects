"""
CLI unificado para el Agent Memory System.
Punto de entrada unico: python covacha_cli.py <subcommand>
"""

import argparse
import json
import sys

# Imports opcionales — cada subcommand verifica disponibilidad
try:
    from node_config import load_node_config, init_node_config
except ImportError:
    load_node_config = None  # type: ignore[assignment]
    init_node_config = None  # type: ignore[assignment]

try:
    from node_registry import deregister_node, update_node_status
except ImportError:
    deregister_node = None  # type: ignore[assignment]
    update_node_status = None  # type: ignore[assignment]

try:
    from message_bus import send_message, get_unread_messages
except ImportError:
    send_message = None  # type: ignore[assignment]
    get_unread_messages = None  # type: ignore[assignment]

try:
    from dependency_manager import (
        add_dependency,
        is_task_unblocked,
        get_dependencies,
    )
except ImportError:
    add_dependency = None  # type: ignore[assignment]
    is_task_unblocked = None  # type: ignore[assignment]
    get_dependencies = None  # type: ignore[assignment]

try:
    from contract_registry import publish_contract, search_contracts
except ImportError:
    publish_contract = None  # type: ignore[assignment]
    search_contracts = None  # type: ignore[assignment]


def _get_config() -> dict:
    """Carga la config del nodo o retorna dict vacio."""
    if load_node_config is None:
        return {}
    return load_node_config()


def _get_tenant(args: argparse.Namespace) -> str | None:
    """Resuelve tenant desde args o auto-detect."""
    if hasattr(args, "tenant") and args.tenant:
        return args.tenant
    cfg = _get_config()
    return cfg.get("tenant", {}).get("id")


def _get_workspace(args: argparse.Namespace) -> str | None:
    """Resuelve workspace desde args o default a tenant."""
    if hasattr(args, "workspace") and args.workspace:
        return args.workspace
    return _get_tenant(args)


def _get_node_id(args: argparse.Namespace) -> str | None:
    """Resuelve node_id desde args o auto-detect."""
    if hasattr(args, "node") and args.node:
        return args.node
    cfg = _get_config()
    return cfg.get("node_id")


# --- Subcommands ---


def cmd_init(args: argparse.Namespace) -> None:
    """Setup interactivo del nodo local."""
    if init_node_config is None:
        print("Error: modulo node_config no disponible.")
        sys.exit(1)

    tenant = args.tenant or input("Tenant ID [baatdigital]: ").strip() or "baatdigital"
    org = args.org or input("GitHub org [baatdigital]: ").strip() or "baatdigital"
    base = args.base_path or None

    config = init_node_config(tenant_id=tenant, github_org=org, base_path=base)
    print(f"Nodo configurado: {config['node_id']}")
    print(f"  Tenant: {config['tenant']['id']}")
    ws = config.get("workspaces", [{}])[0]
    print(f"  Capabilities: {', '.join(ws.get('capabilities', []))}")
    print(f"  Repos: {len(ws.get('repos', []))}")
    print(f"  Config guardada en ~/.covacha-node.yml")


def cmd_start(args: argparse.Namespace) -> None:
    """Placeholder para el Agent Loop."""
    print("Agent Loop not implemented yet")


def cmd_stop(args: argparse.Namespace) -> None:
    """Deregistra el nodo y libera tarea actual si hay."""
    tenant_id = _get_tenant(args)
    node_id = _get_node_id(args)

    if not tenant_id or not node_id:
        print("Error: no se pudo determinar tenant/node.")
        sys.exit(1)

    if deregister_node is not None:
        deregister_node(tenant_id, node_id)
        print(f"Nodo {node_id} desregistrado del tenant {tenant_id}")
    else:
        print("Error: modulo node_registry no disponible.")


def cmd_status(args: argparse.Namespace) -> None:
    """Muestra status del swarm (delega a swarm_status)."""
    from swarm_status import main as swarm_main
    # Simular args de click invocando directamente
    ctx_args = []
    tenant_id = _get_tenant(args)
    if tenant_id:
        ctx_args.extend(["--tenant", tenant_id])
    ws = _get_workspace(args)
    if ws and ws != tenant_id:
        ctx_args.extend(["--workspace", ws])
    swarm_main(ctx_args, standalone_mode=False)


def cmd_claim(args: argparse.Namespace) -> None:
    """Reclama una tarea (delega a claim_task)."""
    from claim_task import main as claim_main
    ctx_args = ["--task", args.task_id]
    node_id = _get_node_id(args)
    if node_id:
        ctx_args.extend(["--node", node_id])
    tenant_id = _get_tenant(args)
    if tenant_id:
        ctx_args.extend(["--tenant", tenant_id])
    ws = _get_workspace(args)
    if ws:
        ctx_args.extend(["--workspace", ws])
    claim_main(ctx_args, standalone_mode=False)


def cmd_release(args: argparse.Namespace) -> None:
    """Libera una tarea (delega a release_task)."""
    from release_task import main as release_main
    ctx_args = ["--task", args.task_id, "--status", args.status]
    node_id = _get_node_id(args)
    if node_id:
        ctx_args.extend(["--node", node_id])
    tenant_id = _get_tenant(args)
    if tenant_id:
        ctx_args.extend(["--tenant", tenant_id])
    ws = _get_workspace(args)
    if ws:
        ctx_args.extend(["--workspace", ws])
    release_main(ctx_args, standalone_mode=False)


def cmd_msg_send(args: argparse.Namespace) -> None:
    """Envia un mensaje al bus inter-nodo."""
    if send_message is None:
        print("Error: modulo message_bus no disponible.")
        sys.exit(1)
    tenant_id = _get_tenant(args)
    ws = _get_workspace(args)
    node_id = _get_node_id(args)
    if not all([tenant_id, ws, node_id]):
        print("Error: tenant, workspace y node son requeridos.")
        sys.exit(1)
    msg_id = send_message(
        tenant_id, ws, node_id,
        msg_type=args.type,
        task_id=args.task,
        to_node=getattr(args, "to", None),
    )
    print(f"Mensaje enviado: {msg_id}")


def cmd_msg_read(args: argparse.Namespace) -> None:
    """Lee mensajes no leidos para este nodo."""
    if get_unread_messages is None:
        print("Error: modulo message_bus no disponible.")
        sys.exit(1)
    tenant_id = _get_tenant(args)
    ws = _get_workspace(args)
    node_id = _get_node_id(args)
    if not all([tenant_id, ws, node_id]):
        print("Error: tenant, workspace y node son requeridos.")
        sys.exit(1)
    msgs = get_unread_messages(tenant_id, ws, node_id)
    if not msgs:
        print("Sin mensajes no leidos.")
        return
    for m in msgs:
        print(f"  [{m.get('type','')}] task={m.get('task_id','')} from={m.get('from_node','')}")


def cmd_deps_add(args: argparse.Namespace) -> None:
    """Agrega una dependencia entre tareas."""
    if add_dependency is None:
        print("Error: modulo dependency_manager no disponible.")
        sys.exit(1)
    tenant_id = _get_tenant(args)
    ws = _get_workspace(args)
    if not tenant_id or not ws:
        print("Error: tenant y workspace son requeridos.")
        sys.exit(1)
    add_dependency(tenant_id, ws, args.task, args.depends_on)
    print(f"Dependencia creada: ISS-{args.task} depende de ISS-{args.depends_on}")


def cmd_deps_check(args: argparse.Namespace) -> None:
    """Verifica si una tarea esta desbloqueada."""
    if is_task_unblocked is None or get_dependencies is None:
        print("Error: modulo dependency_manager no disponible.")
        sys.exit(1)
    tenant_id = _get_tenant(args)
    ws = _get_workspace(args)
    if not tenant_id or not ws:
        print("Error: tenant y workspace son requeridos.")
        sys.exit(1)
    deps = get_dependencies(tenant_id, ws, args.task)
    unblocked = is_task_unblocked(tenant_id, ws, args.task)
    print(f"ISS-{args.task}: {'DESBLOQUEADA' if unblocked else 'BLOQUEADA'}")
    if deps:
        for d in deps:
            status = d.get("blocker_status", "?")
            print(f"  depende de ISS-{d.get('blocker_task','?')} ({status})")


def cmd_contract_publish(args: argparse.Namespace) -> None:
    """Publica un contrato de API."""
    if publish_contract is None:
        print("Error: modulo contract_registry no disponible.")
        sys.exit(1)
    tenant_id = _get_tenant(args)
    ws = _get_workspace(args)
    node_id = _get_node_id(args)
    if not all([tenant_id, ws, node_id]):
        print("Error: tenant, workspace y node son requeridos.")
        sys.exit(1)
    req_schema = json.loads(args.request_schema) if args.request_schema else {}
    res_schema = json.loads(args.response_schema) if args.response_schema else {}
    cid = publish_contract(
        tenant_id, ws, args.name, args.version or "1.0",
        args.method, args.path,
        req_schema, res_schema,
        published_by=node_id,
    )
    print(f"Contrato publicado: {cid}")


def cmd_contract_search(args: argparse.Namespace) -> None:
    """Busca contratos de API."""
    if search_contracts is None:
        print("Error: modulo contract_registry no disponible.")
        sys.exit(1)
    tenant_id = _get_tenant(args)
    ws = _get_workspace(args)
    if not tenant_id or not ws:
        print("Error: tenant y workspace son requeridos.")
        sys.exit(1)
    results = search_contracts(
        tenant_id, ws,
        path_pattern=args.path,
        method=args.method,
    )
    if not results:
        print("Sin contratos encontrados.")
        return
    for c in results:
        print(
            f"  {c.get('name','?')} v{c.get('version','?')} "
            f"[{c.get('method','')} {c.get('path','')}]"
        )


def cmd_eval(args: argparse.Namespace) -> None:
    """Placeholder para evaluacion de tareas."""
    print(f"Eval not implemented yet (task={args.task}, type={args.type})")


def build_parser() -> argparse.ArgumentParser:
    """Construye el parser principal con todos los subcommands."""
    parser = argparse.ArgumentParser(
        prog="covacha",
        description="CLI unificado para el Agent Memory System",
    )
    parser.add_argument("--tenant", default=None, help="Tenant ID")
    parser.add_argument("--workspace", default=None, help="Workspace ID")
    parser.add_argument("--node", default=None, help="Node ID")

    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Setup interactivo del nodo")
    p_init.add_argument("--org", default=None)
    p_init.add_argument("--base-path", default=None)

    # start
    sub.add_parser("start", help="Inicia el Agent Loop (placeholder)")

    # stop
    sub.add_parser("stop", help="Deregistra el nodo")

    # status
    sub.add_parser("status", help="Muestra estado del swarm")

    # claim
    p_claim = sub.add_parser("claim", help="Reclama una tarea")
    p_claim.add_argument("task_id", help="ID de la tarea")

    # release
    p_release = sub.add_parser("release", help="Libera una tarea")
    p_release.add_argument("task_id", help="ID de la tarea")
    p_release.add_argument("--status", default="done", choices=["done", "blocked", "cancelled"])

    # msg
    p_msg = sub.add_parser("msg", help="Mensajes inter-nodo")
    msg_sub = p_msg.add_subparsers(dest="msg_command")

    p_msg_send = msg_sub.add_parser("send", help="Enviar mensaje")
    p_msg_send.add_argument("--type", required=True, help="Tipo de mensaje")
    p_msg_send.add_argument("--task", default=None, help="Task ID asociado")
    p_msg_send.add_argument("--to", default=None, help="Node destino (broadcast si no)")

    msg_sub.add_parser("read", help="Leer mensajes no leidos")

    # deps
    p_deps = sub.add_parser("deps", help="Dependencias entre tareas")
    deps_sub = p_deps.add_subparsers(dest="deps_command")

    p_deps_add = deps_sub.add_parser("add", help="Agregar dependencia")
    p_deps_add.add_argument("--task", required=True, help="Tarea bloqueada")
    p_deps_add.add_argument("--depends-on", required=True, help="Tarea bloqueadora")

    p_deps_check = deps_sub.add_parser("check", help="Verificar dependencias")
    p_deps_check.add_argument("--task", required=True, help="Tarea a verificar")

    # contract
    p_contract = sub.add_parser("contract", help="Contratos de API")
    contract_sub = p_contract.add_subparsers(dest="contract_command")

    p_pub = contract_sub.add_parser("publish", help="Publicar contrato")
    p_pub.add_argument("--name", required=True, help="Nombre del contrato")
    p_pub.add_argument("--method", default="GET", help="HTTP method")
    p_pub.add_argument("--path", required=True, help="API path")
    p_pub.add_argument("--version", default="1.0", help="Version")
    p_pub.add_argument("--request-schema", default=None, help="JSON schema request")
    p_pub.add_argument("--response-schema", default=None, help="JSON schema response")

    p_search = contract_sub.add_parser("search", help="Buscar contratos")
    p_search.add_argument("--path", default=None, help="Filtro por path")
    p_search.add_argument("--method", default=None, help="Filtro por method")

    # eval
    p_eval = sub.add_parser("eval", help="Evaluacion de tareas (placeholder)")
    p_eval.add_argument("--task", required=True, help="Task ID")
    p_eval.add_argument("--type", default="pre_release", help="Tipo de evaluacion")

    return parser


def run_cli(argv: list[str] | None = None) -> None:
    """Ejecuta el CLI con los argumentos dados o sys.argv."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return

    dispatch: dict = {
        "init": cmd_init,
        "start": cmd_start,
        "stop": cmd_stop,
        "status": cmd_status,
        "claim": cmd_claim,
        "release": cmd_release,
        "eval": cmd_eval,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    elif args.command == "msg":
        _dispatch_msg(args)
    elif args.command == "deps":
        _dispatch_deps(args)
    elif args.command == "contract":
        _dispatch_contract(args)
    else:
        parser.print_help()


def _dispatch_msg(args: argparse.Namespace) -> None:
    """Dispatch para subcomandos de msg."""
    if args.msg_command == "send":
        cmd_msg_send(args)
    elif args.msg_command == "read":
        cmd_msg_read(args)
    else:
        print("Usa: covacha msg {send|read}")


def _dispatch_deps(args: argparse.Namespace) -> None:
    """Dispatch para subcomandos de deps."""
    if args.deps_command == "add":
        cmd_deps_add(args)
    elif args.deps_command == "check":
        cmd_deps_check(args)
    else:
        print("Usa: covacha deps {add|check}")


def _dispatch_contract(args: argparse.Namespace) -> None:
    """Dispatch para subcomandos de contract."""
    if args.contract_command == "publish":
        cmd_contract_publish(args)
    elif args.contract_command == "search":
        cmd_contract_search(args)
    else:
        print("Usa: covacha contract {publish|search}")


if __name__ == "__main__":
    run_cli()
