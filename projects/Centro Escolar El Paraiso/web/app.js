/**
 * 🇨🇭 Centro Escolar El Paraíso - Frontend Logic
 * Media Arts & BNS Motion Adaptations - Splash Loader & Scroll Theme Shifting
 */

document.addEventListener('DOMContentLoaded', () => {
  initSplashLoader();
  initNavigation();
  initChatbot();
  initLeadMagnetForm();
  initTestimonialSlider();
  initAnnouncementsSlider();
  initStatsCounters();
  initSplitTextScroll();
  initThemeShifting();
  initRotaryHero();
  initOverlayMenu();
});

/* ==========================================================================
   0. CINEMATIC LOADING SPLASH SCREEN (Media Arts Style)
   ========================================================================== */
function initSplashLoader() {
  const splash = document.getElementById('loading-splash');
  if (!splash) return;

  // Wait 1.1s for the progress bar animation, then fade out
  setTimeout(() => {
    splash.classList.add('fade-out');
    
    // Clean up splash from DOM after transition completes (800ms)
    setTimeout(() => {
      if (splash.parentNode) {
        splash.parentNode.removeChild(splash);
      }
    }, 800);
  }, 1100);
}

/* ==========================================================================
   1. NAVIGATION & SCROLL TRACKING
   ========================================================================== */
function initNavigation() {
  const sections = document.querySelectorAll('section, main > div');
  const navLinks = document.querySelectorAll('.nav-link');

  // Smooth Scroll
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('href');
      if (targetId === '#') return;
      
      const targetSection = document.querySelector(targetId);
      if (targetSection) {
        targetSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Intersection Observer for Active State
  const observerOptions = {
    root: null,
    rootMargin: '-40% 0px -40% 0px',
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        if (!id) return;
        navLinks.forEach(link => {
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }
    });
  }, observerOptions);

  sections.forEach(section => {
    if (section.getAttribute('id')) {
      observer.observe(section);
    }
  });
}

/* ==========================================================================
   2. Monthly Announcements Slider & Stats Counters (LokalApps Style)
   ========================================================================== */
function initAnnouncementsSlider() {
  const slidesBg = document.querySelectorAll('.announcement-bg-slide');
  const slidesContent = document.querySelectorAll('.announcement-content-slide');
  const slidesBadge = document.querySelectorAll('.announcement-badge-slide');
  const btnPrev = document.getElementById('ann-prev');
  const btnNext = document.getElementById('ann-next');
  
  if (!slidesBg.length || !slidesContent.length || !slidesBadge.length || !btnPrev || !btnNext) return;
  
  let currentIdx = 0;
  const totalSlides = slidesBg.length;
  let intervalId = null;

  function showSlide(index) {
    slidesBg[currentIdx].classList.remove('active');
    slidesContent[currentIdx].classList.remove('active');
    slidesBadge[currentIdx].classList.remove('active');
    
    currentIdx = (index + totalSlides) % totalSlides;
    
    slidesBg[currentIdx].classList.add('active');
    slidesContent[currentIdx].classList.add('active');
    slidesBadge[currentIdx].classList.add('active');
  }

  function nextSlide() {
    showSlide(currentIdx + 1);
  }

  function prevSlide() {
    showSlide(currentIdx - 1);
  }

  btnNext.addEventListener('click', () => {
    nextSlide();
    resetAutoPlay();
  });

  btnPrev.addEventListener('click', () => {
    prevSlide();
    resetAutoPlay();
  });

  function startAutoPlay() {
    intervalId = setInterval(nextSlide, 5000);
  }

  function resetAutoPlay() {
    if (intervalId) {
      clearInterval(intervalId);
      startAutoPlay();
    }
  }

  startAutoPlay();
}

