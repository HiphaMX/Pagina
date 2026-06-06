# 🎯 BRIEF DE INSPIRACIÓN: Tenity-Style Dinamismo & Animaciones

**De**: KAM (Key Account Manager)  
**Para**: DesignFlow (Especialista UX/UI & Webflow)  
**Proyecto**: ni2 — Inmobiliaria de Trámite Ágil  

---

## 🧠 CONTEXTO Y PROPÓSITO
El usuario ha solicitado inyectar **mayor dinamismo y animaciones fluidas** a la web de **ni2**, tomando como referencia directa la experiencia visual e interacciones del portal global **Tenity** (tenity.com). 

El estilo de Tenity destaca por:
1.  **Estructura de Grillas Geométricas Activas**: Las líneas y bordes no son solo divisorios; reaccionan a las interacciones del cursor.
2.  **Transiciones Cinemáticas y Suaves**: Todo cambio de estado utiliza curvas de aceleración personalizadas (`cubic-bezier`).
3.  **Animaciones de Entrada Escalonadas (Staggered)**: Los elementos de la interfaz se revelan en secuencia al cargar la página o hacer scroll.
4.  **Micro-interacciones de Dirección**: Uso de flechas deslizantes y elementos cinéticos que sugieren acción y flujo constante.

---

## 🎨 PALETA DE ANIMACIONES Y INTERACCIONES RECOMENDADA

Para dotar a **ni2** de esta sofisticación interactiva sin comprometer la velocidad de carga (LCP), implementaremos las siguientes directrices técnicas directamente en el código nativo:

### 1. Sistema de Transiciones Fluidas (CSS Tokens)
Definimos curvas personalizadas que emulan la física orgánica de Tenity:
```css
--transition-tenity: all 0.5s cubic-bezier(0.16, 1, 0.3, 1); /* Curva de desaceleración suave */
--transition-fast: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
```

### 2. Animaciones de Entrada Escalonadas (Staggered Reveal)
Al cargar el sitio, el Hero y sus componentes no aparecerán de golpe. Utilizaremos un retardo escalonado (`animation-delay`) combinado con una clase de activación en el body:
*   **H1**: Aparece primero con un ligero desplazamiento vertical (de abajo hacia arriba).
*   **Subtítulo**: Aparece `100ms` después.
*   **Caja de Conversión (Tabs/Buscador)**: Aparece `250ms` después.
*   **Trust Bullets**: Aparecen `400ms` después.

### 3. Grilla Reactiva con Efecto Hover Activo
En la sección de características del método ni2:
*   Las tarjetas (`.feature-card`) tendrán bordes sutiles que, al hacer hover, no solo cambian de color, sino que activan una línea sutil de brillo en la parte inferior.
*   El icono SVG sufrirá una micro-animación de escala (`transform: scale(1.1) rotate(2deg)`).

### 4. Transición de Pestañas con Efecto "Morphing"
Al alternar entre *"Quiero Comprar/Rentar"* y *"Quiero Vender"*, el contenedor de conversión principal suavizará su altura y opacidad de forma progresiva, evitando saltos bruscos.

### 5. Carrusel de Propiedades con Hover Cinético
*   Al pasar el cursor sobre una tarjeta de propiedad (`.property-card`), la imagen de fondo aumentará de escala suavemente (`transform: scale(1.06)`).
*   Un botón de acción oculto *"Ver Detalles →"* se deslizará desde la parte inferior de la tarjeta con opacidad de `0` a `1`.
*   El precio tendrá una transición de color vibrante al rojo quemado con un micro-resplandor de texto.

---

## 🛠️ PLAN DE EJECUCIÓN (Llamado a la Acción para DesignFlow)
DesignFlow, procede de inmediato a actualizar la base de código del proyecto:
1.  **styles.css**: Agregar las variables de animación, configurar los keyframes de entrada (`@keyframes fade-in-up`), definir los estados de hover cinéticos en botones y tarjetas de propiedades, y estructurar el scroll smooth con Intersection Observer.
2.  **index.html & landing-venta-rapida.html**: Agregar las clases de animación `.reveal-on-scroll` y los atributos de retardo correspondientes a las secciones clave.
3.  **main.js**: Programar un script ultra-ligero basado en `IntersectionObserver` para inyectar la clase `.visible` a los elementos a medida que el usuario hace scroll, y mejorar la interactividad de la alternancia de pestañas con animaciones de opacidad y altura.
