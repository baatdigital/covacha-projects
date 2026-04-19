# Diseño: Generación Automática de Contenido para Promociones con IA

**Fecha:** 2026-04-19  
**Estado:** Aprobado  
**Repositorios afectados:** covacha-botia, covacha-core, mf-marketing, mf-settings  

---

## 1. Resumen Ejecutivo

Feature que permite, desde la vista de una promoción existente, generar automáticamente con un solo clic: estrategia de campaña, KPIs, copy para todos los formatos (carrusel, historia, imagen, Meta Ads, WhatsApp, email, guión de video), assets visuales en Canva, borrador de campaña en Meta Ads, y adición automática al funnel de WhatsApp y al funnel de email. Todo sin intervención manual tras el clic inicial.

### Decisiones de diseño clave
- **Canva:** OAuth por cliente — cada organización conecta su propia cuenta de Canva
- **IA:** One-shot automático — un clic genera todo en paralelo
- **Arquitectura:** Async — covacha-core coordina, covacha-botia ejecuta la IA, frontend hace polling
- **Agentes:** Pipeline orquestado — orchestrator central + 2 agentes nuevos + agentes existentes reutilizados
- **Funnels:** Dos funnels automáticos — WhatsApp y Email

---

## 2. Flujo Completo del Sistema

```
Usuario (mf-marketing)
  │
  ├─ Clic "✨ Generar con IA" en editor de promoción
  │
  ▼
covacha-core — POST /api/v1/agencies/{org_id}/promotions/{id}/generate-content
  │
  ├─ Crea GenerationJob en DynamoDB (status: pending)
  ├─ Responde inmediato: { job_id, status: "pending" }
  └─ Llama covacha-botia async: POST /api/v1/bots/promotion/generate
  
mf-marketing
  └─ Polling cada 3s: GET /api/v1/agencies/{org_id}/promotions/{id}/generation-status/{job_id}

covacha-botia — PromotionContentOrchestrator
  FASE 1 (en paralelo):
  ├─ strategy_planner (existente) → estrategia + KPIs + presupuesto
  ├─ copywriter_expert_agent (NUEVO) → copy carrusel, historia, imagen, WhatsApp, email, guión video
  └─ facebook_ads_expert_agent (NUEVO) → headline A/B, ad copy, config campaña, segmentación
  FASE 2 (secuencial, requiere output del copywriter):
  └─ canva_tool (nueva herramienta) → genera diseños en Canva del cliente vía OAuth token

covacha-botia → callback → covacha-core: POST /api/v1/internal/generation-complete
  │
covacha-core (acciones automáticas):
  ├─ Guarda todo el contenido generado en DynamoDB (ligado a la promoción)
  ├─ Programa posts en content_calendar con horarios sugeridos por IA
  ├─ Crea campaña en borrador en Meta Ads Manager
  ├─ Agrega mensaje al funnel de WhatsApp
  ├─ Agrega mensaje al funnel de Email
  └─ Actualiza job status: completed

mf-marketing
  └─ Detecta status: completed → muestra panel de resultados con tabs por formato
```

---

## 3. Agentes y Skills (covacha-botia)

### 3.1 copywriter_expert_agent (NUEVO)

**Tipo:** SPECIALIZED  
**Modelo:** claude-sonnet-4-20250514  
**Seed file:** `seed_copywriter_expert_agent.py`

**Responsabilidades:**
- Copy de carrusel: portada + 4-6 slides + CTA final
- Copy de historia (Story): texto + CTA + countdown si hay fecha límite
- Copy de imagen estática (feed)
- Mensaje de WhatsApp: versión corta y larga con emoji strategy
- Email completo: asunto, preview text, cuerpo, CTA
- Guión de video/Reels: escenas, narración, subtítulos

**Herramientas:** ninguna externa (solo generación de texto)

**System prompt core:**
> Eres un experto en copywriting digital especializado en mercados latinoamericanos. Generas copy persuasivo, auténtico y adaptado al tono de marca del cliente para cada formato de contenido. Siempre incluyes un CTA claro y adaptado al formato.

---

### 3.2 facebook_ads_expert_agent (NUEVO)

**Tipo:** SPECIALIZED  
**Modelo:** claude-sonnet-4-20250514  
**Seed file:** `seed_facebook_ads_expert_agent.py`

