// 🌶️ Chile Chillón — Lógica de UI & Interactividad "Ultrapro"

// --- Dataset de la Trilogía ---
const salsasData = {
  jalapeno: {
    name: "Chile Chillón Jalapeño",
    subtitle: "El Picor Alegre y Fresco",
    scoville: "3,500 SHU",
    fillHeight: "30%",
    color: "#D30611",
    accentClass: "text-[#D30611]",
    glowColor: "rgba(211, 6, 17, 0.4)",
    radialGlow: "radial-gradient(circle, #D30611 0%, rgba(211, 6, 17, 0) 70%)",
    description: "Un picor alegre y herbal, ideal para potenciar el sabor de tus snacks, botanas y comidas cotidianas de forma fácil y sin complicaciones. Combina la frescura del cilantro con el calor del jalapeño artesanal.",
    ingredients: "Jalapeños premium seleccionados, cilantro criollo fresco, ajo de rancho asado, sal de grano y un toque de limón.",
    chillido: "Nivel Alegre 🌶️",
    badgeColor: "bg-[#D30611]/10 text-[#D30611] border-[#D30611]/20",
    image: "https://images.unsplash.com/photo-1591871937573-74dbba515c4c?q=80&w=600&auto=format&fit=crop"
  },
  habanero: {
    name: "Chile Chillón Habanero",
    subtitle: "El Balance Tropical Perfecto",
    scoville: "150,000 SHU",
    fillHeight: "65%",
    color: "#FF5A00",
    accentClass: "text-[#FF5A00]",
    glowColor: "rgba(255, 90, 0, 0.4)",
    radialGlow: "radial-gradient(circle, #FF5A00 0%, rgba(255, 90, 0, 0) 70%)",
    description: "Nuestra obra maestra del equilibrio tropical. El habanero naranja ahumado aporta un picor de intensidad media-alta junto a un aroma robusto que amplifica instantáneamente carnes, mariscos y salsas caseras.",
    ingredients: "Habanero naranja tatemado, cebolla morada asada, especias secretas de la casa y jugo de naranja agria.",
    chillido: "Nivel Intenso 🌶️🌶️",
    badgeColor: "bg-[#FF5A00]/10 text-[#FF5A00] border-[#FF5A00]/20",
    image: "https://images.unsplash.com/photo-1608797178974-15b35a61d121?q=80&w=600&auto=format&fit=crop"
  },
  fuego: {
    name: "Chile Chillón Fuego Extremo",
    subtitle: "El Despertar del Fuego",
    scoville: "350,000 SHU",
    fillHeight: "100%",
    color: "#D30611",
    accentClass: "text-[#D30611]",
    glowColor: "rgba(211, 6, 17, 0.4)",
    radialGlow: "radial-gradient(circle, #D30611 0%, rgba(211, 6, 17, 0) 70%)",
    description: "Para los verdaderos audaces y alquimistas de la cocina. Un picor brutal, persistente y atrevido que desafía los sentidos pero conserva el sazón original del ingrediente, llevándolo a su máxima potencia.",
    ingredients: "Habanero rojo selecto maduro, chile de árbol seco, mezcla meticulosa de chiles endémicos secos.",
    chillido: "Nivel Extremo 🌶️🌶️🌶️",
    badgeColor: "bg-[#D30611]/10 text-[#D30611] border-[#D30611]/20",
    image: "https://images.unsplash.com/photo-1588252303782-cb80119cb665?q=80&w=600&auto=format&fit=crop"
  }
};

document.addEventListener("DOMContentLoaded", () => {
  // 1. Manejo del Preloader Inteligente
  initPreloader();

  // 2. Custom Cursor Magnético
  initCustomCursor();

  // 3. Inicializar Termómetro Scoville
  initThermometer();

  // 4. Manifiesto Scroll Reveal
  initScrollReveal();

  // 5. Envío de Formulario con FastAPI
  initContactForm();

  // 6. Amplificador de Antojos (Platillos Compatibles)
  initDishSelector();

  // 7. Recetario - Guardar Favoritos
  initRecipeFavorites();

  // 8. Inicializar Tienda y Carrito de Compras
  initCart();

  // 9. Inicializar Opiniones de Google y Aleatorización
  initTestimonios();

  // 10. Menú Hamburguesa Móvil
  initMobileMenu();
});

// --- Preloader ---
function initPreloader() {
  const preloader = document.getElementById("preloader");
  if (!preloader) return;

  const bar = document.getElementById("preloader-bar");
  const percentText = document.getElementById("preloader-percentage");
  const msgText = document.getElementById("preloader-message");
  const preloaderChile = document.getElementById("preloader-chile");

  // Loop de animación para las lágrimas del chile chillón (en sentido inverso para que las lágrimas fluyan hacia afuera)
  let frame = 6;
  const frameInterval = setInterval(() => {
    frame = frame - 1;
    if (frame < 1) frame = 6;
    if (preloaderChile) {
      preloaderChile.src = `Assets/Chillando/enchilado${frame}.svg`;
    }
  }, 120);

  let progress = 0;
  const duration = 3500; // 3.5 seconds loading time
  const intervalTime = 20; // 20ms steps
  const totalSteps = duration / intervalTime;
  const stepIncrement = 100 / totalSteps;

  const timer = setInterval(() => {
    progress += stepIncrement;
    if (progress >= 100) {
      progress = 100;
      clearInterval(timer);
      clearInterval(frameInterval); // Limpiar bucle de animación
      
      if (bar) bar.style.width = "100%";
      if (percentText) percentText.textContent = "100%";
      if (msgText) msgText.textContent = "¡Listo para chillar! 🌶️";

      setTimeout(() => {
        preloader.classList.add("fade-out");
        setTimeout(() => preloader.remove(), 700);
      }, 450);
    } else {
      const displayVal = Math.floor(progress);
      if (bar) bar.style.width = displayVal + "%";
      if (percentText) percentText.textContent = displayVal + "%";
      
      if (msgText) {
        if (displayVal < 25) {
          msgText.textContent = "Encendiendo el fuego... 🔥";
        } else if (displayVal < 55) {
          msgText.textContent = "Moliendo chiles frescos... 🌶️";
        } else if (displayVal < 85) {
          msgText.textContent = "Ajustando el picor... 🧪";
        } else {
          msgText.textContent = "Embotellando locura... 🍯";
        }
      }
    }
  }, intervalTime);
}

