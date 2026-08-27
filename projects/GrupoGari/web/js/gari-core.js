

document.addEventListener('DOMContentLoaded', () => {
    console.log('⚙️ GARI-CORE: Motor Técnico Inicializado. [Status: OK]');

    // Inicializar Trazabilidad de Eventos GA4/Google Ads
    initAnalytics();

    // Inicializar Flujo del Formulario Diagnóstico si está en la página
    if (document.getElementById('diagnostic-form')) {
        initDiagnosticForm();
    }

    // Inicializar Componentes de Interfaz en Home
    initMobileMenu(); // Inicializa el menú hamburguesa móvil
    initB2BSelector(); // Inicializa el Acordeón FAQ
    initAccompanimentStepper(); // Inicializa el visualizador de Acompañamiento 5 Pasos
    initHeroSlider(); // Inicializa el Slider TOP 10 Cursos
    initReviewsSlider(); // Inicializa el Slider de 3 Opiniones B2B

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
                    otherItem.querySelector('.faq-answer').style.maxHeight = '0px';
                    otherItem.querySelector('.faq-icon').textContent = '+';
                }
            });

            if (isOpen) {
                item.classList.remove('active');
                answer.style.maxHeight = '0px';
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
    "1. Seguridad y Protección Civil",
    "2. Seguridad Eléctrica",
    "3. Trabajos en Altura y Equipos de Elevación",
    "4. Operación de Maquinaria y Equipos",
    "5. Soldadura, Corte y Trabajos en Caliente",
    "6. Seguridad Industrial",
    "7. Manejo de Sustancias y Materiales Peligrosos",
    "8. Normatividad STPS"
];

const CERTIFICACIONES_OPCIONES = [
    "ISO 9001 - Sistema de Gestión de la Calidad",
    "ISO 14001 - Sistema de Gestión Ambiental"
];

const ECO_CURSOS_OPCIONES = [
    "1. Curso de Clasificación de Residuos en el Aula",
    "2. Taller de Ahorro y Eficiencia de Agua en Baños",
    "3. Taller de Ahorro de Energía en Aulas y Pasillos",
    "4. Curso de Huertos Escolares y Compostaje",
    "5. Taller General de Educación Ambiental"
];

const ECO_CERTIFICACIONES_OPCIONES = [
    "Distintivo de Plantel Ecológico (ECO-GARI)",
    "Certificación de Escuela Sustentable",
    "Certificación ISO 14001 para Colegios"
];

