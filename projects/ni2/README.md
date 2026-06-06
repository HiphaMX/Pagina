# Proyecto "ni2" - Documentación de Estrategia, Arquitectura de Información y Medición

Este documento detalla la planificación estratégica, el diseño UX/UI y el plan de medición digital para **ni2**, un agente de bienes raíces de "Respuesta y Trámite Ágil" enfocado en optimización de conversiones, experiencia móvil y campañas de Google Ads de alta rentabilidad.

---

## 1. PROPUESTA DE VALOR Y DIFERENCIADOR (Enfoque estilo Seguros Hiscox)

El mercado inmobiliario está lleno de intermediarios que no responden a tiempo, listados duplicados, formularios infinitos y llamadas invasivas de spam. **ni2** se posiciona bajo el enfoque de **"Inmobiliaria de Respuesta y Trámite Ágil"**, un modelo de negocio centrado en la eficiencia operativa, la transparencia y el respeto al tiempo del usuario.

### Copys de Conversión Específicos (Resolución de Dolores Reales)

*   **Para Propietarios (Vendedores/Rentadores):**
    > **Dolor**: "No sé cuánto vale mi casa, los agentes tardan semanas en darme un precio y me piden firmar exclusividades eternas."
    > **Solución/Copy ni2**: *"Evaluamos tu propiedad en menos de 48 horas. Sin avalúos inflados, sin exclusividades obligatorias, sin burocracia. Recibe una oferta de comercialización ágil hoy mismo."*
    
*   **Para Buscadores (Compradores/Arrendatarios):**
    > **Dolor**: "Portales llenos de anuncios duplicados, propiedades que ya no están disponibles, y spam interminable tras registrarme."
    > **Solución/Copy ni2**: *"Proceso de filtrado rápido y verificado. Sin ventanas emergentes molestas, sin propiedades fantasmas, sin llamadas de spam. Solo listados actualizados en tiempo real y asesoramiento directo por WhatsApp en menos de 10 minutos."*

---

## 2. WIREFRAME DE CONTENIDO: SECCIÓN PRINCIPAL (HERO SECTION) - HOME

Este wireframe detalla la distribución de contenidos, jerarquía visual y textos de conversión (copywriting) para la cabecera principal de la página de inicio, aplicando el estilo limpio y de grillas de **Tenity**.

```
+-------------------------------------------------------------------------------------------------+
|  [ni2] (Logo)                  [Buscar Propiedades]    [Soy Propietario]    [Llamar: 55-1234-5678] (tel)  |
+-------------------------------------------------------------------------------------------------+
|                                                                                                 |
|   INMOBILIARIA DE RESPUESTA Y TRÁMITE ÁGIL                                                      |
|   <h1>Tu propiedad vendida, rentada o encontrada. Sin burocracia.</h1>                          |
|   <p>Evaluamos tu inmueble en 48 horas o filtramos tu búsqueda sin spam ni pérdidas de tiempo.</p>|
|                                                                                                 |
|   +-----------------------------------------------------------------------------------------+   |
|   |  [ QUIERO COMPRAR / RENTAR ]             [ QUIERO VENDER / RENTAR MI PROPIEDAD ]         |   |
|   |  (Pestaña Activa: Buscador Rápido)       (Pestaña: Captación Propietarios)              |   |
|   |                                                                                         |   |
|   |  +------------------+  +------------------+  +------------------+  +-----------------+  |   |
|   |  | ¿Qué buscas?      |  | Tipo de Inmueble |  | Ubicación        |  | [ BUSCAR AHORA ]|  |   |
|   |  | [Comprar / Rentar]|  | [Casa/Depto/Ter] |  | [Zona / Alcaldía]|  | (CTA Emerald)   |  |   |
|   |  +------------------+  +------------------+  +------------------+  +-----------------+  |   |
|   +-----------------------------------------------------------------------------------------+   |
|                                                                                                 |
|   [✓] Valuación en < 48 hrs    [✓] Cero Spam / Contacto WhatsApp    [✓] Trámites 100% Digitales |
|                                                                                                 |
+-------------------------------------------------------------------------------------------------+
```

