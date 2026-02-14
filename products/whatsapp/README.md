# MF-WhatsApp – Épicas e historias de usuario

Este directorio contiene la definición completa de **épicas** e **historias de usuario** del proyecto MF-WhatsApp, con criterios de aceptación detallados y alineados a **arquitectura hexagonal** y al ecosistema SuperPago/sp-agents.

## Contenido

| Archivo | Descripción |
|--------|-------------|
| [EPICAS.md](EPICAS.md) | Definición de las 5 épicas (EP-MFW-001 a EP-MFW-005) |
| [ARQUITECTURA.md](ARQUITECTURA.md) | Arquitectura hexagonal aplicada a MF-WhatsApp |
| [stories/](stories/) | Una historia por archivo (HU-MFW-001 a HU-MFW-017) |

## Crear issues en GitHub

### Opción 1: Desde tu máquina (recomendado la primera vez)

Desde la raíz del repo, con [GitHub CLI](https://cli.github.com/) (`gh`) instalado y autenticado:

```bash
# Crear labels de épicas si no existen
./scripts/setup-labels.sh

# Crear las 17 historias de usuario
./scripts/create-mfw-issues.sh

# Solo simular (no crea issues)
./scripts/create-mfw-issues.sh --dry-run
```

### Opción 2: Desde GitHub Actions

1. En el repo: **Actions** → **Create MF-WhatsApp User Story Issues**.
2. **Run workflow** (rama `main` o `develop`).
3. Opcional: marcar **Solo simular** para dry-run.
4. El job crea los issues con el token del repo (no necesitas `gh` local).

## Labels recomendados

Asegúrate de tener creados (por ejemplo con `./scripts/setup-labels.sh`):

- `user-story`, `epic-1` … `epic-5`
- `backend`, `frontend`, `infra`
- `priority:high`, `priority:medium`, `priority:low`
- `mac-1`, `mac-2`, `in-progress`, `blocked`, `ready`

## Referencia rápida

| Épica | Código | Historias |
|-------|--------|-----------|
| Integración SP-Agents y Autenticación | EP-MFW-001 | HU-MFW-001, HU-MFW-002, HU-MFW-003 |
| Dashboard Multi-Cliente (Super Admin) | EP-MFW-002 | HU-MFW-004, HU-MFW-005, HU-MFW-006 |
| Interface Conversaciones WhatsApp Web | EP-MFW-003 | HU-MFW-007, HU-MFW-008, HU-MFW-009, HU-MFW-010 |
| Sistema de Automatización y Bots | EP-MFW-004 | HU-MFW-011, HU-MFW-012, HU-MFW-013, HU-MFW-014 |
| Análisis y Reportes de Mensajería | EP-MFW-005 | HU-MFW-015, HU-MFW-016, HU-MFW-017 |
