# MEMORY.md — Patrones Globales del Ecosistema BAAT Digital
<!-- Cargado automáticamente al inicio de cada sesión Claude Code. Max 200 líneas. -->

## Inicio de sesión (Agent Teams)

```bash
# 1. Bootstrap (genera CONTEXT.md con contexto de DynamoDB + GitHub)
cd /Users/casp/sandboxes/superpago/covacha-projects
python scripts/agent_memory/bootstrap.py --team backend --machine mac-1 --module covacha-payment

# 2. Reclamar tarea
python scripts/agent_memory/claim_task.py --task 043 --team backend --machine mac-1

# 3. Al terminar
python scripts/agent_memory/release_task.py --task 043 --team backend --machine mac-1 --status done --learning "gotcha encontrado"

# 4. Ver estado del equipo
python scripts/agent_memory/team_status.py
```

## Stack por repo

| Repo | Stack | Propósito |
|---|---|---|
| covacha-payment | Python/Flask/DynamoDB | Pagos SPEI, transferencias |
| covacha-core | Python/Flask/DynamoDB | Core multi-tenant, autenticación |
| covacha-botia | Python/Flask/DynamoDB | Bots WhatsApp, agentes IA |
| covacha-transaction | Python/Flask/DynamoDB | Historial de transacciones |
| mf-sp | Angular 21 | Frontend SPEI |
| mf-marketing | Angular 21 | Marketing y landings |
| mf-core | Angular 21 (Shell) | Orquestador de micro-frontends |

## Patrones DynamoDB (single-table)

- PK prefijos: `USER#`, `TXN#`, `ORG#`, `TASK#`, `LEARNING#`, `TEAM#`
- Usar `decimal.Decimal` para montos, NUNCA `float`
- GSI tarda ~5min en propagar en staging
- Batch write: máximo 25 items por operación
- ConditionExpression para locking atómico (ver dynamo_client.py)

## Patrones Flask/Python

- Blueprints en `/app/routes/`, servicios en `/app/services/`
- Type hints obligatorios en todas las funciones
- Docstrings en español para funciones públicas
- `try/except ClientError` específico, nunca bare except
- Tests: `pytest -v`, cobertura mínima 98% (backend), 80% (scripts)

## Git workflow

```bash
# Branch naming
feature/ISS-XXX-descripcion-kebab-case
fix/ISS-XXX-descripcion

# Commit format (OBLIGATORIO)
feat(ISS-042): agregar endpoint de cotizaciones

# Flujo
feature/* → push → CI (tests + coverage)
  → PR automático si coverage >= 98%
    → merge a develop → auto-promote a main → deploy AWS
```

## Selección de modelos Claude

| Labels del issue | Modelo | Cuándo |
|---|---|---|
| research, docs, sync, chore | haiku | Read-only, bajo costo |
| feature, bugfix, backend, frontend | sonnet | Implementación |
| architecture, epic, cross-repo | opus | Decisiones críticas |

## Infraestructura AWS

- Region: us-east-1
- DynamoDB: PAY_PER_REQUEST, TTL habilitado
- EC2 en VPC privada detrás de ALBs
- API Gateway + WAF → VPC Link → ALB → EC2
- Variables de entorno: AWS Parameter Store (NUNCA en código)
- Deploy: GitHub Actions → CodeDeploy → EC2

## Gotchas conocidos

- Mock FINCH API en tests de integración (nunca llamar real en tests)
- CORS: configurar explícitamente, NUNCA `*` en producción
- WhatsApp webhooks: siempre validar token de verificación
- Pagos: usar idempotency keys, webhooks para confirmación (no polling)
- Angular: OnPush strategy + Signals para performance

## GitHub Project Board

- Org: baatdigital | Project #1: SuperPago
- URL: https://github.com/orgs/baatdigital/projects/1
- Scripts de sincronización: `scripts/agent_memory/` en covacha-projects
