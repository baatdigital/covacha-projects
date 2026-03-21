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

try:
    from tenant_manager import (
        create_tenant as tm_create_tenant,
        get_tenant as tm_get_tenant,
        list_tenants as tm_list_tenants,
        delete_tenant as tm_delete_tenant,
        create_workspace as tm_create_workspace,
        list_workspaces as tm_list_workspaces,
        delete_workspace as tm_delete_workspace,
    )
except ImportError:
    tm_create_tenant = None  # type: ignore[assignment]
    tm_get_tenant = None  # type: ignore[assignment]
    tm_list_tenants = None  # type: ignore[assignment]
    tm_delete_tenant = None  # type: ignore[assignment]
    tm_create_workspace = None  # type: ignore[assignment]
    tm_list_workspaces = None  # type: ignore[assignment]
    tm_delete_workspace = None  # type: ignore[assignment]

try:
    from workspace_discovery import auto_setup_workspaces
except ImportError:
    auto_setup_workspaces = None  # type: ignore[assignment]

try:
    from migration import migrate_to_multi_tenant, verify_migration
except ImportError:
    migrate_to_multi_tenant = None  # type: ignore[assignment]
    verify_migration = None  # type: ignore[assignment]


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


# --- Tenant subcommands ---


def cmd_tenant_create(args: argparse.Namespace) -> None:
    """Crea un tenant nuevo."""
    if tm_create_tenant is None:
        print("Error: modulo tenant_manager no disponible.")
        sys.exit(1)
    try:
        result = tm_create_tenant(
            args.name, args.github_org, args.admin_email,
            plan=args.plan,
        )
        print(f"Tenant '{args.name}' creado (plan: {args.plan})")
        print(f"  Max nodos: {result['max_nodes']}")
        print(f"  Max workspaces: {result['max_workspaces']}")
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def cmd_tenant_list(args: argparse.Namespace) -> None:
    """Lista todos los tenants."""
    if tm_list_tenants is None:
        print("Error: modulo tenant_manager no disponible.")
        sys.exit(1)
    tenants = tm_list_tenants()
    if not tenants:
        print("Sin tenants registrados.")
        return
    for t in tenants:
        name = t.get("org_name", "?")
        plan = t.get("plan", "?")
        print(f"  {name} (plan: {plan}, org: {t.get('github_org', '?')})")


def cmd_tenant_info(args: argparse.Namespace) -> None:
    """Muestra informacion de un tenant."""
    if tm_get_tenant is None:
        print("Error: modulo tenant_manager no disponible.")
        sys.exit(1)
    tenant = tm_get_tenant(args.tenant)
    if not tenant:
        print(f"Tenant '{args.tenant}' no encontrado.")
        sys.exit(1)
    print(json.dumps(tenant, indent=2, default=str))


def cmd_tenant_delete(args: argparse.Namespace) -> None:
    """Elimina un tenant."""
    if tm_delete_tenant is None:
        print("Error: modulo tenant_manager no disponible.")
        sys.exit(1)
    try:
        tm_delete_tenant(args.tenant)
        print(f"Tenant '{args.tenant}' eliminado.")
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


# --- Workspace subcommands ---


def cmd_workspace_create(args: argparse.Namespace) -> None:
    """Crea un workspace dentro de un tenant."""
    if tm_create_workspace is None:
        print("Error: modulo tenant_manager no disponible.")
        sys.exit(1)
    repos = args.repos.split(",") if args.repos else []
    try:
        result = tm_create_workspace(
            tenant_id=args.tenant,
            workspace_id=args.name.lower().replace(" ", "-"),
            workspace_name=args.name,
            github_project_id=f"project-{args.github_project}",
            github_project_number=int(args.github_project),
            status_field_id="",
            status_options={},
            repos=repos,
        )
        print(f"Workspace '{args.name}' creado en tenant '{args.tenant}'")
        print(f"  Repos: {', '.join(repos) if repos else '(ninguno)'}")
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def cmd_workspace_list(args: argparse.Namespace) -> None:
    """Lista workspaces de un tenant."""
    if tm_list_workspaces is None:
        print("Error: modulo tenant_manager no disponible.")
        sys.exit(1)
    tenant_id = _get_tenant(args)
    if not tenant_id:
        print("Error: se requiere --tenant.")
        sys.exit(1)
    workspaces = tm_list_workspaces(tenant_id)
    if not workspaces:
        print(f"Sin workspaces en tenant '{tenant_id}'.")
        return
    for ws in workspaces:
        name = ws.get("workspace_name", ws.get("workspace_id", "?"))
        active = "activo" if ws.get("active") else "inactivo"
        print(f"  {name} ({active}, repos: {len(ws.get('repos', []))})")