// --- Menú Hamburguesa Móvil ---
function initMobileMenu() {
  const drawer = document.getElementById("mobile-menu-drawer");
  const openBtn = document.getElementById("mobile-menu-toggle");
  const closeBtn = document.getElementById("mobile-menu-close");
  const links = document.querySelectorAll(".mobile-nav-link");

  if (openBtn && drawer) {
    openBtn.addEventListener("click", () => {
      drawer.classList.remove("translate-x-full");
    });
  }

  if (closeBtn && drawer) {
    closeBtn.addEventListener("click", () => {
      drawer.classList.add("translate-x-full");
    });
  }

  links.forEach(link => {
    link.addEventListener("click", () => {
      if (drawer) drawer.classList.add("translate-x-full");
    });
  });
}

// --- Custom Cursor ---
function initCustomCursor() {
  // Solo en dispositivos no móviles / desktop
  if (window.innerWidth < 1024) return;

  const cursor = document.createElement("div");
  cursor.className = "custom-cursor";
  const glow = document.createElement("div");
  glow.className = "custom-cursor-glow";

  document.body.appendChild(cursor);
  document.body.appendChild(glow);
  document.body.classList.add("has-custom-cursor");

  let mouseX = 0, mouseY = 0;
  let cursorX = 0, cursorY = 0;
  let glowX = 0, glowY = 0;

  // Estado para la física de las hojuelas de chile
  const activeParticles = [];
  let lastMouseX = 0, lastMouseY = 0;
  let lastSpawnTime = 0;

  document.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;

    const now = Date.now();
    if (now - lastSpawnTime > 35) { // Limitar tasa de refresco para rendimiento a 60fps
      const dx = mouseX - lastMouseX;
      const dy = mouseY - lastMouseY;
      const speed = Math.sqrt(dx * dx + dy * dy);

      if (speed > 2) { // Solo esparcir hojuelas si el cursor se está moviendo
        spawnChiliParticle(mouseX, mouseY, dx * 0.18, dy * 0.18);
        lastSpawnTime = now;
      }
      lastMouseX = mouseX;
      lastMouseY = mouseY;
    }
  });

  // Generador dinámico de partículas con colores y formas orgánicas
  function spawnChiliParticle(x, y, baseVx, baseVy) {
    const el = document.createElement("div");
    
    // Distribución: 55% chile rojo, 25% chile naranja/habanero, 10% chile tatemado, 10% semilla dorada
    const r = Math.random();
    let bgColor = "#D30611"; // Rojo flama
    let width = Math.random() * 5 + 4; // 4px a 9px
    let height = Math.random() * 6 + 5; // 5px a 11px
    let borderRadius = `${Math.random()*4+2}px ${Math.random()*4+2}px ${Math.random()*4+2}px ${Math.random()*4+2}px`;
    
    if (r < 0.55) {
      bgColor = "#D30611"; // Rojo
    } else if (r < 0.8) {
      bgColor = "#FF5A00"; // Naranja Habanero
    } else if (r < 0.9) {
      bgColor = "#7A0207"; // Tatemado (Café rojizo oscuro)
    } else {
      bgColor = "#FFD000"; // Semilla de chile dorada
      width = 4;
      height = 5.5;
      borderRadius = "50%"; // Semillas redondas
    }

    // Estilos optimizados para renderizado acelerado por GPU
    el.style.position = "fixed";
    el.style.left = "0";
    el.style.top = "0";
    el.style.width = `${width}px`;
    el.style.height = `${height}px`;
    el.style.backgroundColor = bgColor;
    el.style.borderRadius = borderRadius;
    el.style.pointerEvents = "none";
    el.style.zIndex = "999996";
    el.style.transform = `translate3d(${x}px, ${y}px, 0)`;
    el.style.opacity = "1";
    el.style.boxShadow = "0 1px 3px rgba(0,0,0,0.15)";
    
    document.body.appendChild(el);

    activeParticles.push({
      el: el,
      x: x - width / 2,
      y: y - height / 2,
      vx: baseVx + (Math.random() - 0.5) * 2.5, // Velocidad inicial + inercia del cursor
      vy: baseVy - Math.random() * 1.5 - 0.5, // Flotación inicial hacia arriba
      gravity: 0.12, // Gravedad suave para jalar las hojuelas abajo
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 12,
      scale: Math.random() * 0.4 + 0.8, // Escala orgánica variada
      alpha: 1.0,
      alphaDecay: Math.random() * 0.015 + 0.012 // Desvanecimiento progresivo
    });
  }

  // Loop de renderizado suave (60fps)
  function animateCursor() {
    // Retraso para el cursor principal
    cursorX += (mouseX - cursorX) * 0.2;
    cursorY += (mouseY - cursorY) * 0.2;
    cursor.style.left = `${cursorX}px`;
    cursor.style.top = `${cursorY}px`;

    // Retraso mayor para el glow magnético
    glowX += (mouseX - glowX) * 0.12;
    glowY += (mouseY - glowY) * 0.12;
    glow.style.left = `${glowX}px`;
    glow.style.top = `${glowY}px`;

    // Actualizar y renderizar físicas de partículas
    for (let i = activeParticles.length - 1; i >= 0; i--) {
      const p = activeParticles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += p.gravity;
      p.rotation += p.rotationSpeed;
      p.alpha -= p.alphaDecay;

      if (p.alpha <= 0) {
        p.el.remove();
        activeParticles.splice(i, 1);
      } else {
        // Uso de translate3d para forzar renderizado por GPU (silky smooth)
        p.el.style.transform = `translate3d(${p.x}px, ${p.y}px, 0) rotate(${p.rotation}deg) scale(${p.scale})`;
        p.el.style.opacity = p.alpha;
      }
    }

    requestAnimationFrame(animateCursor);
  }
  animateCursor();

  // Hover en elementos interactivos
  const interactives = document.querySelectorAll("a, button, select, input, textarea, [role='button'], .interactive-card");
  interactives.forEach(item => {
    item.addEventListener("mouseenter", () => {
      document.body.classList.add("cursor-hover");
    });
    item.addEventListener("mouseleave", () => {
      document.body.classList.add("cursor-hover-out");
      document.body.classList.remove("cursor-hover");
      setTimeout(() => document.body.classList.remove("cursor-hover-out"), 300);
    });
  });
}

