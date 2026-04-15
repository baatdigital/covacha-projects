# Manual de Usuario: Cobros y Links de Pago

## BAAT Digital - Guia rapida para cobrar a tus clientes

---

## Que puedes hacer con este modulo?

Con el modulo de **Cobro** puedes:

1. **Generar un Link de Pago** - Creas una URL que envias a tu cliente por WhatsApp, email o cualquier medio. Tu cliente abre el link, ingresa su tarjeta y paga. Asi de facil.

2. **Cobro Directo** - Si tienes al cliente al telefono o en persona, ingresas el monto y los datos de su tarjeta directamente. El cobro se procesa al instante.

---

## Antes de empezar

Necesitas:
- Acceso al panel de BAAT Digital: `https://app.baatdigital.com.mx`
- Tener un cliente creado en el sistema
- Conexion a internet

---

## PASO 1: Acceder al modulo de Cobro

1. Inicia sesion en **app.baatdigital.com.mx**
2. En el menu lateral, selecciona **Marketing**
3. Haz clic en el **cliente** al que deseas cobrar
4. Una vez dentro del cliente, haz clic en el icono de **engrane** (Configuracion/Settings) en la parte superior
5. En el menu lateral de configuracion, busca y haz clic en **"Cobro"**
   - Es el ultimo item del menu, debajo de "Inteligencia Artificial"
   - Tiene un icono de tarjeta de credito

> **Ruta directa:** Si conoces el ID del cliente, puedes ir directamente a:
> `https://app.baatdigital.com.mx/marketing/clients/{ID_CLIENTE}/settings?section=cobro`

---

## OPCION A: Generar un Link de Pago

Usa esta opcion cuando quieras enviarle un link a tu cliente para que pague por su cuenta.

### Paso 1: Seleccionar "Link de Pago"

Al entrar al modulo de Cobro, veras dos botones grandes:
- **Link de Pago** (icono de cadena) - Selecciona este
- **Cobro Directo** (icono de tarjeta)

Haz clic en **"Link de Pago"**. Se resaltara en morado.

### Paso 2: Llenar los datos del cobro

Veras un formulario con 4 campos:

| Campo | Que poner | Ejemplo |
|-------|-----------|---------|
| **Monto a cobrar (MXN)** | El monto en pesos que quieres cobrar | `2500` |
| **Descripcion del cobro** | Una descripcion corta de que es el pago | `Paquete SEO mensual marzo` |
| **Email del cliente** (opcional) | El correo de tu cliente | `maria@empresa.com` |
| **Nombre del cliente** (opcional) | El nombre de tu cliente | `Maria Lopez` |

### Paso 3: Revisar las comisiones

Debajo del formulario aparece un **recuadro gris** con el desglose de comisiones:

```
Monto base                    $2,500.00
Comision Openpay               $  87.58
Comision SuperPago             $   1.50
─────────────────────────────────────────
Total a cobrar                 $2,589.08 MXN
```

> **Nota sobre comisiones:**
> - **Openpay** cobra 2.9% + $2.50 MXN + IVA por cada transaccion
> - **SuperPago** cobra $1.50 MXN adicional
> - Estas comisiones se suman al monto base. Tu cliente pagara el total.

### Paso 4: Generar el link

Haz clic en el boton morado **"Generar Link de Pago"**.

Espera unos segundos. Aparecera un recuadro verde con:
- La **URL del link** (algo como `https://app.baatdigital.com.mx/baatdigital/pay/R1I5A4LN`)
- Un boton **"Copiar"** para copiar el link al portapapeles

### Paso 5: Compartir el link

Haz clic en **"Copiar"** y el boton cambiara a **"Copiado!"**.

Ahora puedes pegar ese link en:
- **WhatsApp** - Envialo por mensaje directo
- **Email** - Pegalo en un correo
- **SMS** - Envialo por mensaje de texto
- **Cualquier medio** - El link funciona en cualquier navegador

### Que ve tu cliente?

Cuando tu cliente abre el link:

1. Ve una pagina con el logo de **BAAT Digital**
2. Ve la **descripcion** del cobro y el **monto total**
3. Ve un formulario para ingresar los datos de su tarjeta:
   - Numero de tarjeta
   - Fecha de vencimiento
   - Codigo CVV