function initStatsCounters() {
  const counters = document.querySelectorAll('.stats_number .number-val');
  if (!counters.length) return;
  
  const observerOptions = {
    root: null,
    threshold: 0.1
  };

  const observer = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = entry.target;
        const countTo = parseInt(target.getAttribute('data-count-to'), 10);
        animateCount(target, countTo);
        observer.unobserve(target);
      }
    });
  }, observerOptions);

  counters.forEach(counter => {
    observer.observe(counter);
  });

  function animateCount(element, countTo) {
    let start = 0;
    const duration = 2000; // 2 seconds
    const startTime = performance.now();

    function update(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Easing function: easeOutExpo
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const currentCount = Math.floor(easeProgress * countTo);
      
      element.textContent = currentCount.toLocaleString();

      if (progress < 1) {
        requestAnimationFrame(update);
      } else {
        element.textContent = countTo.toLocaleString();
      }
    }

    requestAnimationFrame(update);
  }
}

/* ==========================================================================
   3. BNS SPLIT TEXT SCROLL REVEAL ANIMATION
   ========================================================================== */
function initSplitTextScroll() {
  const textElements = document.querySelectorAll('[data-split-scroll]');
  
  textElements.forEach(element => {
    const textContent = element.textContent.trim();
    const words = textContent.split(/\s+/);
    element.innerHTML = '';
    
    words.forEach((word, idx) => {
      const span = document.createElement('span');
      span.classList.add('split-word');
      span.textContent = word;
      span.style.transitionDelay = `${idx * 45}ms`;
      element.appendChild(span);
      element.appendChild(document.createTextNode(' '));
    });
  });

  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -15% 0px',
    threshold: 0.1
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const splitWords = entry.target.querySelectorAll('.split-word');
        splitWords.forEach(word => word.classList.add('active'));
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  textElements.forEach(el => observer.observe(el));
}

/* ==========================================================================
   4. SCROLL-TRIGGERED SECTION THEME SHIFTING (Media Arts Style)
   ========================================================================== */
function initThemeShifting() {
  const portalSection = document.getElementById('portal-comunidad');
  if (!portalSection) return;

  const observerOptions = {
    root: null,
    rootMargin: '-30% 0px -30% 0px', // Trigger when section occupies center 40% of viewport
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        document.body.classList.add('theme-dark');
      } else {
        document.body.classList.remove('theme-dark');
      }
    });
  }, observerOptions);

  observer.observe(portalSection);
}

/* ==========================================================================
   5. CONSTRUCTIVIST RAG CHATBOT SIMULATOR (TUTOR ESCOLAR)
   ========================================================================== */
const RAG_DATABASE = [
  {
    keywords: ['cime', 'matematicas', 'matemática', 'regleta', 'regletas', 'aritmetica', 'multiplicar', 'dividir'],
    answer: 'En el Centro Escolar El Paraíso, las matemáticas se enseñan manipulando y comprendiendo las relaciones físicas de las regletas CIME. El alumno interactúa con bloques de colores tridimensionales para "sentir" las divisiones y multiplicaciones, deduciendo los algoritmos matemáticos por su propio razonamiento lógico antes de pasarlos al papel.',
    source: 'Reglamento de Metodología CIME, Sec. 1.2'
  },
  {
    keywords: ['robotica', 'robótica', 'tecnologia', 'tecnología', 'programacion', 'programación', 'circuito', 'circuitos', 'computacion', 'computación'],
    answer: 'Nuestros talleres de Robótica Aplicada desafían al alumno a resolver problemas prácticos de ingeniería y lógica de código. Al programar robots y ensamblar sensores, el estudiante experimenta con el ensayo y error en tiempo real, convirtiendo la corrección de fallos en un proceso creativo y constructivo.',
    source: 'Reglamento Académico, Art. 18'
  },
  {
    keywords: ['equitacion', 'equitación', 'caballo', 'caballos', 'naturaleza', 'aire libre', 'campo'],
    answer: 'El programa de equitación es una columna clave para el desarrollo socioemocional y la psicomotricidad del alumno. A través del cuidado y la monta de caballos en nuestra pista escolar, el estudiante desarrolla empatía, seguridad corporal, control postural y resiliencia al sintonizar su temperamento con el animal.',
    source: 'Manual de Convivencia, Cap. IV, Art. 12'
  },
  {
    keywords: ['inscripcion', 'inscripciones', 'admision', 'admisiones', 'ingreso', 'costo', 'costos', 'precio', 'precios', 'colegiatura', 'colegiaturas', 'requisitos'],
    answer: 'El proceso de admisión para el ciclo escolar vigente incluye una Sesión de Admisión familiar y una valoración psicopedagógica para comprender el perfil del menor. Para obtener detalles de costos específicos según el nivel escolar, le invitamos a contactar directamente a admisiones@elparaiso.edu.mx.',
    source: 'Reglamento de Admisiones, Cap. II, Art. 4'
  },
  {
    keywords: ['ingles', 'inglés', 'idioma', 'idiomas', 'oxford', 'ote', 'certificacion', 'certificación'],
    answer: 'La formación en inglés está respaldada por la certificación oficial Oxford Test of English (OTE). Nuestra metodología constructivista prioriza el uso adaptativo del idioma en situaciones de comunicación del mundo real, midiendo el progreso de lectura, habla, escucha y escritura.',
    source: 'Reglamento de Idiomas, Art. 9'
  },
  {
    keywords: ['arte', 'artes', 'pintura', 'creatividad', 'plastica', 'plástica', 'expresion', 'expresión', 'taller', 'talleres'],
    answer: 'Los talleres de Artes Visuales se imparten al aire libre para que los alumnos experimenten con luz natural y texturas orgánicas. Los facilitadores guían la técnica sin imponer criterios rígidos de belleza, estimulando al alumno a construir y argumentar sus propios lenguajes visuales.',
    source: 'Plan de Estudios de Artes, Sec. 3.1'
  }
];

