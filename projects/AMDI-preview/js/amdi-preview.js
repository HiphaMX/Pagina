/**
 * AMDI Architectural & Editorial Experience Engine
 * Preview Environment (Estudio Bang Inspiration)
 */

document.addEventListener("DOMContentLoaded", () => {
  initStudioClock();
  initProjectFilters();
  initQuickViewDrawer();
  initMobileNav();
});

/* ==========================================================================
   1. STUDIO CLOCK (Guadalajara, Jalisco GMT-6)
   ========================================================================== */
function initStudioClock() {
  const clockElement = document.querySelector(".amdi-clock-pill .time-val");
  if (!clockElement) return;

  function updateClock() {
    const options = {
      timeZone: "America/Mexico_City",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: true,
    };
    const formatter = new Intl.DateTimeFormat("es-MX", options);
    clockElement.textContent = formatter.format(new Date());
  }

  updateClock();
  setInterval(updateClock, 1000);
}

/* ==========================================================================
   2. INTERACTIVE PROJECT FILTERS (proyectos.html)
   ========================================================================== */
function initProjectFilters() {
  const filterButtons = document.querySelectorAll(".amdi-filter-pill");
  const projectCards = document.querySelectorAll(".amdi-mosaic-card");

  if (!filterButtons.length || !projectCards.length) return;

  filterButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      filterButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");

      const filter = btn.getAttribute("data-filter");

      projectCards.forEach((card) => {
        const category = card.getAttribute("data-category");
        if (filter === "all" || category === filter) {
          card.style.display = "flex";
          setTimeout(() => {
            card.style.opacity = "1";
            card.style.transform = "translateY(0)";
          }, 10);
        } else {
          card.style.opacity = "0";
          card.style.transform = "translateY(8px)";
          setTimeout(() => {
            card.style.display = "none";
          }, 250);
        }
      });
    });
  });
}

/* ==========================================================================
   3. QUICK-VIEW PROJECT DRAWER
   ========================================================================== */
