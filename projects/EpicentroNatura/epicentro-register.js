/**
 * Epicentro Natura - Sistema Unificado de Registro y Verificación Comercial
 * Proporciona el stepper interactivo en 4 fases, pre-llenado automático de categoría
 * y selección de métodos de contacto preferidos.
 */

(function () {
  'use strict';

  const SUBCATEGORIES_MAP = {
    "comida-delivery": [
      { slug: "pizzas-pastas", label: "Pizzas y Pastas" },
      { slug: "tacos-carnes", label: "Tacos y Carnes" },
      { slug: "comida-casera", label: "Comida Casera" },
      { slug: "snacks-botanas", label: "Snacks y Botanas" },
      { slug: "mariscos", label: "Mariscos" },
      { slug: "pasteleria-reposteria", label: "Pastelería y Repostería" },
      { slug: "cafeterias-barras", label: "Cafeterías y Barras" },
      { slug: "helados-nieve", label: "Helados y Nieve" },
      { slug: "donas-churros", label: "Donas y Churros" },
      { slug: "galletas-postres", label: "Galletas y Postres" }
    ],
    "productos-artesanales": [
      { slug: "herbolaria-cuidado-natural", label: "Herbolaria y Cuidado Natural" },
      { slug: "alimentos-gourmet", label: "Alimentos Gourmet y Conservas" },
      { slug: "velas-aromaterapia", label: "Velas y Aromaterapia" },
      { slug: "textiles-decoracion", label: "Textiles y Decoración" },
      { slug: "joyeria-ceramica", label: "Joyería y Cerámica" }
    ],
    "educacion": [
      { slug: "colegios-institutos", label: "Colegios e Institutos" },
      { slug: "clases-particulares", label: "Clases Particulares" },
      { slug: "bienestar-formacion", label: "Bienestar y Formación" },
      { slug: "idiomas", label: "Idiomas" },
      { slug: "arte-musica", label: "Arte y Música" }
    ],
    "servicios-profesionales": [
      { slug: "contabilidad-fiscal", label: "Contabilidad & Fiscal" },
      { slug: "abogados-legal", label: "Abogados & Legal" },
      { slug: "diseno-marketing", label: "Diseño & Marketing" },
      { slug: "inmobiliario", label: "Inmobiliario" },
      { slug: "consultoria", label: "Consultoría" },
      { slug: "diseno-interiores", label: "Diseño de interiores" },
      { slug: "arquitectura", label: "Arquitectura" },
      { slug: "fisioterapeuta", label: "Fisioterapeuta" },
      { slug: "finanzas", label: "Finanzas" },
      { slug: "otros", label: "Otros" }
    ],
    "servicios-hogar": [
      { slug: "electricidad-iluminacion", label: "Electricidad e Iluminación" },
      { slug: "fontaneria-gas", label: "Fontanería y Gas" },
      { slug: "carpinteria", label: "Carpintería" },
      { slug: "cerrajeria", label: "Cerrajería" },
      { slug: "limpieza-especializada", label: "Limpieza especializada" },
      { slug: "mantenimiento", label: "Mantenimiento" },
      { slug: "jardineria", label: "Jardinería" },
      { slug: "carwash", label: "Carwash" },
      { slug: "tintoreria-planchaduria", label: "Tintorería y Planchaduría" },
      { slug: "otros", label: "Otros" }
    ],
    "hogar": [
      { slug: "cortinas-persianas", label: "Cortinas y Persianas" },
      { slug: "plantas-paisajismo", label: "Plantas y Paisajismo" },
      { slug: "muebles-decoracion", label: "Muebles y Decoración" }
    ],
    "mascotas": [
      { slug: "estetica-spa", label: "Estética y Spa Canino" },
      { slug: "veterinaria-vacunas", label: "Veterinaria y Vacunas" },
      { slug: "alimentos-accesorios", label: "Alimentos y Accesorios" },
      { slug: "paseadores-cuidado", label: "Paseadores y Cuidado" }
    ],
    "fitness": [
      { slug: "gimnasios-studios", label: "Gimnasios y Studios" },
      { slug: "entrenador-personal", label: "Entrenador Personal" },
      { slug: "yoga-pilates", label: "Yoga y Pilates" },
      { slug: "cross-training", label: "Cross Training" },
      { slug: "artes-marciales", label: "Artes Marciales" },
      { slug: "tiendas-suplementos", label: "Tiendas de suplementos" }
    ]
  };

  let currentRegId = null;
  let currentBusinessName = "";
  let waVerified = false;
  let currentPaymentMode = "mp";
  let currentSelectedPlan = "microsite"; // "microsite" ($399/año) o "free_basic" ($0)

  // Configuración del Micrositio Oficial ($399/año)
  let registerCoverPhoto = "";
  let registerFeaturedProducts = []; // Array of { name, price, description, photo }
  let registerMenuSections = []; // Array of { title, subtitle, description, items: [{ name, price, description }] }
  let tempNewProductPhoto = "";
  let registerUploadedPhotos = []; // compatibilidad retroactiva

  function selectRegistrationPlan(plan) {
    currentSelectedPlan = plan;
    const btnMicro = document.getElementById("plan-btn-microsite");
    const btnFree = document.getElementById("plan-btn-free");
    const photosSec = document.getElementById("reg-photos-section");
    const proNotice = document.getElementById("reg-pro-notice");
    const freeNotice = document.getElementById("reg-free-notice");
    const websiteSec = document.getElementById("reg-website-section");
    const stepLabel = document.getElementById("wizard-step-label");
    const btnSubmit1 = document.getElementById("btn-submit-step1");

    if (plan === "microsite") {
      if (btnMicro) {
        btnMicro.className = "p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-emerald-600 flex items-center justify-between cursor-pointer";
      }
      if (btnFree) {
        btnFree.className = "p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex items-center justify-between opacity-80 hover:opacity-100 cursor-pointer";
      }
      if (photosSec) photosSec.classList.remove("hidden");
      if (proNotice) proNotice.classList.remove("hidden");
      if (freeNotice) freeNotice.classList.add("hidden");
      if (websiteSec) websiteSec.classList.remove("hidden");
      if (stepLabel) stepLabel.textContent = "Paso 1 de 3";
      if (btnSubmit1) {
        btnSubmit1.innerHTML = `<span>Continuar a Validación (Paso 1 de 3)</span> <i data-lucide="arrow-right" class="w-4 h-4"></i>`;
      }
    } else {
      if (btnMicro) {
        btnMicro.className = "p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex items-center justify-between opacity-80 hover:opacity-100 cursor-pointer";
      }
      if (btnFree) {
        btnFree.className = "p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-slate-900 flex items-center justify-between cursor-pointer";
      }
      if (photosSec) photosSec.classList.add("hidden");
      if (proNotice) proNotice.classList.add("hidden");
      if (freeNotice) freeNotice.classList.remove("hidden");
      if (websiteSec) websiteSec.classList.add("hidden");
      if (stepLabel) stepLabel.textContent = "Paso 1 de 2";
      if (btnSubmit1) {
        btnSubmit1.innerHTML = `<span>Continuar con Registro Gratuito (Paso 1 de 2)</span> <i data-lucide="arrow-right" class="w-4 h-4"></i>`;
      }
    }
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  function compressImageFile(file, maxWidth = 1000, quality = 0.82) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          const canvas = document.createElement("canvas");
          let width = img.width;
          let height = img.height;
          if (width > maxWidth) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          }
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext("2d");
          ctx.fillStyle = "#ffffff";
          ctx.fillRect(0, 0, width, height);
          ctx.drawImage(img, 0, 0, width, height);
          resolve(canvas.toDataURL("image/webp", quality));
        };
        img.onerror = reject;
        img.src = e.target.result;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  // --- GESTIÓN DE PORTADA DEL MICROSITIO ---
  async function handleRegisterCoverFile(e) {
    const file = (e.target.files || [])[0];
    if (!file) return;
    try {
      registerCoverPhoto = await compressImageFile(file, 1400, 0.85);
      renderRegisterCoverPreview();
    } catch (err) {
      console.warn("Error comprimiendo portada:", err);
    }
    e.target.value = "";
  }

  function promptRegisterCoverUrl() {
    const url = prompt("Ingresa la URL pública de la portada (ej. https://...):");
    if (url && url.trim().startsWith("http")) {
      registerCoverPhoto = url.trim();
      renderRegisterCoverPreview();
    }
  }

  function removeRegisterCoverPhoto() {
    registerCoverPhoto = "";
    renderRegisterCoverPreview();
  }

  function renderRegisterCoverPreview() {
    const preview = document.getElementById("reg-cover-preview");
    if (!preview) return;
    if (registerCoverPhoto) {
      preview.innerHTML = `
        <div class="relative w-full h-28 rounded-2xl bg-slate-900 overflow-hidden shadow-xs border border-slate-200 group">
          <img src="${registerCoverPhoto}" alt="Portada" class="w-full h-full object-cover">
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent flex items-end justify-between p-2.5">
            <span class="text-[11px] font-bold text-white flex items-center gap-1"><i data-lucide="image" class="w-3.5 h-3.5 text-emerald-400"></i> Portada seleccionada</span>
            <button type="button" onclick="removeRegisterCoverPhoto()" class="px-2 py-1 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-[10px] font-bold shadow-xs transition-colors">
              ✕ Quitar
            </button>
          </div>
        </div>
      `;
    } else {
      preview.innerHTML = `
        <div class="p-3 rounded-2xl bg-slate-50 border border-dashed border-slate-300 text-center text-[11px] text-slate-400">
          Sin portada seleccionada (se utilizará la portada oficial de Epicentro Natura).
        </div>
      `;
    }
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  // --- GESTIÓN DE PRODUCTOS DESTACADOS (MÁX. 10) ---
  async function handleNewProdPhotoFile(e) {
    const file = (e.target.files || [])[0];
    if (!file) return;
    try {
      tempNewProductPhoto = await compressImageFile(file, 800, 0.85);
      renderNewProdPhotoPreview();
    } catch (err) {
      console.warn("Error comprimiendo foto de producto:", err);
    }
    e.target.value = "";
  }

  function promptNewProdPhotoUrl() {
    const url = prompt("Ingresa la URL pública de la foto del producto:");
    if (url && url.trim().startsWith("http")) {
      tempNewProductPhoto = url.trim();
      renderNewProdPhotoPreview();
    }
  }

  function removeNewProdPhoto() {
    tempNewProductPhoto = "";
    renderNewProdPhotoPreview();
  }

  function renderNewProdPhotoPreview() {
    const box = document.getElementById("reg-new-prod-photo-preview");
    if (!box) return;
    if (tempNewProductPhoto) {
      box.innerHTML = `
        <div class="relative w-12 h-12 rounded-xl bg-white border border-slate-200 overflow-hidden shadow-xs flex items-center justify-center p-0.5 group">
          <img src="${tempNewProductPhoto}" alt="Miniatura" class="w-full h-full object-contain bg-white">
          <button type="button" onclick="removeNewProdPhoto()" title="Quitar foto" class="absolute inset-0 bg-slate-900/60 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">✕</button>
        </div>
      `;
    } else {
      box.innerHTML = `
        <div class="w-12 h-12 rounded-xl bg-slate-100 border border-dashed border-slate-300 flex items-center justify-center text-slate-400">
          <i data-lucide="image" class="w-5 h-5"></i>
        </div>
      `;
    }
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  function addRegisterFeaturedProduct() {
    if (registerFeaturedProducts.length >= 10) {
      alert("Ya has alcanzado el límite máximo de 10 productos destacados.");
      return;
    }
    const nameInput = document.getElementById("reg-new-prod-name");
    const priceInput = document.getElementById("reg-new-prod-price");
    const descInput = document.getElementById("reg-new-prod-desc");
    const tagInput = document.getElementById("reg-new-prod-tag");
    const fitInput = document.getElementById("reg-new-prod-fit");

    const name = nameInput ? nameInput.value.trim() : "";
    if (!name) {
      alert("Por favor indica el nombre del producto.");
      if (nameInput) nameInput.focus();
      return;
    }
    const price = priceInput ? parseFloat(priceInput.value) || 0.0 : 0.0;
    const desc = descInput ? descInput.value.trim() : "";
    const tag = tagInput ? tagInput.value.trim() : "";
    const fit = fitInput ? fitInput.value : "contain";

    registerFeaturedProducts.push({
      name: name,
      price: price,
      description: desc,
      photo: tempNewProductPhoto || "",
      tag: tag,
      fit: fit
    });

    if (nameInput) nameInput.value = "";
    if (priceInput) priceInput.value = "";
    if (descInput) descInput.value = "";
    if (tagInput) tagInput.value = "";
    tempNewProductPhoto = "";
    renderNewProdPhotoPreview();
    renderRegisterFeaturedGrid();
  }

  function removeRegisterFeaturedProduct(idx) {
    registerFeaturedProducts.splice(idx, 1);
    renderRegisterFeaturedGrid();
  }

  window.editRegisterProductTag = function(idx) {
    if (idx < 0 || idx >= registerFeaturedProducts.length) return;
    const current = registerFeaturedProducts[idx].tag || "";
    const newTag = prompt("Ingresa la etiqueta para la foto de este producto (ej. Asesoría Profesional, Especialidad, Más Vendido, Promoción):", current);
    if (newTag !== null) {
      registerFeaturedProducts[idx].tag = newTag.trim();
      renderRegisterFeaturedGrid();
    }
  };

  window.toggleRegisterProductFit = function(idx) {
    if (idx < 0 || idx >= registerFeaturedProducts.length) return;
    const currentFit = registerFeaturedProducts[idx].fit || "contain";
    registerFeaturedProducts[idx].fit = (currentFit === "cover") ? "contain" : "cover";
    renderRegisterFeaturedGrid();
  };

  function renderRegisterFeaturedGrid() {
    const grid = document.getElementById("reg-featured-grid");
    const badge = document.getElementById("reg-featured-counter-badge");
    if (badge) badge.textContent = `${registerFeaturedProducts.length} / 10`;

    // Sincronizar compatibilidad retroactiva con photos
    registerUploadedPhotos = registerFeaturedProducts.map(p => p.photo).filter(Boolean);

    if (!grid) return;
    if (registerFeaturedProducts.length === 0) {
      grid.innerHTML = `
        <div class="py-3 text-center text-[11px] text-slate-400">
          No has agregado productos destacados aún (puedes añadir hasta 10 con foto, precio y descripción).
        </div>
      `;
      return;
    }

    grid.innerHTML = registerFeaturedProducts.map((p, idx) => `
      <div class="p-2.5 rounded-2xl bg-white border border-slate-200 shadow-xs flex items-center justify-between gap-3 group">
        <div class="flex items-center gap-3 min-w-0">
          <div class="relative w-12 h-12 rounded-xl bg-white border border-slate-100 flex items-center justify-center shrink-0 overflow-hidden">
            ${p.photo
              ? `<img src="${p.photo}" alt="${p.name}" class="w-full h-full ${p.fit === 'cover' ? 'object-cover' : 'object-contain p-1'}">`
              : `<span class="text-xs font-mono font-bold text-slate-400">#${idx + 1}</span>`}
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="text-xs font-bold text-slate-900 truncate">${p.name}</span>
              ${p.tag ? `<span class="px-1.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[9px] font-bold uppercase tracking-wider shrink-0">${p.tag}</span>` : ''}
              <span class="px-1.5 py-0.5 rounded-md ${p.fit === 'cover' ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-100 text-slate-600'} text-[9px] font-mono shrink-0">${p.fit === 'cover' ? 'Rellenar' : 'Altura'}</span>
            </div>
            <div class="text-[11px] font-mono font-bold text-emerald-700">$${parseFloat(p.price || 0).toFixed(2)} MXN</div>
            ${p.description ? `<p class="text-[10px] text-slate-500 truncate max-w-[200px] sm:max-w-xs">${p.description}</p>` : ''}
          </div>
        </div>
        <div class="flex items-center gap-1 shrink-0">
          <button type="button" onclick="toggleRegisterProductFit(${idx})" title="Alternar ajuste: Altura o Rellenar" class="px-2 py-1 rounded-lg ${p.fit === 'cover' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200' : 'bg-slate-100 text-slate-600'} text-[10px] font-bold flex items-center gap-1 transition-colors">
            <span>${p.fit === 'cover' ? '🖼️ Rellenar' : '📐 Altura'}</span>
          </button>
          <button type="button" onclick="editRegisterProductTag(${idx})" title="Cambiar etiqueta" class="px-2 py-1 rounded-lg bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 text-slate-600 text-[10px] font-bold flex items-center gap-1 transition-colors">
            <i data-lucide="tag" class="w-3 h-3 text-emerald-600"></i>
            <span>${p.tag ? p.tag : '+ Etiqueta'}</span>
          </button>
          <button type="button" onclick="removeRegisterFeaturedProduct(${idx})" title="Eliminar producto" class="w-7 h-7 rounded-lg bg-slate-100 hover:bg-rose-600 hover:text-white text-slate-500 flex items-center justify-center text-xs transition-colors shrink-0">
            ✕
          </button>
        </div>
      </div>
    `).join("");
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  // --- GESTIÓN DE OTROS PRODUCTOS (ESTILO MENÚ SIN FOTO, MÁX. 2 SECCIONES) ---
  function addRegisterMenuSection() {
    if (registerMenuSections.length >= 2) {
      alert("Puedes agregar un máximo de 2 secciones tipo menú para complementos.");
      return;
    }
    const defaultTitles = [
      { title: "Presentaciones por Litro", subtitle: "Para familias y eventos", desc: "Precios especiales en presentaciones grandes." },
      { title: "Botanas y Complementos", subtitle: "Acompañamientos frescos", desc: "El complemento perfecto para compartir." }
    ];
    const def = defaultTitles[registerMenuSections.length] || { title: "Otros Productos", subtitle: "Complementos", desc: "" };
    registerMenuSections.push({
      title: def.title,
      subtitle: def.subtitle,
      description: def.desc,
      items: []
    });
    renderRegisterMenuSections();
  }

  function removeRegisterMenuSection(secIdx) {
    registerMenuSections.splice(secIdx, 1);
    renderRegisterMenuSections();
  }

  function updateMenuSecMeta(secIdx, field, val) {
    if (registerMenuSections[secIdx]) {
      registerMenuSections[secIdx][field] = val;
    }
  }

  function addRegisterMenuItem(secIdx) {
    const sec = registerMenuSections[secIdx];
    if (!sec) return;
    const nameInput = document.getElementById(`sec-${secIdx}-new-item-name`);
    const priceInput = document.getElementById(`sec-${secIdx}-new-item-price`);
    const descInput = document.getElementById(`sec-${secIdx}-new-item-desc`);

    const name = nameInput ? nameInput.value.trim() : "";
    if (!name) {
      alert("Por favor ingresa el nombre del complemento o producto.");
      if (nameInput) nameInput.focus();
      return;
    }
    const price = priceInput ? parseFloat(priceInput.value) || 0.0 : 0.0;
    const desc = descInput ? descInput.value.trim() : "";

    sec.items.push({ name, price, description: desc });

    if (nameInput) nameInput.value = "";
    if (priceInput) priceInput.value = "";
    if (descInput) descInput.value = "";

    renderRegisterMenuSections();
  }

  function removeRegisterMenuItem(secIdx, itemIdx) {
    if (registerMenuSections[secIdx] && registerMenuSections[secIdx].items) {
      registerMenuSections[secIdx].items.splice(itemIdx, 1);
      renderRegisterMenuSections();
    }
  }

  function renderRegisterMenuSections() {
    const container = document.getElementById("reg-menu-sections-container");
    const badge = document.getElementById("reg-menu-sec-counter-badge");
    const addBtn = document.getElementById("btn-add-menu-section");

    if (badge) badge.textContent = `${registerMenuSections.length} / 2 secciones`;
    if (addBtn) addBtn.style.display = registerMenuSections.length >= 2 ? "none" : "inline-flex";

    if (!container) return;
    if (registerMenuSections.length === 0) {
      container.innerHTML = `
        <div class="p-3 rounded-2xl bg-slate-50 border border-dashed border-slate-300 text-center text-[11px] text-slate-400">
          No has añadido secciones tipo menú. (Opcional, útil para complementos o presentaciones sin foto).
        </div>
      `;
      return;
    }

    container.innerHTML = registerMenuSections.map((sec, secIdx) => `
      <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2.5">
        <div class="flex items-center justify-between">
          <span class="text-xs font-black uppercase text-emerald-800 tracking-wider">Sección Menú #${secIdx + 1}</span>
          <button type="button" onclick="removeRegisterMenuSection(${secIdx})" class="text-[11px] font-bold text-rose-600 hover:text-rose-800 transition-colors">
            ✕ Eliminar Sección
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div>
            <label class="block text-[10px] font-bold text-slate-700 mb-0.5">Título de Sección *</label>
            <input type="text" value="${sec.title || ''}" oninput="updateMenuSecMeta(${secIdx}, 'title', this.value)" placeholder="Ej. Presentaciones por Litro" class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-white focus:ring-1 focus:ring-emerald-500 focus:outline-none">
          </div>
          <div>
            <label class="block text-[10px] font-bold text-slate-700 mb-0.5">Subtítulo</label>
            <input type="text" value="${sec.subtitle || ''}" oninput="updateMenuSecMeta(${secIdx}, 'subtitle', this.value)" placeholder="Ej. Para reuniones o familias" class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-white focus:ring-1 focus:ring-emerald-500 focus:outline-none">
          </div>
        </div>

        <div>
          <label class="block text-[10px] font-bold text-slate-700 mb-0.5">Descripción de la Sección</label>
          <input type="text" value="${sec.description || ''}" oninput="updateMenuSecMeta(${secIdx}, 'description', this.value)" placeholder="Ej. Presentaciones ideales para surtir al mayoreo..." class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-white focus:ring-1 focus:ring-emerald-500 focus:outline-none">
        </div>

        <div class="pt-2 border-t border-slate-200">
          <span class="text-[10px] font-bold text-slate-500 uppercase tracking-wider block mb-1">Renglones de Menú (${sec.items.length})</span>
          ${sec.items.length === 0 ? `<p class="text-[10px] text-slate-400 italic mb-2">No has agregado renglones a esta sección.</p>` : `
            <div class="space-y-1 mb-2">
              ${sec.items.map((item, itemIdx) => `
                <div class="p-2 rounded-xl bg-white border border-slate-200 flex items-center justify-between text-xs">
                  <div class="min-w-0 pr-2">
                    <span class="font-bold text-slate-900">${item.name}</span>
                    <span class="font-mono text-emerald-700 font-bold ml-1.5">$${parseFloat(item.price || 0).toFixed(2)}</span>
                    ${item.description ? `<p class="text-[10px] text-slate-500 truncate">${item.description}</p>` : ''}
                  </div>
                  <button type="button" onclick="removeRegisterMenuItem(${secIdx}, ${itemIdx})" class="text-rose-500 hover:text-rose-700 text-xs px-1.5 py-0.5">✕</button>
                </div>
              `).join("")}
            </div>
          `}

          <div class="p-2 rounded-xl bg-white border border-slate-200 grid grid-cols-1 sm:grid-cols-12 gap-1.5 items-center">
            <input type="text" id="sec-${secIdx}-new-item-name" placeholder="Nombre (ej. 1 Litro Salsa Macha)" class="sm:col-span-5 px-2 py-1 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">
            <input type="number" step="0.5" id="sec-${secIdx}-new-item-price" placeholder="Precio ($)" class="sm:col-span-3 px-2 py-1 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none font-mono">
            <input type="text" id="sec-${secIdx}-new-item-desc" placeholder="Desc. breve" class="sm:col-span-4 px-2 py-1 text-xs rounded-lg border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">
            <button type="button" onclick="addRegisterMenuItem(${secIdx})" class="sm:col-span-12 py-1 px-2 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold transition-colors flex items-center justify-center gap-1">
              <span>+ Añadir Renglón al Menú</span>
            </button>
          </div>
        </div>
      </div>
    `).join("");
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  // Compatibilidad con fotos sueltas previas
  function renderRegisterPhotosGrid() {
    renderRegisterFeaturedGrid();
  }
  function handleRegisterPhotoFiles(e) {
    handleNewProdPhotoFile(e);
  }
  function promptRegisterPhotoUrl() {
    promptNewProdPhotoUrl();
  }
  function removeRegisterPhoto(idx) {
    removeRegisterFeaturedProduct(idx);
  }

  function setPaymentMode(mode) {
    currentPaymentMode = "mp";
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  function detectActiveCategory(explicitCat) {
    if (explicitCat && typeof explicitCat === 'string' && explicitCat.trim()) {
      const clean = explicitCat.trim().toLowerCase();
      return clean === 'escuelas' ? 'educacion' : clean;
    }
    if (window.currentCategorySlug && window.currentCategorySlug !== 'all') {
      const clean = String(window.currentCategorySlug).trim().toLowerCase();
      return clean === 'escuelas' ? 'educacion' : clean;
    }
    try {
      const params = new URLSearchParams(window.location.search);
      const cat = params.get('cat');
      if (cat && cat !== 'all') {
        const clean = cat.trim().toLowerCase();
        return clean === 'escuelas' ? 'educacion' : clean;
      }
    } catch (e) {}

    try {
      const path = window.location.pathname || '';
      const m = path.match(/categorias\/([a-z0-9-]+)\.html/);
      if (m && m[1] && m[1] !== 'all') {
        const clean = m[1].toLowerCase();
        return clean === 'escuelas' ? 'educacion' : clean;
      }
    } catch (e) {}

    return null;
  }

  function renderWizardHTML() {
    return `
    <div class="relative w-full max-w-xl rounded-3xl bg-white p-6 sm:p-8 shadow-2xl max-h-[92vh] overflow-y-auto">
      <button onclick="closeRegisterModal()" class="absolute top-5 right-5 p-2 rounded-full text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors">
        <i data-lucide="x" class="w-5 h-5"></i>
      </button>

      <!-- Stepper Header -->
      <div class="mb-6 pr-10">
        <div class="flex items-center justify-between gap-1 mb-2">
          <span class="text-[10px] font-black uppercase tracking-wider text-emerald-600">ALTA OFICIAL Y VERIFICACIÓN</span>
          <span id="wizard-step-label" class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Paso 1 de 3</span>
        </div>
        <h3 id="wizard-title" class="text-xl sm:text-2xl font-black text-slate-950">Registrar Comercio o Servicio</h3>
        <p id="wizard-desc" class="text-xs text-slate-500 mt-1">Conéctate directamente con las familias de cotos Natura con sello de confianza.</p>

        <!-- Progress Pills -->
        <div class="grid grid-cols-3 gap-2 mt-4">
          <div id="step-bar-1" class="h-1.5 rounded-full bg-emerald-600 transition-all"></div>
          <div id="step-bar-2" class="h-1.5 rounded-full bg-slate-200 transition-all"></div>
          <div id="step-bar-3" class="h-1.5 rounded-full bg-slate-200 transition-all"></div>
        </div>
      </div>

      <!-- FASE 1: DATOS DEL COMERCIO Y CONTACTO -->
      <div id="reg-step-1">
        <!-- SELECTOR DE PLAN: PLAN PRO ($399/AÑO) VS REGISTRO GRATUITO ($0) -->
        <div class="mb-4 p-1.5 bg-slate-100 rounded-2xl border border-slate-200 grid grid-cols-1 sm:grid-cols-2 gap-2">
          <button type="button" id="plan-btn-microsite" onclick="selectRegistrationPlan('microsite')" class="p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-emerald-600 flex items-center justify-between cursor-pointer">
            <span class="text-xs sm:text-sm font-black text-slate-900 flex items-center gap-1.5">
              <i data-lucide="sparkles" class="w-4 h-4 text-emerald-600"></i> Plan Pro
            </span>
            <span class="px-2.5 py-1 text-[11px] font-black uppercase rounded-lg bg-emerald-100 text-emerald-800 font-mono">$399 / año</span>
          </button>

          <button type="button" id="plan-btn-free" onclick="selectRegistrationPlan('free_basic')" class="p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex items-center justify-between opacity-80 hover:opacity-100 cursor-pointer">
            <span class="text-xs sm:text-sm font-bold text-slate-700 flex items-center gap-1.5">
              <i data-lucide="file-text" class="w-4 h-4 text-slate-400"></i> Registro gratuito
            </span>
            <span class="px-2.5 py-1 text-[11px] font-bold rounded-lg bg-slate-200 text-slate-700 font-mono">$0</span>
          </button>
        </div>

        <div id="reg-pro-notice" class="mb-4 p-3.5 rounded-2xl bg-emerald-50/90 border border-emerald-200/90 flex items-start gap-2.5 text-left">
          <i data-lucide="sparkles" class="w-4 h-4 text-emerald-600 shrink-0 mt-0.5"></i>
          <p class="text-[11px] text-emerald-950 leading-relaxed font-medium">
            Página interactiva con posibilidad de publicar hasta 10 fotografías de tus productos o servicios, además posibilidad de incluir un botón hacia tu sitio web propio.
          </p>
        </div>

        <div id="reg-free-notice" class="hidden mb-4 p-3.5 rounded-2xl bg-amber-50/80 border border-amber-200/80 flex items-start gap-2.5 text-left">
          <i data-lucide="info" class="w-4 h-4 text-amber-600 shrink-0 mt-0.5"></i>
          <p class="text-[11px] text-amber-900 leading-relaxed font-medium">
            Tu comercio se publicará con textos de contacto e hipervínculos funcionales directos (llamada y WhatsApp). No incluye fotos ni vínculo a sitios web.
          </p>
        </div>

        <form onsubmit="submitStep1(event)" class="space-y-4">
          <!-- Campo Trampa Honeypot Anti-Bot -->
          <input type="text" id="reg-honeypot" name="hp_field" style="display:none!important;" tabindex="-1" autocomplete="off">

          <div>
            <label class="block text-xs font-bold text-slate-800 mb-1">Nombre Comercial *</label>
            <input type="text" id="reg-name" required placeholder="Ej. Pizzería Di Vico / Plomería Los Robles" class="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-800 mb-1">Giro de la Oferta *</label>
              <select id="reg-category" onchange="syncSubcategoriesDropdown()" class="w-full px-3 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                <option value="comida-delivery">Comida & Delivery</option>
                <option value="productos-artesanales">Productos artesanales</option>
                <option value="educacion">Educación</option>
                <option value="servicios-profesionales">Servicios Profesionales</option>
                <option value="servicios-hogar">Servicios hogar</option>
                <option value="hogar">Hogar y Decoración</option>
                <option value="mascotas">Mascotas</option>
                <option value="fitness">Fitness</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-800 mb-1">Subcategoría *</label>
              <select id="reg-subcategory" class="w-full px-3 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                <option value="pizzas-pastas">Pizzas y Pastas</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-800 mb-1">Tipo de Espacio / Atención *</label>
              <select id="reg-type" class="w-full px-3 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                <option value="local-establecido">Punto de venta / Local fijo</option>
                <option value="sin-punto-venta">A domicilio en coto / Con previa cita</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-800 mb-1">Ubicación / Coto / Local *</label>
              <input type="text" id="reg-address" required placeholder="Ej. Coto Ceiba Casa 45 / Plaza Natura" class="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
            </div>
          </div>

          <div class="border-t border-slate-100 pt-3">
            <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">Datos del Titular (para validación)</span>
            <div>
              <label class="block text-xs font-bold text-slate-800 mb-1">Nombre Completo del Responsable *</label>
              <input type="text" id="reg-owner" required placeholder="Ej. Lic. Carlos Méndez" class="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-bold text-slate-800 mb-1">Correo Electrónico *</label>
              <input type="email" id="reg-email" required placeholder="tu@correo.com" class="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-800 mb-1">WhatsApp de Pedidos / Atención *</label>
              <input type="tel" id="reg-wa" required placeholder="33 1234 5678" class="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-800 mb-1 flex items-center justify-between">
              <span>Horario de Atención Comercial *</span>
              <span class="text-[10px] font-normal text-slate-400">Ej. Lun a Sáb 09:00 a 19:00 hrs</span>
            </label>
            <div class="relative">
              <i data-lucide="clock" class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2"></i>
              <input type="text" id="reg-schedule" required placeholder="Ej. Lunes a Sábado · 09:00 a 19:00 hrs" class="w-full pl-10 pr-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
            </div>
          </div>

          <!-- MÉTODOS DE CONTACTO Y ATENCIÓN PREFERIDOS -->
          <div class="pt-1">
            <label class="block text-xs font-bold text-slate-800 mb-1.5 flex items-center justify-between">
              <span>Métodos de Contacto / Atención Preferidos *</span>
              <span class="text-[10px] font-normal text-slate-400">Selecciona los que utilices</span>
            </label>
            <div class="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-white cursor-pointer transition-all has-[:checked]:border-emerald-600 has-[:checked]:bg-emerald-50/60 has-[:checked]:text-emerald-950">
                <input type="checkbox" name="pref_contact" value="whatsapp" checked class="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500">
                <span class="text-xs font-semibold text-slate-800 flex items-center gap-1">💬 WhatsApp</span>
              </label>
              <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-white cursor-pointer transition-all has-[:checked]:border-emerald-600 has-[:checked]:bg-emerald-50/60 has-[:checked]:text-emerald-950">
                <input type="checkbox" name="pref_contact" value="llamada" checked class="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500">
                <span class="text-xs font-semibold text-slate-800 flex items-center gap-1">📞 Llamada</span>
              </label>
              <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-white cursor-pointer transition-all has-[:checked]:border-emerald-600 has-[:checked]:bg-emerald-50/60 has-[:checked]:text-emerald-950">
                <input type="checkbox" name="pref_contact" value="punto-venta" class="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500">
                <span class="text-xs font-semibold text-slate-800 flex items-center gap-1">🏪 Punto de Venta</span>
              </label>
              <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-white cursor-pointer transition-all has-[:checked]:border-emerald-600 has-[:checked]:bg-emerald-50/60 has-[:checked]:text-emerald-950">
                <input type="checkbox" name="pref_contact" value="delivery" class="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500">
                <span class="text-xs font-semibold text-slate-800 flex items-center gap-1">🛵 A Domicilio</span>
              </label>
              <label class="flex items-center gap-2 p-2.5 rounded-xl border border-slate-200 bg-slate-50 hover:bg-white cursor-pointer transition-all has-[:checked]:border-emerald-600 has-[:checked]:bg-emerald-50/60 has-[:checked]:text-emerald-950 col-span-2 sm:col-span-1">
                <input type="checkbox" name="pref_contact" value="cita-previa" class="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500">
                <span class="text-xs font-semibold text-slate-800 flex items-center gap-1">📅 Previa Cita</span>
              </label>
            </div>
          </div>

          <div id="reg-website-section">
            <label class="block text-xs font-bold text-slate-800 mb-1 flex items-center justify-between">
              <span class="flex items-center gap-1.5">
                <span>Sitio Web Oficial del Negocio</span>
                <span class="px-1.5 py-0.5 text-[9px] font-black rounded bg-emerald-100 text-emerald-800 uppercase">Plan Pro</span>
              </span>
              <span class="text-[11px] font-normal text-slate-400">(Opcional)</span>
            </label>
            <div class="relative">
              <i data-lucide="globe" class="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2"></i>
              <input type="url" id="reg-website" placeholder="https://www.tunegocio.com.mx" class="w-full pl-10 pr-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
            </div>
          </div>

          <div class="flex items-center gap-2 pt-1">
            <input type="checkbox" id="reg-delivery" class="w-4 h-4 text-emerald-600 rounded border-slate-300 focus:ring-emerald-500">
            <label for="reg-delivery" class="text-xs text-slate-700">Ofrezco servicio a domicilio en cotos de la zona</label>
          </div>

          <!-- CONFIGURACIÓN DE PÁGINA INTERACTIVA EN EPIZENTRO ($399/AÑO): PORTADA, DESTACADOS Y MENÚ -->
          <div id="reg-photos-section" class="border-t border-slate-100 pt-3 space-y-4">
            <!-- 1. PORTADA DE TU PÁGINA INTERACTIVA -->
            <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <div class="flex items-center justify-between">
                <div>
                  <span class="text-xs font-bold text-slate-900 block">1. Portada de tu página interactiva (Hero Banner)</span>
                  <span class="text-[11px] text-slate-500">Fotografía horizontal para el fondo superior de tu página interactiva.</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <input type="file" id="reg-cover-file-input" accept="image/*" class="hidden" onchange="handleRegisterCoverFile(event)">
                  <button type="button" onclick="document.getElementById('reg-cover-file-input').click()" class="px-2.5 py-1 rounded-xl bg-white hover:bg-slate-100 text-slate-700 text-[11px] font-bold border border-slate-200 flex items-center gap-1 shadow-xs">
                    <i data-lucide="camera" class="w-3 h-3 text-emerald-600"></i> Subir
                  </button>
                  <button type="button" onclick="promptRegisterCoverUrl()" class="px-2.5 py-1 rounded-xl bg-white hover:bg-slate-100 text-slate-700 text-[11px] font-bold border border-slate-200 flex items-center gap-1 shadow-xs">
                    <i data-lucide="link" class="w-3 h-3 text-emerald-600"></i> URL
                  </button>
                </div>
              </div>
              <div id="reg-cover-preview">
                <div class="p-3 rounded-xl bg-white border border-dashed border-slate-300 text-center text-[11px] text-slate-400">
                  Sin portada seleccionada (se utilizará la portada oficial de Epicentro Natura).
                </div>
              </div>
            </div>

            <!-- 2. PRODUCTOS DESTACADOS (MÁX. 10) -->
            <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div class="flex items-center justify-between">
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-xs font-bold text-slate-900">2. Productos Destacados</span>
                    <span class="px-1.5 py-0.2 text-[9px] font-black uppercase rounded-md bg-emerald-100 text-emerald-800 font-mono">Máx. 10</span>
                  </div>
                  <span class="text-[11px] text-slate-500">Cada producto incluye foto, nombre, precio y descripción con botón "Pedir por WhatsApp".</span>
                </div>
                <span id="reg-featured-counter-badge" class="px-2 py-0.5 text-[10px] font-black uppercase rounded-full bg-emerald-100 text-emerald-800 font-mono">0 / 10</span>
              </div>

              <!-- Encabezados de la sección de destacados (proporcionados por el usuario) -->
              <div class="p-2.5 rounded-xl bg-white border border-slate-200 space-y-2">
                <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Encabezados de la Sección Destacados</span>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  <div>
                    <label class="block text-[10px] font-bold text-slate-700 mb-0.5">Título General *</label>
                    <input type="text" id="reg-featured-title" value="Nuestra Selección Destacada" placeholder="Ej. Nuestra Selección Destacada" class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">
                  </div>
                  <div>
                    <label class="block text-[10px] font-bold text-slate-700 mb-0.5">Subtítulo</label>
                    <input type="text" id="reg-featured-subtitle" value="Hecho a mano en pequeños lotes" placeholder="Ej. Hecho a mano en pequeños lotes" class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">
                  </div>
                </div>
                <div>
                  <label class="block text-[10px] font-bold text-slate-700 mb-0.5">Descripción General</label>
                  <textarea id="reg-featured-desc" rows="1" placeholder="Ej. Recetas familiares y fórmulas artesanales elaboradas con ingredientes seleccionados." class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">Elaborados con ingredientes seleccionados y recetas tradicionales.</textarea>
                </div>
              </div>

              <!-- Mini formulario para añadir un producto destacado -->
              <div class="p-3 rounded-xl bg-white border border-emerald-200 shadow-xs space-y-2">
                <span class="text-[11px] font-bold text-emerald-900 block">+ Añadir Producto Destacado</span>
                <div class="flex items-center gap-2">
                  <div id="reg-new-prod-photo-preview" class="shrink-0">
                    <div class="w-12 h-12 rounded-xl bg-slate-100 border border-dashed border-slate-300 flex items-center justify-center text-slate-400">
                      <i data-lucide="image" class="w-5 h-5"></i>
                    </div>
                  </div>
                  <div class="flex flex-col gap-1">
                    <input type="file" id="reg-new-prod-file-input" accept="image/*" class="hidden" onchange="handleNewProdPhotoFile(event)">
                    <button type="button" onclick="document.getElementById('reg-new-prod-file-input').click()" class="px-2 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-bold border border-slate-200 flex items-center gap-1">
                      <i data-lucide="camera" class="w-3 h-3 text-emerald-600"></i> Cargar Foto
                    </button>
                    <button type="button" onclick="promptNewProdPhotoUrl()" class="px-2 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-bold border border-slate-200 flex items-center gap-1">
                      <i data-lucide="link" class="w-3 h-3 text-emerald-600"></i> URL Foto
                    </button>
                  </div>
                  <div class="flex-1 grid grid-cols-1 sm:grid-cols-2 gap-1.5">
                    <input type="text" id="reg-new-prod-name" placeholder="Nombre (ej. Salsa Macha Cacahuate)" class="px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">
                    <input type="number" step="0.5" id="reg-new-prod-price" placeholder="Precio ($ ej. 95)" class="px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none font-mono">
                  </div>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-4 gap-1.5">
                  <div class="sm:col-span-2">
                    <input type="text" id="reg-new-prod-desc" placeholder="Descripción breve (ej. Chile tostado artesanal con cacahuate y ajo)" class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">
                  </div>
                  <div>
                    <input type="text" id="reg-new-prod-tag" placeholder="Etiqueta (ej. Salsa picante)" class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">
                  </div>
                  <div>
                    <select id="reg-new-prod-fit" class="w-full px-2 py-1.5 text-xs rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:outline-none">
                      <option value="contain">📐 Altura (Fondo blanco)</option>
                      <option value="cover">🖼️ Rellenar campo (Foto)</option>
                    </select>
                  </div>
                </div>
                <button type="button" onclick="addRegisterFeaturedProduct()" class="w-full py-2 px-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-xs transition-colors flex items-center justify-center gap-1.5">
                  <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                  <span>Agregar a Productos Destacados</span>
                </button>
              </div>

              <!-- Grid de productos añadidos -->
              <div id="reg-featured-grid" class="space-y-2">
                <div class="py-3 text-center text-[11px] text-slate-400">
                  No has agregado productos destacados aún (puedes añadir hasta 10 con foto, precio y descripción).
                </div>
              </div>
            </div>

            <!-- 3. OTROS PRODUCTOS (ESTILO MENÚ SIN FOTO, MÁX. 2 SECCIONES) -->
            <div class="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div class="flex items-center justify-between">
                <div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-xs font-bold text-slate-900">3. Otros Productos / Menú sin Foto</span>
                    <span class="px-1.5 py-0.2 text-[9px] font-black uppercase rounded-md bg-slate-200 text-slate-700 font-mono">Máx. 2 secciones</span>
                  </div>
                  <span class="text-[11px] text-slate-500">Para renglones tipo menú, presentaciones por litro, botanas o complementos sin foto.</span>
                </div>
                <span id="reg-menu-sec-counter-badge" class="px-2 py-0.5 text-[10px] font-black uppercase rounded-full bg-slate-200 text-slate-700 font-mono">0 / 2 secciones</span>
              </div>

              <div class="flex items-center justify-end">
                <button type="button" id="btn-add-menu-section" onclick="addRegisterMenuSection()" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-colors flex items-center gap-1 shadow-xs">
                  <i data-lucide="plus" class="w-3.5 h-3.5 text-emerald-400"></i>
                  <span>+ Añadir Sección de Menú</span>
                </button>
              </div>

              <div id="reg-menu-sections-container" class="space-y-3">
                <div class="p-3 rounded-2xl bg-white border border-dashed border-slate-300 text-center text-[11px] text-slate-400">
                  No has añadido secciones tipo menú. (Opcional, útil para complementos o presentaciones sin foto).
                </div>
              </div>
            </div>
          </div>

          <button type="submit" id="btn-submit-step1" class="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2">
            <span>Continuar a Validación (Paso 1 de 3)</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </form>
      </div>

      <!-- FASE 2: VALIDACIÓN INMEDIATA POR WHATSAPP -->
      <div id="reg-step-2" class="hidden space-y-4">
        <div class="p-3.5 rounded-2xl bg-emerald-50 border border-emerald-100 flex items-start gap-3">
          <i data-lucide="shield-check" class="w-5 h-5 text-emerald-600 shrink-0 mt-0.5"></i>
          <p class="text-xs text-emerald-900 leading-relaxed">
            <strong>Protección Comunitaria:</strong> Validamos tu WhatsApp con 1 solo toque para comprobar tu identidad comercial, proteger a las familias de los cotos y habilitar contacto directo de clientes sin intermediarios.
          </p>
        </div>

        <div class="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-4 text-center">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-emerald-100 text-emerald-700 mx-auto">
            <i data-lucide="message-circle" class="w-6 h-6"></i>
          </div>

          <div>
            <div class="flex items-center justify-center gap-2 mb-1">
              <h4 class="text-sm font-bold text-slate-900">Validación Rápida por WhatsApp</h4>
              <span id="badge-wa-status" class="px-2.5 py-0.5 text-[11px] font-bold rounded-full bg-amber-50 text-amber-700 border border-amber-200">Pendiente</span>
            </div>
            <p class="text-xs text-slate-600 max-w-md mx-auto">
              Toca el botón verde para abrir WhatsApp y enviar tu código de validación <strong id="step2-wa-code-display" class="font-mono text-emerald-700 text-sm">NATURA-XXXX</strong> al canal oficial de Epicentro Natura.
            </p>
          </div>

          <div class="flex flex-col sm:flex-row items-center justify-center gap-2 pt-1">
            <a id="reg-wa-link-btn" href="#" target="_blank" onclick="onWaLinkClicked()" class="w-full sm:w-auto px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-md transition-all active:scale-98">
              <i data-lucide="message-circle" class="w-4 h-4"></i>
              <span>Abrir WhatsApp con mi Código</span>
            </a>
            <button onclick="handleVerifyWhatsappCode()" id="btn-verify-wa" class="w-full sm:w-auto px-5 py-3 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm shrink-0 transition-colors">
              Confirmar Validación
            </button>
          </div>
          <p class="text-[11px] text-slate-400">
            Al tocar el botón de WhatsApp, tu validación quedará activada automáticamente para avanzar.
          </p>
        </div>

        <button id="btn-to-step-3" disabled onclick="goToStep3()" class="w-full py-3.5 px-4 rounded-xl bg-slate-200 text-slate-400 font-bold text-sm cursor-not-allowed transition-all flex items-center justify-center gap-2">
          <span>Continuar a Verificación Oficial (Paso 3 de 3)</span>
          <i data-lucide="arrow-right" class="w-4 h-4"></i>
        </button>
      </div>

      <!-- FASE 3: ACTIVACIÓN Y COBRO (MERCADO PAGO O ASESOR KAM) -->
      <div id="reg-step-3" class="hidden space-y-4">
        <div class="p-5 rounded-2xl bg-gradient-to-br from-amber-500/10 via-emerald-500/5 to-transparent border border-amber-400/30 text-center space-y-3">
          <div class="w-12 h-12 mx-auto rounded-full bg-amber-500/20 text-amber-600 flex items-center justify-center">
            <i data-lucide="award" class="w-6 h-6"></i>
          </div>
          <h4 class="text-lg font-black text-slate-950">Página interactiva en epizentro con catálogo</h4>
          <p class="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
            Obtén tu <strong>página interactiva en epizentro</strong> (con fotos de productos, precios y menú de pedidos directos por WhatsApp).
          </p>

          <div class="py-2">
            <span class="text-3xl font-black text-slate-950 font-mono">$399.00</span>
            <span class="text-xs font-bold text-slate-500 uppercase ml-1">MXN / Suscripción Anual</span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-left text-[11px] text-slate-700 bg-white/80 p-3 rounded-xl border border-slate-200">
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Tu página interactiva en epizentro</div>
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Catálogo hasta 10 Fotos & Precios</div>
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Pedidos Directos a tu WhatsApp</div>
          </div>
        </div>

        <!-- Pasarela Oficial de Pago Seguro Mercado Pago -->
        <div class="space-y-3 p-4 rounded-2xl bg-white border border-slate-200 text-center shadow-xs">
          <button type="button" id="btn-pay-mp" onclick="triggerMercadoPagoPayment()" class="w-full py-4 px-4 rounded-xl bg-[#009ee3] hover:bg-[#0082ba] text-white font-bold text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2">
            <i data-lucide="shield-check" class="w-5 h-5"></i>
            <span>Pagar Suscripción Anual con Mercado Pago ($399 MXN / año)</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
          <p class="text-[11px] text-center text-slate-500 leading-relaxed">
            🔒 Pago seguro procesado directamente en Mercado Pago. Acepta Tarjetas de Crédito, Débito, Transferencia SPEI y Saldo en cuenta. Activación automática e inmediata tras conciliar.
          </p>
        </div>

        <!-- Canjear Código de Cortesía / Invitación -->
        <div class="mt-4 pt-3 border-t border-slate-200">
          <div class="text-left">
            <button type="button" onclick="toggleCouponBox()" class="text-xs font-bold text-slate-600 hover:text-emerald-700 flex items-center justify-between w-full p-2 rounded-xl hover:bg-slate-100 transition-colors">
              <span class="flex items-center gap-1.5"><i data-lucide="tag" class="w-3.5 h-3.5 text-emerald-600"></i> ¿Tienes código de cortesía o invitación?</span>
              <i id="coupon-chevron" data-lucide="chevron-down" class="w-4 h-4 transition-transform"></i>
            </button>
            <div id="coupon-container" class="hidden mt-2 p-3 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <label class="block text-[11px] font-bold text-slate-700">Ingresa tu código de cortesía o pase fundador:</label>
              <div class="flex gap-2">
                <input type="text" id="reg-coupon-code" placeholder="Ej. NATURA100" class="w-full px-3 py-2 text-xs uppercase font-mono tracking-wider font-bold rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-emerald-500">
                <button type="button" onclick="handleApplyCoupon()" id="btn-apply-coupon" class="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shrink-0 transition-colors">
                  Aplicar
                </button>
              </div>
              <p id="coupon-feedback" class="text-[11px] font-bold hidden"></p>
            </div>
          </div>
        </div>

        <!-- DIFERENCIACIÓN DEL REGISTRO GRATUITO BÁSICO -->
        <div class="mt-4 p-4 rounded-2xl bg-slate-50 border border-slate-200 text-left">
          <div class="flex items-start gap-3">
            <div class="w-7 h-7 rounded-xl bg-slate-200 text-slate-600 flex items-center justify-center shrink-0 mt-0.5">
              <i data-lucide="info" class="w-4 h-4"></i>
            </div>
            <div>
              <h5 class="text-xs font-bold text-slate-900">¿Prefieres solo registro básico sin costo?</h5>
              <p class="text-[11px] text-slate-500 mt-1 leading-relaxed">
                El <strong>registro gratuito</strong> incluye únicamente tus datos generales de contacto: <strong>teléfono, WhatsApp, ubicación y horarios</strong> en el directorio. <em>(No incluye página interactiva en epizentro)</em>
              </p>
              <div class="pt-2">
                <button type="button" onclick="skipVerificationPayment()" class="text-xs font-bold text-slate-600 hover:text-emerald-700 underline transition-colors">
                  Continuar con Registro Básico Gratuito ($0) &rarr;
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- FASE 4: CONFIRMACIÓN, PAGO Y VALIDACIÓN DINÁMICA -->
      <div id="reg-step-4" class="hidden text-center py-4">
        <div id="step4-dynamic-content">
          <!-- Inyectado dinámicamente según el estado: pending_payment, verified_success, free_basic -->
        </div>
      </div>

    </div>
    `;
  }

  function ensureModalMounted() {
    let modal = document.getElementById("register-modal");
    if (!modal) {
      modal = document.createElement("div");
      modal.id = "register-modal";
      modal.dataset.version = "v500";
      modal.className = "fixed inset-0 z-50 hidden items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs";
      document.body.appendChild(modal);
    }

    // Si el modal no contiene el stepper completo o carece del botón oficial de Mercado Pago o es versión antigua
    if (!document.getElementById("reg-step-1") || !document.getElementById("btn-pay-mp") || modal.dataset.version !== "v500") {
      modal.innerHTML = renderWizardHTML();
      modal.dataset.version = "v500";
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }
    return modal;
  }

  function syncSubcategoriesDropdown() {
    const catSelect = document.getElementById("reg-category");
    const subSelect = document.getElementById("reg-subcategory");
    if (!catSelect || !subSelect) return;
    const cat = catSelect.value || "comida-delivery";
    const list = SUBCATEGORIES_MAP[cat] || [];
    subSelect.innerHTML = list.map(s => `<option value="${s.slug}">${s.label}</option>`).join("");
  }

  function openRegisterModal(preselectedCat) {
    const modal = ensureModalMounted();
    currentRegId = null;
    waVerified = false;
    currentPaymentMode = "mp";
    registerCoverPhoto = "";
    registerFeaturedProducts = [];
    registerMenuSections = [];
    tempNewProductPhoto = "";
    registerUploadedPhotos = [];
    renderRegisterCoverPreview();
    renderRegisterFeaturedGrid();
    renderRegisterMenuSections();
    setPaymentMode("mp");
    selectRegistrationPlan("microsite");

    // Pre-llenar la categoría detectada
    const detectedCat = detectActiveCategory(preselectedCat);
    const catSelect = document.getElementById("reg-category");
    if (catSelect && detectedCat) {
      const exists = Array.from(catSelect.options).some(o => o.value === detectedCat);
      if (exists) {
        catSelect.value = detectedCat;
      }
    }

    syncSubcategoriesDropdown();
    setWizardStep(1);

    modal.classList.remove("hidden");
    modal.classList.add("flex");
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  function closeRegisterModal() {
    const modal = document.getElementById("register-modal");
    if (modal) {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    }
  }

  function setWizardStep(step) {
    const s1 = document.getElementById("reg-step-1");
    const s2 = document.getElementById("reg-step-2");
    const s3 = document.getElementById("reg-step-3");
    const s4 = document.getElementById("reg-step-4");
    if (s1) s1.classList.toggle("hidden", step !== 1);
    if (s2) s2.classList.toggle("hidden", step !== 2);
    if (s3) s3.classList.toggle("hidden", step !== 3);
    if (s4) s4.classList.toggle("hidden", step !== 4);

    const label = document.getElementById("wizard-step-label");
    const title = document.getElementById("wizard-title");
    const desc = document.getElementById("wizard-desc");
    const bar1 = document.getElementById("step-bar-1");
    const bar2 = document.getElementById("step-bar-2");
    const bar3 = document.getElementById("step-bar-3");
    const isFree = (currentSelectedPlan === "free_basic");

    if (step === 1) {
      if (label) label.textContent = isFree ? "Paso 1 de 2" : "Paso 1 de 3";
      if (title) title.textContent = isFree ? "Alta Básica Comunitaria (Gratis)" : "Registrar Comercio o Servicio";
      if (desc) desc.textContent = isFree ? "Publicación en el directorio con datos de contacto e hipervínculos funcionales." : "Conéctate directamente con las familias de cotos Natura con tu página interactiva y catálogo.";
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-slate-200 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-slate-200 transition-all";
    } else if (step === 2) {
      if (label) label.textContent = isFree ? "Paso 2 de 2" : "Paso 2 de 3";
      if (title) title.textContent = "Validación por WhatsApp";
      if (desc) desc.textContent = "Confirma tu número comercial con 1 toque para proteger la confianza de la comunidad.";
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar3) bar3.className = isFree ? "h-1.5 rounded-full bg-emerald-600 transition-all" : "h-1.5 rounded-full bg-slate-200 transition-all";
    } else if (step === 3) {
      if (label) label.textContent = "Paso 3 de 3";
      if (title) title.textContent = "Suscripción anual por página interactiva";
      if (desc) desc.textContent = "";
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
    } else if (step === 4) {
      if (label) label.textContent = "Completado";
      if (title) title.textContent = isFree ? "¡Registro Básico Gratuito Enviado!" : "Estatus de Registro y Verificación";
      if (desc) desc.textContent = isFree ? "Tu negocio ha sido registrado con datos generales e hipervínculos de contacto." : "Consulta el estado de activación de tu página interactiva en epizentro.";
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
    }
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  async function submitStep1(e) {
    if (e && e.preventDefault) e.preventDefault();
    const btn = document.getElementById("btn-submit-step1");
    const originalText = btn ? btn.innerHTML : "<span>Continuar a Validación (Paso 1 de 3)</span>";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>Generando código seguro...</span>`;
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }

    let timeoutId = null;
    try {
      const hpEl = document.getElementById("reg-honeypot");
      const hp = hpEl ? hpEl.value : "";
      const nameEl = document.getElementById("reg-name");
      currentBusinessName = nameEl ? nameEl.value.trim() : "Mi Negocio";

      const catSelect = document.getElementById("reg-category");
      const subSelect = document.getElementById("reg-subcategory");
      const catSlug = catSelect ? catSelect.value : "comida-delivery";
      const catLabel = (catSelect && catSelect.selectedIndex >= 0 && catSelect.options[catSelect.selectedIndex])
        ? catSelect.options[catSelect.selectedIndex].text
        : "Comida y Delivery";
      const subSlug = (subSelect && subSelect.value) ? subSelect.value : "pizzas-pastas";
      const subLabel = (subSelect && subSelect.selectedIndex >= 0 && subSelect.options[subSelect.selectedIndex])
        ? subSelect.options[subSelect.selectedIndex].text
        : "Pizzas y Pastas";

      const spaceType = document.getElementById("reg-type") ? document.getElementById("reg-type").value : "local-establecido";
      const address = document.getElementById("reg-address") ? document.getElementById("reg-address").value.trim() : "";
      const owner = document.getElementById("reg-owner") ? document.getElementById("reg-owner").value.trim() : "";
      const email = document.getElementById("reg-email") ? document.getElementById("reg-email").value.trim() : "";
      const phone = document.getElementById("reg-phone") ? document.getElementById("reg-phone").value.trim() : "";
      const wa = document.getElementById("reg-wa") ? document.getElementById("reg-wa").value.trim() : "";
      const rawWebsite = document.getElementById("reg-website") ? document.getElementById("reg-website").value.trim() : "";
      const website = (currentSelectedPlan === "microsite") ? (rawWebsite || null) : null;
      const schedule = document.getElementById("reg-schedule") ? document.getElementById("reg-schedule").value.trim() : "Lunes a Sábado · 09:00 a 19:00 hrs";

      // Métodos de contacto preferidos
      const checkedBoxes = Array.from(document.querySelectorAll('input[name="pref_contact"]:checked')).map(el => el.value);
      const prefMethods = checkedBoxes.length > 0 ? checkedBoxes.join(",") : "whatsapp";

      const deliveryChecked = checkedBoxes.includes("delivery") || (document.getElementById("reg-delivery") ? document.getElementById("reg-delivery").checked : false);

      const featuredTitle = document.getElementById("reg-featured-title") ? document.getElementById("reg-featured-title").value.trim() : "Nuestra Selección Destacada";
      const featuredSubtitle = document.getElementById("reg-featured-subtitle") ? document.getElementById("reg-featured-subtitle").value.trim() : "";
      const featuredDesc = document.getElementById("reg-featured-desc") ? document.getElementById("reg-featured-desc").value.trim() : "";

      const micrositeData = {
        cover_photo: registerCoverPhoto || null,
        website_url: website,
        featured_section: {
          title: featuredTitle || "Nuestra Selección Destacada",
          subtitle: featuredSubtitle,
          description: featuredDesc,
          products: registerFeaturedProducts
        },
        other_products_sections: registerMenuSections
      };

      const payload = {
        business_name: currentBusinessName,
        category_slug: catSlug,
        category_label: catLabel,
        subcategory_slug: subSlug,
        subcategory_label: subLabel,
        coto_address: address,
        business_type: spaceType,
        space_label: spaceType === "local-establecido" ? "Punto de venta físico" : "A domicilio en coto / Con previa cita",
        owner_name: owner,
        email: email,
        phone: phone,
        whatsapp: wa,
        schedule: schedule,
        cover_photo: (currentSelectedPlan === "microsite" && registerCoverPhoto) ? registerCoverPhoto : null,
        microsite_data: (currentSelectedPlan === "microsite") ? JSON.stringify(micrositeData) : null,
        photos: (currentSelectedPlan === "microsite" && registerFeaturedProducts.length > 0)
          ? JSON.stringify(registerFeaturedProducts.map(p => p.photo).filter(Boolean))
          : null,
        plan_type: currentSelectedPlan,
        preferred_contact_methods: prefMethods,
        website: website,
        delivery_available: deliveryChecked,
        honeypot: hp
      };

      const controller = new AbortController();
      timeoutId = setTimeout(() => controller.abort(), 6000);

      let data = null;
      try {
        const res = await fetch("/api/epicentro/register/initiate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
          signal: controller.signal
        });
        clearTimeout(timeoutId);

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || "Error al procesar el registro inicial.");
        }
        data = await res.json();
      } catch (fetchErr) {
        clearTimeout(timeoutId);
        console.warn("Aviso en API /api/epicentro/register/initiate (usando fallback seguro):", fetchErr);
      }

      if (data && data.registration_id) {
        currentRegId = data.registration_id;
        const waCodeDisplay = document.getElementById("step2-wa-code-display");
        if (waCodeDisplay) waCodeDisplay.textContent = data.whatsapp_code || "NATURA-XXXX";
        const waLinkBtn = document.getElementById("reg-wa-link-btn");
        if (waLinkBtn) {
          waLinkBtn.href = data.whatsapp_link || `https://wa.me/523336762545?text=Verificar%20${data.whatsapp_code}`;
        }
      } else {
        currentRegId = "mock-" + Date.now();
        const waCodeDisplay = document.getElementById("step2-wa-code-display");
        if (waCodeDisplay) waCodeDisplay.textContent = "NATURA-8321";
        const waLinkBtn = document.getElementById("reg-wa-link-btn");
        if (waLinkBtn) {
          waLinkBtn.href = `https://wa.me/523336762545?text=Hola%20Epicentro%20Natura,%20confirmo%20mi%20negocio%20${encodeURIComponent(currentBusinessName)}%20con%20codigo%20NATURA-8321`;
        }
      }

      setWizardStep(2);
    } catch (err) {
      console.error("Error inesperado en submitStep1:", err);
      setWizardStep(2);
    } finally {
      if (timeoutId) clearTimeout(timeoutId);
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
        if (window.lucide && lucide.createIcons) lucide.createIcons();
      }
    }
  }

  function onWaLinkClicked() {
    setTimeout(() => {
      handleVerifyWhatsappCode();
    }, 800);
  }

  async function handleVerifyWhatsappCode() {
    const btn = document.getElementById("btn-verify-wa");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Validando...";
    }

    const codeVal = document.getElementById("step2-wa-code-display")
      ? document.getElementById("step2-wa-code-display").textContent.trim()
      : "";

    try {
      const res = await fetch("/api/epicentro/register/verify-whatsapp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ registration_id: currentRegId, whatsapp_code: codeVal })
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Error al validar WhatsApp.");
      }
      markWaAsVerified();
    } catch (err) {
      alert("No se pudo validar WhatsApp: " + (err.message || "Por favor verifica que hayas enviado tu código al bot o intenta nuevamente."));
      const btn = document.getElementById("btn-verify-wa");
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Confirmar Validación";
      }
    }
  }

  function markWaAsVerified() {
    waVerified = true;
    const badge = document.getElementById("badge-wa-status");
    if (badge) {
      badge.className = "px-2.5 py-0.5 text-[11px] font-bold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-300";
      badge.textContent = "✓ WhatsApp Validado";
    }
    const btn = document.getElementById("btn-verify-wa");
    if (btn) {
      btn.disabled = true;
      btn.className = "w-full sm:w-auto px-4 py-2.5 rounded-xl bg-emerald-600 text-white font-bold text-xs sm:text-sm shrink-0 cursor-default";
      btn.textContent = "✓ Validado";
    }
    checkCanProceedStep3();
  }

  function checkCanProceedStep3() {
    const btn = document.getElementById("btn-to-step-3");
    if (!btn || !waVerified) return;

    btn.disabled = false;
    if (currentSelectedPlan === "free_basic") {
      btn.className = "w-full py-3.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2 cursor-pointer";
      btn.innerHTML = `<span>Finalizar Registro Básico Gratuito ($0)</span> <i data-lucide="check" class="w-4 h-4 text-emerald-400"></i>`;
      btn.onclick = finishFreeRegistration;
    } else {
      btn.className = "w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2 cursor-pointer";
      btn.innerHTML = `<span>Continuar a Verificación Oficial (Paso 3 de 3)</span> <i data-lucide="arrow-right" class="w-4 h-4"></i>`;
      btn.onclick = goToStep3;
    }
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  async function finishFreeRegistration() {
    const btn = document.getElementById("btn-to-step-3");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>Guardando registro gratuito...</span>`;
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }

    try {
      if (currentRegId && !currentRegId.startsWith("mock-")) {
        await fetch("/api/epicentro/register/report-kam-payment", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            registration_id: currentRegId,
            kam_name: "Registro Básico Gratuito",
            amount: 0.0,
            payment_method: "free_basic",
            notes: "Alta comunitaria básica sin costo (solo textos e hipervínculos: teléfono, WhatsApp, ubicación y horarios)"
          })
        }).catch(e => console.warn("Aviso reporte gratis:", e));
      }
    } catch (e) {
      console.warn(e);
    }

    const folioSuffix = currentRegId ? (currentRegId.includes("-") ? currentRegId.split("-").pop().slice(0, 4).toUpperCase() : currentRegId.slice(-4).toUpperCase()) : Math.floor(1000 + Math.random() * 9000);
    showStep4Success(`NATURA-GRATIS-${folioSuffix}`, {
      title: "¡Registro Básico Gratuito Enviado!",
      desc: "Tu comercio ha sido registrado con datos generales (teléfono, WhatsApp, ubicación y horarios). Podrás activar tu página interactiva en epizentro con catálogo de fotos con la suscripción anual en cualquier momento."
    }, "free_basic");
  }

  function goToStep3() {
    if (!waVerified) {
      alert("Por favor abre WhatsApp con tu código o pulsa 'Confirmar Validación' para continuar.");
      return;
    }
    setWizardStep(3);
  }

  async function triggerMercadoPagoPayment() {
    if (!currentRegId) {
      alert("Por favor completa los pasos anteriores antes de proceder al pago.");
      return;
    }

    const btn = document.getElementById("btn-pay-mp");
    const origText = btn ? btn.innerHTML : "";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>Generando pasarela de pago segura...</span>`;
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }

    try {
      // 1. Solicitar preferencia oficial y trazable a Mercado Pago vinculada al registro
      const res = await fetch("/api/epicentro/register/create-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          registration_id: currentRegId
        })
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "No se pudo generar la pasarela de pago.");
      }

      const checkoutUrl = data.init_point || data.sandbox_init_point;
      if (!checkoutUrl) {
        throw new Error("Mercado Pago no retornó un punto de pago válido.");
      }

      // Guardar reg_id en almacenamiento de sesión para seguimiento
      try {
        sessionStorage.setItem("last_epicentro_reg_id", currentRegId);
      } catch (e) {}

      // Redirigir directamente al checkout seguro de Mercado Pago
      window.location.href = checkoutUrl;
    } catch (err) {
      console.error("Error iniciando pago en Mercado Pago:", err);
      alert("Error al inicializar Mercado Pago: " + (err.message || "Por favor intenta nuevamente."));
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origText;
        if (window.lucide && lucide.createIcons) lucide.createIcons();
      }
    }
  }

  async function skipVerificationPayment() {
    const ok = confirm("¿Confirmas tu registro básico gratuito?\n\nImportante: Tu negocio aparecerá en el directorio comunitario con tus datos generales (teléfono, WhatsApp, ubicación y horarios), pero NO incluye página interactiva en epizentro.");
    if (!ok) return;

    try {
      if (currentRegId && !currentRegId.startsWith("mock-")) {
        await fetch("/api/epicentro/register/report-kam-payment", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            registration_id: currentRegId,
            kam_name: "Registro Básico Gratuito",
            amount: 0.0,
            payment_method: "free_basic",
            notes: "Alta básica sin costo (solo teléfono, whatsapp, ubicación y horarios; sin página interactiva)"
          })
        }).catch(e => console.warn("Aviso reporte gratis:", e));
      }
    } catch (e) {
      console.warn(e);
    }

    const suffix = currentRegId ? (currentRegId.includes("-") ? currentRegId.split("-").pop().slice(0, 4).toUpperCase() : currentRegId.slice(-4).toUpperCase()) : Math.floor(1000 + Math.random() * 9000);
    showStep4Success(`NATURA-GRATIS-${suffix}`, {
      title: "¡Registro Básico Gratuito Enviado!",
      desc: "Tu comercio ha sido registrado con datos generales (teléfono, WhatsApp, ubicación y horarios). Podrás activar tu página interactiva en epizentro y fotos con la suscripción anual en cualquier momento."
    }, "free_basic");
  }

  function toggleCouponBox() {
    const container = document.getElementById("coupon-container");
    const chevron = document.getElementById("coupon-chevron");
    if (!container) return;
    const isHidden = container.classList.contains("hidden");
    container.classList.toggle("hidden", !isHidden);
    if (chevron) {
      chevron.style.transform = isHidden ? "rotate(180deg)" : "rotate(0deg)";
    }
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  async function handleApplyCoupon() {
    const input = document.getElementById("reg-coupon-code");
    const btn = document.getElementById("btn-apply-coupon");
    const feedback = document.getElementById("coupon-feedback");
    const codeVal = input ? input.value.trim().toUpperCase() : "";

    if (!codeVal) {
      if (feedback) {
        feedback.className = "text-[11px] font-bold text-rose-600 block";
        feedback.textContent = "Por favor ingresa un código de cortesía.";
      }
      return;
    }

    if (btn) {
      btn.disabled = true;
      btn.textContent = "Validando...";
    }

    try {
      const res = await fetch("/api/epicentro/register/apply-coupon", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          registration_id: currentRegId,
          coupon_code: codeVal
        })
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "Código de cortesía inválido o expirado.");
      }

      if (feedback) {
        feedback.className = "text-[11px] font-bold text-emerald-700 block";
        feedback.textContent = "✓ ¡Código válido! Tu negocio ha sido verificado con Sello Oficial.";
      }

      setTimeout(() => {
        showStep4Success(data.folio || `NATURA-VERIFIED-${codeVal}`, {
          title: "¡Comercio Verificado con Cortesía!",
          desc: "Tu código de cortesía ha sido validado exitosamente. Tu comercio cuenta con su Página interactiva en epizentro con catálogo."
        }, "verified_success");
      }, 700);
    } catch (err) {
      if (currentRegId && currentRegId.startsWith("mock-") && ["NATURA100", "FUNDADOR", "EPICENTRO2026", "HIPHA"].includes(codeVal)) {
        if (feedback) {
          feedback.className = "text-[11px] font-bold text-emerald-700 block";
          feedback.textContent = "✓ ¡Código válido! Tu negocio ha sido verificado sin costo.";
        }
        setTimeout(() => {
          showStep4Success(`NATURA-PROMO-${codeVal}`, {
            title: "¡Comercio Verificado con Cortesía!",
            desc: "Tu código promocional ha sido aceptado. Tu comercio cuenta con su Página interactiva en epizentro con catálogo."
          }, "verified_success");
        }, 700);
      } else {
        if (feedback) {
          feedback.className = "text-[11px] font-bold text-rose-600 block";
          feedback.textContent = err.message || "Código inválido o expirado.";
        }
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Aplicar";
        }
      }
    }
  }

  function renderStep4Content(mode, folio, customTexts) {
    const bName = currentBusinessName || "tu negocio";
    const container = document.getElementById("step4-dynamic-content");
    if (!container) return;

    if (mode === "pending_payment") {
      const waMsg = encodeURIComponent(`Hola Hipha / Epicentro Natura, inicié mi suscripción anual para "${bName}" con folio ${folio}. Adjunto mi comprobante para activar mi página interactiva en epizentro con catálogo.`);
      const waLink = `https://wa.me/523336762545?text=${waMsg}`;

      container.innerHTML = `
        <div class="space-y-4 max-w-md mx-auto">
          <div class="w-16 h-16 mx-auto rounded-full bg-amber-100 text-amber-600 flex items-center justify-center shadow-inner">
            <i data-lucide="clock" class="w-9 h-9 animate-pulse"></i>
          </div>

          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-[11px] font-bold">
            <span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
            Pendiente de Acreditación · Validación Requerida
          </div>

          <h4 class="text-xl font-black text-slate-950">${(customTexts && customTexts.title) ? customTexts.title : "¡Completando Pago en Mercado Pago!"}</h4>
          
          <p class="text-xs text-slate-600 max-w-sm mx-auto leading-relaxed">
            ${(customTexts && customTexts.desc) ? customTexts.desc : `Hemos registrado tu solicitud para <strong class="text-slate-900">${bName}</strong>. Para activar tu <strong>página interactiva en epizentro con catálogo</strong>, completa tu suscripción anual de <strong>$399 MXN</strong> en Mercado Pago.`}
          </p>

          <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 max-w-xs mx-auto space-y-1">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Folio de Seguimiento</span>
            <span class="text-base font-mono font-black text-amber-600">${folio}</span>
          </div>

          <!-- Acciones de Validación -->
          <div class="space-y-2.5 max-w-sm mx-auto pt-1">
            <a href="${waLink}" target="_blank" rel="noopener noreferrer" class="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs sm:text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2 cursor-pointer no-underline">
              <i data-lucide="message-circle" class="w-4 h-4"></i>
              <span>Ya realicé mi pago · Validar por WhatsApp</span>
            </a>

            <button type="button" id="btn-check-status" onclick="checkCurrentRegistrationStatus()" class="w-full py-2.5 px-4 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 font-bold text-xs shadow-xs transition-all flex items-center justify-center gap-2 cursor-pointer">
              <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-slate-400"></i>
              <span id="btn-check-status-text">Verificar Estatus de Acreditación</span>
            </button>
            <p id="check-status-feedback" class="text-[11px] text-slate-500 hidden text-center px-2 leading-relaxed"></p>

            <div class="pt-1">
              <a href="https://mpago.la/2jXGN6C" target="_blank" rel="noopener noreferrer" class="text-[11px] font-semibold text-slate-500 hover:text-emerald-700 underline transition-colors">
                ¿No abrió la ventana? Reabrir pasarela de Mercado Pago ($399 MXN) &rarr;
              </a>
            </div>
          </div>

          <div class="pt-3 border-t border-slate-100">
            <button onclick="closeRegisterModal();" class="text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors">
              Cerrar y continuar navegando
            </button>
          </div>
        </div>
      `;
    } else if (mode === "free_basic") {
      container.innerHTML = `
        <div class="space-y-4 max-w-md mx-auto">
          <div class="w-16 h-16 mx-auto rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
            <i data-lucide="clipboard-check" class="w-9 h-9"></i>
          </div>

          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-800 text-[11px] font-bold">
            <i data-lucide="check" class="w-3.5 h-3.5"></i>
            Alta Básica Comunitaria Recibida
          </div>

          <h4 class="text-xl font-black text-slate-950">${(customTexts && customTexts.title) ? customTexts.title : "¡Registro Básico Gratuito Enviado!"}</h4>
          
          <p class="text-xs text-slate-600 max-w-sm mx-auto leading-relaxed">
            Tu comercio <strong class="text-slate-900">${bName}</strong> ha sido registrado con sus datos generales (teléfono, WhatsApp, ubicación y horarios).
          </p>

          <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 max-w-xs mx-auto">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Folio de Registro Básico</span>
            <span class="text-base font-mono font-black text-blue-600">${folio}</span>
          </div>

          <p class="text-xs text-slate-500 max-w-xs mx-auto">
            ${(customTexts && customTexts.desc) ? customTexts.desc : "Podrás activar tu página interactiva en epizentro con catálogo con la suscripción anual ($399 MXN) en cualquier momento."}
          </p>

          <button onclick="closeRegisterModal(); location.reload();" class="w-full py-3.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm">
            Entendido, Ver en el Directorio
          </button>
        </div>
      `;
    } else {
      // verified_success (acreditado, cupón verificado, o validación completada)
      container.innerHTML = `
        <div class="space-y-4 max-w-md mx-auto">
          <div class="w-16 h-16 mx-auto rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
            <i data-lucide="check-circle-2" class="w-9 h-9"></i>
          </div>

          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold">
            <i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-600"></i>
            Comercio Verificado con Éxito
          </div>

          <h4 class="text-xl font-black text-slate-950">${(customTexts && customTexts.title) ? customTexts.title : "¡Comercio Verificado con Éxito!"}</h4>
          
          <p class="text-xs text-slate-600 max-w-sm mx-auto leading-relaxed">
            Tu comercio <strong class="text-slate-900">${bName}</strong> cuenta con su Página interactiva en epizentro con catálogo.
          </p>

          <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 max-w-xs mx-auto">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Folio de Verificación</span>
            <span class="text-base font-mono font-black text-emerald-600">${folio}</span>
          </div>

          <p class="text-xs text-slate-500 max-w-xs mx-auto">
            ${(customTexts && customTexts.desc) ? customTexts.desc : "Tu negocio ya se encuentra registrado y activo en el directorio comunitario con su página interactiva en epizentro."}
          </p>

          <button onclick="closeRegisterModal(); location.reload();" class="w-full py-3.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm">
            Entendido, Ver en el Directorio
          </button>
        </div>
      `;
    }

    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  async function checkCurrentRegistrationStatus() {
    const btn = document.getElementById("btn-check-status");
    const textEl = document.getElementById("btn-check-status-text");
    const feedback = document.getElementById("check-status-feedback");

    if (!currentRegId) {
      if (feedback) {
        feedback.className = "text-[11px] text-amber-700 block text-center";
        feedback.textContent = "No hay un registro activo en esta sesión para consultar.";
        feedback.classList.remove("hidden");
      }
      return;
    }

    if (btn) btn.disabled = true;
    if (textEl) textEl.textContent = "Consultando...";

    try {
      const res = await fetch(`/api/epicentro/register/status/${currentRegId}`);
      if (!res.ok) throw new Error("Aún no se refleja la acreditación.");
      const data = await res.json();

      if (data.is_verified_badge || data.status === "active" || data.payment_status === "approved" || data.payment_status === "verified") {
        if (feedback) {
          feedback.className = "text-[11px] text-emerald-700 font-bold block text-center";
          feedback.textContent = "✓ ¡Acreditación confirmada! Mostrando Comercio Verificado...";
          feedback.classList.remove("hidden");
        }
        setTimeout(() => {
          showStep4Success(data.folio || `NATURA-VERIFIED-${currentRegId.slice(-4).toUpperCase()}`, {
            title: "¡Comercio Verificado con Éxito!",
            desc: "Tu pago ha sido acreditado. Tu comercio cuenta con su Página interactiva en epizentro con catálogo activo."
          }, "verified_success");
        }, 800);
      } else {
        if (feedback) {
          feedback.className = "text-[11px] text-slate-600 block text-center leading-relaxed";
          feedback.textContent = "Tu pago sigue en proceso de acreditación. Si ya completaste tu pago en Mercado Pago, pulsa el botón de WhatsApp para adjuntar tu comprobante y agilizar la activación inmediata.";
          feedback.classList.remove("hidden");
        }
      }
    } catch (err) {
      if (feedback) {
        feedback.className = "text-[11px] text-slate-600 block text-center leading-relaxed";
        feedback.textContent = "Tu pago sigue en proceso de acreditación bancaria. Puedes enviar tu comprobante por WhatsApp para validación inmediata con un moderador.";
        feedback.classList.remove("hidden");
      }
    } finally {
      if (btn) btn.disabled = false;
      if (textEl) textEl.textContent = "Verificar Estatus de Acreditación";
    }
  }

  function showStep4Success(folio, customTexts, mode = "verified_success") {
    renderStep4Content(mode, folio, customTexts);
    setWizardStep(4);
  }

  // Exportar funciones y estado al ámbito global
  window.SUBCATEGORIES_MAP = SUBCATEGORIES_MAP;
  window.openRegisterModal = openRegisterModal;
  window.closeRegisterModal = closeRegisterModal;
  window.setWizardStep = setWizardStep;
  window.submitStep1 = submitStep1;
  window.syncSubcategoriesDropdown = syncSubcategoriesDropdown;
  window.onWaLinkClicked = onWaLinkClicked;
  window.handleVerifyWhatsappCode = handleVerifyWhatsappCode;
  window.goToStep3 = goToStep3;
  window.triggerMercadoPagoPayment = triggerMercadoPagoPayment;
  window.skipVerificationPayment = skipVerificationPayment;
  window.toggleCouponBox = toggleCouponBox;
  window.handleApplyCoupon = handleApplyCoupon;
  window.showStep4Success = showStep4Success;
  window.renderStep4Content = renderStep4Content;
  window.checkCurrentRegistrationStatus = checkCurrentRegistrationStatus;
  window.handleRegisterPhotoFiles = handleRegisterPhotoFiles;
  window.promptRegisterPhotoUrl = promptRegisterPhotoUrl;
  window.removeRegisterPhoto = removeRegisterPhoto;
  window.renderRegisterPhotosGrid = renderRegisterPhotosGrid;
  window.handleRegisterCoverFile = handleRegisterCoverFile;
  window.promptRegisterCoverUrl = promptRegisterCoverUrl;
  window.removeRegisterCoverPhoto = removeRegisterCoverPhoto;
  window.handleNewProdPhotoFile = handleNewProdPhotoFile;
  window.promptNewProdPhotoUrl = promptNewProdPhotoUrl;
  window.removeNewProdPhoto = removeNewProdPhoto;
  window.addRegisterFeaturedProduct = addRegisterFeaturedProduct;
  window.removeRegisterFeaturedProduct = removeRegisterFeaturedProduct;
  window.editRegisterProductTag = editRegisterProductTag;
  window.toggleRegisterProductFit = toggleRegisterProductFit;
  window.addRegisterMenuSection = addRegisterMenuSection;
  window.removeRegisterMenuSection = removeRegisterMenuSection;
  window.updateMenuSecMeta = updateMenuSecMeta;
  window.addRegisterMenuItem = addRegisterMenuItem;
  window.removeRegisterMenuItem = removeRegisterMenuItem;
  window.setPaymentMode = setPaymentMode;
  window.selectRegistrationPlan = selectRegistrationPlan;
  window.finishFreeRegistration = finishFreeRegistration;

  function checkUrlAutoOpen() {
    try {
      const urlParams = new URLSearchParams(window.location.search);

      // Detección de retorno de pasarela con pago aprobado
      const paymentReturn = urlParams.get("payment") || urlParams.get("collection_status") || urlParams.get("status");
      const regIdParam = urlParams.get("reg_id") || urlParams.get("external_reference");
      if (paymentReturn === "success" || paymentReturn === "approved") {
        openRegisterModal();
        if (regIdParam) currentRegId = regIdParam;
        showStep4Success(regIdParam ? `NATURA-VERIFIED-${regIdParam.slice(-4).toUpperCase()}` : "NATURA-VERIFIED-OK", {
          title: "¡Pago Acreditado con Éxito!",
          desc: "Tu suscripción anual está activa. Tu página interactiva en epizentro y catálogo ya están habilitados en el directorio comunitario."
        }, "verified_success");
        return;
      }

      if (urlParams.get("open_register") === "1") {
        openRegisterModal(urlParams.get("cat"));
        const step = parseInt(urlParams.get("step") || "1", 10);
        if (step > 1 && step <= 4) {
          if (step >= 2) waVerified = true;
          setWizardStep(step);
        }
      }
    } catch (e) {}
  }

  // Auto-inicializar si el DOM ya cargó o cuando termine de cargar
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      ensureModalMounted();
      syncSubcategoriesDropdown();
      checkUrlAutoOpen();
    });
  } else {
    ensureModalMounted();
    syncSubcategoriesDropdown();
    checkUrlAutoOpen();
  }
})();
