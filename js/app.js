const API_URL = 'http://127.0.0.1:8000/api/auth';
let currentModal = null;

// UI Helpers
function toggleModal(modalId) {
    const overlay = document.getElementById('modal-overlay');
    const modal = document.getElementById(modalId);
    
    if (currentModal === modalId) {
        // Close
        overlay.classList.remove('opacity-100');
        modal.classList.remove('scale-100');
        
        setTimeout(() => {
            overlay.classList.add('hidden');
            modal.classList.add('hidden');
            currentModal = null;
        }, 300);
    } else {
        // Open
        if(currentModal) {
            document.getElementById(currentModal).classList.add('hidden');
        }
        overlay.classList.remove('hidden');
        modal.classList.remove('hidden');
        
        // Small delay to trigger animation
        setTimeout(() => {
            overlay.classList.add('opacity-100');
            modal.classList.add('scale-100');
            
            // Dispatch event when modal finishes opening
            window.dispatchEvent(new CustomEvent('modalOpened', { detail: { modalId: modalId } }));
        }, 10);
        currentModal = modalId;
    }
}

function switchModal(closeId, openId) {
    document.getElementById(closeId).classList.add('hidden');
    document.getElementById(closeId).classList.remove('scale-100');
    const openModal = document.getElementById(openId);
    openModal.classList.remove('hidden');
    // Trigger animation
    setTimeout(() => {
        openModal.classList.add('scale-100');
    }, 10);
    currentModal = openId;
}

// Close on overlay click
const overlay = document.getElementById('modal-overlay');
if (overlay) {
    overlay.addEventListener('click', (e) => {
        if(e.target.id === 'modal-overlay' && currentModal) {
            toggleModal(currentModal);
        }
    });
}

let lastScrollTop = 0;

// Lógica de scroll para el navbar: ocultar al bajar, mostrar al subir
window.addEventListener('scroll', () => {
    const nav = document.getElementById('navbar');
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    
    // Cambiar fondo al hacer scroll
    if (scrollTop > 20) {
        nav.classList.add('bg-[#050810]/90', 'backdrop-blur-lg');
        nav.classList.remove('glass-panel');
    } else {
        nav.classList.remove('bg-[#050810]/90', 'backdrop-blur-lg');
        nav.classList.add('glass-panel');
    }

    // Ocultar/Mostrar dependiendo de la dirección
    if (scrollTop > lastScrollTop && scrollTop > 100) {
        // Scrolling down - hide
        nav.style.transform = 'translateY(-100%)';
    } else {
        // Scrolling up - show
        nav.style.transform = 'translateY(0)';
    }
    
    lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
});

