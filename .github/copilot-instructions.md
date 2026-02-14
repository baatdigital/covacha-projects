# Copilot Instructions - covacha-projects

Este repo es el orquestador central. NO contiene código de aplicación.

## Al revisar PRs en este repo
- Verifica que dependency-graph.yml sea consistente con products/*.yml
- Verifica que repos/*.yml tengan campos requeridos: name, product, type, language
- Verifica que rules/ no contradiga las reglas en los CLAUDE.md de cada repo
- Si se modifica breaking_patterns, sugiere verificar todos los consumidores

## Formato
- YAML válido en todos los archivos .yml
- Comentarios descriptivos en archivos de configuración
- Scripts deben tener header con descripción y uso