**Responsabilidades:**
- Headline principal + 2 variantes A/B
- Copy principal del anuncio
- Descripción y CTA button recomendado
- Configuración de campaña: objetivo (tráfico, conversiones, alcance), tipo de puja
- Segmentación sugerida: edades, intereses, geografía, comportamientos
- Presupuesto diario/total recomendado

**Herramientas:** ninguna externa (solo generación de configuración)

**System prompt core:**
> Eres un experto en Meta Ads (Facebook e Instagram) con amplia experiencia en el mercado mexicano y latinoamericano. Generas configuraciones de campaña optimizadas basadas en el objetivo de negocio, la audiencia target y el presupuesto disponible. Siempre propones variantes A/B para headlines.

---

### 3.3 PromotionContentOrchestrator (NUEVO)

**Archivo:** `application/services/promotion_content_orchestrator.py`

**Responsabilidades:**
- Recibe el payload completo de la promoción desde covacha-core
- Ejecuta en paralelo los 3 agentes (strategy_planner, copywriter_expert, facebook_ads_expert) — Fase 1
- Llama canva_tool con resultados del copywriter una vez completa Fase 1 — Fase 2 (secuencial)
- Agrega resultados en un payload unificado
- Llama callback de covacha-core con el resultado completo

**Input:**
```python
{
    "job_id": str,
    "org_id": str,
    "promotion": {
        "id": str,
        "title": str,
        "description": str,
        "category": str,
        "audience": str,
        "start_date": str,
        "end_date": str,
        "banner_text": str,
        "banner_cta": str,
        "theme": dict,
    },
    "canva_token": str,  # token OAuth del cliente (inyectado por covacha-core)
    "callback_url": str
}
```

**Output (al callback):**
```python
{
    "job_id": str,
    "status": "completed" | "failed",
    "result": {
        "strategy": { "objective", "audience", "kpis", "budget_recommendation" },
        "copy": {
            "carousel": { "cover", "slides": [...], "cta_slide" },
            "story": { "text", "cta", "countdown" },
            "static_image": { "headline", "body", "cta" },
            "whatsapp": { "short", "long" },
            "email": { "subject", "preview_text", "body", "cta" },
            "video_script": { "scenes": [...], "narration", "subtitles" }
        },
        "ads": {
            "headlines": [str, str, str],  # variantes A/B/C
            "primary_text": str,
            "description": str,
            "cta_button": str,
            "campaign_config": { "objective", "bidding", "daily_budget", "audience" }
        },
        "canva_assets": {
            "carousel_design_id": str,
            "carousel_export_url": str,
            "story_design_id": str,
            "story_export_url": str,
            "static_image_design_id": str,
            "static_image_export_url": str
        }
    },
    "error": str | None
}
```

---

### 3.4 canva_tool (NUEVA HERRAMIENTA)

**Archivo:** `application/services/canva_tool.py`

**Responsabilidades:**
- Autenticarse en Canva API usando el OAuth token del cliente
- Crear diseño de carrusel a partir del copy generado (template base + colores del theme de la promoción)
- Crear diseño de historia (9:16)
- Crear diseño de imagen feed (1:1)
- Exportar cada diseño como PNG y retornar URL de descarga

**Canva API endpoints usados:**
- `POST /v1/designs` — crear diseño desde template
- `POST /v1/designs/{id}/export` — exportar como PNG
- `GET /v1/exports/{id}` — polling hasta que export esté listo

---

## 4. Backend (covacha-core)

### 4.1 Nuevos Endpoints

```
POST   /api/v1/agencies/{org_id}/promotions/{promo_id}/generate-content
GET    /api/v1/agencies/{org_id}/promotions/{promo_id}/generation-status/{job_id}
POST   /api/v1/internal/generation-complete          (llamado por covacha-botia)

GET    /api/v1/integrations/canva/oauth/authorize    (redirect a Canva OAuth)
GET    /api/v1/integrations/canva/oauth/callback     (Canva callback con code)
GET    /api/v1/integrations/canva/status             (estado de conexión por org)
DELETE /api/v1/integrations/canva                    (desconectar)
```

### 4.2 Nuevos Archivos