// Authentication Logic
async function fetchUserProfile(token) {
    try {
        const res = await fetch(`${API_URL}/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if(res.ok) {
            const data = await res.json();
            updateUIForLoggedInUser(data);
        } else {
            localStorage.removeItem('token'); // Invalid token
        }
    } catch (err) {
        console.error("No se pudo cargar el perfil:", err);
    }
}

function updateUIForLoggedInUser(user) {
    document.getElementById('auth-buttons').classList.add('hidden');
    const userMenu = document.getElementById('user-menu');
    userMenu.classList.remove('hidden');
    
    const name = user.full_name || user.email.split('@')[0];
    document.getElementById('user-greeting').innerHTML = `<i class="ph ph-user-circle text-lg align-middle mr-1 text-primary-400"></i> Hola, ${name}`;
}

function logout() {
    localStorage.removeItem('token');
    document.getElementById('auth-buttons').classList.remove('hidden');
    document.getElementById('user-menu').classList.add('hidden');
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorEl = document.getElementById('login-error');
    const btnText = document.querySelector('#login-btn span');
    const loader = document.getElementById('login-loader');

    errorEl.classList.add('hidden');
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
        const params = new URLSearchParams();
        params.append('username', email); // OAuth2 expects username
        params.append('password', password);

        const res = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: params
        });

        const data = await res.json();

        if(res.ok) {
            localStorage.setItem('token', data.access_token);
            toggleModal('login-modal');
            fetchUserProfile(data.access_token);
            document.getElementById('login-form').reset();
        } else {
            errorEl.textContent = data.detail || 'Credenciales inválidas.';
            errorEl.classList.remove('hidden');
        }
    } catch (error) {
        errorEl.textContent = 'Error de conexión. Asegúrate de que la API esté corriendo.';
        errorEl.classList.remove('hidden');
    } finally {
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const full_name = document.getElementById('reg-name').value;
    const errorEl = document.getElementById('register-error');
    const successEl = document.getElementById('register-success');
    const btnText = document.querySelector('#register-btn span');
    const loader = document.getElementById('register-loader');

    errorEl.classList.add('hidden');
    successEl.classList.add('hidden');
    btnText.classList.add('hidden');
    loader.classList.remove('hidden');

    try {
        const res = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, full_name, is_active: true })
        });

        const data = await res.json();

        if(res.ok) {
            successEl.classList.remove('hidden');
            // Auto login after 1 second
            setTimeout(() => {
                document.getElementById('login-email').value = email;
                document.getElementById('login-password').value = password;
                switchModal('register-modal', 'login-modal');
                document.getElementById('register-form').reset();
                successEl.classList.add('hidden');
                
                // Optionally trigger login click automatically
                // document.getElementById('login-btn').click();
            }, 1000);
        } else {
            errorEl.textContent = data.detail || 'Error al registrar el usuario.';
            errorEl.classList.remove('hidden');
        }
    } catch (error) {
        errorEl.textContent = 'Error de conexión. Asegúrate de que la API esté corriendo.';
        errorEl.classList.remove('hidden');
    } finally {
        btnText.classList.remove('hidden');
        loader.classList.add('hidden');
    }
}



window.onload = () => {
    const token = localStorage.getItem('token');
    if(token) fetchUserProfile(token);
    
    // Iniciar Timeline si existe en el DOM
    if (document.getElementById('timeline-content')) {
        renderPhase(0);
    }
}

// ─── TIMELINE INBOUND LOGIC ──────────────────────────────────────────────────────
const timelineData = [
    {
        stage: "Fase 0: Inicio", time: "Mes 1", iconColor: "text-slate-400", ringColor: "border-slate-500", glow: "shadow-slate-500/40",
        tools: [
            { name: "Google Search Console", icon: "ph-magnifying-glass", desc: "Para entender cómo te busca el mercado realmente." },
            { name: "Buyer Persona Generator", icon: "ph-users", desc: "Define a quién le hablas antes de publicar contenido." }
        ],
        strategy: "Sin datos de búsqueda, tu contenido es solo una opinión. Aquí se valida la demanda real del ecosistema."
    },
    {
        stage: "Fase 1: Atracción", time: "Mes 2-3", iconColor: "text-blue-400", ringColor: "border-blue-500", glow: "shadow-[0_0_20px_rgba(59,130,246,0.5)]",
        tools: [
            { name: "CMS optimizado", icon: "ph-pen-nib", desc: "Tu activo digital principal. El blog es tu vendedor 24/7." },
            { name: "Distribución RRSS", icon: "ph-share-network", desc: "Campañas orgánicas para expandir la masa micelial." }
        ],
        strategy: "El contenido debe resolver problemas, no vender directo. La autoridad se construye alimentando a la audiencia."
    },
    {
        stage: "Fase 2: Conversión", time: "Mes 4", iconColor: "text-indigo-400", ringColor: "border-indigo-500", glow: "shadow-[0_0_20px_rgba(99,102,241,0.5)]",
        tools: [
            { name: "Landing Pages", icon: "ph-layout", desc: "Páginas de alta conversión sin distracciones." },
            { name: "Lead Magnets", icon: "ph-shield-check", desc: "El intercambio ético: valor descargable por datos." }
        ],
        strategy: "El tráfico sin conversión es vanidad. Cada visitante debe tener una ruta clara y atractiva hacia el registro."
    },
    {
        stage: "Fase 3: Nutrición", time: "Mes 5-6", iconColor: "text-fuchsia-400", ringColor: "border-fuchsia-500", glow: "shadow-[0_0_20px_rgba(217,70,239,0.5)]",
        tools: [
            { name: "Marketing Automation", icon: "ph-paper-plane-tilt", desc: "Correos secuenciales basados en el comportamiento." },
            { name: "CRM Central", icon: "ph-database", desc: "Gestión unificada de las relaciones de tus clientes." }
        ],
        strategy: "El valor real está en el seguimiento. Más del 80% de los cierres ocurren después de 5 puntos de toque."
    },
    {
        stage: "Fase 4: Optimización", time: "Continuo", iconColor: "text-primary-400", ringColor: "border-primary-500", glow: "shadow-[0_0_20px_rgba(6,182,212,0.5)]",
        tools: [
            { name: "Analítica Web (GA4)", icon: "ph-chart-line-up", desc: "Medición exacta del ROI y atribución por canal." },
            { name: "Mapas de Calor", icon: "ph-crosshair", desc: "Detección visual de puntos de fricción del usuario." }
        ],
        strategy: "Lo que no se mide no crece. Aquí el Inbound Marketing se convierte en ciencia pura."
    }
];

let currentPhaseIndex = 0;
let timelineTimeout = null;

function renderTimelineNav() {
    const navContainer = document.getElementById('timeline-nav');
    if (!navContainer) return;
    navContainer.innerHTML = '';
    
    timelineData.forEach((item, index) => {
        const isActive = index === currentPhaseIndex;
        const isPast = index <= currentPhaseIndex;
        
        const btn = document.createElement('button');
        btn.onclick = () => renderPhase(index);
        btn.className = `flex flex-col items-center group transition-all duration-300 w-full md:w-auto ${isPast ? 'opacity-100' : 'opacity-40 hover:opacity-70'}`;
        
        btn.innerHTML = `
            <div class="w-14 h-14 rounded-full border-[3px] flex items-center justify-center bg-slate-900 transition-all duration-500 ${isActive ? `${item.ringColor} ${item.glow} scale-110` : 'border-white/20 group-hover:border-white/50'} z-10 relative">
                <span class="text-xl font-bold ${isActive ? item.iconColor : 'text-slate-500'}">${index}</span>
            </div>
            <div class="mt-4 text-center">
                <span class="block text-[10px] font-black uppercase tracking-widest ${isActive ? item.iconColor : 'text-slate-500'} transition-colors">${item.time}</span>
                <span class="text-xs font-bold text-slate-300 mt-1 block">${item.stage.split(': ')[1]}</span>
            </div>
        `;
        navContainer.appendChild(btn);
    });
}

function renderPhase(index) {
    currentPhaseIndex = index;
    const data = timelineData[index];
    const contentContainer = document.getElementById('timeline-content');
    if (!contentContainer) return;
    
    // Animamos la salida
    contentContainer.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    contentContainer.style.opacity = 0;
    contentContainer.style.transform = 'translateY(15px)';
    contentContainer.style.filter = 'blur(4px)';
    
    setTimeout(() => {
        let toolsHtml = '';
        data.tools.forEach(t => {
            toolsHtml += `
                <div class="flex gap-4 p-5 rounded-2xl glass-panel group hover:border-primary-500/30 transition-all duration-500 hover:-translate-y-1 hover:shadow-[0_4px_20px_rgba(6,182,212,0.15)]">
                    <div class="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0 group-hover:bg-white/10 transition-colors">
                        <i class="ph ${t.icon} text-2xl ${data.iconColor}"></i>
                    </div>
                    <div>
                        <h4 class="font-bold text-white text-base">${t.name}</h4>
                        <p class="text-sm text-slate-400 mt-1 leading-relaxed">${t.desc}</p>
                    </div>
                </div>
            `;
        });

        contentContainer.innerHTML = `
            <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-[11px] font-bold uppercase tracking-widest mb-6 ${data.iconColor}">
                <i class="ph-bold ph-clock"></i> Despliegue: ${data.time}
            </div>
            <h2 class="text-3xl md:text-4xl font-extrabold text-white mb-6 leading-tight">${data.stage}</h2>
            <p class="text-lg text-slate-300 mb-10 leading-relaxed">${data.strategy}</p>

            <h3 class="text-xs font-black uppercase tracking-widest text-slate-500 mb-5 flex items-center gap-2">
                <i class="ph-fill ph-stack"></i> Stack Recomendado
            </h3>
            <div class="space-y-4">
                ${toolsHtml}
            </div>
        `;
        
        const nextStepEl = document.getElementById('next-step-text');
        if (nextStepEl) {
            if (index < timelineData.length - 1) {
                nextStepEl.innerText = `Transición a ${timelineData[index + 1].stage.split(': ')[1]}...`;
            } else {
                nextStepEl.innerText = "Mantener el ciclo de optimización infinito (Ecosistema Activo).";
            }
        }

        renderTimelineNav();
        
        // Forzar reflow para que el navegador registre el estado inicial antes de animar entrada
        void contentContainer.offsetWidth;
        
        contentContainer.style.opacity = 1;
        contentContainer.style.transform = 'translateY(0)';
        contentContainer.style.filter = 'blur(0px)';
        
        // Auto-advance after 5 seconds
        if (timelineTimeout) clearTimeout(timelineTimeout);
        timelineTimeout = setTimeout(nextPhase, 5000);
    }, 300);
}

function nextPhase() {
    renderPhase((currentPhaseIndex + 1) % timelineData.length);
}

// ─── CUSTOM CURSOR ────────────────────────────────────────────────────
function initCursor() {
    let dot = document.getElementById('cursor-dot');
    let ring = document.getElementById('cursor-ring');
    
    // Ensure elements exist
    if (!dot) {
        dot = document.createElement('div');
        dot.id = 'cursor-dot';
        document.body.appendChild(dot);
    }
    if (!ring) {
        ring = document.createElement('div');
        ring.id = 'cursor-ring';
        document.body.appendChild(ring);
    }

    // Force styles to override any aggressive CSS media queries
    dot.style.position = 'fixed';
    dot.style.pointerEvents = 'none';
    dot.style.zIndex = '99999';
    dot.style.display = 'block';
    
    ring.style.position = 'fixed';
    ring.style.pointerEvents = 'none';
    ring.style.zIndex = '99998';
    ring.style.display = 'block';

    let cx = window.innerWidth / 2, cy = window.innerHeight / 2;
    let rx = cx, ry = cy;

    // Detect touch vs mouse for hybrid devices (touchscreen laptops)
    window.addEventListener('touchstart', () => {
        dot.style.display = 'none';
        ring.style.display = 'none';
    }, { passive: true });

    document.addEventListener('mousemove', e => {
        // Only re-enable if it was hidden by touch
        if (dot.style.display === 'none') {
            dot.style.display = 'block';
            ring.style.display = 'block';
        }
        cx = e.clientX; cy = e.clientY;
        dot.style.left = cx + 'px'; dot.style.top = cy + 'px';
    });

    function lerp() {
        rx += (cx - rx) * 0.12; ry += (cy - ry) * 0.12;
        ring.style.left = rx + 'px'; ring.style.top = ry + 'px';
        requestAnimationFrame(lerp);
    }
    requestAnimationFrame(lerp);

    document.addEventListener('mousedown', () => ring.classList.add('clicking'));
    document.addEventListener('mouseup', () => ring.classList.remove('clicking'));

    const attachHoverEvents = () => {
        document.querySelectorAll('a, button, [onclick], input, textarea, select').forEach(el => {
            if(!el.dataset.cursorBound) {
                el.dataset.cursorBound = 'true';
                el.addEventListener('mouseenter', () => ring.classList.add('hovering'));
                el.addEventListener('mouseleave', () => ring.classList.remove('hovering'));
            }
        });
    };
    
    attachHoverEvents();
    
    // Observe DOM changes to attach hover to dynamic elements
    const observer = new MutationObserver(attachHoverEvents);
    observer.observe(document.body, { childList: true, subtree: true });
}

// Ejecutar lo antes posible
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCursor);
} else {
    initCursor();
}

// ─── MOBILE MENU ──────────────────────────────────────────────────────
function toggleMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const btn  = document.getElementById('ham-btn');
    const icon = btn.querySelector('i');
    if (!menu || !btn) return;
    
    const open = menu.classList.contains('open');
    menu.classList.toggle('open', !open);
    menu.setAttribute('aria-hidden', String(open));
    btn.setAttribute('aria-expanded', String(!open));
    if(icon) icon.className = open ? 'ph ph-list text-2xl' : 'ph ph-x text-2xl';
    document.body.style.overflow = open ? '' : 'hidden';
}
function closeMobileMenu() {
    const menu = document.getElementById('mobile-menu');
    const btn  = document.getElementById('ham-btn');
    if (!menu) return;
    menu.classList.remove('open');
    menu.setAttribute('aria-hidden', 'true');
    if (btn) { btn.setAttribute('aria-expanded', 'false'); const i = btn.querySelector('i'); if(i) i.className = 'ph ph-list text-2xl'; }
    document.body.style.overflow = '';
}
// Close menu on Escape
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeMobileMenu(); });

// Lógica para apertura general del modal de contacto (limpia selecciones previas)
function openGeneralContact() {
    const serviceField = document.getElementById('contact-service-field');
    if (serviceField) {
        serviceField.value = '';
    }
    const messageTextarea = document.querySelector('#contact-modal textarea[name="mensaje"]');
    if (messageTextarea && (
        messageTextarea.value.startsWith('Hola Hipha, me interesa') ||
        messageTextarea.value.startsWith('Hola Hipha, estoy interesado')
    )) {
        messageTextarea.value = '';
    }
    toggleModal('contact-modal');
}

// Preselección de cualquier servicio o plan en el modal de contacto
function selectServiceOrPlan(serviceName, defaultMessage) {
    const serviceField = document.getElementById('contact-service-field');
    if (serviceField) {
        serviceField.value = serviceName || '';
    }
    const messageTextarea = document.querySelector('#contact-modal textarea[name="mensaje"]');
    if (messageTextarea && defaultMessage) {
        messageTextarea.value = defaultMessage;
    }
    toggleModal('contact-modal');
}

// Lógica para preselección de planes de suscripción
function selectSubscriptionPlan(planKey) {
    let displayName = 'Plan Web';
    let defaultMsg = 'Hola Hipha, me interesa contratar el Plan Web. Quisiera más información sobre el proceso.';

    if (planKey === 'WEB') {
        displayName = 'Plan Web (Mensual)';
        defaultMsg = 'Hola Hipha, me interesa contratar el Plan Web (pago mensual $770/mes). Quisiera más información sobre el proceso.';
    } else if (planKey === 'WEB ANUAL') {
        displayName = 'Plan Web (Anual)';
        defaultMsg = 'Hola Hipha, me interesa contratar el Plan Web (pago anual $7,760/año con descuento). Quisiera más información sobre el proceso.';
    } else if (planKey === 'DESIGN') {
        displayName = 'Plan Design';
        defaultMsg = 'Hola Hipha, me interesa contratar el Plan Design ($2,770/mes sin plazos forzosos). Quisiera más información.';
    } else if (planKey === 'MKT') {
        displayName = 'Plan MKT';
        defaultMsg = 'Hola Hipha, me interesa contratar el Plan MKT ($7,760/mes). Quisiera agendar una llamada de seguimiento comercial.';
    } else if (planKey) {
        displayName = planKey;
        defaultMsg = `Hola Hipha, estoy interesado en contratar ${planKey}.`;
    }

    selectServiceOrPlan(displayName, defaultMsg);
}

// ─── Toast de notificación al compartir ──────────────────────────────────
function showShareToast(message) {
    let toast = document.getElementById('share-toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'share-toast';
        toast.className = 'fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-xl bg-slate-900/90 backdrop-blur-md border border-cyan-500/30 text-white text-xs font-semibold shadow-2xl flex items-center gap-2 transition-all duration-300 opacity-0 pointer-events-none translate-y-4';
        document.body.appendChild(toast);
    }
    toast.innerHTML = `<i class="ph-bold ph-check text-green-400 text-sm"></i> <span>${message}</span>`;
    toast.classList.remove('opacity-0', 'pointer-events-none', 'translate-y-4');
    toast.classList.add('opacity-100', 'translate-y-0');
    
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => {
        toast.classList.remove('opacity-100', 'translate-y-0');
        toast.classList.add('opacity-0', 'pointer-events-none', 'translate-y-4');
    }, 2800);
}

// ─── Fallback tradicional de copiado al portapapeles ─────────────────────
function fallbackCopyText(text, onSuccess) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '-9999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            if (onSuccess) onSuccess();
            showShareToast('¡Enlace copiado al portapapeles!');
        }
    } catch (err) {
        prompt('Copia este enlace directo:', text);
    }
    document.body.removeChild(textArea);
}

// ─── Compartir servicio o plan (Web Share API + Copia al portapapeles) ───
async function shareCard(title, text, anchorId, btnEl) {
    const url = `${window.location.origin}${window.location.pathname}#${anchorId}`;
    
    // Feedback visual en el botón
    const icon = btnEl ? btnEl.querySelector('i') : null;
    const originalClass = icon ? icon.className : '';
    const setSuccessFeedback = () => {
        if (icon) {
            icon.className = 'ph-bold ph-check text-green-400 text-lg';
            setTimeout(() => {
                icon.className = originalClass;
            }, 2200);
        }
    };

    // Intentar Web Share API nativo en dispositivos táctiles / móviles
    if (navigator.share && window.matchMedia('(max-width: 768px)').matches) {
        try {
            await navigator.share({
                title: `${title} | Hipha`,
                text: `${text}\n\nConoce los detalles aquí:`,
                url: url
            });
            setSuccessFeedback();
            return;
        } catch (err) {
            if (err.name === 'AbortError') {
                return; // Cancelado por el usuario
            }
        }
    }

    // Copiar al portapapeles
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(url);
            setSuccessFeedback();
            showShareToast('¡Enlace copiado al portapapeles!');
        } catch (err) {
            fallbackCopyText(url, setSuccessFeedback);
        }
    } else {
        fallbackCopyText(url, setSuccessFeedback);
    }
}

