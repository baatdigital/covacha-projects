# BIDS-PRODUCT-PLAN — covacha-bids

**Producto**: covacha-bids (agente de prospeccion + bid-assistant multi-portal)
**Estado**: DISEÑO APROBADO (2026-05-13). Pendiente implementacion Fase 0.
**Owner**: Carlos / baatdigital + SuperPago
**Duracion estimada**: 10-12 semanas (7 fases)
**Costo prod estable**: $30-50/mes MVP, $80-120/mes con proxy anti-bot

---

## 1. Vision

Sistema que mapea portales de proyectos freelance/B2B, evalua oportunidades contra perfiles configurables, redacta propuestas en ingles nativo, y postula en modo hibrido controlado. Genera DB de clientes/empresas/costos/propuestas para analytics, skill-gap, y mejora continua del win-rate.

Tres usuarios objetivo:
1. **baatdigital** — agencia amplia, proyectos bajo-medio ticket ($2k-$15k)
2. **SuperPago** — fintech/sistemas especialista, alto ticket ($8k-$200k)
3. **Perfiles individuales** — freelancing personal (Carlos, devs del team)

## 2. Portales objetivo (MVP + expansion)

| Portal | Acceso | TOS auto-submit | Mercado | Fase |
|---|---|---|---|---|
| Upwork | API GraphQL OAuth | NO (forzar draft+manual) | EN global | 0 |
| Freelancer.com | API REST oficial | Parcial (membership) | EN global | 0 |
| Guru.com | Scrape Playwright + RSS | NO | EN global | 1 |
| Workana | Scrape + RSS | NO | ES LATAM | 1 |
| Fiverr | Scrape (Buyer Requests deprecated) | NO | EN global | 2 |
| PeoplePerHour | Scrape | NO | EN UK/EU | 2 |
| RemoteOK / WWR | RSS publico | N/A (no submit) | EN remote | 3 |
| Hubstaff Talent | Scrape | NO | EN | 3 |

## 3. Arquitectura

Nuevo servicio Python/Flask `covacha-bids` (puerto 5008). Patron alineado a covacha-payment/covacha-notification.

```
covacha-bids/
├── src/mipay_bids/
│   ├── portals/         # PortalAdapter strategy
│   ├── crawler/         # Orquestador + rate limiters + scheduling
│   ├── evaluator/       # Scoring engine 4 dimensiones
│   ├── bid_assistant/   # LLM service (Haiku/Sonnet/Opus router)
│   ├── analytics/       # Skill-gap + reports + Athena queries
│   ├── implementation/  # Lifecycle post-win (milestones, invoices)
│   ├── events/          # SQS publisher → covacha-notification
│   ├── routes/          # Flask blueprints
│   └── services/        # Una clase por use-case
└── tests/
```

Modelos + repositorios en `covacha-libs/covacha_libs/{models,repositories}/bids/` con vendor pattern. NUNCA definir modelos en `src/*/models/`.

## 4. Modelo de datos (7 tablas DynamoDB)

### 4.1 `bids_portals` — Catalogo
- PK: `PORTAL#<slug>` SK: `META`
- attrs: `name, base_url, listing_url, auth_type, api_key_ref, rate_limit_rpm, requires_login, tos_auto_submit, supported_filters, active, adapter_class`
- GSI1: `type-index` (api vs scrape)

### 4.2 `bids_projects` — Proyectos extraidos
- PK: `PROJECT#<portal>#<external_id>` SK: `META`
- attrs: `title, description, skills[], budget_min, budget_max, currency, posted_at, client_external_id, raw_payload, normalized_tech_stack[], estimated_hours, estimated_cost_usd, score_total, score_breakdown, status (new|scored|shortlisted|drafted|submitted|won|lost|ignored), language, region`
- GSI1: `status-postedAt` GSI2: `score-postedAt` GSI3: `client-postedAt`

