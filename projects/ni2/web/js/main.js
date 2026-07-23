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
  initEcosystemWhatsAppLinks();
  initHomeSlider();
  initLightboxGallery();
  initPropertyDetailPage();
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

  const intentSelect = document.getElementById('search-intent');
  const priceInput = document.getElementById('search-price');
  const priceValueLabel = document.getElementById('price-slider-value');
  const priceSliderLabel = document.getElementById('price-slider-label');

  function formatMoney(amount, isRent) {
    if (isRent) {
      return `$${Number(amount).toLocaleString('es-MX')} MXN/mes`;
    } else {
      if (amount >= 1000000) {
        const millions = (amount / 1000000).toFixed(1);
        const formatted = millions.endsWith('.0') ? millions.slice(0, -2) : millions;
        return `$${formatted}M MXN`;
      }
      return `$${Number(amount).toLocaleString('es-MX')} MXN`;
    }
  }

  function updateSliderParams() {
    if (!intentSelect || !priceInput || !priceValueLabel) return;
    const isRent = intentSelect.value === 'rent';
    
    if (isRent) {
      priceInput.min = '5000';
      priceInput.max = '100000';
      priceInput.step = '1000';
      priceInput.value = '30000';
      if (priceSliderLabel) priceSliderLabel.textContent = 'Renta Máxima';
    } else {
      priceInput.min = '1000000';
      priceInput.max = '25000000';
      priceInput.step = '500000';
      priceInput.value = '15000000';
      if (priceSliderLabel) priceSliderLabel.textContent = 'Presupuesto Máximo';
    }
    
    priceValueLabel.textContent = formatMoney(priceInput.value, isRent);
  }

  if (intentSelect) {
    intentSelect.addEventListener('change', updateSliderParams);
  }

  if (priceInput && priceValueLabel) {
    priceInput.addEventListener('input', (e) => {
      const isRent = intentSelect ? intentSelect.value === 'rent' : false;
      priceValueLabel.textContent = formatMoney(e.target.value, isRent);
    });
  }

  // Inicializar al cargar la página
  updateSliderParams();

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
  const priceInput = document.getElementById('search-price');

  if (!intentSelect || !typeSelect || !locationSelect) return;

  const intentVal = intentSelect.value;
  const typeVal = typeSelect.value;
  const locationVal = locationSelect.value;
  const priceVal = priceInput ? parseInt(priceInput.value) : null;

  const cards = document.querySelectorAll('#properties-carousel .property-card');
  const noPropertiesMsg = document.getElementById('no-properties-message');
  let visibleCount = 0;

  cards.forEach(card => {
    const cardIntent = card.getAttribute('data-intent');
    const cardType = card.getAttribute('data-type');
    const cardLocation = card.getAttribute('data-location');
    const cardPrice = parseInt(card.getAttribute('data-price') || '0');

    // Filtros lógicos
    const matchIntent = !intentVal || cardIntent === intentVal;
    const matchType = !typeVal || cardType === typeVal;
    const matchLocation = !locationVal || cardLocation === locationVal;
    const matchPrice = !priceVal || cardPrice <= priceVal;

    if (matchIntent && matchType && matchLocation && matchPrice) {
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
    max_price: priceVal,
    results_count: visibleCount
  });
}

function resetSearchFilters() {
  const intentSelect = document.getElementById('search-intent');
  const typeSelect = document.getElementById('search-property-type');
  const locationSelect = document.getElementById('search-location');
  const priceInput = document.getElementById('search-price');
  const priceValueLabel = document.getElementById('price-slider-value');
  const priceSliderLabel = document.getElementById('price-slider-label');

  if (intentSelect) intentSelect.selectedIndex = 0;
  if (typeSelect) typeSelect.selectedIndex = 0;
  if (locationSelect) locationSelect.selectedIndex = 0;

  if (priceInput && priceValueLabel) {
    priceInput.min = '1000000';
    priceInput.max = '25000000';
    priceInput.step = '500000';
    priceInput.value = '15000000';
    if (priceSliderLabel) priceSliderLabel.textContent = 'Presupuesto Máximo';
    priceValueLabel.textContent = '$15M MXN';
  }

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

// ==========================================
// 8. ENLACES DE WHATSAPP DEL ECOSISTEMA (JESSY, GUS, ADY, VÍCTOR, JAVI)
// ==========================================
function initEcosystemWhatsAppLinks() {
  const links = document.querySelectorAll('.wa-link');
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      
      const specialist = link.getAttribute('data-specialist') || 'ni2';
      const service = link.getAttribute('data-service') || 'Información General';
      
      // Número principal de WhatsApp de ni2
      const phone = '525512345678';
      
      const message = `Hola, me interesa recibir información o cotizar el servicio de ${service} con ni2.`;
      
      const encodedMsg = encodeURIComponent(message);
      const waUrl = `https://wa.me/${phone}?text=${encodedMsg}`;
      
      // Tracking de GA4
      trackGA4Event('click_specialist_whatsapp', {
        specialist_name: specialist,
        service_requested: service,
        link_url: waUrl
      });
      
      // Abrir en nueva ventana
      window.open(waUrl, '_blank');
    });
  });
}

