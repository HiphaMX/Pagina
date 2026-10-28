# Project-Scoped Rules: HiphaMX-fastapi

- **Organización de Proyectos y Landing Pages**:
  - Todas las nuevas landing pages y sus archivos asociados (HTML, assets, etc.) creadas para clientes o proyectos externos deben ser colocadas en sus respectivos subdirectorios dentro de la carpeta `projects/` (por ejemplo, `projects/ValenciaServicios/index.html`).
  - No deben crearse archivos HTML sueltos de proyectos en el directorio raíz, para mantener limpia la estructura del repositorio.
  - La URL limpia se configurará mediante reglas de reescritura en `vercel.json` apuntando hacia el subdirectorio del proyecto en `projects/`.

- **Envío de Correos y SMTP en Proyectos**:
  - Al implementar el envío de correos electrónicos para nuevos clientes o proyectos, se debe evitar configurar a mano el remitente (`From`) con un dominio que no corresponda al servidor SMTP autenticado (esto causa fallas en políticas de SPF/DMARC y rebotes permanentes 554 5.7.1).
  - En su lugar, se debe utilizar la función centralizada `_prepare_project_email` en `app/core/mailer.py`, la cual maneja automáticamente el fallback seguro al SMTP general de la agencia (configurando el `From` con el usuario autenticado y el `Reply-To` con el correo específico del proyecto) cuando no hay SMTP propio configurado en Vercel.

- **Clasificación y Homologación de Proyectos (Prospectos) y Clientes (En Firme)**:
  - **Proyectos (Prospectos / Demos)**:
    - Son sitios en desarrollo, demos o propuestas para prospectos que aún no son clientes en firme.
    - Se publican bajo el dominio de la agencia como subcarpetas (`hipha.mx/IEER`, `hipha.mx/Letrerama`, etc.).
    - Las URLs limpias y reescrituras se manejan en `vercel.json` enlazando a `projects/[Nombre]/web/`.
    - **Regla de Correos**: No requieren ni deben tener variables SMTP dedicadas. Utilizan automáticamente el fallback del servidor SMTP general de la agencia (`HIPHA`).
    - *Prospectos Activos*: Centro Escolar El Paraiso (`el-paraiso`), IEER (`ieer`), Pumpapa (`pumpapa`), ni2 (`ni2`).
  - **Clientes (Proyectos en Firme)**:
    - Son proyectos aprobados que ya trabajan activamente con la agencia.
    - Se despliegan en su propio dominio o subdominio en Vercel mediante reglas específicas de `host` en `vercel.json` (ej. `urologia-avanzada.com.mx`).
    - **Regla de Correos**: Es obligatorio definir sus credenciales SMTP dedicadas en el esquema de Pydantic (`app/core/config.py`) y en el panel de Vercel. Si están pendientes de entrega de credenciales, heredan temporalmente el fallback al SMTP de la agencia (`HIPHA`).
    - *Clientes Activos*: uro-oncology, urologia-avanzada, Oncología Robótica, el chile chillón, white clean, Valencia servicios, Botica silvestre, Jessica Mendoza, Grupo Gari, Letrerama.
    - **Regla de Web Agéntica y GEO (llms.txt y robots.txt)**: Es un estándar obligatorio para todos los clientes activos implementar un archivo `/llms.txt` en Markdown en la raíz del sitio web de producción. Este archivo sirve como índice semántico para que los agentes de IA (ChatGPT, Gemini, Perplexity) consuman y citen los servicios del cliente de forma rápida. En `robots.txt`, para clientes comerciales que buscan visibilidad GEO, se debe permitir expresamente el acceso (`Allow: /`) a buscadores y agentes de grounding en tiempo real (`Google-Extended`, `GPTBot`, `OAI-SearchBot`, `PerplexityBot`, `ClaudeBot`), ya que bloquear `Google-Extended` inhabilita las búsquedas y respuestas de Google Gemini sobre el dominio.

- **Protocolo de Protección / Modo DEMO para Proyectos en Standby**:
  - **Objetivo**: Proteger la propiedad intelectual de la agencia y evitar que clientes, prospectos o terceros hagan mal uso comercial o despliegue no autorizado de propuestas de diseño y desarrollo web desarrolladas por Hipha mientras no estén formalizados o activos en el corto plazo.
  - **Comportamiento del Modo DEMO**:
    - **Visual**: El sitio web conserva su estética, contrastes, tipografía y fotografías originales intactas (sin veladuras ni capas invasivas de color) para permitir una evaluación visual fidedigna por parte de la directiva o tomadores de decisión.
    - **Popup Emergente**: Al ingresar al sitio, se despliega un diálogo modal que comunica el estado del proyecto:
      - Título: `Propuesta Web · Demo Gráfico`
      - Mensaje: *"Este sitio web es un prototipo funcional y propuesta conceptual desarrollada por Hipha para [Proyecto]. Actualmente este proyecto se encuentra en pausa operativa (standby) para evaluación."*
      - Ficha: `Desarrollo: Hipha`
      - Botón Principal: `contactarme con Hipha` enlazado directamente al WhatsApp de la agencia (`https://wa.me/523336762545?text=...`).
      - Botón Secundario: `Ver Demo Gráfico` (cierra el modal y permite recorrer la maqueta visualmente).
    - **Insignia Flotante (Floating Pill)**: Permanece visible en la esquina inferior (`[ ⚡ Demo Gráfico | WhatsApp ]`) permitiendo reabrir el aviso o abrir el chat de WhatsApp con un solo clic en cualquier momento.
    - **Neutralización de Hipervínculos**: Todos los enlaces (`<a>`) del sitio web se desactivan de forma estricta tanto en CSS (`pointer-events: none !important; cursor: default !important;`) como por intercepción de eventos en JavaScript. El único enlace interactivo permitido en toda la plataforma es el botón de WhatsApp a Hipha.
    - **Compatibilidad con Cursores y Top-Layer**: Si el proyecto utiliza cursores personalizados (`cursor: none`), el script restablece el cursor del sistema sobre el diálogo y oculta los elementos del custom cursor para que no queden atrapados detrás del modal en el Top Layer del navegador.
  - **Formas de Activación**:
    1. **Vía Script Modular Rápido (Recomendado)**:
       Agregar en el `<head>` o antes del cierre de `</body>` de cualquier HTML:
       `<script src="/js/hipha-demo-guard.js" data-project="Nombre del Proyecto" data-phone="523336762545"></script>`
       (Inyecta automáticamente estilos encapsulados, modal accesible, floating pill, neutralización de enlaces y bloqueo de formularios sin tocar el CSS/JS del proyecto).
    2. **Vía Integración Nativa (Código del Proyecto)**:
       Implementar la lógica directamente en el `app.js` y `style.css` del proyecto, siguiendo el patrón de referencia implementado en `projects/Centro Escolar El Paraiso/web/`.