function initChatbot() {
  const chatMessagesBox = document.getElementById('chat-messages-box');
  const chatInputField = document.getElementById('chat-input-field');
  const chatSubmitBtn = document.getElementById('chat-submit-btn');

  if (!chatMessagesBox || !chatInputField || !chatSubmitBtn) return;

  chatSubmitBtn.addEventListener('click', handleUserSendMessage);
  chatInputField.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      handleUserSendMessage();
    }
  });

  function handleUserSendMessage() {
    const text = chatInputField.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    chatInputField.value = '';
    scrollToBottom();

    const typingIndicator = showTypingIndicator();

    setTimeout(() => {
      removeTypingIndicator(typingIndicator);
      const response = queryRagDatabase(text);
      appendMessage(response.answer, 'bot', response.source);
      scrollToBottom();
    }, 1000);
  }

  function appendMessage(text, sender, source = null) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender === 'user' ? 'message-user' : 'message-bot');
    
    const p = document.createElement('p');
    p.textContent = text;
    msgDiv.appendChild(p);

    if (source) {
      const span = document.createElement('span');
      span.classList.add('message-source');
      span.textContent = source;
      msgDiv.appendChild(span);
    }

    chatMessagesBox.appendChild(msgDiv);
  }

  function showTypingIndicator() {
    const indicatorDiv = document.createElement('div');
    indicatorDiv.classList.add('message', 'message-bot');
    indicatorDiv.id = 'temp-typing-indicator';

    const typingContainer = document.createElement('div');
    typingContainer.classList.add('typing-indicator');

    for (let i = 0; i < 3; i++) {
      const dot = document.createElement('div');
      dot.classList.add('typing-dot');
      typingContainer.appendChild(dot);
    }

    indicatorDiv.appendChild(typingContainer);
    chatMessagesBox.appendChild(indicatorDiv);
    scrollToBottom();
    return indicatorDiv;
  }

  function removeTypingIndicator(indicator) {
    if (indicator && indicator.parentNode) {
      indicator.parentNode.removeChild(indicator);
    }
  }

  function scrollToBottom() {
    chatMessagesBox.scrollTop = chatMessagesBox.scrollHeight;
  }

  function queryRagDatabase(query) {
    const cleanQuery = query.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    
    for (const doc of RAG_DATABASE) {
      for (const keyword of doc.keywords) {
        if (cleanQuery.includes(keyword)) {
          return {
            answer: doc.answer,
            source: `[${doc.source}]`
          };
        }
      }
    }

    return {
      answer: 'No tengo registro de esa información en los reglamentos y metodologías actuales del colegio. Por favor, ponte en contacto directo con la Coordinación Administrativa al correo admisiones@elparaiso.edu.mx para poder resolver tu duda detalladamente.',
      source: '[Reglamento General, Canales de Contacto]'
    };
  }
}