// ─── Resaltado visual al llegar a un Anchor/Hash ────────────────────────
function highlightCardElement(element) {
    if (!element) return;
    element.classList.remove('card-highlight-pulse');
    // Forzar reflow para reiniciar animación si ya estaba aplicada
    void element.offsetWidth;
    element.classList.add('card-highlight-pulse');
    setTimeout(() => {
        element.classList.remove('card-highlight-pulse');
    }, 2800);
}

function checkAndHighlightHash() {
    if (window.location.hash) {
        const rawHash = window.location.hash.substring(1);
        const targetEl = document.getElementById(rawHash);
        if (targetEl) {
            setTimeout(() => {
                targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
                highlightCardElement(targetEl);
            }, 500);
        }
    }
}

window.addEventListener('hashchange', () => {
    if (window.location.hash) {
        const rawHash = window.location.hash.substring(1);
        const targetEl = document.getElementById(rawHash);
        if (targetEl) {
            targetEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            highlightCardElement(targetEl);
        }
    }
});

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAndHighlightHash);
} else {
    checkAndHighlightHash();
}


// Lógica para colapsar y desplegar subfilas en la tabla comparativa
function toggleTableSubrows(className, element) {
    const rows = document.querySelectorAll('.' + className);
    if (rows.length === 0) return;
    const isHidden = rows[0].classList.contains('hidden');
    rows.forEach(row => {
        if (isHidden) {
            row.classList.remove('hidden');
        } else {
            row.classList.add('hidden');
        }
    });
    if (element) {
        element.textContent = isHidden ? '(Ocultar detalles)' : '(Ver detalles)';
    }
}

