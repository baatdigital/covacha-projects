"""
Configuración central del sistema de memoria compartida.
Lee variables de entorno con fallback a defaults de desarrollo.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# AWS
AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
DYNAMO_TABLE: str = os.getenv("DYNAMO_TABLE", "covacha-agent-memory")

# GitHub Project Board (baatdigital org, SuperPago project #1)
GITHUB_ORG: str = "baatdigital"
GITHUB_PROJECT_ID: str = "PVT_kwDOBBTMcM4BPNTK"
GITHUB_STATUS_FIELD_ID: str = "PVTSSF_lADOBBTMcM4BPNTKzg9rxDE"
GITHUB_PRODUCTO_FIELD_ID: str = "PVTSSF_lADOBBTMcM4BPNTKzg9rxJ8"

# Status option IDs en el Project Board
STATUS_TODO: str = "f75ad846"
STATUS_IN_PROGRESS: str = "47fc9ee4"
STATUS_DONE: str = "98236657"

# Producto
PRODUCTO_SUPERPAGO: str = "ecf14cc9"

# Locking
LOCK_TTL_SECONDS: int = 1800  # 30 min anti-deadlock

# Repos por tipo de issue
REPO_BACKEND: str = "covacha-payment"
REPO_FRONTEND: str = "mf-sp"
REPO_CROSS: str = "covacha-projects"

# Modelos Claude por tipo de tarea
MODEL_HAIKU: str = "haiku"
MODEL_SONNET: str = "sonnet"
MODEL_OPUS: str = "opus"

# Mapeo de labels a modelo recomendado
MODEL_MAP: dict[str, str] = {
    # Haiku: tareas simples, read-only, docs
    "research": MODEL_HAIKU,
    "exploration": MODEL_HAIKU,
    "search": MODEL_HAIKU,
    "docs": MODEL_HAIKU,
    "tracking": MODEL_HAIKU,
    "sync": MODEL_HAIKU,
    "chore": MODEL_HAIKU,
    # Sonnet: implementación balanceada
    "feature": MODEL_SONNET,
    "bugfix": MODEL_SONNET,
    "backend": MODEL_SONNET,
    "frontend": MODEL_SONNET,
    "test": MODEL_SONNET,
    "refactor": MODEL_SONNET,
    # Opus: decisiones críticas y arquitectura
    "architecture": MODEL_OPUS,
    "epic": MODEL_OPUS,
    "cross-repo": MODEL_OPUS,
    "security": MODEL_OPUS,
}

# Modelo default cuando no hay label reconocida
MODEL_DEFAULT: str = MODEL_SONNET
