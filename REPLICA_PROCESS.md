# 🚀 REPLICA PROCESS: The "Ultrapro" Landing Page Playbook

Este documento detalla el paso a paso metodológico que utilizamos para construir la landing page de HiphaMX. El objetivo es que cualquier agente del equipo (KAM, BrandMind, DesignFlow) pueda tomar este playbook y replicar la misma calidad, estructura y *feeling* de "agencia ultrapro" para cualquier marca futura.

## 0. Prerrequisitos y Configuración del Proyecto

Antes de escribir una sola línea de código o generar un diseño, se debe establecer el espacio de trabajo.

1.  **Carpeta del Proyecto:** KAM debe crear un directorio para el cliente en `projects/[NOMBRE_CLIENTE]/`.
2.  **Archivos Base:** Copiar el contenido de `projects/_template/` a la nueva carpeta del cliente.
3.  **El Intake:** El cliente (o KAM en su nombre) debe completar el `PROJECT_INTAKE_FORM.md` (el cuestionario de 20 preguntas). **Ningún trabajo creativo o técnico arranca sin esto.**

## 1. La Capa Estratégica (Agent: BrandMind)

El diseño visual es secundario; la estrategia manda. BrandMind procesa el intake form para generar los cimientos de la marca.

### Entregables de BrandMind:
1.  **Brand Brief (`brand_brief.md`):** Define el arquetipo, el tono de voz, la promesa central, y las referencias visuales (paleta de colores sugerida, tipografías).
2.  **Wireframe Brief (`wireframe_brief.md`):** Estructura lógica de la landing page.
    *   **Hero Section:** El *hook* (H1), el subtítulo explicativo y el CTA principal.
    *   **Secciones de Valor:** Problema -> Solución (Features como beneficios).
    *   **Social Proof:** Testimonios, métricas de éxito ("+100 marcas impulsadas").
    *   **Footer:** Enlaces rápidos, contacto, CTA final.
3.  **Copywriting Master:** Textos persuasivos para cada bloque del wireframe, usando fórmulas de alta conversión (ver `AGENT_BRANDMIND.md`).

## 2. La Capa de Diseño y Código (Agent: DesignFlow)

DesignFlow toma los briefs de BrandMind y los convierte en realidad digital. La regla de oro es mantener un *feeling* premium y moderno.

### 2.1 El Stack Visual "Ultrapro"
Para replicar el look de HiphaMX, se deben utilizar las siguientes técnicas:

*   **Tailwind CSS:** Para estilización rápida y utilitaria.
*   **Modo Oscuro (Dark Theme) por defecto:** Un fondo oscuro (`#050810` o similar) inmediatamente eleva la percepción de calidad en nichos tech/marketing.
*   **Glassmorphism:** Uso intensivo de fondos semitransparentes con desenfoque (`backdrop-blur`).
    *   *Ejemplo CSS:* `background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.1);`
*   **Gradientes Vibrantes y Neón:** Uso estratégico de colores saturados (cyan, magenta, violeta) aplicados en textos (`bg-clip-text text-transparent`), botones o "blobs" difuminados de fondo para dar profundidad.
*   **Micro-animaciones:**
    *   Transiciones suaves en `hover` (elevación de tarjetas, resplandor en botones).
    *   Aparición en cascada al hacer scroll (e.g., `fade-in-up`).
    *   Animaciones infinitas sutiles (elementos flotando, carruseles continuos de logos/testimonios).
*   **Tipografía Moderna:** Fuentes sin remates (sans-serif) limpias y legibles como *Inter*, *Outfit* o *Plus Jakarta Sans*. Uso de grosores extremos (Light vs ExtraBold) para jerarquía.
*   **Cursor Personalizado:** Reemplazar el cursor del sistema por un punto y un anillo que reaccionen a elementos interactivos da una sensación inmersiva.

### 2.2 Estructura del Código
*   **Modularidad:** Mantener el código en `index.html` estructurado por `<section>` con IDs claros (e.g., `#hero`, `#soluciones`, `#social-proof`).
*   **Variables CSS:** Extraer los colores principales a variables en el `:root` o en la configuración de Tailwind para facilitar futuros *re-skins*.
*   **Assets:** Los iconos deben ser modernos (como *Phosphor Icons*). Las imágenes o recursos generados deben almacenarse en la carpeta del proyecto.

## 3. Integración y Orquestación (Agent: KAM)

A lo largo del proceso, el KAM actúa como director de orquesta.

1.  **Validación Continua:** KAM verifica que el código generado por DesignFlow respete estrictamente los lineamientos del `brand_brief.md`.
2.  **Gestión de Assets:** Si la landing requiere imágenes de apoyo hiperrealistas, KAM solicita los prompts a VIRALGEN/IMAGENOLOGO basándose en la paleta del proyecto.
3.  **Documentación:** KAM mantiene actualizado el `BRIEF_MEMORIA.md` para que cualquier agente pueda retomar el contexto en el futuro.

## 4. Despliegue (Producción)

Una vez que la landing page está pulida y funcional localmente:

1.  **Git Flow:** Asegurar que todo el código y la documentación en la carpeta `projects/[CLIENTE]/` estén comiteados en el repositorio.
2.  **Hosting (Vercel):** La estructura estática (HTML/Tailwind/JS) es ideal para Vercel.
    *   Asegurar que exista un archivo `vercel.json` configurado correctamente para enrutamiento si es necesario.
    *   El comando `vercel` desde la CLI despliega inmediatamente la versión de producción.

## Checklist Rápido de Réplica:
- [ ] Intake Form completado (20 preguntas).
- [ ] Brand Brief generado (Arquetipo, Tono, Paleta).
- [ ] Wireframe + Copy generado (H1, Secciones, CTAs).
- [ ] Diseño en Dark Mode con Glassmorphism + Tailwind.
- [ ] Micro-animaciones implementadas (hover, scroll).
- [ ] Repositorio actualizado.
- [ ] Desplegado a Vercel.