// --- Termómetro Scoville ---
function initThermometer() {
  const fill = document.getElementById("scoville-fill");
  const scovilleNumber = document.getElementById("scoville-number");
  const prodName = document.getElementById("product-name");
  const prodSub = document.getElementById("product-subtitle");
  const prodDesc = document.getElementById("product-desc");
  const prodIng = document.getElementById("product-ingredients");
  const prodChill = document.getElementById("product-chillido");
  const prodImg = document.getElementById("product-image");
  const dynamicBlob = document.getElementById("blob-dynamic");
  const selectors = document.querySelectorAll(".chile-selector");

  if (!fill) return;

  // Cambiar salsa activa
  function setActiveSalsa(key) {
    const data = salsasData[key];
    if (!data) return;

    // Actualizar Termómetro
    fill.style.height = data.fillHeight;
    fill.style.background = `linear-gradient(to top, ${data.color}, #ffffff)`;

    // Cambiar texto de Scoville con glow
    scovilleNumber.innerText = data.scoville;
    scovilleNumber.style.color = data.color;
    scovilleNumber.style.textShadow = `0 0 20px ${data.glowColor}`;

    // Actualizar Blob del fondo
    if (dynamicBlob) {
      dynamicBlob.style.background = data.radialGlow;
      dynamicBlob.style.opacity = "0.2";
    }

    // Animación de salida del panel informativo
    const infoPanel = document.getElementById("product-info-panel");
    if (infoPanel) {
      infoPanel.style.opacity = "0";
      infoPanel.style.transform = "translateY(15px)";
      
      if (prodImg) {
        prodImg.style.opacity = "0";
        prodImg.style.transform = "scale(0.95)";
      }

      setTimeout(() => {
        // Cargar nuevos datos
        prodName.innerText = data.name;
        prodSub.innerText = data.subtitle;
        prodDesc.innerText = data.description;
        prodIng.innerText = data.ingredients;
        
        // Cargar Badge
        prodChill.innerText = data.chillido;
        prodChill.className = `px-3 py-1 border rounded-full text-xs font-semibold tracking-wider uppercase inline-block transition-colors duration-500 ${data.badgeColor}`;

        // Cargar Imagen si existe
        if (prodImg) {
          prodImg.src = data.image;
          prodImg.alt = data.name;
          prodImg.style.opacity = "1";
          prodImg.style.transform = "scale(1)";
        }

        infoPanel.style.opacity = "1";
        infoPanel.style.transform = "translateY(0)";
      }, 400);
    }
  }

  selectors.forEach(btn => {
    btn.addEventListener("click", () => {
      selectors.forEach(s => s.classList.remove("active", "border-[#FF5A00]", "border-[#D30611]", "border-[#D30611]", "bg-slate-100"));
      
      const key = btn.dataset.salsa;
      btn.classList.add("active", "bg-slate-100");
      
      // Aplicar color de borde activo según el tipo
      if (key === "jalapeno") btn.classList.add("border-[#D30611]");
      if (key === "habanero") btn.classList.add("border-[#FF5A00]");
      if (key === "fuego") btn.classList.add("border-[#D30611]");

      setActiveSalsa(key);
    });
  });

  // Inicializar en Habanero por defecto
  setActiveSalsa("habanero");
}

// --- Scroll Reveal ---
function initScrollReveal() {
  const revealParagraph = document.querySelector(".reveal-text");
  if (!revealParagraph) return;

  const text = revealParagraph.innerText;
  const words = text.split(" ");
  revealParagraph.innerHTML = words.map(w => `<span>${w}</span>`).join(" ");

  const spans = revealParagraph.querySelectorAll("span");

  window.addEventListener("scroll", () => {
    const rect = revealParagraph.getBoundingClientRect();
    const windowHeight = window.innerHeight;
    
    // Calcular qué porcentaje del párrafo ha pasado por la pantalla
    const progress = (windowHeight - rect.top) / (rect.height + windowHeight * 0.4);
    const wordsToShow = Math.floor(spans.length * Math.min(Math.max(progress, 0), 1));

    spans.forEach((span, idx) => {
      if (idx < wordsToShow) {
        span.classList.add("active");
      } else {
        span.classList.remove("active");
      }
    });
  });
}

