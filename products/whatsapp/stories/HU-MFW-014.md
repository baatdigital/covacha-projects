## 📖 Historia de Usuario

**Como** administrador de cliente  
**Quiero** configurar horarios de operación para las respuestas automáticas  
**Para** que el bot solo responda en horarios de atención al cliente  

---

## 🎯 Criterios de Aceptación

- [ ] **C1.** En la configuración de automatización (junto a HU-MFW-011) hay una sección “Horarios de atención” o “Horario del bot”: el usuario puede definir días de la semana y rango de horas (inicio–fin) en que el bot debe responder.
- [ ] **C2.** Fuera del horario configurado, el bot no envía respuestas automáticas; los mensajes entrantes se almacenan y se muestran en la bandeja para atención manual (sin cambiar el flujo existente de mensajes).
- [ ] **C3.** Se permite configurar distintos horarios por día (ej. Lun–Vie 9–18, Sáb 9–13) o un horario único para todos los días; la zona horaria puede ser la del tenant o seleccionable (ej. America/Mexico_City).
- [ ] **C4.** La configuración se guarda por número (phoneNumberId); al cambiar de número en el selector se muestra y edita el horario de ese número.
- [ ] **C5.** Validación: hora fin > hora inicio; al menos un día con al menos un rango; se muestra error si la configuración es inválida.
- [ ] **C6.** Opción “24 horas” (bot siempre activo en horario) para no tener que rellenar todos los días; y opción “Desactivado” (solo manual).
- [ ] **C7.** En la UI del chat o en configuración, indicador “Bot activo en horario de atención” / “Fuera de horario (solo manual)” según hora actual y configuración.

---

## ⚡ Requisitos No Funcionales

| Categoría | Requisito |
|-----------|-----------|
| **Performance** | Carga de configuración de horario < 500ms; guardado < 1s |
| **Accesibilidad** | WCAG 2.1 AA; navegación por teclado; labels para screen readers |
| **Seguridad** | Timezone validado contra lista IANA; horarios validados en backend (no confiar solo en frontend); config solo modificable por admin con permiso |
| **Observabilidad** | Logs de error en consola con contexto; errores capturados por Sentry |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |

---

## 📋 Tareas Técnicas

**Backend:**
- [ ] Modelo de horario: por phoneNumberId, timezone, schedule: array de { dayOfWeek, startTime, endTime } o 24h flag; GET/PUT en mismo endpoint de automatización o específico; la lógica de "dentro/fuera de horario" se evalúa en el backend al recibir mensaje; documentar.