// ==========================================
// 9. DYNAMIC HERO SLIDER (HOMEPAGE)
// ==========================================
function initHomeSlider() {
  const slides = document.querySelectorAll('.hero-slide');
  if (slides.length === 0) return;

  const prevBtn = document.getElementById('slider-btn-prev');
  const nextBtn = document.getElementById('slider-btn-next');
  const dots = document.querySelectorAll('.slider-dot');
  
  let currentSlideIndex = 0;
  let autoplayTimer = null;

  function showSlide(index) {
    // Reset index bounds
    if (index >= slides.length) currentSlideIndex = 0;
    else if (index < 0) currentSlideIndex = slides.length - 1;
    else currentSlideIndex = index;

    // Toggle active slide
    slides.forEach((slide, i) => {
      if (i === currentSlideIndex) {
        slide.classList.add('active');
      } else {
        slide.classList.remove('active');
      }
    });

    // Toggle active dot
    dots.forEach((dot, i) => {
      if (i === currentSlideIndex) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });

    // Track slide view
    trackGA4Event('hero_slide_view', {
      slide_index: currentSlideIndex,
      slide_id: slides[currentSlideIndex].id
    });
  }

  function startAutoplay() {
    stopAutoplay();
    autoplayTimer = setInterval(() => {
      showSlide(currentSlideIndex + 1);
    }, 5000);
  }

  function stopAutoplay() {
    if (autoplayTimer) {
      clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  }

  // Click handlers
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      stopAutoplay();
      showSlide(currentSlideIndex - 1);
      startAutoplay();
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      stopAutoplay();
      showSlide(currentSlideIndex + 1);
      startAutoplay();
    });
  }

  dots.forEach(dot => {
    dot.addEventListener('click', (e) => {
      stopAutoplay();
      const index = parseInt(dot.getAttribute('data-slide') || '0');
      showSlide(index);
      startAutoplay();
    });
  });

  // Start slideshow
  showSlide(0);
  startAutoplay();
}

