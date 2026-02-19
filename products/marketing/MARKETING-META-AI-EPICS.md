# Marketing - Integracion Meta AI / LLama (EP-MK-025)

**Fecha**: 2026-02-18
**Product Owner**: BaatDigital / Marketing
**Estado**: Planificacion
**Continua desde**: MARKETING-EPICS.md (EP-MK-013: AI Config Multi-Provider)
**User Stories**: US-MK-101 a US-MK-107

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Arquitectura de Integracion Meta AI](#arquitectura-de-integracion-meta-ai)
3. [Modelos de Dominio](#modelos-de-dominio)
4. [Mapa de la Epica](#mapa-de-la-epica)
5. [Epica Detallada](#epica-detallada)
6. [User Stories Detalladas](#user-stories-detalladas)
7. [Estrategia de Testing](#estrategia-de-testing)
8. [Roadmap](#roadmap)
9. [Grafo de Dependencias](#grafo-de-dependencias)
10. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

EP-MK-013 define la configuracion de proveedores IA multi-provider (OpenAI, Anthropic/Claude, Gemini) por cliente. Sin embargo, **Meta AI / LLama** merece una integracion dedicada por las siguientes razones:

### Por que Meta AI / LLama es diferente

| Aspecto | OpenAI / Claude / Gemini | Meta AI / LLama |
|---------|--------------------------|-----------------|
| API | APIs propietarias cloud-only | API Meta AI + opcion self-hosted + Hugging Face |
| Modelos | GPT-4, Claude 3.5, Gemini Pro | LLama 3.1 (8B/70B/405B), LLama 3.2 (1B/3B/11B/90B), LLama 3.3 (70B) |
| Licencia | Propietaria, pago por token | Open-weight, free para uso comercial (<700M MAU) |
| Ventaja marketing | Generacion de texto generico | **Optimizado para ecosistema Meta**: FB, IG, WhatsApp, Ads |
| Vision | Solo texto (o multimodal limitado) | LLama 3.2 11B/90B: **multimodal** (analisis de imagenes) |
| Costo | $2-60 por 1M tokens | **Gratis** self-hosted, $0.05-0.90 via Together/Fireworks |
| Hosting | Solo cloud | Cloud (Meta AI API, Together, Fireworks) o **self-hosted** (EC2/GPU) |

### Capacidades Unicas para Marketing Digital

1. **Generacion de copies optimizados para Meta Ads**: LLama entiende el ecosistema de anuncios de Meta (character limits, best practices, CTAs)
2. **Analisis multimodal de creativos**: LLama 3.2 Vision puede analizar imagenes de posts/ads y sugerir mejoras
3. **Moderacion de comentarios**: Analisis de sentimiento y deteccion de spam nativo
4. **Costo operativo minimo**: Modelos open-weight permiten uso intensivo sin preocuparse por costos de API
5. **Personalizacion total**: Fine-tuning con datos del cliente para tono de marca perfecto
6. **Privacidad**: Datos del cliente no salen del servidor si se usa self-hosted

### Relacion con EP-MK-013

| EP-MK-013 (existente) | EP-MK-025 (nueva) |
|------------------------|---------------------|
| Wizard generico multi-provider | Wizard especializado Meta AI con catalogo de modelos LLama |
| API key simple (1 key por provider) | Meta AI API key + opcion Together AI + opcion self-hosted endpoint |
| Config basica (temp, max_tokens) | Config avanzada: quantization, context window, vision mode, fine-tune ID |
| Generacion de texto | Generacion de texto + analisis de imagenes (multimodal) |
| Sin comparativa entre providers | Dashboard comparativo de rendimiento y costos entre todos los providers |

EP-MK-025 **extiende** EP-MK-013 agregando Meta AI como proveedor con capacidades adicionales, y agrega la capa de comparativa cross-provider.

### Repositorios Involucrados

| Repositorio | Funcion | Cambios |
|-------------|---------|---------|
| `mf-marketing` | Frontend Angular 21 | Config Meta AI, catalogo modelos, playground, comparativa |
| `covacha-core` | Backend API Flask | Servicio Meta AI, proxy LLama, endpoints config/generate |
| `covacha-libs` | Modelos compartidos | Modelos Pydantic para Meta AI config y responses |

---

## Arquitectura de Integracion Meta AI

```
                    ┌─────────────────────────────────────────────┐
                    │           mf-marketing (Angular 21)          │
                    │                                              │
                    │  ┌──────────────┐  ┌──────────────────────┐  │
                    │  │ AI Provider  │  │ LLama Model Catalog  │  │
                    │  │ Settings     │  │ (browse, compare,    │  │
                    │  │ (EP-MK-013)  │  │  select)             │  │
                    │  └──────┬───────┘  └──────────┬───────────┘  │
                    │         │                      │              │
                    │  ┌──────┴──────────────────────┴───────────┐  │
                    │  │        AI Generation Interface           │  │
                    │  │  (content, ads copy, image analysis)    │  │
                    │  └──────────────────┬──────────────────────┘  │
                    │                     │                         │
                    │  ┌──────────────────┴──────────────────────┐  │
                    │  │     Provider Comparison Dashboard        │  │
                    │  │  (quality, speed, cost per provider)    │  │
                    │  └─────────────────────────────────────────┘  │
                    └──────────────────┬──────────────────────────┘
                                       │ HTTP
                    ┌──────────────────┴──────────────────────────┐
                    │           covacha-core (Flask)               │
                    │                                              │
                    │  ┌─────────────────────────────────────────┐ │
                    │  │     AI Provider Router (existente)       │ │
                    │  │  Selecciona provider segun config del   │ │
                    │  │  cliente: OpenAI | Claude | Gemini |    │ │
                    │  │  *** Meta AI / LLama (NUEVO) ***        │ │
                    │  └────┬──────┬───────┬───────┬─────────────┘ │
                    │       │      │       │       │               │
                    │       ▼      ▼       ▼       ▼               │
                    │  ┌────────┐ ┌─────┐ ┌─────┐ ┌────────────┐  │
                    │  │OpenAI  │ │Claud│ │Gemin│ │ Meta AI /  │  │
                    │  │Service │ │e Svc│ │i Svc│ │ LLama Svc  │  │
                    │  └────────┘ └─────┘ └─────┘ └─────┬──────┘  │
                    │                                     │        │
                    └─────────────────────────────────────┼────────┘
                                                          │
                          ┌───────────────────────────────┼────────────┐
                          │                               │            │
                          ▼                               ▼            ▼
                   ┌─────────────┐              ┌──────────────┐ ┌──────────┐
                   │ Meta AI API │              │ Together AI  │ │Self-host │
                   │ (llama-api) │              │ Fireworks AI │ │(EC2/GPU) │
                   │             │              │ Groq         │ │          │
                   │ Modelos:    │              │              │ │ LLama    │
                   │ LLama 3.1  │              │ Mismos       │ │ via      │
                   │ LLama 3.2  │              │ modelos,     │ │ vLLM /   │
                   │ LLama 3.3  │              │ API compat.  │ │ Ollama   │
                   └─────────────┘              └──────────────┘ └──────────┘
```

### Proveedores de Hosting LLama Soportados

| Proveedor | API Endpoint | Modelos | Costo aprox (1M tokens) | Latencia |
|-----------|-------------|---------|------------------------|----------|
| **Meta AI API** | `api.llama.com/v1/chat/completions` | LLama 3.1/3.2/3.3 todos | Gratis (con limits) | ~500ms |
| **Together AI** | `api.together.xyz/v1/chat/completions` | LLama 3.x completo | $0.05 - $0.90 | ~300ms |
| **Fireworks AI** | `api.fireworks.ai/inference/v1/chat/completions` | LLama 3.x completo | $0.10 - $0.90 | ~200ms |
| **Groq** | `api.groq.com/openai/v1/chat/completions` | LLama 3.1/3.3 70B, 8B | $0.05 - $0.80 | ~100ms |
| **Self-hosted** | Configurable | Cualquier LLama | Solo infra | Variable |

Todos usan formato **OpenAI-compatible** (messages array, completions endpoint), lo cual simplifica la integracion.

---

## Modelos de Dominio

### Frontend (TypeScript - mf-marketing)

```typescript
// src/app/domain/models/meta-ai-config.model.ts

// --- Enums ---

export type LlamaHostingProvider = 'meta_ai' | 'together' | 'fireworks' | 'groq' | 'self_hosted';

export type LlamaModelFamily = 'llama-3.1' | 'llama-3.2' | 'llama-3.3';

export type LlamaCapability = 'text' | 'vision' | 'code' | 'multilingual' | 'function_calling';

export type GenerationUseCase =
  | 'social_post'
  | 'ad_copy'
  | 'email_copy'
  | 'whatsapp_message'
  | 'image_analysis'
  | 'comment_moderation'
  | 'hashtag_generation'
  | 'content_calendar'
  | 'brand_voice';

// --- Catalogo de Modelos ---

export interface LlamaModel {
  id: string;                          // "llama-3.3-70b-instruct"
  name: string;                        // "LLama 3.3 70B Instruct"
  family: LlamaModelFamily;
  parameterCount: string;              // "70B", "8B", "405B"
  contextWindow: number;               // 131072 (128K)
  capabilities: LlamaCapability[];
  supportedProviders: LlamaHostingProvider[];
  costPer1MInput: number;              // USD por 1M tokens input
  costPer1MOutput: number;             // USD por 1M tokens output
  maxOutputTokens: number;
  releaseDate: string;
  recommended: boolean;                // modelo recomendado para marketing
  description: string;
  benchmarks: ModelBenchmark;
}

export interface ModelBenchmark {
  mmlu: number;                        // conocimiento general
  humanEval: number;                   // generacion de codigo
  mbpp: number;                        // programacion
  hellaSwag: number;                   // razonamiento
  arc: number;                         // razonamiento avanzado
  marketingScore?: number;             // score custom para marketing (basado en tests internos)
}

// --- Configuracion de Meta AI por Cliente ---

export interface MetaAIConfig {
  id: string;
  clientId: string;
  organizationId: string;
  enabled: boolean;
  hostingProvider: LlamaHostingProvider;
  apiKey: string;                      // cifrada en backend, masked en frontend
  apiEndpoint: string;                 // URL del endpoint (auto-fill segun provider)
  selectedModelId: string;             // modelo principal
  fallbackModelId?: string;            // modelo fallback (mas barato/rapido)
  parameters: LlamaParameters;
  useCases: GenerationUseCaseConfig[];
  quotaMonthly: number;                // limite mensual en USD o tokens
  createdAt: string;
  updatedAt: string;
}

export interface LlamaParameters {
  temperature: number;                 // 0.0 - 2.0, default 0.7
  topP: number;                        // 0.0 - 1.0, default 0.9
  maxTokens: number;                   // max output tokens, default 2048
  frequencyPenalty: number;            // 0.0 - 2.0, default 0.0
  presencePenalty: number;             // 0.0 - 2.0, default 0.0
  systemPrompt: string;                // prompt de sistema para el cliente
  responseFormat?: 'text' | 'json';
}

export interface GenerationUseCaseConfig {
  useCase: GenerationUseCase;
  enabled: boolean;
  customPrompt?: string;               // override del system prompt para este caso de uso
  modelOverride?: string;              // usar otro modelo para este caso especifico
  maxTokensOverride?: number;
}

// --- Solicitud de Generacion ---

export interface MetaAIGenerationRequest {
  clientId: string;
  useCase: GenerationUseCase;
  prompt: string;
  context?: GenerationContext;
  imageUrl?: string;                   // para analisis de imagen (LLama 3.2 vision)
  platform?: 'facebook' | 'instagram' | 'whatsapp' | 'email';
  language?: string;                   // default: 'es'
  tone?: 'formal' | 'casual' | 'creative' | 'professional' | 'friendly';
  maxLength?: number;                  // caracteres max del output
  variations?: number;                 // generar N variantes (1-5)
}

export interface GenerationContext {
  clientName?: string;
  industry?: string;
  brandVoice?: string;
  targetAudience?: string;
  product?: string;
  previousContent?: string;            // contenido previo para consistencia
  competitorRefs?: string[];
}

export interface MetaAIGenerationResponse {
  id: string;
  content: string;
  variations?: string[];
  tokensUsed: TokenUsage;
  model: string;
  provider: LlamaHostingProvider;
  latencyMs: number;
  metadata: GenerationMetadata;
}

export interface TokenUsage {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  estimatedCostUsd: number;
}

export interface GenerationMetadata {
  finishReason: 'stop' | 'length' | 'error';
  suggestedHashtags?: string[];
  suggestedEmojis?: string[];
  contentWarnings?: string[];
  platformCompliance?: PlatformCompliance;
}

export interface PlatformCompliance {
  platform: string;
  characterLimit: number;
  currentLength: number;
  isCompliant: boolean;
  warnings: string[];                  // "Excede limite de FB (63206 chars)" etc.
}

// --- Comparativa de Proveedores ---

export interface ProviderComparison {
  providers: ProviderMetrics[];
  period: string;                      // "2026-02"
  bestForQuality: string;              // provider ID
  bestForSpeed: string;
  bestForCost: string;
  recommendation: string;              // "Meta AI ofrece mejor relacion costo/calidad para este cliente"
}

export interface ProviderMetrics {
  provider: string;                    // "meta_ai", "openai", "anthropic", "gemini"
  model: string;                       // modelo principal usado
  requestCount: number;
  totalTokens: number;
  totalCostUsd: number;
  avgLatencyMs: number;
  avgQualityScore: number;             // 1-5, basado en feedback del usuario
  errorRate: number;                   // porcentaje de requests fallidos
  topUseCases: string[];
}

// --- Uso y Costos ---

export interface MetaAIUsageEntry {
  id: string;
  clientId: string;
  timestamp: string;
  useCase: GenerationUseCase;
  model: string;
  provider: LlamaHostingProvider;
  tokensInput: number;
  tokensOutput: number;
  costUsd: number;
  latencyMs: number;
  qualityRating?: number;              // 1-5, feedback del usuario
  userId: string;
}

export interface MetaAIUsageSummary {
  clientId: string;
  period: string;
  totalRequests: number;
  totalTokens: number;
  totalCostUsd: number;
  quotaUsedPercent: number;
  byUseCase: Record<GenerationUseCase, { count: number; tokens: number; cost: number }>;
  byModel: Record<string, { count: number; tokens: number; cost: number }>;
  dailyTrend: { date: string; requests: number; tokens: number; cost: number }[];
}
```

### Backend (Python - covacha-core / covacha-libs)

```python
# covacha-libs/models/meta_ai_config.py

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict
from enum import Enum


class LlamaHostingProvider(str, Enum):
    META_AI = "meta_ai"
    TOGETHER = "together"
    FIREWORKS = "fireworks"
    GROQ = "groq"
    SELF_HOSTED = "self_hosted"


class LlamaModelFamily(str, Enum):
    LLAMA_3_1 = "llama-3.1"
    LLAMA_3_2 = "llama-3.2"
    LLAMA_3_3 = "llama-3.3"


class GenerationUseCase(str, Enum):
    SOCIAL_POST = "social_post"
    AD_COPY = "ad_copy"
    EMAIL_COPY = "email_copy"
    WHATSAPP_MESSAGE = "whatsapp_message"
    IMAGE_ANALYSIS = "image_analysis"
    COMMENT_MODERATION = "comment_moderation"
    HASHTAG_GENERATION = "hashtag_generation"
    CONTENT_CALENDAR = "content_calendar"
    BRAND_VOICE = "brand_voice"


# --- Catalogo de Modelos LLama ---

LLAMA_MODEL_CATALOG = [
    {
        "id": "llama-3.3-70b-instruct",
        "name": "LLama 3.3 70B Instruct",
        "family": "llama-3.3",
        "parameter_count": "70B",
        "context_window": 131072,
        "capabilities": ["text", "code", "multilingual", "function_calling"],
        "supported_providers": ["meta_ai", "together", "fireworks", "groq"],
        "cost_per_1m_input": 0.10,
        "cost_per_1m_output": 0.30,
        "max_output_tokens": 4096,
        "recommended": True,
        "description": "Mejor modelo para generacion de contenido de marketing. "
                       "Rendimiento comparable a GPT-4 a fraccion del costo.",
    },
    {
        "id": "llama-3.2-90b-vision-instruct",
        "name": "LLama 3.2 90B Vision Instruct",
        "family": "llama-3.2",
        "parameter_count": "90B",
        "context_window": 131072,
        "capabilities": ["text", "vision", "multilingual"],
        "supported_providers": ["meta_ai", "together", "fireworks"],
        "cost_per_1m_input": 0.55,
        "cost_per_1m_output": 0.80,
        "max_output_tokens": 4096,
        "recommended": False,
        "description": "Modelo multimodal: analiza imagenes de posts/ads y sugiere mejoras. "
                       "Ideal para revision de creativos y analisis de competencia.",
    },
    {
        "id": "llama-3.2-11b-vision-instruct",
        "name": "LLama 3.2 11B Vision Instruct",
        "family": "llama-3.2",
        "parameter_count": "11B",
        "context_window": 131072,
        "capabilities": ["text", "vision", "multilingual"],
        "supported_providers": ["meta_ai", "together", "fireworks", "groq"],
        "cost_per_1m_input": 0.06,
        "cost_per_1m_output": 0.06,
        "max_output_tokens": 4096,
        "recommended": False,
        "description": "Modelo vision ligero y rapido. Bueno para moderacion "
                       "de imagenes y analisis rapido de creativos.",
    },
    {
        "id": "llama-3.1-405b-instruct",
        "name": "LLama 3.1 405B Instruct",
        "family": "llama-3.1",
        "parameter_count": "405B",
        "context_window": 131072,
        "capabilities": ["text", "code", "multilingual", "function_calling"],
        "supported_providers": ["meta_ai", "together", "fireworks"],
        "cost_per_1m_input": 0.80,
        "cost_per_1m_output": 0.80,
        "max_output_tokens": 4096,
        "recommended": False,
        "description": "Modelo mas potente de Meta. Para tareas complejas: "
                       "estrategias de marketing completas, analisis competitivo profundo.",
    },
    {
        "id": "llama-3.1-8b-instruct",
        "name": "LLama 3.1 8B Instruct",
        "family": "llama-3.1",
        "parameter_count": "8B",
        "context_window": 131072,
        "capabilities": ["text", "multilingual"],
        "supported_providers": ["meta_ai", "together", "fireworks", "groq", "self_hosted"],
        "cost_per_1m_input": 0.05,
        "cost_per_1m_output": 0.05,
        "max_output_tokens": 4096,
        "recommended": False,
        "description": "Modelo ultra-ligero y economico. Ideal para tareas simples: "
                       "hashtags, moderacion basica, traducciones, variaciones de copy.",
    },
    {
        "id": "llama-3.2-3b-instruct",
        "name": "LLama 3.2 3B Instruct",
        "family": "llama-3.2",
        "parameter_count": "3B",
        "context_window": 131072,
        "capabilities": ["text", "multilingual"],
        "supported_providers": ["meta_ai", "together", "groq", "self_hosted"],
        "cost_per_1m_input": 0.02,
        "cost_per_1m_output": 0.02,
        "max_output_tokens": 4096,
        "recommended": False,
        "description": "Modelo minimo para tareas de clasificacion, sentimiento, "
                       "y moderacion de comentarios en alto volumen.",
    },
]


# --- Modelos Pydantic ---

class LlamaParameters(BaseModel):
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=2048, ge=1, le=16384)
    frequency_penalty: float = Field(default=0.0, ge=0.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=0.0, le=2.0)
    system_prompt: str = ""
    response_format: Optional[str] = None


class UseCaseConfig(BaseModel):
    use_case: GenerationUseCase
    enabled: bool = True
    custom_prompt: Optional[str] = None
    model_override: Optional[str] = None
    max_tokens_override: Optional[int] = None


class MetaAIConfig(BaseModel):
    """Configuracion de Meta AI / LLama por cliente."""
    id: str
    client_id: str
    organization_id: str
    enabled: bool = False
    hosting_provider: LlamaHostingProvider
    api_key: str = ""                  # cifrada con Fernet en backend
    api_endpoint: str = ""
    selected_model_id: str = "llama-3.3-70b-instruct"
    fallback_model_id: Optional[str] = "llama-3.1-8b-instruct"
    parameters: LlamaParameters = LlamaParameters()
    use_cases: List[UseCaseConfig] = []
    quota_monthly: float = 50.0        # USD
    created_at: str = ""
    updated_at: str = ""

    @field_validator("api_endpoint")
    @classmethod
    def set_default_endpoint(cls, v: str, info) -> str:
        """Auto-fill endpoint segun hosting provider."""
        if v:
            return v
        provider = info.data.get("hosting_provider")
        endpoints = {
            LlamaHostingProvider.META_AI: "https://api.llama.com/v1/chat/completions",
            LlamaHostingProvider.TOGETHER: "https://api.together.xyz/v1/chat/completions",
            LlamaHostingProvider.FIREWORKS: "https://api.fireworks.ai/inference/v1/chat/completions",
            LlamaHostingProvider.GROQ: "https://api.groq.com/openai/v1/chat/completions",
        }
        return endpoints.get(provider, "")


class GenerationRequest(BaseModel):
    client_id: str
    use_case: GenerationUseCase
    prompt: str
    image_url: Optional[str] = None
    platform: Optional[str] = None
    language: str = "es"
    tone: str = "professional"
    max_length: Optional[int] = None
    variations: int = Field(default=1, ge=1, le=5)


class TokenUsage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class GenerationResponse(BaseModel):
    id: str
    content: str
    variations: List[str] = []
    tokens_used: TokenUsage
    model: str
    provider: LlamaHostingProvider
    latency_ms: int = 0
    suggested_hashtags: List[str] = []
    platform_compliance: Optional[Dict] = None


class UsageEntry(BaseModel):
    id: str
    client_id: str
    timestamp: str
    use_case: GenerationUseCase
    model: str
    provider: LlamaHostingProvider
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    latency_ms: int = 0
    quality_rating: Optional[int] = None
    user_id: str = ""


class UsageSummary(BaseModel):
    client_id: str
    period: str
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    quota_used_percent: float = 0.0
    by_use_case: Dict[str, Dict] = {}
    by_model: Dict[str, Dict] = {}
    daily_trend: List[Dict] = []
```

### DynamoDB Schema

```
Tabla: covacha-core (single-table design)

# Config Meta AI por cliente
PK: ORG#{orgId}#CLIENT#{clientId}
SK: META_AI_CONFIG

# Uso/consumo por request (para facturacion y analytics)
PK: ORG#{orgId}#CLIENT#{clientId}
SK: META_AI_USAGE#{timestamp}#{requestId}
GSI1 (usage-gsi): GSI1PK=ORG#{orgId}  GSI1SK=META_AI_USAGE#{yearMonth}

# Comparativas de providers (pre-computadas mensualmente)
PK: ORG#{orgId}#CLIENT#{clientId}
SK: AI_COMPARISON#{yearMonth}

# Cache de respuestas (TTL 24h para evitar regenerar contenido similar)
PK: ORG#{orgId}#CLIENT#{clientId}
SK: META_AI_CACHE#{hash(prompt+model)}
TTL: 86400 (24 horas)
```

---

## Mapa de la Epica

| ID | Epica | Complejidad | Prioridad | User Stories | Dependencias |
|----|-------|-------------|-----------|--------------|--------------|
| EP-MK-025 | Integracion Meta AI / LLama para Marketing | XL | Alta | US-MK-101 a US-MK-107 (7 US) | EP-MK-013 (AI Config base) |

**Estimacion total**: ~40-55 dev-days

---

## Epica Detallada

### EP-MK-025: Integracion Meta AI / LLama para Marketing

**Objetivo**: Integrar Meta AI / LLama como proveedor de IA en la plataforma de marketing, permitiendo a los clientes configurar API keys, seleccionar modelos del catalogo LLama (3.1/3.2/3.3), generar contenido optimizado para redes sociales, analizar imagenes de creativos, moderar comentarios, y comparar rendimiento/costos contra otros proveedores (OpenAI, Claude, Gemini).

**Estado actual**: EP-MK-013 tiene wizard parcial de AI config para OpenAI/Anthropic/Gemini. No hay soporte para Meta AI / LLama. No hay catalogo de modelos ni comparativa de providers.

**Modelos LLama disponibles**:

| Modelo | Params | Vision | Recomendado Para |
|--------|--------|--------|------------------|
| LLama 3.3 70B Instruct | 70B | No | Generacion de contenido (mejor relacion calidad/costo) |
| LLama 3.2 90B Vision | 90B | **Si** | Analisis de creativos e imagenes |
| LLama 3.2 11B Vision | 11B | **Si** | Moderacion de imagenes (rapido y barato) |
| LLama 3.1 405B Instruct | 405B | No | Estrategias complejas, analisis profundo |
| LLama 3.1 8B Instruct | 8B | No | Hashtags, traducciones, variaciones (ultra-barato) |
| LLama 3.2 3B Instruct | 3B | No | Clasificacion, sentimiento en alto volumen |

---

## User Stories Detalladas

---

### US-MK-101: Configuracion de proveedor Meta AI / LLama por cliente

**ID:** US-MK-101
**Epica:** EP-MK-025
**Prioridad:** P0
**Story Points:** 8

Como **gestor de agencia** quiero configurar Meta AI / LLama como proveedor de IA para un cliente, seleccionando el hosting provider (Meta AI API, Together, Fireworks, Groq o self-hosted), ingresando la API key y configurando parametros, igual que se configura OpenAI o Claude, para usar modelos LLama en la generacion de contenido del cliente.

**Criterios de Aceptacion:**
- [ ] Wizard de 4 pasos: Hosting Provider > API Key > Modelo > Parametros
- [ ] Paso 1: Seleccionar hosting (Meta AI, Together, Fireworks, Groq, Self-hosted) con descripcion de cada uno
- [ ] Paso 2: Ingresar API key + endpoint (auto-fill segun provider, editable para self-hosted)
- [ ] Paso 2: Validacion de API key con test call real (enviar "Hello" y verificar response 200)
- [ ] Paso 2: API key cifrada en backend (Fernet), mostrada como `sk-...****` en frontend
- [ ] Paso 3: Seleccionar modelo principal del catalogo (con filtro por capabilities) + modelo fallback opcional
- [ ] Paso 4: Configurar parametros: temperature, top_p, max_tokens, frequency/presence penalty
- [ ] Paso 4: Configurar system prompt del cliente (reutiliza editor de EP-MK-013 si existe)
- [ ] Guardar configuracion en DynamoDB (PK/SK: META_AI_CONFIG)
- [ ] Editar configuracion existente sin perder API key (solo actualizar campos modificados)
- [ ] Toggle on/off para activar/desactivar Meta AI sin borrar config

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `MetaAIConfigService` en `covacha-core/services/meta_ai_config_service.py`
- [ ] **Backend**: Endpoints CRUD:
  - `POST /api/v1/organization/{orgId}/clients/{clientId}/ai-providers/meta` (crear config)
  - `GET /api/v1/organization/{orgId}/clients/{clientId}/ai-providers/meta` (obtener config)
  - `PUT /api/v1/organization/{orgId}/clients/{clientId}/ai-providers/meta` (actualizar)
  - `DELETE /api/v1/organization/{orgId}/clients/{clientId}/ai-providers/meta` (eliminar)
  - `POST /api/v1/organization/{orgId}/clients/{clientId}/ai-providers/meta/validate` (test key)
- [ ] **Backend**: Cifrado de API key con `cryptography.fernet` (key en env var `AI_ENCRYPTION_KEY`)
- [ ] **Frontend**: Crear `MetaAIConfigWizardComponent` (4 pasos standalone)
- [ ] **Frontend**: Crear `HostingProviderSelectorComponent` con cards descriptivas
- [ ] **Frontend**: Integrar en tab "AI" de client settings (junto a OpenAI/Claude/Gemini)
- [ ] **Tests unitarios (10+)**: config CRUD, cifrado API key, validacion endpoint, auto-fill endpoint, toggle on/off
- [ ] **Tests de integracion (4+)**: crear config → validar key mock → persistir DynamoDB, cifrado round-trip
- [ ] **Tests E2E (2+)**: wizard completo → guardar → verificar en settings; editar config existente

---

### US-MK-102: Catalogo interactivo de modelos LLama

**ID:** US-MK-102
**Epica:** EP-MK-025
**Prioridad:** P0
**Story Points:** 5

Como **gestor de agencia** quiero explorar un catalogo visual de todos los modelos LLama disponibles con sus capacidades, costos y benchmarks para elegir el modelo optimo para cada cliente y caso de uso.

**Criterios de Aceptacion:**
- [ ] Pagina/modal de catalogo con todos los modelos LLama (6+ modelos)
- [ ] Cada modelo muestra: nombre, familia, parametros, capabilities (badges), costo, context window
- [ ] Filtros: por familia (3.1/3.2/3.3), por capability (text/vision/code), por costo (bajo/medio/alto)
- [ ] Indicador "Recomendado" en el modelo sugerido para marketing (LLama 3.3 70B)
- [ ] Comparativa lado a lado: seleccionar 2-3 modelos y ver tabla comparativa
- [ ] Badge de "Vision" en modelos multimodales (3.2 11B, 3.2 90B)
- [ ] Indicador de providers disponibles por modelo (iconos de Meta, Together, Fireworks, Groq)
- [ ] Boton "Seleccionar" que aplica el modelo a la config del cliente
- [ ] Tooltip con descripcion detallada y caso de uso recomendado al hover

**Tareas Tecnicas:**
- [ ] **Backend**: Endpoint `GET /api/v1/ai-providers/meta/models` (retorna catalogo estatico + precios actualizados)
- [ ] **Frontend**: Crear `LlamaModelCatalogComponent` con grid de model cards
- [ ] **Frontend**: Crear `ModelComparisonComponent` para comparativa lado a lado
- [ ] **Frontend**: Crear `ModelCardComponent` con badges, metricas y CTA
- [ ] **Tests unitarios (6+)**: rendering de catalogo, filtros, comparativa, seleccion
- [ ] **Tests de integracion (2+)**: endpoint de catalogo → response structure
- [ ] **Tests E2E (2+)**: navegar catalogo → filtrar → comparar → seleccionar modelo

---

### US-MK-103: Generacion de contenido social con LLama

**ID:** US-MK-103
**Epica:** EP-MK-025
**Prioridad:** P0
**Story Points:** 8

Como **Community Manager** quiero generar posts para Facebook, Instagram y WhatsApp usando LLama, con el tono de marca del cliente, para acelerar la creacion de contenido de calidad.

**Criterios de Aceptacion:**
- [ ] Boton "Generar con Meta AI" en creacion de posts (junto al existente "Generar con AI" de EP-MK-013)
- [ ] Selector de plataforma destino: Facebook, Instagram, WhatsApp (ajusta limites de caracteres automaticamente)
- [ ] Inputs: tema/producto, tono (formal/casual/creativo/profesional/amigable), longitud deseada
- [ ] Genera: copy principal + sugerencias de hashtags + emojis sugeridos
- [ ] Generar 1-5 variaciones del copy para elegir la mejor
- [ ] Compliance de plataforma: warning si excede limites (FB 63206, IG 2200, WA 1024 chars)
- [ ] Streaming de respuesta (SSE) para UX fluida en generaciones largas
- [ ] El copy generado es editable antes de guardar como post
- [ ] Usa automaticamente el system prompt y modelo configurado del cliente
- [ ] Si Meta AI no esta configurado, muestra mensaje "Configure Meta AI en Settings > AI"
- [ ] Tracking de uso: cada generacion registra tokens, costo, modelo, latencia

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `MetaAIGenerationService` en `covacha-core/services/meta_ai_generation_service.py`
- [ ] **Backend**: Endpoint `POST /api/v1/organization/{orgId}/clients/{clientId}/ai/meta/generate` (streaming SSE)
- [ ] **Backend**: Prompts especializados por plataforma (FB tiene mas espacio, IG requiere hashtags, WA es conversacional)
- [ ] **Backend**: Registrar cada request en DynamoDB (PK/SK: META_AI_USAGE#{timestamp})
- [ ] **Frontend**: Crear `MetaAIContentGeneratorComponent` integrado en creacion de post
- [ ] **Frontend**: Crear `VariationsSelectorComponent` para elegir entre variaciones generadas
- [ ] **Frontend**: Crear `PlatformComplianceBadgeComponent` (verde=ok, amarillo=warning, rojo=excede)
- [ ] **Frontend**: Integrar SSE con `EventSource` o `fetch` + ReadableStream para streaming
- [ ] **Tests unitarios (10+)**: generation service, prompts por plataforma, compliance check, streaming mock, variaciones
- [ ] **Tests de integracion (4+)**: generate endpoint → LLama API mock → response parsing → usage tracking
- [ ] **Tests E2E (2+)**: generar post FB → verificar copy + hashtags; generar 3 variaciones → seleccionar una

---

### US-MK-104: Generacion de copies para Meta Ads con LLama

**ID:** US-MK-104
**Epica:** EP-MK-025
**Prioridad:** P0
**Story Points:** 5

Como **gestor de agencia** quiero generar copies optimizados para Facebook/Instagram Ads usando LLama para crear anuncios efectivos mas rapido, aprovechando que LLama entiende el ecosistema de Meta Ads.

**Criterios de Aceptacion:**
- [ ] Integracion en paso 3 (Anuncios) del Campaign Builder wizard (EP-MK-007)
- [ ] Inputs especificos de ads: objetivo de campana, producto/servicio, audiencia target, CTA deseado
- [ ] Genera: headline (40 chars max), primary text (125 chars recomendado), description (30 chars), CTA
- [ ] Respeta limites de caracteres de Meta Ads automaticamente
- [ ] Genera variaciones A/B (2-5 copies diferentes) para testing
- [ ] Sugerencias de CTA basadas en objetivo: "Comprar ahora", "Mas info", "Registrate", etc.
- [ ] Preview de como se ve el copy en un mockup de ad de Facebook/Instagram
- [ ] Si el cliente tiene brand kit, el tono se alinea automaticamente

**Tareas Tecnicas:**
- [ ] **Backend**: Extender `MetaAIGenerationService` con use case `ad_copy`
- [ ] **Backend**: Prompts especializados para Meta Ads con conocimiento de best practices
- [ ] **Backend**: Validacion de limites de caracteres de Meta Ads
- [ ] **Frontend**: Crear `AdCopyGeneratorComponent` integrado en campaign builder
- [ ] **Frontend**: Crear `AdPreviewMockupComponent` (preview visual del anuncio)
- [ ] **Tests unitarios (8+)**: ad copy generation, character limits, CTA suggestions, variations, preview
- [ ] **Tests de integracion (3+)**: generate ad copy → validate limits → format response
- [ ] **Tests E2E (2+)**: generar copy de ad → verificar preview → seleccionar variacion

---

### US-MK-105: Analisis de imagenes y moderacion con LLama Vision

**ID:** US-MK-105
**Epica:** EP-MK-025
**Prioridad:** P1
**Story Points:** 8

Como **Community Manager** quiero usar LLama Vision (3.2) para analizar imagenes de posts/creativos y moderar comentarios automaticamente para optimizar la calidad visual del contenido y mantener las comunidades limpias.

**Criterios de Aceptacion:**
- [ ] **Analisis de creativos**: Subir imagen de post/ad y obtener:
  - Descripcion del contenido visual
  - Sugerencias de mejora (composicion, texto en imagen, colores vs brand kit)
  - Score de calidad estimado (1-10)
  - Compliance con policies de Meta Ads (texto < 20% de la imagen, sin contenido prohibido)
- [ ] **Moderacion de comentarios**: Analisis automatico de comentarios con:
  - Clasificacion: positivo, neutral, negativo, spam, ofensivo
  - Confianza del clasificador (0-1)
  - Accion sugerida: responder, ocultar, eliminar, escalar a humano
  - Batch processing: analizar 50+ comentarios en una sola request
- [ ] Usa modelo LLama 3.2 Vision (11B para batch rapido, 90B para analisis profundo)
- [ ] Dashboard de moderacion: resumen de comentarios clasificados, acciones pendientes
- [ ] Configurable por cliente: activar/desactivar moderacion automatica

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `LlamaVisionService` para analisis de imagenes (multimodal API)
- [ ] **Backend**: Crear `CommentModerationService` con batch processing via SQS
- [ ] **Backend**: Endpoints:
  - `POST /api/v1/.../ai/meta/analyze-image` (analisis de imagen)
  - `POST /api/v1/.../ai/meta/moderate-comments` (batch de comentarios)
- [ ] **Backend**: Prompts especializados para analisis visual de marketing y moderacion
- [ ] **Frontend**: Crear `ImageAnalysisComponent` con upload + resultado inline
- [ ] **Frontend**: Crear `CommentModerationDashboardComponent` con tabla de resultados
- [ ] **Frontend**: Crear `ModerationActionComponent` (botones: aprobar, ocultar, eliminar, escalar)
- [ ] **Tests unitarios (10+)**: vision service, moderacion batch, clasificacion, acciones
- [ ] **Tests de integracion (4+)**: analyze-image → vision API mock, moderate-comments → batch → classify
- [ ] **Tests E2E (2+)**: subir imagen → ver analisis; moderar comentarios → aplicar accion

---

### US-MK-106: Dashboard de uso y costos de Meta AI por cliente

**ID:** US-MK-106
**Epica:** EP-MK-025
**Prioridad:** P1
**Story Points:** 5

Como **director de agencia** quiero ver un dashboard con el consumo de Meta AI por cliente mostrando requests, tokens, costos y quota utilizada para controlar gastos y facturar al cliente.

**Criterios de Aceptacion:**
- [ ] KPIs principales: total requests, total tokens, costo total USD, % quota usada
- [ ] Grafica de tendencia diaria (requests y costo por dia, ultimos 30 dias)
- [ ] Desglose por caso de uso: social_post, ad_copy, image_analysis, moderation (tabla + donut chart)
- [ ] Desglose por modelo: cuantos requests y costo por cada modelo LLama usado
- [ ] Alerta visual cuando quota > 80% (amarillo) y > 100% (rojo)
- [ ] Filtro por periodo (semana, mes, trimestre, custom)
- [ ] Comparativa mes actual vs mes anterior (con flechas de tendencia)
- [ ] Exportar datos como CSV para facturacion
- [ ] Accesible desde tab "AI" en settings del cliente

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `MetaAIUsageService` que agrega datos de usage entries
- [ ] **Backend**: Endpoint `GET /api/v1/.../clients/{clientId}/ai-providers/meta/usage?period=monthly`
- [ ] **Backend**: Pre-computar resumen mensual con GSI de usage (evitar scan)
- [ ] **Frontend**: Crear `MetaAIUsageDashboardComponent` con KPI cards + graficas
- [ ] **Frontend**: Crear `UsageByUseCaseChartComponent` (donut chart)
- [ ] **Frontend**: Crear `UsageTrendChartComponent` (line chart diario)
- [ ] **Frontend**: Integrar con ng2-charts
- [ ] **Tests unitarios (8+)**: aggregation service, KPIs, filtros, exportacion CSV
- [ ] **Tests de integracion (3+)**: usage endpoint → aggregation → response
- [ ] **Tests E2E (2+)**: ver dashboard → cambiar periodo → verificar graficas; exportar CSV

---

### US-MK-107: Comparativa de rendimiento entre proveedores IA

**ID:** US-MK-107
**Epica:** EP-MK-025
**Prioridad:** P1
**Story Points:** 5

Como **director de agencia** quiero comparar el rendimiento, velocidad y costo de Meta AI / LLama contra OpenAI, Claude y Gemini para cada cliente para elegir el mejor proveedor segun las necesidades.

**Criterios de Aceptacion:**
- [ ] Tabla comparativa: Meta AI vs OpenAI vs Claude vs Gemini (solo providers configurados del cliente)
- [ ] Metricas por provider: total requests, avg latency (ms), total cost (USD), avg quality score (1-5)
- [ ] Grafica de radar: calidad vs velocidad vs costo vs volumen por provider
- [ ] Ranking automatico: "Mejor para calidad", "Mejor para velocidad", "Mejor para costo"
- [ ] Recomendacion generada: "Para este cliente, Meta AI ofrece 80% de la calidad de Claude a 30% del costo"
- [ ] Playground de comparativa: enviar el mismo prompt a 2+ providers y comparar respuestas lado a lado
- [ ] Quality score basado en feedback del usuario (pulgar arriba/abajo en cada generacion)
- [ ] Datos del ultimo mes por defecto, filtrable por periodo

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `AIProviderComparisonService` que consolida metricas de todos los providers
- [ ] **Backend**: Endpoint `GET /api/v1/.../clients/{clientId}/ai-providers/compare?period=monthly`
- [ ] **Backend**: Endpoint `POST /api/v1/.../clients/{clientId}/ai-providers/playground` (enviar a multiples providers)
- [ ] **Backend**: Logica de recomendacion basada en scoring ponderado (calidad 40%, costo 30%, velocidad 30%)
- [ ] **Frontend**: Crear `ProviderComparisonComponent` con tabla + radar chart
- [ ] **Frontend**: Crear `ProviderPlaygroundComponent` (prompt → N providers → compare responses)
- [ ] **Frontend**: Crear `QualityFeedbackComponent` (pulgar arriba/abajo en cada generacion)
- [ ] **Frontend**: Integrar feedback en `MetaAIContentGeneratorComponent` y otros generadores
- [ ] **Tests unitarios (8+)**: comparison aggregation, scoring, playground, feedback tracking
- [ ] **Tests de integracion (3+)**: compare endpoint → multi-provider aggregation → scoring
- [ ] **Tests E2E (2+)**: ver comparativa → abrir playground → enviar prompt a 2 providers → comparar

---

## Estrategia de Testing

### Resumen de Tests por User Story

| US | Unit Tests | Integration Tests | E2E Tests | Total |
|----|-----------|-------------------|-----------|-------|
| US-MK-101 | 10+ | 4+ | 2+ | 16+ |
| US-MK-102 | 6+ | 2+ | 2+ | 10+ |
| US-MK-103 | 10+ | 4+ | 2+ | 16+ |
| US-MK-104 | 8+ | 3+ | 2+ | 13+ |
| US-MK-105 | 10+ | 4+ | 2+ | 16+ |
| US-MK-106 | 8+ | 3+ | 2+ | 13+ |
| US-MK-107 | 8+ | 3+ | 2+ | 13+ |
| **Total** | **60+** | **23+** | **14+** | **97+** |

### Unit Tests (Backend - pytest)

```python
# Ejemplos clave

def test_debe_crear_meta_ai_config_cuando_datos_validos():
    """Verifica creacion de MetaAIConfig con provider y modelo."""

def test_debe_cifrar_api_key_al_guardar():
    """Verifica que api_key se almacena cifrada con Fernet, nunca en plaintext."""

def test_debe_auto_fill_endpoint_segun_provider():
    """Verifica que Together -> api.together.xyz, Groq -> api.groq.com, etc."""

def test_debe_validar_api_key_con_test_call():
    """Verifica que validate endpoint hace request real y retorna ok/error."""

def test_debe_generar_post_con_hashtags_y_compliance():
    """Verifica que generacion incluye hashtags y platform compliance."""

def test_debe_respetar_limite_caracteres_instagram_2200():
    """Verifica warning cuando copy > 2200 chars para IG."""

def test_debe_clasificar_comentario_negativo_correctamente():
    """Verifica clasificacion de sentimiento con modelo mock."""

def test_debe_calcular_costo_basado_en_tokens_y_pricing():
    """Verifica: cost = (input_tokens/1M * cost_input) + (output_tokens/1M * cost_output)."""

def test_debe_generar_recomendacion_de_provider_por_scoring():
    """Verifica scoring: calidad 40% + costo 30% + velocidad 30%."""

def test_debe_registrar_usage_entry_por_cada_generacion():
    """Verifica que cada request crea un UsageEntry en DynamoDB."""

def test_debe_rechazar_generacion_cuando_quota_excedida():
    """Verifica que retorna 429 cuando el cliente excedio su quota mensual."""
```

### Unit Tests (Frontend - Karma + Jasmine)

```typescript
// Ejemplos clave

it('should display 4 wizard steps for Meta AI config', () => { ... });
it('should mask API key as sk-...****', () => { ... });
it('should show recommended badge on LLama 3.3 70B', () => { ... });
it('should filter catalog by vision capability', () => { ... });
it('should show platform compliance warning for IG > 2200 chars', () => { ... });
it('should render streaming response progressively', () => { ... });
it('should display radar chart with 4 provider metrics', () => { ... });
it('should show yellow alert when quota > 80%', () => { ... });
```

### Integration Tests (pytest)

```python
def test_crear_config_meta_ai_endpoint_persiste_cifrado():
    """POST config → verifica item en DynamoDB con key cifrada."""

def test_generar_contenido_social_via_together_api_mock():
    """generate endpoint → Together API mock → parse response → track usage."""

def test_analizar_imagen_con_llama_vision_mock():
    """analyze-image → LLama Vision mock → descripcion + score + compliance."""

def test_comparativa_providers_agrega_metricas_correctamente():
    """compare endpoint → agrega datos de 4 providers → scoring → recomendacion."""

def test_playground_envia_a_multiples_providers_en_paralelo():
    """playground → async requests a 2+ providers → respuestas lado a lado."""
```

### E2E Tests (Playwright)

```typescript
test('configurar Meta AI completo: wizard → validar → guardar', async ({ page }) => {
  // 1. Navegar a settings > AI del cliente
  // 2. Click "Agregar Meta AI / LLama"
  // 3. Completar wizard 4 pasos
  // 4. Verificar config guardada
});

test('generar post con LLama y seleccionar variacion', async ({ page }) => {
  // 1. Crear nuevo post
  // 2. Click "Generar con Meta AI"
  // 3. Llenar inputs (tema, tono, plataforma)
  // 4. Verificar 3 variaciones generadas
  // 5. Seleccionar una → verificar en editor
});

test('comparar providers en playground', async ({ page }) => {
  // 1. Abrir comparativa de providers
  // 2. Abrir playground
  // 3. Escribir prompt
  // 4. Enviar a Meta AI + Claude
  // 5. Verificar 2 respuestas lado a lado
});
```

---

## Roadmap

### Sprint 1 (Semana 1-2): Configuracion y Catalogo

```
US-MK-101: Configuracion de proveedor Meta AI / LLama
US-MK-102: Catalogo interactivo de modelos LLama
```
**Entregable**: Clientes pueden configurar Meta AI con API key y seleccionar modelo.

### Sprint 2 (Semana 3-4): Generacion de Contenido

```
US-MK-103: Generacion de contenido social con LLama
US-MK-104: Generacion de copies para Meta Ads
```
**Entregable**: Community Managers pueden generar posts y ad copies con LLama.

### Sprint 3 (Semana 5-7): Vision, Analytics y Comparativa

```
US-MK-105: Analisis de imagenes y moderacion con LLama Vision
US-MK-106: Dashboard de uso y costos
US-MK-107: Comparativa de rendimiento entre proveedores
```
**Entregable**: Capacidades multimodales + dashboard de costos + playground cross-provider.

---

## Grafo de Dependencias

```
EP-MK-013 (AI Config Multi-Provider)
  └── Prerequisito: wizard base, system prompts, quotas, billing
  └── EP-MK-025 EXTIENDE EP-MK-013 con Meta AI como provider

US-MK-101 (Config Meta AI)
  └── Depende de: EP-MK-013 (patron de config existente)
  └── Prerequisito para todas las demas US

US-MK-102 (Catalogo Modelos)
  └── Depende de: US-MK-101 (se accede desde wizard de config)
  └── Independiente para implementar

US-MK-103 (Generacion Social)
  └── Depende de: US-MK-101 (necesita config activa)
  └── Se integra con: social media posts existentes

US-MK-104 (Ad Copies)
  └── Depende de: US-MK-101 + US-MK-103 (reutiliza generation service)
  └── Se integra con: EP-MK-007 (Campaign Builder)

US-MK-105 (Vision + Moderacion)
  └── Depende de: US-MK-101 (necesita config con modelo vision)
  └── Se integra con: EP-MK-015 (Social Media Management Agent)

US-MK-106 (Dashboard Uso)
  └── Depende de: US-MK-103 (necesita datos de uso)
  └── Se integra con: EP-MK-013 US-MK-036 (quotas) y US-MK-038 (billing)

US-MK-107 (Comparativa Providers)
  └── Depende de: US-MK-106 (necesita datos de todos los providers)
  └── Se integra con: EP-MK-013 (providers existentes)
  └── Independiente: playground puede funcionar sin datos historicos
```

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigacion |
|--------|---------|--------------|------------|
| Meta AI API cambia endpoints o pricing | Config rota, costos incorrectos | Media | Catalogo de modelos configurable (no hardcoded), versionar endpoints |
| Rate limits de Meta AI API (free tier) | Generaciones bloqueadas | Alta | Fallback automatico a Together/Fireworks, cache de respuestas similares |
| Modelo LLama genera contenido inapropiado | Riesgo reputacional | Baja | Safety filters en system prompt, review humano obligatorio para ads |
| API key expuesta en logs o frontend | Seguridad critica | Media | Cifrado Fernet en backend, NUNCA enviar key al frontend, mask en UI |
| Self-hosted LLama en EC2 es lento | UX mala, timeouts | Media | Timeout configurable, sugerir modelos mas pequenos (8B) para self-hosted |
| Calidad de LLama inferior a GPT-4/Claude para espanol | Contenido de baja calidad | Media | Playground de comparativa para evaluar antes de elegir, fine-tuning futuro |
| Costos de Together/Fireworks escalan con uso | Sorpresa en facturacion | Media | Quotas por cliente (US-MK-106), alertas al 80% y 100% |

---

## Definition of Done (EP-MK-025)

Para considerar una user story como DONE:

- [ ] Codigo siguiendo arquitectura hexagonal (mf-marketing) y servicios/rutas/modelos (covacha-core)
- [ ] API keys NUNCA en plaintext: cifrado Fernet en backend, masked en frontend
- [ ] Unit tests con coverage >= 80%: Backend (pytest), Frontend (Karma + Jasmine)
- [ ] Integration tests para cada endpoint con mocks de LLama API
- [ ] E2E tests para flujos principales (Playwright)
- [ ] Streaming SSE funcional para generaciones largas
- [ ] Build de produccion exitoso en ambos repos
- [ ] Ningun archivo > 1000 lineas, ninguna funcion > 50 lineas
- [ ] Type hints completos (Python), interfaces definidas (TypeScript)
- [ ] Code review aprobado
- [ ] PR creado automaticamente via GitHub Actions (coverage >= 98%)
- [ ] Estado actualizado en covacha-projects y GitHub Project Board
