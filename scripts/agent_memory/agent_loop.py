"""Agent Loop — Daemon autonomo que corre en cada maquina del swarm.

Ciclo: heartbeat -> procesar mensajes -> buscar tarea -> claim ->
ejecutar Claude Code -> release + notificar. Repite hasta shutdown.
"""
import argparse
import logging
import os
import subprocess
import time
from typing import Any

from config import AGENT_LOOP_POLL_INTERVAL
from contract_registry import search_contracts
from dependency_manager import resolve_dependency
from dynamo_client import (
    claim_task,
    get_learnings,
    release_task,
    save_learning,
)
from message_bus import (
    get_recent_messages,
    get_unread_messages,
    mark_as_read,
    send_message,
)
from node_config import load_node_config
from node_registry import (
    deregister_node,
    heartbeat,
    register_node,
    update_node_status,
)
from prompt_generator import generate_implementation_prompt
from task_finder import find_next_across_workspaces, find_next_task

logger = logging.getLogger("agent_loop")


class AgentLoop:
    """Daemon autonomo que busca, reclama y ejecuta tareas."""

    def __init__(
        self,
        tenant_id: str,
        node_config: dict[str, Any],
        workspace_id: str | None = None,
    ) -> None:
        self.tenant_id = tenant_id
        self.node_config = node_config
        self.node_id: str = node_config.get("node_id", "unknown")
        self.workspace_id: str = (
            workspace_id
            or _first_workspace_id(node_config)
        )
        self.running: bool = True

    # ------------------------------------------------------------------
    # Ciclo principal
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Loop principal. Corre hasta que self.running=False o Ctrl+C."""
        register_node(self.tenant_id, self.node_config)
        logger.info("Nodo %s registrado en swarm", self.node_id)

        try:
            while self.running:
                self._iteration()
        except KeyboardInterrupt:
            self._shutdown()

    def _iteration(self) -> None:
        """Una iteracion del loop: heartbeat, mensajes, buscar y ejecutar."""
        heartbeat(self.tenant_id, self.node_id)
        self._process_messages()

        task = find_next_task(
            self.tenant_id, self.workspace_id, self.node_config
        )

        if not task:
            task = self._try_switch_workspace()

        if not task:
            logger.info(
                "No hay tareas. Esperando %ds...",
                AGENT_LOOP_POLL_INTERVAL,
            )
            time.sleep(AGENT_LOOP_POLL_INTERVAL)
            return

        self._execute_task(task)

    # ------------------------------------------------------------------
    # Ejecucion de tareas
    # ------------------------------------------------------------------

    def _execute_task(self, task: dict) -> None:
        """Reclama y ejecuta una tarea."""
        task_number = str(task.get("number", ""))
        claimed = claim_task(task_number, self.node_id, self.node_id)
        if not claimed:
            logger.warning(
                "Lock collision ISS-%s. Reintentando...", task_number
            )
            return

        update_node_status(
            self.tenant_id,
            self.node_id,
            "working",
            task_number,
            self.workspace_id,
        )
        logger.info(
            "Ejecutando ISS-%s: %s",
            task_number,
            task.get("title", ""),
        )

        result = self._run_claude_code(task)
        self._release_and_notify(task, result)

    def _run_claude_code(self, task: dict) -> dict[str, Any]:
        """Lanza Claude Code para implementar la tarea."""
        prompt = generate_implementation_prompt(
            task=task,
            node_config=self.node_config,
            contracts=self._get_relevant_contracts(),
            learnings=self._get_learnings(task),
            messages=self._get_recent_messages(),
            workspace_id=self.workspace_id,
        )

        repo_path = self._get_repo_path(task.get("repo", ""))
        model = task.get("recommended_model", "sonnet")

        try:
            result = subprocess.run(
                [
                    "claude", "--print", "--model", model,
                    "-p", prompt, "--max-turns", "50",
                ],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=3600,
            )
            return {
                "status": "done" if result.returncode == 0 else "blocked",
                "output": result.stdout[-2000:] if result.stdout else "",
                "error": result.stderr[-500:] if result.stderr else "",
                "learnings": extract_learnings(result.stdout),
            }
        except subprocess.TimeoutExpired:
            return _error_result("Timeout (1h)")
        except FileNotFoundError:
            return _error_result("Claude Code no instalado")

    # ------------------------------------------------------------------
    # Release y notificaciones
    # ------------------------------------------------------------------

    def _release_and_notify(self, task: dict, result: dict) -> None:
        """Libera tarea y notifica al swarm."""
        task_number = str(task.get("number", ""))
        release_task(task_number, result["status"])
        update_node_status(self.tenant_id, self.node_id, "idle")

        repo = task.get("repo", "unknown")
        for learning in result.get("learnings", []):
            save_learning(repo, learning, self.node_id)

        if result["status"] == "done":
            resolve_dependency(
                self.tenant_id, self.workspace_id, task_number
            )
            send_message(
                self.tenant_id, self.workspace_id,
                self.node_id, "task_completed", task_number,
            )
        else:
            send_message(
                self.tenant_id, self.workspace_id,
                self.node_id, "task_blocked", task_number,
                payload={"error": result.get("error", "")},
            )

    # ------------------------------------------------------------------
    # Mensajes
    # ------------------------------------------------------------------

    def _process_messages(self) -> None:
        """Lee y procesa mensajes pendientes."""
        messages = get_unread_messages(
            self.tenant_id, self.workspace_id, self.node_id
        )
        for msg in messages:
            logger.info(
                "MSG [%s] de %s: %s",
                msg.get("type"),
                msg.get("from_node"),
                msg.get("task_id", ""),
            )
            mark_as_read(
                self.tenant_id, self.workspace_id,
                msg["PK"], self.node_id,
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _try_switch_workspace(self) -> dict | None:
        """Intenta encontrar tarea en otro workspace si esta habilitado."""
        if not self.node_config.get("auto_switch_workspace"):
            return None
        result = find_next_across_workspaces(
            self.tenant_id, self.node_config
        )
        if result:
            self.workspace_id, task = result
            return task
        return None

    def _shutdown(self) -> None:
        """Shutdown graceful: desregistra el nodo."""
        logger.info("Apagando nodo %s...", self.node_id)
        update_node_status(self.tenant_id, self.node_id, "leaving")
        send_message(
            self.tenant_id, self.workspace_id,
            self.node_id, "node_left",
        )
        deregister_node(self.tenant_id, self.node_id)

    def _get_repo_path(self, repo_name: str) -> str:
        """Busca el path local del repo en node_config."""
        for ws in self.node_config.get("workspaces", []):
            for repo in ws.get("repos", []):
                if repo.get("name") == repo_name:
                    return repo["path"]
        return os.getcwd()

    def _get_relevant_contracts(self) -> list[dict]:
        """Obtiene contratos relevantes del workspace."""
        try:
            return search_contracts(self.tenant_id, self.workspace_id)
        except Exception:
            return []

    def _get_learnings(self, task: dict) -> dict:
        """Obtiene learnings del modulo de la tarea."""
        try:
            return get_learnings(task.get("repo", ""))
        except Exception:
            return {}

    def _get_recent_messages(self) -> list[dict]:
        """Obtiene mensajes recientes del workspace."""
        try:
            return get_recent_messages(
                self.tenant_id, self.workspace_id, limit=5
            )
        except Exception:
            return []


# ------------------------------------------------------------------
# Funciones de modulo
# ------------------------------------------------------------------

def extract_learnings(output: str) -> list[str]:
    """Extrae learnings del output de Claude Code.

    Busca lineas con prefijo Learning:, Learned:, Gotcha: o Aprendizaje:
    """
    learnings: list[str] = []
    if not output:
        return learnings
    prefixes = ("learning:", "learned:", "gotcha:", "aprendizaje:")
    for line in output.split("\n"):
        stripped = line.strip()
        lower = stripped.lower()
        for prefix in prefixes:
            if lower.startswith(prefix):
                value = stripped[len(prefix):].strip()
                if value:
                    learnings.append(value)
                break
    return learnings


def _first_workspace_id(node_config: dict) -> str:
    """Extrae el ID del primer workspace del config."""
    workspaces = node_config.get("workspaces", [])
    if workspaces:
        return workspaces[0].get("id", "default")
    return "default"


def _error_result(error_msg: str) -> dict[str, Any]:
    """Construye un resultado de error estandar."""
    return {"status": "blocked", "error": error_msg, "learnings": []}


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------

def main() -> None:
    """Entry point CLI para el Agent Loop."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Agent Loop - Daemon autonomo del swarm"
    )
    parser.add_argument("--tenant", help="Tenant ID")
    parser.add_argument("--workspace", help="Workspace ID")
    parser.add_argument(
        "--node-config", help="Path a .covacha-node.yml"
    )
    args = parser.parse_args()

    config = load_node_config(args.node_config) if args.node_config else load_node_config()
    tenant_id = args.tenant or config.get("tenant", {}).get(
        "id", "baatdigital"
    )
    workspace_id = args.workspace or _first_workspace_id(config)

    loop = AgentLoop(tenant_id, config, workspace_id)
    loop.run()


if __name__ == "__main__":
    main()
