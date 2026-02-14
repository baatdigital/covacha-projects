## 📖 Historia de Usuario

**Como** usuario de WhatsApp Business con conversaciones sensibles
**Quiero** ocultar una conversacion con un codigo privado y que en su lugar se muestre una conversacion de negocio simulada
**Para** proteger mi privacidad y que nadie pueda ver el contenido real sin mi autorizacion

---

## 🎯 Criterios de Aceptacion

### Activar modo privado

- [ ] **C1.** En la vista de conversacion (header del chat), existe un boton/icono discreto (ej. candado) para activar el "modo privado" en esa conversacion; al pulsarlo se solicita crear un codigo PIN de 4-6 digitos (solo la primera vez); las siguientes veces solo se pide confirmar.
- [ ] **C2.** Al activar el modo privado en una conversacion, la conversacion real se oculta inmediatamente y en su lugar se muestra una conversacion de negocio generada automaticamente (mensajes predefinidos de tipo "Hola, gracias por contactarnos", confirmaciones de pedido, etc.).
- [ ] **C3.** La conversacion aparece en la lista con apariencia 100% normal (mismo contacto, mismo avatar); no debe haber ninguna indicacion visual de que esta en modo privado (ni iconos, ni colores, ni badges).

### Desactivar modo privado (ver conversacion real)

- [ ] **C4.** Para ver la conversacion real, el usuario debe ingresar su codigo PIN privado; puede hacerlo desde un gesto discreto (ej. long-press en el nombre del contacto, o triple-tap en el header) que abre un dialogo de PIN.
- [ ] **C5.** Al ingresar el PIN correcto, se muestra la conversacion real completa (todos los mensajes reales) reemplazando la conversacion simulada; el modo privado queda desactivado temporalmente.
- [ ] **C6.** Despues de 3 intentos fallidos de PIN, el dialogo se bloquea por 60 segundos; mostrar temporizador de espera.

### Auto-bloqueo

- [ ] **C7.** Si el usuario sale de la conversacion (navega a otra, cierra la app, o pasa a background) y la conversacion estaba desbloqueada, automaticamente vuelve al modo privado (muestra la conversacion de negocio).
- [ ] **C8.** Timeout configurable: si no hay interaccion en X minutos (default 2 min), la conversacion vuelve automaticamente a modo privado.

### Conversacion de negocio simulada

- [ ] **C9.** La conversacion simulada tiene al menos 8-12 mensajes de aspecto profesional/comercial (confirmaciones de pedido, preguntas de catalogo, agradecimientos, horarios de atencion); los mensajes tienen timestamps coherentes (ultimos 2-3 dias).
- [ ] **C10.** Existe al menos 3 plantillas de conversacion de negocio diferentes; el sistema asigna una aleatoriamente al activar el modo privado (para que no todas las conversaciones ocultas se vean iguales).
- [ ] **C11.** La conversacion simulada es de solo lectura; si el usuario intenta enviar un mensaje estando en modo privado, se muestra un toast discreto "Desbloquea para enviar mensajes".

### Gestion de conversaciones privadas

- [ ] **C12.** El usuario puede desactivar permanentemente el modo privado de una conversacion (desde el menu de la conversacion > "Quitar proteccion"); requiere ingresar el PIN.
- [ ] **C13.** El usuario puede cambiar su PIN privado desde Configuracion del modulo (requiere ingresar PIN actual primero).
- [ ] **C14.** Si el usuario olvida su PIN, puede resetearlo verificando su identidad (email OTP o biometrico si esta disponible); esto desprotege todas las conversaciones.

---

## ⚡ Requisitos No Funcionales

| Categoria | Requisito |
|-----------|-----------|
| **Seguridad** | PIN almacenado con hash (SHA-256 + salt) en localStorage cifrado; nunca en texto plano; los mensajes reales NO se eliminan, solo se ocultan en la UI; el flag de "conversacion privada" se almacena localmente, no se envia al backend |
| **Performance** | Cambio entre conversacion real y simulada < 200ms; sin parpadeo ni recarga visible |
| **UX** | El modo privado debe ser completamente invisible para un observador casual; no debe haber ninguna forma de detectar que una conversacion esta protegida sin conocer el gesto + PIN |
| **Accesibilidad** | Dialogo de PIN navegable por teclado; labels para screen readers (pero discretos) |
| **Compatibilidad** | Chrome 90+, Firefox 90+, Safari 15+, Edge 90+ |
| **Observabilidad** | Logs locales (debug only) para troubleshooting; errores de PIN capturados localmente; NO se loguea al backend que conversaciones estan en modo privado |

---

## 📋 Tareas Tecnicas

**Frontend (Hexagonal):**

