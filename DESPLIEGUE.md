# Despliegue de Palacios Video

Este documento recoge los pasos manuales para publicar y operar la web comercial
de Palacios Video. No escribas claves ni secretos en el codigo: todo lo sensible
va en variables de entorno del proveedor correspondiente.

## Fase 1 - Publicar la landing en Render

### Que se ha preparado en el repo

- `web/palacios-video-landing.html`: landing estatica publicable.
- `web/index.html`: entrada raiz que abre la landing.
- `render.yaml`: configuracion Blueprint de Render para servir `./web` como
  sitio estatico.

### Cuentas necesarias

1. Cuenta de GitHub con este repositorio subido.
2. Cuenta de Render: https://render.com

### Pasos clic a clic en GitHub

1. Abre GitHub.
2. Crea un repositorio nuevo o abre el repositorio donde vas a subir este
   proyecto.
3. Sube el codigo de esta carpeta.
4. Confirma que en GitHub aparecen estos archivos:
   - `render.yaml`
   - `web/index.html`
   - `web/palacios-video-landing.html`

### Pasos clic a clic en Render

1. Entra en https://dashboard.render.com
2. Inicia sesion o crea una cuenta.
3. Conecta tu cuenta de GitHub si Render te lo pide:
   - Pulsa tu avatar o el selector de cuenta.
   - Ve a `Account Settings`.
   - Entra en `Git Providers`.
   - Conecta GitHub.
   - Autoriza Render para acceder al repo de Palacios Video.
4. En el dashboard de Render, pulsa `New +`.
5. Elige `Blueprint`.
6. Selecciona el repositorio de Palacios Video.
7. Render detectara `render.yaml`.
8. Revisa que el servicio se llame `palacios-video-landing`.
9. Pulsa `Apply`.
10. Espera a que Render cree el servicio.
11. Cuando termine, abre la URL publica que Render muestra en el servicio.

### Configuracion esperada en Render

Si decides crear el sitio manualmente en vez de usar Blueprint:

1. Pulsa `New +`.
2. Elige `Static Site`.
3. Selecciona el repo.
4. Rellena:
   - `Name`: `palacios-video-landing`
   - `Branch`: `master` o la rama que uses
   - `Build Command`: dejar vacio
   - `Publish Directory`: `web`
5. Pulsa `Create Static Site`.

### Verificacion manual

1. Abre la URL publica de Render.
2. Comprueba que carga Palacios Video.
3. Comprueba que el boton `Ver planes` baja a la seccion de planes.

### Pendiente manual

- Yo no puedo verificar el despliegue real porque depende de tu cuenta de
  Render y del repo remoto conectado.

## Fase 2 - Pagos con Stripe Payment Links

### Que se ha preparado en el repo

- Los botones de `Creator`, `Pro` y `Agencia` ya leen sus URLs desde:
  - `STRIPE_LINK_CREATOR`
  - `STRIPE_LINK_PRO`
  - `STRIPE_LINK_AGENCIA`
- `web/build-stripe-links.js` genera `web/stripe-links.js` durante el build de
  Render.
- `render.yaml` ejecuta `node web/build-stripe-links.js` antes de publicar la
  carpeta `web`.

### Cuenta necesaria

1. Cuenta de Stripe: https://dashboard.stripe.com
2. La landing ya desplegada en Render.

### Crear los productos en Stripe

1. Entra en https://dashboard.stripe.com
2. Inicia sesion.
3. En el menu lateral, entra en `Product catalog`.
4. Pulsa `Add product`.
5. Crea el producto `Palacios Video Creator`:
   - `Name`: `Palacios Video Creator`
   - `Pricing model`: `Standard pricing`
   - `Price`: `29`
   - `Currency`: `EUR`
   - `Recurring`: mensual
6. Pulsa `Save product`.
7. Repite el proceso para:
   - `Palacios Video Pro`, `79 EUR`, mensual.
   - `Palacios Video Agencia`, `199 EUR`, mensual.

### Crear Payment Links

Para cada producto:

