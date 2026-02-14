# Arquitectura hexagonal – MF-WhatsApp

## Capas obligatorias

```
src/app/
├── domain/                    # Sin dependencias Angular
│   ├── models/                # Conversation, Message, Contact, WhatsAppNumber, ClientSummary, etc.
│   └── ports/                 # WhatsAppPort, ConversationsPort, MetricsPort, etc.
│
├── application/               # Casos de uso
│   └── use-cases/
│       ├── get-conversations.use-case.ts
│       ├── send-message.use-case.ts
│       ├── list-clients.use-case.ts
│       ├── get-metrics.use-case.ts
│       └── ...
│
├── infrastructure/            # Adapters (HTTP, WebSocket)
│   └── adapters/
│       ├── whatsapp.adapter.ts      # API REST WhatsApp / sp_webhook
│       ├── conversations.adapter.ts
│       ├── realtime.adapter.ts      # WebSocket
│       └── metrics.adapter.ts
│
├── presentation/
│   ├── pages/                 # 1 página por ruta, lazy-loaded
│   │   ├── home/              # Dashboard clientes (super admin)
│   │   ├── chat/              # Interface tipo WhatsApp Web
│   │   ├── automation/        # Config bots/agentes
│   │   └── analytics/         # Métricas y reportes
│   ├── components/            # Reutilizables, @Input/@Output
│   └── layout/
│
├── core/
│   ├── http/http.service.ts   # Headers X-API-KEY, Authorization, X-SP-Organization-Id
│   └── services/
│       ├── organization-validator.service.ts
│       └── toast.service.ts
│
├── shared-state/              # Shell: covacha:auth, covacha:user, covacha:tenant
└── remote-entry/              # entry.component.ts, entry.routes.ts
```

## Reglas de dependencias

- **domain/** → sin importar de `@angular/*` ni de otras capas.
- **application/** → solo domain, shared-state; nunca HttpService ni presentation.
- **infrastructure/** → domain, core/http; implementan ports.
- **presentation/** → application (use cases), domain/models; nunca infrastructure directamente.
- **core/** → shared-state; transversal.

## Integraciones backend

- **sp_webhook** (webhook.superpago.com.mx): webhooks WhatsApp, mensajes.
- **mipay_core** (api.superpago.com.mx): organizaciones, usuarios, clientes.
- **covacha-botIA**: agentes/IA para automatizaciones (asignación de agente por número).
- **WebSockets**: notificaciones en tiempo real (mensajes nuevos, estados).

## Path aliases

Usar siempre: `@domain/*`, `@application/*`, `@infrastructure/*`, `@presentation/*`, `@core/*`, `@shared-state`, `@env`.