### Distribución de Contenido y Copywriting (Código HTML Sugerido)

```html
<section class="hero-section">
  <div class="hero-container">
    <span class="badge-tagline">Inmobiliaria de Respuesta y Trámite Ágil</span>
    <h1 class="hero-title">Tu propiedad vendida, rentada o encontrada. <strong>Sin burocracia.</strong></h1>
    <p class="hero-subtitle">Evaluamos tu inmueble en menos de 48 horas o filtramos tu búsqueda sin spam, ventanas emergentes ni pérdidas de tiempo.</p>

    <!-- Caja de Conversión Principal con Pestañas -->
    <div class="conversion-box">
      <div class="tab-headers">
        <button class="tab-btn active" id="tab-search" onclick="switchTab('search')">Quiero Comprar o Rentar</button>
        <button class="tab-btn" id="tab-sell" onclick="switchTab('sell')">Quiero Vender o Rentar mi Propiedad</button>
      </div>

      <!-- Pestaña 1: Buscador Rápido (Compradores/Inquilinos) -->
      <form class="tab-content active" id="content-search" action="/search" method="GET">
        <div class="form-grid-row">
          <div class="form-group">
            <label for="search-intent">¿Qué buscas?</label>
            <select id="search-intent" name="intent">
              <option value="buy">Comprar</option>
              <option value="rent">Rentar</option>
            </select>
          </div>
          <div class="form-group">
            <label for="property-type">Tipo de propiedad</label>
            <select id="property-type" name="type">
              <option value="house">Casa</option>
              <option value="apartment">Departamento</option>
              <option value="land">Terreno</option>
            </select>
          </div>
          <div class="form-group">
            <label for="location">Ubicación</label>
            <select id="location" name="location">
              <option value="cdmx-sur">CDMX - Zona Sur</option>
              <option value="cdmx-poniente">CDMX - Zona Poniente</option>
              <option value="cdmx-delvalle">CDMX - Col. Del Valle / Narvarte</option>
              <option value="cdmx-polanco">CDMX - Polanco / Lomas</option>
            </select>
          </div>
          <button type="submit" class="cta-button-accent" id="cta-hero-buscar">Buscar Propiedades</button>
        </div>
      </form>

      <!-- Pestaña 2: Acceso Rápido Propietarios -->
      <div class="tab-content" id="content-sell" style="display: none;">
        <div class="owner-quick-pitch">
          <p>Obtén un análisis comercial rápido de tu inmueble. Evaluamos tu propiedad en menos de 48 horas sin costo.</p>
          <a href="#propietarios-form" class="cta-button-accent" id="cta-hero-vender" onclick="scrollToElement('propietarios-form')">Iniciar Valuación Gratuita</a>
        </div>
      </div>
    </div>

    <!-- Indicadores de Confianza Fricción Cero -->
    <div class="trust-bullets">
      <div class="bullet-item">
        <svg class="bullet-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
        </svg>
        <span>Valuación en &lt; 48 horas</span>
      </div>
      <div class="bullet-item">
        <svg class="bullet-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clip-rule="evenodd"/>
        </svg>
        <span>Contacto directo vía WhatsApp</span>
      </div>
      <div class="bullet-item">
        <svg class="bullet-icon" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm3 10a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H7a1 1 0 01-1-1v-3zm7 2a1 1 0 011-1h2a1 1 0 011 1v1a1 1 0 01-1 1h-2a1 1 0 01-1-1v-1z" clip-rule="evenodd"/>
        </svg>
        <span>Trámites 100% digitales y ágiles</span>
      </div>
    </div>
  </div>
</section>
```

---

## 3. DISEÑO DETALLADO DEL FORMULARIO DE CAPTACIÓN PARA PROPIETARIOS

Para cumplir con la directriz de **alta conversión y fricción cero**, el formulario de captación para propietarios se diseña como una estructura secuencial, eliminando campos irrelevantes en las etapas iniciales y utilizando validaciones ágiles.

### Estructura UX y Campos del Formulario (ID Único: `propietarios-form`)

