"""Migracion del schema viejo (TASK#, TEAM#) al nuevo (TENANT#|WS#|TASK#, NODE#).

Script para migrar datos existentes en covacha-agent-memory al formato
multi-tenant con aislamiento por tenant y workspace.
"""
import argparse
import json
import time
from typing import Any

from botocore.exceptions import ClientError

from dynamo_client import get_dynamo_client


def _full_table_scan(table: Any) -> list[dict[str, Any]]:
    """Scan completo de la tabla sin filtros."""
    response = table.scan()
    items: list[dict[str, Any]] = response.get("Items", [])
    while "LastEvaluatedKey" in response:
        response = table.scan(
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response.get("Items", []))
    return items


def _map_old_pk(
    old_pk: str, tenant_id: str, workspace_id: str
) -> str | None:
    """Mapea un PK del schema viejo al nuevo.

    Retorna None si el item debe ser saltado (TEAM# o ya migrado).
    """
    if old_pk.startswith("TENANT#"):
        return None  # Ya migrado

    if old_pk.startswith("TASK#"):
        return f"TENANT#{tenant_id}|WS#{workspace_id}|{old_pk}"

    if old_pk.startswith("LEARNING#"):
        return f"TENANT#{tenant_id}|WS#{workspace_id}|{old_pk}"

    if old_pk.startswith("SYNC#"):
        return f"TENANT#{tenant_id}|WS#{workspace_id}|{old_pk}"

    if old_pk.startswith("TEAM#"):
        return None  # Skip, ya tenemos NODE# en nuevo schema

    if old_pk.startswith("MSG#"):
        return f"TENANT#{tenant_id}|WS#{workspace_id}|{old_pk}"

    return None  # Desconocido, skip


def migrate_to_multi_tenant(
    tenant_id: str = "baatdigital",
    workspace_id: str = "superpago",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Migra datos existentes al schema multi-tenant.

    Para cada item existente, calcula el nuevo PK con prefijos
    TENANT#|WS# y escribe el item nuevo via batch_write.

    Si dry_run es True, solo cuenta items sin escribir.
    Retorna dict con contadores de migrated, skipped y errors.
    """
    table = get_dynamo_client()
    all_items = _full_table_scan(table)

    migrated = 0
    skipped = 0
    errors: list[str] = []

    items_to_write: list[dict[str, Any]] = []

    for item in all_items:
        old_pk = item.get("PK", "")
        new_pk = _map_old_pk(old_pk, tenant_id, workspace_id)

        if new_pk is None:
            skipped += 1
            continue

        new_item = {**item, "PK": new_pk}
        items_to_write.append(new_item)
        migrated += 1

    if not dry_run:
        _batch_write_items(table, items_to_write, errors)

    return {
        "migrated": migrated,
        "skipped": skipped,
        "errors": errors,
        "dry_run": dry_run,
    }


def _batch_write_items(
    table: Any,
    items: list[dict[str, Any]],
    errors: list[str],
) -> None:
    """Escribe items a DynamoDB uno por uno (put_item)."""
    for item in items:
        try:
            table.put_item(Item=item)
        except ClientError as exc:
            errors.append(
                f"Error escribiendo PK={item.get('PK')}: {exc}"
            )


def verify_migration(
    tenant_id: str, workspace_id: str
) -> dict[str, Any]:
    """Verifica el estado de la migracion.

    Cuenta items con prefijo TENANT#{t}|WS#{ws} (nuevo schema)
    y items sin prefijo TENANT# (viejo schema).
    Retorna dict con contadores y flag de completitud.
    """
    table = get_dynamo_client()
    all_items = _full_table_scan(table)

    prefix = f"TENANT#{tenant_id}|WS#{workspace_id}"
    new_schema_items = 0
    old_schema_items = 0

    for item in all_items:
        pk = item.get("PK", "")
        if pk.startswith(prefix):
            new_schema_items += 1
        elif not pk.startswith("TENANT#"):
            old_schema_items += 1

    return {
        "new_schema_items": new_schema_items,
        "old_schema_items": old_schema_items,
        "complete": new_schema_items >= old_schema_items,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Migracion a schema multi-tenant"
    )
    parser.add_argument("--tenant", default="baatdigital")
    parser.add_argument("--workspace", default="superpago")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.verify:
        result = verify_migration(args.tenant, args.workspace)
    else:
        result = migrate_to_multi_tenant(
            args.tenant, args.workspace, args.dry_run
        )
    print(json.dumps(result, indent=2))
