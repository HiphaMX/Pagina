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
  const oldForm = document.getElementById('Contacto');
  const formSuccess = document.getElementById('form-success');
  const formError = document.getElementById('form-error');

  if (oldForm) {
    // Clonar el formulario para limpiar cualquier event listener residual de Webflow/jQuery
    const contactoForm = oldForm.cloneNode(true);
    oldForm.parentNode.replaceChild(contactoForm, oldForm);

    contactoForm.addEventListener('submit', function (e) {
      e.preventDefault();
      e.stopPropagation();

      // Ocultar estados previos
      if (formSuccess) {
        formSuccess.classList.add('hidden');
        formSuccess.style.display = 'none';
      }
      if (formError) {
        formError.classList.add('hidden');
        formError.style.display = 'none';
      }

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

      // ─── VALIDACIÓN INTEGRAL Y DETALLADA ───
      let errorMsg = '';
      
      // Sanitizar teléfono (quitar espacios, guiones, etc. para validar longitud de 10 dígitos)
      const cleanPhone = telefonoVal.replace(/\D/g, '');
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

      if (!nombreVal) {
        errorMsg = 'Por favor, ingresa tu nombre.';
      } else if (!apellidoVal) {
        errorMsg = 'Por favor, ingresa tu apellido.';
      } else if (!emailVal || !emailRegex.test(emailVal)) {
        errorMsg = 'Por favor, ingresa un correo electrónico válido.';
      } else if (!telefonoVal) {
        errorMsg = 'Por favor, ingresa tu teléfono de contacto.';
      } else if (cleanPhone.length !== 10) {
        errorMsg = 'El teléfono de contacto debe tener exactamente 10 dígitos numéricos.';
      } else if (!servicioVal) {
        errorMsg = 'Por favor, selecciona un servicio requerido.';
      } else if (!ubicacionVal || ubicacionVal === 'Selecciona tu ubicación') {
        errorMsg = 'Por favor, selecciona un municipio/ubicación válida.';
      }

      if (errorMsg) {
        if (formError) {
          const errorTextDiv = formError.querySelector('.div-block-17') || formError;
          errorTextDiv.textContent = errorMsg;
          formError.classList.remove('hidden');
          formError.style.display = 'block';
          formError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        return;
      }

      // ─── ESTADO DE CARGA EN EL BOTÓN ───
      const submitBtn = contactoForm.querySelector('input[type="submit"]');
      const originalBtnVal = submitBtn ? submitBtn.value : 'Cotizar';
      if (submitBtn) {
        submitBtn.value = submitBtn.getAttribute('data-wait') || 'Enviando...';
        submitBtn.disabled = true;
      }

      // Enviar datos al backend para disparar los correos
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
        if (submitBtn) {
          submitBtn.value = originalBtnVal;
          submitBtn.disabled = false;
        }

        if (res.ok) {
          // Mostrar banner de éxito
          if (formSuccess) {
            formSuccess.classList.remove('hidden');
            formSuccess.style.display = 'block';
            formSuccess.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
          }
          // Reiniciar formulario
          contactoForm.reset();
        } else {
          throw new Error('Server error');
        }
      })
      .catch(err => {
        console.error('Error al enviar contacto:', err);
        if (submitBtn) {
          submitBtn.value = originalBtnVal;
          submitBtn.disabled = false;
        }
        if (formError) {
          const errorTextDiv = formError.querySelector('.div-block-17') || formError;
          errorTextDiv.textContent = 'Hubo un inconveniente al enviar tu solicitud de cotización por correo. Por favor, intenta de nuevo.';
          formError.classList.remove('hidden');
          formError.style.display = 'block';
          formError.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      });
    });
  }

});