*   **Paso 1: Datos Básicos del Inmueble (Filtro Rápido)**
    *   *Objetivo*: Captar el tipo y ubicación de la propiedad con mínimo esfuerzo de teclado.
    *   *Campos*:
        1.  **Tipo de Propiedad** (Botones de opción / Radio cards de gran tamaño táctil: *Casa, Departamento, Terreno, Oficina*).
        2.  **Ubicación / Alcaldía o Zona** (Menú desplegable limpio con buscador predictivo: *ej. Benito Juárez, Coyoacán, Miguel Hidalgo, Álvaro Obregón*).
        3.  **¿Cuál es tu objetivo?** (Botones de opción: *Vender rápido, Rentar bajo contrato seguro*).
*   **Paso 2: Valor Estimado e Intención (Segmentación)**
    *   *Campos*:
        4.  **Rango de Valor Estimado** (Menú desplegable con rangos amplios para evitar que el usuario deba escribir una cifra exacta: *ej. Menos de $2M, $2M - $4M, $4M - $8M, Más de $8M MXN*).
        5.  **¿Qué tanta prisa tienes por cerrar?** (Botones de opción de alta conversión: *Urgente < 30 días, Intermedio < 3 meses, Solo quiero evaluar mi propiedad por ahora*).
*   **Paso 3: Datos de Contacto Ágil (Fricción Cero)**
    *   *Campos*:
        6.  **Nombre Completo** (Input de texto simple con autocompletado nativo habilitado: `autocomplete="name"`).
        7.  **WhatsApp / Teléfono Móvil** (Input de tipo telefónico `type="tel"`, validación de 10 dígitos. Mensaje de soporte: *"Te contactaremos exclusivamente por WhatsApp en menos de 10 minutos"*).

### Lógica UX y Reglas del Formulario
1.  **Validación en tiempo real**: Mensajes de error visuales de estilo sutil bajo el campo utilizando el selector `:user-valid` y `:user-invalid` de CSS para evitar disparar alertas molestas antes de que el usuario termine de escribir.
2.  **Sin ventanas emergentes**: El formulario vive de forma nativa en la parte media de la página o en una sección dedicada del Home.
3.  **Progreso Visual**: Una línea de progreso sutil y delgada (`2px`) en la parte superior del formulario indica al usuario que está a solo 3 breves pasos de recibir su valuación.

---

## 4. ESTRUCTURA DE LANDING PAGE DE CONVERSIÓN ("VENTA DE CASAS RÁPIDAS")

Esta Landing Page está estrictamente diseñada para recibir el tráfico pagado de campañas de Google Ads asociadas a intenciones de venta ágil ("vender casa rápido", "rematar propiedad cdmx", "agente inmobiliario urgente").

### Estructura de Secciones (de Arriba a Abajo)

1.  **Cabecera Minimalista (Header)**:
    *   Logo de **ni2** alineado a la izquierda.
    *   Sin menú de navegación principal (para evitar fugas de tráfico/clics distractores).
    *   Único elemento a la derecha: Botón de llamada telefónica directa: `tel:5512345678` con icono de teléfono en verde esmeralda y el texto: *"¿Urgencia? Llama ahora al 55-1234-5678 (Respuesta en 1 minuto)"*.
2.  **Sección Hero de Conversión Exacta (Arriba del pliegue / Above the Fold)**:
    *   **Título H1 Directo**: *"Vendemos tu casa en CDMX en menos de 30 días. Valuación gratuita en 48 horas."*
    *   **Subtítulo**: *Olvídate de comisiones abusivas, exclusivas eternas y papeleos interminables. Evaluamos tu propiedad sin costo y la promovemos de inmediato ante compradores calificados.*
    *   **Formulario Integrado a la Derecha (en Desktop) / Justo Abajo (en Mobile)**: El formulario multipaso ágil de 3 pasos (detallado anteriormente) con un CTA Emerald potente: *"Quiero Valuación en 48 horas"*.
