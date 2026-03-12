# Plan de Mejora Continua - Ecosistema SuperPago
**Fecha**: 2026-03-10
**Autor**: Analisis automatizado via Claude Code
**Alcance**: mf-marketing (primario) + ecosistema MFs (cross-repo)

---

## 1. Estado Actual de Calidad

### Metricas de Codigo (mf-marketing)

| Metrica | Valor Actual | Objetivo | Gap |
|---------|-------------|----------|-----|
| Archivos > 1000 lineas | 0 | 0 | 0 (cumple) |
| Archivos > 900 lineas (riesgo) | 7 componentes | 0 | 7 |
| Servicios > 500 lineas | 3 (task 940, dashboard-data 853, shared-state 708) | 0 | 3 |
| Usos de `any` | 143 | 0 | 143 |
| `subscribe()` sin cleanup | 377 llamadas en archivos sin patron de cleanup | 0 | 377 |
| `subscribe()` totales (no-spec) | 452 | < 50 | 402 |
| Cleanup patterns (takeUntil/destroy) | 46 | >= subscribe count | -406 |
| Signals adoptados | 1,082 | -- | Buena adopcion |
| BehaviorSubject (legacy) | 11 (5 subjects en 4 servicios) | 0 | 11 |
| OnPush adoption | 173/236 = 73.3% | 100% | 63 componentes |
| Componentes sin OnPush | 64 | 0 | 64 |
| Test coverage ratio (spec:component) | 234:236 = 99.2% | 1:1 | 2 componentes |
| Servicios sin specs | 6 | 0 | 6 |
| Adapters sin specs | 4 | 0 | 4 |
| Console.log en produccion | 207 | 0 | 207 |
| Lazy loading (loadComponent/Children) | 74 | -- | Buena cobertura |
| Bundle budget (initial) | max 1 MB | < 1 MB | Configurado OK |
| node_modules | 582 MB | -- | Monitorear |

### Top 7 Componentes en Riesgo (> 870 lineas)

| Archivo | Lineas | Riesgo |
|---------|--------|--------|
| `presentation/pages/ai-orchestrator/ai-orchestrator-dashboard.component.ts` | 993 | CRITICO (7 lineas del limite) |
| `presentation/pages/client-workspace/tabs/client-media-library.component.ts` | 938 | ALTO |
| `presentation/pages/campaign-builder/steps/review-step.component.ts` | 938 | ALTO |
| `presentation/pages/strategies/strategies.component.ts` | 924 | ALTO |
| `presentation/pages/catalog/catalog.component.ts` | 913 | ALTO |
| `presentation/pages/client-workspace/tabs/client-settings.component.ts` | 908 | ALTO |
| `presentation/components/image-uploader-crop/image-uploader-crop.component.ts` | 900 | ALTO |

### Top 3 Servicios Sobredimensionados

| Archivo | Lineas | Limite |
|---------|--------|--------|
| `application/task.service.ts` | 940 | 1000 (riesgo inminente) |
| `core/services/dashboard-data.service.ts` | 853 | 1000 |
| `shared-state/shared-state.service.ts` | 708 | 1000 |

### Top 15 Archivos con Memory Leaks Potenciales (subscribe sin cleanup)

| Archivo | subscribes | cleanup patterns |
|---------|-----------|-----------------|
| `client-workspace/tabs/client-settings.component.ts` | 19 | 0 |
| `client-workspace/tabs/client-portal.component.ts` | 15 | 0 |
| `client-workspace/tabs/client-media-library.component.ts` | 15 | 0 |
| `facebook-connect-modal/facebook-connect-modal.component.ts` | 13 | 0 |
| `quotations/quotations-page.component.ts` | 11 | 0 |
| `pipeline-item-modal/pipeline-item-modal.component.ts` | 10 | 0 |
| `use-cases/quotations/quotations.use-case.ts` | 10 | 0 |
| `ai-orchestrator/ai-orchestrator-dashboard.component.ts` | 9 | 0 |
| `application/task.service.ts` | 9 | 0 |
| `client-workspace/tabs/client-content.component.ts` | 8 | 0 |
| `calendar/calendar.component.ts` | 8 | 0 |
| `settings/settings.component.ts` | 7 | 0 |
| `client-detail/client-detail.component.ts` | 7 | 0 |
| `analytics/analytics.component.ts` | 7 | 0 |
| `ab-test-manager/ab-test-manager.component.ts` | 7 | 0 |

### BehaviorSubjects a Migrar a Signals

