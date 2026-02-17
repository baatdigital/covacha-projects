"""
Cliente GitHub para operaciones con el Project Board de baatdigital.
GraphQL via requests (evita problema de '!' en gh api graphql).
Comandos simples (issue close, pr list) via gh CLI.
"""

import json
import subprocess
from typing import Any

import requests

from config import GITHUB_ORG, GITHUB_PROJECT_ID, GITHUB_STATUS_FIELD_ID

_GRAPHQL_URL = "https://api.github.com/graphql"

_ITEMS_QUERY = """
query($project: ID!, $cursor: String) {
  node(id: $project) {
    ... on ProjectV2 {
      items(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          fieldValues(first: 20) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field { ... on ProjectV2FieldCommon { id } }
              }
            }
          }
          content {
            ... on Issue {
              number title state
              labels(first: 10) { nodes { name } }
              assignees(first: 5) { nodes { login } }
            }
          }
        }
      }
    }
  }
}
"""

_MOVE_STATUS_MUTATION = """
mutation($project: ID!, $item: ID!, $field: ID!, $value: String!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $project
    itemId: $item
    fieldId: $field
    value: { singleSelectOptionId: $value }
  }) {
    projectV2Item { id }
  }
}
"""


def _gh_token() -> str:
    """Obtiene el token de GitHub del gh CLI autenticado."""
    result = subprocess.run(
        ["gh", "auth", "token"],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _graphql(query: str, variables: dict) -> dict:
    """
    Ejecuta una query/mutation GraphQL contra la API de GitHub.

    Args:
        query: Query o mutation GraphQL
        variables: Variables de la query

    Returns:
        Sección 'data' de la respuesta JSON
    """
    token = _gh_token()
    resp = requests.post(
        _GRAPHQL_URL,
        headers={"Authorization": f"Bearer {token}"},
        json={"query": query, "variables": variables},
        timeout=30,
    )
    resp.raise_for_status()
    body = resp.json()
    if "errors" in body:
        raise RuntimeError(f"Error GraphQL: {body['errors']}")
    return body.get("data", {})

_MOVE_STATUS_MUTATION = (
    "mutation($project:ID!,$item:ID!,$field:ID!,$value:String!){"
    "updateProjectV2ItemFieldValue(input:{projectId:$project itemId:$item "
    "fieldId:$field value:{singleSelectOptionId:$value}}){projectV2Item{id}}}"
)


def run_gh_command(args: list[str]) -> dict | str:
    """
    Ejecuta gh CLI para comandos simples (issue, pr, etc.).
    Para GraphQL usar _graphql() directamente.
    """
    result = subprocess.run(["gh"] + args, check=True, capture_output=True, text=True)
    output = result.stdout.strip()
    if not output:
        return {}
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return output


def _parse_item_node(node: dict) -> dict:
    """Normaliza un nodo de item del Project Board en un dict plano."""
    content = node.get("content") or {}
    labels = [lbl["name"] for lbl in content.get("labels", {}).get("nodes", [])]
    assignees = [a["login"] for a in content.get("assignees", {}).get("nodes", [])]
    status_name: str | None = None
    for fv in node.get("fieldValues", {}).get("nodes", []):
        if (fv.get("field") or {}).get("id") == GITHUB_STATUS_FIELD_ID and "name" in fv:
            status_name = fv["name"]
            break
    return {
        "node_id": node.get("id"),
        "number": content.get("number"),
        "title": content.get("title"),
        "state": content.get("state"),
        "labels": labels,
        "assignees": assignees,
        "status": status_name,
    }


def get_project_items(status_filter: str | None = None) -> list[dict]:
    """
    Lee todos los items del Project Board con paginación automática.

    Args:
        status_filter: Filtra por nombre de status ("Todo", "In Progress", "Done")

    Returns:
        Lista de dicts con node_id, number, title, state, labels, assignees, status
    """
    items: list[dict] = []
    cursor: str | None = None
    while True:
        variables: dict = {"project": GITHUB_PROJECT_ID, "cursor": cursor}
        data = _graphql(_ITEMS_QUERY, variables)
        node_data = data.get("node", {}).get("items", {})
        page_info = node_data.get("pageInfo", {})
        for node in node_data.get("nodes", []):
            if not node.get("content"):
                continue
            parsed = _parse_item_node(node)
            if status_filter is None or parsed["status"] == status_filter:
                items.append(parsed)
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
    return items


def move_issue_to_status(item_node_id: str, status_option_id: str) -> None:
    """
    Mueve un item del Project Board al status indicado via GraphQL mutation.

    Args:
        item_node_id: Node ID del item en el Project (no el número de issue)
        status_option_id: ID de la opción de status (STATUS_TODO/IN_PROGRESS/DONE)
    """
    _graphql(_MOVE_STATUS_MUTATION, {
        "project": GITHUB_PROJECT_ID,
        "item": item_node_id,
        "field": GITHUB_STATUS_FIELD_ID,
        "value": status_option_id,
    })


def close_issue(issue_number: int, repo: str) -> None:
    """Cierra el issue con razón 'completed' en baatdigital/{repo}."""
    run_gh_command([
        "issue", "close", str(issue_number),
        "-R", f"{GITHUB_ORG}/{repo}",
        "--reason", "completed",
    ])


def get_issue_details(issue_number: int, repo: str) -> dict:
    """
    Retorna detalles del issue: number, title, body, labels, state, milestone.

    Args:
        issue_number: Número del issue
        repo: Nombre del repo sin org (ej: "covacha-payment")
    """
    result = run_gh_command([
        "issue", "view", str(issue_number),
        "-R", f"{GITHUB_ORG}/{repo}",
        "--json", "number,title,body,labels,state,milestone",
    ])
    return result if isinstance(result, dict) else {}


def get_branch_for_issue(issue_number: int, repo: str) -> str | None:
    """
    Busca la primera rama feature/ISS-{issue_number}* en el repo.

    Returns:
        Nombre de la rama o None si no existe
    """
    result = run_gh_command([
        "api", f"repos/{GITHUB_ORG}/{repo}/branches",
        "--paginate",
        "--jq", f'.[].name | select(startswith("feature/ISS-{issue_number}"))',
    ])
    if isinstance(result, str) and result.strip():
        return result.strip().splitlines()[0]
    return None


def get_pr_for_issue(issue_number: int, repo: str) -> dict | None:
    """
    Busca el primer PR asociado al issue por número en título/branch.

    Returns:
        Dict con number, state, url o None si no hay PR
    """
    result = run_gh_command([
        "pr", "list",
        "-R", f"{GITHUB_ORG}/{repo}",
        "--search", f"ISS-{issue_number}",
        "--json", "number,state,url",
    ])
    if isinstance(result, list) and result:
        return result[0]
    return None