1. En Stripe, entra en `Payment Links`.
2. Pulsa `New`.
3. Selecciona el producto correspondiente.
4. Cantidad: `1`.
5. Asegurate de que el precio es mensual recurrente.
6. En `After payment`, deja una pagina de confirmacion simple por ahora.
7. Pulsa `Create link`.
8. Copia el enlace generado. Sera parecido a:
   `https://buy.stripe.com/...`

Guarda cada enlace con esta correspondencia:

- Creator -> `STRIPE_LINK_CREATOR`
- Pro -> `STRIPE_LINK_PRO`
- Agencia -> `STRIPE_LINK_AGENCIA`

### Meter las variables en Render

1. Entra en https://dashboard.render.com
2. Abre el servicio `palacios-video-landing`.
3. En el menu del servicio, entra en `Environment`.
4. Pulsa `Add Environment Variable`.
5. Anade:
   - `Key`: `STRIPE_LINK_CREATOR`
   - `Value`: pega el Payment Link de Creator.
6. Pulsa otra vez `Add Environment Variable`.
7. Anade:
   - `Key`: `STRIPE_LINK_PRO`
   - `Value`: pega el Payment Link de Pro.
8. Pulsa otra vez `Add Environment Variable`.
9. Anade:
   - `Key`: `STRIPE_LINK_AGENCIA`
   - `Value`: pega el Payment Link de Agencia.
10. Guarda los cambios.

### Redesplegar en Render

1. En el servicio de Render, entra en `Manual Deploy`.
2. Pulsa `Deploy latest commit`.
3. Espera a que termine el build.
4. Abre la URL publica de la landing.
5. Baja a `Planes mensuales`.
6. Pulsa cada boton:
   - `Elegir Creator`
   - `Elegir Pro`
   - `Elegir Agencia`
7. Cada uno debe abrir su checkout de Stripe.

### Pendiente manual

- Yo no puedo crear tus productos ni Payment Links porque dependen de tu cuenta
  de Stripe.
- Yo no puedo verificar los botones reales hasta que pegues las tres variables
  de entorno en Render y redespliegues.

## Fase 3 - Supabase Auth, base de datos y webhook de Stripe

### Que se ha preparado en el repo

- `supabase/schema.sql`: tablas de suscripciones y uso mensual.
- Login y registro con Supabase Auth en `web/palacios-video-landing.html`.
- Selector de idioma ES/EN en la landing.
- `api/server.js`: endpoint `POST /stripe/webhook` para recibir eventos de
  Stripe y actualizar Supabase.
- `api/package.json`: dependencias del backend.
- `render.yaml`: servicio adicional `palacios-video-api`.

### Importante sobre Stripe

Para asociar un pago a un usuario:

1. El usuario debe iniciar sesion en la landing antes de elegir plan.
2. La landing manda `client_reference_id` a Stripe con el `user_id` de Supabase.
3. Cada Payment Link debe tener metadata:
   - `plan=creator`
   - `plan=pro`
   - `plan=agencia`

Sin esa metadata, el webhook recibe el pago pero no sabe que plan activar.

### Crear proyecto en Supabase

1. Entra en https://supabase.com
2. Inicia sesion o crea una cuenta.
3. Pulsa `New project`.
4. Elige tu organizacion.
5. Rellena:
   - `Project name`: `palacios-video`
   - `Database Password`: genera una contrasena fuerte y guardala.
   - `Region`: elige la mas cercana a tus usuarios.
6. Pulsa `Create new project`.
7. Espera a que Supabase termine de crear el proyecto.

### Ejecutar el schema SQL

1. Entra en tu proyecto de Supabase.
2. En el menu lateral, pulsa `SQL Editor`.
3. Pulsa `New query`.
4. Abre en tu ordenador el archivo:
   `supabase/schema.sql`
5. Copia todo el contenido.
6. Pegalo en el editor SQL de Supabase.
7. Pulsa `Run`.
8. Comprueba que se crean estas tablas:
   - `suscripciones`
   - `uso_mensual`

### Sacar las claves de Supabase

1. En Supabase, entra en `Project Settings`.
2. Entra en `API`.
3. Copia:
   - `Project URL` -> sera `SUPABASE_URL`
   - `anon public` -> sera `SUPABASE_ANON_KEY`
   - `service_role` -> sera `SUPABASE_SERVICE_ROLE_KEY`

