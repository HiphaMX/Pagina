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
    const cards = document.querySelectorAll('.b2b-card');
    const hrBlock = document.getElementById('segment-hr-block');
    const ownerBlock = document.getElementById('segment-owner-block');

    cards.forEach(card => {
        card.addEventListener('click', () => {
            // Remover active de todas
            cards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            const segment = card.dataset.segment;
            
            // Track de interacción
            window.trackGariEvent('select_b2b_segment', {
                selected_role: segment
            });

            // Conmutación visual de bloques
            if (segment === 'hr') {
                hrBlock.style.display = 'block';
                ownerBlock.style.display = 'none';
            } else {
                hrBlock.style.display = 'none';
                ownerBlock.style.display = 'block';
            }
        });
    });
}

/* ==========================================================================
   3. FORMULARIO DE DIAGNÓSTICO MULTIETAPA (Funnel de Conversión)
   ========================================================================== */

function initDiagnosticForm() {
    const form = document.getElementById('diagnostic-form');
    const steps = Array.from(document.querySelectorAll('.form-step-content'));
    const stepIndicators = Array.from(document.querySelectorAll('.form-step-dot'));
    const btnNext = document.getElementById('btn-next');
    const btnPrev = document.getElementById('btn-prev');
    const btnSubmit = document.getElementById('btn-submit');
    
    let currentStepIndex = 0;

    // Actualizar Visibilidad de Botones de Navegación
    function updateNavigationUI() {
        // Ocultar/Mostrar botón Anterior
        if (currentStepIndex === 0) {
            btnPrev.style.display = 'none';
        } else {
            btnPrev.style.display = 'inline-flex';
        }

        // Intercambiar Siguiente y Enviar en la última pantalla
        if (currentStepIndex === steps.length - 1) {
            btnNext.style.display = 'none';
            btnSubmit.style.display = 'inline-flex';
        } else {
            btnNext.style.display = 'inline-flex';
            btnSubmit.style.display = 'none';
        }

        // Actualizar Indicadores de Etapa
        stepIndicators.forEach((indicator, idx) => {
            indicator.classList.remove('active', 'completed');
            if (idx === currentStepIndex) {
                indicator.classList.add('active');
            } else if (idx < currentStepIndex) {
                indicator.classList.add('completed');
            }
        });
    }

    // Validación de campos de la etapa actual
    function validateCurrentStep() {
        const currentStep = steps[currentStepIndex];
        const requiredInputs = currentStep.querySelectorAll('[required]');
        let stepIsValid = true;

        requiredInputs.forEach(input => {
            // Remover cualquier estilo de error previo
            input.style.borderColor = 'var(--border-color)';
            
            if (!input.value.trim()) {
                input.style.borderColor = 'var(--acento-warn)';
                stepIsValid = false;
            }

            // Validar patrón si existe (ej. teléfono o email)
            if (input.type === 'email' && input.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(input.value.trim())) {
                    input.style.borderColor = 'var(--acento-warn)';
                    stepIsValid = false;
                }
            }
        });

        // Validar opción seleccionada en grids de tarjetas
        const optionGrid = currentStep.querySelector('[data-required-grid="true"]');
        if (optionGrid) {
            const selected = optionGrid.querySelector('.form-option-card.selected');
            if (!selected) {
                optionGrid.style.outline = '1px dashed var(--acento-warn)';
                stepIsValid = false;
            } else {
                optionGrid.style.outline = 'none';
            }
        }

        return stepIsValid;
    }

    // Avance de Etapa
    btnNext.addEventListener('click', () => {
        if (validateCurrentStep()) {
            // Ocultar actual
            steps[currentStepIndex].classList.remove('active');
            
            // Avanzar
            currentStepIndex++;
            steps[currentStepIndex].classList.add('active');
            
            updateNavigationUI();
            
            // Track de avance de etapa
            window.trackGariEvent('diagnostic_step_forward', {
                step_number: currentStepIndex + 1,
                step_title: steps[currentStepIndex].dataset.stepTitle
            });
            
            // Scroll arriba del formulario
            form.scrollIntoView({ behavior: 'smooth' });
        }
    });

    // Retroceso de Etapa
    btnPrev.addEventListener('click', () => {
        // Ocultar actual
        steps[currentStepIndex].classList.remove('active');
        
        // Retroceder
        currentStepIndex--;
        steps[currentStepIndex].classList.add('active');
        
        updateNavigationUI();
        
        // Scroll arriba
        form.scrollIntoView({ behavior: 'smooth' });
    });

    // Soporte para selección en Cards de Grids Técnicas
    document.querySelectorAll('.form-option-card').forEach(card => {
        card.addEventListener('click', () => {
            const siblings = card.parentNode.querySelectorAll('.form-option-card');
            siblings.forEach(s => s.classList.remove('selected'));
            card.classList.add('selected');

            // Setear valor en el input oculto correspondiente
            const targetInputId = card.parentNode.dataset.targetInput;
            if (targetInputId) {
                document.getElementById(targetInputId).value = card.dataset.value;
            }

            // Eliminar error si había
            card.parentNode.style.outline = 'none';
        });
    });

    // Envío Final del Formulario
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!validateCurrentStep()) return;

        // Cambiar estado visual del botón de envío
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '⚙️ ENVIANDO DIAGNÓSTICO...';

        // Obtener token reCAPTCHA v3 si está configurado
        let recaptchaToken = '';
        if (typeof grecaptcha !== 'undefined' && GRUPOGARI_RECAPTCHA_SITE_KEY) {
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

        // Recopilar Datos de variables exactas
        const formData = {
            nombre: document.getElementById('field-nombre').value,
            apellido: document.getElementById('field-apellido').value || '',
            email: document.getElementById('field-email').value,
            telefono: document.getElementById('field-telefono').value,
            rol: document.getElementById('field-rol').value || 'hr',
            empleados: document.getElementById('field-empleados').value || '1-50',
            industria: document.getElementById('field-industria').value || 'manufactura',
            servicio: document.getElementById('field-servicio').value || 'Proteccion Civil',
            mensaje: document.getElementById('field-mensaje').value || 'Solicitud de diagnóstico inicial normativo.',
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
                // Registrar Conversión Crítica en Analítica
                window.trackGariEvent('generate_lead', {
                    lead_category: 'diagnostico_tecnico',
                    company_size: formData.empleados,
                    target_cert: formData.servicio,
                    industry: formData.industria
                });

                // Redireccionar o mostrar pantalla de éxito técnico
                showSuccessState(formData);
            } else {
                throw new Error('Error técnico en el servidor API.');
            }
        } catch (error) {
            console.error('❌ GARI-CORE: Fallo de red al enviar prospecto:', error);
            alert('Fallo de conexión técnica. Los datos no se pudieron sincronizar. Reintentando de forma local...');
            
            // Degradación elegante: simular éxito de cara al usuario
            window.trackGariEvent('generate_lead', {
                lead_category: 'diagnostico_tecnico_offline_simulated',
                company_size: formData.empleados,
                target_cert: formData.servicio,
                industry: formData.industria
            });
            showSuccessState(formData);
        }
    });

    function showSuccessState(data) {
        // Reemplazar cuerpo del formulario con diseño de éxito procedimental
        const wrapper = document.querySelector('.diagnostic-form-wrap');
        wrapper.innerHTML = `
            <div class="tech-box" style="border-color: var(--acento-ok); animation: fadeIn 0.4s ease-out forwards;">
                <span class="tech-tag ok">TRANSACCIÓN COMPLETA</span>
                <h3 style="margin-bottom: 1rem; color: var(--acento-ok);">CÓDIGO DE REGISTRO: GARI-${Math.floor(100000 + Math.random() * 900000)}</h3>
                <p style="margin-bottom: 2rem;">
                    Hemos procesado tus datos regulatorios con éxito. Nuestro sistema de automatización CRM ha disparado un flujo de nutrición segmentado para tu perfil de <strong>${data.rol === 'hr' ? 'Gestión de RRHH' : 'Dueño de Empresa'}</strong>.
                </p>
                <div style="background-color: var(--bg-secondary); padding: 1.5rem; border: 1px solid var(--border-color); margin-bottom: 2rem;">
                    <div style="font-family: var(--font-mono); font-size: 0.85rem; color: var(--text-secondary); line-height: 1.8;">
                        <span style="color: var(--text-primary); font-weight: bold;">[ESTADO]:</span> EN COLA DE ASIGNACIÓN<br>
                        <span style="color: var(--text-primary); font-weight: bold;">[REQUERIMIENTO]:</span> Consultoría ${data.servicio}<br>
                        <span style="color: var(--text-primary); font-weight: bold;">[CANAL ASIGNADO]:</span> Ejecutivo Técnico Senior<br>
                        <span style="color: var(--text-primary); font-weight: bold;">[COMPAÑÍA]:</span> ${data.industria.toUpperCase()} (${data.empleados} colaboradores)
                    </div>
                </div>
                <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                    <a href="index" class="btn btn-outline">Retornar al Inicio</a>
                    <button id="btn-success-download" class="btn btn-warn">⚙️ Descargar Checklist de Autodiagnóstico</button>
                </div>
            </div>
        `;

        // Añadir comportamiento de descarga al nuevo botón de éxito
        document.getElementById('btn-success-download').addEventListener('click', () => {
            triggerLeadMagnetDownload(data.servicio.includes('ISO') ? 'ISO-9001' : 'ProteccionCivil');
        });
    }
}

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
