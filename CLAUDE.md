# CLAUDE.md - covacha-projects (Cerebro Central)

## Qué es este repo
Este repo es el CEREBRO CENTRAL del ecosistema BAAT Digital. Aquí se definen:
- Dependencias entre repos (dependencies/dependency-graph.yml)
- Productos y sus repos (products/)
- Metadata de cada repo (repos/)
- Reglas compartidas (rules/)
- Features cross-repo activos (cross-repo/active/)
- Scripts de orquestación (scripts/)

## Ecosistema
- **31 repos** en baatdigital
- **7+ productos**: SuperPago (principal), AlertaTribunal, CRM, IA/Bots, Legacy MiPay
- **Backend**: Python 3.9+, Flask, DynamoDB, AWS
- **Frontend**: Angular 21, Native Federation, hexagonal architecture

## Cómo usar este repo

### Antes de crear una historia de usuario
1. Lee products/<producto>.yml para saber qué repos involucra
2. Lee dependencies/dependency-graph.yml para entender el impacto
3. Si el feature toca >1 repo, crea un issue CROSS aquí primero
4. Luego crea issues individuales en cada repo, referenciando el CROSS

### Antes de modificar un repo
1. Busca el repo en repos/<nombre>.yml
2. Revisa depends_on y consumed_by
3. Si tocas un archivo en breaking_patterns, verifica consumidores

### Para sincronizar reglas
Ejecuta scripts/sync-rules.sh — pushea rules/ a todos los repos

### Para analizar impacto
Ejecuta scripts/impact-analysis.sh <repo> <archivo> — muestra qué repos afecta

## Convenciones
- Archivos YAML usan extensión .yml
- IDs de features cross-repo: CROSS-XXX
- IDs de historias de usuario: ISS-XXX
- Branches: develop → main (auto-merge)
- Coverage mínimo: 80%
- Testing backend: pytest, 3 tests por función
- Testing frontend: Karma+Jasmine, HttpTestingController, Playwright E2E
