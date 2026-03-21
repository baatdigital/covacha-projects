"""Auto-descubrimiento de workspaces desde GitHub Projects.

Usa gh CLI para listar projects de una organizacion, extraer campos
de status y repos asociados, y crear workspaces automaticamente.
"""
import json
import re
import subprocess
from typing import Any

from tenant_manager import create_workspace


def _run_gh(args: list[str]) -> dict[str, Any] | list[Any]:
    """Ejecuta un comando gh CLI y parsea la salida JSON.

    Lanza RuntimeError si el comando falla.
    """
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"gh CLI error (code {result.returncode}): {result.stderr.strip()}"
        )
    return json.loads(result.stdout)


def slugify(text: str) -> str:
    """Convierte un titulo a slug URL-safe.

    Ejemplo: 'Mi Proyecto 123' -> 'mi-proyecto-123'
    Solo alfanumerico y guiones, lowercase.
    """
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def _extract_status_options(
    fields: list[dict[str, Any]],
) -> tuple[str | None, dict[str, str]]:
    """Extrae field_id y opciones del campo Status de un project.

    Retorna (status_field_id, {option_name_lower: option_id}).
    """
    for field in fields:
        if field.get("name") == "Status":
            field_id = field.get("id")
            options: dict[str, str] = {}
            for opt in field.get("options", []):
                name = opt.get("name", "").lower().replace(" ", "_")
                options[name] = opt.get("id", "")
            return field_id, options
    return None, {}


def discover_workspaces(github_org: str) -> list[dict[str, Any]]:
    """Descubre workspaces disponibles leyendo GitHub Projects de la org.

    Usa gh api graphql para listar projects y sus campos.
    Retorna lista de dicts con id, name, github config y task_count.
    """
    # Listar projects de la org
    query = """
    query($org: String!) {
      organization(login: $org) {
        projectsV2(first: 20) {
          nodes {
            id
            title
            number
            items { totalCount }
          }
        }
      }
    }
    """
    data = _run_gh([
        "api", "graphql",
        "-f", f"query={query}",
        "-f", f"org={github_org}",
    ])

    projects = (
        data.get("data", {})
        .get("organization", {})
        .get("projectsV2", {})
        .get("nodes", [])
    )

    workspaces: list[dict[str, Any]] = []
    for project in projects:
        fields = _get_project_fields(project["id"])
        status_field_id, status_options = _extract_status_options(fields)

        ws: dict[str, Any] = {
            "id": slugify(project["title"]),
            "name": project["title"],
            "github": {
                "org": github_org,
                "project_number": project["number"],
                "project_id": project["id"],
                "status_field_id": status_field_id,
                "status_options": status_options,
            },
            "task_count": project.get("items", {}).get("totalCount", 0),
        }
        workspaces.append(ws)

    return workspaces


def _get_project_fields(project_id: str) -> list[dict[str, Any]]:
    """Obtiene los campos (fields) de un GitHub Project via GraphQL."""
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options { id name }
              }
              ... on ProjectV2Field {
                id
                name
              }
            }
          }
        }
      }
    }
    """
    data = _run_gh([
        "api", "graphql",
        "-f", f"query={query}",
        "-f", f"projectId={project_id}",
    ])

    return (
        data.get("data", {})
        .get("node", {})
        .get("fields", {})
        .get("nodes", [])
    )


def discover_repos_from_project(
    github_org: str, project_id: str
) -> list[str]:
    """Obtiene repos unicos de los issues de un GitHub Project.

    Retorna lista de 'org/repo' strings ordenada alfabeticamente.
    """
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              content {
                ... on Issue {
                  repository { nameWithOwner }
                }
                ... on PullRequest {
                  repository { nameWithOwner }
                }
              }
            }
          }
        }
      }
    }
    """
    data = _run_gh([
        "api", "graphql",
        "-f", f"query={query}",
        "-f", f"projectId={project_id}",
    ])

    items = (
        data.get("data", {})
        .get("node", {})
        .get("items", {})
        .get("nodes", [])
    )

    repos: set[str] = set()
    for item in items:
        content = item.get("content")
        if content and content.get("repository"):
            repos.add(content["repository"]["nameWithOwner"])

    return sorted(repos)


def auto_setup_workspaces(
    tenant_id: str,
    github_org: str,
    workspace_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Auto-descubre y crea workspaces desde GitHub Projects.

    1. Descubre workspaces disponibles en la org.
    2. Filtra por workspace_ids si se proporcionan.
    3. Descubre repos de cada project.
    4. Crea los workspaces en DynamoDB.

    Retorna lista de workspaces creados.
    """
    discovered = discover_workspaces(github_org)

    if workspace_ids:
        discovered = [
            ws for ws in discovered if ws["id"] in workspace_ids
        ]

    created: list[dict[str, Any]] = []
    for ws in discovered:
        gh = ws["github"]
        repos = discover_repos_from_project(github_org, gh["project_id"])
        workspace = create_workspace(
            tenant_id=tenant_id,
            workspace_id=ws["id"],
            workspace_name=ws["name"],
            github_project_id=gh["project_id"],
            github_project_number=gh["project_number"],
            status_field_id=gh.get("status_field_id", ""),
            status_options=gh.get("status_options", {}),
            repos=repos,
        )
        created.append(workspace)

    return created
