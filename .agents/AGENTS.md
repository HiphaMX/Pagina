# Project-Scoped Rules: HiphaMX-fastapi

- **Organización de Proyectos y Landing Pages**:
  - Todas las nuevas landing pages y sus archivos asociados (HTML, assets, etc.) creadas para clientes o proyectos externos deben ser colocadas en sus respectivos subdirectorios dentro de la carpeta `projects/` (por ejemplo, `projects/ValenciaServicios/index.html`).
  - No deben crearse archivos HTML sueltos de proyectos en el directorio raíz, para mantener limpia la estructura del repositorio.
  - La URL limpia se configurará mediante reglas de reescritura en `vercel.json` apuntando hacia el subdirectorio del proyecto en `projects/`.

- **Envío de Correos y SMTP en Proyectos**:
  - Al implementar el envío de correos electrónicos para nuevos clientes o proyectos, se debe evitar configurar a mano el remitente (`From`) con un dominio que no corresponda al servidor SMTP autenticado (esto causa fallas en políticas de SPF/DMARC y rebotes permanentes 554 5.7.1).
  - En su lugar, se debe utilizar la función centralizada `_prepare_project_email` en `app/core/mailer.py`, la cual maneja automáticamente el fallback seguro al SMTP general de la agencia (configurando el `From` con el usuario autenticado y el `Reply-To` con el correo específico del proyecto) cuando no hay SMTP propio configurado en Vercel.
