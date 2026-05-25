# Proceso de Réplica: Construcción de Landing Pages "Ultrapro"

Este documento establece el flujo de trabajo técnico y de diseño (el "CÓDIGO de réplica") que hemos utilizado para construir la landing page de HiphaMX. 

**Aclaración Crítica:** El objetivo de este manual NO es crear "clones" visuales o plantillas genéricas. Lo que replicamos es el **Motor Técnico** (velocidad, interactividad, código limpio, animaciones fluidas) y el **Estándar de Calidad Ultrapro**. Cada nueva marca tendrá un diseño 100% independiente, con una identidad visual única, paletas de colores exclusivas, tipografías propias y una estrategia a la medida extraída de su Formulario de Abordaje.

## 1. Arquitectura de Archivos y Dependencias
Para garantizar un rendimiento y consistencia visual de primer nivel, todo nuevo proyecto debe inicializarse con esta estructura:

- `index.html` (Home y layout principal)
- `aviso-de-privacidad.html` y `terminos-y-condiciones.html` (Páginas legales estándar)
- `css/style.css` (Diseño custom, utilidades y animaciones base)
- `js/app.js` (Lógica global de UI, Autenticación y Efectos)
- `js/tailwind-config.js` (Paleta de colores y token de diseño dinámico)

### Dependencias Principales (Vía CDN para velocidad)
- **Tailwind CSS:** Motor de estilos base (`<script src="https://cdn.tailwindcss.com?plugins=typography"></script>`). El plugin de tipografía es **obligatorio** para las páginas legales.
- **Phosphor Icons:** Sistema de iconografía en tres pesos (`regular`, `bold`, `fill`).
- **Google Fonts:** Fuente `Inter` (pesos 300 a 700) para todo el cuerpo del texto.

## 2. Elementos Visuales Core (El "Feeling Ultrapro")

### 2.1 Dark Mode Obligatorio y Glassmorphism
El diseño está anclado en un ecosistema oscuro (`class="dark"` en la etiqueta HTML) sin interruptor de tema. 
- El efecto "Glassmorphism" se logra con la clase `.glass-panel`:
  ```css
  .glass-panel {
      background: rgba(15, 23, 42, 0.4);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.05);
  }
  ```
- **Blobs Magnéticos:** Se utilizan tres divs (`.blob-1`, `.blob-2`, `.blob-3`) con fondos de gradiente (ej. `bg-fuchsia-600`), bordes redondeados, y un altísimo desenfoque (`blur-[100px]`) posicionados de manera absoluta en el fondo, con animaciones de transformación lenta.

### 2.2 Puntero Magnético Personalizado (Custom Cursor)
Para la experiencia inmersiva, el cursor por defecto del SO se oculta (excepto en dispositivos móviles).
- **DOM Requerido:** N/A (Se inyectan dinámicamente vía Javascript).
- **CSS Requerido:** Estilos definidos con `pointer-events: none` y `z-index: 99999`.
- **Lógica (en `app.js`):** La función `initCursor()` debe estar envuelta en un bloque de seguridad robusto que no bloquee el hilo principal si faltan elementos en el DOM, utilizando `MutationObserver` para detectar enlaces generados dinámicamente.

### 2.3 Preloader de Una Sola Vez
Para no fatigar al usuario al navegar entre secciones:
- Se implementa un preloader de pantalla completa que se desvanece tras 2 segundos.
- **Regla de Oro:** Debe utilizar `sessionStorage` (`hiphamx-preloader-seen`). Si la bandera existe, el nodo del preloader se elimina del DOM inmediatamente y no se vuelve a mostrar durante la sesión.

### 2.4 Componente: Timeline Explicativo
El "Timeline" es el corazón de la explicación de servicios.
- Utiliza un array de objetos (`timelineData`) en Javascript.
- Renderiza una barra de navegación izquierda y un contenedor dinámico derecho.
- Las transiciones usan clases de Tailwind (`transition-all duration-300 transform`) acopladas con un reseteo de `opacity` y `filter: blur()` en Javascript.

## 3. SEO y Estructura Legible

- **Páginas Legales:** Deben envolver su contenido en el contenedor `.prose` de Tailwind Typography. Modificadores obligatorios: `prose-invert prose-p:mb-6 prose-p:leading-relaxed text-slate-300`. Esto garantiza la lectura perfecta.
- **Meta Tags:** Cada página requiere `og:title`, `og:description`, `og:image`, `twitter:card` y marcado estructurado JSON-LD.

## 4. Flujo de Despliegue (DevOps)
1. **GitHub:** Todos los cambios se consolidan (`git commit`) con nomenclatura estandarizada.
2. **Vercel:** La rama `main` está conectada para despliegue automático.
3. **Control de Caché:** Cualquier actualización a `js/app.js` o `css/style.css` **debe** incluir un parámetro de purga de caché (`?v=X`) en el HTML para evitar discrepancias en navegadores de usuarios recurrentes.
4. **Vercel Ignore:** El archivo `.vercelignore` debe estar configurado para excluir activos pesados (`projects/DAM/`) pero **nunca** el directorio raíz genérico, asegurando que los logotipos (`projects/NombreMarca/...`) se publiquen.

---

*Nota de Colaboración:* La carpeta `projects/` es el ecosistema central. Subir aquí la información, manuales de marca y assets es **correcto y obligatorio** para que cualquier IA o miembro del equipo tenga el contexto unificado.
