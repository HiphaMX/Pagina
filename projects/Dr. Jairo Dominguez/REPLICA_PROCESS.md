# 🚀 REPLICA PROCESS: The "Ultrapro" Migration Playbook — Dr. Jairo Domínguez

Este documento registra paso a paso el proceso metodológico y técnico ejecutado para clonar y migrar el 100% de la web del **Dr. Jairo Domínguez Arroyo** desde Webflow hacia la arquitectura moderna de HiphaMX en FastAPI y Vercel.

---

## 0. Prerrequisitos y Creación de Entorno
1. **Directorio del Proyecto:** `projects/Dr. Jairo Dominguez/`
2. **Subdirectorios Creados:**
   - `projects/Dr. Jairo Dominguez/assets/`: Repositorio local de todos los recursos estáticos.
   - `projects/Dr. Jairo Dominguez/post/`: Contenedor de los 15 artículos médicos del blog.
3. **Archivos de Estrategia y Memoria:**
   - `BRIEF_MEMORIA.md`, `PROJECT_INTAKE_FORM.md`, `BRAND_DNA_QUESTIONNAIRE.md`, `brand_brief.md`, `voice_brief.md`, `llms.txt`, `robots.txt`, `sitemap.xml`, `vercel.json`.

---

## 1. Extracción y Descarga Exhaustiva (24 Páginas)
- **Páginas Raíz e Informativas (9):**
  - `index.html` (Portada principal con sliders interactivos, sedes y formulario)
  - `diagnostico.html`
  - `cirugias.html`
  - `blog.html`
  - `aviso-de-privacidad.html`
  - `preguntas-frecuentes.html`
  - `trayectoria-profesional.html`
  - `gracias-por-contactarnos.html`
  - `404.html`
- **Artículos Clínicos del Blog en `post/` (15):**
  - `calculos-en-la-vejiga.html`, `calculos-renales.html`, `cancer-de-pene.html`, `cancer-de-prostata.html`, `cancer-de-rinon.html`, `cancer-de-testiculo.html`, `cancer-de-vejiga.html`, `cirugia-endourologica.html`, `cirugia-holep.html`, `cirugia-laparoscopica.html`, `cirugia-robotica.html`, `crecimiento-prostatico.html`, `hablemos-de-la-vasectomia.html`, `paternidad-satisfecha.html`, `volver-a-casa-despues-de-una-cirugia-abierta.html`.

---

## 2. Higienización e Independencia de Assets (89 Archivos Locales)
1. **Detección y Descarga:**
   - Extracción de todas las etiquetas `<img>`, `srcset`, `<link href>`, `<script src>` y estilos internos `url(...)`.
   - Descarga de estilos compilados de Webflow (`urologia-dr-jairo-dominguez.webflow.shared.55e16d678.min.css`) y recursos referenciados (`africamap2.svg`, `iconz.svg`, `backgrowd.jpg`).
   - Descarga e integración local de `jquery-3.5.1.min.dc5e7f18c8.js`, `webfont.js`, chunks de interacción (`webflow.schunk.3967bd5d27f21cce.js`, `webflow.1e9ce508.26428c429af0f870.js`) y el currículum médico oficial en PDF (`JDA20.pdf`, 2.6 MB).
2. **Reescritura de Rutas:**
   - Páginas de raíz: Mapeadas a `assets/<archivo>`.
   - Páginas de subdirectorios (`post/`): Mapeadas a `../assets/<archivo>`.
   - Eliminación de etiquetas obsoletas `<link rel="preconnect" href="https://cdn.prod.website-files.com">`.
   - Resultado: **0 dependencias externas a servidores de Webflow.**

---

## 3. Integración con Backend FastAPI y Fallback Seguro de Correo
1. **Formularios Automatizados (`contact-form.js`):**
   - Script cliente inyectado en las 24 páginas HTML para capturar envíos tanto del formulario en página como del modal emergente.
   - Prevención de spam mediante campo Honeypot.
   - Envío asíncrono vía `POST /api/projects/jairo-dominguez`.
2. **Esquema Pydantic (`app/core/config.py`):**
   - Incorporación de variables `JAIRODOMINGUEZ_SMTP_*` y `JAIRODOMINGUEZ_RECAPTCHA_SECRET_KEY`.
3. **Controlador API (`app/api/projects/jairo_dominguez.py`):**
   - Endpoint validado con Pydantic.
4. **Emails Transaccionales (`app/core/mailer.py`):**
   - `send_jairodominguez_confirmation_email`: Correo con diseño profesional al paciente.
   - `send_jairodominguez_notification_team`: Notificación inmediata al consultorio con enlace directo a WhatsApp.
   - Uso de `_prepare_project_email` para garantizar cumplimiento SPF/DMARC y fallback automático al SMTP de Hipha.
5. **Registro en la Aplicación (`app/main.py`):**
   - Montaje del router en `/api/projects/jairo-dominguez` y `/api/jairo-dominguez`.
   - Mapeo de hosts en `HOST_PROJECT_MAP` (`jairodominguez-urologo` y `jairo-dominguez`).
   - Sembrado del cliente en `AgencyClient`.

---

## 4. Despliegue en Vercel y Web Agéntica
1. **Reglas en `vercel.json`:**
   - Adición de `Dr. Jairo Dominguez` en `ignoreCommand`.
   - Reglas de reescritura para `(www\.)?jairodominguez-urologo\.com`.
   - Subruta en dominio de agencia `hipha.mx/jairo-dominguez/`.
2. **GEO y Grounding de IA:**
   - `/llms.txt`: Índice semántico de servicios, sedes en Morelia y experiencia médica para ChatGPT, Google Gemini y Perplexity.
   - `/robots.txt`: Apertura expresa a rastreadores de IA.
   - `/sitemap.xml`: Estructura canónica de 24 URLs.
3. **Subfooter Institucional:**
   - Firma de Hipha con enlace a `hipha.mx` y logotipo `LogoSubfooter.svg` en todas las páginas.
