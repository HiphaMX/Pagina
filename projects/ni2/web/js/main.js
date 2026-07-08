/**
 * Proyecto ni2 - Lógica Interactiva y Optimización de Conversiones
 * © 2026 ni2 Inmobiliaria Ágil
 */

document.addEventListener('DOMContentLoaded', () => {
  // Inicializaciones
  initTabs();
  initMultiStepForm();
  initCarousel();
  initNativeCallClickTracking();
  initScrollReveal();
  initSearchFilter();
});

// ==========================================
// 1. TABS: QUIERO COMPRAR vs QUIERO VENDER
// ==========================================
function initTabs() {
  const tabSearch = document.getElementById('tab-search');
  const tabSell = document.getElementById('tab-sell');
  const tabMaintenance = document.getElementById('tab-maintenance');
  const contentSearch = document.getElementById('content-search');
  const contentSell = document.getElementById('content-sell');
  const contentMaintenance = document.getElementById('content-maintenance');

  if (!tabSearch || !tabSell || !tabMaintenance) return;

  function deactivateAll() {
    tabSearch.classList.remove('active');
    tabSell.classList.remove('active');
    tabMaintenance.classList.remove('active');
    contentSearch.classList.remove('active');
    contentSell.classList.remove('active');
    contentMaintenance.classList.remove('active');
    contentSearch.style.display = 'none';
    contentSell.style.display = 'none';
    contentMaintenance.style.display = 'none';
  }

  tabSearch.addEventListener('click', () => {
    deactivateAll();
    tabSearch.classList.add('active');
    contentSearch.classList.add('active');
    contentSearch.style.display = 'block';

    // Analytics click track
    trackGA4Event('click_cta_buscar', {
      event_category: 'engagement',
      event_label: 'Cambio a Buscar Propiedades',
      location: 'hero_tabs'
    });
  });

  tabSell.addEventListener('click', () => {
    deactivateAll();
    tabSell.classList.add('active');
    contentSell.classList.add('active');
    contentSell.style.display = 'block';

    // Analytics click track
    trackGA4Event('click_cta_vender', {
      event_category: 'engagement',
      event_label: 'Cambio a Vender o Rentar',
      location: 'hero_tabs'
    });
  });

  tabMaintenance.addEventListener('click', () => {
    deactivateAll();
    tabMaintenance.classList.add('active');
    contentMaintenance.classList.add('active');
    contentMaintenance.style.display = 'block';

    // Analytics click track
    trackGA4Event('click_cta_mantenimiento_tab', {
      event_category: 'engagement',
      event_label: 'Cambio a Remodelar o Construir',
      location: 'hero_tabs'
    });
  });
}