/* ==========================================================================
   6. LEAD MAGNET FORM VALIDATION & SIGNUP
   ========================================================================== */
function initLeadMagnetForm() {
  const form = document.getElementById('lead-magnet-form');
  const nameInput = document.getElementById('lead-name');
  const emailInput = document.getElementById('lead-email');
  const phoneInput = document.getElementById('lead-phone');
  const submitBtn = document.getElementById('lead-submit-btn');
  const generalFeedback = document.getElementById('form-general-feedback');

  if (!form || !nameInput || !emailInput || !phoneInput || !submitBtn || !generalFeedback) return;

  nameInput.addEventListener('input', () => validateField(nameInput, 'feedback-name', 'El nombre debe tener al menos 3 letras.'));
  emailInput.addEventListener('input', () => validateField(emailInput, 'feedback-email', 'Ingrese un correo electrónico válido.'));
  phoneInput.addEventListener('input', () => validateField(phoneInput, 'feedback-phone', 'El teléfono debe tener 10 números.'));

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const isNameValid = validateField(nameInput, 'feedback-name', 'El nombre debe tener al menos 3 letras.');
    const isEmailValid = validateField(emailInput, 'feedback-email', 'Ingrese un correo electrónico válido.');
    const isPhoneValid = validateField(phoneInput, 'feedback-phone', 'El teléfono debe tener 10 números.');

    if (isNameValid && isEmailValid && isPhoneValid) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Generando Guía Personalizada...';
      generalFeedback.className = 'form-feedback';
      generalFeedback.textContent = '';

      setTimeout(() => {
        submitBtn.textContent = 'Guía Descargada';
        generalFeedback.className = 'form-feedback success';
        generalFeedback.textContent = '✓ ¡Registro exitoso! Su guía "Constructivismo en Casa" se está descargando en PDF.';
        
        triggerPdfDownload();
        form.reset();
        
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Descargar Guía en PDF';
          generalFeedback.style.display = 'none';
        }, 5000);
      }, 1500);
    } else {
      generalFeedback.className = 'form-feedback error';
      generalFeedback.textContent = '⚠ Complete correctamente los campos requeridos en rojo.';
    }
  });

  function validateField(input, feedbackId, errorMessage) {
    const feedbackSpan = document.getElementById(feedbackId);
    let isValid = false;

    if (input.id === 'lead-name') isValid = nameInput.value.trim().length >= 3;
    if (input.id === 'lead-email') isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
    if (input.id === 'lead-phone') isValid = /^\d{10}$/.test(phoneInput.value.replace(/\s+/g, ''));

    if (isValid) {
      input.style.borderColor = 'var(--color-border)';
      if (feedbackSpan) {
        feedbackSpan.style.display = 'none';
        feedbackSpan.textContent = '';
      }
    } else {
      input.style.borderColor = 'var(--color-error)';
      if (feedbackSpan) {
        feedbackSpan.className = 'form-feedback error';
        feedbackSpan.textContent = errorMessage;
      }
    }
    return isValid;
  }

  function triggerPdfDownload() {
    const pdfContent = "Centro Escolar El Paraíso - Guía Práctica: Constructivismo en Casa\n\nInstrucciones de mediación para padres de familia bajo el modelo constructivista.";
    const blob = new Blob([pdfContent], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'Guia_Constructivismo_en_Casa_El_Paraiso.pdf';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
}

/* ==========================================================================
   7. PARENT TESTIMONIALS SLIDER
   ========================================================================== */
function initTestimonialSlider() {
  const slides = document.querySelectorAll('.testimonial-slide');
  if (slides.length <= 1) return;

  let currentIdx = 0;
  
  setInterval(() => {
    slides[currentIdx].classList.remove('active');
    currentIdx = (currentIdx + 1) % slides.length;
    slides[currentIdx].classList.add('active');
  }, 6000);
}

/* ==========================================================================
   8. ROTARY DIAL HERO SECTION CONTROLLER (Maxima Therapy Style)
   ========================================================================== */
const HERO_PROGRAMS = [
  {
    tag: "// 00. FILOSOFÍA CONSTRUCTIVISTA",
    title: "El origen<br>es construir",
    desc: "La filosofía constructivista es el núcleo de nuestro centro escolar. El alumno es el protagonista que interactúa, experimenta y colabora para construir su propio aprendizaje de forma significativa y activa.",
    benefit: "El Alumno como Protagonista Activo",
    color: "#0b5d36",
    hover: "#084427"
  },
  {
    tag: "// 01. MATEMÁTICAS CIME",
    title: "El futuro<br>comienza<br>hoy",
    desc: "",
    benefit: "Razonamiento Lógico Manipulativo",
    color: "#10b981",
    hover: "#059669"
  },
  {
    tag: "// 02. ROBÓTICA APLICADA",
    title: "Crear,<br>codificar y<br>construir",
    desc: "",
    benefit: "Pensamiento Crítico y Computacional",
    color: "#3b82f6",
    hover: "#2563eb"
  },
  {
    tag: "// 03. EQUITACIÓN Y SER",
    title: "Empatía,<br>postura y<br>resiliencia",
    desc: "",
    benefit: "Desarrollo Postural y Socioemocional",
    color: "#d97706",
    hover: "#b45309"
  },
  {
    tag: "// 04. IDIOMA GLOBAL",
    title: "Oxford<br>Test of<br>English",
    desc: "",
    benefit: "Certificación Oficial Oxford OTE",
    color: "#8b5cf6",
    hover: "#7c3aed"
  },
  {
    tag: "// 05. ARTES LIBRES",
    title: "Criterio,<br>estética y<br>expresión",
    desc: "",
    benefit: "Expresión Plástica sin Límites",
    color: "#ef4444",
    hover: "#dc2626"
  }
];

function initRotaryHero() {
  const wheel = document.getElementById('rotary-wheel');
  const container = document.getElementById('rotary-dial-container');
  const nodes = document.querySelectorAll('.rotary-node');
  const prevBtn = document.getElementById('rotary-btn-prev');
  const nextBtn = document.getElementById('rotary-btn-next');
  
  const programCard = document.getElementById('hero-program-card');
  const programTag = document.getElementById('hero-program-tag');
  const displayTitle = document.getElementById('hero-display-title');
  const displayDesc = document.getElementById('hero-display-desc');
  const displayBenefit = document.getElementById('hero-benefit-text');
  const primaryBtn = document.getElementById('hero-cta-primary');
  
  if (!wheel || !container || nodes.length === 0 || !programCard) return;

  let currentAngle = 0;
  let activeIdx = 0;
  let isDragging = false;
  let startTouchAngle = 0;
  let startAngle = 0;
  
  // Update detail card layout
  function updateActiveProgram(idx) {
    activeIdx = idx;
    
    // Highlight active node
    nodes.forEach((node, i) => {
      if (i === idx) {
        node.classList.add('active');
      } else {
        node.classList.remove('active');
      }
    });

    // Toggle active background slide
    const slides = document.querySelectorAll('.hero-bg-slide');
    slides.forEach((slide, i) => {
      if (i === idx) {
        slide.classList.add('active');
      } else {
        slide.classList.remove('active');
      }
    });

    const program = HERO_PROGRAMS[idx];
    if (!program) return;

    // Update background overlay tint color dynamically
    const overlay = document.getElementById('hero-bg-overlay');
    if (overlay) {
      overlay.style.backgroundColor = `rgba(${hexToRgb(program.color)}, 0.18)`;
    }

    // Transition card out, update, transition in
    programCard.style.opacity = '0';
    programCard.style.transform = 'translateY(10px)';
    
    setTimeout(() => {
      // Update texts
      programTag.textContent = program.tag;
      displayTitle.innerHTML = program.title;
      displayDesc.textContent = program.desc;
      displayBenefit.textContent = program.benefit;
      
      // Update accent highlights
      primaryBtn.style.backgroundColor = program.color;
      primaryBtn.style.borderColor = program.color;
      primaryBtn.style.boxShadow = `0 4px 14px rgba(${hexToRgb(program.color)}, 0.25)`;
      
      const benefitBox = document.getElementById('hero-display-benefit');
      if (benefitBox) {
        benefitBox.style.borderColor = `rgba(${hexToRgb(program.color)}, 0.15)`;
      }
      
      const benefitDot = document.querySelector('.benefit-dot');
      if (benefitDot) {
        benefitDot.style.backgroundColor = program.color;
      }

      // Transition card back in
      programCard.style.opacity = '1';
      programCard.style.transform = 'translateY(0)';
    }, 250);

    // Apply rotation CSS variables
    wheel.style.setProperty('--dial-rotation', `${currentAngle}deg`);
    wheel.style.setProperty('--dial-counter-rotation', `${-currentAngle}deg`);
  }

  // Hex to RGB parser for box-shadows
  function hexToRgb(hex) {
    let shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, (m, r, g, b) => r + r + g + g + b + b);
    let result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? `${parseInt(result[1], 16)}, ${parseInt(result[2], 16)}, ${parseInt(result[3], 16)}` : '11, 93, 54';
  }

  // Click on nodes
  nodes.forEach((node, i) => {
    node.addEventListener('click', (e) => {
      e.stopPropagation();
      rotateToNode(i);
    });
  });

  function rotateToNode(targetIdx) {
    const targetAngle = -targetIdx * 60;
    let diff = (targetAngle - currentAngle) % 360;
    
    // Shortest path interpolation
    if (diff > 180) diff -= 360;
    if (diff < -180) diff += 360;
    
    currentAngle += diff;
    updateActiveProgram(targetIdx);
  }

  // Next / Prev buttons
  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      let target = activeIdx - 1;
      if (target < 0) target = 5;
      rotateToNode(target);
    });
  }
  
  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      let target = (activeIdx + 1) % 6;
      rotateToNode(target);
    });
  }

  // Get angle relative to wheel center
  function getPointerAngle(e) {
    const rect = wheel.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const clientX = e.clientX || (e.touches && e.touches[0].clientX);
    const clientY = e.clientY || (e.touches && e.touches[0].clientY);
    
    return Math.atan2(clientY - centerY, clientX - centerX) * (180 / Math.PI);
  }

  // Mouse/Touch Drag Handlers
  function onDragStart(e) {
    // Avoid handling inputs from child button click bubbles
    if (e.target.tagName === 'BUTTON' && !e.target.classList.contains('rotary-wheel')) {
      return; 
    }
    
    isDragging = true;
    startTouchAngle = getPointerAngle(e);
    startAngle = currentAngle;
    
    // Disable CSS transitions during live drag
    wheel.style.transition = 'none';
    nodes.forEach(node => {
      node.style.transition = 'none';
      const wrapper = node.closest('.rotary-node-wrapper');
      if (wrapper) wrapper.style.transition = 'none';
      const nodeContent = node.querySelector('.node-content');
      if (nodeContent) nodeContent.style.transition = 'none';
    });
    
    if (e.type === 'mousedown') {
      window.addEventListener('mousemove', onDragMove);
      window.addEventListener('mouseup', onDragEnd);
    } else {
      window.addEventListener('touchmove', onDragMove, { passive: false });
      window.addEventListener('touchend', onDragEnd);
    }
  }

  function onDragMove(e) {
    if (!isDragging) return;
    
    // Prevent touch scrolling when dragging the wheel
    if (e.type === 'touchmove') e.preventDefault();
    
    const currentTouchAngle = getPointerAngle(e);
    const angleDiff = currentTouchAngle - startTouchAngle;
    const dragAngle = startAngle + angleDiff;
    
    currentAngle = dragAngle;
    wheel.style.setProperty('--dial-rotation', `${dragAngle}deg`);
    wheel.style.setProperty('--dial-counter-rotation', `${-dragAngle}deg`);
  }

  function onDragEnd() {
    if (!isDragging) return;
    isDragging = false;
    
    // Restore clean transitions
    wheel.style.transition = '';
    nodes.forEach(node => {
      node.style.transition = '';
      const wrapper = node.closest('.rotary-node-wrapper');
      if (wrapper) wrapper.style.transition = '';
      const nodeContent = node.querySelector('.node-content');
      if (nodeContent) nodeContent.style.transition = '';
    });
    
    window.removeEventListener('mousemove', onDragMove);
    window.removeEventListener('mouseup', onDragEnd);
    window.removeEventListener('touchmove', onDragMove);
    window.removeEventListener('touchend', onDragEnd);
    
    // Snapping logic: find nearest node (60deg intervals)
    let snappedIdx = Math.round(-currentAngle / 60) % 6;
    if (snappedIdx < 0) snappedIdx += 6;
    
    const snapAngle = -snappedIdx * 60;
    let diff = (snapAngle - currentAngle) % 360;
    
    if (diff > 180) diff -= 360;
    if (diff < -180) diff += 360;
    
    currentAngle += diff;
    updateActiveProgram(snappedIdx);
  }

  wheel.addEventListener('mousedown', onDragStart);
  wheel.addEventListener('touchstart', onDragStart, { passive: true });
  
  // Custom button hover state helpers to dynamically update backgrounds
  if (primaryBtn) {
    primaryBtn.addEventListener('mouseenter', () => {
      primaryBtn.style.backgroundColor = HERO_PROGRAMS[activeIdx].hover;
      primaryBtn.style.borderColor = HERO_PROGRAMS[activeIdx].hover;
    });
    primaryBtn.addEventListener('mouseleave', () => {
      primaryBtn.style.backgroundColor = HERO_PROGRAMS[activeIdx].color;
      primaryBtn.style.borderColor = HERO_PROGRAMS[activeIdx].color;
    });
  }

  // Initialize first active program CIME
  updateActiveProgram(0);
}

