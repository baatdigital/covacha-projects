# Auditoria de Micro-Frontends Abandonados

**Fecha:** 2026-03-10
**Issue:** #138
**Autor:** Claude Code

---

## Resumen Ejecutivo

Se evaluaron 3 repositorios con posible abandono. Dos de ellos (`mf-payment` y `mf-payment-card`) no son micro-frontends Angular sino SDKs vanilla JS de pago, por lo que el nombre "mf-" es engañoso. El tercero (`mf-template`) es un boilerplate/template sin uso activo.

| Repo | Ultimo commit | Tipo real | En uso | Recomendacion |
|------|--------------|-----------|--------|---------------|
| mf-template | 2026-01-10 (2 meses) | Template Angular (boilerplate) | NO | ARCHIVE |
| mf-payment | 2026-02-14 (1 mes) | SDK vanilla JS (Web Component) | SI - mf-core index.html | KEEP (renombrar) |
| mf-payment-card | 2026-02-14 (1 mes) | SDK vanilla JS (Web Component) | SI - consumido por mf-payment | MERGE en mf-payment |

---

## 1. mf-template

### Datos

| Propiedad | Valor |
|-----------|-------|
| Package name | `@covacha/mf-template` |
| Version | 0.0.1 |
| Ultimo commit | 2026-01-10 (hace 2 meses) |
| Total commits | 1 (`feat: initial micro-frontend template for Covacha Platform`) |
| Archivos TS | 12 |
| Federation config | SI (Native Federation) |
| Deploy pipeline | SI (deploy.yml) - pero con valores placeholder (`MODULE_NAME: 'template'`) |
| Puerto dev | 4201 (conflicto con mf-auth) |

### Proposito

Template/boilerplate para crear nuevos micro-frontends. Contiene la estructura hexagonal base (domain, application, infrastructure, presentation, core, shared-state, remote-entry) pero sin logica real.

### Referencias externas

- **NO** referenciado en `mf-core/federation.config.js`
- **NO** referenciado en ninguna ruta de mf-core
- **NO** referenciado por ningun otro MF
- **NO** tiene remotes configurados en su propio federation config

### Analisis

- Solo tiene 1 commit, nunca se itero despues de la creacion inicial.
- El deploy pipeline tiene valores placeholder sin personalizar.
- El puerto 4201 colisiona con mf-auth, lo que indica que nunca se uso en desarrollo junto al ecosistema.
- Cualquier MF nuevo creado en los ultimos meses NO uso este template (ej: mf-marketing, mf-dashboard tienen su propia estructura).

### Recomendacion: ARCHIVE

**Razon:** Boilerplate con 1 solo commit, sin uso real, puerto en conflicto. Si se necesita un template en el futuro, es mejor usar un MF existente funcional como referencia (ej: mf-marketing) o crear un `gh repo create --template`.

**Accion:**
1. `gh repo archive baatdigital/mf-template`
2. Documentar en el README que se debe usar mf-marketing como referencia para nuevos MFs

---

## 2. mf-payment

### Datos

| Propiedad | Valor |
|-----------|-------|
| Package name | `@superpago/payment-sdk` |
| Version | 1.0.0 |
| Ultimo commit | 2026-02-14 (hace ~1 mes) |
| Total commits | 10+ |
| Archivos JS/TS | 50 |
| Federation config | NO - No es un MF Angular |
| Deploy pipeline | SI - `deploy.yml` a S3 bucket `superpago-cdn` con CloudFront `E3L7FIY6TU68P4` |
| CDN URL | `https://cdn.superpago.com.mx/sdk/superpago/latest/superpago.min.js` |

### Proposito

**NO es un micro-frontend.** Es un SDK de pagos (Web Component vanilla JS) que permite a sitios externos integrar pagos de servicios con OpenPay. Se distribuye via CDN como `<superpago-payment>`.

### Referencias externas

- **SI** - Cargado directamente en `mf-core/src/index.html`:
  ```html
  <script src="https://cdn.superpago.com.mx/sdk/superpago/latest/superpago.min.js" async></script>
  ```
- **SI** - Bundleado como fallback en `mf-core/src/assets/sdk/superpago.min.js` (267KB)
- **SI** - Carga dinamicamente `mf-payment-card` via CDN cuando se necesita pago con tarjeta
- Tiene su propio CloudFront distribution (`E3L7FIY6TU68P4`)

### Analisis

