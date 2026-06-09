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
