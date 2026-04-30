"""
Lambda PreTokenGeneration trigger para el User Pool 2 (Portal Clientes).

Cuando un usuario se autentica en Cognito Pool 2, este Lambda inyecta en el JWT
los `client_grants` del usuario leyendo `modIA_portal_grants_prod`. Esto permite
que el frontend mf-portal sepa a que clientes (POP, BAATDIGITAL, etc.) tiene
acceso el usuario sin hacer un round-trip extra.

Tambien actualiza `last_login_at` en `modIA_portal_users_prod`.

Cognito event spec:
https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-pre-token-generation.html

Tablas leidas:
- modIA_portal_users_prod (GSI cognito_sub-index para lookup por sub)
- modIA_portal_grants_prod (PK user_id)

Claims agregados al JWT:
- portal_user_id
- client_grants (JSON array de {client_id, role, allowed_phone_ids})
"""
import json
import logging
import os
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Key

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
USERS_TABLE = os.environ.get("PORTAL_USERS_TABLE", "modIA_portal_users_prod")
GRANTS_TABLE = os.environ.get("PORTAL_GRANTS_TABLE", "modIA_portal_grants_prod")


def lambda_handler(event, context):
    """
    Entry point del Lambda. Cognito invoca esto durante token generation.

    Args:
        event: Cognito event con userPoolId, userName, request.userAttributes, etc.
        context: Lambda context.

    Returns:
        Modified event con response.claimsOverrideDetails poblado.
    """
    logger.info("PreTokenGeneration event: %s", json.dumps({
        "trigger": event.get("triggerSource"),
        "userName": event.get("userName"),
    }))

    cognito_sub = event.get("request", {}).get("userAttributes", {}).get("sub")
    if not cognito_sub:
        logger.warning("No cognito sub in event, skipping claim injection")
        return event

    portal_user = _find_portal_user_by_cognito_sub(cognito_sub)
    if not portal_user:
        logger.info("No portal_user for cognito_sub=%s — skipping grants", cognito_sub)
        return event

    user_id = portal_user["id"]
    grants = _find_active_grants_by_user(user_id)

    # Update last_login_at silently (no fallar si tabla no responde)
    try:
        _update_last_login(user_id)
    except Exception as exc:
        logger.warning("Failed to update last_login_at: %s", exc)

    # Inyectar claims
    event.setdefault("response", {})
    event["response"]["claimsOverrideDetails"] = {
        "claimsToAddOrOverride": {
            "portal_user_id": user_id,
            "client_grants": json.dumps(grants),
        }
    }

    logger.info(
        "Injected %d grants for user_id=%s",
        len(grants),
        user_id,
    )
    return event


def _find_portal_user_by_cognito_sub(cognito_sub: str) -> dict | None:
    """Query GSI cognito_sub-index para encontrar el portal_user."""
    table = dynamodb.Table(USERS_TABLE)
    response = table.query(
        IndexName="cognito_sub-index",
        KeyConditionExpression=Key("cognito_sub").eq(cognito_sub),
        Limit=1,
    )
    items = response.get("Items", [])
    return items[0] if items else None


def _find_active_grants_by_user(user_id: str) -> list[dict]:
    """Lista grants activos (revoked_at is null) del usuario."""
    table = dynamodb.Table(GRANTS_TABLE)
    response = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
    )
    items = response.get("Items", [])
    grants = []
    for item in items:
        if item.get("revoked_at"):
            continue
        grants.append({
            "client_id": item["client_id"],
            "role": item.get("role", "operator"),
            "allowed_phone_ids": item.get("allowed_phone_ids", []),
        })
    return grants


def _update_last_login(user_id: str) -> None:
    """Actualiza last_login_at del portal_user."""
    table = dynamodb.Table(USERS_TABLE)
    now = datetime.now(timezone.utc).isoformat()
    table.update_item(
        Key={"id": user_id},
        UpdateExpression="SET last_login_at = :now, updated_at = :now",
        ExpressionAttributeValues={":now": now},
    )