// ==========================================
// 2. FORMULARIO MULTIPASO CONDICIONAL (PROPIETARIOS)
// ==========================================
function initMultiStepForm() {
  const form = document.getElementById('propietarios-form');
  if (!form) return;

  const steps = form.querySelectorAll('.form-step');
  const nextBtns = form.querySelectorAll('.btn-next');
  const prevBtns = form.querySelectorAll('.btn-prev');
  const progressFill = document.getElementById('form-progress-fill');
  const currentStepLabel = document.getElementById('current-step-label');
  
  let currentStep = 0;
  let formStarted = false;

  // Actualizar UI del paso
  function updateStepUI() {
    steps.forEach((step, idx) => {
      if (idx === currentStep) {
        step.classList.add('active');
        step.style.display = 'block';
      } else {
        step.classList.remove('active');
        step.style.display = 'none';
      }
    });

    // Actualizar progreso sutil
    const percent = ((currentStep + 1) / steps.length) * 100;
    if (progressFill) {
      progressFill.style.width = `${percent}%`;
    }
    if (currentStepLabel) {
      currentStepLabel.textContent = `Paso ${currentStep + 1} de ${steps.length}`;
    }

    // Tracking de paso alcanzado
    if (currentStep > 0) {
      trackGA4Event('form_progress', {
        form_id: 'propietarios_form',
        step_number: currentStep + 1,
        step_name: steps[currentStep].getAttribute('data-step-name')
      });
    }
  }

  // Radio cards interacción visual (.option-card)
  const radioContainers = form.querySelectorAll('.options-grid');
  radioContainers.forEach(container => {
    const cards = container.querySelectorAll('.option-card');
    cards.forEach(card => {
      const radio = card.querySelector('input[type="radio"]');
      
      // Sincronizar estado inicial
      if (radio && radio.checked) {
        card.classList.add('selected');
      }

      card.addEventListener('click', () => {
        // Remover seleccionado de vecinos
        cards.forEach(c => c.classList.remove('selected'));
        // Seleccionar esta card
        card.classList.add('selected');
        if (radio) {
          radio.checked = true;
          // Disparar evento change manual para activar tracking o lógica condicional
          radio.dispatchEvent(new Event('change', { bubbles: true }));
        }

        // Fricción cero: Activar inicio del formulario
        triggerFormStart();
      });
    });
  });

  // Trackear inicio del formulario al enfocar o clickear primer campo
  const formInputs = form.querySelectorAll('input, select');
  formInputs.forEach(input => {
    input.addEventListener('focus', triggerFormStart);
    input.addEventListener('change', triggerFormStart);
  });

  function triggerFormStart() {
    if (!formStarted) {
      formStarted = true;
      trackGA4Event('form_start', {
        form_id: 'propietarios_form'
      });
    }
  }

  // Validación de paso actual
  function validateCurrentStep() {
    const stepEl = steps[currentStep];
    let isValid = true;

    // Buscar campos obligatorios en el paso actual
    const inputs = stepEl.querySelectorAll('input[required], select[required]');
    inputs.forEach(input => {
      const errorMsg = stepEl.querySelector(`.form-error-msg[data-error-for="${input.id || input.name}"]`);
      
      if (input.type === 'radio') {
        const name = input.name;
        const checkedRadio = stepEl.querySelector(`input[name="${name}"]:checked`);
        if (!checkedRadio) {
          isValid = false;
          if (errorMsg) errorMsg.style.display = 'block';
        } else {
          if (errorMsg) errorMsg.style.display = 'none';
        }
      } else {
        if (!input.value.trim()) {
          isValid = false;
          input.classList.add('invalid');
          if (errorMsg) errorMsg.style.display = 'block';
        } else {
          input.classList.remove('invalid');
          if (errorMsg) errorMsg.style.display = 'none';

          // Validación extra de teléfono (10 dígitos)
          if (input.type === 'tel') {
            const cleanVal = input.value.replace(/\D/g, '');
            if (cleanVal.length < 10) {
              isValid = false;
              input.classList.add('invalid');
              if (errorMsg) {
                errorMsg.textContent = 'Ingresa un WhatsApp válido de 10 dígitos.';
                errorMsg.style.display = 'block';
              }
            }
          }
        }
      }
    });

    return isValid;
  }

  // Botón Siguiente
  nextBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (validateCurrentStep()) {
        if (currentStep < steps.length - 1) {
          currentStep++;
          updateStepUI();
        }
      }
    });
  });

  // Botón Anterior
  prevBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (currentStep > 0) {
        currentStep--;
        updateStepUI();
      }
    });
  });

  // Enviar formulario (Paso Final)
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    if (validateCurrentStep()) {
      // Estado de carga en botón de envío
      const submitBtn = form.querySelector('button[type="submit"]');
      const originalText = submitBtn ? submitBtn.textContent : 'Enviar';
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Enviando...';
        submitBtn.style.opacity = '0.7';
      }

      // Simular respuesta ágil (menos de 1 segundo)
      setTimeout(() => {
        // Analytics Success Track
        const propType = form.querySelector('input[name="property-type"]:checked')?.value || 'house';
        const urgency = form.querySelector('input[name="urgency"]:checked')?.value || 'evaluate';
        const range = form.querySelector('select[name="price-range"]')?.value || 'not_specified';
        const objective = form.querySelector('input[name="objective"]:checked')?.value || 'sell';

        trackGA4Event('lead_captured', {
          form_id: 'propietarios_form',
          property_type: propType,
          urgency_speed: urgency,
          price_range: range,
          property_objective: objective,
          lead_quality_score: urgency === 'urgent' ? 10 : (urgency === 'medium' ? 7 : 4)
        });

        // Mostrar pantalla de éxito
        const formInner = document.getElementById('form-multistep-inner');
        const successMessage = document.getElementById('form-success-message');
        if (formInner && successMessage) {
          formInner.style.display = 'none';
          successMessage.style.display = 'block';
          successMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }, 800);
    }
  });

  // Inicializar estado UI
  updateStepUI();
}

// ==========================================
// 3. PROPIEDADES CAROUSEL (TOUCH COMPATIBLE)
// ==========================================
function initCarousel() {
  const container = document.getElementById('properties-carousel');
  const btnPrev = document.getElementById('carousel-btn-prev');
  const btnNext = document.getElementById('carousel-btn-next');

  if (!container || !btnPrev || !btnNext) return;

  const scrollAmount = 360; // Ancho aproximado de la tarjeta + gap

  btnPrev.addEventListener('click', () => {
    container.scrollBy({
      left: -scrollAmount,
      behavior: 'smooth'
    });

    trackGA4Event('carousel_navigation', {
      direction: 'left',
      section: 'propiedades_destacadas'
    });
  });

  btnNext.addEventListener('click', () => {
    container.scrollBy({
      left: scrollAmount,
      behavior: 'smooth'
    });

    trackGA4Event('carousel_navigation', {
      direction: 'right',
      section: 'propiedades_destacadas'
    });
  });
}

// ==========================================
// 4. SEGUIMIENTO DE LLAMADAS NATIVAS
// ==========================================
function initNativeCallClickTracking() {
  const callLinks = document.querySelectorAll('a[href^="tel:"]');
  callLinks.forEach(link => {
    link.addEventListener('click', () => {
      const phoneNumber = link.getAttribute('href').replace('tel:', '');
      trackGA4Event('click_native_call', {
        phone_number: phoneNumber,
        location: link.classList.contains('phone-cta-link') ? 'header' : 'body/landing'
      });
    });
  });
}