Nunca pegues `service_role` en el codigo ni en la landing. Solo va en el
backend `palacios-video-api`.

### Meter variables de Supabase en Render

En Render tienes dos servicios:

- `palacios-video-landing`
- `palacios-video-api`

#### Variables para `palacios-video-landing`

1. Render -> abre `palacios-video-landing`.
2. Entra en `Environment`.
3. Anade:
   - `SUPABASE_URL` = pega `Project URL`
   - `SUPABASE_ANON_KEY` = pega `anon public`
4. Guarda.

#### Variables para `palacios-video-api`

1. Render -> abre `palacios-video-api`.
2. Entra en `Environment`.
3. Anade:
   - `SUPABASE_URL` = pega `Project URL`
   - `SUPABASE_SERVICE_ROLE_KEY` = pega `service_role`
4. Guarda.

### Crear o actualizar el servicio API en Render

Si usas Blueprint:

1. Haz `git push`.
2. Render deberia detectar el nuevo servicio `palacios-video-api`.
3. Aplica los cambios del Blueprint.

Si lo creas manualmente:

1. Render -> `New +`.
2. Elige `Web Service`.
3. Selecciona el mismo repo.
4. Rellena:
   - `Name`: `palacios-video-api`
   - `Runtime`: `Node`
   - `Build Command`: `cd api && npm install`
   - `Start Command`: `cd api && npm start`
5. Crea el servicio.
6. Mete las variables indicadas arriba.

Cuando este desplegado, Render te dara una URL como:

`https://palacios-video-api.onrender.com`

Comprueba que funciona abriendo:

`https://palacios-video-api.onrender.com/health`

Debe responder algo parecido a:

`{"ok":true,"service":"palacios-video-api"}`

### Variables de Stripe para `palacios-video-api`

1. En Stripe, entra en `Developers`.
2. Entra en `API keys`.
3. Copia `Secret key`.
4. En Render -> `palacios-video-api` -> `Environment`, anade:
   - `STRIPE_SECRET_KEY` = pega la secret key de Stripe.

### Configurar webhook en Stripe

1. En Stripe, entra en `Developers`.
2. Entra en `Webhooks`.
3. Pulsa `Add endpoint`.
4. En `Endpoint URL`, pega:
   `https://palacios-video-api.onrender.com/stripe/webhook`
5. En eventos, selecciona:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
6. Pulsa `Add endpoint`.
7. En la pagina del webhook, busca `Signing secret`.
8. Pulsa `Reveal`.
9. Copia el valor.
10. En Render -> `palacios-video-api` -> `Environment`, anade:
    - `STRIPE_WEBHOOK_SECRET` = pega el signing secret.
11. Guarda y redeploya `palacios-video-api`.

### Anadir metadata plan a los Payment Links

Para cada Payment Link:

1. Stripe -> `Payment Links`.
2. Abre el Payment Link de Creator.
3. Entra en opciones avanzadas o metadata.
4. Anade metadata:
   - `plan`: `creator`
5. Guarda.
6. Repite:
   - Pro -> `plan`: `pro`
   - Agencia -> `plan`: `agencia`

### Redesplegar todo

1. Haz `git push`.
2. En Render, redeploya `palacios-video-landing`.
3. En Render, redeploya `palacios-video-api`.
4. Abre la landing.
5. Crea una cuenta en la seccion `Cuenta`.
6. Confirma el email si Supabase lo exige.
7. Inicia sesion.
8. Pulsa un plan.
9. Completa un pago de prueba en Stripe.
10. En Supabase, abre `Table Editor` -> `suscripciones`.
11. Verifica que aparece una fila con:
    - `user_id`
    - `plan`
    - `stripe_customer_id`
    - `estado`
    - `horas_limite`
    - `renovacion`

### Pendiente manual

- Yo no puedo crear tu proyecto Supabase ni ejecutar el SQL en tu cuenta.
- Yo no puedo copiar tus claves de Stripe o Supabase.
- Yo no puedo verificar un pago real hasta que configures el webhook y hagas
  un checkout de prueba.
