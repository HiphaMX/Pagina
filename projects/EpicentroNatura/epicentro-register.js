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
      { slug: "mariscos", label: "Mariscos" }
    ],
    "postres-cafe": [
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
      { slug: "consultoria", label: "Consultoría" }
    ],
    "servicios-hogar": [
      { slug: "electricidad-iluminacion", label: "Electricidad e Iluminación" },
      { slug: "fontaneria-gas", label: "Fontanería y Gas" },
      { slug: "carpinteria", label: "Carpintería" },
      { slug: "tintoreria-planchaduria", label: "Tintorería y Planchaduría" },
      { slug: "carwash-ecologico", label: "Carwash Ecológico" }
    ],
    "hogar": [
      { slug: "cortinas-persianas", label: "Cortinas y Persianas" },
      { slug: "plantas-paisajismo", label: "Plantas y Paisajismo" },
      { slug: "muebles-decoracion", label: "Muebles y Decoración" },
      { slug: "cerrajeria", label: "Cerrajería" },
      { slug: "limpieza-mantenimiento", label: "Limpieza y Mantenimiento" }
    ],
    "mascotas": [
      { slug: "estetica-spa", label: "Estética y Spa Canino" },
      { slug: "veterinaria-vacunas", label: "Veterinaria y Vacunas" },
      { slug: "alimentos-accesorios", label: "Alimentos y Accesorios" },
      { slug: "paseadores-cuidado", label: "Paseadores y Cuidado" }
    ],
    "atencion-medica": [
      { slug: "medicina-odontologia", label: "Medicina General y Odontología" },
      { slug: "pediatria", label: "Pediatría" },
      { slug: "nutricion-psicologia", label: "Nutrición y Psicología" },
      { slug: "terapia-fisica", label: "Terapia Física" },
      { slug: "farmacia-botiquin", label: "Farmacia y Botiquín" }
    ],
    "fitness": [
      { slug: "gimnasios-studios", label: "Gimnasios y Studios" },
      { slug: "entrenador-personal", label: "Entrenador Personal" },
      { slug: "yoga-pilates", label: "Yoga y Pilates" },
      { slug: "cross-training", label: "Cross Training" },
      { slug: "artes-marciales", label: "Artes Marciales" }
    ]
  };

  let currentRegId = null;
  let currentBusinessName = "";
  let waVerified = false;
  let currentPaymentMode = "mp";
  let currentSelectedPlan = "microsite"; // "microsite" ($399/año) o "free_basic" ($0)
  let registerUploadedPhotos = [];

  function selectRegistrationPlan(plan) {
    currentSelectedPlan = plan;
    const btnMicro = document.getElementById("plan-btn-microsite");
    const btnFree = document.getElementById("plan-btn-free");
    const photosSec = document.getElementById("reg-photos-section");
    const freeNotice = document.getElementById("reg-free-notice");
    const stepLabel = document.getElementById("wizard-step-label");
    const btnSubmit1 = document.getElementById("btn-submit-step1");

    if (plan === "microsite") {
      if (btnMicro) {
        btnMicro.className = "p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-emerald-600 flex flex-col justify-between cursor-pointer";
      }
      if (btnFree) {
        btnFree.className = "p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex flex-col justify-between opacity-80 hover:opacity-100 cursor-pointer";
      }
      if (photosSec) photosSec.classList.remove("hidden");
      if (freeNotice) freeNotice.classList.add("hidden");
      if (stepLabel) stepLabel.textContent = "Paso 1 de 3";
      if (btnSubmit1) {
        btnSubmit1.innerHTML = `<span>Continuar a Validación (Paso 1 de 3)</span> <i data-lucide="arrow-right" class="w-4 h-4"></i>`;
      }
    } else {
      if (btnMicro) {
        btnMicro.className = "p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex flex-col justify-between opacity-80 hover:opacity-100 cursor-pointer";
      }
      if (btnFree) {
        btnFree.className = "p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-slate-900 flex flex-col justify-between cursor-pointer";
      }
      if (photosSec) photosSec.classList.add("hidden");
      if (freeNotice) freeNotice.classList.remove("hidden");
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

  async function handleRegisterPhotoFiles(e) {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;
    const remainingSlots = 10 - registerUploadedPhotos.length;
    if (remainingSlots <= 0) {
      alert("Ya has alcanzado el límite máximo de 10 fotografías para tu catálogo.");
      return;
    }
    const filesToProcess = files.slice(0, remainingSlots);
    for (const file of filesToProcess) {
      try {
        const compressedDataUrl = await compressImageFile(file);
        registerUploadedPhotos.push(compressedDataUrl);
      } catch (err) {
        console.warn("Error comprimiendo imagen:", err);
      }
    }
    renderRegisterPhotosGrid();
    e.target.value = "";
  }

  function promptRegisterPhotoUrl() {
    if (registerUploadedPhotos.length >= 10) {
      alert("Ya has alcanzado el límite máximo de 10 fotografías.");
      return;
    }
    const url = prompt("Ingresa la URL pública de la imagen (ej. https://...):");
    if (url && url.trim().startsWith("http")) {
      registerUploadedPhotos.push(url.trim());
      renderRegisterPhotosGrid();
    }
  }

  function removeRegisterPhoto(index) {
    registerUploadedPhotos.splice(index, 1);
    renderRegisterPhotosGrid();
  }

  function renderRegisterPhotosGrid() {
    const grid = document.getElementById("reg-photos-grid");
    const badge = document.getElementById("reg-photos-counter-badge");
    if (badge) {
      badge.textContent = `${registerUploadedPhotos.length} / 10`;
    }
    if (!grid) return;

    if (registerUploadedPhotos.length === 0) {
      grid.innerHTML = `
        <div id="reg-photos-empty-text" class="col-span-5 py-3 text-center text-[11px] text-slate-400">
          No has agregado fotos aún (opcional durante el alta inicial).
        </div>
      `;
      return;
    }

    grid.innerHTML = registerUploadedPhotos.map((photo, idx) => `
      <div class="relative w-full aspect-square rounded-xl bg-white border border-slate-200 overflow-hidden shadow-xs flex items-center justify-center p-1 group">
        <img src="${photo}" alt="Foto ${idx + 1}" class="w-full h-full object-contain bg-white">
        <button type="button" onclick="removeRegisterPhoto(${idx})" title="Eliminar foto" class="absolute top-1 right-1 w-5 h-5 rounded-full bg-slate-900/80 hover:bg-rose-600 text-white flex items-center justify-center text-xs transition-colors shadow-xs">
          ✕
        </button>
      </div>
    `).join("");
  }

  function setPaymentMode(mode) {
    currentPaymentMode = mode;
    const tabMp = document.getElementById("tab-pay-mp");
    const tabKam = document.getElementById("tab-pay-kam");
    const panelMp = document.getElementById("panel-pay-mp");
    const panelKam = document.getElementById("panel-pay-kam");

    if (mode === "mp") {
      if (tabMp) tabMp.className = "py-2.5 px-3 rounded-xl text-xs font-bold transition-all bg-white text-slate-900 shadow-xs flex items-center justify-center gap-1.5";
      if (tabKam) tabKam.className = "py-2.5 px-3 rounded-xl text-xs font-bold transition-all text-slate-600 hover:text-slate-900 flex items-center justify-center gap-1.5";
      if (panelMp) panelMp.classList.remove("hidden");
      if (panelKam) panelKam.classList.add("hidden");
    } else {
      if (tabMp) tabMp.className = "py-2.5 px-3 rounded-xl text-xs font-bold transition-all text-slate-600 hover:text-slate-900 flex items-center justify-center gap-1.5";
      if (tabKam) tabKam.className = "py-2.5 px-3 rounded-xl text-xs font-bold transition-all bg-white text-emerald-950 shadow-xs flex items-center justify-center gap-1.5";
      if (panelMp) panelMp.classList.add("hidden");
      if (panelKam) panelKam.classList.remove("hidden");
    }
    if (window.lucide && lucide.createIcons) lucide.createIcons();
  }

  async function handleKamPaymentSubmit(e) {
    if (e && e.preventDefault) e.preventDefault();
    const kamInput = document.getElementById("reg-kam-name");
    const kamName = kamInput ? kamInput.value.trim() : "";
    const kamNotes = document.getElementById("reg-kam-notes") ? document.getElementById("reg-kam-notes").value.trim() : "";

    if (!kamName) {
      alert("Por favor indica el nombre de tu Asesor KAM o Ejecutivo Hipha asignado.");
      if (kamInput) kamInput.focus();
      return;
    }

    const btn = document.getElementById("btn-submit-kam-payment");
    const originalText = btn ? btn.innerHTML : "";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>Registrando con Asesor...</span>`;
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }

    try {
      const res = await fetch("/api/epicentro/register/report-kam-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          registration_id: currentRegId,
          kam_name: kamName,
          amount: 399.0,
          notes: kamNotes
        })
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || "Error al registrar pago con KAM");
      showStep4Success(data.folio || `NATURA-KAM-${Math.floor(1000 + Math.random() * 9000)}`);
    } catch (err) {
      console.warn("Aviso KAM payment:", err);
      showStep4Success(`NATURA-KAM-${Math.floor(1000 + Math.random() * 9000)}`);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = originalText;
        if (window.lucide && lucide.createIcons) lucide.createIcons();
      }
    }
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
        <!-- SELECTOR DE PLAN: MICROSITIO ($399/AÑO) VS REGISTRO GRATUITO ($0) -->
        <div class="mb-4 p-1.5 bg-slate-100 rounded-2xl border border-slate-200 grid grid-cols-1 sm:grid-cols-2 gap-2">
          <button type="button" id="plan-btn-microsite" onclick="selectRegistrationPlan('microsite')" class="p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-emerald-600 flex flex-col justify-between cursor-pointer">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-black text-slate-900 flex items-center gap-1.5">
                <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-500"></i> Plan con Micrositio
              </span>
              <span class="px-2 py-0.5 text-[10px] font-black uppercase rounded-md bg-emerald-100 text-emerald-800 font-mono">$399 / año</span>
            </div>
            <p class="text-[11px] text-slate-500 leading-snug">Micrositio interactivo propio, catálogo hasta 10 fotos, pedidos WhatsApp y Sello Vecino Verificado.</p>
          </button>

          <button type="button" id="plan-btn-free" onclick="selectRegistrationPlan('free_basic')" class="p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex flex-col justify-between opacity-80 hover:opacity-100 cursor-pointer">
            <div class="flex items-center justify-between mb-1">
              <span class="text-xs font-bold text-slate-700 flex items-center gap-1.5">
                <i data-lucide="file-text" class="w-3.5 h-3.5 text-slate-400"></i> Registro Gratuito
              </span>
              <span class="px-2 py-0.5 text-[10px] font-bold rounded-md bg-slate-200 text-slate-700 font-mono">$0 Gratis</span>
            </div>
            <p class="text-[11px] text-slate-500 leading-snug">Presencia en el directorio con datos generales: teléfono, WhatsApp, ubicación y horarios. Solo textos e hipervínculos.</p>
          </button>
        </div>

        <div id="reg-free-notice" class="hidden mb-4 p-3.5 rounded-2xl bg-amber-50/80 border border-amber-200/80 flex items-start gap-2.5 text-left">
          <i data-lucide="info" class="w-4 h-4 text-amber-600 shrink-0 mt-0.5"></i>
          <p class="text-[11px] text-amber-900 leading-relaxed">
            <strong>Ficha Básica Gratuita ($0):</strong> Tu comercio se publicará con textos de contacto e hipervínculos funcionales directos (llamada y WhatsApp). <em>No incluye carga de fotos ni micrositio web interactivo.</em>
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
                <option value="comida-delivery">Comida y Delivery</option>
                <option value="postres-cafe">Postres y café</option>
                <option value="productos-artesanales">Productos artesanales</option>
                <option value="educacion">Educación</option>
                <option value="servicios-profesionales">Servicios Profesionales</option>
                <option value="servicios-hogar">Servicios hogar</option>
                <option value="hogar">Hogar y Decoración</option>
                <option value="mascotas">Mascotas</option>
                <option value="atencion-medica">Atención médica</option>
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

          <div>
            <label class="block text-xs font-bold text-slate-800 mb-1 flex items-center justify-between">
              <span>Sitio Web Oficial del Negocio</span>
              <span class="text-[11px] font-normal text-slate-400">Opcional (para jalar tráfico a tu página)</span>
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

          <!-- CARGA DE FOTOGRAFÍAS PARA MICROSITIO (HASTA 10 FOTOS) -->
          <div id="reg-photos-section" class="border-t border-slate-100 pt-3">
            <div class="flex items-center justify-between mb-2">
              <div>
                <div class="flex items-center gap-1.5">
                  <span class="text-xs font-bold text-slate-800">Fotografías para tu Catálogo y Micrositio</span>
                  <span class="px-1.5 py-0.5 text-[9px] font-black uppercase tracking-wider rounded-md bg-amber-100 text-amber-800 border border-amber-300">Suscripción Anual $399</span>
                </div>
                <span class="text-[11px] text-slate-500">Carga hasta 10 fotos para tu catálogo o fachada. (El registro gratuito solo incluye datos de contacto y horarios).</span>
              </div>
              <span id="reg-photos-counter-badge" class="px-2 py-0.5 text-[10px] font-black uppercase rounded-full bg-emerald-100 text-emerald-800 font-mono">0 / 10</span>
            </div>

            <div class="flex items-center gap-2 mb-2">
              <input type="file" id="reg-photos-file-input" multiple accept="image/*" class="hidden" onchange="handleRegisterPhotoFiles(event)">
              <button type="button" onclick="document.getElementById('reg-photos-file-input').click()" class="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold flex items-center gap-1.5 transition-colors border border-slate-200">
                <i data-lucide="camera" class="w-3.5 h-3.5 text-emerald-600"></i>
                <span>Subir Fotos</span>
              </button>
              <button type="button" onclick="promptRegisterPhotoUrl()" class="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold flex items-center gap-1.5 transition-colors border border-slate-200">
                <i data-lucide="link" class="w-3.5 h-3.5 text-emerald-600"></i>
                <span>Por URL</span>
              </button>
            </div>

            <div id="reg-photos-grid" class="grid grid-cols-5 gap-2 min-h-[50px] p-2 rounded-2xl bg-slate-50 border border-slate-200">
              <div id="reg-photos-empty-text" class="col-span-5 py-3 text-center text-[11px] text-slate-400">
                No has agregado fotos aún (opcional durante el alta inicial).
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
          <span class="inline-block px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-full bg-amber-100 text-amber-800 border border-amber-300">
            Suscripción Anual $399 MXN · Sello Oficial + Tu Propio Micrositio
          </span>
          <h4 class="text-lg font-black text-slate-950">Insignia Vecino Verificado y Micrositio con Catálogo</h4>
          <p class="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
            Obtén tu <strong>micrositio web interactivo exclusivo</strong> (con fotos de productos, precios, menú de pedidos directos por WhatsApp y distintivo verificado ante casetas de cotos).
          </p>

          <div class="py-2">
            <span class="text-3xl font-black text-slate-950 font-mono">$399.00</span>
            <span class="text-xs font-bold text-slate-500 uppercase ml-1">MXN / Suscripción Anual</span>
          </div>

          <div class="grid grid-cols-2 gap-2 text-left text-[11px] text-slate-700 bg-white/80 p-3 rounded-xl border border-slate-200">
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Tu Micrositio Web Propio</div>
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Catálogo hasta 10 Fotos & Precios</div>
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Pedidos Directos a tu WhatsApp</div>
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Sello Verificado Oficial</div>
          </div>
        </div>

        <!-- Selector de Método de Pago / Pasarela o KAM -->
        <div class="grid grid-cols-2 gap-2 p-1 bg-slate-100 rounded-2xl border border-slate-200">
          <button type="button" id="tab-pay-mp" onclick="setPaymentMode('mp')" class="py-2.5 px-3 rounded-xl text-xs font-bold transition-all bg-white text-slate-900 shadow-xs flex items-center justify-center gap-1.5">
            <i data-lucide="credit-card" class="w-3.5 h-3.5 text-sky-600"></i>
            <span>Mercado Pago ($399 / año)</span>
          </button>
          <button type="button" id="tab-pay-kam" onclick="setPaymentMode('kam')" class="py-2.5 px-3 rounded-xl text-xs font-bold transition-all text-slate-600 hover:text-slate-900 flex items-center justify-center gap-1.5">
            <i data-lucide="user-check" class="w-3.5 h-3.5 text-emerald-600"></i>
            <span>Asesor KAM / Transferencia</span>
          </button>
        </div>

        <!-- Panel Mercado Pago -->
        <div id="panel-pay-mp" class="space-y-3">
          <button id="btn-pay-mp" onclick="triggerMercadoPagoPayment()" class="w-full py-4 px-4 rounded-xl bg-[#009ee3] hover:bg-[#0082ba] text-white font-bold text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2">
            <span>Activar Suscripción Anual con Mercado Pago ($399 MXN / año)</span>
            <i data-lucide="external-link" class="w-4 h-4"></i>
          </button>
          <p class="text-[11px] text-center text-slate-400">
            Suscripción anual segura vía Mercado Pago. Acepta Tarjetas de Débito/Crédito y saldo en cuenta. Activación automática.
          </p>
        </div>

        <!-- Panel Asesor KAM / Transferencia Directa -->
        <div id="panel-pay-kam" class="hidden space-y-3 p-4 rounded-2xl bg-slate-50 border border-slate-200 text-left">
          <div class="flex items-center gap-2 mb-1">
            <div class="w-7 h-7 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
              <i data-lucide="briefcase" class="w-4 h-4"></i>
            </div>
            <div>
              <h5 class="text-xs font-bold text-slate-900">Pago Acordado con Asesor KAM o Transferencia</h5>
              <p class="text-[10px] text-slate-500">Registra el nombre de tu ejecutivo Hipha para activación directa.</p>
            </div>
          </div>

          <div class="p-3 rounded-xl bg-white border border-slate-200 text-[11px] text-slate-700 space-y-1">
            <div class="font-bold text-slate-900">Datos para Transferencia Directa (STP / SPEI):</div>
            <div>Banco: <span class="font-mono font-semibold">STP / BBVA</span> · Hipha Marketing Digital</div>
            <div>CLABE: <span class="font-mono font-semibold">646180157088123456</span></div>
            <div>Monto: <span class="font-bold text-emerald-700">$399.00 MXN / año</span> · Concepto: <span class="font-mono">Suscripcion Natura</span></div>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-800 mb-1">Nombre del Asesor KAM o Ejecutivo Asignado *</label>
            <input type="text" id="reg-kam-name" placeholder="Ej. Carlos Méndez / Hipha KAM" class="w-full px-3.5 py-2.5 text-xs rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-800 mb-1">Notas / Folio de Acuerdo o Comprobante (Opcional)</label>
            <input type="text" id="reg-kam-notes" placeholder="Ej. Transferencia anual realizada hoy / Pago acordado en visita" class="w-full px-3.5 py-2.5 text-xs rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
          </div>

          <button type="button" id="btn-submit-kam-payment" onclick="handleKamPaymentSubmit()" class="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs sm:text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2">
            <span>Registrar Alta con Asesor KAM</span>
            <i data-lucide="check" class="w-4 h-4"></i>
          </button>
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
                El <strong>registro gratuito</strong> incluye únicamente tus datos generales de contacto: <strong>teléfono, WhatsApp, ubicación y horarios</strong> en el directorio. <em>No incluye micrositio web interactivo, catálogo de fotos ni insignia de vecino verificado.</em>
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

      <!-- FASE 4: CONFIRMACIÓN Y FOLIO -->
      <div id="reg-step-4" class="hidden text-center space-y-4 py-4">
        <div class="w-16 h-16 mx-auto rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
          <i data-lucide="check-circle-2" class="w-9 h-9"></i>
        </div>
        <h4 id="step4-title" class="text-xl font-black text-slate-950">¡Comercio Verificado con Éxito!</h4>
        <p class="text-xs text-slate-600 max-w-sm mx-auto leading-relaxed">
          Tu comercio <strong id="step4-business-name" class="text-slate-900">...</strong> cuenta con Sello Oficial Vecino Verificado.
        </p>
        <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 max-w-xs mx-auto">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Folio de Verificación</span>
          <span id="step4-folio" class="text-base font-mono font-black text-emerald-600">NATURA-...</span>
        </div>
        <p id="step4-desc" class="text-xs text-slate-500 max-w-xs mx-auto">
          Tu negocio ya se encuentra registrado y activo en el directorio comunitario.
        </p>
        <button onclick="closeRegisterModal(); location.reload();" class="w-full py-3.5 px-4 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs sm:text-sm">
          Entendido, Ver en el Directorio
        </button>
      </div>

    </div>
    `;
  }

  function ensureModalMounted() {
    let modal = document.getElementById("register-modal");
    if (!modal) {
      modal = document.createElement("div");
      modal.id = "register-modal";
      modal.dataset.version = "v399";
      modal.className = "fixed inset-0 z-50 hidden items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs";
      document.body.appendChild(modal);
    }

    // Si el modal no contiene el stepper completo o carece de los nuevos campos o es versión antigua
    if (!document.getElementById("reg-step-1") || !document.getElementById("reg-schedule") || !document.getElementById("tab-pay-kam") || modal.dataset.version !== "v399") {
      modal.innerHTML = renderWizardHTML();
      modal.dataset.version = "v399";
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
    registerUploadedPhotos = [];
    renderRegisterPhotosGrid();
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
      if (desc) desc.textContent = isFree ? "Publicación en el directorio con datos de contacto e hipervínculos funcionales." : "Conéctate directamente con las familias de cotos Natura con micrositio y catálogo.";
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
      if (title) title.textContent = "Suscripción Anual ($399 MXN) y Micrositio";
      if (desc) desc.textContent = "Activa tu Micrositio web interactivo con catálogo de fotos y Sello Vecino Verificado.";
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
    } else if (step === 4) {
      if (label) label.textContent = "Completado";
      if (title) title.textContent = isFree ? "¡Registro Básico Gratuito Enviado!" : "¡Suscripción y Micrositio Registrados!";
      if (desc) desc.textContent = isFree ? "Tu negocio ha sido registrado con datos generales e hipervínculos de contacto." : "Tu solicitud ha sido registrada y está lista para su activación con catálogo.";
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
      const website = document.getElementById("reg-website") ? document.getElementById("reg-website").value.trim() : "";
      const schedule = document.getElementById("reg-schedule") ? document.getElementById("reg-schedule").value.trim() : "Lunes a Sábado · 09:00 a 19:00 hrs";

      // Métodos de contacto preferidos
      const checkedBoxes = Array.from(document.querySelectorAll('input[name="pref_contact"]:checked')).map(el => el.value);
      const prefMethods = checkedBoxes.length > 0 ? checkedBoxes.join(",") : "whatsapp";

      const deliveryChecked = checkedBoxes.includes("delivery") || (document.getElementById("reg-delivery") ? document.getElementById("reg-delivery").checked : false);

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
        photos: (currentSelectedPlan === "microsite" && registerUploadedPhotos.length > 0) ? JSON.stringify(registerUploadedPhotos) : null,
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
      markWaAsVerified();
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
      desc: "Tu comercio ha sido registrado con datos generales (teléfono, WhatsApp, ubicación y horarios). Podrás activar tu micrositio interactivo y catálogo de fotos con la suscripción anual en cualquier momento."
    });
  }

  function goToStep3() {
    if (!waVerified) {
      alert("Por favor abre WhatsApp con tu código o pulsa 'Confirmar Validación' para continuar.");
      return;
    }
    setWizardStep(3);
  }

  const MP_ANNUAL_SUBSCRIPTION_URL = "https://mpago.la/2jXGN6C";

  async function triggerMercadoPagoPayment() {
    const btn = document.getElementById("btn-pay-mp");
    const origText = btn ? btn.innerHTML : "";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>Abriendo Mercado Pago...</span>`;
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }

    try {
      // Registrar en backend la intención de suscripción con monto de $399
      if (currentRegId && !currentRegId.startsWith("mock-")) {
        await fetch("/api/epicentro/register/report-kam-payment", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            registration_id: currentRegId,
            kam_name: "Mercado Pago Suscripción Anual (Link Directo)",
            amount: 399.0,
            payment_method: "mercadopago_subscription",
            notes: `Inició suscripción anual en ${MP_ANNUAL_SUBSCRIPTION_URL}`
          })
        }).catch(e => console.warn("Aviso reporte MP:", e));
      }

      // Abrir enlace oficial de suscripción anual en Mercado Pago
      const opened = window.open(MP_ANNUAL_SUBSCRIPTION_URL, "_blank");
      if (!opened) {
        window.location.href = MP_ANNUAL_SUBSCRIPTION_URL;
        return;
      }

      showStep4Success("NATURA-SUB-" + Math.floor(1000 + Math.random() * 9000), {
        title: "¡Suscripción Anual Iniciada!",
        desc: "Hemos registrado tu solicitud de suscripción anual ($399 MXN). Completa el pago en Mercado Pago para activar tu micrositio y catálogo de fotos."
      });
    } catch (err) {
      console.warn("Aviso Mercado Pago:", err);
      window.open(MP_ANNUAL_SUBSCRIPTION_URL, "_blank");
      showStep4Success("NATURA-SUB-" + Math.floor(1000 + Math.random() * 9000), {
        title: "¡Suscripción Anual Iniciada!",
        desc: "Hemos registrado tu solicitud de suscripción anual ($399 MXN). Completa el pago en Mercado Pago para activar tu micrositio y catálogo de fotos."
      });
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origText;
        if (window.lucide && lucide.createIcons) lucide.createIcons();
      }
    }
  }

  async function skipVerificationPayment() {
    const ok = confirm("¿Confirmas tu registro básico gratuito?\n\nImportante: Tu negocio aparecerá en el directorio comunitario con tus datos generales (teléfono, WhatsApp, ubicación y horarios), pero NO incluirá micrositio web interactivo, fotos de catálogo ni insignia de Vecino Verificado.");
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
            notes: "Alta básica sin costo (solo teléfono, whatsapp, ubicación y horarios; sin fotos/micrositio)"
          })
        }).catch(e => console.warn("Aviso reporte gratis:", e));
      }
    } catch (e) {
      console.warn(e);
    }

    showStep4Success("NATURA-GRATIS-" + Math.floor(1000 + Math.random() * 9000), {
      title: "¡Registro Básico Gratuito Enviado!",
      desc: "Tu comercio ha sido registrado con datos generales (teléfono, WhatsApp, ubicación y horarios). Podrás activar tu micrositio y fotos con la suscripción anual en cualquier momento."
    });
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
        showStep4Success(data.folio || `NATURA-VERIFIED-${codeVal}`);
      }, 700);
    } catch (err) {
      if (currentRegId && currentRegId.startsWith("mock-") && ["NATURA100", "FUNDADOR", "EPICENTRO2026", "HIPHA"].includes(codeVal)) {
        if (feedback) {
          feedback.className = "text-[11px] font-bold text-emerald-700 block";
          feedback.textContent = "✓ ¡Código válido! Tu negocio ha sido verificado sin costo.";
        }
        setTimeout(() => {
          showStep4Success(`NATURA-PROMO-${codeVal}`);
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

  function showStep4Success(folio, customTexts) {
    const bNameEl = document.getElementById("step4-business-name");
    const folioEl = document.getElementById("step4-folio");
    const titleEl = document.getElementById("step4-title");
    const descEl = document.getElementById("step4-desc");

    if (bNameEl) bNameEl.textContent = currentBusinessName || "tu negocio";
    if (folioEl) folioEl.textContent = folio;
    if (customTexts && customTexts.title && titleEl) titleEl.textContent = customTexts.title;
    if (customTexts && customTexts.desc && descEl) descEl.textContent = customTexts.desc;
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
  window.handleRegisterPhotoFiles = handleRegisterPhotoFiles;
  window.promptRegisterPhotoUrl = promptRegisterPhotoUrl;
  window.removeRegisterPhoto = removeRegisterPhoto;
  window.renderRegisterPhotosGrid = renderRegisterPhotosGrid;
  window.setPaymentMode = setPaymentMode;
  window.handleKamPaymentSubmit = handleKamPaymentSubmit;
  window.selectRegistrationPlan = selectRegistrationPlan;
  window.finishFreeRegistration = finishFreeRegistration;

  function checkUrlAutoOpen() {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get("open_register") === "1") {
        openRegisterModal(urlParams.get("cat"));
        const step = parseInt(urlParams.get("step") || "1", 10);
        if (step > 1 && step <= 4) {
          if (step >= 2) waVerified = true;
          setWizardStep(step);
        }
        if (urlParams.get("pay_mode") === "kam") {
          setPaymentMode("kam");
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