// ==========================================
// 5. GA4 ANALYTICS CONSOLE SIMULATOR (MOCK DE EVENTOS)
// ==========================================
function trackGA4Event(eventName, eventParams) {
  // 1. Envío real a gtag si existe
  if (typeof gtag === 'function') {
    gtag('event', eventName, eventParams);
  }

  // 2. Imprimir en consola de desarrollador
  console.log(`%c[GA4 EVENT] ${eventName}`, 'color: #344152; font-weight: bold; font-size: 11px;', eventParams);
}

// Utilidad para scroll suave interactivo
window.scrollToElement = function(elementId) {
  const element = document.getElementById(elementId);
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' });
    
    // Si se desplaza a la sección de propietarios, asegurar que el tab correspondiente esté activo
    if (elementId === 'propietarios-section') {
      const tabSell = document.getElementById('tab-sell');
      if (tabSell && !tabSell.classList.contains('active')) {
        tabSell.click();
      }
    }
  }
};

// ==========================================
// 6. SCROLL REVEAL (TENITY-STYLE INTERACTION)
// ==========================================
function initScrollReveal() {
  const revealElements = document.querySelectorAll('.reveal-on-scroll');
  
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target); // Dejar de observar tras animar
          
          // Registrar evento GA4 de visibilidad de sección
          const sectionId = entry.target.id || entry.target.className.split(' ')[0];
          trackGA4Event('section_view', {
            section_id: sectionId,
            location: window.location.pathname.split('/').pop() || 'home'
          });
        }
      });
    }, {
      threshold: 0.1, // Gatillar al revelar el 10% del elemento
      rootMargin: '0px 0px -40px 0px'
    });
    
    revealElements.forEach(el => {
      observer.observe(el);
    });
  } else {
    // Fallback: hacer visible de inmediato si no hay soporte
    revealElements.forEach(el => {
      el.classList.add('visible');
    });
  }
}

// ==========================================
// 7. FILTRADO ACTIVO DE PROPIEDADES (BUSCADOR HERO)
// ==========================================
function initSearchFilter() {
  const searchForm = document.getElementById('content-search');
  if (!searchForm) return;

  // Escuchar el envío del formulario de búsqueda
  searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    executeFilter();
    
    // Desplazamiento suave a la sección de resultados
    const propertiesSection = document.getElementById('properties-carousel-section');
    if (propertiesSection) {
      propertiesSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });

  // Escuchar clics globales para el botón de restablecer filtros (dentro del mensaje de error)
  document.addEventListener('click', (e) => {
    if (e.target && e.target.id === 'btn-reset-filters') {
      e.preventDefault();
      resetSearchFilters();
    }
  });
}

function executeFilter() {
  const intentSelect = document.getElementById('search-intent');
  const typeSelect = document.getElementById('search-property-type');
  const locationSelect = document.getElementById('search-location');

  if (!intentSelect || !typeSelect || !locationSelect) return;

  const intentVal = intentSelect.value;
  const typeVal = typeSelect.value;
  const locationVal = locationSelect.value;

  const cards = document.querySelectorAll('#properties-carousel .property-card');
  const noPropertiesMsg = document.getElementById('no-properties-message');
  let visibleCount = 0;

  cards.forEach(card => {
    const cardIntent = card.getAttribute('data-intent');
    const cardType = card.getAttribute('data-type');
    const cardLocation = card.getAttribute('data-location');

    // Filtros lógicos
    const matchIntent = !intentVal || cardIntent === intentVal;
    const matchType = !typeVal || cardType === typeVal;
    const matchLocation = !locationVal || cardLocation === locationVal;

    if (matchIntent && matchType && matchLocation) {
      card.style.display = 'flex';
      visibleCount++;
    } else {
      card.style.display = 'none';
    }
  });

  // Mostrar u ocultar mensaje amigable de "sin resultados"
  if (noPropertiesMsg) {
    if (visibleCount === 0) {
      noPropertiesMsg.style.display = 'flex';
    } else {
      noPropertiesMsg.style.display = 'none';
    }
  }

  // Registrar evento GA4 de búsqueda
  trackGA4Event('property_search', {
    search_intent: intentVal,
    property_type: typeVal,
    search_location: locationVal,
    results_count: visibleCount
  });
}

function resetSearchFilters() {
  const intentSelect = document.getElementById('search-intent');
  const typeSelect = document.getElementById('search-property-type');
  const locationSelect = document.getElementById('search-location');

  if (intentSelect) intentSelect.selectedIndex = 0;
  if (typeSelect) typeSelect.selectedIndex = 0;
  if (locationSelect) locationSelect.selectedIndex = 0;

  const cards = document.querySelectorAll('#properties-carousel .property-card');
  cards.forEach(card => {
    card.style.display = 'flex';
  });

  const noPropertiesMsg = document.getElementById('no-properties-message');
  if (noPropertiesMsg) {
    noPropertiesMsg.style.display = 'none';
  }

  // Registrar evento GA4 de reinicio
  trackGA4Event('property_search_reset', {
    action: 'reset_all_filters'
  });
}

