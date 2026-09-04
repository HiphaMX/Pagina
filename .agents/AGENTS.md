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
    - *Clientes Activos*: uro-oncology, urologia-avanzada, el chile chillón, white clean, Valencia servicios, Botica silvestre, HealthyIce, Jessica Mendoza, Grupo Gari, Letrerama.
    - **Regla de Web Agéntica y GEO (llms.txt)**: Es un estándar obligatorio para todos los clientes activos implementar un archivo `/llms.txt` en Markdown en la raíz del sitio web de producción. Este archivo debe servir como un índice semántico para que los agentes de IA (ChatGPT, Gemini, Perplexity) consuman y citen el contenido de valor (blog) y los servicios del cliente de forma rápida. Opcionalmente, se deben definir reglas híbridas en `robots.txt` para bloquear el entrenamiento de modelos (`GPTBot`, `ClaudeBot`, `Google-Extended`) pero permitir buscadores en tiempo real (`OAI-SearchBot`, `PerplexityBot`).

