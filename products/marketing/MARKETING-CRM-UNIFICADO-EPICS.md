# Marketing - CRM Unificado y Leads Pipeline (EP-MK-031 a EP-MK-032)

**Fecha**: 2026-03-19
**Product Owner**: BaatDigital / Marketing
**Estado**: EP-MK-032 COMPLETADO
**Continua desde**: MARKETING-PROMOTIONS-FUNNELS-EPICS.md (EP-MK-026 a EP-MK-030)
**User Stories**: US-MK-141 a US-MK-150

---

## Mapa de Epicas

| ID | Nombre | User Stories | Size | Prioridad | Estado |
|----|--------|-------------|------|-----------|--------|
| EP-MK-031 | Unificacion Social Accounts + Ad Accounts | - | XL | P1 Alta | EN PROGRESO |
| EP-MK-032 | CRM de Leads Unificado | US-MK-141 a US-MK-150 | L | P1 Alta | COMPLETADO |

---

## EP-MK-031: Unificacion Social Accounts + Ad Accounts

> **Estado: EN PROGRESO**

Unificar tablas social_accounts + ad_accounts, flujo OAuth limpio, auto-publish completo.

---

## EP-MK-032: CRM de Leads Unificado

> **Estado: COMPLETADO (backend + frontend) — 2026-03-20**

Pipeline kanban + lista para gestion unificada de leads. Todos los canales (webchat, WhatsApp, formularios, promociones) alimentan la misma tabla `modnot_contact_leads`.

### User Stories

| ID | Nombre | Size | Estado |
|----|--------|------|--------|
| US-MK-141 | Expandir estados de funnel CRM | S | COMPLETADO |
| US-MK-142 | Componente Kanban Board con CDK Drag-Drop | L | COMPLETADO |
| US-MK-143 | Lista/Tabla mejorada como componente reutilizable | M | COMPLETADO |
| US-MK-144 | Toggle vista Kanban/Lista con persistencia | S | COMPLETADO |
| US-MK-145 | Panel de Detalle de Lead (side panel) | L | COMPLETADO |
| US-MK-146 | Endpoint de stats por funnel status | S | COMPLETADO |
| US-MK-147 | Acciones rapidas en Kanban | M | COMPLETADO |
| US-MK-148 | CRM Adapter — loadAll para Kanban | S | COMPLETADO |
| US-MK-149 | Deprecar PortalLeadsAdapter | M | COMPLETADO |
| US-MK-150 | Tests de componentes CRM | M | COMPLETADO |

### Criterios de Aceptacion

- [x] Pipeline completo: NEW → CONTACTED → INTERESTED → QUALIFIED → PROPOSAL → NEGOTIATION → WON | LOST | CLOSED
- [x] Vista Kanban con drag-drop entre columnas
- [x] Vista Lista con inline status dropdown
- [x] Toggle Kanban/Lista con persistencia en localStorage
- [x] Side panel de detalle con notas editables y timeline
- [x] Endpoint GET /leads/stats con conteo por funnel_status
- [x] CRM Adapter con loadAllLeads, loadLeadStats, leadsByStatus
- [x] Portal leads tab con banner de CRM unificado
- [x] PortalLeadsAdapter marcado como @deprecated
- [x] 38 tests backend pasan (9 nuevos)
- [x] ng build sin errores
- [x] Deploy a produccion completado

### Repos involucrados

| Repo | Commits | PR |
|------|---------|-----|
| covacha-libs | ef5e04c | #15 |
| covacha-core | 845c6f8 | #69 |
| mf-marketing | f42c130 | #109 |

### Archivos modificados

**Backend (covacha-libs):**
- `models/concerns/funnel_status_enum.py` — +5 valores (QUALIFIED, PROPOSAL, NEGOTIATION, WON, LOST)
- `repositories/modnotification/modnot_contact_lead_repository.py` — +count_by_funnel_status()

**Backend (covacha-core):**
- `controllers/agency/leads_controller.py` — +lead_stats(), FunnelStatusEnum-based valid_statuses
- `controllers/agency/agency_controller.py` — +lead_stats() delegation
- `config/routes/agency.py` — +GET /leads/stats route
- `tests/unit/controllers/agency/test_leads_controller.py` — +9 tests

**Frontend (mf-marketing):**
- `domain/models/crm.model.ts` — FunnelStatus expandido, KANBAN_STATUSES, LeadStatsResponse
- `infrastructure/adapters/crm.adapter.ts` — loadAllLeads, loadLeadStats, leadsByStatus
- `presentation/components/leads-kanban-board/` — NUEVO (3 archivos)
- `presentation/components/leads-list-view/` — NUEVO (3 archivos)
- `presentation/components/lead-detail-panel/` — NUEVO (3 archivos)
- `presentation/pages/client-workspace/tabs/client-crm.component.*` — toggle + sub-componentes
- `presentation/pages/client-workspace/tabs/client-portal.component.*` — CRM banner
- `infrastructure/adapters/portal/portal-leads.adapter.ts` — @deprecated