- [ ] `domain/models/private-chat.model.ts`: interfaces `PrivateChatConfig`, `SimulatedConversation`, `PinState`; tipos para templates de conversacion simulada.
- [ ] `domain/ports/private-chat.port.ts`: `PrivateChatPort` con metodos: `activatePrivateMode(contactId, pin)`, `deactivatePrivateMode(contactId, pin)`, `verifyPin(pin)`, `isPrivateChat(contactId)`, `getSimulatedConversation(contactId)`, `changePin(oldPin, newPin)`, `resetPin(verificationToken)`.
- [ ] `infrastructure/adapters/private-chat.adapter.ts`: implementacion usando localStorage cifrado; gestion de hash de PIN con Web Crypto API; almacenamiento de config de conversaciones privadas.
- [ ] `application/use-cases/toggle-private-mode.use-case.ts`: logica de activar/desactivar; manejo de intentos fallidos y bloqueo temporal.
- [ ] `application/use-cases/verify-private-pin.use-case.ts`: verificacion de PIN con throttling de intentos.
- [ ] `presentation/components/private-chat-toggle/private-chat-toggle.component.ts`: boton discreto en el header del chat; icono de candado sutil.
- [ ] `presentation/components/pin-dialog/pin-dialog.component.ts`: dialogo de ingreso de PIN (crear/verificar); teclado numerico; indicador de intentos restantes; temporizador de bloqueo.
- [ ] `presentation/components/simulated-conversation/simulated-conversation.component.ts`: renderiza la conversacion de negocio falsa con aspecto identico a una real.
- [ ] `core/services/private-chat-crypto.service.ts`: hashing de PIN con Web Crypto API (SHA-256 + salt); cifrado/descifrado de config en localStorage.
- [ ] `core/services/auto-lock.service.ts`: servicio que detecta inactividad y navegacion fuera del chat para re-activar modo privado automaticamente.
- [ ] `core/data/simulated-templates.ts`: 3+ plantillas de conversaciones de negocio simuladas con mensajes realistas.
- [ ] **Tests:** Ver seccion [Plan de Pruebas](#-plan-de-pruebas) para detalle completo.

**NO requiere Backend** (toda la logica es local/cliente):
- PIN y configuracion se almacenan en localStorage del navegador
- Los mensajes reales permanecen intactos en el backend
- Solo la capa de presentacion decide que mostrar

---

## 🧪 Plan de Pruebas

### Tests Unitarios - Frontend

| Test | Archivo | Descripcion |
|------|---------|-------------|
| `should_activate_private_mode` | `infrastructure/adapters/private-chat.adapter.spec.ts` | Activar modo privado almacena config en localStorage |
| `should_hash_pin_with_salt` | `infrastructure/adapters/private-chat.adapter.spec.ts` | PIN se almacena como hash SHA-256, nunca en texto plano |
| `should_verify_correct_pin` | `application/use-cases/verify-private-pin.use-case.spec.ts` | PIN correcto → retorna true, resetea intentos |
| `should_reject_wrong_pin` | `application/use-cases/verify-private-pin.use-case.spec.ts` | PIN incorrecto → retorna false, incrementa intentos |
| `should_block_after_3_failures` | `application/use-cases/verify-private-pin.use-case.spec.ts` | 3 intentos fallidos → bloqueo 60s, retorna error con tiempo restante |
| `should_show_simulated_when_private` | `presentation/components/simulated-conversation/simulated-conversation.component.spec.ts` | Conversacion privada activa → muestra mensajes simulados |
| `should_show_real_when_unlocked` | `presentation/components/simulated-conversation/simulated-conversation.component.spec.ts` | Conversacion desbloqueada → muestra mensajes reales |
| `should_auto_lock_on_navigate` | `core/services/auto-lock.service.spec.ts` | Navegacion fuera del chat → re-activa modo privado |
| `should_auto_lock_on_timeout` | `core/services/auto-lock.service.spec.ts` | Inactividad 2 min → re-activa modo privado |
| `should_block_send_in_private` | `presentation/components/simulated-conversation/simulated-conversation.component.spec.ts` | Intento de enviar mensaje en modo privado → toast "Desbloquea para enviar" |
| `should_change_pin` | `application/use-cases/toggle-private-mode.use-case.spec.ts` | Cambio de PIN: verifica PIN actual, actualiza hash |
| `should_render_no_visual_hint` | `presentation/components/private-chat-toggle/private-chat-toggle.component.spec.ts` | Conversacion privada en lista: sin iconos ni indicadores visibles |

### Tests de Integracion

| Test | Descripcion |
|------|-------------|
| `full_flow_activate_verify_deactivate` | Flujo completo: activar → ver simulada → ingresar PIN → ver real → salir → ver simulada |
| `pin_reset_flow` | Olvidar PIN → verificar identidad → desproteger todas las conversaciones |

---

## 🔗 Dependencias

| Tipo | Detalle |
|------|---------|
| **Requiere** | HU-MFW-007 (Chat funcional con mensajes) |
| **Requiere** | HU-MFW-009 (Envio de mensajes) |
| **Independiente de** | Backend (toda la logica es cliente-side) |

---

## 📊 Estimacion

| Aspecto | Valor |
|---------|-------|
| **Complejidad** | Alta |
| **Story Points** | 13 pts |
| **Tiempo estimado** | 2-3 semanas |
| **Riesgo principal** | UX: que el modo privado sea realmente invisible y no afecte la experiencia normal |

---

## ✅ Definition of Done

- [ ] Todos los criterios de aceptacion verificados
- [ ] Tests unitarios con coverage >= 98%
- [ ] Build de produccion exitoso
- [ ] PIN almacenado con hash, nunca en texto plano
- [ ] Cambio entre modo real y simulado sin parpadeo
- [ ] No existe forma visual de detectar conversaciones protegidas
- [ ] Auto-bloqueo funcional al salir o por inactividad
- [ ] Al menos 3 plantillas de conversacion simulada
- [ ] Documentacion de la feature en CLAUDE.md
