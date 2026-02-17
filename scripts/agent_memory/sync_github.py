"""
Sincronización GitHub Project Board → DynamoDB.
Lee todos los items del board y actualiza/crea registros en DynamoDB.
"""
import time

import click

from config import REPO_BACKEND, REPO_FRONTEND, REPO_CROSS
from dynamo_client import get_dynamo_client, update_sync_status
from github_client import get_project_items, get_branch_for_issue, get_pr_for_issue
from model_selector import select_model

_STATUS_MAP: dict[str, str] = {"Todo": "todo", "In Progress": "in_progress", "Done": "done"}


def _infer_repo(labels: list[str]) -> str:
    """Infiere el repo a partir de los labels del issue."""
    low = [lbl.lower() for lbl in labels]
    if "backend" in low:
        return REPO_BACKEND
    if "frontend" in low:
        return REPO_FRONTEND
    return REPO_CROSS


def sync_github(dry_run: bool = False) -> dict:
    """
    Sincroniza el GitHub Project Board con DynamoDB.

    Lee todos los items del board, enriquece con branch/PR/modelo y
    hace upsert en la tabla DynamoDB bajo TASK#{number}|META.

    Returns:
        {"synced": int, "errors": list[str]}
    """
    items = get_project_items()
    table = get_dynamo_client()
    synced = 0
    errors: list[str] = []

    for item in items:
        issue_number = item.get("number")
        if issue_number is None:
            errors.append(f"Item sin numero: node_id={item.get('node_id')}")
            continue

        try:
            labels: list[str] = item.get("labels", [])
            repo = _infer_repo(labels)
            status = _STATUS_MAP.get(item.get("status") or "Todo", "todo")
            recommended_model, _ = select_model(labels)
            branch = get_branch_for_issue(issue_number, repo)
            pr = get_pr_for_issue(issue_number, repo)

            record: dict = {
                "PK": f"TASK#{issue_number}", "SK": "META",
                "number": issue_number,
                "title": item.get("title", ""),
                "labels": labels,
                "assignees": item.get("assignees", []),
                "github_node_id": item.get("node_id", ""),
                "status": status,
                "repo": repo,
                "branch": branch,
                "pr_number": pr.get("number") if pr else None,
                "pr_url": pr.get("url") if pr else None,
                "recommended_model": recommended_model,
                "updated_at": int(time.time()),
            }

            if not dry_run:
                table.put_item(Item=record)
            synced += 1

        except Exception as exc:  # noqa: BLE001
            errors.append(f"ISS-{issue_number}: {exc}")

    if not dry_run:
        update_sync_status(errors)

    prefix = "[dry-run] " if dry_run else ""
    print(f"{prefix}✓ Synced {synced} tasks ({len(errors)} errors)")
    for err in errors:
        print(f"  ERROR: {err}")

    return {"synced": synced, "errors": errors}


@click.command()
@click.option("--dry-run", is_flag=True, help="No escribe en DynamoDB")
def main(dry_run: bool) -> None:
    """Sincroniza el GitHub Project Board con la tabla DynamoDB."""
    sync_github(dry_run=dry_run)


if __name__ == "__main__":
    main()
