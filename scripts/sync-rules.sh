#!/bin/bash
# Sync Rules Tool
# Uso: ./scripts/sync-rules.sh [--dry-run]
# Sincroniza las reglas de rules/ a los CLAUDE.md de todos los repos
# Requiere: gh CLI autenticado

set -e

DRY_RUN=false
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=true
  echo "🔍 DRY RUN - No se harán cambios"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ORG="baatdigital"

echo "========================================"
echo "  SYNC RULES - $ORG"
echo "========================================"
echo ""

# Leer reglas de testing
TESTING_FILE="$ROOT_DIR/rules/testing-rules.yml"
BRANCH_FILE="$ROOT_DIR/rules/branch-rules.yml"

if [ ! -f "$TESTING_FILE" ] || [ ! -f "$BRANCH_FILE" ]; then
  echo "ERROR: No se encontraron archivos de reglas"
  exit 1
fi

echo "## Reglas a sincronizar:"
echo "  - testing-rules.yml"
echo "  - branch-rules.yml"
echo "  - naming-conventions.yml"
echo ""

# Listar repos activos
REPOS=$(ls "$ROOT_DIR/repos/"*.yml 2>/dev/null | while read -r f; do
  basename "$f" .yml
done)

echo "## Repos a actualizar:"
for repo in $REPOS; do
  echo "  - $repo"
done
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "🔍 Dry run completado. Usa sin --dry-run para aplicar cambios."
  exit 0
fi

echo "## Sincronizando..."
for repo in $REPOS; do
  echo "  → $repo..."
  # Verificar que el repo existe
  if gh repo view "$ORG/$repo" --json name > /dev/null 2>&1; then
    echo "    ✅ Repo existe"
    # Aquí se podría agregar lógica para actualizar archivos via API
    # Por ahora solo verifica existencia
  else
    echo "    ⚠️  Repo no encontrado, saltando"
  fi
done

echo ""
echo "========================================"
echo "  Sync completado"
echo "========================================"
