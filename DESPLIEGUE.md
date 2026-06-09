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