| Servicio | Subject | Linea |
|----------|---------|-------|
| `social-media.service.ts` | `postsSubject = new BehaviorSubject<SocialPost[]>([])` | 52 |
| `social-media.service.ts` | `accountsSubject = new BehaviorSubject<SocialAccount[]>([])` | 56 |
| `ai-content.service.ts` | `historySubject = new BehaviorSubject<GeneratedContent[]>([])` | 113 |
| `client-management.service.ts` | `clientsSubject = new BehaviorSubject<AgencyClient[]>([])` | 26 |
| `client-management.service.ts` | `selectedClientSubject = new BehaviorSubject<AgencyClient\|null>(null)` | 29 |
| `strategy-management.service.ts` | `strategiesSubject = new BehaviorSubject<MarketingStrategy[]>([])` | 23 |

### Salud del CI/CD

| Pipeline | Archivo | Trigger | Caracteristicas |
|----------|---------|---------|----------------|
| CI - Validate & Test | `ci.yml` | push/PR a develop | Commit validation, branch naming, tests, coverage >= 98% |
| Deploy to AWS CDN | `deploy.yml` | push a main | Build, S3 sync, CloudFront invalidation, cache strategy |
| Auto PR | `auto-pr.yml` | (post-CI) | Creacion automatica de PR |
| Promote to Main | `promote.yml` | manual/auto | Merge develop -> main |
| Auto Merge | `auto-merge-develop-to-main.yml` | -- | Auto-merge |

**Evaluacion**: Pipeline CI/CD maduro y bien configurado. Cache strategy correcta (immutable para assets, 5min para remoteEntry.json, no-cache para index.html).

---

## 2. Deuda Tecnica Priorizada

### Critica (Resolver en Sprint actual)

| # | Deuda | Impacto | Esfuerzo | Archivos Afectados |
|---|-------|---------|----------|-------------------|
| 1 | **377 subscribes sin cleanup** - Memory leaks en produccion | Performance, crashes en sesiones largas | 3-5 dias | 15+ archivos (ver tabla arriba) |
| 2 | **ai-orchestrator-dashboard.component.ts a 993 lineas** - A 7 lineas del limite | Violacion inminente del limite 1000 | 1 dia | 1 archivo -> dividir en 2-3 |
| 3 | **task.service.ts a 940 lineas** - Servicio monolitico | Mantenibilidad, testabilidad | 1 dia | 1 archivo -> dividir en task-crud, task-timer, task-notifications |

### Alta (Resolver en 2 sprints)

| # | Deuda | Impacto | Esfuerzo | Archivos Afectados |
|---|-------|---------|----------|-------------------|
| 4 | **143 usos de `any`** - Mayoria en facebook-oauth*.service.ts (FB SDK) | Type safety, bugs en runtime | 3 dias | `facebook-oauth.service.ts` (12), `facebook-oauth-data.service.ts` (16), `http.service.ts` (4) |
| 5 | **64 componentes sin OnPush** - 27% del total | Performance: change detection innecesario | 2 dias | 64 archivos (lista completa en seccion 1) |
| 6 | **207 console.log en produccion** - Ruido en consola, informacion expuesta | Seguridad (tokens/data leaks), performance | 1 dia | Mayorias en `facebook-oauth*.service.ts`, `single-spa-bootstrap.ts` |
| 7 | **6 servicios criticos sin specs** | Cobertura, regresiones | 3 dias | `meta-ai.service`, `facebook-oauth.service`, `facebook-oauth-data.service`, `facebook-oauth-connect.service`, `task.service`, `strategy-state.service` |

### Media (Backlog)

| # | Deuda | Impacto | Esfuerzo | Archivos Afectados |
|---|-------|---------|----------|-------------------|
| 8 | **11 BehaviorSubjects -> Signals** | Consistencia, performance (Angular 21 best practice) | 2 dias | 4 servicios (ver tabla) |
| 9 | **7 componentes > 870 lineas** | Mantenibilidad (crecimiento gradual) | 3 dias | Ver tabla "Componentes en Riesgo" |
| 10 | **4 adapters sin specs** | Cobertura | 1 dia | `project`, `client-settings`, `google-drive`, `social-report` adapters |
| 11 | **dashboard-data.service.ts (853 lineas)** | Complejidad, dificil de testear | 1 dia | Dividir en dashboard-clients, dashboard-strategies, dashboard-aggregator |
| 12 | **`entry.component.ts` y `app.component.ts` sin specs** | 2 componentes criticos sin coverage | 1 dia | 2 archivos |

### Baja (Nice to have)

| # | Deuda | Impacto | Esfuerzo | Archivos Afectados |
|---|-------|---------|----------|-------------------|
| 13 | **mf-template usa `^21.0.0` vs `21.0.8`** pinned en demas MFs | Drift de version potencial | 15 min | `mf-template/package.json` |
| 14 | **`portal.adapter.ts` a 960 lineas** (no-component) | Cercano al limite | 0.5 dia | 1 archivo |
| 15 | **single-spa-bootstrap.ts** con 6 console.logs | Legacy code, informacion expuesta | 15 min | 1 archivo |