// --- Formulario de Contacto (Lead) ---
function initContactForm() {
  const form = document.getElementById("chilechillon-form");
  const responseDiv = document.getElementById("form-response");

  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Resetear mensajes
    responseDiv.classList.add("hidden");
    responseDiv.innerHTML = "";

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalBtnText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg> Enviando...
    `;

    // Capturar datos y mapear los campos requeridos
    const formData = {
      nombre: form.nombre.value.trim(),
      apellido: form.apellido ? form.apellido.value.trim() : "",
      email: form.email.value.trim(),
      telefono: form.telefono.value.trim(),
      perfil: form.perfil.value,
      mensaje: form.mensaje ? form.mensaje.value.trim() : ""
    };

    try {
      const response = await fetch("/api/contact/chilechillon", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });

      const result = await response.json();

      if (response.ok) {
        responseDiv.className = "mt-6 p-4 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 text-sm glass-panel";
        responseDiv.innerHTML = `
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <strong>¡Fórmula Recibida!</strong> Tu sazón está a punto de potenciarse.
          </div>
          <p class="mt-2 text-xs text-slate-300">Hemos enviado un correo de bienvenida. Un estratega culinario te contactará en breve.</p>
        `;
        form.reset();
      } else {
        throw new Error(result.detail || "Error en el servidor");
      }
    } catch (error) {
      responseDiv.className = "mt-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm glass-panel";
      responseDiv.innerHTML = `
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <strong>Error de Picor:</strong> ${error.message}
        </div>
      `;
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnText;
      responseDiv.classList.remove("hidden");
    }
  });
}

// --- Amplificador de Antojos ---
function initDishSelector() {
  const dishCards = document.querySelectorAll(".dish-card");
  const pairingPanel = document.getElementById("dish-pairing-panel");
  const pairingBadge = document.getElementById("pairing-badge");
  const pairingTitle = document.getElementById("pairing-title");
  const pairingDesc = document.getElementById("pairing-desc");

  if (!dishCards.length || !pairingPanel) return;

  const pairings = {
    tacos: {
      badge: "Salsa Sugerida: Chile Chillón Habanero Tatemado 🌶️🌶️",
      badgeClass: "border-[#FF5A00]/20 bg-[#FF5A00]/5 text-[#FF5A00]",
      title: "Tacos al Pastor de Domingo (por @carlos.gastronomo)",
      desc: "\"¡Los tacos al pastor del domingo se elevan por completo! Unas gotas de Chile Chillón Habanero Tatemado cortan la grasa de la carne a la perfección y potencian cada bocado.\""
    },
    mariscos: {
      badge: "Salsa Sugerida: Chile Chillón Negra 🌶️",
      badgeClass: "border-slate-900/20 bg-slate-900/5 text-slate-900",
      title: "Aguachile Casero de Camarón (por @mariana_foodie)",
      desc: "\"Preparé este aguachile rápido para ver el partido de fútbol el fin de semana y el toque de Chile Chillón Negra fue la combinación perfecta, le da un sabor único a los mariscos.\""
    },
    hamburguesa: {
      badge: "Salsa Sugerida: Chile Chillón Habanero 🌶️🌶️",
      badgeClass: "border-[#FF5A00]/20 bg-[#FF5A00]/5 text-[#FF5A00]",
      title: "Burger Gourmet Casera (por @santiago_bbq)",
      desc: "\"El viernes de hamburguesas caseras no está completo sin la salsa Chile Chillón Habanero. Se integra perfectamente con el queso cheddar fundido y la carne. ¡Una delicia!\""
    },
    sopas: {
      badge: "Salsa Sugerida: Chile Chillón de Árbol 🌶️🌶️🌶️",
      badgeClass: "border-[#D30611]/20 bg-[#D30611]/5 text-[#D30611]",
      title: "Ramen con Sazón de Hogar (por @laura_caldos)",
      desc: "\"Un tazón de sopa de pollo caliente o un ramen rápido a mitad de semana con Chile Chillón de Árbol te revive al instante. Es súper reconfortante y con el picor ideal.\""
    },
    sushi: {
      badge: "Salsa Sugerida: Chile Chillón Negra 🌶️",
      badgeClass: "border-slate-900/20 bg-slate-900/5 text-slate-900",
      title: "Sushi Roll Fusionado (por @chef_sofia.g)",
      desc: "\"Hacer sushi en casa fue toda una experiencia, y bañar los rollos con salsa Chile Chillón Negra combinada con un toque de soya resultó ser una completa y deliciosa revelación.\""
    }
  };

  dishCards.forEach(card => {
    card.addEventListener("click", () => {
      const dish = card.dataset.dish;
      const data = pairings[dish];
      if (!data) return;

      // Quitar clases activas
      dishCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");

      // Transición del panel de descripción
      pairingPanel.style.opacity = "0";
      pairingPanel.style.transform = "translateY(15px)";

      setTimeout(() => {
        // Actualizar contenido
        pairingBadge.innerText = data.badge;
        pairingBadge.className = `px-3 py-1 border text-[10px] font-bold tracking-widest uppercase rounded-full inline-block transition-colors duration-500 ${data.badgeClass}`;
        pairingTitle.innerText = data.title;
        pairingDesc.innerText = data.desc;

        // Mostrar de nuevo
        pairingPanel.style.opacity = "1";
        pairingPanel.style.transform = "translateY(0)";
      }, 300);
    });
  });
}

// --- Recetario de Favoritos ---
function initRecipeFavorites() {
  const favButtons = document.querySelectorAll(".fav-btn");

  favButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const icon = btn.querySelector("i");
      const parentCard = btn.closest(".interactive-card");
      const likesCountElem = parentCard.querySelector(".likes-count");
      let currentLikes = parseInt(likesCountElem.innerText);

      const isActive = btn.classList.contains("active");

      // Añadir micro-animación Pop
      btn.classList.add("heart-pop");
      btn.addEventListener("animationend", () => {
        btn.classList.remove("heart-pop");
      }, { once: true });

      if (isActive) {
        // Desactivar
        btn.classList.remove("active");
        icon.className = "ph-bold ph-heart text-lg transition-transform duration-300 active:scale-150";
        likesCountElem.innerText = currentLikes - 1;
      } else {
        // Activar
        btn.classList.add("active");
        icon.className = "ph-fill ph-heart text-lg transition-transform duration-300 active:scale-150";
        likesCountElem.innerText = currentLikes + 1;
      }
    });
  });
}

// --- Tienda & Carrito de Compras E-Commerce (Añadir al carrito, Fichas de producto, etc.) ---
function initCart() {
  const products = {
    arbol: {
      name: "Chile Chillón de Árbol",
      price: 35,
      spicy: "🌶️🌶️🌶️🌶️",
      image: "Assets/Salsas/de_arbol.webp",
      filterClass: ""
    },
    habanero: {
      name: "Chile Chillón Habanero",
      price: 35,
      spicy: "🌶️🌶️🌶️",
      image: "Assets/Salsas/habanero.webp",
      filterClass: ""
    },
    habanero_tatemado: {
      name: "Habanero Tatemado",
      price: 35,
      spicy: "🌶️🌶️🌶️",
      image: "Assets/Salsas/tatemado.webp",
      filterClass: ""
    },
    negra: {
      name: "Chile Chillón Negra",
      price: 35,
      spicy: "🌶️🌶️",
      image: "Assets/Salsas/negra.webp",
      filterClass: ""
    },
    serrano: {
      name: "Chile Chillón Serrano",
      price: 35,
      spicy: "🌶️🌶️",
      image: "Assets/Salsas/serrano.webp",
      filterClass: ""
    }
  };

  let cart = [];

  // DOM Elements
  const cartToggleBtn = document.getElementById("cart-toggle-btn");
  const cartBadge = document.getElementById("cart-badge");
  const cartDrawer = document.getElementById("cart-drawer");
  const cartOverlay = document.getElementById("cart-overlay");
  const cartCloseBtn = document.getElementById("cart-close-btn");
  const cartItemsContainer = document.getElementById("cart-items-container");
  const cartFooter = document.getElementById("cart-footer");
  const cartSubtotal = document.getElementById("cart-subtotal");
  const cartCheckoutBtn = document.getElementById("cart-checkout-btn");

  const toastNotification = document.getElementById("toast-notification");
  const toastIconContainer = document.getElementById("toast-icon-container");
  const toastTitle = document.getElementById("toast-title");
  const toastMessage = document.getElementById("toast-message");

  if (!cartDrawer) return;

  // Cargar carrito desde localStorage
  try {
    const saved = localStorage.getItem("chilechillon-cart");
    if (saved) {
      cart = JSON.parse(saved);
    }
  } catch (e) {
    cart = [];
  }

  // Guardar carrito
  const saveCart = () => {
    try {
      localStorage.setItem("chilechillon-cart", JSON.stringify(cart));
    } catch (e) {
      console.error(e);
    }
  };

  // Abrir / Cerrar Drawer
  const openCart = () => {
    cartDrawer.classList.add("open");
    cartDrawer.classList.remove("translate-x-full");
    cartOverlay.classList.add("open");
    cartOverlay.classList.remove("pointer-events-none", "opacity-0");
  };

  const closeCart = () => {
    cartDrawer.classList.remove("open");
    cartDrawer.classList.add("translate-x-full");
    cartOverlay.classList.remove("open");
    cartOverlay.classList.add("pointer-events-none", "opacity-0");
  };

  if (cartToggleBtn) cartToggleBtn.addEventListener("click", openCart);
  if (cartCloseBtn) cartCloseBtn.addEventListener("click", closeCart);
  if (cartOverlay) cartOverlay.addEventListener("click", closeCart);

  // Toast Notificaciones Premium
  let toastTimeout = null;
  const showToast = (title, message, type = "success") => {
    if (toastTimeout) clearTimeout(toastTimeout);

    toastTitle.innerText = title;
    toastMessage.innerText = message;

    if (type === "success") {
      toastIconContainer.className = "w-8 h-8 rounded-full bg-green-500/10 flex justify-center items-center border border-green-500/20 text-green-500";
      toastIconContainer.innerHTML = '<i class="ph-fill ph-check-circle text-lg"></i>';
    } else if (type === "info") {
      toastIconContainer.className = "w-8 h-8 rounded-full bg-blue-500/10 flex justify-center items-center border border-blue-500/20 text-blue-500";
      toastIconContainer.innerHTML = '<i class="ph-fill ph-info text-lg"></i>';
    } else {
      toastIconContainer.className = "w-8 h-8 rounded-full bg-red-500/10 flex justify-center items-center border border-red-500/20 text-red-500";
      toastIconContainer.innerHTML = '<i class="ph-fill ph-warning-circle text-lg"></i>';
    }

    toastNotification.classList.remove("translate-y-20", "opacity-0", "pointer-events-none");
    toastNotification.classList.add("translate-y-0", "opacity-100");

    toastTimeout = setTimeout(() => {
      toastNotification.classList.add("translate-y-20", "opacity-0", "pointer-events-none");
      toastNotification.classList.remove("translate-y-0", "opacity-100");
    }, 3000);
  };

  // Renderizar Carrito
  const renderCart = () => {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

    // Actualizar Badge del Navbar
    if (cartBadge) {
      cartBadge.innerText = totalItems;
      if (totalItems > 0) {
        cartBadge.classList.remove("scale-0");
        cartBadge.classList.add("scale-100");
        
        // Micro-animación de rebote (pop)
        cartBadge.classList.add("heart-pop");
        cartBadge.addEventListener("animationend", () => {
          cartBadge.classList.remove("heart-pop");
        }, { once: true });
      } else {
        cartBadge.classList.remove("scale-100");
        cartBadge.classList.add("scale-0");
      }
    }

    // Renderizar Elementos
    if (totalItems === 0) {
      cartItemsContainer.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full text-center text-slate-400">
          <i class="ph-bold ph-shopping-bag text-5xl mb-3 text-slate-200"></i>
          <p class="text-sm">Tu carrito está vacío.</p>
          <button id="cart-back-to-shop-btn" class="mt-4 px-5 py-2 rounded-full bg-[#D30611] text-xs font-bold text-white uppercase tracking-wider transition-all duration-300 hover:bg-[#D30611]/90 hover:scale-105 active:scale-95">Comprar Salsas</button>
        </div>
      `;
      const backToShopBtn = document.getElementById("cart-back-to-shop-btn");
      if (backToShopBtn) {
        backToShopBtn.addEventListener("click", () => {
          closeCart();
          const tiendaSec = document.getElementById("tienda");
          if (tiendaSec) {
            tiendaSec.scrollIntoView({ behavior: "smooth" });
          }
        });
      }
      cartFooter.classList.add("hidden");
    } else {
      let itemsHTML = "";
      let subtotal = 0;

      cart.forEach(item => {
        const prod = products[item.id];
        if (!prod) return;

        const itemSubtotal = prod.price * item.quantity;
        subtotal += itemSubtotal;

        itemsHTML += `
          <div class="cart-item flex items-center justify-between gap-4 p-4 bg-slate-50 rounded-2xl border border-slate-100/50 transition-all duration-300">
            <!-- Miniatura de Botella con filtros dinámicos -->
            <div class="w-16 h-16 rounded-xl bg-white border border-slate-100 overflow-hidden flex justify-center items-center relative flex-shrink-0">
              <div class="absolute w-8 h-8 rounded-full bg-slate-100 blur-md"></div>
              <img src="${prod.image}" alt="${prod.name}" class="h-12 w-auto object-contain relative z-10 ${prod.filterClass}">
            </div>
            
            <!-- Detalles -->
            <div class="flex-grow min-w-0">
              <h4 class="font-semibold text-xs text-slate-900 truncate font-rubik">${prod.name}</h4>
              <p class="text-[10px] text-slate-400 font-bold uppercase tracking-wider mt-0.5">${prod.spicy}</p>
              <div class="flex items-center gap-2 mt-2">
                <span class="text-xs font-bold text-[#D30611] font-rubik">$${prod.price}.00</span>
                <span class="text-[10px] text-slate-400">x ${item.quantity}</span>
              </div>
            </div>

            <!-- Controles -->
            <div class="flex flex-col items-end gap-2">
              <button data-remove-item="${item.id}" class="cart-remove-btn text-slate-300 hover:text-red-500 transition-colors p-1" title="Eliminar del carrito">
                <i class="ph-bold ph-trash text-sm"></i>
              </button>
              
              <div class="flex items-center bg-white rounded-full border border-slate-100 p-0.5 gap-1">
                <button data-qty-change="${item.id}" data-delta="-1" class="w-6 h-6 rounded-full hover:bg-slate-100 text-slate-500 hover:text-slate-900 flex justify-center items-center text-xs font-bold active:scale-90 transition-all">-</button>
                <span class="text-xs font-semibold text-slate-800 w-4 text-center">${item.quantity}</span>
                <button data-qty-change="${item.id}" data-delta="1" class="w-6 h-6 rounded-full hover:bg-slate-100 text-slate-500 hover:text-slate-900 flex justify-center items-center text-xs font-bold active:scale-90 transition-all">+</button>
              </div>
            </div>
          </div>
        `;
      });

      cartItemsContainer.innerHTML = itemsHTML;
      cartSubtotal.innerText = `$${subtotal}.00 MXN`;
      cartFooter.classList.remove("hidden");

      // Vincular eventos de cantidad y eliminar
      const removeButtons = cartItemsContainer.querySelectorAll("[data-remove-item]");
      removeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
          const id = btn.dataset.removeItem;
          removeFromCart(id);
        });
      });

      const qtyChangeBtns = cartItemsContainer.querySelectorAll("[data-qty-change]");
      qtyChangeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
          const id = btn.dataset.qtyChange;
          const delta = parseInt(btn.dataset.delta);
          updateQuantity(id, delta);
        });
      });
    }
  };

  // Funciones de Estado
  const addToCart = (productId) => {
    const existing = cart.find(item => item.id === productId);
    const prod = products[productId];
    if (!prod) return;

    if (existing) {
      existing.quantity += 1;
    } else {
      cart.push({ id: productId, quantity: 1 });
    }

    saveCart();
    renderCart();
    showToast("¡Excelente!", `${prod.name} añadido al carrito.`);
  };

  const updateQuantity = (productId, delta) => {
    const existing = cart.find(item => item.id === productId);
    if (!existing) return;

    existing.quantity += delta;
    if (existing.quantity <= 0) {
      removeFromCart(productId);
    } else {
      saveCart();
      renderCart();
    }
  };

  const removeFromCart = (productId) => {
    const prod = products[productId];
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    renderCart();
    if (prod) {
      showToast("Eliminado", `${prod.name} removido del carrito.`, "info");
    }
  };

  // Vincular botones de "Añadir al Carrito" en la tienda principal
  const addButtons = document.querySelectorAll("[data-add-to-cart]");
  addButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.addToCart;
      addToCart(id);
    });
  });

  // Procesamiento del Pedido (Checkout simulado premium con integración WhatsApp)
  if (cartCheckoutBtn) {
    cartCheckoutBtn.addEventListener("click", () => {
      const originalText = cartCheckoutBtn.innerHTML;
      cartCheckoutBtn.disabled = true;
      cartCheckoutBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg> Procesando Pedido...
      `;

      setTimeout(() => {
        // Crear mensaje formateado de WhatsApp
        let messageText = "¡Hola Chile Chillón! 🌶️ Me gustaría confirmar el siguiente pedido de salsas:\n\n";
        let totalVal = 0;
        cart.forEach(item => {
          const prod = products[item.id];
          if (prod) {
            messageText += `• *${item.quantity}x ${prod.name}* ($${prod.price}.00 MXN c/u)\n`;
            totalVal += prod.price * item.quantity;
          }
        });
        messageText += `\n*Total a pagar: $${totalVal}.00 MXN*\n\n`;
        messageText += "Quedo a la espera de sus datos para coordinar el pago (transferencia/efectivo) y el envío. ¡Muchas gracias!";

        const encodedMessage = encodeURIComponent(messageText);
        // Teléfono placeholder de la marca: 52 33 1234 5678 o similar
        const waUrl = `https://wa.me/523921097809?text=${encodedMessage}`;

        // Vaciar Carrito
        cart = [];
        saveCart();
        renderCart();
        closeCart();

        // Restaurar botón
        cartCheckoutBtn.disabled = false;
        cartCheckoutBtn.innerHTML = originalText;

        // Mostrar Toast de Éxito Premium
        showToast("¡Pedido Generado!", "Redirigiendo a WhatsApp para completar tu compra.");
        
        // Redirigir suavemente
        setTimeout(() => {
          window.open(waUrl, "_blank");
        }, 1500);

      }, 1800);
    });
  }

  // Render inicial
  renderCart();
}