const AMDI_PROJECT_DETAILS = {
  "residencia-antares": {
    title: "Residencia Antares",
    category: "Residencial de Alta Gama",
    location: "Guadalajara, Jalisco",
    year: "2023",
    area: "620 m²",
    headline: "Atmósferas serenas a través de luz natural filtrada y madera noble.",
    description: "Concebida como un refugio contemporáneo dentro de la ciudad, Residencia Antares conjuga líneas tectónicas puras con una cuidada selección de maderas naturales y textiles crudos. Cada ángulo fue orientado para abrazar el jardín interior, generando transiciones sutiles entre interior y exterior.",
    palette: [
      { name: "Roble Blanco", hex: "#d8c4b2", note: "Carpintería y plafones" },
      { name: "Travertino Veracruz", hex: "#e4dbcf", note: "Pisos y cubiertas" },
      { name: "Lino Belga Crudo", hex: "#efe8db", note: "Tapicería y cortinajes" },
      { name: "Acero Ennegrecido", hex: "#232323", note: "Herrería estructural" }
    ],
    images: [
      "images/Residencia-Antares-1_1.webp",
      "images/Residencia-Antares-2_1.webp",
      "images/Residencia-Antares-3_1.webp"
    ]
  },
  "residencia-jesus-maria": {
    title: "Residencia Jesús María",
    category: "Residencial",
    location: "Los Altos de Jalisco",
    year: "2023",
    area: "480 m²",
    headline: "Raíz vernácula, cantera regional y confort contemporáneo.",
    description: "Una reinterpretación honesta de la casona alteña. Residencia Jesús María celebra los materiales autóctonos: cantera rosa y blanca en muros gruesos, techumbres de madera estufada y un diálogo sobrio entre piezas de arte contemporáneo y artesanía local.",
    palette: [
      { name: "Cantera Blanca", hex: "#e5ded4", note: "Muros portantes" },
      { name: "Nogal Americano", hex: "#634735", note: "Mobiliario a la medida" },
      { name: "Barro Cocido", hex: "#ba6646", note: "Acentos cerámicos" },
      { name: "Lino Grisáceo", hex: "#c9c7bf", note: "Textiles living" }
    ],
    images: [
      "images/Residencia-Jesus-Maria-1_1.webp",
      "images/Residencia-Jesus-Maria-2_1.webp",
      "images/Residencia-Jesus-Maria-3_1.webp"
    ]
  },
  "expo-obra-blanca": {
    title: "Expo Obra Blanca",
    category: "Comercial & Showroom",
    location: "Centro Citibanamex, CDMX",
    year: "2023",
    area: "140 m²",
    headline: "Pabellón inmersivo que expone la belleza táctil de los recubrimientos.",
    description: "Diseño y montaje de pabellón efímero para firmas de acabados arquitectónicos en la feria líder de acabados en México. Una geometría escultural de arcos y volúmenes monolíticos que invitaban al visitante a tocar, sentir y experimentar la materialidad en su estado más puro.",
    palette: [
      { name: "Cal Hidráulica", hex: "#f2ece4", note: "Acabado monolítico" },
      { name: "Cobre Oxidado", hex: "#8d5b4c", note: "Acentos esculturales" },
      { name: "Luz Cálida 2700K", hex: "#fde8b9", note: "Iluminación indirecta" }
    ],
    images: [
      "images/Expo-Obra-Blanca-1_1.webp",
      "images/Expo-Obra-Blanca-2_1.webp",
      "images/Expo-Obra-Blanca-3_1.webp"
    ]
  },
  "residencia-los-frailes": {
    title: "Residencia Los Frailes",
    category: "Residencial",
    location: "Zapopan, Jalisco",
    year: "2022",
    area: "540 m²",
    headline: "Lujo discreto, iluminación escenográfica y distribución abierta.",
    description: "Un proyecto residencial donde el minimalismo cálido cobra protagonismo. Salones de doble altura con grandes ventanales, cocina integrada en piedra sinterizada oscura y recámaras diseñadas como suites de hospitalidad.",
    palette: [
      { name: "Mármol Gris Marquina", hex: "#3e4244", note: "Isla de cocina" },
      { name: "Roble Ahumado", hex: "#5b4e43", note: "Lambrines" },
      { name: "Microcemento", hex: "#cac6be", note: "Pisos continuos" }
    ],
    images: [
      "images/Residencia-Los-Frailes-1_1.webp",
      "images/Residencia-Los-Frailes-2_1.webp"
    ]
  },
  "oficinas-valenciana": {
    title: "Oficinas Corporativas Valenciana",
    category: "Comercial",
    location: "Guadalajara, Jal.",
    year: "2023",
    area: "320 m²",
    headline: "Entornos de trabajo inspiradores que combinan privacidad y calidez.",
    description: "Transformación de planta libre en un espacio de trabajo colaborativo que huye de la frialdad corporativa estándar, integrando biofilia, luz tamizada y salas de concentración acústica.",
    palette: [
      { name: "Fieltro Acústico", hex: "#858784", note: "Mamparas divisorias" },
      { name: "Fresno Natural", hex: "#dbc6a8", note: "Estaciones de trabajo" },
      { name: "Verde Oliva", hex: "#5c6553", note: "Tapicería y vegetación" }
    ],
    images: [
      "images/valenciana-1.webp",
      "images/valenciana-2.webp"
    ]
  },
  "boutique-altea": {
    title: "Showroom Altea",
    category: "Comercial & Showroom",
    location: "Andares, Zapopan",
    year: "2022",
    area: "190 m²",
    headline: "Escenografía comercial orientada a una experiencia sensorial de compra.",
    description: "Espacio comercial de mobiliario e interiorismo donde cada ambiente funciona como una viñeta editorial para el cliente final.",
    palette: [
      { name: "Terracota Pulida", hex: "#c46849", note: "Pavimento" },
      { name: "Lino Crudo", hex: "#f0ebe1", note: "Telonería" },
      { name: "Latón Mate", hex: "#c4a35a", note: "Herrajes y luminarias" }
    ],
    images: [
      "images/Expo-Obra-Blanca-1_1.webp"
    ]
  }
};

