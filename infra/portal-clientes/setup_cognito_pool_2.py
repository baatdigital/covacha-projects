"""
Script idempotente para crear/actualizar la infraestructura del Portal Clientes:

1. Cognito User Pool 2: `superpago-client-portal-users` con username=phone
2. Cognito User Pool Client: para el SDK del frontend (mf-portal)
3. IAM Role para el Lambda PreTokenGeneration
4. Lambda function `superpago-portal-pre-token-generation`
5. Permission para que Cognito invoque el Lambda
6. Trigger PreTokenGeneration apuntando al Lambda

Salida (a stdout): JSON con los IDs/ARNs creados, util para configurar:
- Backend covacha-core (env vars COGNITO_PORTAL_POOL_ID, COGNITO_PORTAL_CLIENT_ID)
- Frontend mf-portal (Cognito client_id, identity pool si aplica)

Uso:
    python setup_cognito_pool_2.py [--region us-east-1] [--dry-run]
"""
import argparse
import json
import os
import sys
import zipfile
from io import BytesIO
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

POOL_NAME = "superpago-client-portal-users"
CLIENT_NAME = "superpago-portal-frontend"
LAMBDA_NAME = "superpago-portal-pre-token-generation"
ROLE_NAME = "superpago-portal-lambda-role"
LAMBDA_FILE = Path(__file__).parent / "lambda_pre_token_generation.py"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        print("DRY RUN — no se crean recursos")
        return

    region = args.region
    cognito = boto3.client("cognito-idp", region_name=region)
    iam = boto3.client("iam", region_name=region)
    lambda_client = boto3.client("lambda", region_name=region)
    sts = boto3.client("sts", region_name=region)

    account_id = sts.get_caller_identity()["Account"]
    print(f"AWS Account: {account_id}, Region: {region}")

    # ========================================================================
    # 1. User Pool 2
    # ========================================================================
    pool_id = _ensure_user_pool(cognito)
    print(f"User Pool ID: {pool_id}")

    # ========================================================================
    # 2. App Client
    # ========================================================================
    client_id = _ensure_user_pool_client(cognito, pool_id)
    print(f"User Pool Client ID: {client_id}")

    # ========================================================================
    # 3. IAM Role para Lambda
    # ========================================================================
    role_arn = _ensure_lambda_role(iam, account_id)
    print(f"Lambda Role ARN: {role_arn}")

    # ========================================================================
    # 4. Lambda function
    # ========================================================================
    lambda_arn = _ensure_lambda(lambda_client, role_arn)
    print(f"Lambda ARN: {lambda_arn}")

    # ========================================================================
    # 5. Permission para Cognito → Lambda
    # ========================================================================
    _ensure_lambda_invoke_permission(lambda_client, pool_id, account_id)

    # ========================================================================
    # 6. Trigger PreTokenGeneration
    # ========================================================================
    _ensure_pre_token_trigger(cognito, pool_id, lambda_arn)
    print("PreTokenGeneration trigger configured")

    # ========================================================================
    # Resumen
    # ========================================================================
    print("\n" + "=" * 60)
    print("SETUP COMPLETO. Configura estas vars en covacha-core:")
    print("=" * 60)
    summary = {
        "COGNITO_PORTAL_POOL_ID": pool_id,
        "COGNITO_PORTAL_CLIENT_ID": client_id,
        "COGNITO_PORTAL_REGION": region,
        "LAMBDA_PRE_TOKEN_ARN": lambda_arn,
    }
    print(json.dumps(summary, indent=2))


def _ensure_user_pool(cognito) -> str:
    """Crea el pool si no existe, devuelve el id."""
    pools = cognito.list_user_pools(MaxResults=60).get("UserPools", [])
    for p in pools:
        if p["Name"] == POOL_NAME:
            return p["Id"]

    response = cognito.create_user_pool(
        PoolName=POOL_NAME,
        Policies={
            "PasswordPolicy": {
                "MinimumLength": 10,
                "RequireUppercase": True,
                "RequireLowercase": True,
                "RequireNumbers": True,
                "RequireSymbols": False,
                "TemporaryPasswordValidityDays": 1,
            }
        },
        UsernameAttributes=["phone_number"],
        MfaConfiguration="OFF",
        AccountRecoverySetting={
            "RecoveryMechanisms": [
                {"Priority": 1, "Name": "admin_only"},
            ]
        },
        UserPoolTags={
            "Project": "SuperPago",
            "Module": "PortalClientes",
            "Environment": "prod",
        },
    )
    return response["UserPool"]["Id"]


