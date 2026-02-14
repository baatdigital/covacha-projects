# HU-MFW-019: Bloqueo de Pantalla por Inactividad

## EP-MFW-006: Conversaciones Privadas y Proteccion de Privacidad

## Historia de Usuario

**Como** usuario de WhatsApp Business que maneja conversaciones con informacion sensible de clientes
**Quiero** que la pantalla del modulo se bloquee automaticamente despues de 5 minutos de inactividad
**Para** proteger la privacidad de las conversaciones si me alejo del equipo sin cerrar sesion

---

## Criterios de Aceptacion

### Deteccion de inactividad

- [ ] **C1.** El sistema detecta inactividad del usuario considerando: movimiento de mouse, clicks, teclas presionadas, scroll y toques en pantalla tactil; si ninguno de estos eventos ocurre en 5 minutos continuos, se activa el bloqueo.
- [ ] **C2.** El temporizador de inactividad se reinicia completamente ante cualquier interaccion del usuario.
- [ ] **C3.** El temporizador de inactividad se pausa cuando la pestana/ventana pierde el foco (visibilitychange) y al regresar evalua el tiempo total transcurrido; si supera los 5 minutos, bloquea inmediatamente.

### Pantalla de bloqueo

- [ ] **C4.** Al activarse el bloqueo, se muestra una overlay de pantalla completa (z-index maximo) que cubre todo el contenido del modulo WhatsApp; el contenido de conversaciones no debe ser visible detras de la overlay (ni con scroll, ni con DevTools inspect casual).
- [ ] **C5.** La pantalla de bloqueo muestra: logo de SuperPago, mensaje "Sesion bloqueada por inactividad", campo de PIN o contrasena para desbloquear, y hora actual.
- [ ] **C6.** La pantalla de bloqueo tiene un fondo solido (no transparente ni blur) para garantizar que no se vea el contenido detras.

### Desbloqueo

- [ ] **C7.** El usuario puede desbloquear ingresando su PIN de privacidad (si ya configuro uno en HU-MFW-018) o su contrasena de sesion; al ingresar correctamente, la overlay desaparece y se muestra el estado exacto en que estaba antes del bloqueo.
- [ ] **C8.** Despues de 5 intentos fallidos de desbloqueo, la sesion se cierra automaticamente (redirect a login) y se muestra un toast informativo.
- [ ] **C9.** Existe un enlace "Cerrar sesion" visible en la pantalla de bloqueo para que el usuario pueda salir sin desbloquear.

### Configuracion

- [ ] **C10.** El tiempo de inactividad es configurable por el usuario desde la configuracion del modulo: opciones de 1, 2, 5 (default), 10 y 15 minutos.
- [ ] **C11.** El usuario puede desactivar el bloqueo por inactividad (toggle off); al desactivar se muestra un aviso de seguridad: "Desactivar el bloqueo automatico reduce la proteccion de tus conversaciones".
- [ ] **C12.** La configuracion de tiempo e toggle se persiste en localStorage y sobrevive al cierre de pestana.

### Integracion con el modulo

- [ ] **C13.** El bloqueo aplica solo al modulo mf-whatsapp, no afecta al Shell ni a otros micro-frontends.
- [ ] **C14.** Si el usuario navega fuera del modulo WhatsApp y regresa despues de que el tiempo de inactividad haya expirado, se muestra la pantalla de bloqueo inmediatamente.
- [ ] **C15.** El bloqueo es compatible con el modo privado de conversaciones (HU-MFW-018): si una conversacion estaba desbloqueada (PIN ingresado), al activarse el bloqueo de pantalla tambien se reactiva el modo privado de esa conversacion.

---

## Requisitos No Funcionales

| Categoria | Requisito |
|-----------|-----------|
| **Performance** | Listener de eventos con throttle (1s) para no impactar rendimiento |
| **Seguridad** | Overlay no bypasseable con CSS/JS casual; contenido no accesible via DOM mientras esta bloqueado |
| **UX** | Transicion suave (fade 300ms) al bloquear; desbloqueo instantaneo |
| **Accesibilidad** | Campo de PIN/contrasena con autofocus; navegable por teclado; label accesible |
| **Memoria** | El timer usa un solo `setTimeout` reciclable, no `setInterval`; se limpia en `ngOnDestroy` |

---

## Tareas Tecnicas

**Frontend (Hexagonal):**

- [ ] `domain/models/screen-lock.model.ts` - Interfaces ScreenLockConfig, ScreenLockState
- [ ] `domain/ports/screen-lock.port.ts` - Interface ScreenLockPort
- [ ] `infrastructure/adapters/screen-lock.adapter.ts` - Implementacion con localStorage
- [ ] `application/use-cases/lock-screen.use-case.ts` - Logica de bloqueo/desbloqueo
- [ ] `application/services/inactivity-detector.service.ts` - Deteccion de eventos, temporizador
- [ ] `presentation/components/screen-lock-overlay/screen-lock-overlay.component.ts` - Overlay UI
- [ ] `presentation/components/lock-settings/lock-settings.component.ts` - Configuracion de tiempo/toggle
- [ ] Integrar detector de inactividad en `RemoteEntryComponent`
- [ ] Tests unitarios para inactivity-detector.service (6+)
- [ ] Tests unitarios para lock-screen.use-case (4+)
- [ ] Tests unitarios para screen-lock-overlay.component (4+)
- [ ] Test E2E `tests/e2e/ep-006-privacidad/hu-019-screen-lock.spec.ts`

---

## Dependencias

| Tipo | Detalle |
|------|---------|
| **Opcional** | HU-MFW-018 (PIN de privacidad) - Si existe, reutilizar PIN; si no, usar contrasena de sesion |
| **Desbloquea** | Ninguna |

---

## Estimacion

| Aspecto | Valor |
|---------|-------|
| **Complejidad** | Media |
| **Puntos** | 5 |
| **Archivos nuevos** | 7-8 |
| **Archivos modificados** | 2-3 |

---

## Definition of Done

- [ ] Todos los criterios de aceptacion verificados
- [ ] Tests unitarios >= 98% cobertura en archivos nuevos
- [ ] Test E2E pasando
- [ ] Build de produccion exitoso (`yarn build:prod`)
- [ ] Sin errores de lint
- [ ] PR aprobado y mergeado a develop