**Frontend (Hexagonal):**
- [ ] `domain/models/automation.model.ts`: ScheduleSlot (dayOfWeek, startTime, endTime); AutomationConfig extender con schedule?: ScheduleSlot[], timezone?: string, schedule24h?: boolean.
- [ ] Port y adapter: get/save config ya incluyen schedule; o endpoints específicos getSchedule/saveSchedule.
- [ ] `application/use-cases/automation-config.use-case.ts`: extender para cargar y guardar schedule; validación día/hora.
- [ ] UI: sección “Horario del bot”; selector de zona horaria (dropdown común); por cada día: checkbox “Activo”, hora inicio, hora fin (time inputs o selects); opción “24 horas”; opción “Solo manual (desactivar bot en horario)”; botón Guardar.
- [ ] Indicador en tiempo real: “En horario” / “Fuera de horario” según hora actual del cliente y timezone guardado (cálculo en frontend para mostrar; la decisión real la hace el backend).
- [ ] **Tests:** Ver sección [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `should_load_schedule_config` | `infrastructure/adapters/automation.adapter.spec.ts` | GET retorna schedule con days, times, timezone |
| `should_save_schedule_config` | `infrastructure/adapters/automation.adapter.spec.ts` | PUT envía schedule payload correctamente |
| `should_validate_end_time_after_start` | `application/use-cases/automation-config.use-case.spec.ts` | Error si endTime <= startTime para cualquier día |
| `should_validate_at_least_one_day_active` | `application/use-cases/automation-config.use-case.spec.ts` | Error si ningún día tiene horario activo (excepto 24h o desactivado) |
| `should_render_day_schedule_form` | `presentation/pages/automation/schedule.component.spec.ts` | Formulario con checkboxes por día y time inputs |
| `should_render_timezone_selector` | `presentation/pages/automation/schedule.component.spec.ts` | Dropdown de timezone con lista IANA |
| `should_show_24h_option` | `presentation/pages/automation/schedule.component.spec.ts` | Toggle "24 horas" oculta detalle por día |
| `should_show_disabled_option` | `presentation/pages/automation/schedule.component.spec.ts` | Opción "Manual only" desactiva todo schedule |
| `should_show_schedule_presets` | `presentation/pages/automation/schedule.component.spec.ts` | Presets L-V 9-18, L-S 9-14, 24/7, Personalizado |
| `should_show_in_out_of_hours_indicator` | `presentation/pages/automation/schedule.component.spec.ts` | Indicador "En horario" / "Fuera de horario" según hora actual y config |

### Tests Unitarios - Backend

| Test | Archivo | Descripción |
|------|---------|-------------|
| `test_save_schedule_config` | `tests/unit/controllers/test_automation_controller.py` | PUT guarda schedule en DynamoDB por phoneNumberId |
| `test_validate_timezone_iana` | `tests/unit/services/test_schedule_service.py` | Timezone inválido retorna 400 |
| `test_validate_time_ranges` | `tests/unit/services/test_schedule_service.py` | endTime <= startTime retorna 400 |
| `test_evaluate_schedule_in_hours` | `tests/unit/services/test_schedule_service.py` | Función retorna true cuando hora actual está dentro de horario |
| `test_evaluate_schedule_out_of_hours` | `tests/unit/services/test_schedule_service.py` | Función retorna false cuando hora actual está fuera de horario |
| `test_evaluate_schedule_with_timezone` | `tests/unit/services/test_schedule_service.py` | Evaluación correcta con timezone America/Mexico_City vs UTC |
| `test_bot_responds_in_schedule` | `tests/unit/services/test_auto_response_service.py` | Dentro de horario + automation enabled → bot responde |
| `test_bot_silent_out_of_schedule` | `tests/unit/services/test_auto_response_service.py` | Fuera de horario → no respuesta automática |
| `test_24h_schedule_always_responds` | `tests/unit/services/test_auto_response_service.py` | Config 24h → bot siempre responde cuando enabled |

### Tests de Integración

| Test | Tipo | Descripción |
|------|------|-------------|
| `should_configure_save_and_reload_schedule` | Frontend | Configurar horario → guardar → recargar → valores persistidos |
| `should_show_correct_indicator_based_on_time` | Frontend | Indicador cambia según hora actual y timezone configurado |
| `test_schedule_evaluation_end_to_end` | Backend | Guardar schedule → webhook mensaje → evaluación de horario → respuesta o silencio |
| `test_schedule_timezone_handling` | Backend | Schedule en America/Mexico_City evaluado correctamente con server en UTC |

### Cobertura Esperada

| Componente | Cobertura mínima |
|-----------|-----------------|
| `AutomationAdapter` (schedule) | ≥ 98% |
| `AutomationConfigUseCase` (schedule) | ≥ 98% |
| `ScheduleComponent` | ≥ 98% |
| `ScheduleService` (backend) | ≥ 98% |
| `AutoResponseService` (schedule) | ≥ 98% |

---

## 🔗 Dependencias

**Depende de:** HU-MFW-011 (configuración automatización).  
**Bloquea a:** Ninguna crítica.

---

## 📊 Estimación

**Complejidad:** Media  
**Puntos de Historia:** 5  
**Tiempo estimado:** 3 días  

---

## 📝 Notas Técnicas

- Backend debe evaluar timezone y horario en cada mensaje entrante; evitar dependencia solo de hora del servidor.

---

## ⚠️ Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Desfase de timezone entre servidor y cliente | Alta | Alto | Siempre guardar y evaluar en UTC con timezone explícito (IANA); backend convierte; UI muestra hora local del timezone seleccionado |
| Bot responde fuera de horario por latencia en evaluación | Media | Medio | Evaluación de horario en backend al procesar cada mensaje (no en cron); cache de schedule config con TTL corto (1min) |
| UI de configuración de días compleja y confusa | Media | Bajo | Ofrecer presets (L-V 9-18, L-S 9-14, 24/7, Personalizado); solo mostrar detalle por día si elige Personalizado |

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

`user-story` `epic-4` `backend` `frontend` `priority:medium` `size:L`
