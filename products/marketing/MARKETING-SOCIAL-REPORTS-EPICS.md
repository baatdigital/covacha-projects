# Marketing - Reportes de Resultados de Redes Sociales (EP-MK-024)

**Fecha**: 2026-02-18
**Product Owner**: BaatDigital / Marketing
**Estado**: Planificacion
**Continua desde**: MARKETING-EPICS.md (EP-MK-006 a EP-MK-013), MARKETING-AI-AGENTS-EPICS.md (EP-MK-014 a EP-MK-023)
**User Stories**: US-MK-094 a US-MK-100

---

## Tabla de Contenidos

1. [Contexto y Motivacion](#contexto-y-motivacion)
2. [Modelos de Dominio](#modelos-de-dominio)
3. [Mapa de la Epica](#mapa-de-la-epica)
4. [Epica Detallada](#epica-detallada)
5. [User Stories Detalladas](#user-stories-detalladas)
6. [Estrategia de Testing](#estrategia-de-testing)
7. [Roadmap](#roadmap)
8. [Grafo de Dependencias](#grafo-de-dependencias)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)

---

## Contexto y Motivacion

La agencia digital BaatDigital necesita un sistema integral para **administrar, generar y visualizar reportes de resultados de redes sociales** para sus clientes. Actualmente, los reportes se crean manualmente en PowerPoint o Google Sheets, lo cual:

- Consume 1-2 dias por cliente por reporte mensual
- Produce datos desactualizados al momento de la entrega
- No permite comparativas automatizadas entre periodos
- No estandariza metricas ni formatos entre clientes
- No tiene trazabilidad de reportes generados ni flujo de aprobacion

### Diferenciacion con Epicas Existentes

| Epica Existente | Alcance | Diferencia con EP-MK-024 |
|-----------------|---------|--------------------------|
| EP-MK-009 (Dashboards Ejecutivo) | Dashboard real-time en UI | EP-MK-024 genera **reportes formales** exportables/enviables |
| EP-MK-020 (Agente Analytics IA) | Agente IA que genera reportes via chat/WhatsApp | EP-MK-024 es el **modulo CRUD de gestion** con modelos, templates y flujo de aprobacion |
| EP-MK-012 (Analytics BI Estrategias) | BI de estrategias de marketing | EP-MK-024 se enfoca en **metricas de redes sociales** especificamente |

### Repositorios Involucrados

| Repositorio | Funcion | Cambios |
|-------------|---------|---------|
| `mf-marketing` | Frontend Angular 21 | Pagina de reportes, componentes de visualizacion, templates |
| `covacha-core` | Backend API Flask | Endpoints CRUD, servicio de recopilacion de metricas, exportacion |
| `covacha-libs` | Modelos compartidos | Modelos Pydantic de reportes sociales |

---

## Modelos de Dominio

### Frontend (TypeScript - mf-marketing)

```typescript
// src/app/domain/models/social-media-report.model.ts

// --- Enums y Types ---

export type SocialPlatform = 'facebook' | 'instagram' | 'tiktok' | 'linkedin' | 'twitter';
export type ReportStatus = 'draft' | 'generated' | 'review' | 'approved' | 'sent';
export type ContentType = 'image' | 'video' | 'carousel' | 'reel' | 'story' | 'text';
export type PeriodType = 'weekly' | 'monthly' | 'quarterly' | 'custom';
export type TrendDirection = 'up' | 'down' | 'stable';
export type PostRanking = 'top' | 'average' | 'low';

// --- Entidad Principal: Reporte ---

export interface SocialMediaReport {
  id: string;
  clientId: string;
  organizationId: string;
  title: string;
  period: ReportPeriod;
  platforms: SocialPlatform[];
  status: ReportStatus;
  platformMetrics: PlatformMetrics[];
  topPosts: PostPerformance[];
  audienceDemographics: AudienceDemographics[];
  contentAnalysis: ContentAnalysis[];
  periodComparison: PeriodComparison[];
  recommendations: ReportRecommendation[];
  templateId?: string;
  notes?: string;
  generatedBy: string;
  generatedAt: string;
  approvedBy?: string;
  approvedAt?: string;
  sentTo?: string[];
  sentAt?: string;
  createdAt: string;
  updatedAt: string;
}

// --- Periodo del Reporte ---

export interface ReportPeriod {
  startDate: string;   // ISO 8601
  endDate: string;     // ISO 8601
  type: PeriodType;
  label: string;       // "Enero 2026", "Q1 2026", "Sem 1-7 Feb 2026"
}

// --- Metricas por Plataforma ---

export interface PlatformMetrics {
  platform: SocialPlatform;
  followers: FollowerMetrics;
  reach: ReachMetrics;
  engagement: EngagementMetrics;
  content: ContentMetrics;
  conversions: ConversionMetrics;
}

export interface FollowerMetrics {
  start: number;
  end: number;
  gained: number;
  lost: number;
  netGrowth: number;
  growthRate: number;          // porcentaje
}

export interface ReachMetrics {
  totalImpressions: number;
  totalReach: number;
  organicReach: number;
  paidReach: number;
  avgReachPerPost: number;
}

export interface EngagementMetrics {
  totalLikes: number;
  totalComments: number;
  totalShares: number;
  totalSaves: number;
  totalReactions: number;
  engagementRate: number;      // porcentaje
  avgEngagementPerPost: number;
}

export interface ContentMetrics {
  totalPosts: number;
  totalStories: number;
  totalReels: number;
  postsByType: Record<ContentType, number>;
  avgPostsPerWeek: number;
}

export interface ConversionMetrics {
  linkClicks: number;
  profileVisits: number;
  websiteClicks: number;
  callClicks: number;
  emailClicks: number;
  clickThroughRate: number;    // porcentaje
}

// --- Rendimiento Individual de Posts ---

export interface PostPerformance {
  postId: string;
  platform: SocialPlatform;
  contentType: ContentType;
  publishedAt: string;
  contentPreview: string;
  thumbnailUrl?: string;
  permalink?: string;
  likes: number;
  comments: number;
  shares: number;
  saves: number;
  reach: number;
  impressions: number;
  engagementRate: number;
  clickThroughRate: number;
  ranking: PostRanking;
}

// --- Demografia de Audiencia ---

export interface AudienceDemographics {
  platform: SocialPlatform;
  ageRanges: AgeRangeMetric[];
  genderDistribution: GenderMetric[];
  topCountries: LocationMetric[];
  topCities: LocationMetric[];
  activeHours: ActiveHourMetric[];
}

export interface AgeRangeMetric {
  range: string;          // '13-17', '18-24', '25-34', '35-44', '45-54', '55-64', '65+'
  percentage: number;
  count: number;
}

export interface GenderMetric {
  gender: 'male' | 'female' | 'other';
  percentage: number;
  count: number;
}

export interface LocationMetric {
  name: string;
  percentage: number;
  count: number;
}

export interface ActiveHourMetric {
  dayOfWeek: number;     // 0=Lunes ... 6=Domingo
  hour: number;          // 0-23
  avgEngagement: number;
  postCount: number;
}

// --- Analisis de Contenido ---

export interface ContentAnalysis {
  platform: SocialPlatform;
  byType: ContentTypeAnalysis[];
  byTopic: TopicPerformance[];
  hashtagPerformance: HashtagMetric[];
  bestPostingTimes: BestTimeSlot[];
}

export interface ContentTypeAnalysis {
  type: ContentType;
  count: number;
  avgEngagement: number;
  avgReach: number;
  totalImpressions: number;
}

export interface TopicPerformance {
  topic: string;
  postCount: number;
  avgEngagement: number;
  avgReach: number;
}

export interface HashtagMetric {
  tag: string;
  usageCount: number;
  avgReach: number;
  avgEngagement: number;
}

export interface BestTimeSlot {
  dayOfWeek: number;
  hour: number;
  avgEngagement: number;
  postCount: number;
}

// --- Comparativas Periodo a Periodo ---

export interface PeriodComparison {
  metricName: string;
  category: 'followers' | 'engagement' | 'reach' | 'content' | 'conversions';
  platform: SocialPlatform | 'all';
  currentValue: number;
  previousValue: number;
  changeAbsolute: number;
  changePercentage: number;
  trend: TrendDirection;
}

// --- Recomendaciones del Reporte ---

export interface ReportRecommendation {
  id: string;
  category: 'content' | 'timing' | 'engagement' | 'growth' | 'conversion';
  priority: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: string;             // "Podria aumentar engagement 15-20%"
  actionItems: string[];
}

// --- Templates de Reportes ---

export interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  sections: ReportSection[];
  layout: 'standard' | 'executive' | 'detailed' | 'custom';
  brandingEnabled: boolean;
  isDefault: boolean;
  createdAt: string;
}

export interface ReportSection {
  id: string;
  type: ReportSectionType;
  title: string;
  enabled: boolean;
  order: number;
  config?: Record<string, unknown>;
}

export type ReportSectionType =
  | 'executive_summary'
  | 'platform_overview'
  | 'follower_growth'
  | 'engagement_metrics'
  | 'reach_impressions'
  | 'top_posts'
  | 'worst_posts'
  | 'content_analysis'
  | 'audience_demographics'
  | 'best_posting_times'
  | 'hashtag_performance'
  | 'period_comparison'
  | 'conversions'
  | 'recommendations'
  | 'custom_notes';

// --- Configuracion de Reporte Programado ---

export interface ScheduledReport {
  id: string;
  clientId: string;
  templateId: string;
  frequency: 'weekly' | 'biweekly' | 'monthly';
  dayOfWeek?: number;        // para weekly: 0-6
  dayOfMonth?: number;       // para monthly: 1-28
  recipients: string[];      // emails
  platforms: SocialPlatform[];
  format: 'pdf' | 'html';
  enabled: boolean;
  lastGeneratedAt?: string;
  nextGenerationAt: string;
  createdAt: string;
}
```

### Backend (Python - covacha-core / covacha-libs)

```python
# covacha-libs/models/social_media_report.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum
from datetime import datetime


class SocialPlatform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"


class ReportStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    REVIEW = "review"
    APPROVED = "approved"
    SENT = "sent"


class ContentType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    CAROUSEL = "carousel"
    REEL = "reel"
    STORY = "story"
    TEXT = "text"


class PeriodType(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    CUSTOM = "custom"


class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


class ReportPeriod(BaseModel):
    start_date: str
    end_date: str
    type: PeriodType
    label: str = ""


class FollowerMetrics(BaseModel):
    start: int = 0
    end: int = 0
    gained: int = 0
    lost: int = 0
    net_growth: int = 0
    growth_rate: float = 0.0


class ReachMetrics(BaseModel):
    total_impressions: int = 0
    total_reach: int = 0
    organic_reach: int = 0
    paid_reach: int = 0
    avg_reach_per_post: float = 0.0


class EngagementMetrics(BaseModel):
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_saves: int = 0
    total_reactions: int = 0
    engagement_rate: float = 0.0
    avg_engagement_per_post: float = 0.0


class ContentMetrics(BaseModel):
    total_posts: int = 0
    total_stories: int = 0
    total_reels: int = 0
    posts_by_type: Dict[str, int] = {}
    avg_posts_per_week: float = 0.0


class ConversionMetrics(BaseModel):
    link_clicks: int = 0
    profile_visits: int = 0
    website_clicks: int = 0
    call_clicks: int = 0
    email_clicks: int = 0
    click_through_rate: float = 0.0


class PlatformMetrics(BaseModel):
    platform: SocialPlatform
    followers: FollowerMetrics = FollowerMetrics()
    reach: ReachMetrics = ReachMetrics()
    engagement: EngagementMetrics = EngagementMetrics()
    content: ContentMetrics = ContentMetrics()
    conversions: ConversionMetrics = ConversionMetrics()


class PostPerformance(BaseModel):
    post_id: str
    platform: SocialPlatform
    content_type: ContentType
    published_at: str
    content_preview: str = ""
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    reach: int = 0
    impressions: int = 0
    engagement_rate: float = 0.0
    click_through_rate: float = 0.0
    ranking: str = "average"


class AgeRangeMetric(BaseModel):
    range: str
    percentage: float = 0.0
    count: int = 0


class GenderMetric(BaseModel):
    gender: str
    percentage: float = 0.0
    count: int = 0


class LocationMetric(BaseModel):
    name: str
    percentage: float = 0.0
    count: int = 0


class ActiveHourMetric(BaseModel):
    day_of_week: int
    hour: int
    avg_engagement: float = 0.0
    post_count: int = 0


class AudienceDemographics(BaseModel):
    platform: SocialPlatform
    age_ranges: List[AgeRangeMetric] = []
    gender_distribution: List[GenderMetric] = []
    top_countries: List[LocationMetric] = []
    top_cities: List[LocationMetric] = []
    active_hours: List[ActiveHourMetric] = []


class ContentTypeAnalysis(BaseModel):
    type: ContentType
    count: int = 0
    avg_engagement: float = 0.0
    avg_reach: float = 0.0
    total_impressions: int = 0


class TopicPerformance(BaseModel):
    topic: str
    post_count: int = 0
    avg_engagement: float = 0.0
    avg_reach: float = 0.0


class HashtagMetric(BaseModel):
    tag: str
    usage_count: int = 0
    avg_reach: float = 0.0
    avg_engagement: float = 0.0


class BestTimeSlot(BaseModel):
    day_of_week: int
    hour: int
    avg_engagement: float = 0.0
    post_count: int = 0


class ContentAnalysis(BaseModel):
    platform: SocialPlatform
    by_type: List[ContentTypeAnalysis] = []
    by_topic: List[TopicPerformance] = []
    hashtag_performance: List[HashtagMetric] = []
    best_posting_times: List[BestTimeSlot] = []


class PeriodComparison(BaseModel):
    metric_name: str
    category: str
    platform: str = "all"
    current_value: float = 0.0
    previous_value: float = 0.0
    change_absolute: float = 0.0
    change_percentage: float = 0.0
    trend: TrendDirection = TrendDirection.STABLE


class ReportRecommendation(BaseModel):
    id: str
    category: str
    priority: str = "medium"
    title: str
    description: str
    impact: str = ""
    action_items: List[str] = []


class SocialMediaReport(BaseModel):
    """Modelo principal de reporte de resultados de redes sociales."""
    id: str
    client_id: str
    organization_id: str
    title: str
    period: ReportPeriod
    platforms: List[SocialPlatform]
    status: ReportStatus = ReportStatus.DRAFT
    platform_metrics: List[PlatformMetrics] = []
    top_posts: List[PostPerformance] = []
    audience_demographics: List[AudienceDemographics] = []
    content_analysis: List[ContentAnalysis] = []
    period_comparison: List[PeriodComparison] = []
    recommendations: List[ReportRecommendation] = []
    template_id: Optional[str] = None
    notes: Optional[str] = None
    generated_by: str = ""
    generated_at: Optional[str] = None
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    sent_to: List[str] = []
    sent_at: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""


class ReportSection(BaseModel):
    id: str
    type: str
    title: str
    enabled: bool = True
    order: int = 0
    config: Optional[Dict] = None


class ReportTemplate(BaseModel):
    id: str
    name: str
    description: str = ""
    sections: List[ReportSection] = []
    layout: str = "standard"
    branding_enabled: bool = True
    is_default: bool = False
    created_at: str = ""


class ScheduledReport(BaseModel):
    id: str
    client_id: str
    template_id: str
    frequency: str = "monthly"
    day_of_week: Optional[int] = None
    day_of_month: Optional[int] = None
    recipients: List[str] = []
    platforms: List[SocialPlatform] = []
    format: str = "pdf"
    enabled: bool = True
    last_generated_at: Optional[str] = None
    next_generation_at: str = ""
    created_at: str = ""
```

### DynamoDB Schema

```
Tabla: covacha-core (single-table design)

# Reporte principal
PK: ORG#{orgId}#CLIENT#{clientId}
SK: REPORT#{reportId}
GSI1 (status-gsi): GSI1PK=ORG#{orgId}  GSI1SK=REPORT#STATUS#{status}#{date}
GSI2 (date-gsi):   GSI2PK=ORG#{orgId}  GSI2SK=REPORT#DATE#{generatedAt}

# Metricas por plataforma (item separado por tamano)
PK: ORG#{orgId}#CLIENT#{clientId}
SK: REPORT#{reportId}#PLATFORM#{platform}

# Posts top/bottom del reporte
PK: ORG#{orgId}#CLIENT#{clientId}
SK: REPORT#{reportId}#POST#{postId}

# Templates de reportes (por organizacion)
PK: ORG#{orgId}
SK: REPORT_TEMPLATE#{templateId}

# Reportes programados
PK: ORG#{orgId}#CLIENT#{clientId}
SK: REPORT_SCHEDULE#{scheduleId}
GSI3 (schedule-gsi): GSI3PK=SCHEDULE  GSI3SK=NEXT#{nextGenerationAt}
```

---

## Mapa de la Epica

| ID | Epica | Complejidad | Prioridad | User Stories | Dependencias |
|----|-------|-------------|-----------|--------------|--------------|
| EP-MK-024 | Reportes de Resultados de Redes Sociales | L | Alta | US-MK-094 a US-MK-100 (7 US) | Social media adapters (completado), EP-MK-008 (Brand Kit para branding) |

**Estimacion total**: ~35-45 dev-days

---

## Epica Detallada

### EP-MK-024: Administracion de Reportes de Resultados de Redes Sociales

**Objetivo**: Implementar un sistema completo para crear, generar, visualizar, aprobar y exportar reportes de resultados de redes sociales por cliente, con metricas de plataforma, rendimiento de contenido, demografia de audiencia, comparativas periodo a periodo y recomendaciones accionables.

**Estado actual**: No existe modulo de reportes formales. Los datos de social media existen parcialmente en adapters de FB/IG. No hay persistencia de reportes ni templates.

**Items clave del reporte**:

| Seccion | Datos Principales | Fuente |
|---------|-------------------|--------|
| Resumen ejecutivo | KPIs globales, cambios vs periodo anterior | Agregacion de todas las secciones |
| Crecimiento de seguidores | Inicio, fin, ganados, perdidos, tasa de crecimiento | Facebook Graph API, IG API |
| Alcance e impresiones | Total, organico vs pagado, promedio por post | Facebook Insights, IG Insights |
| Engagement | Likes, comments, shares, saves, tasa de engagement | Facebook Graph API, IG API |
| Top posts | Top 5 y bottom 5 por engagement, con thumbnails | Posts publicados del periodo |
| Analisis de contenido | Rendimiento por tipo (imagen, video, reel, story) | Clasificacion de posts |
| Hashtags | Top hashtags por alcance y engagement | Analisis de posts publicados |
| Audiencia | Edad, genero, ubicacion, horas activas | Facebook Audience Insights |
| Mejores horarios | Heatmap dia/hora de mejor engagement | Analisis historico de posts |
| Comparativa periodo | MoM, YoY con indicadores de tendencia | Datos historicos almacenados |
| Conversiones | Clicks, visitas al perfil, CTR | Facebook/IG Insights |
| Recomendaciones | Acciones sugeridas con impacto estimado | Analisis automatizado + IA |

---

## User Stories Detalladas

---

### US-MK-094: Modelos de dominio y schema DynamoDB para reportes sociales

**ID:** US-MK-094
**Epica:** EP-MK-024
**Prioridad:** P0
**Story Points:** 5

Como **desarrollador del equipo** quiero tener los modelos de dominio (TypeScript + Python + Pydantic) y el schema DynamoDB definidos e implementados para que todo el desarrollo del modulo de reportes tenga una base solida y consistente.

**Criterios de Aceptacion:**
- [x] Modelos TypeScript definidos en `mf-marketing/src/app/domain/models/social-media-report.model.ts`
- [ ] Modelos Pydantic definidos en `covacha-libs/models/social_media_report.py`
- [ ] Schema DynamoDB documentado con PK/SK, GSIs y ejemplos de items
- [ ] Enums compartidos entre frontend y backend son consistentes (SocialPlatform, ReportStatus, ContentType)
- [ ] Validaciones Pydantic incluyen: campos requeridos, rangos numericos (rates 0-100), fechas ISO 8601
- [ ] Type hints completos en todos los modelos Python
- [ ] Barrel export en `social-media-report.model.ts` accesible desde `domain/models/index.ts`

**Tareas Tecnicas:**
- [ ] Crear `social-media-report.model.ts` en mf-marketing con todas las interfaces (ver seccion Modelos)
- [ ] Crear `social_media_report.py` en covacha-libs con modelos Pydantic v2
- [ ] Agregar barrel export al `index.ts` de models
- [ ] Documentar schema DynamoDB con ejemplos de PK/SK
- [ ] **Tests unitarios (8+)**: validacion de cada modelo Pydantic (campos requeridos, defaults, rangos)
- [ ] **Tests de integracion (3+)**: serialization/deserialization JSON ↔ Pydantic ↔ DynamoDB item
- [ ] **Tests E2E**: N/A para esta US (solo modelos)

---

### US-MK-095: CRUD de reportes de redes sociales

**ID:** US-MK-095
**Epica:** EP-MK-024
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero crear, listar, editar y eliminar reportes de resultados de redes sociales por cliente para gestionar el historial de reportes de forma organizada.

**Criterios de Aceptacion:**
- [ ] Crear reporte: seleccionar cliente, periodo (semanal/mensual/trimestral/custom), plataformas, titulo
- [ ] Listar reportes por cliente con filtros: status, periodo, plataforma
- [ ] Ordenar por fecha de generacion (mas reciente primero)
- [ ] Editar reporte en estado `draft` o `review` (titulo, notas, plataformas)
- [ ] Eliminar reporte solo en estado `draft` con confirmacion
- [ ] Flujo de estados: `draft` → `generated` → `review` → `approved` → `sent`
- [ ] Paginacion cursor-based (20 reportes por pagina)
- [ ] Busqueda por titulo del reporte

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `SocialReportService` en `covacha-core/services/social_report_service.py`
- [ ] **Backend**: Crear Blueprint `social_reports_bp` en `covacha-core/routes/social_reports.py`
- [ ] **Backend**: Endpoints:
  - `POST /api/v1/organization/{orgId}/clients/{clientId}/social-reports` (crear)
  - `GET /api/v1/organization/{orgId}/clients/{clientId}/social-reports` (listar con filtros)
  - `GET /api/v1/organization/{orgId}/clients/{clientId}/social-reports/{reportId}` (detalle)
  - `PUT /api/v1/organization/{orgId}/clients/{clientId}/social-reports/{reportId}` (editar)
  - `DELETE /api/v1/organization/{orgId}/clients/{clientId}/social-reports/{reportId}` (eliminar)
  - `PATCH /api/v1/organization/{orgId}/clients/{clientId}/social-reports/{reportId}/status` (cambiar estado)
- [ ] **Backend**: Repositorio DynamoDB `SocialReportRepository` con operaciones CRUD
- [ ] **Frontend**: Crear `SocialReportAdapter` en infrastructure/adapters
- [ ] **Frontend**: Crear `SocialReportListComponent` con tabla, filtros y paginacion
- [ ] **Frontend**: Crear `SocialReportCreateComponent` con wizard de 3 pasos (cliente/periodo/plataformas)
- [ ] **Frontend**: Ruta lazy-loaded `/clients/:id/social-reports`
- [ ] **Tests unitarios (10+)**: servicio CRUD, validaciones de estado, paginacion, filtros
- [ ] **Tests de integracion (5+)**: endpoint → servicio → DynamoDB (crear, listar, editar, eliminar, cambiar estado)
- [ ] **Tests E2E (3+)**: flujo completo crear reporte → listar → cambiar estado → eliminar

---

### US-MK-096: Recopilacion y visualizacion de metricas por plataforma

**ID:** US-MK-096
**Epica:** EP-MK-024
**Prioridad:** P0
**Story Points:** 8

Como **Account Manager** quiero que al generar un reporte se recopilen automaticamente las metricas de cada plataforma social del cliente (Facebook, Instagram) para no tener que ingresar datos manualmente.

**Criterios de Aceptacion:**
- [ ] Boton "Generar metricas" en reporte en estado `draft` inicia recopilacion
- [ ] Metricas recopiladas por plataforma: seguidores, alcance, impresiones, engagement, contenido, conversiones
- [ ] Datos de Facebook: via Graph API (`/{page-id}/insights`, `/{page-id}/feed`)
- [ ] Datos de Instagram: via Instagram Graph API (`/{ig-user-id}/insights`, `/{ig-user-id}/media`)
- [ ] Indicador de progreso durante recopilacion (puede tomar 10-30 segundos)
- [ ] Si una plataforma falla, las demas continuan y se muestra error parcial
- [ ] Visualizacion de metricas en cards con indicadores (icono por plataforma, valor principal, cambio %)
- [ ] Graficas de barras comparando metricas entre plataformas
- [ ] Graficas de linea mostrando tendencia diaria/semanal dentro del periodo

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `SocialMetricsCollector` que orquesta la recopilacion multi-plataforma
- [ ] **Backend**: Crear `FacebookMetricsService` que consume Graph API para metricas de pagina
- [ ] **Backend**: Crear `InstagramMetricsService` que consume IG Graph API para metricas de cuenta business
- [ ] **Backend**: Endpoint `POST /api/v1/.../social-reports/{reportId}/generate` (async, retorna job ID)
- [ ] **Backend**: Endpoint `GET /api/v1/.../social-reports/{reportId}/generate/status` (polling de progreso)
- [ ] **Backend**: Almacenar metricas como items separados en DynamoDB (PK/SK: REPORT#/PLATFORM#)
- [ ] **Frontend**: Crear `PlatformMetricsCardComponent` (una card por plataforma con KPIs)
- [ ] **Frontend**: Crear `MetricsComparisonChartComponent` (barras comparativas entre plataformas)
- [ ] **Frontend**: Crear `MetricsTrendChartComponent` (linea temporal dentro del periodo)
- [ ] **Frontend**: Integrar con ng2-charts o chart.js para graficas
- [ ] **Tests unitarios (12+)**: collectors por plataforma, aggregation, error handling, componentes de graficas
- [ ] **Tests de integracion (4+)**: endpoint generate → collector → Graph API mock → DynamoDB
- [ ] **Tests E2E (2+)**: generar reporte con metricas → verificar visualizacion de cards y graficas

---

### US-MK-097: Ranking de rendimiento de posts individuales

**ID:** US-MK-097
**Epica:** EP-MK-024
**Prioridad:** P0
**Story Points:** 5

Como **Account Manager** quiero ver el ranking de posts publicados durante el periodo del reporte ordenados por rendimiento para identificar que contenido funciona mejor y que contenido mejorar.

**Criterios de Aceptacion:**
- [ ] Top 5 posts con mejor engagement (con thumbnail, preview de texto, metricas)
- [ ] Bottom 5 posts con peor engagement (para identificar areas de mejora)
- [ ] Metricas por post: likes, comments, shares, saves, reach, impressions, engagement rate
- [ ] Filtro por plataforma y por tipo de contenido (imagen, video, reel, story, carousel)
- [ ] Click en un post abre enlace directo a la publicacion en la plataforma
- [ ] Indicador visual de ranking: medalla oro/plata/bronce para top 3
- [ ] Ordenamiento configurable: por engagement rate, por reach, por likes, por comments
- [ ] Analisis de tipo de contenido: "Los reels generan 3x mas engagement que las imagenes"

**Tareas Tecnicas:**
- [ ] **Backend**: Extender `SocialMetricsCollector` para recopilar posts individuales del periodo
- [ ] **Backend**: Servicio `PostRankingService` que calcula ranking y clasifica top/bottom
- [ ] **Backend**: Almacenar top/bottom posts en items separados REPORT#/POST#
- [ ] **Frontend**: Crear `TopPostsComponent` con grid de cards de posts
- [ ] **Frontend**: Crear `PostPerformanceCardComponent` con thumbnail, metricas y ranking
- [ ] **Frontend**: Crear `ContentTypeBreakdownComponent` (donut chart por tipo de contenido)
- [ ] **Tests unitarios (8+)**: ranking calculation, sorting, filtering, componentes UI
- [ ] **Tests de integracion (3+)**: recopilacion de posts → ranking → persistencia
- [ ] **Tests E2E (2+)**: ver top posts en reporte → filtrar por tipo → verificar orden

---

### US-MK-098: Demografia de audiencia y mejores horarios de publicacion

**ID:** US-MK-098
**Epica:** EP-MK-024
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero ver la demografia de la audiencia del cliente y los mejores horarios para publicar para optimizar la estrategia de contenido con datos reales.

**Criterios de Aceptacion:**
- [ ] Distribucion por edad: grafica de barras con rangos (13-17, 18-24, 25-34, 35-44, 45-54, 55-64, 65+)
- [ ] Distribucion por genero: grafica de dona (masculino, femenino, otro)
- [ ] Top 5 paises y top 10 ciudades por numero de seguidores
- [ ] Heatmap de mejores horarios: eje X = hora (0-23), eje Y = dia de la semana, color = engagement
- [ ] Recomendacion automatica: "Tus mejores horarios son Martes 10am y Jueves 3pm"
- [ ] Datos por plataforma (tab selector para ver FB o IG por separado)
- [ ] Si no hay datos suficientes, mostrar mensaje informativo en vez de grafica vacia

**Tareas Tecnicas:**
- [ ] **Backend**: Extender collectors para obtener audience insights de Facebook/IG
- [ ] **Backend**: Facebook: `GET /{page-id}/insights?metric=page_fans_gender_age,page_fans_country,page_fans_city`
- [ ] **Backend**: Instagram: `GET /{ig-user-id}/insights?metric=audience_gender_age,audience_country,audience_city`
- [ ] **Backend**: Servicio `AudienceAnalyticsService` que calcula mejores horarios desde posts historicos
- [ ] **Frontend**: Crear `AudienceDemographicsComponent` con graficas de edad, genero, ubicacion
- [ ] **Frontend**: Crear `BestTimesHeatmapComponent` con heatmap interactivo dia/hora
- [ ] **Frontend**: Integrar heatmap con chart.js matrix plugin o custom SVG
- [ ] **Tests unitarios (8+)**: audience parsing, heatmap calculation, componentes visuales
- [ ] **Tests de integracion (3+)**: audience API mock → service → response structure
- [ ] **Tests E2E (2+)**: ver demographics en reporte → cambiar plataforma → verificar heatmap

---

### US-MK-099: Comparativas periodo a periodo y analisis de tendencias

**ID:** US-MK-099
**Epica:** EP-MK-024
**Prioridad:** P1
**Story Points:** 5

Como **Account Manager** quiero ver comparativas automaticas del periodo actual vs el periodo anterior para demostrar progreso al cliente y detectar regresiones rapidamente.

**Criterios de Aceptacion:**
- [ ] Comparativa automatica: mes actual vs mes anterior (MoM) para todas las metricas
- [ ] Comparativa ano anterior (YoY) si hay datos historicos disponibles
- [ ] Indicadores visuales por metrica: flecha verde (mejora >5%), roja (regresion >5%), gris (estable +-5%)
- [ ] Porcentaje de cambio y valor absoluto de diferencia
- [ ] Tabla resumen con todas las metricas comparadas lado a lado
- [ ] Grafica de linea "periodo actual vs periodo anterior" superpuestas
- [ ] Seccion "Highlights": las 3 metricas que mas mejoraron y las 3 que mas empeoraron
- [ ] Si no hay datos del periodo anterior, mostrar "Primer reporte - sin comparativa disponible"

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `PeriodComparisonService` que calcula deltas y tendencias
- [ ] **Backend**: Recuperar reporte del periodo anterior desde DynamoDB (query por GSI de fecha)
- [ ] **Backend**: Calcular change_percentage = ((current - previous) / previous) * 100
- [ ] **Backend**: Clasificar trend: up (>5%), down (<-5%), stable (-5% a 5%)
- [ ] **Frontend**: Crear `PeriodComparisonTableComponent` con tabla lado-a-lado
- [ ] **Frontend**: Crear `TrendIndicatorComponent` (flecha + color + porcentaje)
- [ ] **Frontend**: Crear `HighlightsComponent` (top 3 mejoras + top 3 regresiones)
- [ ] **Frontend**: Crear `ComparisonOverlayChartComponent` (2 lineas superpuestas)
- [ ] **Tests unitarios (8+)**: calculo de deltas, clasificacion de trends, edge cases (primer reporte, valores 0)
- [ ] **Tests de integracion (3+)**: comparison service con datos reales → validar output correcto
- [ ] **Tests E2E (2+)**: ver comparativa en reporte → verificar indicadores de tendencia

---

### US-MK-100: Templates, exportacion PDF/CSV y envio de reportes

**ID:** US-MK-100
**Epica:** EP-MK-024
**Prioridad:** P1
**Story Points:** 8

Como **Account Manager** quiero seleccionar un template para el reporte, exportarlo como PDF profesional con el branding del cliente, y enviarlo por email para entregar resultados a los clientes sin herramientas externas.

**Criterios de Aceptacion:**
- [ ] 3 templates predefinidos: Standard (todas las secciones), Ejecutivo (resumen + KPIs), Detallado (todo + raw data)
- [ ] Template configurable: activar/desactivar secciones, reordenar
- [ ] PDF incluye: logo del cliente (brand kit), logo de agencia, titulo, periodo, todas las secciones habilitadas con graficas
- [ ] PDF tiene diseno profesional: header con branding, colores del brand kit, tipografia limpia, pie de pagina con fecha
- [ ] Exportar datos tabulares como CSV (metricas, posts, demographics)
- [ ] Preview del reporte en modal antes de exportar
- [ ] Enviar reporte por email: seleccionar destinatarios (contactos del cliente), mensaje personalizable
- [ ] Historial de envios: quien envio, a quien, cuando
- [ ] Al enviar, el status del reporte cambia automaticamente a `sent`
- [ ] Programar envio automatico (semanal/mensual) con template y destinatarios configurados

**Tareas Tecnicas:**
- [ ] **Backend**: Crear `ReportExportService` que genera PDF via puppeteer (HTML → PDF server-side)
- [ ] **Backend**: Crear template HTML del reporte con Jinja2 (inyecta datos + graficas como SVG/images)
- [ ] **Backend**: Endpoint `POST /api/v1/.../social-reports/{reportId}/export` (formato: pdf|csv|html)
- [ ] **Backend**: Endpoint `POST /api/v1/.../social-reports/{reportId}/send` (envio por email via SES)
- [ ] **Backend**: CRUD de templates: `GET/POST/PUT /api/v1/.../social-report-templates`
- [ ] **Backend**: CRUD de reportes programados: `GET/POST/PUT/DELETE /api/v1/.../social-report-schedules`
- [ ] **Backend**: Cron job (SQS) que evalua reportes programados pendientes de generacion
- [ ] **Backend**: Integrar con Brand Kit del cliente para colores/logo en PDF
- [ ] **Frontend**: Crear `ReportPreviewComponent` (modal fullscreen con preview del PDF)
- [ ] **Frontend**: Crear `ReportTemplateEditorComponent` (drag-and-drop de secciones)
- [ ] **Frontend**: Crear `ReportSendComponent` (selector de destinatarios + mensaje + preview)
- [ ] **Frontend**: Crear `ScheduledReportsComponent` (lista de reportes programados con toggle on/off)
- [ ] **Tests unitarios (10+)**: templates CRUD, export service, send service, cron logic, componentes UI
- [ ] **Tests de integracion (5+)**: export endpoint → PDF generation → S3 upload, send → SES mock, schedule → cron
- [ ] **Tests E2E (3+)**: seleccionar template → preview → exportar PDF → verificar descarga; enviar por email → verificar status `sent`

---

## Estrategia de Testing

### Resumen de Tests por User Story

| US | Unit Tests | Integration Tests | E2E Tests | Total |
|----|-----------|-------------------|-----------|-------|
| US-MK-094 | 8+ | 3+ | 0 | 11+ |
| US-MK-095 | 10+ | 5+ | 3+ | 18+ |
| US-MK-096 | 12+ | 4+ | 2+ | 18+ |
| US-MK-097 | 8+ | 3+ | 2+ | 13+ |
| US-MK-098 | 8+ | 3+ | 2+ | 13+ |
| US-MK-099 | 8+ | 3+ | 2+ | 13+ |
| US-MK-100 | 10+ | 5+ | 3+ | 18+ |
| **Total** | **64+** | **26+** | **14+** | **104+** |

### Unit Tests (Backend - pytest)

```python
# Ejemplos de tests unitarios

def test_debe_crear_reporte_cuando_datos_validos():
    """Verifica creacion exitosa de SocialMediaReport con datos minimos."""

def test_debe_fallar_creacion_sin_client_id():
    """Valida que client_id es requerido."""

def test_debe_calcular_growth_rate_correctamente():
    """Verifica: growth_rate = (net_growth / start) * 100."""

def test_debe_calcular_engagement_rate_correctamente():
    """Verifica: engagement_rate = (likes + comments + shares) / reach * 100."""

def test_debe_clasificar_trend_up_cuando_cambio_mayor_5_porciento():
    """Verifica que trend='up' cuando change_percentage > 5."""

def test_debe_clasificar_trend_stable_cuando_cambio_entre_menos5_y_5():
    """Verifica que trend='stable' cuando -5 <= change_percentage <= 5."""

def test_debe_rankear_posts_por_engagement_rate_descendente():
    """Verifica que top posts estan ordenados de mayor a menor engagement."""

def test_debe_manejar_division_por_cero_en_growth_rate():
    """Cuando followers_start=0, growth_rate debe ser 0 en vez de error."""

def test_debe_validar_periodo_start_antes_de_end():
    """Valida que start_date < end_date."""

def test_debe_transicionar_estado_draft_a_generated():
    """Verifica transicion valida de estados."""

def test_debe_rechazar_transicion_sent_a_draft():
    """Verifica que transiciones invalidas lanzan error."""
```

### Unit Tests (Frontend - Karma + Jasmine)

```typescript
// Ejemplos de tests unitarios Angular

it('should create report with default status draft', () => { ... });
it('should display platform metrics cards for each platform', () => { ... });
it('should show green arrow when trend is up', () => { ... });
it('should show red arrow when trend is down', () => { ... });
it('should calculate heatmap colors based on engagement values', () => { ... });
it('should filter posts by content type', () => { ... });
it('should sort reports by date descending', () => { ... });
it('should disable delete button for non-draft reports', () => { ... });
```

### Integration Tests (pytest)

```python
# Ejemplos de tests de integracion

def test_crear_reporte_endpoint_persiste_en_dynamodb():
    """POST /social-reports → verifica item en DynamoDB mock."""

def test_generar_metricas_facebook_recopila_insights():
    """generate endpoint → FacebookMetricsService → Graph API mock → DynamoDB."""

def test_exportar_pdf_genera_archivo_valido():
    """export endpoint → ReportExportService → puppeteer mock → S3 mock."""

def test_enviar_reporte_actualiza_status_a_sent():
    """send endpoint → SES mock → verifica status en DynamoDB."""

def test_comparativa_periodo_recupera_reporte_anterior():
    """PeriodComparisonService → DynamoDB query por GSI → calcula deltas."""
```

### E2E Tests (Playwright)

```typescript
// Ejemplos de tests E2E

test('flujo completo: crear reporte → generar → aprobar → exportar PDF', async ({ page }) => {
  // 1. Navegar a reportes del cliente
  // 2. Crear nuevo reporte (wizard)
  // 3. Generar metricas
  // 4. Verificar que metricas se muestran
  // 5. Aprobar reporte
  // 6. Exportar como PDF
  // 7. Verificar descarga
});

test('comparativa muestra indicadores de tendencia correctos', async ({ page }) => {
  // 1. Crear reporte con datos mock del periodo actual y anterior
  // 2. Verificar flechas verdes/rojas/grises
  // 3. Verificar porcentajes de cambio
});

test('enviar reporte por email actualiza historial', async ({ page }) => {
  // 1. Aprobar reporte
  // 2. Click "Enviar por email"
  // 3. Seleccionar destinatarios
  // 4. Enviar
  // 5. Verificar status "sent" y historial de envio
});
```

---

## Roadmap

### Sprint 1 (Semana 1-2): Fundamentos

```
US-MK-094: Modelos de dominio y schema DynamoDB
US-MK-095: CRUD de reportes
```
**Entregable**: Se pueden crear, listar y gestionar reportes (sin metricas aun).

### Sprint 2 (Semana 3-4): Recopilacion de Datos

```
US-MK-096: Recopilacion de metricas por plataforma
US-MK-097: Ranking de rendimiento de posts
```
**Entregable**: Reportes con metricas reales de FB/IG y ranking de posts.

### Sprint 3 (Semana 5-6): Analytics y Exportacion

```
US-MK-098: Demografia de audiencia y mejores horarios
US-MK-099: Comparativas periodo a periodo
US-MK-100: Templates, exportacion y envio
```
**Entregable**: Reportes completos exportables como PDF con branding.

---

## Grafo de Dependencias

```
US-MK-094 (Modelos)
  └── Prerequisito para todas las demas US

US-MK-095 (CRUD)
  └── Depende de: US-MK-094
  └── Prerequisito para: US-MK-096, US-MK-097, US-MK-098, US-MK-099, US-MK-100

US-MK-096 (Metricas plataforma)
  └── Depende de: US-MK-094, US-MK-095
  └── Depende de: Social media adapters (FB/IG OAuth completado)

US-MK-097 (Ranking posts)
  └── Depende de: US-MK-096 (necesita posts recopilados)

US-MK-098 (Audiencia)
  └── Depende de: US-MK-096 (comparte collectors)

US-MK-099 (Comparativas)
  └── Depende de: US-MK-096 (necesita metricas del periodo actual)
  └── Depende de: Al menos 1 reporte previo generado

US-MK-100 (Templates y exportacion)
  └── Depende de: US-MK-096 (necesita datos para exportar)
  └── Se integra con: EP-MK-008 (Brand Kit para PDF branding)
  └── Se integra con: EP-MK-020 (Agente Analytics puede usar templates)

Integraciones futuras:
  EP-MK-020 (Agente Analytics) → Usa este modulo como fuente de datos y templates
  EP-MK-009 (Dashboards) → Puede consumir datos de reportes para KPIs agregados
```

---

## Riesgos y Mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigacion |
|--------|---------|--------------|------------|
| Rate limits de Facebook/IG Graph API | Recopilacion incompleta | Alta | Batch requests, cache de metricas, retry con backoff |
| Generacion de PDF lenta (puppeteer) | UX mala, timeouts | Media | Generacion async con notificacion, pre-render graficas como SVG |
| Datos insuficientes para audiencia (cuentas nuevas) | Secciones vacias | Media | Mostrar mensaje "Datos insuficientes" en vez de graficas vacias, minimo 7 dias de datos |
| DynamoDB items muy grandes (muchos posts) | Exceder 400KB limit | Media | Almacenar posts como items separados (REPORT#/POST#), limitar a top/bottom 10 |
| Templates PDF no se ven bien en todos los clientes email | Reportes feos en email | Baja | Enviar PDF adjunto (no inline), fallback a link de descarga |
| Tokens de FB/IG expirados al generar | Recopilacion falla | Alta | Validar tokens antes de generar, notificar si token expirado, redirect a reconexion |

---

## Definition of Done (EP-MK-024)

Para considerar una user story como DONE:

- [ ] Codigo implementado siguiendo arquitectura hexagonal (mf-marketing) y separacion servicios/rutas/modelos (covacha-core)
- [ ] Unit tests con coverage >= 80%: Backend (pytest), Frontend (Karma + Jasmine)
- [ ] Integration tests para cada endpoint con mocks de servicios externos
- [ ] E2E tests para flujos principales (Playwright)
- [ ] Build de produccion exitoso en ambos repos
- [ ] Ningun archivo > 1000 lineas, ninguna funcion > 50 lineas
- [ ] Type hints completos (Python), interfaces definidas (TypeScript)
- [ ] Code review aprobado
- [ ] PR creado automaticamente via GitHub Actions (coverage >= 98%)
- [ ] Estado actualizado en covacha-projects y GitHub Project Board