3.  **Sección de Comparativa Competitiva (Dolor vs. Solución ni2)**:
    *   Diseñada como una tabla/rejilla comparativa de grillas estilo Tenity que confronta el servicio tradicional contra ni2:
        *   *Inmobiliarias Tradicionales*: Contratos de exclusividad forzosa por 6 meses, valuaciones que tardan semanas, decenas de visitas de curiosos no calificados, comisiones del 6%.
        *   *El Método ni2*: Cero contratos de exclusividad obligatoria, valuación comercial en 48 horas, visitas agendadas solo con compradores con crédito pre-aprobado verificado, comisión justa del 4%.
4.  **Sección del Proceso en 3 Pasos Simples**:
    *   *Paso 1*: Completas el formulario rápido (2 minutos).
    *   *Paso 2*: Recibes la valuación comercial y propuesta ágil de venta en 48 horas.
    *   *Paso 3*: Promocionamos tu casa con tecnología de punta y la vendemos en tiempo récord.
5.  **Sección de Testimonios y Prueba Social de Alta Calidad**:
    *   Tres testimonios reales con fotografía, nombre, alcaldía y días transcurridos para la venta:
        *   *"Vendí mi departamento en la Col. Del Valle en 24 días. El trámite fue transparente y la atención digital por WhatsApp impecable."* - Carlos M., 24 días.
6.  **Footer Simple**:
    *   Enlace al Aviso de Privacidad y Términos y Condiciones.
    *   Copyright 2026 ni2.

---

## 5. PLAN DE MEDICIÓN Y ANALÍTICA DIGITAL (CÓDIGO DE IMPLEMENTACIÓN)

Para el correcto funcionamiento en Google Analytics 4 (GA4), se implementará el siguiente código de seguimiento en `projects/ni2/web/js/main.js` para registrar las interacciones de manera estructurada:

### Código de Tracking de Eventos (Ejemplo Javascript)

```javascript
// Asegurar que GA4 está cargado antes de disparar eventos
function trackGA4Event(eventName, eventParams) {
  if (typeof gtag === 'function') {
    gtag('event', eventName, eventParams);
    console.log(`[GA4 Event] ${eventName}`, eventParams);
  } else {
    console.warn(`[GA4 Offline/Mock] Evento "${eventName}" no enviado (gtag no definido):`, eventParams);
  }
}

// 1. Registro de Interacción de Botones de Intención Rival (A/B Test)
document.addEventListener('DOMContentLoaded', () => {
  const ctaBuscar = document.getElementById('cta-hero-buscar');
  const ctaVender = document.getElementById('cta-hero-vender');

  if (ctaBuscar) {
    ctaBuscar.addEventListener('click', () => {
      trackGA4Event('click_cta_buscar', {
        event_category: 'engagement',
        event_label: 'Quiero Comprar o Rentar',
        location: 'hero_tab_search'
      });
    });
  }

  if (ctaVender) {
    ctaVender.addEventListener('click', () => {
      trackGA4Event('click_cta_vender', {
        event_category: 'engagement',
        event_label: 'Iniciar Valuacion Propietarios',
        location: 'hero_tab_sell'
      });
    });
  }
});

// 2. Registro del Flujo del Formulario (Form Funnel Optimization)
let formStarted = false;

function trackFormStep(stepNumber, stepName) {
  trackGA4Event('form_progress', {
    form_id: 'propietarios_form',
    step_number: stepNumber,
    step_name: stepName
  });
}

function initFormTracking() {
  const formInputs = document.querySelectorAll('#propietarios-form input, #propietarios-form select');
  
  formInputs.forEach(input => {
    input.addEventListener('focus', () => {
      if (!formStarted) {
        formStarted = true;
        trackGA4Event('form_start', {
          form_id: 'propietarios_form'
        });
      }
    });
  });
}

function trackFormSuccess() {
  trackGA4Event('lead_captured', {
    form_id: 'propietarios_form',
    transaction_type: document.querySelector('input[name="owner-intent"]:checked')?.value || 'vender',
    lead_quality: document.querySelector('select[name="owner-urgency"]')?.value || 'no_specified'
  });
}
```