- Este repo esta ACTIVO y en USO en produccion.
- El nombre `mf-payment` es engañoso porque no es un micro-frontend Angular con Module Federation.
- Es un SDK publico que se embebe en cualquier pagina web.
- Tiene arquitectura propia: domain, application, infrastructure, UI (Web Components).
- Depende de `mf-payment-card` como sub-componente para pago con tarjeta.

### Recomendacion: KEEP (con renombramiento)

**Razon:** En uso activo en produccion, cargado en mf-core. No debe archivarse.

**Accion sugerida:**
1. Renombrar repo a `superpago-sdk` o `payment-sdk` para reflejar que NO es un micro-frontend
2. Actualizar referencia en covacha-projects/repos/
3. Considerar MERGE de mf-payment-card en este repo (ver seccion 3)

---

## 3. mf-payment-card

### Datos

| Propiedad | Valor |
|-----------|-------|
| Package name | `@superpago/payment-card` |
| Version | 1.0.0 |
| Ultimo commit | 2026-02-14 (hace ~1 mes) |
| Total commits | 10+ |
| Archivos JS/TS | 11 |
| Federation config | NO - No es un MF Angular |
| Deploy pipeline | SI - `deploy.yml` a S3 bucket `superpago-cdn-card` con CloudFront `E2T71ML4VVEFNN` |
| CDN URL | `https://cdn.superpago.com.mx/sdk/sp-payment-card/latest/sp-payment-card.min.js` |

### Proposito

**NO es un micro-frontend.** Es un Web Component vanilla JS (`<sp-card-payment>`) para captura de datos de tarjeta con OpenPay. Incluye tokenizacion, 3D Secure, y billing. Es cargado dinamicamente por `mf-payment` cuando el usuario elige pagar con tarjeta.

### Referencias externas

- **NO** referenciado directamente en mf-core routes ni federation config
- **SI** - Bundleado como fallback en `mf-core/src/assets/sdk/sp-payment-card.min.js` (65KB)
- **SI** - Cargado dinamicamente por `mf-payment` via CDN:
  ```js
  const SP_CARD_PAYMENT_CDN = 'https://cdn.superpago.com.mx/sdk/sp-payment-card/latest/sp-payment-card.min.js';
  ```
- Tiene su propio S3 bucket (`superpago-cdn-card`) y CloudFront distribution (`E2T71ML4VVEFNN`)

### Analisis

- Este repo esta ACTIVO pero es un sub-componente de `mf-payment`, no un producto independiente.
- Solo tiene 11 archivos fuente - es muy pequeno para justificar un repo separado.
- Su unico consumidor es `mf-payment`, no se usa directamente en ningun otro lugar.
- Tener un S3 bucket, CloudFront distribution y pipeline separado para 11 archivos es overhead innecesario.

### Recomendacion: MERGE en mf-payment

**Razon:** Sub-componente con un solo consumidor (mf-payment), 11 archivos, overhead de infra desproporcionado.

**Accion:**
1. Mover `src/` de mf-payment-card a `mf-payment/packages/payment-card/` o `mf-payment/src/card/`
2. Unificar pipeline de deploy para generar ambos bundles desde un solo repo
3. Consolidar S3 buckets (usar `superpago-cdn` con prefijo `/sdk/sp-payment-card/`)
4. Archivar `mf-payment-card` despues del merge
5. Actualizar la URL de CDN en `mf-payment` si cambia

---

## Impacto de las Acciones

### Infraestructura que se puede consolidar

| Recurso | Actual | Despues del merge |
|---------|--------|-------------------|
| Repos GitHub | 3 | 1 (mf-payment renombrado) |
| S3 Buckets | 3 (cdn, cdn-card, cdn-microfrontends) | 1 (superpago-cdn con prefijos) |
| CloudFront Distributions | 3 | 1-2 |
| Deploy Pipelines | 3 | 1 |

### Riesgos

- **mf-template**: Riesgo CERO al archivar. No tiene consumidores.
- **mf-payment-card merge**: Riesgo BAJO. Solo requiere actualizar la URL de CDN dentro de mf-payment si cambia la ruta S3. Los consumidores externos (mf-core) cargan mf-payment que a su vez carga payment-card, asi que el cambio es interno.
- **Renombrar mf-payment**: Riesgo BAJO. No afecta URLs de CDN ni funcionalidad. Solo cambia el nombre del repo en GitHub.

---

## Siguiente Paso

1. Aprobar este analisis
2. Archivar `mf-template` via `gh repo archive`
3. Planificar merge de `mf-payment-card` en `mf-payment` (1-2 horas de trabajo)
4. Renombrar `mf-payment` a `payment-sdk` o `superpago-sdk`
5. Actualizar `covacha-projects/repos/` con los cambios
