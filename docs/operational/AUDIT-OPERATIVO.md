# Auditoria Operativa - Ecosistema SuperPago
**Fecha**: 2026-03-10
**Auditor**: Operations Auditor Agent

---

## Resumen Ejecutivo

El ecosistema tiene **21 repositorios** activos. El frontend principal (mf-marketing) compila exitosamente pero tiene **tests rotos en CI local** (crash por full page reload en spec 520 de 8744). El backend (covacha-core) tiene 597 archivos Python, 1588 archivos de test, y su ultimo deploy a main fue el 2026-03-11. Hay **15 de 21 repos con cambios sin commitear**, y practicamente **todos los commits usan ISS-000** (sin tracking real de issues).

**Calificacion general: 5/10 - Funcional pero fragil.**

---

## Estado Real por Repositorio

### mf-marketing (Frontend Principal)
- **Build**: PASA (con 4 warnings menores de optional chaining en templates)
- **Tests**: FALLA - 520 de 8744 specs pasan, luego crash "Some of your tests did a full page reload!" seguido de DISCONNECTED. **8,224 specs nunca se ejecutan.**
- **Angular**: 21.0.8 (corriendo en Node.js v25.8.0 - UNSUPPORTED, version impar)
- **Ultimo deploy (main)**: 2026-03-09
- **Actividad**: Muy alta - 20+ commits recientes, todos con ISS-000
- **Archivos sin commitear**: 41 (todos los nuevos tests E2E de Playwright)
- **Deuda Tecnica**:

| Metrica | Valor | Severidad |
|---------|-------|-----------|
| Archivos > 1000 lineas | 6 (todos .spec.ts) | MEDIA |
| Archivos produccion cercanos a 1000 | 3 (993, 960, 940 lineas) | MEDIA |
| Usos de `any` | 880 ocurrencias | ALTA |
| TODOs/FIXMEs pendientes | 12 | BAJA |
| console.log en produccion | 21 | MEDIA |
| console.warn en produccion | 33 | MEDIA |
| console.error en produccion | 152 | ALTA |
| Catch blocks vacios | 0 | OK |
| Total lineas TS produccion | 124,033 | INFO |
| Total lineas TS spec | 109,675 | INFO |
| Archivos spec | 318 | INFO |
| Archivos fuente | 407 | INFO |

---

### covacha-core (Backend Principal)
- **Build**: No verificado (no hay Procfile, no hay app.py/run.py en raiz - requiere requirements.txt con 148 deps)
- **Tests**: 1,588 archivos de test para 352 archivos fuente (ratio 4.5:1 - excelente cobertura de archivos)
- **Ultimo deploy (main)**: 2026-03-11
- **Actividad**: Alta, ultimo commit reciente
- **Archivos sin commitear**: 0 (limpio)
- **Deuda Tecnica**:

| Metrica | Valor | Severidad |
|---------|-------|-----------|
| Archivos Python > 800 lineas | 8 (max: 871 - seed_promotions.py) | MEDIA |
| Controllers > 700 lineas | 6 (facebook_ads: 868, strategy: 842, facebook_sync: 839) | MEDIA |
| Bare except blocks | 0 | OK |
| print() en produccion | 88 ocurrencias en 17 archivos | MEDIA |
| Credencial hardcodeada | 1 (MASTER-SuperSecretKey en script de seed) | CRITICA |
| Total archivos Python | 597 | INFO |

---

### covacha-libs (Libreria Compartida)
- **Ultimo deploy (main)**: 2026-03-11
- **Actividad**: Activa (hard_delete, filtros)
- **Archivos sin commitear**: 4 (incluyendo modelos de modmarketing sin commitear)
- **Estado**: Funcional, ultimo cambio reciente

### covacha-botia (IA Backend)
- **Ultimo deploy (main)**: 2026-02-11 (**28 dias sin deploy**)
- **Ultima actividad**: 2026-03-08 (develop tiene trabajo no deployado)
- **Archivos sin commitear**: 1

### covacha-inventory
- **Ultimo deploy (main)**: 2026-02-14 (**24 dias sin deploy**)
- **Ultima actividad**: 2026-03-08
- **Nota**: Ultimo commit menciona "corregir 233 tests fallidos"

### covacha-notification
- **Ultimo deploy (main)**: 2026-02-11 (**27 dias sin deploy**)
- **Ultima actividad**: 2026-03-06
- **Nota**: Ultimo commit menciona "corregir 68 tests fallidos"

### covacha-payment
- **Ultimo deploy (main)**: 2026-02-11 (**27 dias sin deploy**)
- **Ultima actividad**: 2026-02-26
- **Nota**: Ultimo commit menciona "corregir 141 tests fallidos"

