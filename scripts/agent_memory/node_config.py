"""Configuracion local de nodo para el Agent Swarm.

Maneja el archivo ~/.covacha-node.yml que identifica a cada maquina
en el swarm. Soporta auto-deteccion de repos y capabilities.
"""
import os
import platform
import shutil
from pathlib import Path
from typing import Any

import yaml

from config import DEFAULT_BASE_PATH


def get_node_config_path() -> Path:
    """Retorna la ruta al archivo de configuracion del nodo (~/.covacha-node.yml)."""
    return Path.home() / ".covacha-node.yml"


def load_node_config() -> dict[str, Any]:
    """Lee y parsea el archivo YAML de configuracion del nodo.

    Retorna un diccionario vacio si el archivo no existe.
    """
    config_path = get_node_config_path()
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def save_node_config(config: dict[str, Any]) -> None:
    """Escribe la configuracion del nodo al archivo YAML."""
    config_path = get_node_config_path()
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)


def generate_node_id() -> str:
    """Genera un node_id unico basado en username y hostname.

    Formato: {username}-{hostname_limpio}
    Ejemplo: casp-cesars-macbook-pro
    """
    hostname = platform.node()
    username = os.getenv("USER", os.getenv("USERNAME", "unknown"))
    clean_host = hostname.split(".")[0].lower().replace(" ", "-")
    return f"{username}-{clean_host}"


def detect_local_repos(base_path: str | None = None) -> list[dict[str, str]]:
    """Detecta repositorios locales buscando directorios con .git.

    Escanea el directorio base (por defecto ~/sandboxes/superpago/)
    y retorna una lista de diccionarios con path y name de cada repo.
    """
    resolved_path = base_path or DEFAULT_BASE_PATH
    resolved_path = os.path.expanduser(resolved_path)
    base = Path(resolved_path)
    if not base.exists():
        return []
    repos: list[dict[str, str]] = []
    for child in sorted(base.iterdir()):
        if child.is_dir() and (child / ".git").exists():
            repos.append({
                "path": str(child),
                "name": child.name,
            })
    return repos


def detect_capabilities(repos: list[dict[str, str]]) -> list[str]:
    """Infiere capabilities del nodo a partir de los repos clonados.

    Reglas de inferencia:
    - covacha-* repos -> backend
    - mf-* repos -> frontend
    - covacha-projects -> ops
    - pytest disponible en PATH -> testing
    - ng disponible en PATH -> frontend
    """
    caps: set[str] = set()
    for repo in repos:
        name = repo["name"]
        if name.startswith("covacha-"):
            caps.add("backend")
        if name.startswith("mf-"):
            caps.add("frontend")
        if name == "covacha-projects":
            caps.add("ops")
    # Herramientas disponibles en el sistema
    if shutil.which("pytest"):
        caps.add("testing")
    if shutil.which("ng"):
        caps.add("frontend")
    return sorted(caps)


def init_node_config(
    tenant_id: str,
    github_org: str,
    base_path: str | None = None,
) -> dict[str, Any]:
    """Auto-genera la configuracion completa del nodo.

    Detecta repos locales, infiere capabilities, genera node_id
    y guarda el archivo ~/.covacha-node.yml.

    Retorna el config generado.
    """
    node_id = generate_node_id()
    repos = detect_local_repos(base_path)
    caps = detect_capabilities(repos)
    roles = ["developer"]

    config: dict[str, Any] = {
        "node_id": node_id,
        "tenant": {
            "id": tenant_id,
            "github_org": github_org,
        },
        "workspaces": [
            {
                "id": tenant_id,
                "repos": repos,
                "capabilities": caps,
                "roles": roles,
            },
        ],
        "preferred_model": "sonnet",
        "max_concurrent_tasks": 1,
        "auto_switch_workspace": True,
    }
    save_node_config(config)
    return config
