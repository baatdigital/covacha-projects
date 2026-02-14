## 📖 Historia de Usuario

**Como** super administrador  
**Quiero** ver el rendimiento de los bots por cliente  
**Para** optimizar las automatizaciones y mejorar la experiencia  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** En una vista “Rendimiento de bots” (o dentro de Analytics con filtro “super admin”) el super administrador ve una lista o tabla de clientes con métricas asociadas a la automatización: número de conversaciones atendidas por bot, porcentaje de escalamiento manual (take-over), tiempo promedio de respuesta del bot, satisfacción si se captura.
- [ ] **C2.** Los datos se pueden filtrar por período (date range) y opcionalmente por cliente; la lista muestra un ítem por cliente (o por número) con las métricas agregadas.
- [ ] **C3.** Métricas mostradas: conversaciones con bot activo, % resueltas sin intervención humana, % que pasaron a manual (take-over), tiempo medio de primera respuesta del bot.
- [ ] **C4.** Solo super_admin (o rol equivalente) puede acceder a esta vista; administrador de cliente no la ve o ve solo sus propios datos (según política).
- [ ] **C5.** Carga con skeleton o spinner; estado vacío “Sin datos” cuando no hay métricas en el período.
- [ ] **C6.** Opcional: gráfico de tendencia (ej. % take-over en el tiempo) para identificar patrones; exportar a CSV si se implementa HU-MFW-017.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Reporte de bots carga en < 2s para hasta 50 clientes; paginación si más |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Solo super_admin accede a reportes cross-cliente; datos agregados, no conversaciones individuales expuestas |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoint de métricas de bots: GET con orgId (y opcional clientId, dateFrom, dateTo); respuesta por cliente/número: botConversationsCount, takeoverCount, takeoverRate?, avgBotResponseTimeSeconds?; documentar.
- [ ] Agregación desde eventos de conversación (bot_responded, take_over); persistir en tabla de métricas o calcular on-demand.

**Frontend (Hexagonal):**
- [ ] `domain/models/metrics.model.ts`: BotPerformanceMetrics (clientId?, phoneNumberId?, botConversationsCount, takeoverCount, takeoverRate?, avgBotResponseTimeSeconds?).
- [ ] `domain/ports/metrics.port.ts`: getBotPerformance(orgId, params?: { clientId?, dateFrom, dateTo }) → lista de BotPerformanceMetrics.
- [ ] Adapter: GET a endpoint de rendimiento de bots.
- [ ] `application/use-cases/bot-performance.use-case.ts`: estado list, loading, error; load(params).
- [ ] `presentation/pages/analytics/bot-performance/` o sección en analytics: tabla o cards por cliente/número con métricas; date range; solo visible para super_admin (PermissionService).
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_fetch_bot_performance_metrics` | `infrastructure/adapters/metrics.adapter.spec.ts` | GET bot-performance retorna BotPerformanceMetrics[] |
| `should_filter_by_client_id` | `infrastructure/adapters/metrics.adapter.spec.ts` | Query param clientId filtra resultados |
| `should_load_performance_data` | `application/use-cases/bot-performance.use-case.spec.ts` | Use case carga datos y actualiza signals |
| `should_handle_empty_performance_data` | `application/use-cases/bot-performance.use-case.spec.ts` | Sin datos → lista vacía, "Sin datos" en UI |
| `should_render_performance_table` | `presentation/pages/analytics/bot-performance.component.spec.ts` | Tabla con cliente, bot conversations, takeover rate |
| `should_show_date_range_picker` | `presentation/pages/analytics/bot-performance.component.spec.ts` | Filtro por período funcional |
| `should_only_show_for_super_admin` | `presentation/pages/analytics/bot-performance.component.spec.ts` | Componente oculto si no es super_admin |
| `should_show_skeleton_while_loading` | `presentation/pages/analytics/bot-performance.component.spec.ts` | Skeleton durante carga |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_get_bot_performance_by_org` | `tests/unit/controllers/test_bot_metrics_controller.py` | GET retorna métricas por cliente/número |
| `test_get_bot_performance_by_client` | `tests/unit/controllers/test_bot_metrics_controller.py` | Filtro por clientId funciona |
| `test_calculate_takeover_rate` | `tests/unit/services/test_bot_metrics_service.py` | Tasa de escalamiento calculada correctamente |
| `test_calculate_bot_response_time` | `tests/unit/services/test_bot_metrics_service.py` | Tiempo promedio de respuesta del bot correcto |
| `test_requires_super_admin` | `tests/unit/controllers/test_bot_metrics_controller.py` | 403 si no es super_admin |
| `test_log_bot_responded_event` | `tests/unit/services/test_bot_event_service.py` | Evento bot_responded registrado correctamente |
| `test_log_human_takeover_event` | `tests/unit/services/test_bot_event_service.py` | Evento human_takeover registrado correctamente |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_load_and_display_bot_metrics` | Frontend | Carga → tabla con datos por cliente → filtros funcionan |
| `should_filter_by_period_and_client` | Frontend | Cambiar período y cliente → datos actualizados |
| `test_bot_metrics_aggregation` | Backend | Eventos registrados → GET metrics → valores agregados correctos |
| `test_takeover_rate_calculation_accuracy` | Backend | 10 conversations, 3 takeovers → rate 30% correcto |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `MetricsAdapter` (bot performance) | ≥ 98% |
| `BotPerformanceUseCase` | ≥ 98% |
| `BotPerformanceComponent` | ≥ 98% |
| `BotMetricsService` (backend) | ≥ 98% |
| `BotEventService` (backend) | ≥ 98% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-015 (métricas base), HU-MFW-012/013 (eventos de bot y take-over).  
**Bloquea a:** Ninguna crítica.

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 5  
**Tiempo estimado:** 3–4 días  

---

## 📝 Notas Técnicas

- Backend debe registrar eventos "bot responded" y "human took over" para calcular tasas.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Eventos de bot (respuesta, escalamiento) no registrados en backend | Alta | Alto | Requerir que covacha-botIA y sp_webhook logueen eventos (bot_responded, human_takeover) en tabla de eventos; sin eventos, no hay métricas |
| Métricas de satisfacción no disponibles (no hay encuestas post-conversación) | Media | Medio | Para MVP, omitir satisfacción; planear HU futura para encuestas post-conversación; usar 'tasa de resolución' como proxy |
| Comparación entre clientes sin contexto (volúmenes muy diferentes) | Baja | Bajo | Mostrar métricas absolutas Y porcentuales; permitir ordenar por cualquier columna |

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

`user-story` `epic-5` `backend` `frontend` `priority:medium` `size:L`