---

## 3. Plan de Mejora por Trimestre

### Q2 2026 (Abril-Junio) - "Estabilidad y Performance"

- [ ] **Semana 1-2**: Agregar `takeUntilDestroyed()` a los 15 archivos top con subscribe leaks (#1)
- [ ] **Semana 2**: Dividir `ai-orchestrator-dashboard.component.ts` (993 -> 3 archivos) (#2)
- [ ] **Semana 2**: Dividir `task.service.ts` en task-crud, task-timer, task-notifications (#3)
- [ ] **Semana 3-4**: Tipar FB SDK wrappers - crear `types/facebook-sdk.d.ts` para eliminar 28+ `any` (#4)
- [ ] **Semana 4-5**: Agregar OnPush a 64 componentes (batch de 15/semana) (#5)
- [ ] **Semana 5-6**: Reemplazar `console.log` con servicio de logging con niveles (prod=error only) (#6)
- [ ] **Semana 6-8**: Escribir specs para 6 servicios criticos sin tests (#7)

### Q3 2026 (Julio-Septiembre) - "Modernizacion"

- [ ] Migrar 11 BehaviorSubjects a Angular Signals (#8)
- [ ] Dividir 7 componentes > 870 lineas antes de que lleguen a 1000 (#9)
- [ ] Completar specs para 4 adapters sin tests (#10)
- [ ] Dividir `dashboard-data.service.ts` (#11)
- [ ] Evaluar tree-shaking del bundle y reducir node_modules (582 MB)
- [ ] Implementar ESLint rule: max-lines-per-file = 1000, warn at 800

### Q4 2026 (Octubre-Diciembre) - "Automatizacion y Observabilidad"

- [ ] CI: Agregar lint rule para detectar `subscribe()` sin `takeUntilDestroyed`
- [ ] CI: Agregar check de tamano de archivos (warn > 800, fail > 1000)
- [ ] CI: Agregar check `any` count (fail si incrementa)
- [ ] Dashboard de metricas de calidad (historico de deuda tecnica)
- [ ] Evaluar migration path a Angular 22 LTS

---

## 4. Patrones a Estandarizar (Cross-MF)

### 4.1 Subscription Management (ESTANDARIZAR)

**Patron actual (inconsistente)**: Mezcla de nada, `takeUntil`, `takeUntilDestroyed`, `unsubscribe`.

**Patron a adoptar**:
```typescript
// Angular 21+: usar takeUntilDestroyed() en todos los componentes
private destroyRef = inject(DestroyRef);

ngOnInit() {
  this.someService.getData()
    .pipe(takeUntilDestroyed(this.destroyRef))
    .subscribe(data => { ... });
}
```

**Archivos afectados**: 452 `subscribe()` calls, 46 con cleanup = solo 10.2% tiene cleanup.

### 4.2 State Management (ESTANDARIZAR)

**Patron actual**: BehaviorSubject en 4 servicios core, signal() en 1,082 lugares.

**Patron a adoptar**: Angular Signals para estado local y derivado.
```typescript
// ANTES
private clientsSubject = new BehaviorSubject<AgencyClient[]>([]);
clients$ = this.clientsSubject.asObservable();

// DESPUES
private _clients = signal<AgencyClient[]>([]);
readonly clients = this._clients.asReadonly();
```

### 4.3 Change Detection (ESTANDARIZAR)

**Patron a adoptar**: OnPush en 100% de componentes. Solo 73.3% actualmente.

### 4.4 Angular Version Pinning (ESTANDARIZAR)

| MF | Version | Correcto? |
|----|---------|-----------|
| mf-auth | 21.0.8 | Si |
| mf-core | 21.0.8 | Si |
| mf-dashboard | 21.0.8 | Si |
| mf-docs | 21.0.8 | Si |
| mf-ia | 21.0.8 | Si |
| mf-inventory | 21.0.8 | Si |
| mf-marketing | 21.0.8 | Si |
| mf-settings | 21.0.8 | Si |
| mf-sp | 21.0.8 | Si |
| mf-whatsapp | 21.0.8 | Si |
| **mf-template** | **^21.0.0** | **NO - usar pin exacto** |

**Federation**: Todos los MFs en `@angular-architects/native-federation@21.0.4` (consistente).

### 4.5 Logging (ESTANDARIZAR)

**Patron a adoptar**: Servicio centralizado con niveles.
```typescript
// Reemplazar 207 console.log con:
@Injectable({ providedIn: 'root' })
export class LoggerService {
  private level = environment.production ? LogLevel.ERROR : LogLevel.DEBUG;
  debug(tag: string, ...args: unknown[]) { ... }
  warn(tag: string, ...args: unknown[]) { ... }
  error(tag: string, ...args: unknown[]) { ... }
}
```

---

## 5. Automatizaciones Pendientes

| # | Automatizacion | Impacto | Esfuerzo | Tipo |
|---|---------------|---------|----------|------|
| 1 | **ESLint rule: no-unsubscribed-observable** - Detectar subscribes sin cleanup en CI | Prevenir memory leaks | 0.5 dia | CI/CD |
| 2 | **ESLint rule: max-lines = 1000** - Fallar build si un archivo excede el limite | Prevenir crecimiento | 0.5 dia | CI/CD |
| 3 | **ESLint rule: no-any** - Warn en CI si se agrega nuevo `any` | Type safety | 0.5 dia | CI/CD |
| 4 | **Pre-commit hook: OnPush check** - Nuevos componentes deben tener OnPush | Consistencia | 0.5 dia | Git hook |
| 5 | **CI: Console.log detector** - Fallar si hay console.log fuera de LoggerService | Seguridad | 0.5 dia | CI/CD |
| 6 | **Dependabot/Renovate** - Auto-update de dependencias con auto-merge para patch | Seguridad deps | 1 dia | GitHub |
| 7 | **Lighthouse CI en PR** - Budget check automatico en cada PR | Performance | 1 dia | CI/CD (ya existe `yarn lighthouse:ci`) |
| 8 | **E2E post-deploy smoke** - Ejecutar `yarn e2e:smoke` automaticamente despues de deploy | Confiabilidad | 0.5 dia | CI/CD (workflow existe, verificar integracion) |

---

## 6. Metricas de Seguimiento

### Dashboard Propuesto (revisar mensualmente)

| Metrica | Medicion | Comando |
|---------|----------|---------|
| Subscribe leak ratio | `subscribe()` sin cleanup / total | `grep -rn "subscribe(" src/ --include="*.ts" --exclude="*.spec.ts" \| wc -l` vs cleanup count |
| OnPush adoption % | OnPush / total componentes | `grep -rn "OnPush" src/ \| wc -l` / `find src -name "*.component.ts" \| wc -l` |
| `any` count | Total `any` en codigo | `grep -rn ": any\|:any\|as any" src/ --include="*.ts" --exclude="*.spec.ts" \| wc -l` |
| Max file size | Lineas del archivo mas grande | `find src -name "*.ts" -exec wc -l {} + \| sort -rn \| head -1` |
| Console.log count | Logs en no-spec | `grep -rn "console\." src/ --include="*.ts" --exclude="*.spec.ts" \| wc -l` |
| Signal vs BehaviorSubject | Ratio modernizacion | signal count vs BehaviorSubject count |
| Spec coverage | Archivos con spec / total archivos | Components + services + adapters con spec |
| Bundle size | Initial chunk | `ng build --stats-json` |

### Valores Actuales (Baseline 2026-03-10)

```
subscribe_leak_ratio:     89.8% (406/452 sin cleanup)
onpush_adoption:          73.3% (173/236)
any_count:                143
max_file_lines:           993 (ai-orchestrator-dashboard.component.ts)
console_log_count:        207
signal_vs_subject:        1082:11 (99:1 ratio - excelente)
spec_coverage_components: 99.2% (234/236)
spec_coverage_services:   85% (aprox, 6 sin spec)
```

### Objetivos Q2 2026

```
subscribe_leak_ratio:     < 20%
onpush_adoption:          > 95%
any_count:                < 50
max_file_lines:           < 900
console_log_count:        0 (usar LoggerService)
spec_coverage:            100% para componentes, servicios, adapters
```

---

## 7. Resumen Ejecutivo

**Estado general**: El proyecto mf-marketing tiene una base solida - Angular 21 adoptado, signals bien implementados (1,082 usos), lazy loading extensivo (74 rutas), CI/CD maduro con 5 workflows, y consistencia cross-repo en versiones de Angular y Federation.

**Riesgo principal**: **Memory leaks por subscriptions sin cleanup** (89.8% de subscribes no tienen patron de limpieza). Esto afecta directamente la experiencia del usuario en sesiones largas.

**Quick wins** (alto impacto, bajo esfuerzo):
1. Agregar `takeUntilDestroyed()` a los 15 archivos top (2 dias)
2. Dividir `ai-orchestrator-dashboard.component.ts` antes de que cruce 1000 lineas (0.5 dia)
3. Reemplazar `console.log` con LoggerService (1 dia)
4. Pinear `@angular/core` en mf-template a `21.0.8` (15 min)

**Inversion total estimada Q2**: ~4 semanas-persona para resolver toda la deuda critica y alta.