// ==========================================
// 10. BASE DE DATOS DE PROPIEDADES (ZMG)
// ==========================================
const PROPERTIES_DATABASE = {
  prop1: {
    title: "Departamento de Lujo en Providencia",
    intent: "Venta",
    intentCode: "buy",
    price: 4850000,
    priceStr: "$4,850,000 MXN",
    type: "Departamento",
    typeSummary: "Departamento entero en Guadalajara",
    location: "Guadalajara, Jalisco",
    address: "Av. Providencia 2340, Providencia, Guadalajara, Jal.",
    coords: [20.6923, -103.3812],
    specs: "3 Rec. • 2 Baños • 110 m²",
    description: "Espectacular departamento completamente remodelado ubicado en la zona más exclusiva de Providencia. Cuenta con acabados de granito en cocina, pisos de porcelanato, iluminación LED inteligente y amplios ventanales que ofrecen una iluminación natural envidiable. Ideal para ejecutivos o familias que buscan seguridad, confort y una excelente conectividad vial en Guadalajara.",
    amenities: [
      { name: "Vista a la ciudad", icon: "🏙️" },
      { name: "Cocina equipada", icon: "🍳" },
      { name: "Estacionamiento (2 autos)", icon: "🚗" },
      { name: "Elevador", icon: "🛗" },
      { name: "Seguridad 24/7", icon: "🛡️" },
      { name: "Conexión Wifi de alta velocidad", icon: "📶" }
    ],
    gallery: [
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Fachada Exterior del Edificio' },
      { src: '/ni2/img/loft_americana.jpg', caption: 'Sala de Estar / Interior' },
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Recámara Principal / Acabados' },
      { src: '/ni2/img/loft_americana.jpg', caption: 'Cocina Integral' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Área Común / Lobby' }
    ]
  },
  prop2: {
    title: "Loft Industrial en Colonia Americana",
    intent: "Renta",
    intentCode: "rent",
    price: 26500,
    priceStr: "$26,500 MXN / mes",
    type: "Loft",
    typeSummary: "Loft entero en Colonia Americana",
    location: "Guadalajara, Jalisco",
    address: "Calle Libertad 1420, Colonia Americana, Guadalajara, Jal.",
    coords: [20.6725, -103.3644],
    specs: "1 Rec. • 1.5 Baños • 75 m²",
    description: "Hermoso loft de diseño industrial con techos de doble altura, muros de ladrillo aparente y ventanas de herrería negra de piso a techo. Cuenta con un diseño abierto que integra cocina, comedor y estancia en el primer nivel, y una amplia recámara en mezanina con baño completo. Se ubica en el corazón de la Colonia Americana, rodeado de cafés y restaurantes.",
    amenities: [
      { name: "Diseño industrial", icon: "🧱" },
      { name: "Cocina abierta", icon: "🍳" },
      { name: "Cochera techada", icon: "🚗" },
      { name: "Acepta mascotas", icon: "🐾" },
      { name: "Aire acondicionado", icon: "❄️" },
      { name: "Conexión Wifi de alta velocidad", icon: "📶" }
    ],
    gallery: [
      { src: '/ni2/img/loft_americana.jpg', caption: 'Doble Altura y Ventanales' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Fachada y Accesos del Complejo' },
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Detalle de Escaleras y Mezzanine' },
      { src: '/ni2/img/loft_americana.jpg', caption: 'Sala de Estar y Estancia' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Baño de Visitas' }
    ]
  },
  prop3: {
    title: "Casa Vista Hermosa Bugambilias",
    intent: "Venta",
    intentCode: "buy",
    price: 12900000,
    priceStr: "$12,900,000 MXN",
    type: "Casa",
    typeSummary: "Casa entera en Bugambilias",
    location: "Tlajomulco de Zúñiga, Jalisco",
    address: "Paseo de los Cedros 452, Bugambilias Segunda Sección, Tlajomulco, Jal.",
    coords: [20.6128, -103.4358],
    specs: "4 Rec. • 4.5 Baños • 320 m²",
    description: "Espectacular residencia con vistas panorámicas únicas de la ciudad. Cuenta con cochera subterránea para 4 autos, alberca templada con deck de madera, amplio jardín arbolado, cocina equipada con isla de cuarzo y acabados de mármol en todos los baños. La recámara principal cuenta con vestidor doble y jacuzzi. Fraccionamiento con vigilancia 24/7.",
    amenities: [
      { name: "Alberca templada", icon: "🏊" },
      { name: "Jardín privado", icon: "🌳" },
      { name: "Cochera para 4 autos", icon: "🚗" },
      { name: "Seguridad 24/7", icon: "🛡️" },
      { name: "Vista Panorámica", icon: "🌄" },
      { name: "Cocina con isla", icon: "🍳" }
    ],
    gallery: [
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Fachada con alberca en Bugambilias' },
      { src: '/ni2/img/loft_americana.jpg', caption: 'Cocina y Acabados de Isla' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Detalle de Recámara Principal' },
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Jardín y Vista Exterior' },
      { src: '/ni2/img/loft_americana.jpg', caption: 'Estancia Familiar / Family Room' }
    ]
  },
  prop4: {
    title: "Terreno Habitacional en Valle Real",
    intent: "Venta",
    intentCode: "buy",
    price: 24500000,
    priceStr: "$24,500,000 MXN",
    type: "Terreno",
    typeSummary: "Lote habitacional en Valle Real",
    location: "Zapopan, Jalisco",
    address: "Av. de las Flores Lot 12, Valle Real, Zapopan, Jal.",
    coords: [20.7208, -103.4294],
    specs: "Zona Residencial Premium • Todos los servicios • 550 m²",
    description: "Excelente lote completamente plano ubicado en una de las cerradas más tranquilas del Fraccionamiento Valle Real. Listo para escriturar e iniciar obra. Cuenta con todos los servicios ocultos (agua, luz, telefonía, drenaje), seguridad privada y acceso controlado. Una oportunidad única de inversión patrimonial en la zona de mayor plusvalía.",
    amenities: [
      { name: "Acceso controlado", icon: "🚪" },
      { name: "Servicios ocultos", icon: "⚡" },
      { name: "Lote plano", icon: "📐" },
      { name: "Seguridad 24/7", icon: "🛡️" },
      { name: "Áreas verdes comunes", icon: "🌳" },
      { name: "Casa Club", icon: "🏡" }
    ],
    gallery: [
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Entorno de la Privada' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Vista Aérea del Terreno' },
      { src: '/ni2/img/loft_americana.jpg', caption: 'Accesos y Vigilancia Valle Real' },
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Casa Club y Amenidades Comunes' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Vistas del Fraccionamiento' }
    ]
  },
  prop5: {
    title: "Oficina Corporativa en Puerta de Hierro",
    intent: "Renta",
    intentCode: "rent",
    price: 85000,
    priceStr: "$85,000 MXN / mes",
    type: "Oficina",
    typeSummary: "Oficina Corporativa en Puerta de Hierro",
    location: "Zapopan, Jalisco",
    address: "Paseo de los Virreyes 45, Puerta de Hierro, Zapopan, Jal.",
    coords: [20.7103, -103.4125],
    specs: "Completamente equipada • 2 Baños privados • 180 m²",
    description: "Oficina corporativa AAA en el corazón del distrito financiero de Puerta de Hierro. Cuenta con recepción amueblada, sala de juntas ejecutiva, 4 despachos privados y una amplia área abierta para estaciones de trabajo. Incluye 5 cajones de estacionamiento techados y seguridad integral con CCTV y control de acceso biométrico.",
    amenities: [
      { name: "Acceso biométrico", icon: "🔑" },
      { name: "Sala de juntas", icon: "💼" },
      { name: "Estacionamiento (5 autos)", icon: "🚗" },
      { name: "Seguridad 24/7", icon: "🛡️" },
      { name: "CCTV integrado", icon: "📹" },
      { name: "Aire acondicionado", icon: "❄️" }
    ],
    gallery: [
      { src: '/ni2/img/loft_americana.jpg', caption: 'Lobby Principal del Edificio' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Sala de Juntas Ejecutiva' },
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Área Abierta de Trabajo' },
      { src: '/ni2/img/loft_americana.jpg', caption: 'Recepción y Control' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Vistas al Distrito Financiero' }
    ]
  },
  prop6: {
    title: "Penthouse de Lujo en Chapalita",
    intent: "Venta",
    intentCode: "buy",
    price: 9200000,
    priceStr: "$9,200,000 MXN",
    type: "Penthouse",
    typeSummary: "Penthouse entero en Chapalita",
    location: "San Pedro Tlaquepaque, Jalisco",
    address: "Av. de las Rosas 120, Chapalita, Tlaquepaque, Jal.",
    coords: [20.6653, -103.3986],
    specs: "3 Rec. • 3.5 Baños • 210 m²",
    description: "Extraordinario penthouse de dos niveles con amplia terraza privada que ofrece una espectacular vista a la arboleda de Chapalita. Planta baja con sala, comedor, cocina integral equipada con barra desayunadora y recámara de visitas. Planta alta con recámara principal tipo suite, estudio de TV y acceso directo a la terraza social semi-techada.",
    amenities: [
      { name: "Terraza privada", icon: "🍹" },
      { name: "Cocina integral", icon: "🍳" },
      { name: "Estacionamiento (3 autos)", icon: "🚗" },
      { name: "Elevador directo", icon: "🛗" },
      { name: "Seguridad 24/7", icon: "🛡️" },
      { name: "Estudio de TV", icon: "📺" }
    ],
    gallery: [
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Terraza Privada del Penthouse' },
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Sala y Comedor con vista' },
      { src: '/ni2/img/loft_americana.jpg', caption: 'Cocina Integral de Cuarzo' },
      { src: '/ni2/img/depto_providencia.jpg', caption: 'Recámara Principal / Suite' },
      { src: '/ni2/img/casa_bugambilias.jpg', caption: 'Baño Principal con Tina' }
    ]
  }
};

// ==========================================
// 11. POPUP LIGHTBOX GALLERY (REAL ESTATE)
// ==========================================
function initLightboxGallery() {
  const modal = document.getElementById('lightbox-modal');
  if (!modal) return;

  const slidesContainer = document.getElementById('lightbox-slides');
  const captionText = document.getElementById('lightbox-caption');
  const dotsContainer = document.getElementById('lightbox-dots');
  const prevBtn = document.getElementById('lightbox-btn-prev');
  const nextBtn = document.getElementById('lightbox-btn-next');
  const closeBtn = document.querySelector('.lightbox-close');

  let currentGallery = [];
  let currentImageIndex = 0;

  // Extraer las galerías de la base de datos central
  const propertyGalleries = {};
  for (const id in PROPERTIES_DATABASE) {
    propertyGalleries[id] = PROPERTIES_DATABASE[id].gallery;
  }

  function renderGallery() {
    if (!slidesContainer || !dotsContainer) return;
    slidesContainer.innerHTML = '';
    dotsContainer.innerHTML = '';

    currentGallery.forEach((item, index) => {
      // Crear Slide
      const slide = document.createElement('div');
      slide.className = `lightbox-slide ${index === currentImageIndex ? 'active' : ''}`;
      
      const img = document.createElement('img');
      img.src = item.src;
      img.alt = item.caption;
      
      slide.appendChild(img);
      slidesContainer.appendChild(slide);

      // Crear Dot
      const dot = document.createElement('span');
      dot.className = `lightbox-dot ${index === currentImageIndex ? 'active' : ''}`;
      dot.addEventListener('click', () => {
        showLightboxSlide(index);
      });
      dotsContainer.appendChild(dot);
    });

    updateCaption();
  }

  function updateCaption() {
    if (captionText && currentGallery[currentImageIndex]) {
      captionText.textContent = `${currentImageIndex + 1} de ${currentGallery.length}: ${currentGallery[currentImageIndex].caption}`;
    }
  }

  function showLightboxSlide(index) {
    if (index >= currentGallery.length) currentImageIndex = 0;
    else if (index < 0) currentImageIndex = currentGallery.length - 1;
    else currentImageIndex = index;

    // Toggle active slide
    const slides = document.querySelectorAll('.lightbox-slide');
    slides.forEach((slide, i) => {
      if (i === currentImageIndex) {
        slide.classList.add('active');
      } else {
        slide.classList.remove('active');
      }
    });

    // Toggle active dot
    const dots = document.querySelectorAll('.lightbox-dot');
    dots.forEach((dot, i) => {
      if (i === currentImageIndex) {
        dot.classList.add('active');
      } else {
        dot.classList.remove('active');
      }
    });

    updateCaption();
  }

  function nextLightboxSlide() {
    showLightboxSlide(currentImageIndex + 1);
  }

  function prevLightboxSlide() {
    showLightboxSlide(currentImageIndex - 1);
  }

  function openLightbox(propertyId) {
    currentGallery = propertyGalleries[propertyId] || [];
    if (currentGallery.length === 0) return;

    currentImageIndex = 0;
    renderGallery();
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';

    trackGA4Event('view_property_gallery', {
      property_id: propertyId,
      images_count: currentGallery.length
    });
  }

  function closeLightbox() {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }

  // Bind click events on cards
  document.addEventListener('click', (e) => {
    const target = e.target;
    if (target && (target.classList.contains('open-gallery-btn') || target.hasAttribute('data-property-id'))) {
      const propId = target.getAttribute('data-property-id');
      if (propId) {
        e.preventDefault();
        openLightbox(propId);
      }
    }
  });

  // Bind modal controls
  if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
  if (prevBtn) prevBtn.addEventListener('click', prevLightboxSlide);
  if (nextBtn) nextBtn.addEventListener('click', nextLightboxSlide);

  // Close modal clicking outside content
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeLightbox();
    }
  });

  // Teclado para navegar y salir
  document.addEventListener('keydown', (e) => {
    if (modal.style.display === 'flex') {
      if (e.key === 'Escape') closeLightbox();
      else if (e.key === 'ArrowRight') nextLightboxSlide();
      else if (e.key === 'ArrowLeft') prevLightboxSlide();
    }
  });
}

// ==========================================
// 12. DYNAMIC PROPERTY DETAILS (AIRBNB STYLE)
// ==========================================
function initPropertyDetailPage() {
  const mapContainer = document.getElementById('map-container');
  if (!mapContainer) return;

  // 1. Obtener ID de propiedad de la URL (?id=prop1)
  const urlParams = new URLSearchParams(window.location.search);
  const propertyId = urlParams.get('id') || 'prop1';

  // 2. Buscar datos en la base de datos
  const prop = PROPERTIES_DATABASE[propertyId];
  if (!prop) {
    document.getElementById('prop-title').textContent = 'Propiedad no encontrada';
    return;
  }

  // 3. Poblar textos básicos
  document.title = `ni2 | ${prop.title}`;
  document.getElementById('prop-title').textContent = prop.title;
  document.getElementById('prop-location-summary').textContent = prop.location;
  document.getElementById('prop-intent-badge').textContent = prop.intent;
  
  if (prop.intentCode === 'rent') {
    document.getElementById('prop-intent-badge').style.backgroundColor = 'var(--accent-color)';
  }

  document.getElementById('prop-type-summary').textContent = prop.typeSummary;
  document.getElementById('prop-specs-summary').textContent = prop.specs;
  document.getElementById('prop-description-text').textContent = prop.description;
  document.getElementById('prop-location-address').textContent = prop.address;
  document.getElementById('prop-price-card').textContent = prop.priceStr;

  // 4. Poblar las imágenes de la cuadrícula de Airbnb (requiere 5 imágenes)
  const imgLarge = document.getElementById('img-large');
  const imgSmall1 = document.getElementById('img-small-1');
  const imgSmall2 = document.getElementById('img-small-2');
  const imgSmall3 = document.getElementById('img-small-3');
  const imgSmall4 = document.getElementById('img-small-4');

  if (imgLarge) {
    imgLarge.src = prop.gallery[0] ? prop.gallery[0].src : '/ni2/img/depto_providencia.jpg';
    imgLarge.alt = prop.gallery[0] ? prop.gallery[0].caption : '';
    imgLarge.setAttribute('data-property-id', propertyId);
  }
  if (imgSmall1 && prop.gallery[1]) {
    imgSmall1.src = prop.gallery[1].src;
    imgSmall1.alt = prop.gallery[1].caption;
    imgSmall1.setAttribute('data-property-id', propertyId);
  }
  if (imgSmall2 && prop.gallery[2]) {
    imgSmall2.src = prop.gallery[2].src;
    imgSmall2.alt = prop.gallery[2].caption;
    imgSmall2.setAttribute('data-property-id', propertyId);
  }
  if (imgSmall3 && prop.gallery[3]) {
    imgSmall3.src = prop.gallery[3].src;
    imgSmall3.alt = prop.gallery[3].caption;
    imgSmall3.setAttribute('data-property-id', propertyId);
  }
  if (imgSmall4 && prop.gallery[4]) {
    imgSmall4.src = prop.gallery[4].src;
    imgSmall4.alt = prop.gallery[4].caption;
    imgSmall4.setAttribute('data-property-id', propertyId);
  }

  // Botón "Mostrar todas las fotos"
  const btnShowAll = document.getElementById('btn-show-all');
  if (btnShowAll) {
    btnShowAll.setAttribute('data-property-id', propertyId);
  }

  // 5. Poblar lista de amenidades
  const amenitiesList = document.getElementById('prop-amenities-list');
  if (amenitiesList) {
    amenitiesList.innerHTML = '';
    prop.amenities.forEach(item => {
      const itemEl = document.createElement('div');
      itemEl.className = 'amenity-item-wrapper';
      
      const iconEl = document.createElement('span');
      iconEl.className = 'amenity-icon';
      iconEl.textContent = item.icon;
      
      const textEl = document.createElement('span');
      textEl.textContent = item.name;
      
      itemEl.appendChild(iconEl);
      itemEl.appendChild(textEl);
      amenitiesList.appendChild(itemEl);
    });
  }

  // 6. Inicializar Mapa Interactivo de Leaflet.js
  try {
    const map = L.map('map-container', {
      center: prop.coords,
      zoom: 15,
      scrollWheelZoom: false
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Pin personalizado de ni2
    const marker = L.marker(prop.coords).addTo(map);
    marker.bindPopup(`<b>ni2: ${prop.title}</b><br>${prop.location}`).openPopup();
  } catch (err) {
    console.error('Error al inicializar el mapa Leaflet:', err);
  }

  // 7. Botón de WhatsApp dinámico y centralizado
  const btnWA = document.getElementById('btn-booking-wa');
  if (btnWA) {
    btnWA.addEventListener('click', () => {
      const phone = '525512345678';
      const message = `Hola, me interesa agendar una visita o recibir más información de la propiedad: "${prop.title}" (${prop.intent}) que vi en el portal ni2.`;
      const encodedMsg = encodeURIComponent(message);
      const waUrl = `https://wa.me/${phone}?text=${encodedMsg}`;
      
      // GA4 track
      trackGA4Event('click_booking_whatsapp', {
        property_id: propertyId,
        property_title: prop.title,
        link_url: waUrl
      });
      
      window.open(waUrl, '_blank');
    });
  }
}