| Archivo | Responsabilidad |
|---------|----------------|
| `controllers/promotion_generation_controller.py` | Maneja trigger de generación y polling de status |
| `controllers/canva_oauth_controller.py` | Maneja flujo OAuth con Canva |
| `services/promotion_generation_service.py` | Crea job, llama botia, ejecuta acciones post-generación |
| `services/canva_integration_service.py` | OAuth flow, token refresh, estado de conexión |
| `repositories/generation_job_repository.py` | CRUD de GenerationJob en DynamoDB |
| `repositories/canva_token_repository.py` | CRUD de CanvaToken en DynamoDB (tokens AES-encrypted) |
| `config/routes/promotion_generation.py` | Blueprint de generación |
| `config/routes/canva_oauth.py` | Blueprint de OAuth Canva |

### 4.3 promotion_generation_service.py — Flujo detallado

```python
def trigger_generation(org_id, promo_id, user_id) -> GenerationJob:
    # 1. Obtener promoción completa
    # 2. Obtener Canva token del cliente (si está conectado)
    # 3. Crear job en DynamoDB (status: pending)
    # 4. Llamar covacha-botia async (fire-and-forget con timeout 0)
    # 5. Retornar job_id

def handle_generation_complete(payload) -> None:
    # 1. Validar job_id
    # 2. Guardar contenido generado en DynamoDB (ligado a promoción)
    # 3. Programar posts en content_calendar (horarios sugeridos por IA)
    # 4. Crear campaña borrador en Meta Ads vía facebook_ads service
    # 5. Agregar al funnel de WhatsApp (mensaje generado)
    # 6. Agregar al funnel de Email (email generado)
    # 7. Actualizar job status: completed
```

### 4.4 Nuevas Variables de Entorno

```bash
CANVA_CLIENT_ID=
CANVA_CLIENT_SECRET=
CANVA_REDIRECT_URI=https://api.superpago.com.mx/api/v1/integrations/canva/callback
BOTIA_BASE_URL=http://localhost:5003  # o URL de producción
BOTIA_INTERNAL_SECRET=               # shared secret para validar callback de covacha-botia
DYNAMODB_GENERATION_JOBS_TABLE=modcore_generation_jobs_prod
DYNAMODB_CANVA_TOKENS_TABLE=modcore_canva_tokens_prod
```

---

## 5. Modelos de Datos (DynamoDB)

> **Regla arquitectónica del ecosistema:** Los modelos Pydantic y repositorios DynamoDB deben vivir en `covacha-libs`. Los repos `covacha-core` y `covacha-botia` solo definen servicios, controladores y rutas. Los modelos `GenerationJob` y `CanvaToken` deben crearse en `covacha-libs/covacha_libs/models/modcore/` y `covacha-libs/covacha_libs/repositories/modcore/` respectivamente.

### 5.1 modcore_generation_jobs_prod

```
PK: ORG#{org_id}
SK: JOB#{job_id}

Fields:
- job_id: str (UUID)
- org_id: str
- promotion_id: str
- status: "pending" | "processing" | "completed" | "failed"
- botia_job_id: str | None
- result: dict | None  (payload completo del contenido generado)
- error: str | None
- created_at: str (ISO 8601)
- updated_at: str (ISO 8601)
- created_by: str (user_id)

GSI1: PK=PROMO#{promotion_id}, SK=JOB#{created_at}  (para listar jobs por promoción)
```

### 5.2 modcore_canva_tokens_prod

```
PK: ORG#{org_id}
SK: CANVA#token

Fields:
- org_id: str
- access_token: str  (AES-encrypted, misma llave que CREDENTIALS_ENCRYPTION_KEY)
- refresh_token: str (AES-encrypted)
- expires_at: str (ISO 8601)
- canva_user_id: str
- canva_user_email: str
- connected_at: str (ISO 8601)
- connected_by: str (user_id)
```

---

## 6. Frontend (mf-marketing)

### 6.1 Nuevos Componentes

| Componente | Responsabilidad |
|-----------|----------------|
| `ai-generation-panel` | Panel lateral derecho en el editor de promoción. Muestra progreso y resultados con tabs. |
| `generation-progress` | Barra de progreso con 4 pasos: Estrategia → Copy → Assets Canva → Programando |
| `content-preview-card` | Card reutilizable para previsualizar cada pieza de contenido generada |