def _ensure_user_pool_client(cognito, pool_id: str) -> str:
    """Crea el app client si no existe."""
    clients = cognito.list_user_pool_clients(UserPoolId=pool_id, MaxResults=60).get(
        "UserPoolClients", []
    )
    for c in clients:
        if c["ClientName"] == CLIENT_NAME:
            return c["ClientId"]

    response = cognito.create_user_pool_client(
        UserPoolId=pool_id,
        ClientName=CLIENT_NAME,
        GenerateSecret=False,  # SPA — no secret
        ExplicitAuthFlows=[
            "ALLOW_USER_PASSWORD_AUTH",
            "ALLOW_REFRESH_TOKEN_AUTH",
            "ALLOW_USER_SRP_AUTH",
        ],
        TokenValidityUnits={
            "AccessToken": "hours",
            "IdToken": "hours",
            "RefreshToken": "days",
        },
        AccessTokenValidity=1,
        IdTokenValidity=1,
        RefreshTokenValidity=30,
        PreventUserExistenceErrors="ENABLED",
        EnableTokenRevocation=True,
    )
    return response["UserPoolClient"]["ClientId"]


def _ensure_lambda_role(iam, account_id: str) -> str:
    """Crea IAM role con basic execution + DynamoDB read/update."""
    try:
        existing = iam.get_role(RoleName=ROLE_NAME)
        return existing["Role"]["Arn"]
    except iam.exceptions.NoSuchEntityException:
        pass

    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    iam.create_role(
        RoleName=ROLE_NAME,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description="Permite al Lambda PreTokenGeneration leer modIA_portal_*",
        Tags=[
            {"Key": "Project", "Value": "SuperPago"},
            {"Key": "Module", "Value": "PortalClientes"},
        ],
    )

    # Logs basicos
    iam.attach_role_policy(
        RoleName=ROLE_NAME,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )

    # DynamoDB read/update sobre las tablas portal
    inline_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:Query",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem",
                ],
                "Resource": [
                    f"arn:aws:dynamodb:*:{account_id}:table/modIA_portal_users_prod",
                    f"arn:aws:dynamodb:*:{account_id}:table/modIA_portal_users_prod/index/*",
                    f"arn:aws:dynamodb:*:{account_id}:table/modIA_portal_grants_prod",
                    f"arn:aws:dynamodb:*:{account_id}:table/modIA_portal_grants_prod/index/*",
                ],
            }
        ],
    }
    iam.put_role_policy(
        RoleName=ROLE_NAME,
        PolicyName="PortalDynamoDBRead",
        PolicyDocument=json.dumps(inline_policy),
    )

    # IAM eventual consistency: esperar antes de usar el role
    import time as _t

    _t.sleep(10)

    return iam.get_role(RoleName=ROLE_NAME)["Role"]["Arn"]


def _ensure_lambda(lambda_client, role_arn: str) -> str:
    """Crea o actualiza el Lambda function."""
    zip_bytes = _build_lambda_zip()

    try:
        existing = lambda_client.get_function(FunctionName=LAMBDA_NAME)
        # Update code
        lambda_client.update_function_code(
            FunctionName=LAMBDA_NAME,
            ZipFile=zip_bytes,
        )
        return existing["Configuration"]["FunctionArn"]
    except lambda_client.exceptions.ResourceNotFoundException:
        pass

    response = lambda_client.create_function(
        FunctionName=LAMBDA_NAME,
        Runtime="python3.11",
        Role=role_arn,
        Handler="lambda_pre_token_generation.lambda_handler",
        Code={"ZipFile": zip_bytes},
        Description="Inyecta client_grants en JWT del Cognito Pool 2",
        Timeout=10,
        MemorySize=128,
        Environment={
            "Variables": {
                "PORTAL_USERS_TABLE": "modIA_portal_users_prod",
                "PORTAL_GRANTS_TABLE": "modIA_portal_grants_prod",
            }
        },
        Tags={
            "Project": "SuperPago",
            "Module": "PortalClientes",
        },
    )
    return response["FunctionArn"]


def _build_lambda_zip() -> bytes:
    """Empaqueta el archivo lambda como zip en memoria."""
    if not LAMBDA_FILE.exists():
        print(f"ERROR: lambda file not found: {LAMBDA_FILE}", file=sys.stderr)
        sys.exit(1)

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(LAMBDA_FILE, arcname="lambda_pre_token_generation.py")
    buf.seek(0)
    return buf.read()


def _ensure_lambda_invoke_permission(lambda_client, pool_id: str, account_id: str) -> None:
    """Permite a Cognito (specific pool) invocar el Lambda."""
    statement_id = f"cognito-invoke-{pool_id.replace('_', '-')}"
    try:
        lambda_client.add_permission(
            FunctionName=LAMBDA_NAME,
            StatementId=statement_id,
            Action="lambda:InvokeFunction",
            Principal="cognito-idp.amazonaws.com",
            SourceArn=f"arn:aws:cognito-idp:us-east-1:{account_id}:userpool/{pool_id}",
        )
    except ClientError as exc:
        if "ResourceConflictException" in str(exc):
            return  # Permission ya existe
        raise


def _ensure_pre_token_trigger(cognito, pool_id: str, lambda_arn: str) -> None:
    """Configura el Lambda como PreTokenGeneration trigger."""
    pool = cognito.describe_user_pool(UserPoolId=pool_id)["UserPool"]
    triggers = pool.get("LambdaConfig", {}) or {}
    triggers["PreTokenGeneration"] = lambda_arn

    cognito.update_user_pool(
        UserPoolId=pool_id,
        LambdaConfig=triggers,
    )


if __name__ == "__main__":
    main()
