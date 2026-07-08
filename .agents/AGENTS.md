# Project-Scoped Rules: HiphaMX-fastapi

- **Organización de Proyectos y Landing Pages**:
  - Todas las nuevas landing pages y sus archivos asociados (HTML, assets, etc.) creadas para clientes o proyectos externos deben ser colocadas en sus respectivos subdirectorios dentro de la carpeta `projects/` (por ejemplo, `projects/ValenciaServicios/index.html`).
  - No deben crearse archivos HTML sueltos de proyectos en el directorio raíz, para mantener limpia la estructura del repositorio.
  - La URL limpia se configurará mediante reglas de reescritura en `vercel.json` apuntando hacia el subdirectorio del proyecto en `projects/`.
