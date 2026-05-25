# 🛠️ HIPHAMX WORKSPACE WORKFLOW & HYGIENE POLICY
## Saneamiento y Buenas Prácticas para Agentes y Desarrolladores

Para garantizar que el caos de carpetas sobredimensionadas, archivos temporales inútiles y fallos de despliegue en Vercel **nunca regrese**, establecemos este protocolo obligatorio de estructura e higiene del espacio de trabajo. Todos los agentes (KAM, BrandMind, DesignFlow, etc.) deben respetar rigurosamente estas reglas.

---

## 1. La Estructura del Proyecto (La Separación de Responsabilidades)

El espacio de trabajo se divide estrictamente en tres zonas:

```
/HiphaMX-fastapi                  <-- Repositorio Principal (Git & Vercel)
  ├── app/                        <-- API Backend de producción (FastAPI)
  ├── api/                        <-- Punto de entrada Serverless de Vercel
  │
  ├── projects/                   <-- CARPETA DE PRODUCCIÓN ESTÁTICA
  │     ├── [NombreCliente]/      <-- Solo contiene HTML, CSS, JS optimizados
  │     └── (Sin node_modules, sin .next, sin venv, sin archivos de diseño)
  │
  └── Hipha Projects/             <-- ⚠️ ÁREA DE TRABAJO LOCAL (100% IGNORADA)
        ├── [NombreCliente]/      <-- Entorno de desarrollo del cliente
        └── (Aquí viven los frameworks, node_modules, .next, venv y briefs)
```

### 📌 Regla de Oro:
*   **`projects/` (En Git/Producción):** Solo contiene los archivos estáticos listos para que Vercel los sirva al público. **Prohibido** crear entornos virtuales, instalar paquetes o tener carpetas de caché aquí.
*   **`Hipha Projects/` (Solo Local):** Es el arenero/sandbox donde los agentes trabajan con frameworks (React, Next.js, Webflow, etc.). Esta carpeta está en `.gitignore` y `.vercelignore`, por lo que **nunca se subirá a la nube ni pesará en el repositorio**.

---

## 2. Reglas Estrictas de Higiene del Espacio de Trabajo

Para evitar bloqueos de almacenamiento y errores de límite de tamaño (Vercel no permite despliegues mayores a 100 MB), sigue estas directrices:

1.  **Dependencias Locales:**
    *   Cualquier entorno virtual de Python debe llamarse `venv/` o `venv_pdf/` en la raíz (ya pre-configurados para ser ignorados).
    *   Nunca instales dependencias de Node (`node_modules`) o generes cachés de construcción (`.next`, `dist`, `build`) en la raíz del proyecto o dentro de `projects/`. Todo framework debe correr y compilarse dentro de `Hipha Projects/`.
2.  **Archivos de Diseño y Raw Media:**
    *   Los archivos pesados como PDFs de branding, imágenes sin comprimir o archivos `.psd` / `.ai` deben guardarse dentro de `Hipha Projects/[Cliente]/` o en almacenamiento externo (Google Drive/Figma) y enlazarse. Nunca deben comitearse en el historial de Git principal.
3.  **Logs y Archivos de Depuración:**
    *   Los archivos `deploy.log`, `stderr.txt` y `stdout.txt` están ignorados por defecto. Si necesitas depurar, lee los logs localmente pero nunca fuerces su subida al repositorio.

---

## 3. Script Automatizado de Limpieza e Higiene (`scripts/hygiene.py`)

Para darte tranquilidad absoluta, hemos implementado un script interactivo en la raíz del proyecto para que tú o cualquier agente pueda evaluar el estado de la carpeta y limpiarla con un solo comando.

### Cómo ejecutarlo:
```bash
python3 scripts/hygiene.py
```

### Lo que hace el script:
1.  **Analiza** si hay carpetas prohibidas como `node_modules` o `.next` fuera de las zonas seguras (e.g. en `projects/` o en la raíz).
2.  **Reporta** el tamaño total del directorio y de la carpeta `.git`.
3.  **Elimina** automáticamente archivos basura como `.DS_Store` o archivos de depuración huérfanos.
4.  **Advierte** si hay archivos de más de 5 MB que se hayan escapado de las reglas de Git.

---

## 4. Flujo de Trabajo para Nuevos Clientes

1.  **Fase 1: Estrategia (BrandMind)**
    *   Crea la carpeta en `Hipha Projects/[Cliente]/` (Sandbox).
    *   Genera allí los cuestionarios de Intake y los briefs estratégicos (`brand_brief.md`, `voice_brief.md`).
2.  **Fase 2: Código / Diseño (DesignFlow)**
    *   Si se usa un framework (Next.js/React), desarróllalo localmente en `Hipha Projects/[Cliente]/`.
    *   Si es una landing page estática lista, se coloca directamente en `projects/[Cliente]/web/`.
3.  **Fase 3: Optimización y Despliegue (KAM)**
    *   Ejecuta `python3 scripts/hygiene.py` para asegurar que no se hayan generado dependencias pesadas por error.
    *   Realiza el despliegue con `vercel --prod` o mediante la automatización de GitHub.