/* ==========================================================================
   9. FULLSCREEN NAVIGATION OVERLAY (Korowa Style)
   ========================================================================== */
function initOverlayMenu() {
  const dialog = document.getElementById('nav-menu');
  const triggerBtn = document.getElementById('menu-trigger-btn');
  const closeBtn = document.getElementById('nav-menu-close-btn');
  const accordion = document.getElementById('nav-menu-accordion');
  const detailsElements = accordion ? accordion.querySelectorAll('.nav-menu_link-group-tab_component') : [];
  const menuLinks = dialog ? dialog.querySelectorAll('a') : [];

  if (!dialog || !triggerBtn || !closeBtn) return;

  // Open Dialog
  triggerBtn.addEventListener('click', () => {
    document.body.classList.add('body-no-scroll');
    dialog.showModal();
    // Reset details to the first one open
    detailsElements.forEach((details, idx) => {
      details.open = (idx === 0);
    });
  });

  // Close Dialog
  function closeMenu() {
    dialog.classList.add('closing');
    setTimeout(() => {
      dialog.close();
      dialog.classList.remove('closing');
      document.body.classList.remove('body-no-scroll');
    }, 450);
  }

  closeBtn.addEventListener('click', closeMenu);

  // Close when clicking dialog backdrop
  dialog.addEventListener('click', (e) => {
    if (e.target === dialog) {
      closeMenu();
    }
  });

  // Handle ESC key to also remove body overflow scroll lock
  dialog.addEventListener('cancel', (e) => {
    e.preventDefault();
    closeMenu();
  });

  // Exclusive Accordion hover switching for desktop
  if (window.matchMedia('(min-width: 769px)').matches) {
    detailsElements.forEach(details => {
      const summary = details.querySelector('summary');
      if (summary) {
        summary.addEventListener('mouseenter', () => {
          detailsElements.forEach(d => {
            if (d !== details) d.removeAttribute('open');
          });
          details.setAttribute('open', '');
        });
      }
    });
  }

  // Exclusive Accordion click toggle constraint (for fallback and touch)
  detailsElements.forEach(details => {
    details.addEventListener('toggle', () => {
      if (details.open) {
        detailsElements.forEach(d => {
          if (d !== details) d.removeAttribute('open');
        });
      }
    });
  });

  // Close menu when clicking links & smooth scroll
  menuLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href');
      if (targetId && targetId.startsWith('#')) {
        e.preventDefault();
        
        closeMenu();

        // Smooth scroll to target section after overlay closes
        setTimeout(() => {
          const targetSection = document.querySelector(targetId);
          if (targetSection) {
            targetSection.scrollIntoView({ behavior: 'smooth' });
          }
        }, 500);
      }
    });
  });
}