### 6.2 ai-generation.service.ts

```typescript
triggerGeneration(orgId: string, promoId: string): Observable<GenerationJob>
pollStatus(orgId: string, promoId: string, jobId: string): Observable<GenerationJob>
// Polling con interval(3000) + takeUntil status === 'completed' | 'failed'
```

### 6.3 Integración en promotion-editor-page

- Botón `✨ Generar con IA` junto al botón Guardar
- Al hacer clic: llama `triggerGeneration()`, abre panel lateral con progress
- Panel lateral usa `pollStatus()` hasta completar
- Al completar: muestra tabs con el contenido generado
- Cada tab tiene botón "Editar en Canva" (abre diseño en Canva del cliente) y "Programado" (badge)

---

## 7. Frontend (mf-settings)

### 7.1 Nueva Página: Integraciones

**Ruta:** `/settings/integrations`

**Archivo:** `presentation/pages/integrations/integrations.component.ts`

**Cards de integración:**
- **Canva** — estado conectado/desconectado, botón "Conectar" (OAuth redirect) o "Desconectar"
- **Meta** (ya existente, mover aquí si aplica)

### 7.2 canva-integration.service.ts

```typescript
getStatus(orgId: string): Observable<CanvaConnectionStatus>
getOAuthUrl(orgId: string): Observable<{ url: string }>
disconnect(orgId: string): Observable<void>
```

---

## 8. Seguridad

- Tokens Canva almacenados AES-encrypted en DynamoDB (misma llave `CREDENTIALS_ENCRYPTION_KEY` ya usada para otras credenciales)
- El endpoint interno `/api/v1/internal/generation-complete` requiere un shared secret entre covacha-core y covacha-botia (`BOTIA_INTERNAL_SECRET` env var)
- El Canva OAuth token se inyecta en el payload a botia cifrado y se descifra solo dentro de canva_tool
- Validar que el `org_id` del job corresponde al org del usuario en cada endpoint de polling

---

## 9. Manejo de Errores

| Escenario | Comportamiento |
|-----------|---------------|
| Canva no conectado | El orchestrator genera todo excepto los assets visuales; job completa sin Canva assets; el panel muestra aviso "Conecta Canva en Ajustes para generar imágenes" |
| Timeout en botia (>5 min) | covacha-core tiene un job monitor que marca jobs como `failed` si llevan >5 min sin callback |
| Error parcial en un agente | El orchestrator registra el error del agente fallido, continúa con los demás, retorna resultado parcial con `partial: true` |
| Meta Ads no conectado | Se omite la creación de borrador; job completa igual |
| Canva token expirado | canva_tool intenta refresh automático antes de usar el token |

---

## 10. Testing

### covacha-botia
- `test_copywriter_expert_agent.py` — mock LLM, verificar estructura del output para cada formato
- `test_facebook_ads_expert_agent.py` — mock LLM, verificar campos de campaign_config
- `test_promotion_content_orchestrator.py` — mock agentes, verificar que los 3 corren en paralelo y se agrega el resultado correctamente
- `test_canva_tool.py` — mock Canva API, verificar llamadas a /designs y /exports

### covacha-core
- `test_promotion_generation_service.py` — mock botia call, verificar creación de job y acciones post-generación
- `test_canva_integration_service.py` — mock Canva OAuth, verificar flujo completo
- `test_generation_job_repository.py` — mock DynamoDB, verificar CRUD
- `test_canva_token_repository.py` — verificar AES encryption/decryption

### mf-marketing
- `ai-generation-panel.component.spec.ts` — mock service, verificar estados de progreso y tabs de resultado
- `ai-generation.service.spec.ts` — mock HTTP, verificar polling con takeUntil

---

## 11. Secuencia de Implementación (orden sugerido)

1. **covacha-botia** — 2 nuevos agentes + orchestrator + canva_tool + controller
2. **covacha-core** — tablas DynamoDB + Canva OAuth + endpoints de generación + acciones post-generación
3. **mf-settings** — página Integraciones + Canva connect
4. **mf-marketing** — panel IA + progress + tabs de resultado

Cada fase tiene sus propios tests. Cobertura mínima: 98%.
