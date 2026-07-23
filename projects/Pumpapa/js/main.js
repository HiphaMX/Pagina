document.addEventListener('DOMContentLoaded', () => {
  // --- Lateral Navigation & Scroll Snapping Sychronization ---
  const sections = document.querySelectorAll('section.snap-section');
  const navDots = document.querySelectorAll('.dot-nav-item');
  
  // Smooth scroll to sections when dots are clicked
  navDots.forEach(dot => {
    dot.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = dot.getAttribute('href');
      const targetSection = document.querySelector(targetId);
      if (targetSection) {
        targetSection.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Track scrolling to activate the correct dot
  const observerOptions = {
    root: null,
    rootMargin: '-30% 0px -30% 0px', // Trigger when section occupies most of screen center
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navDots.forEach(dot => {
          if (dot.getAttribute('href') === `#${id}`) {
            dot.classList.add('active');
          } else {
            dot.classList.remove('active');
          }
        });
      }
    });
  }, observerOptions);

  sections.forEach(section => observer.observe(section));

  // --- Magic Sparkle Particles ---
  const handleSparkle = (e) => {
    if (Math.random() > 0.15) return;

    const sparkleContainer = document.body;
    const star = document.createElement('div');
    star.className = 'sparkle-star';
    star.innerHTML = '✦';

    const x = e.clientX || (e.touches && e.touches[0].clientX);
    const y = e.clientY + window.scrollY || (e.touches && e.touches[0].clientY + window.scrollY);

    if (!x || !y) return;

    star.style.left = `${x}px`;
    star.style.top = `${y}px`;

    const dx = (Math.random() - 0.5) * 120;
    const dy = (Math.random() - 0.5) * 120 - 50; 
    const rot = Math.random() * 360;

    star.style.setProperty('--dx', `${dx}px`);
    star.style.setProperty('--dy', `${dy}px`);
    star.style.setProperty('--rot', `${rot}deg`);

    const colors = ['#FF6666', '#FFCC33', '#CC99CC', '#66CCCC', '#99CC33'];
    star.style.color = colors[Math.floor(Math.random() * colors.length)];

    sparkleContainer.appendChild(star);

    setTimeout(() => star.remove(), 1200);
  };

  window.addEventListener('mousemove', handleSparkle);
  window.addEventListener('touchmove', handleSparkle);

  // --- Interactive Frame Simulator & Size Controls ---
  const frameSimulator = document.querySelector('.frame-simulator');
  const sizeButtons = document.querySelectorAll('.size-btn');
  const frameHint = document.getElementById('frame-hint-text');

  // Open/Close frame acrylic swing
  if (frameSimulator) {
    frameSimulator.addEventListener('click', () => {
      frameSimulator.classList.toggle('opened');
      if (frameHint) {
        if (frameSimulator.classList.contains('opened')) {
          frameHint.innerHTML = '✨ ¡Haz clic de nuevo para cerrar el acrílico!';
        } else {
          frameHint.innerHTML = '✨ Haz clic en el marco para abrir el acrílico';
        }
      }
    });
  }

  // Size buttons trigger layout dimensions change
  sizeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      sizeButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      
      const targetSize = btn.dataset.size; // 'chico', 'mediano', 'grande'
      
      if (frameSimulator) {
        frameSimulator.className = 'frame-simulator'; // reset
        frameSimulator.classList.add(`size-${targetSize}`);
      }
    });
  });

  // --- Real-time Price Calculator (Cotizador) ---
  const checkCuento = document.getElementById('calc-cuento');
  const extraDidactico = document.getElementById('calc-extra-didactico');
  
  const checkFotos = document.getElementById('calc-fotos');
  const extraAlbum = document.getElementById('calc-extra-album');
  
  const checkMarco = document.getElementById('calc-marco');
  const selectMarcoSize = document.getElementById('calc-marco-size');
  const extraCuracion = document.getElementById('calc-extra-curacion');
  
  const totalValueEl = document.getElementById('calc-total-val');
  const buyBtn = document.getElementById('calc-buy-btn');

  // Prices constants
  const PRICES = {
    cuentoBase: 6500,
    cuentoExtra: 450,
    fotosBase: 1800,
    fotosExtra: 850,
    marcoSizes: {
      chico: 650,
      mediano: 950,
      grande: 1350
    },
    marcoCuracion: 300
  };

  const calculateTotal = () => {
    let total = 0;
    let detailsList = [];

    // Cuento Pillar
    if (checkCuento && checkCuento.checked) {
      total += PRICES.cuentoBase;
      detailsList.push('Cuento Ilustrado (25 pz)');
      if (extraDidactico && extraDidactico.checked) {
        total += PRICES.cuentoExtra;
        detailsList.push('Didáctico Digital');
      }
      if (extraDidactico) extraDidactico.disabled = false;
    } else {
      if (extraDidactico) extraDidactico.disabled = true;
    }

    // Fotos Pillar
    if (checkFotos && checkFotos.checked) {
      total += PRICES.fotosBase;
      detailsList.push('Sesión Fotográfica Familiar');
      if (extraAlbum && extraAlbum.checked) {
        total += PRICES.fotosExtra;
        detailsList.push('Álbum Impreso Extra');
      }
      if (extraAlbum) extraAlbum.disabled = false;
    } else {
      if (extraAlbum) extraAlbum.disabled = true;
    }

    // Marco Pillar
    if (checkMarco && checkMarco.checked) {
      const selectedSize = selectMarcoSize ? selectMarcoSize.value : 'mediano';
      const sizePrice = PRICES.marcoSizes[selectedSize] || 950;
      total += sizePrice;
      detailsList.push(`Marco de Memorias (${selectedSize.toUpperCase()})`);
      
      if (extraCuracion && extraCuracion.checked) {
        total += PRICES.marcoCuracion;
        detailsList.push('Curación / Maquetación');
      }
      if (selectMarcoSize) selectMarcoSize.disabled = false;
      if (extraCuracion) extraCuracion.disabled = false;
    } else {
      if (selectMarcoSize) selectMarcoSize.disabled = true;
      if (extraCuracion) extraCuracion.disabled = true;
    }

    // Update View
    if (totalValueEl) {
      totalValueEl.textContent = `$${total.toLocaleString('es-MX')} MXN`;
    }

    // Enable/Disable checkout button
    if (buyBtn) {
      if (total > 0) {
        buyBtn.disabled = false;
        buyBtn.style.opacity = '1';
        buyBtn.style.cursor = 'pointer';
      } else {
        buyBtn.disabled = true;
        buyBtn.style.opacity = '0.5';
        buyBtn.style.cursor = 'not-allowed';
      }
    }

    return { total, detailsList };
  };

  // Attach event listeners to all calculator inputs
  const calcInputs = [
    checkCuento, extraDidactico, 
    checkFotos, extraAlbum, 
    checkMarco, selectMarcoSize, extraCuracion
  ];

  calcInputs.forEach(input => {
    if (input) {
      input.addEventListener('change', calculateTotal);
    }
  });

  // Run initial calculation
  calculateTotal();

  // --- Simulated Secure Checkout ---
  const checkoutModal = document.getElementById('checkout-modal');
  const checkoutClose = document.getElementById('checkout-close');
  const summaryProductName = document.getElementById('summary-product-name');
  const summaryProductPrice = document.getElementById('summary-product-price');
  const summaryTotalVal = document.getElementById('summary-total-val');
  const paymentForm = document.getElementById('payment-form-sim');
  const successView = document.getElementById('payment-success-view');

  const openCheckout = () => {
    const { total, detailsList } = calculateTotal();
    if (total === 0) return;

    summaryProductName.textContent = detailsList.join(' + ');
    summaryProductPrice.textContent = `$${total.toLocaleString('es-MX')} MXN`;
    summaryTotalVal.textContent = `$${total.toLocaleString('es-MX')} MXN`;

    // Reset view
    if (paymentForm) paymentForm.style.display = 'flex';
    if (successView) successView.style.display = 'none';
    if (paymentForm) paymentForm.reset();

    checkoutModal.classList.add('active');
  };

  const closeCheckout = () => {
    checkoutModal.classList.remove('active');
  };

  if (buyBtn) {
    buyBtn.addEventListener('click', openCheckout);
  }

  if (checkoutClose) {
    checkoutClose.addEventListener('click', closeCheckout);
  }

  if (checkoutModal) {
    checkoutModal.addEventListener('click', (e) => {
      if (e.target === checkoutModal) {
        closeCheckout();
      }
    });
  }

  // Credit Card Formatter
  const cardNum = document.getElementById('card-number');
  if (cardNum) {
    cardNum.addEventListener('input', (e) => {
      let val = e.target.value.replace(/\D/g, '');
      val = val.match(/.{1,4}/g)?.join(' ') || val;
      e.target.value = val.substring(0, 19);
    });
  }

  const cardExpiry = document.getElementById('card-expiry');
  if (cardExpiry) {
    cardExpiry.addEventListener('input', (e) => {
      let val = e.target.value.replace(/\D/g, '');
      if (val.length > 2) {
        val = val.substring(0, 2) + '/' + val.substring(2, 4);
      }
      e.target.value = val.substring(0, 5);
    });
  }

  const cardCvv = document.getElementById('card-cvv');
  if (cardCvv) {
    cardCvv.addEventListener('input', (e) => {
      e.target.value = e.target.value.replace(/\D/g, '').substring(0, 4);
    });
  }

  // Payment Submit
  if (paymentForm) {
    paymentForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const submitBtn = paymentForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = '✨ Procesando pago seguro...';

      setTimeout(() => {
        paymentForm.style.display = 'none';
        successView.style.display = 'block';
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
        
        triggerCelebrationSparkle();
      }, 2000);
    });
  }

  const triggerCelebrationSparkle = () => {
    const rect = successView.getBoundingClientRect();
    for (let i = 0; i < 30; i++) {
      setTimeout(() => {
        const star = document.createElement('div');
        star.className = 'sparkle-star';
        star.innerHTML = '✦';
        
        const x = rect.left + rect.width / 2 + (Math.random() - 0.5) * 150;
        const y = rect.top + rect.height / 2 + (Math.random() - 0.5) * 150 + window.scrollY;
        
        star.style.left = `${x}px`;
        star.style.top = `${y}px`;
        
        const dx = (Math.random() - 0.5) * 250;
        const dy = (Math.random() - 0.5) * 250;
        const rot = Math.random() * 360;
        
        star.style.setProperty('--dx', `${dx}px`);
        star.style.setProperty('--dy', `${dy}px`);
        star.style.setProperty('--rot', `${rot}deg`);
        
        const colors = ['#FF6666', '#FFCC33', '#CC99CC', '#66CCCC', '#99CC33'];
        star.style.color = colors[Math.floor(Math.random() * colors.length)];
        
        document.body.appendChild(star);
        setTimeout(() => star.remove(), 1200);
      }, i * 30);
    }
  };
});