### 4.3 `bids_companies` — Clientes/empresas en portales
- PK: `COMPANY#<portal>#<external_id>` SK: `META`
- attrs: `name, country, rating, total_spent, projects_posted, hire_rate, avg_budget, verified_payment, payment_method, tech_stack_history[], notes, blacklist, reliability_score`
- GSI1: `rating-totalSpent`

### 4.4 `bids_proposals` — Historial propuestas
- PK: `PROPOSAL#<id>` SK: `META`
- attrs: `project_id, profile_id, portal, draft_en, draft_es_translation, draft_score, submitted_at, price_quoted, hours_quoted, outcome (pending|interview|won|lost), won_amount, cost_actual, hours_actual, margin, llm_cost_usd, lessons_learned, prompt_version`
- GSI1: `outcome-submittedAt` GSI2: `profile-submittedAt`

### 4.5 `bids_profiles` — Bidder profiles (dual mode)
- PK: `PROFILE#<id>` SK: `META`
- attrs: `mode (company|individual), name, tech_stack[], hourly_rate_usd, portfolio_links, writing_style_sample_en, target_portals[], categories {preferred[],acceptable[],skip[]}, keywords_boost, portal_filters, weights, circuit_breaker {max_per_day, min_win_rate_7d, paused_until}`

### 4.6 `bids_metrics` — Counters + circuit breaker state
- PK: `METRIC#<profile_id>#<YYYY-MM-DD>` SK: `<portal>`
- attrs: `submitted_count, won_count, lost_count, llm_cost_usd, win_rate_7d, win_rate_30d, breaker_state (open|closed|half)`

### 4.7 `bids_implementation` — Lifecycle post-win
- PK: `IMPL#<proposal_id>` SK: `META | MILESTONE#<n> | INVOICE#<n> | CHATLOG#<msgid>`
- META attrs: `status (kickoff|in_progress|qa|delivered|paid|closed), start_date, target_end, actual_end, profile_id, client_external_id, contract_value, currency, hours_budgeted, hours_consumed, margin_actual`

## 5. Crawler + Adapters

Strategy pattern. `PortalAdapter` abstracto en `covacha-libs/covacha_libs/portals/base.py`:

```python
class PortalAdapter(ABC):
    slug: str
    auth_type: Literal["api", "scrape", "hybrid"]
    tos_allows_auto_submit: bool

    @abstractmethod
    def fetch_projects(self, filters: ProjectFilters) -> list[RawProject]: ...
    @abstractmethod
    def fetch_company(self, external_id: str) -> RawCompany: ...
    @abstractmethod
    def submit_proposal(self, project_id: str, proposal: ProposalDraft) -> SubmitResult: ...
    @abstractmethod
    def normalize_project(self, raw: RawProject) -> Project: ...
```

CrawlerService corre via EventBridge cada 10min. Para portales scrape usa Fargate Spot (Playwright + stealth). Anti-detection: delays aleatorios 3-15s, user-agent rotation, session cookies persistidas en DDB, opcional proxy rotation (ScraperAPI/Bright Data).

## 6. Evaluador

Score 0-100 por dimension. Total = weighted sum por perfil.

| Dim | Default weight | Como se calcula |
|---|---|---|
| `tech_match` | 0.35 | Embeddings Bedrock Titan v2 cosine (proyecto vs profile.tech_stack) + bonus si dominio coincide + penalty si skill faltante |
| `viability` | 0.25 | LLM estima horas P10-P90 → cost = horas × rate. Filtro duro: `budget < rate*5h` → 0 |
| `client_quality` | 0.25 | `rating*40 + verified_payment*20 + hire_rate*20 + total_spent_norm*20`. Blacklist → 0. Cliente nuevo → 50 |
| `competition` | 0.15 | `freshness = 100 * exp(-age_min/120)` + `competition = 100 - min(bids_count*5, 100)`, avg simple |

Thresholds: `>=75` auto-submit (hibrido+breaker), `60-74` draft-only manual, `<60` ignored.