def cmd_workspace_discover(args: argparse.Namespace) -> None:
    """Auto-descubre workspaces desde GitHub Projects."""
    if auto_setup_workspaces is None:
        print("Error: modulo workspace_discovery no disponible.")
        sys.exit(1)
    tenant_id = _get_tenant(args)
    if not tenant_id:
        print("Error: se requiere --tenant.")
        sys.exit(1)
    cfg = _get_config()
    github_org = cfg.get("tenant", {}).get("github_org", tenant_id)
    try:
        created = auto_setup_workspaces(tenant_id, github_org)
        print(f"{len(created)} workspace(s) creados desde GitHub.")
        for ws in created:
            print(f"  {ws.get('workspace_id', '?')}")
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def cmd_workspace_delete(args: argparse.Namespace) -> None:
    """Elimina un workspace."""
    if tm_delete_workspace is None:
        print("Error: modulo tenant_manager no disponible.")
        sys.exit(1)
    try:
        tm_delete_workspace(args.tenant, args.workspace)
        print(f"Workspace '{args.workspace}' eliminado de '{args.tenant}'.")
    except RuntimeError as exc:
        print(f"Error: {exc}")
        sys.exit(1)


def cmd_workspace_sync(args: argparse.Namespace) -> None:
    """Placeholder para sync de workspace con GitHub."""
    tenant_id = _get_tenant(args)
    ws = _get_workspace(args)
    print(f"Sync not implemented yet (tenant={tenant_id}, workspace={ws})")


# --- Migrate subcommand ---


def cmd_migrate(args: argparse.Namespace) -> None:
    """Ejecuta o verifica la migracion a multi-tenant."""
    if args.verify:
        if verify_migration is None:
            print("Error: modulo migration no disponible.")
            sys.exit(1)
        result = verify_migration(args.tenant, args.workspace)
    else:
        if migrate_to_multi_tenant is None:
            print("Error: modulo migration no disponible.")
            sys.exit(1)
        result = migrate_to_multi_tenant(
            args.tenant, args.workspace, args.dry_run,
        )
    print(json.dumps(result, indent=2, default=str))


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

    # tenant
    p_tenant = sub.add_parser("tenant", help="Gestion de tenants")
    tenant_sub = p_tenant.add_subparsers(dest="tenant_command")

    p_tc = tenant_sub.add_parser("create", help="Crear tenant")
    p_tc.add_argument("--name", required=True, help="Tenant ID/nombre")
    p_tc.add_argument("--github-org", required=True, help="GitHub org")
    p_tc.add_argument("--admin-email", required=True, help="Email admin")
    p_tc.add_argument("--plan", default="team", help="Plan (free/team/business/enterprise)")

    tenant_sub.add_parser("list", help="Listar tenants")

    p_ti = tenant_sub.add_parser("info", help="Info de un tenant")
    p_ti.add_argument("--tenant", required=True, help="Tenant ID")

    p_td = tenant_sub.add_parser("delete", help="Eliminar tenant")
    p_td.add_argument("--tenant", required=True, help="Tenant ID")

    # workspace
    p_ws = sub.add_parser("workspace", help="Gestion de workspaces")
    ws_sub = p_ws.add_subparsers(dest="workspace_command")

    p_wc = ws_sub.add_parser("create", help="Crear workspace")
    p_wc.add_argument("--tenant", required=True, help="Tenant ID")
    p_wc.add_argument("--name", required=True, help="Nombre del workspace")
    p_wc.add_argument("--github-project", required=True, help="GitHub Project number")
    p_wc.add_argument("--repos", default=None, help="Repos (comma-separated)")

    p_wl = ws_sub.add_parser("list", help="Listar workspaces")

    p_wd = ws_sub.add_parser("discover", help="Auto-descubrir desde GitHub")

    p_wdel = ws_sub.add_parser("delete", help="Eliminar workspace")
    p_wdel.add_argument("--tenant", required=True, help="Tenant ID")
    p_wdel.add_argument("--workspace", required=True, help="Workspace ID")

    p_wsync = ws_sub.add_parser("sync", help="Sync con GitHub")

    # migrate
    p_mig = sub.add_parser("migrate", help="Migracion a multi-tenant")
    p_mig.add_argument("--tenant", default="baatdigital", help="Tenant ID destino")
    p_mig.add_argument("--workspace", default="superpago", help="Workspace ID destino")
    p_mig.add_argument("--dry-run", action="store_true", help="Solo contar, no migrar")
    p_mig.add_argument("--verify", action="store_true", help="Verificar estado de migracion")

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
    elif args.command == "tenant":
        _dispatch_tenant(args)
    elif args.command == "workspace":
        _dispatch_workspace(args)
    elif args.command == "migrate":
        cmd_migrate(args)
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


def _dispatch_tenant(args: argparse.Namespace) -> None:
    """Dispatch para subcomandos de tenant."""
    cmd = getattr(args, "tenant_command", None)
    if cmd == "create":
        cmd_tenant_create(args)
    elif cmd == "list":
        cmd_tenant_list(args)
    elif cmd == "info":
        cmd_tenant_info(args)
    elif cmd == "delete":
        cmd_tenant_delete(args)
    else:
        print("Usa: covacha tenant {create|list|info|delete}")


def _dispatch_workspace(args: argparse.Namespace) -> None:
    """Dispatch para subcomandos de workspace."""
    cmd = getattr(args, "workspace_command", None)
    if cmd == "create":
        cmd_workspace_create(args)
    elif cmd == "list":
        cmd_workspace_list(args)
    elif cmd == "discover":
        cmd_workspace_discover(args)
    elif cmd == "delete":
        cmd_workspace_delete(args)
    elif cmd == "sync":
        cmd_workspace_sync(args)
    else:
        print("Usa: covacha workspace {create|list|discover|delete|sync}")


if __name__ == "__main__":
    run_cli()