// Lógica para alternar facturación mensual/anual en el Plan Web
function setWebPlanBilling(type, buttonEl) {
    const container = buttonEl.closest('.glass-panel');
    const monthlyPrice = container.querySelector('#web-price-monthly');
    const annualPrice = container.querySelector('#web-price-annual');
    const ctaButton = container.querySelector('button[onclick^="selectSubscriptionPlan"]');
    if (!monthlyPrice || !annualPrice || !ctaButton) return;

    const buttons = buttonEl.parentNode.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.className = "flex-1 text-[11px] font-bold text-center py-1.5 rounded-lg transition-all text-slate-400 hover:text-white";
    });

    if (type === 'monthly') {
        buttonEl.className = "flex-1 text-[11px] font-bold text-center py-1.5 rounded-lg transition-all bg-cyan-600/20 text-cyan-400";
        monthlyPrice.classList.remove('hidden');
        annualPrice.classList.add('hidden');
        ctaButton.setAttribute('onclick', "selectSubscriptionPlan('WEB')");
    } else {
        buttonEl.className = "flex-1 text-[11px] font-bold text-center py-1.5 rounded-lg transition-all bg-cyan-600/20 text-cyan-400";
        monthlyPrice.classList.add('hidden');
        annualPrice.classList.remove('hidden');
        ctaButton.setAttribute('onclick', "selectSubscriptionPlan('WEB ANUAL')");
    }
}