Re-scoring trigger: DynamoDB Stream cuando cambia perfil o se cierra propuesta (feedback loop adaptativo).

## 7. Bid Assistant — LLM router

| Modo | Modelo | Proposito |
|---|---|---|
| `score` / `price_optimize` | `claude-haiku-4-5-20251001` | Operaciones baratas alto volumen |
| `auto_draft` / `coach` | `claude-sonnet-4-6` | Drafts ingles nativo + coaching ES→EN |
| `client_intel` | `claude-opus-4-7` | Investigacion profunda solo cuentas top-tier |

Output `auto_draft`:
```json
{
  "language": "en",
  "subject": "...",
  "body_en": "...",
  "body_es_translation": "...",
  "price_quoted": 4500,
  "hours_estimated": 60,
  "winability_score": 78,
  "differentiators": ["fintech domain", "spanish+english", "SPEI prior work"],
  "prompt_version": "v3.2",
  "llm_cost_usd": 0.012
}
```

Output `coach`: side-by-side draft usuario vs version mejorada + bullets explicativos.

Prompts versionados en `prompts/`. Few-shot examples re-entrenados semanalmente con wins recientes. A/B testing entre versiones.

## 8. Submit hibrido + Circuit Breaker

Reglas TOS-safe (no negociables, en codigo):
- `portal.tos_auto_submit=false` → forzar draft-only sin importar config usuario
- Cap diario `max_per_day` por perfil/portal
- Si `win_rate_7d < min_win_rate_7d` → breaker abre 48h
- Pause manual override via `paused_until`
- Estado breaker en `bids_metrics.breaker_state` (open|closed|half-open)

## 9. Perfiles

### baatdigital
- mode: `company`
- categories.preferred: `paginas-web, desarrollo-simple, bots-ia, integraciones, marketing-digital, diseño-branding, mantenimiento-wp-shopify`
- tech_stack: `python, angular, react, node, wordpress, shopify, mobile-rn, aws-basico, openai-api, langchain`
- hourly_rate_usd: 45, budget_min_usd: 2000
- regions: `US, CA, UK, AU, MX, LATAM`, languages: `en, es`
- weights: `{tech:0.30, viability:0.30, client:0.25, competition:0.15}`

### SuperPago
- mode: `company`
- categories.preferred: `sistemas-custom, desarrollos-pesados, integraciones-ia-avanzadas, fintech, whatsapp-business-escala, multi-tenant-saas, arquitectura-cloud`
- tech_stack: `python, flask, dynamodb, aws, angular, whatsapp-api, openpay, finch, spei, stripe, micro-frontends, agents-ia, multimodal-llm`
- hourly_rate_usd: 75, budget_min_usd: 8000
- regions: `MX, LATAM, US, ES`, languages: `es, en`
- weights: `{tech:0.45, viability:0.20, client:0.25, competition:0.10}`

### Individuales (template)
- mode: `individual`
- circuit_breaker.max_per_day mas bajo (default 5)
- weights configurables por specialty

## 10. Integracion covacha-notification (5007)

Eventos publicados via SQS `modnot-events`:

| Evento | Canal | Template HSM | Recipient |
|---|---|---|---|
| `bid.shortlist_ready` | WhatsApp | `bids_daily_digest` | Owner perfil |
| `bid.draft_pending_approval` | WhatsApp+email | `bids_approval_needed` | Owner |
| `bid.submitted` | WhatsApp | `bids_submitted` | Owner |
| `bid.client_replied` | WhatsApp urgente | `bids_client_msg` | Owner |
| `bid.won` | WhatsApp+email | `bids_won_celebration` | Owner+team |
| `bid.lost` | email digest | `bids_lost_digest` | Owner |
| `breaker.opened` | WhatsApp | `bids_breaker_alert` | Owner |
| `impl.milestone_due` | WhatsApp | `impl_milestone` | PM/Owner |
| `impl.client_message` | WhatsApp | `impl_client_msg` | Owner |
| `impl.payment_received` | WhatsApp+email | `impl_payment` | Owner |