4. Hace clic en **"Pagar $X,XXX.XX MXN"**
5. Si el banco requiere verificacion (3D Secure), se redirige al sitio del banco
6. Al completar el pago, ve un mensaje de **"Pago exitoso"**

---

## OPCION B: Cobro Directo

Usa esta opcion cuando quieras cobrar inmediatamente (por ejemplo, si tienes al cliente al telefono dictandote los datos de su tarjeta).

### Paso 1: Seleccionar "Cobro Directo"

En el modulo de Cobro, haz clic en **"Cobro Directo"** (icono de tarjeta). Se resaltara en morado.

### Paso 2: Ingresar el monto

Llena los dos campos:

| Campo | Que poner | Ejemplo |
|-------|-----------|---------|
| **Monto a cobrar (MXN)** | El monto en pesos | `1500` |
| **Descripcion** | De que es el cobro | `Cobro mensualidad abril` |

### Paso 3: Revisar comisiones

Igual que con el link, veras el desglose de comisiones automaticamente.

### Paso 4: Llenar datos de la tarjeta

Debajo aparece un formulario de tarjeta (proporcionado por OpenPay):
- **Numero de tarjeta** - Los 16 digitos de la tarjeta
- **Fecha de vencimiento** - MM/AA
- **CVV** - Los 3 o 4 digitos de seguridad (atras de la tarjeta)
- **Nombre del titular** - Como aparece en la tarjeta

### Paso 5: Procesar el cobro

Haz clic en **"Cobrar $X,XXX.XX MXN"**.

Espera unos segundos. Si el cobro es exitoso, aparecera un mensaje verde:

```
Cobro procesado exitosamente. ID: xxxxxxxx-xxxx-xxxx
```

Si hay algun error (tarjeta declinada, fondos insuficientes), aparecera un mensaje rojo con la descripcion del problema.

---

## Historial de Cobros

En la parte inferior del modulo de Cobro, siempre veras una tabla con los **ultimos cobros** realizados:

| Fecha | Tipo | Descripcion | Monto | Estado |
|-------|------|-------------|-------|--------|
| 07/04/2026 | Link | Paquete SEO mensual | $2,500.00 | active |
| 07/04/2026 | Directo | Cobro mensualidad | $1,500.00 | paid |

- **Tipo "Link"** = Se genero un link de pago
- **Tipo "Directo"** = Se cobro directamente con tarjeta
- **Estado "active"** = El link esta activo, esperando pago
- **Estado "paid"** = Ya fue pagado

---

## Preguntas Frecuentes

### Cuanto tarda en llegar el dinero?
El dinero se deposita en tu cuenta de OpenPay en **24-48 horas habiles** despues de que el cliente paga.

### El link tiene fecha de expiracion?
Por defecto los links no expiran. Puedes compartirlo cuando quieras.

### Puedo cobrar en dolares?
Actualmente solo se puede cobrar en **pesos mexicanos (MXN)**.

### Que pasa si el cliente tiene problemas para pagar?
- Verificar que la tarjeta tenga fondos suficientes
- Verificar que la tarjeta sea Visa o Mastercard
- Si aparece pantalla de "3D Secure", el cliente debe completar la verificacion con su banco
- Si persiste el problema, intentar con otra tarjeta

### Cuanto es la comision?
Para un cobro de **$1,000 MXN**:
- Openpay: ~$38.04 MXN (2.9% + $2.50 + IVA)
- SuperPago: $1.50 MXN
- **Total comision: ~$39.54 MXN**
- **Tu cliente paga: $1,039.54 MXN**

### Puedo cancelar un link de pago?
Actualmente no hay opcion de cancelar desde el panel. Si necesitas cancelar un link, contacta al equipo de soporte.

### Es seguro?
Si. Los pagos son procesados por **OpenPay** (propiedad de BBVA), que cumple con los estandares de seguridad PCI DSS. Los datos de tarjeta nunca se almacenan en nuestros servidores.

---

## Resumen Rapido

```
GENERAR LINK DE PAGO:
Settings → Cobro → Link de Pago → Monto + Descripcion → Generar → Copiar → Enviar al cliente

COBRO DIRECTO:
Settings → Cobro → Cobro Directo → Monto → Datos de tarjeta → Cobrar
```

---

*Documento generado el 7 de abril de 2026*
*BAAT Digital - Agencia de Marketing Digital*
*Soporte: soporte@baatdigital.com.mx*
