## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** ver métricas de mis conversaciones de WhatsApp  
**Para** entender el volumen y efectividad de mi comunicación  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Existe una página o sección “Métricas” o “Analytics” accesible desde el menú del MF (para el cliente actual); muestra un dashboard con al menos: mensajes enviados y recibidos por período (día/semana/mes), tiempo de respuesta promedio, tasa de resolución de consultas (si el backend la expone), engagement por contacto (ej. conversaciones activas únicas).
- [ ] **C2.** El usuario puede seleccionar el período (date range: últimos 7 días, 30 días, mes actual, custom); los datos se actualizan al cambiar el período.
- [ ] **C3.** Los datos se filtran por el cliente/organización actual y opcionalmente por número de WhatsApp (selector de número si hay varios).
- [ ] **C4.** Métricas mostradas con tarjetas (cards) o gráficos claros; números con formato legible (ej. 1.2k, separador de miles); tiempo de respuesta en minutos/horas.
- [ ] **C5.** Si no hay datos para el período, se muestra “Sin datos” o “0” sin error; carga con skeleton o spinner mientras se obtienen datos.
- [ ] **C6.** Definición de “tiempo de respuesta”: tiempo desde mensaje entrante hasta primera respuesta del equipo (backend debe calcularlo); “tasa de resolución” según definición de negocio (ej. conversación cerrada con respuesta).
- [ ] **C7.** Diseño responsive; al menos usable en tablet y desktop.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Dashboard carga en < 2s; cambio de período actualiza gráficos en < 1s; endpoint de métricas responde < 500ms |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Métricas filtradas por organización en backend; no exponer métricas de otras orgs; date range limitado a máximo 1 año |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint de métricas: GET con query params orgId, phoneNumberId? (opcional), dateFrom, dateTo; respuesta con sentCount, receivedCount, avgResponseTimeMinutes?, resolutionRate?, activeConversationsCount?; documentar.
- [ ] Cálculo de tiempo de respuesta y resolución según reglas de negocio; persistencia en DynamoDB o agregación desde tabla de mensajes.

