#!/bin/bash
# Create Cross-Repo Story
# Uso: ./scripts/create-cross-story.sh
# Crea un issue CROSS en covacha-projects y issues hijos en repos afectados
# Requiere: gh CLI autenticado

set -e

ORG="baatdigital"
ORCHESTRATOR="covacha-projects"

echo "========================================"
echo "  CREATE CROSS-REPO STORY"
echo "========================================"
echo ""

# Solicitar información
read -p "Nombre del feature: " FEATURE_NAME
read -p "Descripción: " DESCRIPTION
read -p "Repos afectados (separados por espacio): " -a REPOS
read -p "Orden de ejecución (separados por espacio): " -a ORDER
read -p "Story points totales: " POINTS

echo ""
echo "## Resumen:"
echo "Feature: $FEATURE_NAME"
echo "Repos: ${REPOS[*]}"
echo "Orden: ${ORDER[*]}"
echo "Points: $POINTS"
echo ""

read -p "¿Crear issues? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
  echo "Cancelado."
  exit 0
fi

# Crear issue CROSS en orchestrator
CROSS_BODY="## Feature Cross-Repo: $FEATURE_NAME

$DESCRIPTION

### Repos afectados
$(for r in "${REPOS[@]}"; do echo "- [ ] $r"; done)

### Orden de ejecución
$(i=1; for r in "${ORDER[@]}"; do echo "$i. $r"; i=$((i+1)); done)

### Story Points: $POINTS

### Issues hijos
(se actualizará después de crear los issues)"

echo "Creando issue CROSS en $ORCHESTRATOR..."
CROSS_URL=$(gh issue create \
  --repo "$ORG/$ORCHESTRATOR" \
  --title "[CROSS] $FEATURE_NAME" \
  --body "$CROSS_BODY" \
  --label "cross-repo" 2>&1)

echo "  ✅ CROSS issue creado: $CROSS_URL"

# Crear issues hijos en cada repo
echo ""
echo "Creando issues hijos..."
for repo in "${REPOS[@]}"; do
  echo "  → $repo..."
  CHILD_URL=$(gh issue create \
    --repo "$ORG/$repo" \
    --title "[CROSS] $FEATURE_NAME" \
    --body "Parte del feature cross-repo: $CROSS_URL

$DESCRIPTION

Referencia: $CROSS_URL" \
    --label "cross-repo" 2>&1) || echo "    ⚠️  Error creando issue en $repo"
  
  if [ -n "$CHILD_URL" ]; then
    echo "    ✅ $CHILD_URL"
  fi
done

echo ""
echo "========================================"
echo "  Cross-repo story creada exitosamente"
echo "========================================"