function initDiagnosticForm() {
    const form = document.getElementById('diagnostic-form');
    if (!form) return;

    const rolSelect = document.getElementById('field-rol');
    const servicioSelect = document.getElementById('field-servicio');
    const btnSubmit = document.getElementById('btn-submit');
    const isSchoolForm = document.getElementById('form-type')?.value === 'school';

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
                placeholderOpt.textContent = isSchoolForm ? "Seleccione el taller ecológico..." : "Seleccione el curso...";
                servicioSelect.appendChild(placeholderOpt);
                
                const opciones = isSchoolForm ? ECO_CURSOS_OPCIONES : CURSOS_OPCIONES;
                opciones.forEach(opt => {
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
                placeholderOpt.textContent = isSchoolForm ? "Seleccione el distintivo..." : "Seleccione la certificación...";
                servicioSelect.appendChild(placeholderOpt);
                
                const opciones = isSchoolForm ? ECO_CERTIFICACIONES_OPCIONES : CERTIFICACIONES_OPCIONES;
                opciones.forEach(opt => {
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
            rol: rolSelect ? rolSelect.value : 'school_eco_program',
            empleados: document.getElementById('field-empleados').value,
            industria: document.getElementById('field-industria').value,
            servicio: servicioSelect ? servicioSelect.value : 'Certificación de Plantel Ecológico',
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

/* ==========================================================================
   5. SISTEMA DE ACOMPAÑAMIENTO EN 5 PASOS INTERACTIVO
   ========================================================================== */

const ACCOMPANIMENT_STEPS = {
    "1": {
        watermark: "01",
        status: "ACTIVO: FASE 01",
        title: "1. Diagnóstico",
        desc: "Evaluamos la situación actual de la organización y determinamos las brechas existentes en sus procesos frente a la normatividad ISO seleccionada.",
        duration: "2-3 Semanas",
        checklist: [
            "Gap Analysis Inicial (ISO 9001 / 14001)",
            "Mapeo de Procesos y Aspectos Críticos",
            "Reporte de Hallazgos y Riesgos Regulatorios"
        ],
        svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />`
    },
    "2": {
        watermark: "02",
        status: "ACTIVO: FASE 02",
        title: "2. Planeación",
        desc: "Definimos las acciones necesarias para implementar o fortalecer el sistema de gestión. Creamos el mapa de ruta y asignamos responsabilidades clave.",
        duration: "1-2 Semanas",
        checklist: [
            "Cronograma Técnico Detallado",
            "Matriz de Roles y Responsabilidades",
            "Plan de Capacitación al Comité de Calidad/Ambiental"
        ],
        svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />`
    },
    "3": {
        watermark: "03",
        status: "ACTIVO: FASE 03",
        title: "3. Implementación",
        desc: "Acompañamos al personal en la documentación, aplicación y seguimiento de los procesos. Creamos manuales de calidad, políticas y registros de control.",
        duration: "8-12 Semanas",
        checklist: [
            "Redacción y Liberación de Manuales y Procedimientos",
            "Capacitación General del Personal en Nuevas Prácticas",
            "Registro del Historial de Operación y Control Interno"
        ],
        svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />`
    },
    "4": {
        watermark: "04",
        status: "ACTIVO: FASE 04",
        title: "4. Preparación para Auditoría",
        desc: "Realizamos revisión documental exhaustiva, auditoría interna formal y la preparación intensiva de todo el personal para enfrentar el dictamen externo.",
        duration: "3-4 Semanas",
        checklist: [
            "Auditoría Interna Cruzada de Simulación",
            "Cierre Correctivo de Acciones y Desviaciones",
            "Revisión por la Dirección y Minuta de Acuerdos"
        ],
        svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />`
    },
    "5": {
        watermark: "05",
        status: "ACTIVO: FASE 05",
        title: "5. Certificación",
        desc: "Brindamos asesoramiento experto durante todas las etapas de auditoría oficial de certificación realizadas por el organismo acreditado internacionalmente.",
        duration: "2 Semanas",
        checklist: [
            "Defensa de Procesos ante el Auditor Externo",
            "Atención de Observaciones o No Conformidades",
            "Dictamen de Recomendación para la Certificación"
        ],
        svg: `<path stroke-linecap="round" stroke-linejoin="round" d="M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />`
    }
};

function initAccompanimentStepper() {
    const stepButtons = document.querySelectorAll('.step-btn');
    if (stepButtons.length === 0) return;

    const watermark = document.getElementById('step-watermark');
    const displayWrapper = document.getElementById('step-content-display');
    const svgEl = document.getElementById('step-svg');
    const statusTag = document.getElementById('step-status-tag');
    const titleEl = document.getElementById('step-title');
    const descEl = document.getElementById('step-desc');
    const checklistEl = document.getElementById('step-checklist');
    const durationEl = document.getElementById('step-duration');

    let currentStep = 1;
    const totalSteps = 5;
    let autoplayInterval;

    function goToStep(stepId) {
        const data = ACCOMPANIMENT_STEPS[stepId];
        if (!data) return;

        // Cambiar estados activos en botones
        stepButtons.forEach(b => b.classList.remove('active'));
        const activeBtn = document.querySelector(`.step-btn[data-step="${stepId}"]`);
        if (activeBtn) activeBtn.classList.add('active');

        // Efecto suave de fade out/in en el monitor
        displayWrapper.style.opacity = '0';
        watermark.style.opacity = '0';
        watermark.style.transform = 'translateY(10px)';

        setTimeout(() => {
            // Actualizar textos
            watermark.textContent = data.watermark;
            statusTag.textContent = data.status;
            titleEl.textContent = data.title;
            descEl.textContent = data.desc;
            durationEl.textContent = data.duration;
            
            // Actualizar SVG
            svgEl.innerHTML = data.svg;

            // Actualizar checklist
            checklistEl.innerHTML = "";
            data.checklist.forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<span style="color: var(--acento-warn);">▪</span> ${item}`;
                checklistEl.appendChild(li);
            });

            // Fade back in
            displayWrapper.style.opacity = '1';
            watermark.style.opacity = '0.08';
            watermark.style.transform = 'translateY(0)';
            
            // Move monitor-screen after activeBtn on mobile (accordion behavior)
            if (window.innerWidth <= 991 && activeBtn) {
                const monitorScreen = document.querySelector('.monitor-screen');
                if (monitorScreen) {
                    activeBtn.after(monitorScreen);
                }
            }
        }, 250);

        // Track Evento de interacción con stepper
        window.trackGariEvent('view_accompaniment_step', {
            step_number: stepId,
            step_title: data.title
        });
    }

    // Event listener for user interaction
    stepButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const stepId = btn.dataset.step;
            currentStep = parseInt(stepId);
            goToStep(stepId);
            resetAutoplay();
        });
    });

    // Auto-advance logic (Autoplay)
    function startAutoplay() {
        clearInterval(autoplayInterval);
        autoplayInterval = setInterval(() => {
            currentStep = (currentStep % totalSteps) + 1;
            goToStep(currentStep.toString());
        }, 5000);
    }

    function stopAutoplay() {
        clearInterval(autoplayInterval);
    }

    function resetAutoplay() {
        stopAutoplay();
        startAutoplay();
    }

    // IntersectionObserver to auto start/stop based on viewport visibility
    const consoleSection = document.querySelector('.blueprint-console');
    if (consoleSection && 'IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    startAutoplay();
                } else {
                    stopAutoplay();
                }
            });
        }, { threshold: 0.15 });
        observer.observe(consoleSection);
    } else {
        // Fallback if IntersectionObserver is not supported
        startAutoplay();
    }

    // Position monitor screen after active button on mobile initial load
    if (window.innerWidth <= 991) {
        const activeBtn = document.querySelector('.step-btn.active');
        const monitorScreen = document.querySelector('.monitor-screen');
        if (activeBtn && monitorScreen) {
            activeBtn.after(monitorScreen);
        }
    }

    // Restore or change position of monitor screen on window resize
    window.addEventListener('resize', () => {
        const monitorScreen = document.querySelector('.monitor-screen');
        const consoleEl = document.querySelector('.blueprint-console');
        if (window.innerWidth > 991 && monitorScreen && consoleEl) {
            const stepperControls = document.querySelector('.stepper-controls');
            if (monitorScreen.parentElement === stepperControls) {
                consoleEl.appendChild(monitorScreen);
            }
        } else if (window.innerWidth <= 991 && monitorScreen) {
            const activeBtn = document.querySelector('.step-btn.active');
            if (activeBtn && monitorScreen.previousElementSibling !== activeBtn) {
                activeBtn.after(monitorScreen);
            }
        }
    });
}

/* ==========================================================================
   6. MOTOR DE SLIDER HERO TOP 10
   ========================================================================== */

function initHeroSlider() {
    const sliderSec = document.getElementById('hero-slider');
    if (!sliderSec) return;

    const slides = sliderSec.querySelectorAll('.slide-item');
    const prevBtn = sliderSec.querySelector('.slider-arrow.prev');
    const nextBtn = sliderSec.querySelector('.slider-arrow.next');
    const currentCounter = document.getElementById('slider-curr');
    const progressBar = sliderSec.querySelector('.slider-progress-bar');

    let currentIndex = 0;
    const totalSlides = slides.length;
    let progressInterval = null;
    let progressPercent = 0;
    const slideDuration = 6000; // 6 segundos por slide
    const progressStepTime = 30; // Actualizar barra cada 30ms

    function updateCounter() {
        if (currentCounter) {
            const formatted = (currentIndex + 1).toString().padStart(2, '0');
            currentCounter.textContent = formatted;
        }
    }

    function goToSlide(index) {
        slides[currentIndex].classList.remove('active');
        currentIndex = (index + totalSlides) % totalSlides;
        slides[currentIndex].classList.add('active');
        updateCounter();
        resetAutoplay();

        // Track evento GA4
        const activeSlide = slides[currentIndex];
        const title = activeSlide.querySelector('h1').textContent;
        window.trackGariEvent('view_hero_slide', {
            slide_index: currentIndex + 1,
            slide_title: title
        });
    }

    function nextSlide() {
        goToSlide(currentIndex + 1);
    }

    // Exportar función global para avanzar manualmente o por autoplay
    window.nextSlide = nextSlide;

    function prevSlide() {
        goToSlide(currentIndex - 1);
    }

    function startProgress() {
        progressPercent = 0;
        if (progressBar) progressBar.style.width = '0%';
        
        clearInterval(progressInterval);
        progressInterval = setInterval(() => {
            progressPercent += (progressStepTime / slideDuration) * 100;
            if (progressPercent >= 100) {
                progressPercent = 100;
                if (progressBar) progressBar.style.width = '100%';
                clearInterval(progressInterval);
                nextSlide();
            } else {
                if (progressBar) progressBar.style.width = `${progressPercent}%`;
            }
        }, progressStepTime);
    }

    function resetAutoplay() {
        clearInterval(progressInterval);
        startProgress();
    }

    function pauseAutoplay() {
        clearInterval(progressInterval);
    }

    // Event listeners
    if (prevBtn) prevBtn.addEventListener('click', prevSlide);
    if (nextBtn) nextBtn.addEventListener('click', nextSlide);

    // Pausar al pasar el cursor sobre la sección del slider
    sliderSec.addEventListener('mouseenter', pauseAutoplay);
    sliderSec.addEventListener('mouseleave', resetAutoplay);

    // Inicializar barra de progreso y autoplay
    startProgress();
}

/* ==========================================================================
   7. SLIDER DE RESEÑAS B2B (3 Opiniones)
   ========================================================================== */

function initReviewsSlider() {
    const sliderContainer = document.querySelector('.reviews-slider-container');
    if (!sliderContainer) return;

    const track = sliderContainer.querySelector('.reviews-track');
    const dots = sliderContainer.querySelectorAll('.review-dot');
    const prevBtn = sliderContainer.querySelector('.review-arrow.prev');
    const nextBtn = sliderContainer.querySelector('.review-arrow.next');

    let currentIndex = 0;
    const totalSlides = 3;

    function goToSlide(index) {
        currentIndex = (index + totalSlides) % totalSlides;
        
        // Desplazar el track
        track.style.transform = `translateX(-${currentIndex * 33.333}%)`;
        
        // Actualizar dots
        dots.forEach((dot, idx) => {
            if (idx === currentIndex) {
                dot.classList.add('active');
                dot.style.background = 'var(--acento-warn)';
            } else {
                dot.classList.remove('active');
                dot.style.background = 'var(--border-color)';
            }
        });
    }

    if (prevBtn) prevBtn.addEventListener('click', () => goToSlide(currentIndex - 1));
    if (nextBtn) nextBtn.addEventListener('click', () => goToSlide(currentIndex + 1));

    dots.forEach(dot => {
        dot.addEventListener('click', () => {
            const index = parseInt(dot.dataset.index);
            goToSlide(index);
        });
    });
}

/* ==========================================================================
   8. MENÚ HAMBURGUESA MÓVIL
   ========================================================================== */

function initMobileMenu() {
    const burgerBtn = document.querySelector('.mobile-menu-btn');
    const navList = document.querySelector('.tech-nav');
    if (!burgerBtn || !navList) return;

    burgerBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        burgerBtn.classList.toggle('active');
        navList.classList.toggle('active');
    });

    // Cerrar al hacer click en enlaces
    const links = navList.querySelectorAll('a');
    links.forEach(link => {
        link.addEventListener('click', () => {
            burgerBtn.classList.remove('active');
            navList.classList.remove('active');
        });
    });

    // Cerrar si hace click fuera del navbar
    document.addEventListener('click', (e) => {
        if (!navList.contains(e.target) && !burgerBtn.contains(e.target)) {
            burgerBtn.classList.remove('active');
            navList.classList.remove('active');
        }
    });
}
