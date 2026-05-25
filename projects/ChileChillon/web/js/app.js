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
});

// --- Preloader ---
function initPreloader() {
  const preloader = document.getElementById("preloader");
  if (!preloader) return;

  let seen = false;
  try {
    seen = sessionStorage.getItem("chilechillon-preloader-seen") === "true";
  } catch (e) {
    seen = false;
  }

  if (seen) {
    preloader.remove();
  } else {
    setTimeout(() => {
      preloader.classList.add("fade-out");
      try {
        sessionStorage.setItem("chilechillon-preloader-seen", "true");
      } catch (e) {}
      setTimeout(() => preloader.remove(), 600);
    }, 1800);
  }
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

  let mouseX = 0, mouseY = 0;
  let cursorX = 0, cursorY = 0;
  let glowX = 0, glowY = 0;

  document.addEventListener("mousemove", (e) => {
    mouseX = e.clientX;
    mouseY = e.clientY;
  });

  // Loop de renderizado suave
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
      </svg> Fabricando tu Alquimia...
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
      badge: "Salsa Sugerida: Chile Chillón Habanero 🌶️🌶️",
      badgeClass: "border-[#FF5A00]/20 bg-[#FF5A00]/5 text-[#FF5A00]",
      title: "Tacos al Pastor Elevados",
      desc: "El habanero naranja tatemado corta la grasa de la carne al pastor asada y combina maravillosamente con el dulzor de la piña, logrando que la cebollita asada y el cilantro exploten en sabor. ¡El maridaje callejero supremo!"
    },
    mariscos: {
      badge: "Salsa Sugerida: Chile Chillón Jalapeño 🌶️",
      badgeClass: "border-[#D30611]/20 bg-[#D30611]/5 text-[#D30611]",
      title: "Aguachile Potenciado",
      desc: "La acidez del limón del aguachile y el pepino fresco encuentran a su media naranja en el picor alegre y fresco del Jalapeño. Aporta notas herbales sin opacar la frescura marina."
    },
    hamburguesa: {
      badge: "Salsa Sugerida: Chile Chillón Fuego Extremo 🌶️🌶️🌶️",
      badgeClass: "border-[#D30611]/20 bg-[#D30611]/5 text-[#D30611]",
      title: "Burguer & Papas Explosivas",
      desc: "El queso cheddar fundido y la costra de carne asada al carbón necesitan la audacia de nuestro Fuego Extremo. Despierta las papas fritas y hace vibrar cada bocado con un picor brutal pero adictivo."
    },
    sopas: {
      badge: "Salsa Sugerida: Chile Chillón Habanero 🌶️🌶️",
      badgeClass: "border-[#FF5A00]/20 bg-[#FF5A00]/5 text-[#FF5A00]",
      title: "Ramen & Caldos Robustos",
      desc: "Un chorrito de Habanero en tus caldos caseros o tazón de ramen humeante aporta un resplandor ahumado que se integra al fondo de forma espectacular, levantando cualquier sopa de inmediato."
    },
    sushi: {
      badge: "Salsa Sugerida: Chile Chillón Jalapeño 🌶️",
      badgeClass: "border-[#D30611]/20 bg-[#D30611]/5 text-[#D30611]",
      title: "Sushi & Bowls Fusionados",
      desc: "Las texturas cremosas del aguacate y el queso crema en los rollos se cortan de forma limpia por la frescura herbal de la salsa de Jalapeño. Potencia la soya de manera insospechada."
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

