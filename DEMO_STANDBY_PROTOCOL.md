# 🛡️ Protocolo Oficial: Modo DEMO Gráfico para Proyectos en Standby

**Hipha Media & Software — Estándar Operativo de Protección Intelectual**

---

## 1. Propósito y Alcance

Este protocolo define el procedimiento formal para poner en **Modo DEMO Gráfico** cualquier proyecto web, landing page o propuesta digital desarrollada por Hipha que se encuentre en:
- Pausa operativa o evaluación por parte del prospecto/cliente.
- Demos o propuestas conceptuales activas bajo subcarpetas de la agencia (`hipha.mx/[proyecto]/`).
- Proyectos en standby donde existe riesgo de que el cliente o terceros hagan mal uso comercial, despliegue no autorizado o aprovechen la maqueta funcional sin formalización contractual.

---

## 2. Características del Modo DEMO Gráfico

| Componente | Especificación |
|---|---|
| **Aspecto Visual** | **100% Intacto**: Se mantiene la paleta de colores, diseño, tipografía y fotografía original (sin veladuras ni capas oscuras o multiplicadas invasivas) para que la directiva aprecie fielmente la propuesta de diseño. |
| **Popup Modal** | Diálogo emergente en top-layer que aparece al cargar el sitio. Informa de manera sobria y profesional que se trata de un prototipo conceptual de **Hipha**, indicando `Desarrollo: Hipha`. |
| **Botón de Contacto** | Botón verde destacado con el texto **`contactarme con Hipha`** e ícono oficial de WhatsApp, dirigido al número `3336762545` con mensaje prellenado del proyecto. |
| **Botón de Exploración** | Botón **`Ver Demo Gráfico`** para cerrar el modal y poder revisar la maqueta. |
| **Insignia Flotante** | Badge discreto en la esquina inferior derecha (`[ ⚡ Demo Gráfico | WhatsApp ]`) que permite reabrir el modal o contactar a Hipha en cualquier momento. |
| **Neutralización de Enlaces** | **Todos los hipervínculos (`<a>`) se desactivan** mediante CSS (`pointer-events: none !important; cursor: default !important;`) y captura en JS (`e.preventDefault()`). El único enlace activo en toda la web es el botón de WhatsApp a Hipha. |
| **Formularios** | Bloqueo de envíos de formularios para evitar captura no autorizada de leads en maquetas en pausa. |
| **Compatibilidad con Cursores** | Restauración automática del puntero nativo (`cursor: auto` / `pointer`) sobre el diálogo y suspensión de custom cursors DOM para evitar que el puntero se oculte detrás del `<dialog>` en el Top Layer del navegador. |

---

## 3. Métodos de Activación

### Método 1: Script Universal Autónomo (Recomendado — En 30 segundos)

Cualquier proyecto o landing page (incluso con dominios externos o stacks estáticos) puede activarse agregando una sola línea antes de `</body>`:

```html
<script src="/js/hipha-demo-guard.js" data-project="Nombre del Cliente" data-phone="523336762545"></script>
```

**Parámetros configurables (`data-*`):**
- `data-project`: Nombre del cliente o propuesta (por defecto toma el `<title>` de la página).
- `data-phone`: Número de WhatsApp con código de país (por defecto: `523336762545`).

*El script inyecta automáticamente los estilos CSS encapsulados, el modal nativo `<dialog>`, la insignia flotante y las reglas de neutralización de hipervínculos.*

---

### Método 2: Integración Nativa en Código del Proyecto

Para proyectos con arquitectura personalizada de CSS/JS (como `projects/Centro Escolar El Paraiso/web/`):

1. **En el CSS del proyecto (`style.css`):**
   ```css
   /* MODO DEMO GRÁFICO: Hipervínculos desactivados */
   a:not(.standby-whatsapp-btn):not(.standby-floating-pill_wa):not([href*="3336762545"]) {
     pointer-events: none !important;
     cursor: default !important;
   }
   ```

2. **En el JS del proyecto (`app.js`):**
   - Interceptar clics en `<a>` para cancelar la navegación excepto al WhatsApp de Hipha.
   - Desplegar el modal `<dialog class="standby-modal">` con el botón `contactarme con Hipha`.
   - Mostrar la insignia flotante `.standby-floating-pill` al cerrar el modal.

---

## 4. Desactivación (Reactivación de Proyecto)

Cuando el cliente apruebe la propuesta y se reactive el desarrollo:
1. Retirar el script `hipha-demo-guard.js` del HTML o revertir las reglas en `app.js` / `style.css`.
2. Asignar credenciales SMTP dedicadas y dominio propio según las reglas de `.agents/AGENTS.md`.
3. Ejecutar `npx vercel --prod --yes` para desplegar la versión comercial activa.
