## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** configurar respuestas automáticas para mi número de WhatsApp  
**Para** atender consultas básicas sin intervención manual  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** Existe una sección o página “Automatización” (o “Respuestas automáticas”) accesible desde el menú del cliente o desde la vista de chat; solo para usuarios con permiso de administrar automatización.
- [ ] **C2.** El usuario puede activar/desactivar “respuestas automáticas” por número de WhatsApp (toggle global por número); cuando está activo, el backend (o covacha-botIA) responde según reglas configuradas.
- [ ] **C3.** El usuario puede configurar al menos un mensaje de bienvenida o respuesta automática simple: texto libre (y opcionalmente palabras clave que disparen la respuesta); guardado en backend y aplicado cuando la automatización está activa.
- [ ] **C4.** La configuración se guarda por número (phoneNumberId); al cambiar de número en el selector se muestra la configuración de ese número.
- [ ] **C5.** Validación: mensaje de respuesta no vacío; longitud máxima según límites de WhatsApp (ej. 4096 caracteres); se muestra error claro si falla la validación o el guardado.
- [ ] **C6.** Indicador en la UI del chat (o en el encabezado del número) que muestre si la automatización está “Activa” o “Inactiva” para el número actual.
- [ ] **C7.** Documentación breve en la misma pantalla: qué son las respuestas automáticas y que pueden complementarse con un agente IA (HU-MFW-012).

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Carga de config por número < 500ms; guardado < 1s con feedback visual |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Solo usuarios con permiso de automatización pueden modificar config; validación de longitud en backend también (no solo frontend); XSS en mensaje de bienvenida prevenido |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Endpoints (o uso de existentes): GET/PUT configuración de automatización por phoneNumberId (activo: boolean, welcomeMessage?: string, keywords?: string[]); persistencia en DynamoDB o en sp_webhook/covacha-botIA; documentar.

**Frontend (Hexagonal):**
- [ ] `domain/models/automation.model.ts`: AutomationConfig (phoneNumberId, enabled, welcomeMessage?, keywordResponses?).
- [ ] `domain/ports/automation.port.ts`: getConfig(orgId, phoneNumberId), saveConfig(orgId, phoneNumberId, config).
- [ ] `infrastructure/adapters/automation.adapter.ts`: GET/PUT a endpoints documentados.
- [ ] `application/use-cases/automation-config.use-case.ts`: estado config, loading, error; load(phoneNumberId), save(config); validación de longitud y no vacío antes de guardar.
- [ ] `presentation/pages/automation/` o sección en configuración: formulario con toggle “Activar respuestas automáticas”, textarea “Mensaje de bienvenida/respuesta”, botón Guardar; selector de número si hay varios.
- [ ] Mostrar en chat o header: badge “Automación activa” / “Inactiva” según config cargada.
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_load_automation_config_for_number` | `infrastructure/adapters/automation.adapter.spec.ts` | GET config retorna enabled, welcomeMessage, keywords por phoneNumberId |
| `should_save_automation_config` | `infrastructure/adapters/automation.adapter.spec.ts` | PUT config envía payload correcto al endpoint |
| `should_validate_message_not_empty` | `application/use-cases/automation-config.use-case.spec.ts` | No permite guardar con mensaje de bienvenida vacío |
| `should_validate_message_max_length` | `application/use-cases/automation-config.use-case.spec.ts` | Error si mensaje > 4096 caracteres |
| `should_update_config_signal_on_load` | `application/use-cases/automation-config.use-case.spec.ts` | Signals config, loading, error se actualizan correctamente |
| `should_toggle_automation_enabled` | `presentation/pages/automation/automation.component.spec.ts` | Toggle activa/desactiva automatización |
| `should_show_automation_active_badge` | `presentation/pages/automation/automation.component.spec.ts` | Badge "Automación activa" visible cuando enabled |
| `should_show_config_form` | `presentation/pages/automation/automation.component.spec.ts` | Formulario con toggle, textarea, keywords visibles |
| `should_disable_save_when_invalid` | `presentation/pages/automation/automation.component.spec.ts` | Botón guardar deshabilitado con validación fallida |
| `should_show_tooltip_when_config_exists_but_disabled` | `presentation/pages/automation/automation.component.spec.ts` | Tooltip "Configuración lista, activa para aplicar" cuando config guardada pero toggle off |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_get_automation_config` | `tests/unit/controllers/test_automation_controller.py` | GET retorna config por phoneNumberId |
| `test_save_automation_config` | `tests/unit/controllers/test_automation_controller.py` | PUT guarda config en DynamoDB |
| `test_save_validates_message_length` | `tests/unit/services/test_automation_service.py` | Mensaje > 4096 chars retorna 400 |
| `test_save_validates_message_not_empty_when_enabled` | `tests/unit/services/test_automation_service.py` | Config enabled sin mensaje retorna 400 |
| `test_auto_response_triggered_when_enabled` | `tests/unit/services/test_auto_response_service.py` | Mensaje entrante + config enabled → respuesta automática enviada |
| `test_auto_response_not_triggered_when_disabled` | `tests/unit/services/test_auto_response_service.py` | Mensaje entrante + config disabled → sin respuesta automática |
| `test_keyword_matching` | `tests/unit/services/test_auto_response_service.py` | Mensaje con keyword configurado → respuesta específica |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_load_save_and_display_config` | Frontend | Cargar config → editar → guardar → recargar → valores persistidos |
| `should_toggle_and_persist_automation_state` | Frontend | Toggle on → guardar → badge actualizado → reload mantiene estado |
| `test_auto_response_end_to_end` | Backend | Config guardada → webhook mensaje entrante → respuesta automática enviada |
| `test_config_isolation_per_phone_number` | Backend | Config de número A no afecta número B |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `AutomationAdapter` | ≥ 98% |
| `AutomationConfigUseCase` | ≥ 98% |
| `AutomationComponent` | ≥ 98% |
| `AutomationService` (backend) | ≥ 98% |
| `AutoResponseService` (backend) | ≥ 98% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-007/008 (contexto de número), backend con modelo de configuración.  
**Bloquea a:** HU-MFW-012 (asignar agente IA), HU-MFW-014 (horarios).

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 5  
**Tiempo estimado:** 3 días  

---

## 📝 Notas Técnicas

- Si la lógica de "respuesta automática" vive en covacha-botIA, el backend de mf-whatsapp puede ser un proxy a esa API; el MF solo edita configuración.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Configuración de auto-respuesta aplicada a número equivocado | Media | Alto | Confirmar phoneNumberId antes de guardar; mostrar nombre/número en confirmación; test de integración con mock |
| covacha-botIA API no disponible o con contrato diferente | Media | Alto | Usar adapter con mock para desarrollo; documentar contrato esperado; feature flag para habilitar cuando API lista |
| Usuario configura auto-respuesta y olvida activar toggle | Alta | Bajo | UX: si hay config guardada pero toggle off, mostrar tooltip/badge 'Configuración lista, activa para aplicar' |

---

## ✅ Definición de Hecho (DoD)

- [ ] Código implementado según criterios de aceptación
- [ ] Tests unitarios (coverage >= 98% en código nuevo/modificado)
- [ ] Lint limpio (`ng lint` sin errores)
- [ ] Build exitoso (`yarn build:prod`)
- [ ] Sin errores en consola del navegador
- [ ] Documentación actualizada (CLAUDE.md si aplica)
- [ ] PR creado con descripción y linked issue
- [ ] Criterios de aceptación validados manualmente

---

## 🏷️ Labels

`user-story` `epic-4` `backend` `frontend` `priority:high` `size:L`
