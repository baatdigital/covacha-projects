# Roadmap 2026 - Nuevos Productos SuperPago Ecosistema

**Fecha**: 2026-03-14
**Autor**: Business Strategy Agent + Claude Code
**Estado**: Propuesta para aprobacion
**GitHub Issue**: baatdigital/covacha-projects#133

---

## Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Matriz de Priorizacion](#matriz-de-priorizacion)
3. [Timeline por Trimestre](#timeline-por-trimestre)
4. [Dependencias entre Productos](#dependencias-entre-productos)
5. [Recursos Necesarios](#recursos-necesarios)
6. [Quick Wins vs Inversiones Largas](#quick-wins-vs-inversiones-largas)
7. [Orden Recomendado de Desarrollo](#orden-recomendado-de-desarrollo)
8. [KPIs de Exito por Producto](#kpis-de-exito-por-producto)
9. [Riesgos y Mitigaciones](#riesgos-y-mitigaciones)
10. [Revenue Proyectado](#revenue-proyectado)

---

## Resumen Ejecutivo

El ecosistema SuperPago tiene una ventaja competitiva unica: infraestructura de pagos SPEI + WhatsApp Business API + multi-tenancy + micro-frontends ya construidos. Los 6 nuevos productos propuestos reutilizan entre 55% y 80% de esta infraestructura, permitiendo time-to-market agresivos de 2-4 meses.

**Revenue potencial total Year 1**: ~$54M MXN/ano
**Inversion total estimada**: ~$2M MXN
**ROI proyectado**: 27x

### Productos Propuestos (en orden de prioridad)

| # | Producto | Revenue Year 1 | Esfuerzo | Reuso | Score |
|---|---------|---------------|----------|-------|-------|
| 1 | POS Virtual QR + SPEI | $12M MXN | 8 sem | 80% | 9/10 |
| 2 | Bot de Cobranza WhatsApp | $6M MXN | 8 sem | 75% | 8.5/10 |
| 3 | CRM WhatsApp-First | $6M MXN | 14 sem | 65% | 8/10 |
| 4 | Programa de Lealtad | $7.2M MXN | 10 sem | 65% | 7.5/10 |
| 5 | Nomina Digital SPEI | $7.2M MXN | 12 sem | 70% | 7/10 |
| 6 | E-commerce Builder | $14.4M MXN | 16 sem | 60% | 6.5/10 |

---

## Matriz de Priorizacion

### Criterios de Evaluacion

| Criterio | Peso | Descripcion |
|----------|------|-------------|
| Revenue potencial | 25% | Tamano de mercado y conversion esperada |
| Esfuerzo de desarrollo | 25% | Semanas, devs, complejidad |
| Reutilizacion ecosistema | 20% | % de infra existente reutilizada |
| Time to market | 15% | Rapidez para generar revenue |
| Sinergia con productos existentes | 15% | Cross-sell, upsell, efecto red |

### Evaluacion Detallada

| Producto | Revenue (25%) | Esfuerzo (25%) | Reuso (20%) | TTM (15%) | Sinergia (15%) | **Score** |
|----------|--------------|---------------|------------|----------|---------------|-----------|
| POS Virtual | 8 | 9 | 10 | 10 | 9 | **9.0** |
| Bot Cobranza | 6 | 9 | 9 | 10 | 8 | **8.3** |
| CRM WhatsApp | 6 | 6 | 7 | 7 | 9 | **6.9** |
| Lealtad | 7 | 7 | 7 | 8 | 8 | **7.3** |
| Nomina | 7 | 7 | 8 | 7 | 6 | **7.1** |
| E-commerce | 10 | 5 | 6 | 5 | 8 | **6.8** |

### Analisis de la Matriz

1. **POS Virtual** lidera por el balance optimo: revenue alto ($12M), esfuerzo bajo (8 sem), y reuso maximo (80%). Es el "no-brainer".
2. **Bot de Cobranza** es el segundo quick win: mismo esfuerzo que POS, 75% reuso, y mercado de $50B MXN en cobranza.
3. **Lealtad** y **Nomina** son similares en score pero con perfiles diferentes: Lealtad tiene mas sinergia (POS+Lealtad), Nomina es mas independiente.
4. **CRM WhatsApp** tiene alto potencial pero requiere 14 semanas y es el mas complejo (PWA, inbox, pipeline).
5. **E-commerce** tiene el mayor revenue potencial ($14.4M) pero tambien el mayor esfuerzo (16 sem) y menor reuso (60%).

---

## Timeline por Trimestre

### Q2 2026 (Abril - Junio): Quick Wins

**Objetivo**: Lanzar los 2 productos de mayor score con menor esfuerzo.

```
Abril    Mayo     Junio
|--------|--------|--------|
|==POS Virtual (8 sem)==|
|                       |→ Launch POS
|==Bot Cobranza (8 sem)==|
|                        |→ Launch Bot
```

| Producto | Inicio | Fin | Devs | Revenue esperado Q2 |
|----------|--------|-----|------|---------------------|
| POS Virtual | Abr 1 | May 26 | 2 | $0 (launch) |
| Bot Cobranza | Abr 1 | May 26 | 2 | $0 (launch) |

**Entregables Q2:**
- POS Virtual v1.0 publicado
- Bot Cobranza v1.0 publicado
- Primeros 100 comercios onboarded en POS
- Primeras 50 empresas usando Bot Cobranza
- Product-market fit validado en ambos

### Q3 2026 (Julio - Septiembre): Expansion

**Objetivo**: Lanzar Lealtad (complemento natural de POS) y comenzar CRM.

```
Julio    Agosto   Septiembre
|--------|--------|--------|
|==Programa Lealtad (10 sem)======|
|                                 |→ Launch Lealtad
|==CRM WhatsApp (14 sem)==================|
|                                          |→ (continua Q4)
```

| Producto | Inicio | Fin | Devs | Revenue esperado Q3 |
|----------|--------|-----|------|---------------------|
| Lealtad | Jul 1 | Sep 8 | 2 | $0 (launch) |
| CRM WhatsApp | Jul 1 | Oct 6 (Q4) | 2 | $0 (en desarrollo) |
| POS Virtual | - | - | 0.5 (mantenimiento) | $3M (prorated) |
| Bot Cobranza | - | - | 0.5 (mantenimiento) | $1.5M (prorated) |

**Entregables Q3:**
- Lealtad v1.0 publicado (integrado con POS Virtual)
- CRM WhatsApp al 60% de avance
- POS Virtual v1.1 (CFDI, mejoras)
- 500+ comercios en POS
- 200+ empresas en Bot Cobranza

### Q4 2026 (Octubre - Diciembre): Consolidacion

**Objetivo**: Lanzar CRM, iniciar Nomina, y planificar E-commerce para Q1 2027.

```
Octubre  Noviembre Diciembre
|--------|--------|--------|
|=CRM (cont)=|
|            |→ Launch CRM
|==Nomina Digital (12 sem)========|
|                                 |→ (continua Q1 2027)
|     |=E-commerce (planif)==|
```

| Producto | Inicio | Fin | Devs | Revenue esperado Q4 |
|----------|--------|-----|------|---------------------|
| CRM WhatsApp | (cont) | Oct 6 | 2 | $0 (launch) |
| Nomina Digital | Oct 1 | Dic 24 (cont Q1) | 2 | $0 (en desarrollo) |
| POS Virtual | - | - | 0.5 | $3M |
| Bot Cobranza | - | - | 0.5 | $1.5M |
| Lealtad | - | - | 0.5 | $1.8M (prorated) |

**Entregables Q4:**
- CRM WhatsApp v1.0 publicado
- Nomina Digital al 75% de avance
- E-commerce Builder planificado en detalle
- 1,000+ comercios en POS
- Revenue trimestral > $5M MXN

### Q1 2027 (Enero - Marzo): E-commerce + Consolidacion

```
Enero    Febrero  Marzo
|--------|--------|--------|
|=Nomina (cont)==|
|               |→ Launch Nomina
|==E-commerce Builder (16 sem)==================|
|                                               |→ (continua Q2)
```

---

## Dependencias entre Productos

### Grafo de Dependencias

```
                covacha-payment (SPEI)
                    |
        +-----------+-----------+
        |           |           |
   POS Virtual   Nomina    Bot Cobranza
        |                       |
        |                       |
   Lealtad                 CRM WhatsApp
   (puntos de POS)     (inbox WhatsApp)
        |                       |
        +-----------+-----------+
                    |
              E-commerce Builder
         (usa POS/SPEI + WhatsApp + Inventario)
```

### Dependencias Criticas

| Producto | Depende de | Tipo | Descripcion |
|----------|-----------|------|-------------|
| POS Virtual | covacha-payment (EP-SP-001, EP-SP-002) | Infraestructura | Motor SPEI existente |
| Bot Cobranza | covacha-botia | Infraestructura | Motor IA + WhatsApp existente |
| Lealtad | POS Virtual (EP-POS-001) | Producto | Acumulacion automatica vinculada a pagos POS |
| CRM WhatsApp | covacha-botia, covacha-crm | Infraestructura | Inbox WhatsApp + motor CRM |
| Nomina | covacha-payment (SPEI batch) | Infraestructura | Dispersiones masivas SPEI |
| E-commerce | POS Virtual + mf-marketing + covacha-inventory | Multi | Builder + checkout + inventario |

### Sinergias entre Productos

| Sinergia | Productos | Efecto |
|----------|-----------|--------|
| POS + Lealtad | POS → acumula puntos automatico | Clientes del POS se inscriben en lealtad, aumenta frecuencia de compra |
| POS + E-commerce | POS checkout reutilizado en tienda online | 1 motor de cobro QR para ambos productos |
| Bot Cobranza + CRM | Cobranza alimenta pipeline de CRM | Deudores que pagan se convierten en oportunidades de venta |
| CRM + E-commerce | CRM gestiona clientes de la tienda | WhatsApp unificado para ventas online y presenciales |
| Lealtad + E-commerce | Puntos acumulables en tienda online | Cross-sell entre tienda fisica (POS) y online |
| Nomina + POS | Empleados pagados usan POS para gastar | Ecosistema cerrado: cobra con POS, paga con Nomina |

---

## Recursos Necesarios

### Equipo por Fase

| Fase | Periodo | Backend | Frontend | Total | Productos |
|------|---------|---------|----------|-------|-----------|
| Q2 2026 | Abr-Jun | 2 | 2 | 4 devs | POS + Bot Cobranza |
| Q3 2026 | Jul-Sep | 2 | 2 | 4 devs | Lealtad + CRM WhatsApp |
| Q4 2026 | Oct-Dic | 2 | 2 | 4 devs | CRM (final) + Nomina |
| Q1 2027 | Ene-Mar | 2 | 2 | 4 devs | Nomina (final) + E-commerce |

**Equipo constante**: 4 developers full-stack (2 backend, 2 frontend)
**Soporte**: 0.5 dev para mantenimiento de productos lanzados

### Infraestructura Adicional

| Recurso | Productos | Costo Mensual Est. |
|---------|-----------|-------------------|
| EC2 adicional (2 instancias) | Todos | $150 USD |
| CloudFront distributions (3 nuevos MFs) | POS, CRM, Nomina | $50 USD |
| WhatsApp Business API (mensajes) | Bot Cobranza, CRM, Lealtad | $200-500 USD |
| PAC Timbrado CFDI (Finkok) | POS, Nomina, E-commerce | $100 USD |
| S3 almacenamiento adicional | Todos | $30 USD |
| **Total infraestructura** | | **~$530-830 USD/mes** |

### Nuevos Repositorios a Crear

| Repo | Tipo | Producto |
|------|------|----------|
| mf-pos | Frontend (Angular MF) | POS Virtual |
| mf-crm | Frontend (Angular MF) | CRM WhatsApp |
| mf-nomina | Frontend (Angular MF) | Nomina Digital |
| mf-ecommerce | Frontend (Angular MF) | E-commerce Builder |

**Nota**: Los backends reutilizan repos existentes (covacha-payment, covacha-botia, covacha-core, covacha-crm, covacha-inventory). No se crean nuevos repos de backend.

---

## Quick Wins vs Inversiones Largas

### Quick Wins (Q2 2026)

| Producto | Semanas | Devs | Costo | Revenue Y1 | ROI |
|----------|---------|------|-------|-----------|-----|
| POS Virtual | 8 | 2 | $250K | $12M | **48x** |
| Bot Cobranza | 8 | 2 | $250K | $6M | **24x** |
| **Total Quick Wins** | **8** | **4** | **$500K** | **$18M** | **36x** |

**Porque son quick wins:**
- 75-80% de reutilizacion de codigo existente
- Solo 8 semanas de desarrollo cada uno
- Product-market fit validable rapidamente (MVP funcional en 4 semanas)
- POS: mercado masivo (6M comercios en Mexico)
- Bot Cobranza: dolor claro ($50B mercado de cobranza)

### Inversiones Medianas (Q3 2026)

| Producto | Semanas | Devs | Costo | Revenue Y1 | ROI |
|----------|---------|------|-------|-----------|-----|
| Lealtad | 10 | 2 | $300K | $7.2M | **24x** |
| CRM WhatsApp | 14 | 2 | $400K | $6M | **15x** |
| **Total Medianas** | **14** | **4** | **$700K** | **$13.2M** | **19x** |

**Justificacion:**
- Lealtad es complemento natural de POS (upsell organico)
- CRM tiene alto potencial de retention (sticky product)

### Inversiones Largas (Q4 2026 - Q1 2027)

| Producto | Semanas | Devs | Costo | Revenue Y1 | ROI |
|----------|---------|------|-------|-----------|-----|
| Nomina | 12 | 2 | $350K | $7.2M | **21x** |
| E-commerce | 16 | 3 | $500K | $14.4M | **29x** |
| **Total Largas** | **16** | **5** | **$850K** | **$21.6M** | **25x** |

**Justificacion:**
- Nomina requiere logica fiscal compleja (ISR, IMSS) pero tiene mercado grande
- E-commerce tiene el mayor revenue potencial pero necesita builder visual robusto

---

## Orden Recomendado de Desarrollo

### Recomendacion: Inicio Paralelo de Quick Wins

```
PRIORIDAD 1 (Mes 1-2):
  ├── POS Virtual       → 80% reuso, revenue rapido, base para Lealtad
  └── Bot Cobranza      → 75% reuso, mercado claro, base para CRM

PRIORIDAD 2 (Mes 3-5):
  ├── Programa Lealtad  → Complemento de POS, upsell natural
  └── CRM WhatsApp      → Producto sticky, largo ciclo de vida

PRIORIDAD 3 (Mes 5-8):
  ├── Nomina Digital    → Independiente, mercado grande
  └── E-commerce        → Mayor revenue pero mayor esfuerzo

MANTENIMIENTO CONTINUO:
  └── Productos lanzados: mejoras, bug fixes, onboarding
```

### Razonamiento del Orden

1. **POS + Bot Cobranza primero** porque:
   - Maximo reuso (75-80%), minimo riesgo
   - Revenue rapido para financiar productos siguientes
   - POS es prerequisito para Lealtad
   - Bot Cobranza valida el mercado de cobranza para CRM

2. **Lealtad + CRM segundo** porque:
   - Lealtad amplifica el valor de POS (upsell)
   - CRM es el producto mas "sticky" (alta retencion)
   - Ambos fortalecen el ecosistema WhatsApp

3. **Nomina + E-commerce tercero** porque:
   - Mayor complejidad tecnica
   - E-commerce necesita POS para checkout
   - Nomina es independiente y puede paralelizarse

---

## KPIs de Exito por Producto

### POS Virtual

| KPI | Target 3 meses | Target 6 meses | Target 12 meses |
|-----|---------------|-----------------|-----------------|
| Comercios activos | 200 | 1,000 | 5,000 |
| Transacciones/mes | 5,000 | 50,000 | 500,000 |
| MRR | $40K | $200K | $1M |
| Churn mensual | < 10% | < 7% | < 5% |
| NPS | > 40 | > 50 | > 60 |

### Bot Cobranza

| KPI | Target 3 meses | Target 6 meses | Target 12 meses |
|-----|---------------|-----------------|-----------------|
| Empresas activas | 50 | 200 | 500 |
| Tasa de recuperacion | 25% | 35% | 45% |
| MRR | $50K | $200K | $500K |
| Mensajes enviados/mes | 50K | 200K | 1M |
| Churn mensual | < 8% | < 5% | < 3% |

### CRM WhatsApp

| KPI | Target 3 meses | Target 6 meses | Target 12 meses |
|-----|---------------|-----------------|-----------------|
| Empresas activas | 100 | 300 | 1,000 |
| Conversaciones gestionadas/mes | 10K | 50K | 200K |
| MRR | $50K | $150K | $500K |
| Response time promedio | < 5 min | < 3 min | < 2 min |
| Churn mensual | < 7% | < 5% | < 3% |

### Programa de Lealtad

| KPI | Target 3 meses | Target 6 meses | Target 12 meses |
|-----|---------------|-----------------|-----------------|
| Comercios con programa | 100 | 500 | 2,000 |
| Clientes inscritos (total) | 5K | 50K | 500K |
| Tasa de canje | 15% | 25% | 35% |
| MRR | $30K | $150K | $600K |
| Incremento frecuencia de compra | 10% | 20% | 30% |

### Nomina Digital

| KPI | Target 3 meses | Target 6 meses | Target 12 meses |
|-----|---------------|-----------------|-----------------|
| Empresas activas | 50 | 300 | 2,000 |
| Empleados gestionados | 500 | 5,000 | 40,000 |
| Dispersiones exitosas/mes | 100 | 1,200 | 8,000 |
| MRR | $15K | $100K | $600K |
| Error rate en calculo | < 0.1% | < 0.05% | < 0.01% |

### E-commerce Builder

| KPI | Target 3 meses | Target 6 meses | Target 12 meses |
|-----|---------------|-----------------|-----------------|
| Tiendas publicadas | 100 | 500 | 3,000 |
| GMV (gross merchandise value) | $1M | $10M | $50M |
| MRR | $40K | $200K | $1.2M |
| Conversion rate promedio | 1% | 2% | 3% |
| Churn mensual | < 10% | < 7% | < 5% |

---

## Riesgos y Mitigaciones

### Riesgos Estrategicos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Lanzar 6 productos diluye el foco | Alta | Alto | Secuenciar: solo 2 productos en desarrollo a la vez |
| Equipo insuficiente (4 devs para 6 productos) | Media | Alto | Contratar 2 devs adicionales para Q3, o priorizar 4 productos |
| Mercado no responde como esperado | Media | Alto | MVP rapido, validar P-M fit antes de invertir en features |
| Competencia reacciona | Media | Medio | Moverse rapido (2 meses), iterar con feedback real |
| WhatsApp cambia policies/precios | Baja | Alto | Diversificar canales (Telegram, SMS), mantener WhatsApp como principal |

### Riesgos Tecnicos

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Infraestructura no escala | Baja | Alto | Auto-scaling, load testing antes de cada launch |
| Integraciones SAT/CFDI fallan | Media | Alto | PAC de respaldo, sandbox extensivo, tests automatizados |
| WhatsApp Business API rate limits | Media | Medio | Rate limiting propio mas conservador, queue management |
| Deuda tecnica acumulada | Alta | Medio | 20% del tiempo dedicado a refactor y tests |
| Seguridad (datos bancarios/fiscales) | Baja | Critico | Encriptacion, auditorias, OWASP, penetration testing |

### Riesgos de Mercado

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|-------------|---------|------------|
| Adoption lenta de SPEI QR | Media | Alto | Plan Free en POS, educacion al comerciante |
| PyMEs no pagan software | Alta | Medio | Freemium agresivo, ROI demostrable rapido |
| Regulacion cambia (CONDUSEF, SAT) | Media | Medio | Parametros configurables, actualizacion sin deploy |

---

## Revenue Proyectado

### Year 1 (Escenario Conservador)

| Producto | Q2 | Q3 | Q4 | Q1-2027 | **Total Y1** |
|----------|-----|-----|-----|---------|-------------|
| POS Virtual | $0 | $3M | $3M | $3M | **$9M** |
| Bot Cobranza | $0 | $1.5M | $1.5M | $1.5M | **$4.5M** |
| Lealtad | - | $0 | $1.8M | $1.8M | **$3.6M** |
| CRM WhatsApp | - | - | $0 | $1.5M | **$1.5M** |
| Nomina | - | - | $0 | $0 | **$0** |
| E-commerce | - | - | - | $0 | **$0** |
| **Total** | **$0** | **$4.5M** | **$6.3M** | **$7.8M** | **$18.6M** |

### Year 1 (Escenario Optimista)

| Producto | Q2 | Q3 | Q4 | Q1-2027 | **Total Y1** |
|----------|-----|-----|-----|---------|-------------|
| POS Virtual | $0.5M | $4M | $4M | $4M | **$12.5M** |
| Bot Cobranza | $0.3M | $2M | $2M | $2M | **$6.3M** |
| Lealtad | - | $0.5M | $2.5M | $2.5M | **$5.5M** |
| CRM WhatsApp | - | - | $0.5M | $2M | **$2.5M** |
| Nomina | - | - | $0 | $1M | **$1M** |
| E-commerce | - | - | - | $0 | **$0** |
| **Total** | **$0.8M** | **$6.5M** | **$9M** | **$11.5M** | **$27.8M** |

### Inversion vs Revenue

| Concepto | Monto |
|----------|-------|
| Inversion total desarrollo (6 productos) | $2.05M MXN |
| Inversion infraestructura (12 meses) | $120K MXN |
| Revenue Year 1 (conservador) | $18.6M MXN |
| Revenue Year 1 (optimista) | $27.8M MXN |
| **ROI conservador** | **8.5x** |
| **ROI optimista** | **12.7x** |
| **Break-even** | **Q3 2026 (mes 5-6)** |

---

## Resumen de Documentos Creados

| Producto | Archivo Epicas | Archivo YML | Epicas | User Stories |
|----------|---------------|-------------|--------|-------------|
| POS Virtual | POS-VIRTUAL-EPICS.md | pos-virtual.yml | 8 (EP-POS-001 a EP-POS-008) | 40 (US-POS-001 a US-POS-040) |
| Bot Cobranza | BOT-COBRANZA-EPICS.md | bot-cobranza.yml | 8 (EP-BC-001 a EP-BC-008) | 38 (US-BC-001 a US-BC-038) |
| CRM WhatsApp | CRM-WHATSAPP-EPICS.md | crm-whatsapp.yml | 8 (EP-CW-001 a EP-CW-008) | 42 (US-CW-001 a US-CW-042) |
| Lealtad | LEALTAD-EPICS.md | lealtad.yml | 7 (EP-LY-001 a EP-LY-007) | 35 (US-LY-001 a US-LY-035) |
| Nomina Digital | NOMINA-DIGITAL-EPICS.md | nomina-digital.yml | 8 (EP-NM-001 a EP-NM-008) | 38 (US-NM-001 a US-NM-038) |
| E-commerce Builder | ECOMMERCE-BUILDER-EPICS.md | ecommerce-builder.yml | 8 (EP-EC-001 a EP-EC-008) | 40 (US-EC-001 a US-EC-040) |
| **TOTAL** | | | **47 epicas** | **233 user stories** |

---

## Proximos Pasos

1. **Inmediato**: Revisar y aprobar prioridades con stakeholders
2. **Semana 1**: Crear issues en GitHub para EP-POS-001 a EP-POS-008 y EP-BC-001 a EP-BC-008
3. **Semana 1-2**: Asignar equipo a Q2 (POS + Bot Cobranza)
4. **Semana 2**: Comenzar desarrollo de POS Virtual y Bot de Cobranza en paralelo
5. **Mes 2**: Review de avance y ajuste de timeline Q3
6. **Trimestral**: Review de metricas y ajuste de roadmap
