/**
 * epicentro-search.js - Motor de Búsqueda Inteligente para Epizentro Natura
 *
 * Características:
 *  1. Normalización diacrítica (insensible a acentos: chillon == chillón, pizzeria == pizzería)
 *  2. Búsqueda multitoken por palabras clave independientes (ej. "salsa chillon natura")
 *  3. Indexación profunda del corpus: nombres, categorías, productos de micrositio y cotos
 *  4. Dropdown interactivo de sugerencias en vivo (experiencia tipo Rappi / MercadoLibre)
 *  5. URLs limpias y normalizadas (/natura/categoria?cat=all&q=...)
 */

(function (window, document) {
  "use strict";

  // 1. NORMALIZACIÓN FONÉTICA Y DIACRÍTICA ROBUSTA
  function normalizeSearchText(str) {
    if (!str && str !== 0) return "";
    return String(str)
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "") // Remueve tildes y diacríticos
      .replace(/ñ/g, "n")              // Mapeo seguro de eñe para búsquedas sin tilde
      .replace(/[^\w\s]/g, " ")        // Reemplaza signos y puntuación por espacios
      .replace(/\s+/g, " ")            // Colapsa espacios múltiples
      .trim();
  }

  // 2. CONSTRUCCIÓN DEL CORPUS DE BÚSQUEDA DEL NEGOCIO
  function buildBusinessSearchCorpus(b) {
    if (!b) return "";
    const parts = [
      b.name,
      b.business_name,
      b.category_label,
      b.category_slug,
      b.subcategory_label,
      b.subcategory_slug,
      b.description,
      b.address,
      b.coto,
      b.coto_address,
      b.community_name,
      b.community_slug,
      b.space_label,
      b.type_label,
      b.type_slug,
      b.kam_name
    ];

    // Extraer productos y palabras clave desde microsite_data
    if (b.microsite_data) {
      let md = b.microsite_data;
      if (typeof md === "string") {
        try { md = JSON.parse(md); } catch (e) { md = null; }
      }
      if (md) {
        if (md.tagline) parts.push(md.tagline);
        if (md.featured_section) {
          if (md.featured_section.title) parts.push(md.featured_section.title);
          if (md.featured_section.description) parts.push(md.featured_section.description);
          if (Array.isArray(md.featured_section.products)) {
            md.featured_section.products.forEach(p => {
              if (p.name) parts.push(p.name);
              if (p.title) parts.push(p.title);
              if (p.desc) parts.push(p.desc);
              if (p.description) parts.push(p.description);
              if (p.tags) parts.push(Array.isArray(p.tags) ? p.tags.join(" ") : p.tags);
            });
          }
        }
      }
    }

    // Sinónimos y catálogo clave para comercios destacados y fundadores
    const normName = normalizeSearchText(b.name || b.business_name || "");
    if (normName.includes("chillon") || normName.includes("chile")) {
      parts.push("salsa salsas picante picantes macha habanero arbol tatemada negra cacahuates semillas botanas comida gourmet delivery");
    } else if (normName.includes("botica")) {
      parts.push("herbolaria adaptogenos tinturas extractos salud bienestar melena de leon hongo hongos relajacion insomnio estres concentracion gotas naturales medicina alternativa");
    } else if (normName.includes("amdi")) {
      parts.push("arquitectura arquitecto arquitecta planos render renders 3d diseno interior interiores interiorismo remodelacion consultoria residencial");
    }

    return normalizeSearchText(parts.filter(Boolean).join(" "));
  }

  // 3. MATCHER MULTITOKEN INTELIGENTE
  function matchBusinessSearch(b, queryText) {
    if (!queryText) return true;
    const qClean = normalizeSearchText(queryText);
    if (!qClean) return true;

    const tokens = qClean.split(" ").filter(t => t.length > 0);
    if (tokens.length === 0) return true;

    if (!b._searchCorpus) {
      b._searchCorpus = buildBusinessSearchCorpus(b);
    }

    // Coincidencia: Todos los tokens deben estar presentes en el corpus
    return tokens.every(token => b._searchCorpus.includes(token));
  }

  // 4. CONSTRUCTOR DE URLS NORMALIZADAS
  function getCategoryPageUrl(cat = "all", q = "", coto = "all") {
    const isEpizentroHost = window.location.hostname.includes("epizentro.com");
    const isSubfolder = window.location.pathname.includes("/categorias/") || window.location.href.includes("/categorias/");

    let basePath;
    if (isEpizentroHost) {
      basePath = "/natura/categoria";
    } else {
      basePath = isSubfolder ? "../categoria.html" : "categoria.html";
    }

    const params = new URLSearchParams();
    if (cat && cat !== "all") params.set("cat", cat);
    else if (cat === "all") params.set("cat", "all");

    if (q && q.trim()) params.set("q", q.trim());
    if (coto && coto !== "all") params.set("coto", coto);

    const qs = params.toString();
    return qs ? `${basePath}?${qs}` : basePath;
  }

  // 5. RESOLVER ENLACE DIRECTO DEL COMERCIO
  function resolveBusinessUrl(b) {
    const isSubfolder = window.location.pathname.includes("/categorias/") || window.location.href.includes("/categorias/");
    const prefix = isSubfolder ? "../" : "";
    const isEpizentroHost = window.location.hostname.includes("epizentro.com");

    const norm = normalizeSearchText(b.name || "");
    if (norm.includes("chillon") || b.id === "12c7bc70-34b8-4ef5-b884-d4f60ccf8d97") {
      return isEpizentroHost ? "/natura/chile-chillon" : `${prefix}chile-chillon.html`;
    }
    if (norm.includes("botica") || b.id === "reg-botica-silvestre" || b.id === "0a595ddc-4d7f-450b-81de-45d098c9e74e") {
      return isEpizentroHost ? "/natura/botica-silvestre" : `${prefix}botica-silvestre.html`;
    }
    if (norm.includes("amdi") || b.id === "ac02b6c2-624e-407f-bcfc-7d736dbcbd83") {
      return isEpizentroHost ? "/natura/amdi" : `${prefix}amdi.html`;
    }

    if (b.website && !b.website.startsWith("http")) {
      return isEpizentroHost ? `/natura/${b.website}` : `${prefix}${b.website}.html`;
    }

    // Fallback: abrir en directorio filtrado
    return getCategoryPageUrl(b.category_slug || "all", b.name);
  }

  // 6. RESALTAR COINCIDENCIAS VISUALES EN TEXTO
  function escapeHtml(str) {
    if (!str && str !== 0) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function highlightMatch(text, query) {
    if (!query || !text) return escapeHtml(text || "");
    const qClean = normalizeSearchText(query);
    if (!qClean) return escapeHtml(text);

    const tokens = qClean.split(" ").filter(t => t.length > 1);
    if (tokens.length === 0) return escapeHtml(text);

    let pattern;
    try {
      pattern = new RegExp(`(${tokens.map(t => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`, "gi");
    } catch (e) {
      return escapeHtml(text);
    }

    return escapeHtml(text).replace(pattern, '<mark class="bg-amber-200 text-slate-950 font-bold px-0.5 rounded">$1</mark>');
  }

  // 7. INICIALIZADOR DEL DROPDOWN EN VIVO EN EL NAVBAR
  function initNavbarLiveSearch() {
    const input = document.getElementById("search-input");
    if (!input) return;

    // Desactivar autocompletado nativo del navegador para no encimar el menú
    input.setAttribute("autocomplete", "off");
    input.setAttribute("spellcheck", "false");

    // Contenedor padre relativo de la barra de búsqueda
    const searchBarContainer = input.closest(".relative");
    if (!searchBarContainer) return;

    // Crear o recuperar el dropdown flotante
    let dropdown = document.getElementById("epicentro-search-dropdown");
    if (!dropdown) {
      dropdown = document.createElement("div");
      dropdown.id = "epicentro-search-dropdown";
      dropdown.className = "hidden absolute left-0 right-0 top-full mt-2 bg-white rounded-2xl border border-snow-400 shadow-2xl z-50 overflow-hidden text-left divide-y divide-snow-300 max-h-[80vh] overflow-y-auto";
      searchBarContainer.appendChild(dropdown);
    }

    let debounceTimer = null;

    function closeDropdown() {
      if (dropdown) dropdown.classList.add("hidden");
    }

    function renderDropdown(q) {
      if (!q || q.length < 1) {
        closeDropdown();
        return;
      }

      const allBiz = Array.isArray(window.ALL_BUSINESSES) ? window.ALL_BUSINESSES : [];
      const allCats = Array.isArray(window.ALL_CATEGORIES) ? window.ALL_CATEGORIES : [];
      const cotoSelect = document.getElementById("coto-select");
      const coto = cotoSelect ? cotoSelect.value : "all";

      // Filtrar comercios coincidentes
      const matchingBiz = allBiz.filter(b => {
        const matchCoto = (coto === "all") || (b.community_slug === coto);
        return matchCoto && matchBusinessSearch(b, q);
      });

      // Filtrar categorías coincidentes
      const qNorm = normalizeSearchText(q);
      const matchingCats = allCats.filter(c => {
        return normalizeSearchText(c.name).includes(qNorm) || normalizeSearchText(c.slug).includes(qNorm);
      });

      const hasResults = matchingBiz.length > 0 || matchingCats.length > 0;

      let html = "";

      if (!hasResults) {
        html = `
          <div class="p-5 text-center">
            <div class="w-10 h-10 rounded-xl bg-snow-300/70 text-slate-400 mx-auto flex items-center justify-center mb-2.5">
              <i data-lucide="search-x" class="w-5 h-5"></i>
            </div>
            <p class="text-xs font-bold text-slate-800">No encontramos coincidencias para "${escapeHtml(q)}"</p>
            <p class="text-[11px] text-slate-400 mt-1 max-w-xs mx-auto">Prueba con términos como <em>salsas, adaptógenos, planos, botica</em> o selecciona Toda la zona.</p>
            <div class="mt-3">
              <a href="${getCategoryPageUrl('all', q, coto)}" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-bold transition-colors">
                <span>Buscar en todo el directorio</span>
                <i data-lucide="arrow-right" class="w-3 h-3"></i>
              </a>
            </div>
          </div>
        `;
      } else {
        // Sección Comercios
        if (matchingBiz.length > 0) {
          const topBiz = matchingBiz.slice(0, 4);
          html += `
            <div class="p-2">
              <div class="px-3 py-1.5 text-[10px] font-black uppercase tracking-wider text-slate-400 flex items-center justify-between">
                <span>Comercios y Servicios (${matchingBiz.length})</span>
                <span class="text-indigo-600 font-bold">Natura</span>
              </div>
              <div class="space-y-1">
                ${topBiz.map(b => {
                  const url = resolveBusinessUrl(b);
                  const photo = (Array.isArray(b.photos) && b.photos[0]) || b.cover_photo || null;
                  const catLabel = b.category_label || (b.category_slug ? b.category_slug.toUpperCase() : "COMERCIO");
                  const cotoLabel = b.coto || b.community_name || "Natura";

                  return `
                    <a href="${url}" class="flex items-center gap-3 p-2 rounded-xl hover:bg-indigo-50/70 transition-colors group">
                      <div class="w-10 h-10 rounded-xl bg-white border border-snow-400 overflow-hidden shrink-0 flex items-center justify-center shadow-2xs">
                        ${photo ? `<img src="${photo}" alt="${escapeHtml(b.name)}" class="w-full h-full object-contain bg-white">` : `<i data-lucide="store" class="w-5 h-5 text-indigo-600"></i>`}
                      </div>
                      <div class="flex-1 min-w-0">
                        <div class="flex items-center gap-1.5">
                          <h4 class="text-xs font-bold text-slate-900 group-hover:text-indigo-600 truncate transition-colors">${highlightMatch(b.name, q)}</h4>
                          ${b.has_badge ? `<span class="shrink-0 text-[9px] font-black px-1.5 py-0.2 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">Verificado</span>` : ""}
                        </div>
                        <p class="text-[11px] text-slate-400 truncate mt-0.5">${highlightMatch(b.description || catLabel, q)}</p>
                      </div>
                      <div class="shrink-0 text-right hidden sm:block">
                        <span class="inline-block text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 border border-snow-400 truncate max-w-[120px]">${escapeHtml(cotoLabel)}</span>
                      </div>
                    </a>
                  `;
                }).join("")}
              </div>
            </div>
          `;
        }

        // Sección Categorías
        if (matchingCats.length > 0) {
          const topCats = matchingCats.slice(0, 3);
          html += `
            <div class="p-2 bg-slate-50/50">
              <div class="px-3 py-1 text-[10px] font-black uppercase tracking-wider text-slate-400">
                <span>Categorías</span>
              </div>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-1 mt-1">
                ${topCats.map(c => `
                  <a href="${getCategoryPageUrl(c.slug, '', coto)}" class="flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-white hover:shadow-2xs transition-all text-xs font-bold text-slate-700 hover:text-indigo-600">
                    <div class="w-6 h-6 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
                      <i data-lucide="${c.icon || 'tag'}" class="w-3.5 h-3.5"></i>
                    </div>
                    <span class="truncate">${highlightMatch(c.name, q)}</span>
                  </a>
                `).join("")}
              </div>
            </div>
          `;
        }

        // Pie: Ver todos los resultados
        html += `
          <div class="p-2.5 bg-slate-50 flex items-center justify-between text-xs font-bold">
            <span class="text-slate-500 text-[11px] pl-2">Presiona Enter para buscar</span>
            <a href="${getCategoryPageUrl('all', q, coto)}" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold transition-all shadow-sm">
              <span>Ver todos los resultados (${matchingBiz.length})</span>
              <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
            </a>
          </div>
        `;
      }

      dropdown.innerHTML = html;
      dropdown.classList.remove("hidden");
      if (window.lucide && lucide.createIcons) lucide.createIcons();
    }

    // Eventos del Input
    input.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      const q = e.target.value.trim();

      // Si existe función local de filtrado en la página (como categoria.html), ejecutarla
      if (typeof window.applyAllFilters === "function") {
        window.applyAllFilters();
      }

      debounceTimer = setTimeout(() => {
        renderDropdown(q);
      }, 120);
    });

    input.addEventListener("focus", (e) => {
      const q = e.target.value.trim();
      if (q.length >= 1) {
        renderDropdown(q);
      }
    });

    // Cerrar al presionar Escape o dar Enter
    input.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        closeDropdown();
      } else if (e.key === "Enter") {
        closeDropdown();
        // Si no estamos en categoria.html, redirigir
        if (!window.location.pathname.includes("categoria")) {
          const q = input.value.trim();
          const cotoSelect = document.getElementById("coto-select");
          const coto = cotoSelect ? cotoSelect.value : "all";
          window.location.href = getCategoryPageUrl("all", q, coto);
        }
      }
    });

    // Cerrar si se hace clic fuera del buscador
    document.addEventListener("click", (e) => {
      if (!searchBarContainer.contains(e.target)) {
        closeDropdown();
      }
    });
  }

  // Auto-iniciar al cargar el DOM
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initNavbarLiveSearch);
  } else {
    initNavbarLiveSearch();
  }

  // Exportar utilidades globales para reutilización transparente
  window.normalizeSearchText = normalizeSearchText;
  window.buildBusinessSearchCorpus = buildBusinessSearchCorpus;
  window.matchBusinessSearch = matchBusinessSearch;
  window.getCategoryPageUrl = getCategoryPageUrl;
  window.resolveBusinessUrl = resolveBusinessUrl;
  window.highlightMatch = highlightMatch;

  window.EpicentroSearch = {
    normalize: normalizeSearchText,
    buildCorpus: buildBusinessSearchCorpus,
    match: matchBusinessSearch,
    getUrl: getCategoryPageUrl,
    resolveUrl: resolveBusinessUrl,
    init: initNavbarLiveSearch
  };

})(window, document);
