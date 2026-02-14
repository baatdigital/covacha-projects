#!/bin/bash
# Priority Matrix
# Uso: ./scripts/priority-matrix.sh
# Muestra la matriz de prioridades cross-producto

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ORG="baatdigital"

echo "========================================"
echo "  PRIORITY MATRIX - $ORG"
echo "========================================"
echo ""

# Leer productos
for product_file in "$ROOT_DIR"/products/*.yml; do
  NAME=$(grep "^name:" "$product_file" | awk '{print $2}')
  PRIORITY=$(grep "^priority:" "$product_file" | awk '{print $2}')
  STATUS=$(grep "^status:" "$product_file" | awk '{print $2}')
  
  echo "[$PRIORITY] $NAME ($STATUS)"
  
  # Contar issues abiertos en los repos del producto
  # (esto requiere gh CLI y puede ser lento)
  echo ""
done

echo "========================================"
echo "  Usa GitHub Projects v2 para vista completa"
echo "========================================"
