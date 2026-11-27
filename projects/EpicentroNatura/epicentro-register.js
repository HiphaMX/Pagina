/**
 * Epicentro Natura - Sistema Unificado de Registro Ágil y Autoservicio Comercial
 * Flujo en 3 Momentos:
 * 1. Micro-Registro (30 segundos en móvil: Nombre, Categoría, Coto, WhatsApp)
 * 2. Efecto WOW: Live Preview interactivo con portada curada y selección de plan
 * 3. Activación (Mercado Pago o Cupón) y Acceso Directo al Portal de Autoservicio (/natura/editar)
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
      { slug: "cortinas-persianas", label: "Cortinas y Persianas" },
      { slug: "plantas-paisajismo", label: "Plantas y Paisajismo" },
      { slug: "muebles-decoracion", label: "Muebles y Decoración" },
      { slug: "carwash", label: "Carwash" },
      { slug: "tintoreria-planchaduria", label: "Tintorería y Planchaduría" },
      { slug: "otros", label: "Otros" }
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
    ],
    "cuidado-personal": [
      { slug: "barberia-salon", label: "Barbería y Salón" },
      { slug: "spa-masajes", label: "Spa y Masajes" },
      { slug: "cuidado-piel-estetica", label: "Cuidado Facial y Estética" },
      { slug: "unas-pestanas", label: "Uñas y Pestañas" },
      { slug: "nutricion-bienestar", label: "Nutrición y Bienestar Holístico" }
    ]
  };

  const CURATED_COVERS_FALLBACK = {
    "comida-delivery": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=1600&q=80",
    "productos-artesanales": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=1600&q=80",
    "educacion": "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=1600&q=80",
    "servicios-profesionales": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1600&q=80",
    "servicios-hogar": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=1600&q=80",
    "mascotas": "https://images.unsplash.com/photo-1548767797-d8c844163c4c?auto=format&fit=crop&w=1600&q=80",
    "fitness": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1600&q=80",
    "cuidado-personal": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1600&q=80"
  };

  let currentRegId = null;
  let currentRegSlug = null;
  let currentBusinessName = "";
  let currentSelectedPlan = "microsite"; // "microsite" ($499/año) o "basic" ($99/año)
  let currentEditToken = "";
  let currentPreviewData = null;

  // --- SINCRONIZACIÓN DE SUBCATEGORÍAS ---
  function syncSubcategoriesDropdown() {
    const catSelect = document.getElementById("reg-category");
    const subSelect = document.getElementById("reg-subcategory");
    if (!catSelect || !subSelect) return;

    const catSlug = catSelect.value;
    const subList = SUBCATEGORIES_MAP[catSlug] || [];

    subSelect.innerHTML = "";
    subList.forEach(sub => {
      const opt = document.createElement("option");
      opt.value = sub.slug;
      opt.textContent = sub.label;
      subSelect.appendChild(opt);
    });
  }

  // --- SELECCIÓN DE PLAN ---
  function selectRegistrationPlan(plan) {
    currentSelectedPlan = (plan === "basic" || plan === "free_basic" || plan === "directorio") ? "basic" : "microsite";
    const btnMicro = document.getElementById("plan-btn-microsite");
    const btnBasic = document.getElementById("plan-btn-basic");
    const payBtnText = document.getElementById("btn-pay-mp-text");

    if (currentSelectedPlan === "microsite") {
      if (btnMicro) {
        btnMicro.className = "p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-emerald-600 flex items-center justify-between cursor-pointer";
      }
      if (btnBasic) {
        btnBasic.className = "p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex items-center justify-between opacity-80 hover:opacity-100 cursor-pointer";
      }
      if (payBtnText) {
        payBtnText.textContent = "Pagar Página Escaparate Individual ($499 MXN / año)";
      }
    } else {
      if (btnMicro) {
        btnMicro.className = "p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex items-center justify-between opacity-80 hover:opacity-100 cursor-pointer";
      }
      if (btnBasic) {
        btnBasic.className = "p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-slate-900 flex items-center justify-between cursor-pointer";
      }
      if (payBtnText) {
        payBtnText.textContent = "Pagar Plan Esencial ($99 MXN / año)";
      }
    }
  }

  // --- MONTAJE DEL MODAL EN EL DOM ---
  function mountRegisterModal() {
    let modal = document.getElementById("register-modal");

    // Si ya existe y está actualizado a la versión v2, retornarlo
    if (modal && modal.dataset.onboardingVersion === "v2") {
      return modal;
    }

    if (!modal) {
      modal = document.createElement("div");
      modal.id = "register-modal";
      document.body.appendChild(modal);
    }

    modal.dataset.onboardingVersion = "v2";
    modal.className = "fixed inset-0 z-50 hidden items-center justify-center p-3 sm:p-4 bg-slate-950/80 backdrop-blur-md overflow-y-auto";

    modal.innerHTML = `
    <div class="relative w-full max-w-xl bg-white rounded-3xl shadow-2xl border border-slate-200 overflow-hidden my-auto" onclick="event.stopPropagation()">
      
      <!-- HEADER CON INDICADOR DE PROGRESO -->
      <div class="p-5 sm:p-6 pb-4 bg-gradient-to-b from-slate-50 to-white border-b border-slate-100">
        <div class="flex items-center justify-between gap-3">
          <div class="flex items-center gap-2">
            <span class="w-8 h-8 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-black text-sm">
              <i data-lucide="store" class="w-4 h-4"></i>
            </span>
            <div>
              <h3 id="wizard-title" class="text-base sm:text-lg font-black text-slate-900 leading-tight">
                Registra tu Negocio en Epizentro Natura
              </h3>
              <p id="wizard-desc" class="text-xs text-slate-500 mt-0.5">
                Presencia verificada para las familias de los cotos en 30 segundos
              </p>
            </div>
          </div>
          <button type="button" onclick="closeRegisterModal()" class="w-8 h-8 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition-colors cursor-pointer shrink-0">
            <i data-lucide="x" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Barras de progreso -->
        <div class="grid grid-cols-3 gap-2 mt-4">
          <div id="step-bar-1" class="h-1.5 rounded-full bg-emerald-600 transition-all"></div>
          <div id="step-bar-2" class="h-1.5 rounded-full bg-slate-200 transition-all"></div>
          <div id="step-bar-3" class="h-1.5 rounded-full bg-slate-200 transition-all"></div>
        </div>
      </div>

      <div class="p-5 sm:p-6 max-h-[80vh] overflow-y-auto">

        <!-- FASE 1: MICRO-REGISTRO RÁPIDO (30 SEGUNDOS) -->
        <div id="reg-step-1">
          <form onsubmit="submitMicroRegister(event)" class="space-y-4">
            <!-- Honeypot anti-bot -->
            <input type="text" id="reg-honeypot" name="hp_field" style="display:none!important;" tabindex="-1" autocomplete="off">

            <div>
              <label class="block text-xs font-bold text-slate-800 mb-1">Nombre Comercial de tu Negocio *</label>
              <input type="text" id="reg-name" required placeholder="Ej. Panadería Don Juan / Plomería Los Robles" class="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-bold text-slate-800 mb-1">Giro de la Oferta *</label>
                <select id="reg-category" onchange="syncSubcategoriesDropdown()" class="w-full px-3 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
                  <option value="comida-delivery">Comida & Delivery</option>
                  <option value="productos-artesanales">Productos artesanales</option>
                  <option value="servicios-hogar">Servicios hogar</option>
                  <option value="mascotas">Mascotas</option>
                  <option value="fitness">Fitness</option>
                  <option value="cuidado-personal">Cuidado personal</option>
                  <option value="educacion">Educación</option>
                  <option value="servicios-profesionales">Servicios Profesionales</option>
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
                <label class="block text-xs font-bold text-slate-800 mb-1">Coto, Fraccionamiento o Zona *</label>
                <input type="text" id="reg-address" required placeholder="Ej. Coto Ceiba / Mariano Otero" class="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
              </div>
              <div>
                <label class="block text-xs font-bold text-slate-800 mb-1">WhatsApp de Pedidos y Clientes *</label>
                <input type="tel" id="reg-wa" required placeholder="33 1234 5678" class="w-full px-3.5 py-2.5 text-xs sm:text-sm rounded-xl border border-slate-200 bg-slate-50 focus:bg-white focus:ring-2 focus:ring-emerald-500 focus:outline-none">
              </div>
            </div>

            <!-- Desplegable Opcional de Titular y Correo -->
            <div class="pt-1">
              <button type="button" onclick="toggleOptionalFields()" class="text-xs text-slate-500 hover:text-emerald-700 font-semibold flex items-center gap-1.5 cursor-pointer">
                <span id="optional-fields-label">+ Datos adicionales (Opcional: Titular y correo)</span>
                <i id="optional-chevron" data-lucide="chevron-down" class="w-3.5 h-3.5 transition-transform"></i>
              </button>

              <div id="optional-fields-container" class="hidden mt-2 p-3 rounded-2xl bg-slate-50 border border-slate-200 grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                <div>
                  <label class="block text-[11px] font-bold text-slate-700 mb-0.5">Nombre del Responsable</label>
                  <input type="text" id="reg-owner" placeholder="Ej. Carlos Méndez" class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-white focus:outline-none">
                </div>
                <div>
                  <label class="block text-[11px] font-bold text-slate-700 mb-0.5">Correo Electrónico</label>
                  <input type="email" id="reg-email" placeholder="tu@correo.com" class="w-full px-2.5 py-1.5 text-xs rounded-xl border border-slate-200 bg-white focus:outline-none">
                </div>
              </div>
            </div>

            <div class="pt-2">
              <button type="submit" id="btn-submit-step1" class="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs sm:text-sm shadow-lg shadow-emerald-600/30 transition-all active:scale-95 flex items-center justify-center gap-2 cursor-pointer">
                <span>Generar Vista Previa de mi Ficha</span>
                <i data-lucide="arrow-right" class="w-4 h-4"></i>
              </button>
            </div>

            <p class="text-[11px] text-center text-slate-400">
              ⚡ Te mostraremos cómo se verá tu ficha antes de cualquier cobro. Podrás subir tus fotos y catálogo después de activar.
            </p>
          </form>
        </div>

        <!-- FASE 2: PREVISUALIZACIÓN VIVA (EFECTO WOW) & ACTIVACIÓN -->
        <div id="reg-step-2" class="hidden space-y-5">
          
          <div class="p-3 rounded-2xl bg-emerald-50 border border-emerald-200 flex items-center gap-2 text-xs text-emerald-950 font-medium">
            <i data-lucide="sparkles" class="w-4 h-4 text-emerald-600 shrink-0"></i>
            <span><strong>¡Así verán tu negocio los vecinos!</strong> Tu ficha se generó con una portada curada de alta calidad.</span>
          </div>

          <!-- TARJETA LIVE PREVIEW EXACTA -->
          <div class="rounded-2xl border border-slate-200 bg-white shadow-lg overflow-hidden relative">
            <div class="relative w-full h-36 bg-slate-900 overflow-hidden">
              <img id="preview-cover-img" src="" alt="Portada Preview" class="w-full h-full object-cover">
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
              
              <div class="absolute top-2.5 right-2.5">
                <span class="px-2.5 py-1 rounded-full bg-slate-950/80 backdrop-blur-md border border-emerald-400/40 text-emerald-300 text-[10px] font-black uppercase flex items-center gap-1">
                  <i data-lucide="badge-check" class="w-3 h-3 text-emerald-400"></i>
                  <span>Sello Vecino Verificado</span>
                </span>
              </div>
            </div>

            <div class="p-4 space-y-2 -mt-6 relative z-10">
              <div class="bg-white/95 backdrop-blur-sm p-3.5 rounded-xl border border-slate-200 shadow-md space-y-2">
                <div class="flex items-center justify-between gap-2">
                  <h4 id="preview-title" class="text-base font-black text-slate-900 leading-tight">
                    Nombre del Negocio
                  </h4>
                  <span id="preview-category-badge" class="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                    Comida & Delivery
                  </span>
                </div>

                <div class="flex items-center gap-2 text-xs text-slate-500">
                  <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600 shrink-0"></i>
                  <span id="preview-coto-text">Coto Ceiba · Prolongación Mariano Otero</span>
                </div>

                <div class="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
                  <span class="text-[11px] text-emerald-700 font-bold flex items-center gap-1">
                    <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    Abierto para pedidos
                  </span>

                  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-emerald-600 text-white text-[11px] font-bold shadow-xs">
                    <i data-lucide="message-circle" class="w-3.5 h-3.5"></i>
                    <span>Pedir por WhatsApp</span>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- SELECTOR DE PLAN -->
          <div class="space-y-2">
            <span class="text-xs font-bold text-slate-800 block">Elige tu modalidad de activación:</span>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button type="button" id="plan-btn-microsite" onclick="selectRegistrationPlan('microsite')" class="p-3 rounded-2xl text-left transition-all bg-white shadow-xs border-2 border-emerald-600 flex items-center justify-between cursor-pointer">
                <div>
                  <span class="text-xs font-black text-slate-900 block flex items-center gap-1">
                    <i data-lucide="sparkles" class="w-3.5 h-3.5 text-emerald-600"></i>
                    Página Escaparate
                  </span>
                  <span class="text-[10px] text-slate-500">Hasta 10 fotos, precios y pedidos</span>
                </div>
                <span class="px-2 py-1 text-[11px] font-black uppercase rounded-lg bg-emerald-100 text-emerald-800 font-mono">$499/año</span>
              </button>

              <button type="button" id="plan-btn-basic" onclick="selectRegistrationPlan('basic')" class="p-3 rounded-2xl text-left transition-all hover:bg-white/70 border-2 border-transparent flex items-center justify-between opacity-80 hover:opacity-100 cursor-pointer">
                <div>
                  <span class="text-xs font-bold text-slate-700 block flex items-center gap-1">
                    <i data-lucide="file-text" class="w-3.5 h-3.5 text-slate-400"></i>
                    Plan Esencial
                  </span>
                  <span class="text-[10px] text-slate-500">Directorio con llamadas y WhatsApp</span>
                </div>
                <span class="px-2 py-1 text-[11px] font-black uppercase rounded-lg bg-slate-200 text-slate-800 font-mono">$99/año</span>
              </button>
            </div>
          </div>

          <!-- TÉRMINOS Y CONDICIONES CHECKBOX -->
          <div class="p-3 rounded-xl bg-slate-50 border border-slate-200">
            <label class="flex items-start gap-2.5 text-xs text-slate-700 cursor-pointer select-none">
              <input type="checkbox" id="reg-terms-check" checked class="mt-0.5 rounded border-slate-300 text-emerald-600 focus:ring-emerald-500 w-4 h-4 shrink-0">
              <span class="leading-relaxed">
                He leído y acepto los <a href="/terminos" target="_blank" class="font-bold text-emerald-700 hover:underline">Términos y Condiciones</a> y Normas Comunitarias de Epizentro.
              </span>
            </label>
          </div>

          <!-- BOTÓN DE COBRO MERCADO PAGO -->
          <div class="space-y-2 pt-1">
            <button type="button" id="btn-pay-mp" onclick="triggerMercadoPagoPayment()" class="w-full py-4 px-4 rounded-xl bg-[#009ee3] hover:bg-[#0082ba] text-white font-extrabold text-xs sm:text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2 cursor-pointer">
              <i data-lucide="shield-check" class="w-4 h-4"></i>
              <span id="btn-pay-mp-text">Pagar Página Escaparate Individual ($499 MXN / año)</span>
              <i data-lucide="arrow-right" class="w-4 h-4"></i>
            </button>
            <p class="text-[10px] text-center text-slate-400">
              🔒 Pago seguro con Mercado Pago (Tarjeta, SPEI, Saldo). Activación inmediata y entrega de enlace para subir fotos.
            </p>
          </div>

          <!-- ACORDEÓN DE CORTESÍA / INVITACIÓN -->
          <div class="pt-2 border-t border-slate-100">
            <button type="button" onclick="toggleCouponBox()" class="text-xs font-semibold text-slate-600 hover:text-emerald-700 flex items-center justify-between w-full p-2 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer">
              <span class="flex items-center gap-1.5">
                <i data-lucide="tag" class="w-3.5 h-3.5 text-emerald-600"></i>
                <span>¿Tienes código de invitación o cortesía de Hipha?</span>
              </span>
              <i id="coupon-chevron" data-lucide="chevron-down" class="w-4 h-4 transition-transform"></i>
            </button>
            <div id="coupon-container" class="hidden mt-2 p-3 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
              <div class="flex gap-2">
                <input type="text" id="reg-coupon-code" placeholder="Ej. NATURA100-24U6" class="w-full px-3 py-2 text-xs uppercase font-mono tracking-wider font-bold rounded-xl border border-slate-200 bg-white focus:ring-2 focus:ring-emerald-500">
                <button type="button" onclick="handleApplyCoupon()" id="btn-apply-coupon" class="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shrink-0 transition-colors cursor-pointer">
                  Aplicar
                </button>
              </div>
              <p id="coupon-feedback" class="text-[11px] font-bold hidden"></p>
            </div>
          </div>

          <!-- BOTÓN VOLVER A PASO 1 -->
          <div class="text-center pt-2">
            <button type="button" onclick="setWizardStep(1)" class="text-xs font-bold text-slate-500 hover:text-slate-800 transition-colors cursor-pointer">
              &larr; Modificar datos del negocio
            </button>
          </div>
        </div>

        <!-- FASE 3: ÉXITO Y AUTOSERVICIO -->
        <div id="reg-step-3" class="hidden text-center py-4 space-y-4 max-w-md mx-auto">
          <div class="w-16 h-16 mx-auto rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
            <i data-lucide="check-circle-2" class="w-9 h-9"></i>
          </div>

          <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-900 text-[11px] font-bold">
            <i data-lucide="badge-check" class="w-3.5 h-3.5 text-emerald-600"></i>
            <span>Negocio Activo · Publicado en el Directorio</span>
          </div>

          <h4 id="success-title" class="text-xl font-black text-slate-950">
            ¡Felicidades, tu negocio ya está publicado!
          </h4>
          
          <p id="success-desc" class="text-xs text-slate-600 max-w-sm mx-auto leading-relaxed">
            Tu negocio <strong id="success-bname" class="text-slate-900"></strong> ya es visible para los vecinos de la comunidad. Nuestro sistema inteligente audita continuamente la red para garantizar un directorio confiable y seguro.
          </p>

          <div class="p-3.5 rounded-xl bg-slate-50 border border-slate-200 max-w-xs mx-auto">
            <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Folio de Verificación</span>
            <span id="success-folio" class="text-base font-mono font-black text-emerald-700">NATURA-VERIFIED-100</span>
          </div>

          <!-- BOTONERA DE ACCIÓN -->
          <div class="space-y-2 pt-2">
            <a id="btn-to-public-showcase" href="#" class="w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-xs sm:text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2 no-underline">
              <i data-lucide="external-link" class="w-4 h-4"></i>
              <span>Ver mi Página Escaparate en Vivo</span>
            </a>

            <a id="btn-to-self-service" href="#" class="w-full py-2.5 px-4 rounded-xl bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center gap-2 no-underline transition-colors">
              <i data-lucide="camera" class="w-4 h-4 text-emerald-600"></i>
              <span>Personalizar Fotos y Catálogo Ahora</span>
            </a>
          </div>

          <!-- AVISO DE WHATSAPP -->
          <div class="p-3 rounded-2xl bg-emerald-50/80 border border-emerald-200 text-left flex items-start gap-2.5 mt-3">
            <i data-lucide="message-circle" class="w-4 h-4 text-emerald-600 shrink-0 mt-0.5"></i>
            <p class="text-[11px] text-emerald-950 leading-relaxed">
              <strong>Guardamos tu enlace:</strong> También enviamos tu enlace de edición privada a tu WhatsApp para que agregues fotos y precios en cualquier momento desde tu celular o computadora.
            </p>
          </div>

          <div class="pt-2">
            <button onclick="closeRegisterModal(); location.reload();" class="text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors">
              Cerrar ventana
            </button>
          </div>
        </div>

      </div>
    </div>
    `;

    // Cerrar al hacer clic en el backdrop oscuro
    modal.onclick = function(e) {
      if (e.target === modal) {
        closeRegisterModal();
      }
    };

    if (window.lucide) lucide.createIcons();
    return modal;
  }

  // --- CONTROL DEL WIZARD STEPPER ---
  function setWizardStep(step) {
    const s1 = document.getElementById("reg-step-1");
    const s2 = document.getElementById("reg-step-2");
    const s3 = document.getElementById("reg-step-3");
    if (s1) s1.classList.toggle("hidden", step !== 1);
    if (s2) s2.classList.toggle("hidden", step !== 2);
    if (s3) s3.classList.toggle("hidden", step !== 3);

    const bar1 = document.getElementById("step-bar-1");
    const bar2 = document.getElementById("step-bar-2");
    const bar3 = document.getElementById("step-bar-3");
    const title = document.getElementById("wizard-title");
    const desc = document.getElementById("wizard-desc");

    if (step === 1) {
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-slate-200 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-slate-200 transition-all";
      if (title) title.textContent = "Registra tu Negocio en Epizentro Natura";
      if (desc) desc.textContent = "Presencia verificada para las familias de los cotos en 30 segundos";
    } else if (step === 2) {
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-slate-200 transition-all";
      if (title) title.textContent = "⭐ Vista Previa Oficial de tu Negocio";
      if (desc) desc.textContent = "Así verán tu escaparate las familias y vecinos de los cotos";
    } else if (step === 3) {
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (title) title.textContent = "¡Comercio Verificado y Activo!";
      if (desc) desc.textContent = "Tu negocio ya forma parte de Epizentro Natura";
    }

    if (window.lucide) lucide.createIcons();
  }

  // --- ENVÍO DEL MICRO-REGISTRO (PASO 1) ---
  async function submitMicroRegister(e) {
    if (e && e.preventDefault) e.preventDefault();

    const hp = document.getElementById("reg-honeypot") ? document.getElementById("reg-honeypot").value : "";
    if (hp && hp.trim()) {
      alert("Solicitud procesada correctamente.");
      closeRegisterModal();
      return;
    }

    const name = document.getElementById("reg-name").value.trim();
    const catSelect = document.getElementById("reg-category");
    const subSelect = document.getElementById("reg-subcategory");
    const catSlug = catSelect ? catSelect.value : "comida-delivery";
    const catLabel = (catSelect && catSelect.selectedIndex >= 0) ? catSelect.options[catSelect.selectedIndex].text : "Comida & Delivery";
    const subSlug = subSelect ? subSelect.value : "pizzas-pastas";
    const subLabel = (subSelect && subSelect.selectedIndex >= 0) ? subSelect.options[subSelect.selectedIndex].text : "Pizzas y Pastas";
    const address = document.getElementById("reg-address").value.trim();
    const wa = document.getElementById("reg-wa").value.trim();

    const ownerInput = document.getElementById("reg-owner");
    const emailInput = document.getElementById("reg-email");
    const owner = (ownerInput && ownerInput.value.trim()) ? ownerInput.value.trim() : name;
    const email = (emailInput && emailInput.value.trim()) ? emailInput.value.trim() : null;

    if (!name || !address || !wa) {
      alert("Por favor completa los campos requeridos: Nombre, Ubicación y WhatsApp.");
      return;
    }

    currentBusinessName = name;

    const btn = document.getElementById("btn-submit-step1");
    let origHtml = "";
    if (btn) {
      origHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>Generando Ficha en Vivo...</span>`;
      if (window.lucide) lucide.createIcons();
    }

    const payload = {
      business_name: name,
      category_slug: catSlug,
      category_label: catLabel,
      subcategory_slug: subSlug,
      subcategory_label: subLabel,
      coto_address: address,
      whatsapp: wa,
      owner_name: owner,
      email: email,
      plan_type: currentSelectedPlan,
      honeypot: hp
    };

    try {
      const res = await fetch("/api/epicentro/register/initiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Error al procesar el micro-registro.");
      }

      const data = await res.json();
      currentRegId = data.registration_id;
      currentRegSlug = data.slug || "";
      currentEditToken = data.edit_token || "";
      currentPreviewData = data;

      try {
        if (currentEditToken) sessionStorage.setItem("last_epicentro_edit_token", currentEditToken);
        if (currentRegId) sessionStorage.setItem("last_epicentro_reg_id", currentRegId);
      } catch (e) {}

      // Actualizar tarjeta Live Preview
      renderLivePreviewCard(data);

      setWizardStep(2);
    } catch (err) {
      console.warn("Aviso en initiate:", err);
      // Fallback local visual
      currentRegId = "mock-" + Date.now();
      currentEditToken = "mock-token-" + Date.now();
      const fallbackData = {
        business_name: name,
        category_label: catLabel,
        coto_address: address,
        whatsapp: wa,
        cover_photo: CURATED_COVERS_FALLBACK[catSlug] || CURATED_COVERS_FALLBACK["comida-delivery"]
      };
      renderLivePreviewCard(fallbackData);
      setWizardStep(2);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origHtml;
        if (window.lucide) lucide.createIcons();
      }
    }
  }

  function renderLivePreviewCard(data) {
    const titleEl = document.getElementById("preview-title");
    const catBadgeEl = document.getElementById("preview-category-badge");
    const cotoEl = document.getElementById("preview-coto-text");
    const coverEl = document.getElementById("preview-cover-img");

    if (titleEl) titleEl.textContent = data.business_name || currentBusinessName;
    if (catBadgeEl) catBadgeEl.textContent = data.category_label || "Comercio Verificado";
    if (cotoEl) cotoEl.textContent = data.coto_address || "Natura Bosque";
    if (coverEl) coverEl.src = data.cover_photo || CURATED_COVERS_FALLBACK["comida-delivery"];

    if (window.lucide) lucide.createIcons();
  }

  // --- ACTIVACIÓN CON MERCADO PAGO ---
  async function triggerMercadoPagoPayment() {
    const termsCheck = document.getElementById("reg-terms-check");
    if (termsCheck && !termsCheck.checked) {
      alert("Para continuar y publicar tu negocio, debes aceptar los Términos y Condiciones y Normas Comunitarias de Epizentro Natura.");
      return;
    }

    const btn = document.getElementById("btn-pay-mp");
    let origHtml = "";
    if (btn) {
      origHtml = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>Abriendo Checkout Seguro...</span>`;
      if (window.lucide) lucide.createIcons();
    }

    try {
      const res = await fetch("/api/epicentro/register/create-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ registration_id: currentRegId })
      });

      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        throw new Error(data.detail || "No se pudo generar la pasarela de pago.");
      }

      const checkoutUrl = data.init_point || data.sandbox_init_point;
      if (!checkoutUrl) {
        throw new Error("Mercado Pago no retornó un punto de pago válido.");
      }

      try {
        sessionStorage.setItem("last_epicentro_reg_id", currentRegId);
      } catch (e) {}

      // Redirigir a Mercado Pago
      window.location.href = checkoutUrl;
    } catch (err) {
      console.error(err);
      alert("Aviso de Mercado Pago: " + (err.message || "Intenta nuevamente."));
      if (btn) {
        btn.disabled = false;
        btn.innerHTML = origHtml;
        if (window.lucide) lucide.createIcons();
      }
    }
  }

  // --- CANJE DE CUPÓN DE CORTESÍA ---
  async function handleApplyCoupon() {
    const termsCheck = document.getElementById("reg-terms-check");
    const feedback = document.getElementById("coupon-feedback");
    if (termsCheck && !termsCheck.checked) {
      if (feedback) {
        feedback.className = "text-[11px] font-bold text-rose-600 block";
        feedback.textContent = "Debes aceptar los Términos y Condiciones para activar tu registro.";
      } else {
        alert("Debes aceptar los Términos y Condiciones para activar tu registro.");
      }
      return;
    }

    const input = document.getElementById("reg-coupon-code");
    const btn = document.getElementById("btn-apply-coupon");
    const codeVal = input ? input.value.trim().toUpperCase() : "";

    if (!codeVal) {
      if (feedback) {
        feedback.className = "text-[11px] font-bold text-rose-600 block";
        feedback.textContent = "Por favor ingresa tu código de cortesía.";
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
        feedback.textContent = "✓ ¡Código válido! Tu negocio ha sido verificado al 100%.";
      }

      currentEditToken = data.edit_token || currentEditToken;

      setTimeout(() => {
        showSuccessScreen(data.folio || `NATURA-VERIFIED-${codeVal}`, data.edit_token || currentEditToken);
      }, 700);
    } catch (err) {
      if (feedback) {
        feedback.className = "text-[11px] font-bold text-rose-600 block";
        feedback.textContent = err.message || "Código inválido.";
      }
      if (btn) {
        btn.disabled = false;
        btn.textContent = "Aplicar";
      }
    }
  }

  // --- PANTALLA DE ÉXITO Y AUTOSERVICIO ---
  function showSuccessScreen(folio, editToken) {
    const bNameEl = document.getElementById("success-bname");
    const folioEl = document.getElementById("success-folio");
    const btnSelfService = document.getElementById("btn-to-self-service");
    const btnPublic = document.getElementById("btn-to-public-showcase");

    if (bNameEl) bNameEl.textContent = currentBusinessName || "tu negocio";
    if (folioEl) folioEl.textContent = folio;

    const tokenToUse = editToken || currentEditToken;
    try {
      if (tokenToUse) sessionStorage.setItem("last_epicentro_edit_token", tokenToUse);
      if (currentRegId) sessionStorage.setItem("last_epicentro_reg_id", currentRegId);
    } catch (e) {}

    const editUrl = tokenToUse ? `/natura/editar?token=${encodeURIComponent(tokenToUse)}` : "#";
    const bizRoute = currentRegSlug || currentRegId;
    const publicUrl = tokenToUse 
      ? `/natura/${encodeURIComponent(bizRoute)}?token=${encodeURIComponent(tokenToUse)}`
      : `/natura/${encodeURIComponent(bizRoute)}`;

    if (btnSelfService) btnSelfService.href = editUrl;
    if (btnPublic) btnPublic.href = publicUrl;

    setWizardStep(3);
  }

  // --- TOGGLES DE UI ---
  window.toggleOptionalFields = function() {
    const container = document.getElementById("optional-fields-container");
    const chevron = document.getElementById("optional-chevron");
    const label = document.getElementById("optional-fields-label");
    if (!container) return;
    const isHidden = container.classList.contains("hidden");
    container.classList.toggle("hidden", !isHidden);
    if (chevron) chevron.style.transform = isHidden ? "rotate(180deg)" : "rotate(0deg)";
    if (label) label.textContent = isHidden ? "- Ocultar datos adicionales" : "+ Datos adicionales (Opcional: Titular y correo)";
    if (window.lucide) lucide.createIcons();
  };

  window.toggleCouponBox = function() {
    const container = document.getElementById("coupon-container");
    const chevron = document.getElementById("coupon-chevron");
    if (!container) return;
    const isHidden = container.classList.contains("hidden");
    container.classList.toggle("hidden", !isHidden);
    if (chevron) chevron.style.transform = isHidden ? "rotate(180deg)" : "rotate(0deg)";
    if (window.lucide) lucide.createIcons();
  };

  // --- API PÚBLICA DEL MODAL ---
  function openRegisterModal(preselectedCat) {
    const modal = mountRegisterModal();
    if (!modal) return;

    let targetCat = preselectedCat;
    if (!targetCat) {
      if (typeof currentCategorySlug !== "undefined" && currentCategorySlug && currentCategorySlug !== "all") {
        targetCat = currentCategorySlug;
      } else {
        const path = (window.location.pathname || "").toLowerCase();
        for (const k of Object.keys(SUBCATEGORIES_MAP)) {
          if (path.includes(k)) {
            targetCat = k;
            break;
          }
        }
      }
    }

    if (targetCat) {
      const catSelect = document.getElementById("reg-category");
      if (catSelect) {
        catSelect.value = targetCat;
      }
    }
    syncSubcategoriesDropdown();
    setWizardStep(1);

    modal.classList.remove("hidden");
    modal.classList.add("flex");
    document.body.style.overflow = "hidden";
    if (window.lucide) lucide.createIcons();
  }

  function closeRegisterModal() {
    const modal = document.getElementById("register-modal");
    if (modal) {
      modal.classList.add("hidden");
      modal.classList.remove("flex");
    }
    document.body.style.overflow = "";
  }

  // Exponer a window
  window.openRegisterModal = openRegisterModal;
  window.closeRegisterModal = closeRegisterModal;
  window.syncSubcategoriesDropdown = syncSubcategoriesDropdown;
  window.selectRegistrationPlan = selectRegistrationPlan;
  window.submitMicroRegister = submitMicroRegister;
  window.triggerMercadoPagoPayment = triggerMercadoPagoPayment;
  window.handleApplyCoupon = handleApplyCoupon;
  window.setWizardStep = setWizardStep;

  // Auto-mount and URL query handling
  function initRegister() {
    mountRegisterModal();

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get("open_register") === "1" || urlParams.get("registro") === "1") {
      const cat = urlParams.get("cat");
      setTimeout(() => openRegisterModal(cat), 200);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initRegister);
  } else {
    initRegister();
  }

  // Cerrar con Escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      const modal = document.getElementById("register-modal");
      if (modal && !modal.classList.contains("hidden")) {
        closeRegisterModal();
      }
    }
  });

})();
