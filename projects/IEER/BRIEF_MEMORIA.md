# 📋 BRIEF MEMORIA — IEER (Ingeniería Especializada en Energías Renovables)

> *Este archivo es la memoria viva del proyecto. Se actualiza en cada fase. Todo el equipo de agentes (KAM, BrandMind, DesignFlow, SiteSentinel, GEOPilot) lo lee antes de ejecutar.*

**Proyecto ID:** `IEER-202611`  
**Fecha de inicio:** Noviembre 2026  
**Última actualización:** 2026-11-09  
**Responsable KAM:** KAM v2.0  
**Estado:** `[x] Discovery` → `[x] Estrategia (BrandMind)` → `[x] Producción Web (DesignFlow)` → `[x] Modo Demo Desactivado` → `[x] Alta como Cliente en Firme` → `[ ] Validación DNS Dominio Propio`  

---

## 🏢 DATOS DEL CLIENTE

| Campo | Detalle |
|---|---|
| **Nombre de la marca** | IEER (Ingeniería Especializada en Energías Renovables) |
| **Industria / Nicho** | Alta Ingeniería Solar · Micro-Redes · Almacenamiento Industrial en Litio LFP · Sistemas Off-Grid de Lujo |
| **Dominio oficial** | `ieer.com.mx` (y `www.ieer.com.mx`) |
| **URL provisional / preview** | `https://hipha.mx/ieer/` |
| **Canales de contacto** | WhatsApp: [+52 33 3302 5665](https://wa.me/523333025665) · Correo: `lcid@ieer.com.mx` |
| **Titular / Contacto** | Ing. Luis Cid |
| **Cobertura Operativa** | Todo el territorio de la República Mexicana |

---

## 🎯 OBJETIVO DEL PROYECTO

> Consolidar a **IEER** como el referente nacional de ingeniería en micro-redes de alta capacidad y sistemas de almacenamiento inteligente en litio, resolviendo la vulnerabilidad de industrias, el bombeo continuo en el campo agropecuario y la total independencia en residencias de descanso y arquitectura de lujo sin depender de las fluctuaciones o ausencias de CFE.

---

## 🎨 DIRECCIÓN DE ARTE & ESTÉTICA
- **Concepto:** *Organic Nature & Luxury Tech* (Fusión de texturas naturales minerales y precisión de ingeniería).
- **Paleta de Colores:**
  - `Fondo Principal:` `#080b0c` (Deep Obsidian Slate / Negro mineral ultra-oscuro)
  - `Cards & Paneles:` `rgba(12, 16, 18, 0.65)`
  - `Acento de Lujo (Energía):` `#a98567` (Warm Bronze / Bronce tierra)
  - `Acento de Luz (Texto):` `#e3ddd5` (Alabaster Cream)
  - `Bordes sutiles:` `rgba(169, 133, 103, 0.12)`
- **Tipografías:**
  - `Display / Títulos:` *Outfit* (pesos ultra-ligeros para elegancia minimalista)
  - `Tech / Badges:` *Space Grotesk* y *Syncopate*
  - `Acento Signature:` *Google Sans Flex* (Semibold 600)

---

## 🏗️ ARQUITECTURA TÉCNICA DEL SITIO
1. **Landing Principal (`index.html`):**
   - Hero interactivo con simulación de inversor y curva solar en tiempo real (Canvas).
   - Módulo de sectores (Industrial, Agropecuario, Residencial Premium, Cargas Críticas).
   - Radar concéntrico de cobertura nacional (estilo Zerocircle).
   - Formulario de consulta técnica conectado a `/api/contact/ieer`.
   - Botón directo de WhatsApp flotante hacia `+52 33 3302 5665`.
2. **Landing Pages Dedicadas por Segmento:**
   - `comercial.html` (`/comercial`): Especializada en almacenamiento BESS comercial e industrial, Peak Shaving, continuidad de línea (<10 ms) y retorno de inversión.
   - `agricola.html` (`/agricola`): Especializada en bombeo solar fotovoltaico de 10 a 150 HP, sustitución de diésel y pivotes/goteo tecnificado.
   - `residencial.html` (`/residencial`): Especializada en residencias de descanso, villas de lujo, cero decibelios e integración arquitectónica coplanar.
3. **IEER Journal (Artículos Técnicos Especializados):**
   - `blog.html`: Repositorio Editorial Completo (`/blog`) con buscador y filtrado interactivo por categorías (Almacenamiento, Micro-Redes, Calidad de Energía, Normativa, Agropecuario).
   - `articulo-autonomia.html`: La Nueva Era de la Autonomía Energética Industrial.
   - `articulo-calidad-energia.html`: Calidad de Energía: El Silencioso Pilar de la Eficiencia.
   - `articulo-offgrid.html`: Integración de Sistemas Off-Grid en Arquitectura Luxury.
   - `articulo-codigo-red.html`: Código de Red 2.0: Guía de Cumplimiento Técnico en Media y Alta Tensión.
   - `articulo-bombeo-solar.html`: Bombeo Solar de Alto Rendimiento en Pozo Profundo y Superficie: Cero Diésel.
   - `articulo-baterias-litio.html`: Baterías Litio LFP vs. Plomo-Ácido: Ciclo de Vida, LCOS y Retorno de Inversión.
4. **Web Agéntica & GEO:**
   - `llms.txt`: Resumen semántico para modelos de lenguaje (Gemini, ChatGPT, Perplexity).
   - `robots.txt`: Permisos explícitos para buscadores y motores de grounding IA.
   - `sitemap.xml`: Índice canónico XML de páginas y artículos técnicos.

---

## 🔐 HISTORIAL DE CAMBIOS Y PROTOCOLOS
- **2026-11-09:** Aprobación de la transición de Prospecto a **Cliente en Firme**.
- **2026-11-09:** Desactivación y retiro definitivo del script modular `hipha-demo-guard.js`.
- **2026-11-09:** Configuración de enrutamiento por host `^(www\.)?ieer\.com\.mx$` en `vercel.json`.
- **2026-11-09:** Implementación de endpoint de backend `/api/contact/ieer` y funciones SMTP de fallback seguro en `mailer.py`.
- **2026-11-09:** Incorporación a `AgencyClient` en base de datos y al monitoreo continuo de `WebGuardian`.
- **2026-11-10:** Integración de la sección de Comprobación de Experiencia y Certeza Operativa debajo del Hero1 (estilo Design Flow, bento grid de 3 pilares: tiempo de respuesta ≤ 24h, ciclo integral de 4 etapas, y alcances de 5 kW a +100 kW en laboratorios, fábricas, clínicas, spa y hotelería). Despliegue en producción verificado.
- **2026-11-10:** Corrección de geometría adaptativa de la cápsula de navegación.
- **2026-11-10:** Reestructuración editorial de la sección de Blog en `index.html`: retiro del texto 'CONSTRUYENDO EL FUTURO ENERGÉTICO', categorización de las 3 fichas insignias como 'Publicaciones Recientes', incorporación de CTAs 'Ver todas las publicaciones' (cabecera) y 'Ver más publicaciones' (pie). Creación de la página completa `blog.html` (`/blog`) con filtrado dinámico por categorías y enrutamiento configurado en `vercel.json`. Despliegue verificado en producción.
- **2026-11-10 / 2026-11-11:** Limpieza de UI en `index.html`: retiro del botón 'Ver más publicaciones' inferior y de la etiqueta 'IEER Journal · Publicaciones Recientes'. Incorporación de botones CTA 'Ver más' en cada slide del Mega Parallax Slider de Segmentos apuntando a sus respectivas landings (`/comercial`, `/agricola`, `/residencial`). Actualización de opciones del formulario de contacto (Residencial, Complejo Industrial, Hotelería / Spa / Wellness, Hospitales / UCIs / Laboratorios).
- **2026-11-10 / 2026-11-11:** Creación de 3 landings de segmento de mercado con diseño Luxury Tech y UX optimizada en móvil: `comercial.html`, `agricola.html`, `residencial.html`.
- **2026-11-10 / 2026-11-11:** Creación de 3 artículos técnicos completos con análisis matemático, fórmulas de ingeniería, tablas comparativas: `articulo-codigo-red.html`, `articulo-bombeo-solar.html`, `articulo-baterias-litio.html`. Actualización de `blog.html` para enlazar artículos directamente en lugar de enlaces WhatsApp externos. Actualización de `vercel.json` y `llms.txt`, y creación de `sitemap.xml`.
- **2026-11-11 (Ajustes de Diseño & UX Móvil · DesignFlow & KAM):**
  - **Centrado Móvil Total (<= 768px):** Justificación y alineación centrada de títulos, subtítulos, párrafos descriptivos, formularios interactivos, especificaciones técnicas, tarjetas de solución y elementos de interfaz en `index.html` y todas las páginas del ecosistema (`agricola.html`, `comercial.html`, `residencial.html`, `blog.html`, `preguntas-frecuentes.html`, `aviso-de-privacidad.html` y los 6 artículos técnicos del journal).
  - **Homologación de Navbar:** Estandarización de la barra de navegación en cápsula flotante a lo largo de todo el sitio sin variaciones de estilo entre la home y las secciones. Incorporación de animación de hamburguesa a cruz ("X") y fondo desenfocado con `backdrop-filter: blur(20px)` en menús desplegables móviles.
  - **Tipografía de Marca IEER en Navbar:** Aplicación de la tipografía geométrica seleccionada `Syncopate` (`var(--font-future)`, 700, `0.18em` tracking, uppercase) en `.nav-brand-link` sobre la misma posición física en todas las páginas.
  - **Rediseño del Footer & Corrección de Descuadre:** Retiro del isotipo SVG vertical de 180px (`IEER2.svg`) y sustitución por la tipografía de marca `IEER` (`Syncopate`, 1.85rem, letter-spacing `0.22em`, color alabastro `#e3ddd5`), alineando perfectamente la columna de marca con las columnas de Soluciones, Navegación y Contacto en desktop, y centrado visual completo en dispositivos móviles.
  - **Actualización de Autoría del Blog:** Homologación de todas las firmas de los artículos técnicos del journal a `Frank D. // Ingeniería Especializada en Energías Renovables`, actualizando avatares visuales (`FD`), cajas de autor y bloques de metadatos estructurados Schema.org JSON-LD (`TechArticle`).
  - **Ficha Especializada Hospitales & Laboratorios (`comercial.html`):** Sustitución de la ficha de plazas comerciales por *Hospitales & Laboratorios*: icono `ph-hospital`, respaldo eléctrico de grado médico para quirófanos, áreas UCI, equipos de diagnóstico y bancos de reactivos, con especificaciones de transferencia sub-ciclo (<10 ms), cadena de frío 24/7 y cumplimiento normativo NOM-001-SEDE Art. 517.
