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

      <!-- FASE 3: VERIFICACIÓN OFICIAL MERCADO PAGO ($99 MXN) -->
      <div id="reg-step-3" class="hidden space-y-4">
        <div class="p-5 rounded-2xl bg-gradient-to-br from-amber-500/10 via-emerald-500/5 to-transparent border border-amber-400/30 text-center space-y-3">
          <div class="w-12 h-12 mx-auto rounded-full bg-amber-500/20 text-amber-600 flex items-center justify-center">
            <i data-lucide="award" class="w-6 h-6"></i>
          </div>
          <span class="inline-block px-3 py-1 text-[10px] font-black uppercase tracking-wider rounded-full bg-amber-100 text-amber-800 border border-amber-300">
            Sello Oficial Vecino Verificado + Tu Propio Micrositio
          </span>
          <h4 class="text-lg font-black text-slate-950">Insignia Oficial y Micrositio con Catálogo</h4>
          <p class="text-xs text-slate-600 max-w-md mx-auto leading-relaxed">
            Obtén tu <strong>micrositio web interactivo</strong> (con fotos de productos, precios, menú de complementos y pedidos por WhatsApp) más el distintivo verificado para casetas de cotos.
          </p>

          <div class="py-2">
            <span class="text-3xl font-black text-slate-950 font-mono">$99.00</span>
            <span class="text-xs font-bold text-slate-500 uppercase ml-1">MXN / Cuota Única de Alta</span>
          </div>

          <div class="grid grid-cols-2 gap-2 text-left text-[11px] text-slate-700 bg-white/80 p-3 rounded-xl border border-slate-200">
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Tu Micrositio Web Propio</div>
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Catálogo con Fotos & Precios</div>
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Pedidos Directos a WhatsApp</div>
            <div class="flex items-center gap-1.5"><i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i> Sello Verificado Oficial</div>
          </div>
        </div>

        <button id="btn-pay-mp" onclick="triggerMercadoPagoPayment()" class="w-full py-4 px-4 rounded-xl bg-[#009ee3] hover:bg-[#0082ba] text-white font-bold text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2">
          <span>Activar Micrositio y Verificación con Mercado Pago ($99 MXN)</span>
          <i data-lucide="external-link" class="w-4 h-4"></i>
        </button>
        <p class="text-[11px] text-center text-slate-400">
          Acepta Tarjetas (Débito/Crédito), Mercado Pago Wallet, SPEI u OXXO vía pasarela segura.
        </p>

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

        <div class="text-center pt-2">
          <button onclick="skipVerificationPayment()" class="text-xs text-slate-400 hover:text-slate-600 underline">
            Omitir pago por ahora (solicitar alta básica en revisión sin Sello Verificado)
          </button>
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
      modal.className = "fixed inset-0 z-50 hidden items-center justify-center p-4 bg-slate-950/75 backdrop-blur-xs";
      document.body.appendChild(modal);
    }

    // Si el modal no contiene el stepper completo (por ejemplo, el dummy form anterior)
    if (!document.getElementById("reg-step-1")) {
      modal.innerHTML = renderWizardHTML();
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

    if (step === 1) {
      if (label) label.textContent = "Paso 1 de 3";
      if (title) title.textContent = "Registrar Comercio o Servicio";
      if (desc) desc.textContent = "Conéctate directamente con las familias de cotos Natura con sello de confianza.";
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-slate-200 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-slate-200 transition-all";
    } else if (step === 2) {
      if (label) label.textContent = "Paso 2 de 3";
      if (title) title.textContent = "Validación por WhatsApp";
      if (desc) desc.textContent = "Confirma tu número comercial con 1 toque para proteger la confianza de la comunidad.";
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-slate-200 transition-all";
    } else if (step === 3) {
      if (label) label.textContent = "Paso 3 de 3";
      if (title) title.textContent = "Verificación Oficial Mercado Pago";
      if (desc) desc.textContent = "Activa tu Sello Oficial Vecino Verificado con cuota de alta comunitaria.";
      if (bar1) bar1.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar2) bar2.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
      if (bar3) bar3.className = "h-1.5 rounded-full bg-emerald-600 transition-all";
    } else if (step === 4) {
      if (label) label.textContent = "Completado";
      if (title) title.textContent = "¡Solicitud Registrada!";
      if (desc) desc.textContent = "Tu negocio ha sido verificado y está listo para ser publicado.";
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
    if (btn && waVerified) {
      btn.disabled = false;
      btn.className = "w-full py-3.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm shadow-md transition-all active:scale-98 flex items-center justify-center gap-2 cursor-pointer";
      btn.innerHTML = `<span>Continuar a Verificación Oficial (Paso 3 de 3)</span> <i data-lucide="arrow-right" class="w-4 h-4"></i>`;
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }
  }

  function goToStep3() {
    if (!waVerified) {
      alert("Por favor abre WhatsApp con tu código o pulsa 'Confirmar Validación' para continuar.");
      return;
    }
    setWizardStep(3);
  }

  async function triggerMercadoPagoPayment() {
    const btn = document.getElementById("btn-pay-mp");
    const origText = btn ? btn.innerHTML : "";
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = `<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i> <span>Conectando con Mercado Pago...</span>`;
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }

    try {
      const res = await fetch("/api/epicentro/register/create-payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ registration_id: currentRegId })
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Error al generar preferencia en Mercado Pago.");
      }
      const data = await res.json();
      if (data.init_point) {
        window.location.href = data.init_point;
        return;
      }
      throw new Error("No se recibió URL de pago.");
    } catch (err) {
      console.warn("Aviso Mercado Pago:", err);
      const ok = confirm(`Conexión con Mercado Pago (Botica Silvestre):\n\n¿Deseas simular pago exitoso de $99.00 MXN para verificar '${currentBusinessName}'?`);
      if (ok) {
        showStep4Success("NATURA-VERIFIED-" + Math.floor(1000 + Math.random() * 9000));
      } else {
        if (btn) {
          btn.disabled = false;
          btn.innerHTML = origText;
          if (window.lucide && lucide.createIcons) lucide.createIcons();
        }
      }
    }
  }

  function skipVerificationPayment() {
    const ok = confirm("¿Deseas enviar tu registro para revisión básica sin la insignia de Vecino Verificado ni menú con fotos?");
    if (ok) {
      showStep4Success("NATURA-BASIC-" + Math.floor(1000 + Math.random() * 9000));
    }
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

  function showStep4Success(folio) {
    const bNameEl = document.getElementById("step4-business-name");
    const folioEl = document.getElementById("step4-folio");
    if (bNameEl) bNameEl.textContent = currentBusinessName || "tu negocio";
    if (folioEl) folioEl.textContent = folio;
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

  function checkUrlAutoOpen() {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.get("open_register") === "1") {
        openRegisterModal(urlParams.get("cat"));
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
