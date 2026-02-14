#!/bin/bash
# Impact Analysis Tool
# Uso: ./scripts/impact-analysis.sh <repo-name> [file-pattern]
# Ejemplo: ./scripts/impact-analysis.sh covacha-libs "models/*.py"
# Analiza qué repos se ven afectados por cambios en un repo/archivo

set -e

REPO_NAME="${1:?Error: Proporciona el nombre del repo (ej: covacha-libs)}"
FILE_PATTERN="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
DEP_FILE="$ROOT_DIR/dependencies/dependency-graph.yml"

echo "========================================"
echo "  IMPACT ANALYSIS - $REPO_NAME"
echo "========================================"
echo ""

if [ ! -f "$DEP_FILE" ]; then
  echo "ERROR: No se encontró dependency-graph.yml"
  exit 1
fi

# Buscar el repo en el grafo
echo "## Repo: $REPO_NAME"
echo ""

# Extraer tipo e impacto
TYPE=$(grep -A1 "^${REPO_NAME}:" "$DEP_FILE" | grep "type:" | awk '{print $2}' || echo "unknown")
IMPACT=$(grep -A20 "^${REPO_NAME}:" "$DEP_FILE" | grep "impact:" | awk '{print $2}' || echo "unknown")

echo "Tipo: $TYPE"
echo "Impacto: $IMPACT"
echo ""

# Buscar consumidores directos
echo "## Consumidores directos:"
grep -A50 "^${REPO_NAME}:" "$DEP_FILE" | grep -E "^\s+- " | grep -v "^--" | while read -r line; do
  echo "  $line"
done
echo ""

# Buscar quién depende de este repo
echo "## Repos que dependen de $REPO_NAME:"
grep -B1 "$REPO_NAME" "$DEP_FILE" | grep -E "^[a-z]" | sed 's/://' | while read -r dep; do
  if [ "$dep" != "$REPO_NAME" ]; then
    echo "  - $dep"
  fi
done
echo ""

# Si se proporcionó un patrón de archivo
if [ -n "$FILE_PATTERN" ]; then
  echo "## Riesgo para patrón: $FILE_PATTERN"
  BREAKING="$ROOT_DIR/dependencies/breaking-changes.yml"
  if [ -f "$BREAKING" ]; then
    if grep -q "$FILE_PATTERN" "$BREAKING" 2>/dev/null; then
      echo "  ⚠️  ALTO RIESGO: Este patrón está en breaking-changes.yml"
      grep -A3 "$FILE_PATTERN" "$BREAKING" | while read -r line; do
        echo "  $line"
      done
    else
      echo "  ✅ Este patrón NO está en breaking-changes.yml"
    fi
  fi
fi

echo ""
echo "========================================"
echo "  Consulta dependency-graph.yml para más detalle"
echo "========================================"