Reusa cola `modnot-whatsapp-outgoing` + Lambda `modnot-whatsapp-sender`. Templates Meta HSM registrados via `/notifications/meta/templates`.

## 11. Integracion covacha-botia (5002)

Nuevo agent `sales/bid-conversation`:

```
POST /agents/sales/bid-conversation/reply
Body: {conversation_id, project_context, client_message, profile_id, tone}
Resp: {reply_en, reply_es, suggested_actions}
```

Casos:
1. Cliente responde en portal → respuesta AI con un click
2. Cliente migra a WhatsApp post-win → handoff conversacional
3. Cliente pregunta avance implementacion → consulta `bids_implementation` + responde milestone status

Reusa quick-replies + categorias mf-whatsapp con `bids-followup` / `bids-client`.

## 12. Lifecycle Implementacion

Kanban: Kickoff → Dev → QA → Delivered → Paid.

Tabla `bids_implementation` con milestones, invoices, hours tracker, margin actual. Notificaciones automaticas:
- Milestone vence en 48h → WhatsApp PM
- Cliente sin responder 72h → escalate
- Invoice vencida → reminder cordial via covacha-botia

Fase 2 frontend mf-bids muestra kanban.

## 13. Analytics + Skill-Gap

### Pipeline
```
DynamoDB Streams → Lambda exporter (batch 5min) → S3 parquet → Glue Catalog → Athena → Metabase
```

### Dashboards Metabase
- **Overview**: Win-rate 7d/30d, Pipeline activo, Revenue MTD, LLM cost MTD
- **Por perfil**: Comparativo baatdigital vs SuperPago vs individuales
- **Por portal**: Submitted/Won/Lost, costo medio cliente, mejor ROI
- **Clientes top**: Empresas mejor pagadas, recurrencia
- **Skill demand**: Top skills demandados 30d, $/hr por skill
- **Skill-gap**: Skills donde perdimos > donde ganamos, oportunidades sin atender
- **Implementation**: Proyectos in-flight, milestones vencidos, margen real

### SkillGapService (cron semanal lunes 9am)
```python
lost = proposals.list_lost(profile_id, days=30)
won = proposals.list_won(profile_id, days=90)
unattended = projects.list_high_score_ignored(profile_id, days=14)

gap = compute_gap(skills_lost, skills_won, skills_missing, profile.tech_stack)
agenda = llm_learning_agenda(gap, profile)  # Sonnet 4.6
```

Output: `top_gaps[:10] + weekly_agenda + estimated_uplift_pct`. Notifica via WhatsApp + email digest.

## 14. Frontend mf-bids (Fase 5)

Angular MF puerto 4212. Hexagonal frontend. Federation skip list completa.

Paginas:
- Lista proyectos con filtros multi-perfil + score sort + status kanban
- Detalle proyecto (cliente intel, competencia, draft inline con coach)
- Editor propuesta (split-view ES→EN + winability score live)
- Kanban implementacion
- Dashboard (embed Metabase o vistas nativas ngx-echarts)

Expuesto via Native Federation a mf-dashboard.

## 15. Stack + Costos

| Componente | $/mes |
|---|---|
| Backend covacha-bids (EC2 ASG existente, co-tenant) | $0 marginal |
| DynamoDB 7 tablas on-demand (~5GB) | $5-10 |
| Crawler API (Lambda + EventBridge) | $0-1 |
| Crawler scrape (Fargate Spot 0.25 vCPU) | $3-5 |
| LLM scoring Haiku (~50/dia × 1.5k tokens) | $2-4 |
| LLM drafts Sonnet (~15/dia × 4k tokens) | $5-10 |
| Embeddings Bedrock Titan v2 | $0.50 |
| Metabase EC2 t3.small + EBS 20GB | $14 |
| S3 + Athena analytics (<1GB) | $0.55 |
| SES emails (free tier 62k/mes) | $0 |
| WhatsApp via covacha-notification | $0 marginal |
| **Total MVP** | **$30-40** |
| Proxy ScraperAPI (opcional) | +$49 |
| Bright Data residenciales (heavy) | +$120-200 |
| **Total Pro con proxy** | **$80-120** |

