"""Crea la tabla DynamoDB `covacha-agent-memory` para Agent Teams Claude Code."""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
TABLE_NAME: str = "covacha-agent-memory"


def _dynamo_client() -> boto3.client:
    """Retorna cliente DynamoDB con credenciales del entorno."""
    return boto3.client(
        "dynamodb",
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY or None,
    )


def _gsi(index_name: str, pk_attr: str) -> dict:
    """Construye definicion de GSI con PK personalizada, RANGE=PK, proyeccion ALL."""
    return {
        "IndexName": index_name,
        "KeySchema": [
            {"AttributeName": pk_attr, "KeyType": "HASH"},
            {"AttributeName": "PK", "KeyType": "RANGE"},
        ],
        "Projection": {"ProjectionType": "ALL"},
    }


def create_table() -> None:
    """
    Crea la tabla covacha-agent-memory en DynamoDB.

    Esquema: PK (S) + SK (S), TTL en atributo `ttl`, billing PAY_PER_REQUEST.
    GSIs: status-gsi (por estado de tarea) y label-gsi (por label de agente).
    Si la tabla ya existe imprime aviso y continua sin error.
    """
    client = _dynamo_client()
    try:
        client.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {"AttributeName": "PK",     "AttributeType": "S"},
                {"AttributeName": "SK",     "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
                {"AttributeName": "label",  "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            GlobalSecondaryIndexes=[
                _gsi("status-gsi", "status"),
                _gsi("label-gsi",  "label"),
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        client.get_waiter("table_exists").wait(TableName=TABLE_NAME)
        client.update_time_to_live(
            TableName=TABLE_NAME,
            TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl"},
        )
        print(f"Tabla '{TABLE_NAME}' creada exitosamente en region '{AWS_REGION}'.")
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceInUseException":
            print(f"La tabla '{TABLE_NAME}' ya existe en '{AWS_REGION}'. Sin cambios.")
        else:
            raise


if __name__ == "__main__":
    create_table()