**Frontend (Hexagonal):**
- [ ] `domain/models/metrics.model.ts`: ConversationMetrics (period, sentCount, receivedCount, avgResponseTimeMinutes?, resolutionRate?, activeConversations?).
- [ ] `domain/ports/metrics.port.ts`: getMetrics(orgId, params: { phoneNumberId?, dateFrom, dateTo }).
- [ ] `infrastructure/adapters/metrics.adapter.ts`: GET a endpoint de métricas; mapear a ConversationMetrics.
- [ ] `application/use-cases/metrics-dashboard.use-case.ts`: estado metrics, loading, error; loadMetrics(dateFrom, dateTo, phoneNumberId?); usar SharedState para orgId.
- [ ] `presentation/pages/analytics/` o `metrics/`: date range picker (o presets 7d/30d/mes); selector de número opcional; tarjetas o gráficos (reutilizar librería existente en ecosistema si hay); pipe para formatear números y tiempos.
- [ ] Ruta en entry.routes.ts; solo usuarios con permiso de ver métricas (o todos los admins del cliente).
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_fetch_metrics_with_date_range` | `infrastructure/adapters/metrics.adapter.spec.ts` | GET envía dateFrom, dateTo, phoneNumberId como query params |
| `should_map_metrics_response_to_model` | `infrastructure/adapters/metrics.adapter.spec.ts` | Respuesta API mapeada a ConversationMetrics correctamente |
| `should_load_metrics_on_period_change` | `application/use-cases/metrics-dashboard.use-case.spec.ts` | Cambio de período dispara nueva carga de métricas |
| `should_update_metrics_signals` | `application/use-cases/metrics-dashboard.use-case.spec.ts` | Signals metrics, loading, error se actualizan |
| `should_handle_empty_metrics` | `application/use-cases/metrics-dashboard.use-case.spec.ts` | Sin datos → metrics con valores 0, sin error |
| `should_render_metrics_cards` | `presentation/pages/analytics/metrics-dashboard.component.spec.ts` | Cards de enviados, recibidos, tiempo respuesta visibles |
| `should_render_date_range_picker` | `presentation/pages/analytics/metrics-dashboard.component.spec.ts` | Presets 7d/30d/mes y custom range picker |
| `should_render_number_filter` | `presentation/pages/analytics/metrics-dashboard.component.spec.ts` | Selector de número opcional cuando hay múltiples |
| `should_show_skeleton_while_loading` | `presentation/pages/analytics/metrics-dashboard.component.spec.ts` | Skeleton loader durante carga |
| `should_format_numbers_readably` | `presentation/pages/analytics/metrics-dashboard.component.spec.ts` | Números con formato legible (1.2k, separadores) |
| `should_format_response_time` | `presentation/pages/analytics/metrics-dashboard.component.spec.ts` | Tiempo de respuesta en min/horas legible |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_get_metrics_by_date_range` | `tests/unit/controllers/test_metrics_controller.py` | GET retorna métricas filtradas por dateFrom/dateTo |
| `test_get_metrics_by_phone_number` | `tests/unit/controllers/test_metrics_controller.py` | Filtro por phoneNumberId funciona |
| `test_get_metrics_filtered_by_org` | `tests/unit/controllers/test_metrics_controller.py` | Métricas filtradas por organización del header |
| `test_calculate_avg_response_time` | `tests/unit/services/test_metrics_aggregation_service.py` | Cálculo promedio de tiempo de respuesta correcto |
| `test_calculate_sent_received_count` | `tests/unit/services/test_metrics_aggregation_service.py` | Conteo de enviados/recibidos por período correcto |
| `test_metrics_empty_for_period` | `tests/unit/services/test_metrics_aggregation_service.py` | Período sin mensajes retorna conteos en 0 |
| `test_metrics_date_range_limit` | `tests/unit/controllers/test_metrics_controller.py` | Rango > 1 año retorna 400 |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_load_and_display_metrics_for_period` | Frontend | Seleccionar período → métricas cargan → cards actualizadas |
| `should_change_period_and_update_charts` | Frontend | Cambiar de 7d a 30d → nueva request → gráficos actualizados |
| `test_metrics_aggregation_with_real_data` | Backend | Insertar mensajes en DynamoDB → GET metrics → valores correctos |
| `test_metrics_endpoint_performance` | Backend | Endpoint responde < 500ms para 30 días de datos |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `MetricsAdapter` | ≥ 98% |
| `MetricsDashboardUseCase` | ≥ 98% |
| `MetricsDashboardComponent` | ≥ 98% |
| `MetricsAggregationService` (backend) | ≥ 98% |
| `MetricsController` (backend) | ≥ 95% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-001 (auth), backend con agregación de métricas.  
**Bloquea a:** HU-MFW-016 (reportes bots puede reutilizar misma página con filtro).

---

## 📊 Estimación

**Complejidad:** Alta  
**Puntos de Historia:** 5  
**Tiempo estimado:** 4–5 días  

---

## 📝 Notas Técnicas

- Si el ecosistema ya tiene mf-analytics o módulo de métricas, alinear diseño y posiblemente reutilizar componentes.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Backend no tiene agregación de métricas implementada | Alta | Alto | Diseñar tabla DynamoDB de métricas agregadas (modcore_whatsapp_metrics); job de agregación diario; para MVP, calcular on-demand con límite de rango |
| Formato de gráficos no consistente con otros dashboards del ecosistema | Media | Bajo | Evaluar y reutilizar librería de charts usada en mf-dashboard o analytics v2; estandarizar paleta de colores |
| Cálculo de 'tiempo de respuesta' ambiguo | Media | Alto | Definir formalmente: tiempo desde primer mensaje incoming hasta primer mensaje outgoing (humano o bot) en esa conversación; documentar en CLAUDE.md |

---

## ✅ Definición de Hecho (DoD)

- [ ] Código implementado según criterios de aceptación
- [ ] Tests unitarios (coverage ≥ 98% en código nuevo/modificado)
- [ ] Lint limpio (`ng lint` sin errores)
- [ ] Build exitoso (`yarn build:prod`)
- [ ] Sin errores en consola del navegador
- [ ] Documentación actualizada (CLAUDE.md si aplica)
- [ ] PR creado con descripción y linked issue
- [ ] Criterios de aceptación validados manualmente

---

## 🏷️ Labels

`user-story` `epic-5` `backend` `frontend` `priority:high` `size:L`