// --- Opiniones de Google Maps y Slider de Paginación ---
function initTestimonios() {
  const grid = document.getElementById("testimonios-grid");
  const ratingBadge = document.getElementById("google-rating-badge");
  const reviewsCountText = document.getElementById("google-reviews-count");
  const prevBtn = document.getElementById("prev-testimonios-btn");
  const nextBtn = document.getElementById("next-testimonios-btn");
  const dotsContainer = document.getElementById("testimonios-dots");
  
  if (!grid) return;

  // Fallback reviews in case API is completely unreachable
  let reviews = [
    {
      name: "Rogelio Chávez",
      initials: "RC",
      tag: "Cliente Google",
      stars: 5,
      text: "Es la primera salsa que realmente no solo pica por picar, sino que amplifica el sabor real de las botanas. En mi mesa de fin de semana ya no puede faltar el Habanero."
    },
    {
      name: "Alina Torres",
      initials: "AT",
      tag: "Cliente Google",
      stars: 5,
      text: "Sus sabores son muy auténticos! Me encanta la de árbol"
    },
    {
      name: "Josselin M. Sánchez López",
      initials: "JS",
      tag: "Cliente Google",
      stars: 5,
      text: "De mis favoritas!!! Más la de tatemado"
    },
    {
      name: "Chef Mario Cárdenas",
      initials: "MC",
      tag: "Cliente Google",
      stars: 5,
      text: "Implementamos las tres salsas de Chile Chillón directamente en nuestra barra de especialidad. La consistencia del sabor y picor lote por lote nos da total seguridad en la cocina."
    },
    {
      name: "Noe Vazquez",
      initials: "NV",
      tag: "Cliente Google",
      stars: 5,
      text: "Excelentes todas!"
    },
    {
      name: "Maria Fernanda Lopez Estrada",
      initials: "ML",
      tag: "Cliente Google",
      stars: 5,
      text: "El mejor de todos"
    },
    {
      name: "Alejandra Gutiérrez",
      initials: "AG",
      tag: "Cliente Google",
      stars: 5,
      text: "La rotación de producto es fantástica. El cliente final regresa buscando exactamente el mismo lote debido a la calidad. Ha sido una excelente adición comercial a nuestro catálogo."
    },
    {
      name: "Adriana Medina",
      initials: "AM",
      tag: "Cliente Google",
      stars: 5,
      text: "Muy buenas salsas, mi favorita es habanero tatemado en mariscos y especialmente en ceviche de atún!! 100% recomendadas!"
    },
    {
      name: "Jose Juan Alvarez",
      initials: "JA",
      tag: "Cliente Google",
      stars: 5,
      text: "La salsa tatemada está deliciosa, es mi favorita. Las demás también son excelentes y van con todo."
    },
    {
      name: "Daniel Moreno",
      initials: "DM",
      tag: "Cliente Google",
      stars: 5,
      text: "Compré el paquete de las 4 salsas (Árbol, Habanero, Tatemado y Negra) y están increíbles. La salsa Negra con soya y ajo asado le dio un toque único a mis mariscos."
    },
    {
      name: "Jorge Magdaleno",
      initials: "JM",
      tag: "Cliente Google",
      stars: 5,
      text: "Aderezos muy buenos"
    },
    {
      name: "America Dalila Mejia Ceballos",
      initials: "AM",
      tag: "Cliente Google",
      stars: 5,
      text: "Riquísimas y fácil de acompañar con todo"
    },
    {
      name: "Sofía Palacios",
      initials: "SP",
      tag: "Cliente Google",
      stars: 5,
      text: "El servicio y la rapidez de entrega son excepcionales. Además, las botellas llegaron en perfecto estado. Recomiendo ampliamente la salsa Habanero Tatemado."
    },
    {
      name: "Andrea Bleibero",
      initials: "AB",
      tag: "Cliente Google",
      stars: 5,
      text: "Están deliciosas sus salsas, se mantienen en buen estado en el refrigerador. Y me gustan para mariscos, pastas y pizza"
    },
    {
      name: "Israel Godinez",
      initials: "IG",
      tag: "Cliente Google",
      stars: 5,
      text: "Excelentes productos, literalmente van con todo."
    },
    {
      name: "Héctor Ruiz",
      initials: "HR",
      tag: "Cliente Google",
      stars: 5,
      text: "La salsa de Árbol tiene el picor exacto que buscaba, bien equilibrado y con ingredientes totalmente naturales. Ya se volvió mi favorita para los tacos del diario."
    },
    {
      name: "Monserrat Hernandez Maximo",
      initials: "MH",
      tag: "Cliente Google",
      stars: 5,
      text: "Las mejores salsas que he probado"
    },
    {
      name: "Abraham Vazquezo",
      initials: "AV",
      tag: "Cliente Google",
      stars: 5,
      text: "De lujo los chilitos!!!"
    },
    {
      name: "Mariana Villanueva",
      initials: "MV",
      tag: "Cliente Google",
      stars: 5,
      text: "Excelente producto para nuestro restaurante. A los comensales les encanta la variedad y el diseño de la botella llama mucho la atención en la mesa. ¡Un éxito total!"
    },
    {
      name: "Carlos Ortiz",
      initials: "CO",
      tag: "Cliente Google",
      stars: 5,
      text: "Sabor artesanal garantizado. Llevo comprándolas desde hace meses y la consistencia siempre es la misma. Un producto de calidad impecable."
    },
    {
      name: "Laura Guzmán",
      initials: "LG",
      tag: "Cliente Google",
      stars: 5,
      text: "Un picante honesto que de verdad respeta el sabor de la comida. La de Habanero Tatemado con cebolla asada es simplemente espectacular."
    }
  ];

  let currentSlide = 0; // Cada slide muestra 3 reseñas

  function getPageCount() {
    return Math.ceil(reviews.length / 3);
  }

  function renderSlide(slideIndex) {
    if (reviews.length === 0) return;
    const pageCount = getPageCount();

    // Limitar el índice
    if (slideIndex < 0) slideIndex = pageCount - 1;
    if (slideIndex >= pageCount) slideIndex = 0;
    currentSlide = slideIndex;

    const startIdx = currentSlide * 3;
    const selected = reviews.slice(startIdx, startIdx + 3);

    // Animación de salida (Fade Out)
    grid.style.opacity = "0";
    grid.style.transform = "translateY(10px)";
    grid.style.transition = "opacity 0.3s ease, transform 0.3s ease";

    setTimeout(() => {
      grid.innerHTML = selected.map(review => {
        const starHTML = '<i class="ph-fill ph-star"></i>'.repeat(review.stars);
        return `
          <div class="glass-panel p-8 rounded-3xl border-slate-100 shadow-sm relative flex flex-col justify-between h-80 bg-white group hover:-translate-y-2 hover:shadow-md transition-all duration-300">
            <i class="ph-bold ph-quotes text-5xl text-slate-100 absolute top-6 right-6"></i>
            <div>
              <div class="flex gap-1 text-[#FF5A00]">
                ${starHTML}
              </div>
              <p class="mt-6 text-sm text-slate-600 leading-relaxed">
                "${review.text}"
              </p>
            </div>
            <div class="flex items-center gap-4 pt-6 border-t border-slate-100">
              <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-[#D30611] to-[#FF5A00] flex justify-center items-center text-white font-bold text-sm">
                ${review.initials}
              </div>
              <div>
                <div class="text-sm font-bold text-slate-900 font-rubik">${review.name}</div>
                <div class="text-[10px] text-slate-500 uppercase tracking-widest">${review.tag}</div>
              </div>
            </div>
          </div>
        `;
      }).join("");
      
      // Animación de entrada (Fade In)
      grid.style.opacity = "1";
      grid.style.transform = "translateY(0)";
      
      renderDots();
    }, 300);
  }

  function renderDots() {
    if (!dotsContainer) return;
    const pageCount = getPageCount();
    
    let dotsHTML = "";
    for (let i = 0; i < pageCount; i++) {
      if (i === currentSlide) {
        dotsHTML += `<button data-slide-to="${i}" class="w-6 h-2.5 rounded-full bg-[#D30611] transition-all duration-300" aria-label="Página ${i+1} activa"></button>`;
      } else {
        dotsHTML += `<button data-slide-to="${i}" class="w-2.5 h-2.5 rounded-full bg-slate-200 hover:bg-slate-400 transition-all duration-300" aria-label="Ir a página ${i+1}"></button>`;
      }
    }
    dotsContainer.innerHTML = dotsHTML;

    // Vincular clic en dots
    const dots = dotsContainer.querySelectorAll("[data-slide-to]");
    dots.forEach(dot => {
      dot.addEventListener("click", () => {
        const idx = parseInt(dot.dataset.slideTo);
        renderSlide(idx);
      });
    });
  }

  // Cargar reseñas reales de la API
  async function loadRealReviews() {
    try {
      const response = await fetch("/api/contact/reviews/chilechillon");
      if (response.ok) {
        const data = await response.json();
        if (data.reviews && data.reviews.length > 0) {
          reviews = data.reviews;
        }
        if (data.rating && ratingBadge) {
          ratingBadge.innerHTML = `${data.rating.toFixed(1)} ⭐`;
        }
        if (data.user_ratings_total !== undefined && reviewsCountText) {
          reviewsCountText.innerText = `Basado en ${data.user_ratings_total} opiniones reales de Google Maps.`;
        }
      }
    } catch (e) {
      console.warn("No se pudieron cargar reseñas de Google. Usando fallback local:", e);
    } finally {
      renderSlide(0);
      initReviewsWidget();
    }
  }

  // Lógica del widget flotante de reseñas de Google
  function initReviewsWidget() {
    const widget = document.getElementById("google-reviews-widget");
    const closeBtn = document.getElementById("close-reviews-widget-btn");
    if (!widget) return;

    // Verificar si el usuario ya descartó el widget en esta sesión
    let isDismissed = false;
    try {
      isDismissed = sessionStorage.getItem("chilechillon-reviews-widget-dismissed") === "true";
    } catch (e) {
      console.warn("sessionStorage no está disponible o está bloqueado:", e);
    }
    if (isDismissed) return;

    // Retrasar la aparición del widget por 3.5 segundos después de que cargue la página
    setTimeout(() => {
      widget.classList.remove("translate-y-20", "opacity-0");
    }, 3500);

    // Evento de descarte del widget
    if (closeBtn) {
      closeBtn.addEventListener("click", (e) => {
        e.preventDefault();
        widget.classList.add("translate-y-20", "opacity-0");
        try {
          sessionStorage.setItem("chilechillon-reviews-widget-dismissed", "true");
        } catch (e) {
          console.warn("No se pudo guardar la preferencia en sessionStorage:", e);
        }
      });
    }
  }

  // Inicialización
  loadRealReviews();

  if (prevBtn) {
    prevBtn.addEventListener("click", () => {
      renderSlide(currentSlide - 1);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", () => {
      renderSlide(currentSlide + 1);
    });
  }
}