### covacha-transaction
- **Ultimo deploy (main)**: 2026-02-11 (**27 dias sin deploy**)
- **Ultima actividad**: 2026-02-19

### covacha-webhook
- **Ultimo deploy (main)**: 2026-02-11 (**27 dias sin deploy**)
- **Ultima actividad**: 2026-02-19
- **Archivos sin commitear**: 1

### covacha-judicial
- **Ultimo deploy (main)**: 2026-02-14
- **Ultima actividad**: 2026-02-19
- **Archivos sin commitear**: 3

---

### Micro-Frontends

| MF | Deploy (main) | Ultima Actividad | Dirty Files | Estado |
|----|---------------|------------------|-------------|--------|
| **mf-marketing** | 2026-03-09 | 2026-03-10 | 41 | ACTIVO - Tests rotos |
| **mf-core** (Shell) | 2026-03-09 | 2026-03-12 | 2 | ACTIVO |
| **mf-whatsapp** | 2026-03-11 | 2026-03-11 | 7 | ACTIVO |
| **mf-dashboard** | 2026-02-11 | 2026-03-11 | 28 | DIVERGENTE (28 dirty files) |
| **mf-ia** | 2026-02-14 | 2026-03-08 | 0 | ESTABLE |
| **mf-inventory** | 2026-02-11 | 2026-03-08 | 3 | ESTABLE |
| **mf-sp** | N/A (no main) | 2026-03-07 | 7 | SIN DEPLOY |
| **mf-auth** | 2026-02-09 | 2026-02-19 | 3 | ESTANCADO |
| **mf-settings** | 2026-02-11 | 2026-02-19 | 4 | ESTANCADO |
| **mf-payment** | N/A | 2026-02-14 | 4 | ABANDONADO |
| **mf-payment-card** | N/A | 2026-02-14 | 2 | ABANDONADO |
| **mf-template** | N/A | 2026-01-10 | 0 | ABANDONADO (2 meses sin actividad) |

---

## Hallazgos Criticos