## 16. Roadmap (7 fases, 10-12 semanas)

| Fase | Alcance | Esfuerzo | Status |
|---|---|---|---|
| **0 — Foundation** | Scaffold covacha-bids + 7 tablas DDB + adapters API (Upwork/Freelancer) + crawler basico + evaluator stub | 5-7d | TODO |
| **1 — Scrape + Eval** | Adapters Guru/Workana Playwright + scoring 4-dim completo + bid_assistant auto_draft | 7-10d | TODO |
| **2 — Submit hibrido + Notify** | Submit con TOS gate + circuit breaker + integracion covacha-notification (eventos+templates HSM) | 5-7d | TODO |
| **3 — Implementation + Botia** | Tabla bids_implementation + agent sales/bid-conversation en covacha-botia + kanban API | 7-10d | TODO |
| **4 — Analytics + Skill-Gap** | DDB Streams→S3→Athena pipeline + Metabase deploy + skill_gap_service + weekly report | 5d | TODO |
| **5 — mf-bids UI** | Angular MF completo: lista + detalle + editor coach + kanban impl + dashboard embed | 10-15d | TODO |
| **6 — Auto-pilot avanzado** | Feedback loop adaptativo pesos evaluador + multi-perfil avanzado + A/B prompts | 5-7d | TODO |

## 17. Criterios de Aceptacion (alto nivel)

- [ ] Scaffold backend con 7 tablas creadas en DDB dev
- [ ] Modelos+repos en covacha-libs con tests >=98% coverage
- [ ] Crawler API Upwork+Freelancer fetcheando proyectos reales
- [ ] Scrape Guru+Workana con anti-detection funcionando 24h sin block
- [ ] Evaluador retornando 4 scores + total con 2 perfiles configurados
- [ ] Bid assistant auto_draft generando propuesta EN+ES+winability
- [ ] Circuit breaker abriendo en simulacion win-rate < 8%
- [ ] Eventos publicados a SQS modnot-events con templates HSM activos
- [ ] Agent sales/bid-conversation respondiendo en covacha-botia
- [ ] Pipeline DDB→S3→Athena con 7 dashboards Metabase
- [ ] SkillGapService cron weekly enviando agenda via WhatsApp
- [ ] mf-bids deployado en CloudFront con kanban funcional
- [ ] Coverage backend >=98% en todos los modulos

## 18. Riesgos + Mitigaciones

| Riesgo | Mitigacion |
|---|---|
| Ban de portal por scrape/auto-submit | TOS-safe gate en codigo + circuit breaker + delays + proxy si necesario |
| Costos LLM explotan | Router modelos + cache embeddings + threshold scoring antes draft |
| Propuestas auto-draft mediocres bajan rating | Hibrido obligatorio en arranque + approval manual primer mes |
| Scrape rompe por cambio UI portal | Adapter pattern + tests E2E semanales + alerta WhatsApp si falla parsing |
| Falsos positivos en evaluador | Feedback loop semanal con outcomes reales + ajuste pesos |
| Conflicto entre perfiles por mismo proyecto | Routing: cada perfil tiene cola separada; mismo proyecto puede ir a multiples si aplica |

## 19. Referencias

- CLAUDE.md seccion `covacha-bids` (reglas operativas)
- `.claude/napkin.md` categoria `Bids Prospection Stack`
- Patron base: covacha-payment (Flask blueprints + services + libs vendor)
- Patron LLM: covacha-botia (router de modelos + prompts versionados)
- Patron notifications: covacha-notification (SQS events + templates HSM)
