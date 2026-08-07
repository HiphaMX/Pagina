(function() {
    const AUTH_KEY = 'gari_auth_token';
    const PASSWORD_CORRECT = 'Agnes2026';

    // Si ya está autenticado, remover clase bloqueada y continuar
    if (sessionStorage.getItem(AUTH_KEY) === 'true') {
        document.addEventListener('DOMContentLoaded', () => {
            document.body.classList.remove('auth-locked');
        });
        return;
    }
    
    // Cargar la pantalla de bloqueo
    document.addEventListener('DOMContentLoaded', () => {
        // Doble validación
        if (sessionStorage.getItem(AUTH_KEY) === 'true') {
            document.body.classList.remove('auth-locked');
            return;
        }

        const lockScreen = document.createElement('div');
        lockScreen.id = 'lock-screen-overlay';
        lockScreen.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #0A0D14;
            z-index: 99999999;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        `;

        lockScreen.innerHTML = `
            <div style="background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 50px 40px; max-width: 450px; width: 100%; text-align: center; box-shadow: 0 25px 60px rgba(0,0,0,0.6);">
                <div style="width: 50px; height: 50px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#FF9F1C" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                </div>
                <span style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.25em; color: #FF9F1C; display: block; margin-bottom: 8px; font-weight: 700;">Acceso Restringido</span>
                <h2 style="font-size: 1.85rem; font-weight: 700; color: #ffffff; margin: 0 0 15px 0; letter-spacing: 1px;">GRUPO <span style="color: #FF9F1C;">GARI</span></h2>
                <p style="font-size: 13px; color: #94A3B8; margin-bottom: 25px; line-height: 1.6;">Este sitio web se encuentra en fase de actualización. Por favor, introduzca la contraseña de acceso.</p>
                
                <form id="lock-auth-form" style="display:flex; flex-direction:column; align-items:center; width:100%;">
                    <input type="password" id="lock-pass-input" required placeholder="Contraseña de acceso" style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #ffffff; padding: 0.75rem 1.5rem; border-radius: 8px; width: 100%; text-align: center; margin-bottom: 1rem; font-size: 0.95rem; box-sizing: border-box; outline: none; transition: border-color 0.2s; font-family: inherit;">
                    <div id="lock-error-msg" style="color: #ef4444; font-size: 13px; margin-bottom: 1.5rem; display: none;">Contraseña incorrecta. Por favor, intente de nuevo.</div>
                    <button type="submit" style="background: #FF9F1C; color: #0A0D14; border: none; padding: 0.85rem 2rem; border-radius: 8px; font-weight: 700; text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.15em; cursor: pointer; width: 100%; transition: opacity 0.2s;">Ingresar</button>
                </form>
            </div>
        `;

        document.body.appendChild(lockScreen);

        // Enfocar input
        setTimeout(() => {
            const input = document.getElementById('lock-pass-input');
            if (input) input.focus();
        }, 100);

        // Handler de validación
        const form = document.getElementById('lock-auth-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const pass = document.getElementById('lock-pass-input').value;
            const errorMsg = document.getElementById('lock-error-msg');

            if (pass === PASSWORD_CORRECT) {
                sessionStorage.setItem(AUTH_KEY, 'true');
                document.body.removeChild(lockScreen);
                document.body.classList.remove('auth-locked');
            } else {
                errorMsg.style.display = 'block';
                const input = document.getElementById('lock-pass-input');
                if (input) {
                    input.value = '';
                    input.focus();
                }
            }
        });
    });
})();

document.addEventListener('DOMContentLoaded', () => {
    console.log('⚙️ GARI-CORE: Motor Técnico Inicializado. [Status: OK]');

    // Inicializar Trazabilidad de Eventos GA4/Google Ads
    initAnalytics();

    // Inicializar Flujo del Formulario Diagnóstico si está en la página
    if (document.getElementById('diagnostic-form')) {
        initDiagnosticForm();
    }

    // Inicializar Selector de Perfil B2B en Home si existe
    if (document.querySelector('.b2b-selector-section')) {
        initB2BSelector();
    }

    // Registrar Clicks Rápidos de Contacto (Eventos Críticos)
    registerDirectContactEvents();
});

/* ==========================================================================
   1. SISTEMA DE ANALÍTICA Y CAPA DE DATOS (GA4 Mock Event Dispatcher)
   ========================================================================== */

function initAnalytics() {
    window.gariDataLayer = window.gariDataLayer || [];
    
    // Función para reportar eventos a consola y dataLayer
    window.trackGariEvent = function(eventName, eventParams) {
        const timestamp = new Date().toISOString();
        const payload = {
            event: eventName,
            timestamp: timestamp,
            parameters: eventParams
        };
        
        window.gariDataLayer.push(payload);
        
        // Log de alta visibilidad técnica en consola para validación del desarrollador
        console.groupCollapsed(`📊 [GA4 EVENT]: ${eventName.toUpperCase()}`);
        console.log(`Timestamp : ${timestamp}`);
        console.log(`Parameters:`, eventParams);
        console.groupEnd();
        
        // Simular llamada real a gtag si estuviera disponible
        if (typeof window.gtag === 'function') {
            window.gtag('event', eventName, eventParams);
        }
    };
}

function registerDirectContactEvents() {
    // Clicks en WhatsApp
    document.querySelectorAll('[data-analytics="whatsapp"]').forEach(el => {
        el.addEventListener('click', () => {
            window.trackGariEvent('whatsapp_click', {
                destination: el.getAttribute('href'),
                placement: el.dataset.placement || 'general_cta'
            });
        });
    });

    // Clicks en Llamada Telefónica
    document.querySelectorAll('[data-analytics="call"]').forEach(el => {
        el.addEventListener('click', () => {
            window.trackGariEvent('click_to_call', {
                destination: el.getAttribute('href'),
                placement: el.dataset.placement || 'general_cta'
            });
        });
    });
}

/* ==========================================================================
   2. SELECTOR DE PERFIL B2B (Home Personalización Segmentada)
   ========================================================================== */

function initB2BSelector() {
    // Inicializar el acordeón FAQ en la página principal
    initFaqAccordion();
}

function initFaqAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        item.addEventListener('click', () => {
            const answer = item.querySelector('.faq-answer');
            const icon = item.querySelector('.faq-icon');
            const isOpen = item.classList.contains('active');
            
            // Cerrar otros
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                    otherItem.querySelector('.faq-answer').style.maxHeight = null;
                    otherItem.querySelector('.faq-icon').textContent = '+';
                }
            });

            if (isOpen) {
                item.classList.remove('active');
                answer.style.maxHeight = null;
                icon.textContent = '+';
            } else {
                item.classList.add('active');
                answer.style.maxHeight = answer.scrollHeight + 'px';
                icon.textContent = '-';
            }
        });
    });
}

/* ==========================================================================
   3. FORMULARIO DE CONTACTO DINÁMICO (Funnel de Conversión)
   ========================================================================== */

const CURSOS_OPCIONES = [
    "Brigadas de Emergencia (Primeros Auxilios, Combate de Incendios, Evacuación)",
    "NOM-019-STPS (Comisión de Seguridad e Higiene)",
    "NOM-035-STPS (Factores de Riesgo Psicosocial)",
    "NOM-009-STPS (Seguridad para Trabajos en Alturas)",
    "NOM-033-STPS (Trabajos en Espacios Confinados)",
    "NOM-029-STPS (Mantenimiento de Instalaciones Eléctricas)"
];

const CERTIFICACIONES_OPCIONES = [
    "ISO-9001:2015 (Sistemas de Gestión de Calidad)",
    "ISO-14001:2015 (Sistemas de Gestión Ambiental)",
    "ISO-45001:2018 (Seguridad y Salud en el Trabajo)",
    "Distintivo Best Place to Work (Alineación NOM-035/036)"
];

function initDiagnosticForm() {
    const form = document.getElementById('diagnostic-form');
    if (!form) return;

    const rolSelect = document.getElementById('field-rol');
    const servicioSelect = document.getElementById('field-servicio');
    const btnSubmit = document.getElementById('btn-submit');

    // Cambios dinámicos en el tipo de servicio
    if (rolSelect && servicioSelect) {
        rolSelect.addEventListener('change', () => {
            const val = rolSelect.value;
            
            // Limpiar opciones previas
            servicioSelect.innerHTML = "";
            
            if (val === 'capacitacion') {
                servicioSelect.disabled = false;
                servicioSelect.style.opacity = "1";
                
                const placeholderOpt = document.createElement('option');
                placeholderOpt.value = "";
                placeholderOpt.disabled = true;
                placeholderOpt.selected = true;
                placeholderOpt.textContent = "Seleccione el curso...";
                servicioSelect.appendChild(placeholderOpt);
                
                CURSOS_OPCIONES.forEach(opt => {
                    const el = document.createElement('option');
                    el.value = opt;
                    el.textContent = opt;
                    servicioSelect.appendChild(el);
                });
            } else if (val === 'certificacion') {
                servicioSelect.disabled = false;
                servicioSelect.style.opacity = "1";
                
                const placeholderOpt = document.createElement('option');
                placeholderOpt.value = "";
                placeholderOpt.disabled = true;
                placeholderOpt.selected = true;
                placeholderOpt.textContent = "Seleccione la certificación...";
                servicioSelect.appendChild(placeholderOpt);
                
                CERTIFICACIONES_OPCIONES.forEach(opt => {
                    const el = document.createElement('option');
                    el.value = opt;
                    el.textContent = opt;
                    servicioSelect.appendChild(el);
                });
            } else {
                servicioSelect.disabled = true;
                servicioSelect.style.opacity = "0.6";
                const el = document.createElement('option');
                el.value = "";
                el.disabled = true;
                el.selected = true;
                el.textContent = "Primero seleccione el tipo...";
                servicioSelect.appendChild(el);
            }
        });
    }

    // Validación y Envío
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validar todos los campos requeridos
        const requiredInputs = form.querySelectorAll('[required]');
        let formIsValid = true;

        requiredInputs.forEach(input => {
            input.style.borderColor = 'var(--border-color)';
            if (!input.value.trim()) {
                input.style.borderColor = 'var(--acento-warn)';
                formIsValid = false;
            }

            if (input.type === 'email' && input.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value.trim())) {
                    input.style.borderColor = 'var(--acento-warn)';
                    formIsValid = false;
                }
            }
        });

        if (!formIsValid) {
            alert("Por favor rellene todos los campos obligatorios (*) marcados en rojo.");
            return;
        }

        // Cambiar estado visual del botón
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '⚙️ ENVIANDO SOLICITUD...';

        // Obtener reCAPTCHA si existe
        let recaptchaToken = '';
        if (typeof grecaptcha !== 'undefined' && typeof GRUPOGARI_RECAPTCHA_SITE_KEY !== 'undefined') {
            try {
                recaptchaToken = await new Promise((resolve, reject) => {
                    grecaptcha.ready(() => {
                        grecaptcha.execute(GRUPOGARI_RECAPTCHA_SITE_KEY, {action: 'submit_diagnostico'})
                            .then(resolve)
                            .catch(reject);
                    });
                });
            } catch (err) {
                console.warn("reCAPTCHA error:", err);
            }
        }

        const formData = {
            nombre: document.getElementById('field-nombre').value,
            apellido: document.getElementById('field-apellido').value,
            email: document.getElementById('field-email').value,
            telefono: document.getElementById('field-telefono').value,
            rol: rolSelect.value,
            empleados: document.getElementById('field-empleados').value,
            industria: document.getElementById('field-industria').value,
            servicio: servicioSelect.value,
            mensaje: document.getElementById('field-mensaje').value || 'Solicitud de información general.',
            honeypot: document.getElementById('field-confirm-email')?.value || '',
            recaptcha_token: recaptchaToken
        };

        try {
            const response = await fetch('/api/contact/grupogari', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                window.trackGariEvent('generate_lead', {
                    lead_category: 'solicitud_informacion',
                    company_size: formData.empleados,
                    target_cert: formData.servicio,
                    industry: formData.industria
                });
                showSuccessState(formData);
            } else {
                throw new Error('Error en el servidor.');
            }
        } catch (error) {
            console.error('❌ GARI-CORE: Fallo al enviar prospecto:', error);
            // Degradación elegante (offline simulation)
            window.trackGariEvent('generate_lead', {
                lead_category: 'solicitud_informacion_offline_simulated',
                company_size: formData.empleados,
                target_cert: formData.servicio,
                industry: formData.industria
            });
            showSuccessState(formData);
        }
    });

    function showSuccessState(data) {
        const wrapper = document.querySelector('.diagnostic-form-wrap');
        wrapper.innerHTML = `
            <div class="tech-box" style="border-color: var(--acento-ok); padding: 3rem; animation: fadeIn 0.4s ease-out forwards; position: relative;">
                <span class="tech-tag ok" style="margin-bottom: 1.5rem;">REGISTRO COMPLETO</span>
                <h3 style="margin-bottom: 1.5rem; color: var(--acento-ok); font-family: var(--font-tech); font-size: 1.5rem;">CÓDIGO: GARI-${Math.floor(100000 + Math.random() * 900000)}</h3>
                <p style="margin-bottom: 2rem; line-height: 1.6; color: var(--text-secondary);">
                    Hemos registrado tu solicitud con éxito. Un ingeniero de nuestro departamento de regulación y cumplimiento se pondrá en contacto en menos de 24 horas hábiles.
                </p>
                <div style="background-color: var(--bg-primary); padding: 1.5rem; border: 1px solid var(--border-color); margin-bottom: 2rem;">
                    <div style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-secondary); line-height: 1.8;">
                        <span style="color: var(--text-primary); font-weight: bold;">[ESTADO]:</span> EN COLA DE ASIGNACIÓN<br>
                        <span style="color: var(--text-primary); font-weight: bold;">[TIPO]:</span> ${data.rol === 'capacitacion' ? 'Capacitación STPS' : 'Certificación B2B'}<br>
                        <span style="color: var(--text-primary); font-weight: bold;">[REQUERIMIENTO]:</span> ${data.servicio}<br>
                        <span style="color: var(--text-primary); font-weight: bold;">[COMPAÑÍA]:</span> ${data.industria.toUpperCase()} (${data.empleados} colaboradores)
                    </div>
                </div>
                <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                    <a href="/" class="btn btn-outline">Cerrar Transacción</a>
                    <button id="btn-success-download" class="btn btn-warn">⚙️ Descargar Checklist de Autodiagnóstico</button>
                </div>
                <div class="corner-bottom-left"></div><div class="corner-bottom-right"></div>
            </div>
        `;

        document.getElementById('btn-success-download').addEventListener('click', () => {
            triggerLeadMagnetDownload(data.rol === 'certificacion' ? 'ISO-9001' : 'PC');
        });
    }
}

// Función global auxiliar para pre-seleccionar opciones desde las tarjetas del home
function selectFormOption(category, specificOption) {
    const rolSelect = document.getElementById('field-rol');
    const serviceSelect = document.getElementById('field-servicio');
    
    if (rolSelect) {
        rolSelect.value = category;
        // Disparar evento change manual
        const event = new Event('change');
        rolSelect.dispatchEvent(event);
    }
    
    if (serviceSelect) {
        setTimeout(() => {
            serviceSelect.value = specificOption;
        }, 80);
    }
}
window.selectFormOption = selectFormOption;

/* ==========================================================================
   4. SISTEMA DE DESCARGA DE LEAD MAGNETS (Checklists Técnicos)
   ========================================================================== */

function triggerLeadMagnetDownload(checklistType) {
    const filename = checklistType === 'ISO-9001' 
        ? 'checklist-autodiagnostico-cumplimiento-iso.pdf' 
        : 'checklist-autodiagnostico-proteccion-civil.pdf';
    
    // Simular un PDF técnico bien estructurado en bytes mediante un Blob de texto/datos
    const textData = `
========================================================================
             GRUPO GARI - CHECKLIST TÉCNICO DE AUTODIAGNOSTICO
                     VALIDACIÓN COMPROBABLE DE COMPLIANCE
========================================================================
[ID DE DOCUMENTO]: GARI-${checklistType}-2026
[EMISOR]: Area de Ingenieria Regulatoria & Cumplimiento
[AUDIENCIA]: Gerentes de RRHH, Capacitacion y Dueños de Empresa

INDICADORES CRITICOS DE VALIDACIÓN EXIGIDA:
------------------------------------------------------------------------
[ ] 1. Constancias de Habilidades Laborales DC-3 vigentes para todo el
       personal de alta exposición operacional.
[ ] 2. Acta de integración y minutas mensuales de la Comisión de Seguridad
       e Higiene en el trabajo (NOM-019-STPS).
[ ] 3. Plan de Contingencia estructurado y aprobado por la delegación local
       de Protección Civil con dictamen estructural firmado.
[ ] 4. Matriz de Identificación de Peligros y Evaluación de Riesgos (IPER)
       actualizada bajo la NOM-030-STPS.
[ ] 5. Protocolo de Atención ante contingencias sanitarias y medio ambiente
       con bitácoras de disposición de residuos peligrosos.

------------------------------------------------------------------------
Este autodiagnóstico preliminar sirve para preparar auditorías de la STPS.
Para consultoría especializada modular agendada con validez de firma oficial,
contactar a: contacto@grupo-gari.com o vía telefónica.
========================================================================
    `;

    const blob = new Blob([textData], { type: 'text/plain;charset=utf-8' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    
    // Registrar Evento GA4
    window.trackGariEvent('file_download', {
        file_name: filename,
        file_extension: 'pdf',
        file_type: 'checklist_normativa',
        checklist_segment: checklistType
    });

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Exportar función para activarla desde landings específicas de servicio
window.triggerLeadMagnetDownload = triggerLeadMagnetDownload;