### 1. CRITICO: Tests de mf-marketing estan rotos
- 8,744 specs totales, solo 520 se ejecutan antes de crash
- Error: "Some of your tests did a full page reload!" seguido de DISCONNECTED
- **Impacto**: El pipeline CI no puede validar cambios. Cualquier regression pasa desapercibida.
- **Causa probable**: Un spec (alrededor del #520) hace algo que recarga la pagina completa, matando al runner de Karma.

### 2. CRITICO: Node.js v25.8.0 es version impar (NO LTS)
- Angular CLI advierte que esta version no es soportada
- **Impacto**: Bugs inesperados, incompatibilidades potenciales, no es production-grade.

### 3. CRITICO: ISS-000 en el 78% de commits (39/50)
- Casi ningun commit esta vinculado a un issue real
- **Impacto**: Sin trazabilidad de cambios, imposible hacer auditorias de que features se deployaron, incumple la politica propia del equipo.

### 4. ALTO: 880 usos de `any` en TypeScript estricto
- En un proyecto que declara `strict: true` en tsconfig
- **Impacto**: Type safety comprometida, bugs en runtime que el compilador deberia atrapar.

### 5. ALTO: 5 repos backend sin deploy en 27+ dias
- covacha-botia, covacha-notification, covacha-payment, covacha-transaction, covacha-webhook
- Todos tienen actividad en develop que no ha llegado a main
- **Impacto**: Codigo desarrollado no llega a produccion, divergencia creciente.

### 6. ALTO: 206 console.log/warn/error en codigo de produccion
- 152 son `console.error` - puede ser intencional pero excesivo
- 21 `console.log` que probablemente son debug residual
- **Impacto**: Noise en consola de produccion, posible leak de informacion sensible.

### 7. ALTO: 15 de 21 repos tienen cambios sin commitear
- mf-dashboard tiene 28 dirty files
- mf-marketing tiene 41 dirty files (todos E2E tests)
- **Impacto**: Trabajo no respaldado, riesgo de perdida, estado inconsistente.

### 8. MEDIO: Credencial hardcodeada en script de seed
- `MASTER-SuperSecretKey123456789` en `covacha-core/scripts/create_organization_setup_table.py`
- Es un script de setup, no codigo de produccion, pero esta en el repo.
- **Impacto**: Si la key es real y el repo se filtra, acceso no autorizado.

### 9. MEDIO: mf-sp no tiene rama main
- El micro-frontend de SuperPago SPEI no tiene rama principal
- 7 archivos sin commitear incluyendo `.angular/`, `dist/`, `.gitignore`
- **Impacto**: No hay pipeline de deploy funcional para este MF.

### 10. MEDIO: 3 MFs aparentemente abandonados
- mf-template: 2 meses sin actividad (solo tiene commit inicial)
- mf-payment y mf-payment-card: 24+ dias sin actividad, solo docs
- **Impacto**: Recursos desperdiciados si se planeaban usar, o simplemente repos zombies.

---

## Deuda Tecnica Consolidada

| Categoria | Cantidad | Severidad | Repos Afectados |
|-----------|----------|-----------|-----------------|
| Tests rotos/crashes | 8,224 specs sin ejecutar | CRITICA | mf-marketing |
| Node.js no-LTS | 1 instancia | CRITICA | mf-marketing (todos los MFs potencialmente) |
| Commits sin issue tracking | ~78% de commits | CRITICA | Todos |
| Usos de `any` en TS | 880 | ALTA | mf-marketing |
| Repos sin deploy >27 dias | 5 repos | ALTA | covacha-botia/notification/payment/transaction/webhook |
| Console statements en prod | 206 | ALTA | mf-marketing |
| print() en prod Python | 88 | MEDIA | covacha-core |
| Archivos cercanos a 1000 lineas | 9 (TS) + 8 (Python) | MEDIA | mf-marketing, covacha-core |
| Dirty working trees | 15 repos, ~100+ archivos | MEDIA | Casi todos |
| Credenciales en codigo | 1 confirmada | MEDIA | covacha-core (scripts/) |
| MFs abandonados | 3 repos | BAJA | mf-template, mf-payment, mf-payment-card |

---

## Metricas de Tamano del Ecosistema

| Metrica | Valor |
|---------|-------|
| Total repositorios | 21 (+ 3 archivos .md sueltos) |
| Repos backend (covacha-*) | 9 |
| Repos frontend (mf-*) | 12 |
| Lineas TS produccion (mf-marketing) | 124,033 |
| Lineas TS specs (mf-marketing) | ~109,675 |
| Archivos Python (covacha-core) | 597 |
| Archivos test Python (covacha-core) | 1,588 |
| Total specs Karma (mf-marketing) | 8,744 |

---

## Recomendaciones Operativas (Prioridad)

### P0 - Inmediato (esta semana)

1. **Arreglar tests de mf-marketing**: Identificar el spec ~520 que causa full page reload. Probablemente un componente que hace `window.location` o `Router.navigate` sin mock. Sin tests funcionales, cualquier cambio es un riesgo.

2. **Cambiar a Node.js LTS**: Migrar a Node 24 LTS o Node 22 LTS. La version 25 es experimental.

3. **Commitear o descartar los 100+ dirty files**: Especialmente los 41 E2E tests en mf-marketing y los 28 en mf-dashboard. Trabajo no commiteado es trabajo que no existe.

### P1 - Esta sprint (2 semanas)

4. **Deploy de repos backend estancados**: 5 repos tienen codigo en develop sin llegar a main en 27+ dias. Hacer merge o determinar si hay blockers.

5. **Reducir usos de `any`**: Planificar reduccion gradual de los 880 usos. Priorizar archivos de produccion (no specs).

6. **Eliminar console.log/warn de produccion**: Los 21 `console.log` y 33 `console.warn` son probablemente debug residual. Reemplazar con logging service o eliminar.

### P2 - Este mes

7. **Implementar issue tracking real**: El 78% de commits con ISS-000 indica que el proceso de tracking no se esta siguiendo. Evaluar si el proceso es demasiado pesado o si falta disciplina.

8. **Limpiar repos abandonados**: Archivar mf-template, mf-payment, mf-payment-card si no se van a usar. Repos muertos generan confusion.

9. **Eliminar credencial hardcodeada**: Aunque sea en un script de seed, mover a variable de entorno.

10. **Resolver mf-sp sin main**: Crear rama main o definir su pipeline de deploy.

### P3 - Siguiente trimestre

11. **Reducir tamano de archivos grandes**: 8 controllers Python >700 lineas y 3 componentes TS >900 lineas necesitan dividirse.

12. **Consolidar estrategia de testing**: Karma + Jest + Playwright es mucho overhead. Evaluar migrar todo a Jest + Playwright.

13. **Auditar print() en backend**: 88 `print()` en produccion Python deberian ser `logger.info()` o eliminarse.

---

## Conclusion

El ecosistema esta **funcionalmente operativo** - el build de produccion pasa, los deploys fluyen, y hay actividad de desarrollo constante. Sin embargo, la **calidad operativa es fragil**:

- Los tests estan rotos, por lo que no hay red de seguridad
- El tracking de issues es cosmetic (ISS-000 everywhere)
- Hay una divergencia significativa entre develop y main en varios repos
- Mucho trabajo no commiteado en working trees

El riesgo principal es que **cualquier regression en mf-marketing pasara desapercibida** porque 94% de los tests nunca se ejecutan. Esto deberia ser la prioridad absoluta.