function initQuickViewDrawer() {
  let backdrop = document.querySelector(".amdi-drawer-backdrop");
  let drawer = document.querySelector(".amdi-drawer");

  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.className = "amdi-drawer-backdrop";
    document.body.appendChild(backdrop);
  }

  if (!drawer) {
    drawer = document.createElement("div");
    drawer.className = "amdi-drawer";
    document.body.appendChild(drawer);
  }

  function closeDrawer() {
    drawer.classList.remove("active");
    backdrop.classList.remove("active");
    document.body.style.overflow = "";
  }

  backdrop.addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeDrawer();
  });

  // Attach to project cards / preview triggers
  document.querySelectorAll("[data-quick-view]").forEach((trigger) => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const slug = trigger.getAttribute("data-quick-view");
      const project = AMDI_PROJECT_DETAILS[slug] || {
        title: trigger.getAttribute("data-title") || "Proyecto AMDI",
        category: trigger.getAttribute("data-cat") || "Arquitectura Interior",
        location: trigger.getAttribute("data-loc") || "Guadalajara, México",
        year: "2023",
        headline: trigger.getAttribute("data-headline") || "Diseño a la medida con acabados artesanales.",
        description: trigger.getAttribute("data-desc") || "Proyecto desarrollado integralmente por AMDI, cuidando cada detalle desde la conceptualización espacial hasta la selección de mobiliario y dirección de obra.",
        palette: [
          { name: "Madera Noble", hex: "#bfa386", note: "Carpintería artesanal" },
          { name: "Piedra Natural", hex: "#dfd8ce", note: "Mármol / Cantera" },
          { name: "Lino Belga", hex: "#eae4d8", note: "Textiles de alta costura" }
        ],
        images: [trigger.getAttribute("data-img") || "images/Residencia-Antares-1_1.webp"]
      };

      openDrawerWithContent(project);
    });
  });

  function openDrawerWithContent(data) {
    const waText = encodeURIComponent(`Hola Adriana / AMDI, estuve viendo el proyecto "${data.title}" en su web y me encantaría cotizar un proyecto con esta línea de diseño.`);
    const waUrl = `https://wa.me/523331003460?text=${waText}`;

    let paletteHtml = "";
    if (data.palette && data.palette.length) {
      paletteHtml = `
        <div class="amdi-palette-board">
          <span class="amdi-mono-tag">Paleta Material & Texturas</span>
          <div class="amdi-palette-grid">
            ${data.palette.map(p => `
              <div class="amdi-palette-item">
                <div class="amdi-palette-swatch" style="background-color: ${p.hex}"></div>
                <span class="amdi-palette-name">${p.name}</span>
                <span class="amdi-palette-sub">${p.note}</span>
              </div>
            `).join("")}
          </div>
        </div>
      `;
    }

    let galleryHtml = "";
    if (data.images && data.images.length) {
      galleryHtml = `
        <div class="amdi-drawer-gallery">
          ${data.images.map(img => `
            <img class="amdi-drawer-img" src="${img}" alt="${data.title}" loading="lazy">
          `).join("")}
        </div>
      `;
    }

    drawer.innerHTML = `
      <div class="amdi-drawer-header">
        <div>
          <span class="amdi-mono-tag">${data.category} · ${data.location}</span>
          <h3 style="margin: 4px 0 0; font-size: 1.5rem; font-weight: 500; letter-spacing: -0.02em;">${data.title}</h3>
        </div>
        <button class="amdi-drawer-close" aria-label="Cerrar">&times;</button>
      </div>
      <div class="amdi-drawer-content">
        <div>
          <p style="font-size: 1.15rem; font-weight: 500; color: #141414; line-height: 1.4; margin-bottom: 12px;">${data.headline}</p>
          <p style="font-size: 0.95rem; color: #666660; line-height: 1.65; margin: 0;">${data.description}</p>
        </div>

        ${paletteHtml}

        <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;">
          <a href="${waUrl}" target="_blank" rel="noopener" class="amdi-btn-editorial amdi-btn-editorial-dark">
            Conversar sobre este estilo en WhatsApp &rarr;
          </a>
          <a href="contacto.html" class="amdi-btn-editorial amdi-btn-editorial-outline">
            Agendar Cita en Estudio
          </a>
        </div>

        ${galleryHtml}
      </div>
    `;

    drawer.querySelector(".amdi-drawer-close").addEventListener("click", closeDrawer);

    backdrop.classList.add("active");
    drawer.classList.add("active");
    document.body.style.overflow = "hidden";
  }
}

/* ==========================================================================
   4. MOBILE NAV TOGGLER
   ========================================================================== */
function initMobileNav() {
  const btn = document.querySelector(".amdi-mobile-menu-btn");
  const nav = document.querySelector(".amdi-nav-links");
  if (!btn || !nav) return;

  btn.addEventListener("click", () => {
    const isShown = nav.style.display === "flex";
    if (isShown) {
      nav.style.display = "none";
    } else {
      nav.style.display = "flex";
      nav.style.flexDirection = "column";
      nav.style.position = "absolute";
      nav.style.top = "100%";
      nav.style.left = "0";
      nav.style.right = "0";
      nav.style.background = "#fafaf8";
      nav.style.padding = "24px 32px";
      nav.style.borderBottom = "1px solid rgba(20,20,20,0.12)";
      nav.style.gap = "18px";
    }
  });
}
