# 🧼 White Clean — Réplica Píxel-Perfecta y 100% Autohospedada

Este proyecto es una copia exacta e impecable de la web de **White Clean** (`www.whiteclean.com.mx`), libre de dependencias externas del ecosistema de Webflow. Está diseñada para ser ultrarrápida, moderna, autohospedada de forma local y 100% compatible con **Vercel** y **GitHub**.

---

## 🚀 Características del Proyecto
*   **Fidelidad Visual Absoluta (100%):** Mantiene la tipografía Montserrat/Raleway/Exo, degradados, banners parallax fijos, menús desplegables e interactividad idéntica a Webflow.
*   **Independencia de CDN:** Todas las imágenes, iconos SVG, tipografías, estilos y scripts JS se cargan localmente desde la carpeta `assets/`, `css/` y `js/` (sin llamadas preconnect a Webflow).
*   **Buscador Inteligente Local:** Motor de búsqueda client-side prémium integrado en `search.html` que indexa de forma instantánea las 20 páginas y 3 artículos de blog locales.
*   **Formulario de Cotización Inteligente:** Intercepta envíos y redirige de forma fluida a WhatsApp con un mensaje estructurado con Markdown.
*   **Clean URLs:** Configurado con `vercel.json` para eliminar la extensión `.html` de la barra de navegación (`/blog` carga `blog.html`, `/post/detallado-automotriz-premium` carga `post/detallado-automotriz-premium.html`).

---

## 💻 Ejecución Local con Clean URLs

Para probar el sitio localmente emulando las URLs limpias sin las extensiones `.html`:

### Opción 1: Usando Vercel CLI (Recomendado)
Si tienes instalado Vercel CLI, ejecuta en la terminal dentro de esta carpeta:
```bash
vercel dev
```
Esto abrirá un servidor local (típicamente en `http://localhost:3000`) con soporte completo para la configuración de `vercel.json`.

### Opción 2: Usando un Servidor de Desarrollo en Node.js
Puedes usar un servidor estático rápido que soporte Clean URLs:
```bash
npx servor --secure
# o usando serve:
npx serve -s .
```

### Opción 3: Servidor Python Estándar
Si usas el comando tradicional de Python:
```bash
python3 -m http.server 8000
```
*Nota: Para navegar localmente con este servidor estándar, deberás ingresar las rutas completas con `.html` (ej: `http://localhost:8000/blog.html`) ya que no tiene motor de reescritura de URLs limpias.*

---

## 📤 Despliegue en Vercel & GitHub

### 1. Subir a GitHub
Puedes crear un repositorio en tu cuenta de GitHub y subir el contenido de la carpeta `web/`:
```bash
git init
git add .
git commit -m "Initial commit of WhiteClean clean clone"
git branch -M main
git remote add origin <tu-repositorio-url>
git push -u origin main
```

### 2. Publicar en Vercel
1. Ve a tu panel de **Vercel** (`vercel.com`).
2. Haz clic en **Add New** > **Project**.
3. Importa el repositorio de GitHub que acabas de subir.
4. En **Build and Development Settings**, si subiste únicamente el contenido de la carpeta `web/` como raíz, deja los valores por defecto. Si subiste el proyecto completo con carpetas padre, selecciona `web` como la **Root Directory**.
5. Haz clic en **Deploy**. ¡Listo! Tu web estará publicada con URLs limpias de forma instantánea.

---

## 📁 Estructura del Directorio Activo
*   `/` - Las 17 páginas HTML principales de la web.
*   `/post/` - Los 3 artículos del blog totalmente adaptados y responsivos.
*   `/css/` - Hojas de estilo optimizadas y limpias (`whiteclean.css`, `webflow.css`, `style.css` personalizado).
*   `/js/` - Lógica de interactividad nativa (`app.js` vanilla JS).
*   `/assets/` - Todo el contenido multimedia (iconos, imágenes, SVG) de forma local.
