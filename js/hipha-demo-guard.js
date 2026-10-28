/**
 * 🛡️ Hipha Demo Guard — Script Modular de Protección para Proyectos en Standby
 * 
 * USO RÁPIDO EN CUALQUIER LANDING O PROYECTO:
 * <script src="/js/hipha-demo-guard.js" data-project="Nombre del Proyecto" data-phone="523336762545"></script>
 * 
 * O con valores por defecto:
 * <script src="/js/hipha-demo-guard.js"></script>
 */

(function () {
  'use strict';

  // 1. Obtener parámetros del script actual o valores por defecto
  const currentScript = document.currentScript || document.querySelector('script[src*="hipha-demo-guard"]');
  const defaultProjectName = document.title ? document.title.split('|')[0].split('—')[0].trim() : 'este proyecto';
  const projectName = (currentScript && currentScript.getAttribute('data-project')) || defaultProjectName;
  const phoneNumber = (currentScript && currentScript.getAttribute('data-phone')) || '523336762545';
  const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(`Hola Hipha, me comunico desde el demo de ${projectName}.`)}`;

  // 2. Inyectar estilos CSS autónomos del Modo Demo Gráfico
  function injectStyles() {
    if (document.getElementById('hipha-demo-guard-styles')) return;

    const style = document.createElement('style');
    style.id = 'hipha-demo-guard-styles';
    style.textContent = `
      /* --- DESACTIVACIÓN DE HIPERVÍNCULOS (MUESTRA GRÁFICA) --- */
      a:not(.hipha-demo-wa-btn):not(.hipha-demo-pill-wa):not([href*="${phoneNumber}"]) {
        pointer-events: none !important;
        cursor: default !important;
      }

      /* Ocultar botones flotantes de WhatsApp externos del cliente para evitar superposición */
      .floating-whatsapp, .whatsapp-float, .floating-wa, [class*="floating-whatsapp"] {
        display: none !important;
      }

      /* En modo demo gráfico, los botones de envío de formularios no procesan leads */
      form button[type="submit"]:not(.hipha-demo-wa-btn), form input[type="submit"] {
        cursor: pointer !important;
      }

      /* --- COMPATIBILIDAD CON CURSORES PERSONALIZADOS & TOP-LAYER --- */
      body.hipha-demo-modal-open,
      body.hipha-demo-modal-open * {
        cursor: auto !important;
      }

      body.hipha-demo-modal-open a,
      body.hipha-demo-modal-open button,
      body.hipha-demo-modal-open [role="button"],
      body.hipha-demo-modal-open input,
      body.hipha-demo-modal-open select {
        cursor: pointer !important;
      }

      body.hipha-demo-modal-open .custom-cursor-dot,
      body.hipha-demo-modal-open .custom-cursor-ring,
      body.hipha-demo-modal-open [class*="custom-cursor"],
      body.hipha-demo-modal-open [class*="cursor-dot"],
      body.hipha-demo-modal-open [class*="cursor-ring"] {
        opacity: 0 !important;
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
      }

      dialog.hipha-demo-dialog,
      dialog.hipha-demo-dialog *,
      dialog.hipha-demo-dialog::backdrop {
        cursor: auto !important;
      }

      dialog.hipha-demo-dialog button,
      dialog.hipha-demo-dialog a,
      dialog.hipha-demo-dialog .hipha-demo-close-x,
      dialog.hipha-demo-dialog .hipha-demo-wa-btn,
      dialog.hipha-demo-dialog .hipha-demo-explore-btn,
      .hipha-demo-pill,
      .hipha-demo-pill * {
        cursor: pointer !important;
      }

      /* --- DIALOG MODAL DEMO GRÁFICO --- */
      dialog.hipha-demo-dialog {
        position: fixed;
        inset: 0;
        margin: auto;
        border: 1px solid rgba(255, 255, 255, 0.16);
        border-radius: 24px;
        background: #0f1f33;
        color: #f8fafc;
        max-width: 520px;
        width: calc(100% - 32px);
        max-height: 90vh;
        overflow-y: auto;
        padding: 0;
        box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 0 1px rgba(255, 255, 255, 0.1);
        z-index: 100000;
        opacity: 0;
        transform: scale(0.95) translateY(12px);
        transition: opacity 0.35s cubic-bezier(0.16, 1, 0.3, 1), transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      }

      dialog.hipha-demo-dialog[open] {
        opacity: 1;
        transform: scale(1) translateY(0);
      }

      dialog.hipha-demo-dialog.closing {
        opacity: 0;
        transform: scale(0.96) translateY(8px);
      }

      dialog.hipha-demo-dialog::backdrop {
        background: rgba(3, 10, 20, 0.65);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        opacity: 0;
        transition: opacity 0.35s ease;
      }

      dialog.hipha-demo-dialog[open]::backdrop {
        opacity: 1;
      }

      dialog.hipha-demo-dialog.closing::backdrop {
        opacity: 0;
      }

      .hipha-demo-inner {
        padding: 32px 28px 28px;
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 18px;
        text-align: left;
      }

      .hipha-demo-close-x {
        position: absolute;
        top: 18px;
        right: 18px;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 1px solid rgba(255, 255, 255, 0.14);
        background: rgba(255, 255, 255, 0.06);
        color: #94a3b8;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .hipha-demo-close-x:hover {
        background: rgba(255, 255, 255, 0.16);
        color: #ffffff;
        transform: rotate(90deg);
      }

      .hipha-demo-title {
        font-size: 1.6rem;
        font-weight: 700;
        line-height: 1.25;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin: 0;
      }

      .hipha-demo-desc {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #cbd5e1;
        margin: 0;
      }

      .hipha-demo-info-box {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 16px;
        display: flex;
        flex-direction: column;
        gap: 8px;
        font-size: 0.82rem;
        color: #94a3b8;
      }

      .hipha-demo-info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .hipha-demo-info-label {
        font-family: monospace;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
      }

      .hipha-demo-info-val {
        font-weight: 600;
        color: #e2e8f0;
      }

      .hipha-demo-actions {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 6px;
      }

      .hipha-demo-wa-btn {
        display: flex !important;
        align-items: center;
        justify-content: center;
        gap: 10px;
        width: 100%;
        padding: 15px 22px;
        border-radius: 14px;
        background: #25d366 !important;
        color: #052414 !important;
        font-weight: 700;
        font-size: 1.05rem;
        text-decoration: none;
        border: none;
        cursor: pointer !important;
        pointer-events: auto !important;
        box-shadow: 0 8px 25px -4px rgba(37, 211, 102, 0.45);
        transition: all 0.25s ease;
      }

      .hipha-demo-wa-btn:hover {
        background: #20ba59 !important;
        transform: translateY(-2px);
        box-shadow: 0 12px 30px -4px rgba(37, 211, 102, 0.6);
        color: #052414 !important;
      }

      .hipha-demo-explore-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 12px 18px;
        border-radius: 12px;
        background: transparent;
        color: #94a3b8;
        font-size: 0.88rem;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.14);
        cursor: pointer;
        transition: all 0.2s ease;
      }

      .hipha-demo-explore-btn:hover {
        background: rgba(255, 255, 255, 0.08);
        color: #f8fafc;
        border-color: rgba(255, 255, 255, 0.28);
      }

      /* --- FLOATING PILL --- */
      .hipha-demo-pill {
        position: fixed;
        bottom: 24px;
        right: 24px;
        display: inline-flex;
        align-items: center;
        gap: 10px;
        padding: 10px 18px;
        background: #0f1f33;
        border: 1px solid rgba(245, 158, 11, 0.45);
        border-radius: 999px;
        color: #f8fafc;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 12px 30px -6px rgba(0, 0, 0, 0.65);
        z-index: 99995;
        cursor: pointer;
        transition: all 0.25s ease;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      }

      .hipha-demo-pill:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 36px -6px rgba(0, 0, 0, 0.8);
        border-color: #25d366;
      }

      .hipha-demo-pill-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #f59e0b;
        box-shadow: 0 0 10px #f59e0b;
        animation: hipha-dot-pulse 2s infinite;
      }

      @keyframes hipha-dot-pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.85); }
      }

      .hipha-demo-pill-wa {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: #25d366;
        color: #052414;
        pointer-events: auto !important;
        cursor: pointer !important;
      }

      @media (max-width: 600px) {
        dialog.hipha-demo-dialog {
          max-width: 92%;
          border-radius: 20px;
        }
        .hipha-demo-inner {
          padding: 24px 20px 20px;
        }
        .hipha-demo-title {
          font-size: 1.35rem;
        }
        .hipha-demo-wa-btn {
          font-size: 0.95rem;
          padding: 13px 18px;
        }
        .hipha-demo-pill {
          bottom: 16px;
          right: 16px;
          padding: 8px 14px;
          font-size: 0.78rem;
        }
      }
    `;
    document.head.appendChild(style);
  }

  // 3. Inyectar Dialog Modal e Insignia Flotante
  function initDemoUI() {
    injectStyles();

    // Dialog Modal
    let dialog = document.getElementById('hipha-demo-dialog');
    if (!dialog) {
      dialog = document.createElement('dialog');
      dialog.id = 'hipha-demo-dialog';
      dialog.className = 'hipha-demo-dialog';
      dialog.setAttribute('aria-labelledby', 'hipha-demo-title');
      dialog.setAttribute('closedby', 'any');
      dialog.innerHTML = `
        <div class="hipha-demo-inner">
          <button type="button" class="hipha-demo-close-x" id="hipha-demo-close-x" aria-label="Cerrar aviso y ver demo gráfico">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>

          <h2 class="hipha-demo-title" id="hipha-demo-title">
            Propuesta Web · Demo Gráfico
          </h2>

          <p class="hipha-demo-desc">
            Este sitio web es un prototipo funcional y propuesta conceptual desarrollada por <strong>Hipha</strong> para <strong>${projectName}</strong>. Actualmente este proyecto se encuentra en pausa operativa (standby) para evaluación.
          </p>

          <div class="hipha-demo-info-box">
            <div class="hipha-demo-info-row">
              <span class="hipha-demo-info-label">Desarrollo</span>
              <span class="hipha-demo-info-val">Hipha</span>
            </div>
          </div>

          <div class="hipha-demo-actions">
            <a href="${whatsappUrl}" 
               target="_blank" 
               rel="noopener noreferrer" 
               class="hipha-demo-wa-btn"
               id="hipha-demo-whatsapp-cta">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.669-.699c.983.541 1.777.781 2.791.781 3.182 0 5.768-2.587 5.768-5.766.001-3.181-2.585-5.767-5.768-5.767zm7.553 5.766c-.001 4.165-3.39 7.554-7.553 7.554-1.258 0-2.457-.319-3.522-.888l-4.509 1.182 1.205-4.398c-.663-1.127-1.026-2.433-1.026-3.791.001-4.165 3.39-7.553 7.553-7.553 4.164 0 7.552 3.388 7.552 7.554z"/>
              </svg>
              <span>contactarme con Hipha</span>
            </a>

            <button type="button" class="hipha-demo-explore-btn" id="hipha-demo-explore-action">
              <span>Ver Demo Gráfico</span>
            </button>
          </div>
        </div>
      `;
      document.body.appendChild(dialog);
    }

    // Floating Pill
    let pill = document.getElementById('hipha-demo-pill');
    if (!pill) {
      pill = document.createElement('div');
      pill.id = 'hipha-demo-pill';
      pill.className = 'hipha-demo-pill';
      pill.setAttribute('role', 'button');
      pill.setAttribute('tabindex', '0');
      pill.setAttribute('aria-label', 'Información de Demo Gráfico - Contactar Hipha');
      pill.innerHTML = `
        <span class="hipha-demo-pill-dot"></span>
        <span>Demo Gráfico</span>
        <a href="${whatsappUrl}" 
           target="_blank" 
           rel="noopener noreferrer" 
           class="hipha-demo-pill-wa" 
           title="Contactarme con Hipha por WhatsApp"
           onclick="event.stopPropagation();">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.669-.699c.983.541 1.777.781 2.791.781 3.182 0 5.768-2.587 5.768-5.766.001-3.181-2.585-5.767-5.768-5.767zm7.553 5.766c-.001 4.165-3.39 7.554-7.553 7.554-1.258 0-2.457-.319-3.522-.888l-4.509 1.182 1.205-4.398c-.663-1.127-1.026-2.433-1.026-3.791.001-4.165 3.39-7.553 7.553-7.553 4.164 0 7.552 3.388 7.552 7.554z"/>
          </svg>
        </a>
      `;
      pill.style.display = 'none';
      document.body.appendChild(pill);
    }

    // Manejadores de apertura y cierre
    const closeBtn = document.getElementById('hipha-demo-close-x');
    const exploreBtn = document.getElementById('hipha-demo-explore-action');

    function openModal() {
      document.body.classList.add('hipha-demo-modal-open');
      if (pill) pill.style.display = 'none';
      if (typeof dialog.showModal === 'function') {
        dialog.showModal();
      } else {
        dialog.setAttribute('open', '');
      }
    }

    function closeModal() {
      dialog.classList.add('closing');
      setTimeout(() => {
        if (typeof dialog.close === 'function') {
          dialog.close();
        } else {
          dialog.removeAttribute('open');
        }
        dialog.classList.remove('closing');
        document.body.classList.remove('hipha-demo-modal-open');
        if (pill) pill.style.display = 'inline-flex';
      }, 350);
    }

    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (exploreBtn) exploreBtn.addEventListener('click', closeModal);

    dialog.addEventListener('click', (e) => {
      if (e.target === dialog) closeModal();
    });

    dialog.addEventListener('cancel', () => {
      document.body.classList.remove('hipha-demo-modal-open');
      if (pill) pill.style.display = 'inline-flex';
    });

    pill.addEventListener('click', openModal);
    pill.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openModal();
      }
    });

    // 4. Neutralizar todos los hipervínculos para modo Demo Gráfico (excepto WhatsApp de Hipha)
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a');
      if (!link) return;
      if (link.href && link.href.includes(phoneNumber)) {
        return; // Permitir enlace hacia WhatsApp de Hipha
      }
      e.preventDefault();
      e.stopPropagation();
    }, true);

    // 5. Bloquear envíos de formularios para evitar captura no autorizada de leads
    document.addEventListener('submit', (e) => {
      e.preventDefault();
      e.stopPropagation();
      openModal();
    }, true);

    // 6. Apertura suave tras carga
    setTimeout(() => {
      openModal();
    }, 600);
  }

  // Inicializar al cargar el DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDemoUI);
  } else {
    initDemoUI();
  }
})();
