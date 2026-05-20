// ─── LÓGICA DE INTERACTIVIDAD DE WHITE CLEAN (VIBRANTE & ULTRA-FLUIDA) ───

document.addEventListener('DOMContentLoaded', () => {
  
  // ─── 1. PRELOADER INICIAL ───
  const preloader = document.getElementById('preloader');
  if (preloader) {
    window.addEventListener('load', () => {
      // Retrasar una fracción de segundo para asegurar fluidez visual
      setTimeout(() => {
        preloader.classList.add('fade-out');
      }, 400);
    });
    
    // Fallback de seguridad si tarda en disparar load
    setTimeout(() => {
      if (!preloader.classList.contains('fade-out')) {
        preloader.classList.add('fade-out');
      }
    }, 2000);
  }

  // ─── 2. MENÚ MÓVIL DESPLEGABLE ───
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');
  
  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      mobileMenu.classList.toggle('hidden');
    });
    
    // Cerrar menú al hacer clic en un enlace de navegación móvil
    const mobileLinks = mobileMenu.querySelectorAll('a');
    mobileLinks.forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
      });
    });

    // Cerrar menú móvil al hacer click fuera
    document.addEventListener('click', (e) => {
      if (!mobileMenu.classList.contains('hidden') && !mobileMenu.contains(e.target) && e.target !== mobileMenuBtn) {
        mobileMenu.classList.add('hidden');
      }
    });
  }

  // ─── 3. TESTIMONIALS SLIDER AUTOMÁTICO & MANUAL ───
  const slides = document.querySelectorAll('.review-slide');
  const dots = document.querySelectorAll('.review-dot');
  let currentReviewIdx = 0;
  let reviewTimer = null;

  function showReview(index) {
    if (slides.length === 0) return;
    
    // Validar rango del índice
    if (index >= slides.length) currentReviewIdx = 0;
    else if (index < 0) currentReviewIdx = slides.length - 1;
    else currentReviewIdx = index;

    // Actualizar slides añadiendo/removiendo clases de control
    slides.forEach((slide, i) => {
      if (i === currentReviewIdx) {
        slide.classList.add('active');
        // Pequeño hack de transición opacidad
        setTimeout(() => {
          slide.classList.remove('opacity-0');
          slide.classList.add('opacity-100');
        }, 10);
      } else {
        slide.classList.remove('active');
        slide.classList.add('opacity-0');
        slide.classList.remove('opacity-100');
      }
    });

    // Actualizar dots
    dots.forEach((dot, i) => {
      if (i === currentReviewIdx) {
        dot.classList.add('review-dot-active');
      } else {
        dot.classList.remove('review-dot-active');
      }
    });
  }

  function startReviewTimer() {
    stopReviewTimer();
    reviewTimer = setInterval(() => {
      showReview(currentReviewIdx + 1);
    }, 6000); // 6 segundos por slide
  }

  function stopReviewTimer() {
    if (reviewTimer) {
      clearInterval(reviewTimer);
    }
  }

  // Exponer globalmente la navegación por dots para los clicks inline del HTML
  window.showReview = (index) => {
    showReview(index);
    // Reiniciar cronómetro en interacción manual
    startReviewTimer();
  };

  // Inicializar slider de testimonios
  if (slides.length > 0) {
    showReview(0);
    startReviewTimer();
  }

  // ─── 4. COTIZADOR E INTEGRACIÓN CON WHATSAPP ───
  const contactoForm = document.getElementById('Contacto');
  const formSuccess = document.getElementById('form-success');
  const formError = document.getElementById('form-error');

  if (contactoForm) {
    contactoForm.addEventListener('submit', function (e) {
      e.preventDefault();

      // Ocultar estados previos
      if (formSuccess) formSuccess.classList.add('hidden');
      if (formError) formError.classList.add('hidden');

      // Obtener y limpiar valores de campos
      const nombreVal = document.getElementById('Nombre')?.value.trim() || '';
      const apellidoVal = document.getElementById('Apellido')?.value.trim() || '';
      const emailVal = document.getElementById('Email')?.value.trim() || '';
      const telefonoVal = document.getElementById('Telefono')?.value.trim() || '';
      
      // select de servicio
      const servicioSelect = document.getElementById('Servicio-requerido');
      const servicioVal = servicioSelect ? servicioSelect.options[servicioSelect.selectedIndex].value : '';
      
      // select de municipio
      const ubicacionSelect = document.getElementById('Ubicacion');
      const ubicacionVal = ubicacionSelect ? ubicacionSelect.options[ubicacionSelect.selectedIndex].value : '';
      
      const mensajeVal = document.getElementById('Mensaje')?.value.trim() || '';

      // Validación simple adicional
      if (!nombreVal || !apellidoVal || !emailVal || !telefonoVal || !servicioVal || !ubicacionVal) {
        if (formError) formError.classList.remove('hidden');
        return;
      }

      // Enviar datos al backend en segundo plano (para disparar correos de confirmación y aviso sin bloquear)
      fetch('/api/contact/whiteclean', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          nombre: nombreVal,
          apellido: apellidoVal,
          email: emailVal,
          telefono: telefonoVal,
          servicio: servicioVal,
          ubicacion: ubicacionVal,
          mensaje: mensajeVal
        })
      })
      .then(res => {
        if (!res.ok) console.error('Error enviando contacto al servidor.');
      })
      .catch(err => console.error('Error de red al enviar contacto:', err));

      // Número de WhatsApp del cliente
      const whatsappPhone = '523312998450';

      // Construcción del mensaje pre-llenado limpio y profesional
      const rawMessage = `¡Hola! Solicito cotización desde la web.

*Datos de contacto:*
• Nombre: ${nombreVal} ${apellidoVal}
• Correo: ${emailVal}
• Teléfono: ${telefonoVal}
• Ubicación: ${ubicacionVal}

*Detalles del servicio:*
• Servicio requerido: ${servicioVal}
${mensajeVal ? `• Mensaje adicional: ${mensajeVal}` : ''}`;

      // Codificar mensaje para la URL
      const encodedText = encodeURIComponent(rawMessage);
      const whatsappUrl = `https://api.whatsapp.com/send?phone=${whatsappPhone}&text=${encodedText}`;

      // Abrir WhatsApp en pestaña nueva
      window.open(whatsappUrl, '_blank');

      // Mostrar banner de éxito
      if (formSuccess) {
        formSuccess.classList.remove('hidden');
        formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }

      // Reiniciar formulario
      contactoForm.reset();
    });
  }

});
