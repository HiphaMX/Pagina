# 🎯 BRIEF DE INSPIRACIÓN: Swiss Design & Grid System (baselarea.swiss)

**De**: KAM (Key Account Manager)  
**Para**: DesignFlow (Especialista UX/UI & Webflow)  
**Proyecto**: ni2 — Inmobiliaria de Trámite Ágil  

---

## 🧠 CONTEXTO Y FILOSOFÍA
El usuario nos ha solicitado rediseñar la cabecera (Navbar) y la sección principal (Hero1) de **ni2**, tomando como referencia directa el estilo de **baselarea.swiss**. 

Este portal es un referente del **Swiss Design (Estilo Tipográfico Internacional)**, cuyos pilares son:
1.  **Clarity & Readability**: Tipografías sans-serif robustas, usadas como elemento visual primario.
2.  **Strict Grid-Based Layouts**: Uso obsesivo de grillas y bordes delgados de `1px` para segmentar y dar ritmo visual, eliminando cualquier adorno innecesario.
3.  **No BS Approach**: Diseño modular centrado en el usuario, facilitando que diferentes segmentos (compradores, vendedores, etc.) encuentren su camino al instante.
4.  **Asimetría Controlada**: Contraste dinámico entre grandes masas de texto tipográfico y cajas modulares de conversión compactas.

---

## 🎨 TOKENS Y CAMBIOS PROPUESTOS PARA NI2

Inyectaremos esta estética suiza y limpia utilizando nuestra paleta aprobada de **Gris Oxford y Negro**, configurando una interfaz sumamente premium:

### 1. Cabecera (Navbar) Suiza
*   **Logo Compacto y Contraste**: El logo `ni2.` se estructurará con una tipografía Outfit extra-bold con `letter-spacing: -0.04em` y el punto en Gris Oxford, emulando la sofisticada marca suiza.
*   **Tipografía de Navegación**: Los enlaces serán en mayúsculas, negritas (`700`), tamaño compacto (`13px`) y con espaciado amplio:
    ```css
    font-family: var(--font-display);
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: 0.06em;
    font-size: 0.8125rem;
    ```
*   **Efecto Separador**: La cabecera estará delimitada por un borde inferior de `1px` color pizarra, sin sombras pesadas, manteniendo un look limpio y plano.

### 2. Hero1 en Grilla Modular Asimétrica (Basel Area Hero)
*   **Tipografía Display Gigante**: El título principal (`.hero-title`) se elevará a proporciones suizas:
    ```css
    font-size: clamp(2.5rem, 5vw, 4.25rem);
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.04em;
    ```
*   **División en Grilla de Bordes Activos (Swiss Grid)**:
    - En escritorio, la pantalla se dividirá en dos secciones mediante una grilla estricta de `1.1fr` y `0.9fr`.
    - La columna izquierda (texto y beneficios) y la derecha (caja de conversión) estarán separadas visualmente por una línea divisoria vertical sutil, estructurando la jerarquía.
*   **Caja de Conversión Suiza (Swiss Modular Box)**:
    - La caja de pestañas se rediseña como un bloque compacto de bordes limpios de `1px` integrados con la grilla.
    - Las pestañas (`.tab-btn`) serán planas, mayúsculas, y separadas por bordes delgados, reaccionando con un fondo Gris Oxford sólido cuando estén activas.
*   **Trust Bullets como "Grid Row Footer"**:
    - Las viñetas de confianza (`.trust-bullets`) se transformarán en un pie de grilla horizontal. Se ubicarán bajo la sección, ocupando el 100% del ancho del Hero, delimitadas por líneas de `1px` arriba y abajo.
    - Cada beneficio se ubicará en una columna separada por un borde vertical intermedio, imitando la estructura modular de baselarea.swiss.

---

## 🛠️ PLAN DE EJECUCIÓN (Llamado a la Acción para DesignFlow)
DesignFlow, procede de inmediato a actualizar el código:
1.  **styles.css**: Configurar las clases suizas para el Navbar, la tipografía display del hero, la grilla modular asimétrica de la cabecera y el pie de grilla de las viñetas.
2.  **index.html & landing-venta-rapida.html**: Adaptar la estructura HTML del Navbar y Hero para acomodar las nuevas clases de grilla y división visual, asegurando que se adapte perfectamente a pantallas móviles de forma fluida.
3.  **main.js**: Sincronizar las micro-animaciones del simulador analítico GA4 para que se disparen con cada nueva pestaña modular suiza.
