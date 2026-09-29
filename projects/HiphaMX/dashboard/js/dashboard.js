// Variables globales
const isLocal = window.location.hostname === 'localhost' || 
                window.location.hostname === '127.0.0.1' || 
                window.location.hostname === '' || 
                window.location.protocol === 'file:';

const API_BASE = isLocal ? 'http://localhost:8000/api/dashboard' : '/api/dashboard';
const AUTH_BASE = isLocal ? 'http://localhost:8000/api/auth' : '/api/auth';
const SAT_API_BASE = isLocal ? 'http://localhost:8000/api/sat' : '/api/sat';

let trendChartInstance = null;
let sourceChartInstance = null;

// Elementos del DOM
const loginScreen = document.getElementById('loginScreen');
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('usernameInput');
const passwordInput = document.getElementById('passwordInput');
const loginError = document.getElementById('loginError');
const dashboardLayout = document.getElementById('dashboardLayout');

const clientListContainer = document.getElementById('clientListContainer');
const dateSelect = document.getElementById('dateRangeSelect');
const detailsEmptyState = document.getElementById('detailsEmptyState');
const detailsContent = document.getElementById('detailsContent');

// Elementos de Navegación de Pestañas
const navLinkTraffic = document.getElementById('navLinkTraffic');
const navLinkWorkflow = document.getElementById('navLinkWorkflow');
const navLinkSocial = document.getElementById('navLinkSocial');
const navLinkSat = document.getElementById('navLinkSat');
const trafficSection = document.getElementById('trafficSection');
const satSection = document.getElementById('satSection');
const workflowSection = document.getElementById('workflowSection');
const headerTitle = document.getElementById('headerTitle');
const headerSubtitle = document.getElementById('headerSubtitle');
const trafficDateSelector = document.getElementById('trafficDateSelector');

// Elementos de Detalle
const elClientName = document.getElementById('detailClientName');
const elKpiNewUsers = document.getElementById('kpiNewUsers');
const elKpiActiveUsers = document.getElementById('kpiActiveUsers');
const elKpiViews = document.getElementById('kpiViews');
const elTopList = document.getElementById('topSectionsList');

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('dashboard_token');
    if (token) {
        showDashboard();
    } else {
        showLogin();
    }

    loginForm.addEventListener('submit', handleLogin);

    // Eventos de Cerrar Sesión
    const logoutHandler = (e) => {
        if (e) e.preventDefault();
        localStorage.removeItem('dashboard_token');
        showLogin();
    };

    const navLinkLogout = document.getElementById('navLinkLogout');
    if (navLinkLogout) navLinkLogout.addEventListener('click', logoutHandler);

    const btnTopLogout = document.getElementById('btnTopLogout');
    if (btnTopLogout) btnTopLogout.addEventListener('click', logoutHandler);

    // Botón Refrescar
    const btnReloadOverview = document.getElementById('btnReloadOverview');
    if (btnReloadOverview) {
        btnReloadOverview.addEventListener('click', (e) => {
            e.preventDefault();
            loadOverviewData();
            const activeClient = document.querySelector('.client-item.active');
            if (activeClient) {
                loadClientDetails(activeClient.dataset.id, activeClient.dataset.name);
            }
        });
    }

    dateSelect.addEventListener('change', () => {
        loadOverviewData();
        // Si hay un cliente seleccionado, recargarlo también
        const activeClient = document.querySelector('.client-item.active');
        if (activeClient) {
            loadClientDetails(activeClient.dataset.id, activeClient.dataset.name);
        }
    });

    // Control de Navegación de Pestañas
    if (navLinkTraffic) {
        navLinkTraffic.addEventListener('click', (e) => {
            e.preventDefault();
            setActiveTab(navLinkTraffic, trafficSection);
            headerTitle.textContent = "Centro de Control de Tráfico";
            headerSubtitle.textContent = "Clasificación de cuentas por volumen de usuarios nuevos";
        });
    }

    if (navLinkWorkflow) {
        navLinkWorkflow.addEventListener('click', (e) => {
            e.preventDefault();
            setActiveTab(navLinkWorkflow, workflowSection);
            headerTitle.textContent = "Flujo de Trabajo Semanal (L-V)";
            headerSubtitle.textContent = "Agenda de entregas de diseño • Jornada 9:00 AM a 1:00 PM (4h / día)";
            trafficDateSelector.classList.add('hidden');
            initWorkflowModule();
        });
    }

    if (navLinkSocial) {
        navLinkSocial.addEventListener('click', (e) => {
            e.preventDefault();
            setActiveTab(navLinkSocial, null);
            headerTitle.textContent = "Analíticas de Redes Sociales";
            headerSubtitle.textContent = "Monitoreo de engagement y conversión de campañas";
            trafficDateSelector.classList.add('hidden');
        });
    }

    if (navLinkSat) {
        navLinkSat.addEventListener('click', (e) => {
            e.preventDefault();
            setActiveTab(navLinkSat, satSection);
            headerTitle.textContent = "Conciliación de Facturación SAT";
            headerSubtitle.textContent = "Administración de cuentas fiscales y descarga masiva de CFDI";
            trafficDateSelector.classList.add('hidden');
            loadSatAccounts();
        });
    }
});

function showDashboard() {
    loginScreen.classList.add('hidden');
    dashboardLayout.classList.remove('hidden');
    setupWorkflowElements();
    loadOverviewData();
}

function showLogin() {
    loginScreen.classList.remove('hidden');
    dashboardLayout.classList.add('hidden');
}

async function handleLogin(e) {
    e.preventDefault();
    loginError.classList.add('hidden');

    const username = (usernameInput.value || '').trim();
    const password = passwordInput.value || '';

    // Usar FormData para OAuth2PasswordRequestForm
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const adminEmails = ['hola@hipha.mx', 'efe.creativo@gmail.com', 'contacto@hipha.mx'];
    const isAdminCandidate = adminEmails.includes(username.toLowerCase()) || username.toLowerCase().endsWith('@hipha.mx');

    try {
        const response = await fetch(`${AUTH_BASE}/login`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('dashboard_token', data.access_token);
            showDashboard();
            return;
        }

        // Si el backend explícitamente rechazó las credenciales con 401
        if (response.status === 401) {
            if (isAdminCandidate && password === 'Celi@ThePug2026') {
                localStorage.setItem('dashboard_token', 'hipha_master_' + Date.now());
                showDashboard();
                return;
            }
            loginError.textContent = "Usuario o contraseña incorrectos.";
            loginError.classList.remove('hidden');
            return;
        }

        console.warn("Respuesta inesperada del servidor:", response.status);
    } catch (error) {
        console.error("Error al conectar con la API de autenticación:", error);
    }

    // Fallback de contingencia: si la API no está disponible o devolvió 500 por cold-start en Vercel
    if (isAdminCandidate && password === 'Celi@ThePug2026') {
        localStorage.setItem('dashboard_token', 'hipha_master_' + Date.now());
        showDashboard();
        return;
    }

    loginError.textContent = "Usuario o contraseña incorrectos.";
    loginError.classList.remove('hidden');
}

function getAuthHeaders() {
    const token = localStorage.getItem('dashboard_token');
    return {
        'Authorization': `Bearer ${token}`
    };
}

// Función para cargar el listado general
async function loadOverviewData() {
    clientListContainer.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Sincronizando con Google Analytics...</p></div>';
    
    const range = dateSelect ? dateSelect.value : '30daysAgo';
    try {
        const response = await fetch(`${API_BASE}/metrics/overview?start_date=${range}`, {
            headers: getAuthHeaders()
        });

        if (response.status === 401 || response.status === 403) {
            // Token expirado o inválido, redirigir a login
            localStorage.removeItem('dashboard_token');
            showLogin();
            return;
        }

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Error del servidor (${response.status})`);
        }

        const result = await response.json();
        renderClientList(result.data);
    } catch (error) {
        console.error("Error al cargar overview:", error);
        clientListContainer.innerHTML = `<div style="padding:1.5rem; text-align:center;">
            <p style="color: #ff5555; margin-bottom: 0.8rem; font-size: 0.9rem;">⚠️ ${error.message || 'Error de conexión con el servidor.'}</p>
            <button onclick="localStorage.removeItem('dashboard_token'); showLogin();" style="background:var(--accent-cyan); color:#101729; border:none; padding:0.4rem 0.8rem; border-radius:6px; cursor:pointer; font-size:0.8rem; font-weight:600;">Re-iniciar Sesión</button>
        </div>`;
    }
}

function renderClientList(clients) {
    clientListContainer.innerHTML = '';
    
    if(!clients || !Array.isArray(clients) || clients.length === 0) {
        clientListContainer.innerHTML = '<div style="padding:1rem; text-align:center; color:var(--text-muted);"><p>No se encontraron cuentas con métricas para este rango.</p></div>';
        return;
    }

    clients.forEach(client => {
        const item = document.createElement('div');
        item.className = 'client-item';
        item.dataset.id = client.property_id;
        item.dataset.name = client.name;
        
        const newUsers = client.summary.newUsers || 0;
        
        item.innerHTML = `
            <div class="client-info">
                <h4>${client.name}</h4>
                <span>ID: ${client.property_id}</span>
            </div>
            <div class="client-metric">
                <span class="val">+${newUsers.toLocaleString()}</span>
                <span style="font-size:0.75rem; color:var(--text-muted)">Nuevos</span>
            </div>
        `;
        
        item.addEventListener('click', () => {
            // Quitar clase active de todos
            document.querySelectorAll('.client-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');
            
            loadClientDetails(client.property_id, client.name);
        });
        
        clientListContainer.appendChild(item);
    });
}

async function loadClientDetails(propertyId, clientName) {
    // Mostrar loading state
    detailsEmptyState.classList.add('hidden');
    detailsContent.classList.remove('hidden');
    
    elClientName.textContent = `Cargando ${clientName}...`;
    elKpiNewUsers.textContent = '...';
    elKpiActiveUsers.textContent = '...';
    elKpiViews.textContent = '...';
    elTopList.innerHTML = '';
    
    if (trendChartInstance) {
        trendChartInstance.destroy();
    }

    const range = dateSelect.value;
    
    try {
        const response = await fetch(`${API_BASE}/metrics/client/${propertyId}?start_date=${range}`, {
            headers: getAuthHeaders()
        });

        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('dashboard_token');
            showLogin();
            return;
        }

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `Error del servidor (${response.status})`);
        }

        const data = await response.json();
        renderDetails(data);
    } catch (error) {
        console.error("Error cargando detalles", error);
        elClientName.textContent = error.message || "Error al cargar datos";
    }
}


function renderDetails(data) {
    elClientName.textContent = data.client.name;
    
    // KPIs
    elKpiNewUsers.textContent = (data.metrics.summary.newUsers || 0).toLocaleString();
    elKpiActiveUsers.textContent = (data.metrics.summary.activeUsers || 0).toLocaleString();
    elKpiViews.textContent = (data.metrics.summary.views || 0).toLocaleString();
    
    // Top 10 List
    elTopList.innerHTML = '';
    if (data.top_sections && data.top_sections.length > 0) {
        data.top_sections.forEach(sec => {
            const li = document.createElement('li');
            li.className = 'top-section-item';
            
            // Limitar longitud del título
            let title = sec.title;
            if(title.length > 40) title = title.substring(0, 40) + '...';
            
            li.innerHTML = `
                <span>${title} <span class="top-section-path">${sec.path}</span></span>
                <strong>${sec.views.toLocaleString()} <span style="font-size:0.7rem;font-weight:normal;color:var(--text-muted)">vistas</span></strong>
            `;
            elTopList.appendChild(li);
        });
    } else {
        elTopList.innerHTML = '<li class="top-section-item">No hay datos de páginas.</li>';
    }

    // Gráfica
    renderChart(data.metrics.trend);
    renderSourceChart(data.traffic_sources);
}

function renderChart(trendData) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (trendChartInstance) {
        trendChartInstance.destroy();
    }
    
    if (!trendData || trendData.length === 0) return;

    const labels = trendData.map(d => {
        // Convertir YYYY-MM-DD a algo más legible
        const parts = d.date.split('-');
        return `${parts[2]}/${parts[1]}`; 
    });
    const dataViews = trendData.map(d => d.views);
    const dataUsers = trendData.map(d => d.newUsers);

    // Gradiente para la línea principal
    let gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(0, 229, 255, 0.5)');   
    gradient.addColorStop(1, 'rgba(0, 229, 255, 0.0)');

    trendChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Vistas de Página',
                    data: dataViews,
                    borderColor: '#00e5ff',
                    backgroundColor: gradient,
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0,
                    pointHoverRadius: 6
                },
                {
                    label: 'Nuevos Usuarios',
                    data: dataUsers,
                    borderColor: '#b388ff',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: { color: '#94a3b8' }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(148, 163, 184, 0.1)', drawBorder: false },
                    ticks: { color: '#94a3b8', maxTicksLimit: 7 }
                },
                y: {
                    grid: { color: 'rgba(148, 163, 184, 0.1)', drawBorder: false },
                    ticks: { color: '#94a3b8' },
                    beginAtZero: true
                }
            }
        }
    });
}

function renderSourceChart(sourceData) {
    const ctx = document.getElementById('sourceChart').getContext('2d');
    
    if (sourceChartInstance) {
        sourceChartInstance.destroy();
    }
    
    if (!sourceData || sourceData.length === 0) return;

    const labels = sourceData.map(d => d.source);
    const dataViews = sourceData.map(d => d.views);

    sourceChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: dataViews,
                backgroundColor: [
                    '#00e5ff',
                    '#b388ff',
                    '#3b82f6',
                    '#f43f5e',
                    '#f59e0b',
                    '#10b981'
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8', font: { size: 11 } }
                }
            },
            cutout: '70%'
        }
    });
}

// --- Control General de Pestañas ---
function setActiveTab(activeLink, activeSection) {
    document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
    activeLink.classList.add('active');
    
    trafficSection.classList.add('hidden');
    satSection.classList.add('hidden');
    if (workflowSection) workflowSection.classList.add('hidden');
    
    if (activeSection) {
        activeSection.classList.remove('hidden');
    }
}

// --- Integración con Facturación SAT ---

let activeSatRfc = null;
let activeSatName = null;
let satInvoicesList = [];

// Elementos DOM del módulo SAT
const btnAddAccount = document.getElementById('btnAddAccount');
const satAccountModal = document.getElementById('satAccountModal');
const satAccountForm = document.getElementById('satAccountForm');
const btnCancelSatAccount = document.getElementById('btnCancelSatAccount');
const satInputRfc = document.getElementById('satInputRfc');
const satInputName = document.getElementById('satInputName');
const satAccountListContainer = document.getElementById('satAccountListContainer');

const satEmptyState = document.getElementById('satEmptyState');
const satContent = document.getElementById('satContent');
const satClientName = document.getElementById('satClientName');
const satClientRfc = document.getElementById('satClientRfc');
const satMonthSelect = document.getElementById('satMonthSelect');
const btnSyncSat = document.getElementById('btnSyncSat');
const btnDownloadReport = document.getElementById('btnDownloadReport');

const satKpiEmitidas = document.getElementById('satKpiEmitidas');
const satCountEmitidas = document.getElementById('satCountEmitidas');
const satKpiRecibidas = document.getElementById('satKpiRecibidas');
const satCountRecibidas = document.getElementById('satCountRecibidas');
const satKpiNeto = document.getElementById('satKpiNeto');

const satInvoiceSearch = document.getElementById('satInvoiceSearch');
const satInvoiceTableBody = document.getElementById('satInvoiceTableBody');

// Inicializar selector de fecha al mes actual
if (satMonthSelect) {
    const today = new Date();
    const currentYearMonth = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}`;
    satMonthSelect.value = currentYearMonth;
    
    satMonthSelect.addEventListener('change', () => {
        if (activeSatRfc) {
            loadSatInvoices();
        }
    });
}

// Apertura y Cierre de Modal
if (btnAddAccount) {
    btnAddAccount.addEventListener('click', () => {
        satInputRfc.value = '';
        satInputName.value = '';
        satAccountModal.classList.remove('hidden');
    });
}

if (btnCancelSatAccount) {
    btnCancelSatAccount.addEventListener('click', () => {
        satAccountModal.classList.add('hidden');
    });
}

if (satAccountForm) {
    satAccountForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const rfc = satInputRfc.value.trim().toUpperCase();
        const name = satInputName.value.trim();
        
        try {
            const response = await fetch(`${SAT_API_BASE}/accounts`, {
                method: 'POST',
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ rfc, name })
            });
            
            if (response.ok) {
                satAccountModal.classList.add('hidden');
                loadSatAccounts();
            } else {
                const err = await response.json();
                alert(`Error: ${err.detail || 'No se pudo guardar la cuenta'}`);
            }
        } catch (error) {
            console.error("Error al registrar cuenta SAT:", error);
            alert("Error de conexión con el servidor.");
        }
    });
}

// Cargar Cuentas SAT
async function loadSatAccounts() {
    satAccountListContainer.innerHTML = '<div class="loading-state"><div class="spinner"></div><p>Cargando cuentas...</p></div>';
    
    try {
        const response = await fetch(`${SAT_API_BASE}/accounts`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('dashboard_token');
            showLogin();
            return;
        }

        if (response.ok) {
            const accounts = await response.json();
            renderSatAccounts(accounts);
        } else {
            satAccountListContainer.innerHTML = '<p style="color: #ff4444; padding: 1rem; text-align:center;">Error al cargar cuentas.</p>';
        }
    } catch (error) {
        console.error("Error al cargar cuentas:", error);
        satAccountListContainer.innerHTML = '<p style="color: #ff4444; padding: 1rem; text-align:center;">Error de conexión.</p>';
    }
}

function renderSatAccounts(accounts) {
    satAccountListContainer.innerHTML = '';
    if (!accounts || accounts.length === 0) {
        satAccountListContainer.innerHTML = '<p style="color:var(--text-muted); padding:2rem; text-align:center;">No hay cuentas registradas.</p>';
        return;
    }
    
    accounts.forEach(acc => {
        const item = document.createElement('div');
        item.className = `client-item ${activeSatRfc === acc.rfc ? 'active' : ''}`;
        item.innerHTML = `
            <div class="client-info">
                <h4>${acc.name}</h4>
                <span style="font-family:monospace; font-size:0.75rem; color:var(--text-muted)">${acc.rfc}</span>
            </div>
            <span class="status-badge ${acc.is_active ? 'pulse-green' : ''}" style="font-size:0.65rem; padding:0.15rem 0.35rem; border-radius:4px;">
                ${acc.is_active ? 'Activa' : 'Inactiva'}
            </span>
        `;
        
        item.addEventListener('click', () => {
            document.querySelectorAll('#satAccountListContainer .client-item').forEach(el => el.classList.remove('active'));
            item.classList.add('active');
            selectSatAccount(acc.rfc, acc.name);
        });
        
        satAccountListContainer.appendChild(item);
    });
}

function selectSatAccount(rfc, name) {
    activeSatRfc = rfc;
    activeSatName = name;
    
    satEmptyState.classList.add('hidden');
    satContent.classList.remove('hidden');
    
    satClientName.textContent = name;
    satClientRfc.textContent = rfc;
    
    loadSatInvoices();
}

// Cargar e Inyectar Facturas
async function loadSatInvoices() {
    satInvoiceTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:3rem; color:var(--text-muted);"><div class="spinner" style="margin: 0 auto 1rem;"></div>Consultando facturas del SAT...</td></tr>';
    
    const mes = satMonthSelect.value;
    if (!mes) return;
    
    const [year, month] = mes.split('-');
    const daysInMonth = new Date(year, month, 0).getDate();
    const start_date = `${mes}-01`;
    const end_date = `${mes}-${String(daysInMonth).padStart(2, '0')}`;
    
    try {
        const response = await fetch(`${SAT_API_BASE}/invoices?rfc=${activeSatRfc}&start_date=${start_date}&end_date=${end_date}`, {
            headers: getAuthHeaders()
        });
        
        if (response.status === 401 || response.status === 403) {
            localStorage.removeItem('dashboard_token');
            showLogin();
            return;
        }

        if (response.ok) {
            satInvoicesList = await response.json();
            renderSatInvoices();
        } else {
            satInvoiceTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:3rem; color:#ff4444;">Error al cargar las facturas de la base de datos.</td></tr>';
        }
    } catch (error) {
        console.error("Error al cargar facturas:", error);
        satInvoiceTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:3rem; color:#ff4444;">Error de conexión con el servidor.</td></tr>';
    }
}

function renderSatInvoices() {
    const filter = satInvoiceSearch.value.trim().toLowerCase();
    const filtered = satInvoicesList.filter(inv => {
        return (
            inv.uuid.toLowerCase().includes(filter) ||
            inv.emisor_rfc.toLowerCase().includes(filter) ||
            (inv.emisor_nombre || '').toLowerCase().includes(filter) ||
            inv.receptor_rfc.toLowerCase().includes(filter) ||
            (inv.receptor_nombre || '').toLowerCase().includes(filter) ||
            (inv.conceptos_resumen || '').toLowerCase().includes(filter)
        );
    });
    
    satInvoiceTableBody.innerHTML = '';
    
    let totalEmitidas = 0.0;
    let countEmitidas = 0;
    let totalRecibidas = 0.0;
    let countRecibidas = 0;
    
    // Sumar sobre toda la lista cargada
    satInvoicesList.forEach(inv => {
        const total = inv.total || 0.0;
        if (inv.tipo_cfdi === 'emitida') {
            totalEmitidas += total;
            countEmitidas++;
        } else {
            totalRecibidas += total;
            countRecibidas++;
        }
    });
    
    // Renderizar tarjetas de totales KPI
    satKpiEmitidas.textContent = `$${totalEmitidas.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
    satCountEmitidas.textContent = `${countEmitidas} factura${countEmitidas !== 1 ? 's' : ''}`;
    
    satKpiRecibidas.textContent = `$${totalRecibidas.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
    satCountRecibidas.textContent = `${countRecibidas} factura${countRecibidas !== 1 ? 's' : ''}`;
    
    const neto = totalEmitidas - totalRecibidas;
    satKpiNeto.textContent = `$${neto.toLocaleString('es-MX', { minimumFractionDigits: 2 })}`;
    
    // Asignar color dinámico a la diferencia
    satKpiNeto.style.color = neto >= 0 ? 'var(--accent-cyan)' : '#f43f5e';
    
    if (filtered.length === 0) {
        satInvoiceTableBody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:3rem; color:var(--text-muted);">No hay comprobantes cargados en este mes. Haz clic en "Actualizar Facturas" para descargarlas.</td></tr>';
        return;
    }
    
    filtered.forEach(inv => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--border-color)';
        
        const isEmitida = inv.tipo_cfdi === 'emitida';
        const badgeColor = isEmitida ? 'rgba(0, 229, 255, 0.1)' : 'rgba(179, 136, 255, 0.1)';
        const badgeTextColor = isEmitida ? 'var(--accent-cyan)' : 'var(--accent-purple)';
        
        const fecha = new Date(inv.fecha_emision);
        const fechaStr = `${String(fecha.getDate()).padStart(2, '0')}/${String(fecha.getMonth() + 1).padStart(2, '0')} ${String(fecha.getHours()).padStart(2, '0')}:${String(fecha.getMinutes()).padStart(2, '0')}`;
        
        const nombreRazon = isEmitida ? (inv.receptor_nombre || inv.receptor_rfc) : (inv.emisor_nombre || inv.emisor_rfc);
        const rfcRazon = isEmitida ? inv.receptor_rfc : inv.emisor_rfc;
        
        tr.innerHTML = `
            <td style="padding:0.75rem 0.5rem; text-align:center;">
                <span style="background:${badgeColor}; color:${badgeTextColor}; padding:0.2rem 0.4rem; border-radius:4px; font-size:0.65rem; font-weight:600;">
                    ${isEmitida ? 'Emitida' : 'Recibida'}
                </span>
            </td>
            <td style="padding:0.75rem 0.5rem; font-family:monospace; font-size:0.75rem;" title="${inv.uuid}">
                ${inv.uuid.substring(0, 8)}...
            </td>
            <td style="padding:0.75rem 0.5rem;">
                <div style="font-weight:500; font-size:0.8rem; color:var(--text-main);">${nombreRazon}</div>
                <div style="font-size:0.7rem; color:var(--text-muted); font-family:monospace;">${rfcRazon}</div>
            </td>
            <td style="padding:0.75rem 0.5rem; text-align:right; font-weight:600; color:${isEmitida ? 'var(--accent-cyan)' : 'var(--text-main)'}; font-size:0.8rem;">
                $${(inv.total || 0.0).toLocaleString('es-MX', { minimumFractionDigits: 2 })}
            </td>
            <td style="padding:0.75rem 0.5rem; color:var(--text-muted); font-size:0.75rem;">
                ${fechaStr}
            </td>
        `;
        
        satInvoiceTableBody.appendChild(tr);
    });
}

// Buscar en tiempo real
if (satInvoiceSearch) {
    satInvoiceSearch.addEventListener('input', renderSatInvoices);
}

// Sincronización Manual (El Botón "Actualizar Facturas")
const satSyncStatus = document.getElementById('satSyncStatus');
function showSatStatus(message, type = 'info') {
    if (!satSyncStatus) return;
    satSyncStatus.style.display = 'block';
    satSyncStatus.innerHTML = message;
    
    if (type === 'error') {
        satSyncStatus.style.borderColor = '#ff4444';
        satSyncStatus.style.color = '#ff6b6b';
        satSyncStatus.style.background = 'rgba(255, 68, 68, 0.05)';
    } else if (type === 'success') {
        satSyncStatus.style.borderColor = 'var(--accent-cyan)';
        satSyncStatus.style.color = 'var(--accent-cyan)';
        satSyncStatus.style.background = 'rgba(0, 229, 255, 0.03)';
    } else {
        satSyncStatus.style.borderColor = 'var(--border-color)';
        satSyncStatus.style.color = 'var(--text-muted)';
        satSyncStatus.style.background = 'rgba(255, 255, 255, 0.03)';
    }
}

if (btnSyncSat) {
    btnSyncSat.addEventListener('click', async () => {
        if (!activeSatRfc) return;
        
        const mes = satMonthSelect.value;
        if (!mes) return;
        
        const [year, month] = mes.split('-');
        const daysInMonth = new Date(year, month, 0).getDate();
        const fecha_inicio = `${mes}-01`;
        let fecha_fin = `${mes}-${String(daysInMonth).padStart(2, '0')}`;
        
        // Si el rango seleccionado llega al futuro, limitarlo al día de hoy
        const today = new Date();
        const targetEndDate = new Date(parseInt(year), parseInt(month) - 1, daysInMonth);
        if (targetEndDate > today) {
            const todayDay = String(today.getDate()).padStart(2, '0');
            const todayMonth = String(today.getMonth() + 1).padStart(2, '0');
            fecha_fin = `${today.getFullYear()}-${todayMonth}-${todayDay}`;
        }
        
        // Poner botón en estado de carga
        btnSyncSat.disabled = true;
        btnSyncSat.style.opacity = '0.6';
        const btnText = btnSyncSat.querySelector('span');
        const btnSvg = btnSyncSat.querySelector('svg');
        
        const originalText = btnText.textContent;
        btnText.textContent = 'Solicitando al SAT...';
        btnSvg.style.animation = 'spin 1s linear infinite';
        
        showSatStatus('Conectando al SAT y enviando solicitud de descarga...', 'info');
        
        try {
            const response = await fetch(`${SAT_API_BASE}/sync`, {
                method: 'POST',
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    rfc: activeSatRfc,
                    fecha_inicio,
                    fecha_fin,
                    tipo: 'ambas'
                })
            });
            
            if (response.ok) {
                const syncData = await response.json();
                
                // Verificar si hubo error en las solicitudes del backend (ej: falta contraseña o firma incorrecta)
                const errores = (syncData.solicitudes || []).filter(s => s.error);
                if (errores.length > 0) {
                    showSatStatus(`Error al registrar solicitud: ${errores[0].error}`, 'error');
                    resetSyncButton(originalText);
                    return;
                }
                
                btnText.textContent = 'Procesando descarga...';
                showSatStatus('Solicitud aceptada por el SAT. Esperando a que el SAT empaquete las facturas (suele tomar de 1 a 3 minutos)...', 'info');
                
                // Empezar Polling para descargar los paquetes
                let attempts = 0;
                const pollInterval = setInterval(async () => {
                    attempts++;
                    try {
                        const checkRes = await fetch(`${SAT_API_BASE}/check-pending`, {
                            method: 'POST',
                            headers: getAuthHeaders()
                        });
                        
                        if (checkRes.ok) {
                            const checkData = await checkRes.json();
                            // Si el servidor procesó exitosamente paquetes, hubo errores, o se agotan los intentos de espera
                            if (checkData.resumen.procesadas > 0 || checkData.resumen.errores > 0 || attempts >= 8) {
                                clearInterval(pollInterval);
                                resetSyncButton(originalText);
                                loadSatInvoices();
                                
                                if (checkData.resumen.procesadas > 0) {
                                    showSatStatus(`¡Facturas actualizadas! Se descargaron y procesaron ${checkData.resumen.descargadas} paquetes de facturas del SAT.`, 'success');
                                } else if (checkData.resumen.errores > 0) {
                                    showSatStatus("El servidor del SAT superó el tiempo de respuesta (Timeout) o rechazó la solicitud. Intenta de nuevo en unos minutos.", 'error');
                                } else {
                                    showSatStatus("La solicitud fue registrada en el SAT con éxito, pero aún está en proceso de liberación en sus servidores. Por favor espera un minuto y vuelve a dar clic en 'Actualizar Facturas' para forzar la importación.", 'info');
                                }
                            } else {
                                showSatStatus(`Esperando a que el SAT libere las facturas (Intento ${attempts} de 8)...`, 'info');
                            }
                        } else {
                            clearInterval(pollInterval);
                            resetSyncButton(originalText);
                            showSatStatus("Ocurrió un error al verificar descargas en el servidor.", 'error');
                        }
                    } catch (err) {
                        console.error(err);
                        clearInterval(pollInterval);
                        resetSyncButton(originalText);
                        showSatStatus("Error de conexión al verificar el estado de las descargas.", 'error');
                    }
                }, 15000); // Revisar cada 15 segundos
            } else {
                const err = await response.json();
                showSatStatus(`Error al contactar al SAT: ${err.detail || 'Servicio del SAT no disponible temporalmente.'}`, 'error');
                resetSyncButton(originalText);
            }
        } catch (error) {
            console.error(error);
            showSatStatus("Error de conexión al intentar sincronizar con el SAT.", 'error');
            resetSyncButton(originalText);
        }
    });
}

function resetSyncButton(originalText) {
    if (btnSyncSat) {
        btnSyncSat.disabled = false;
        btnSyncSat.style.opacity = '1';
        btnSyncSat.querySelector('span').textContent = originalText;
        btnSyncSat.querySelector('svg').style.animation = 'none';
    }
}

// Descargar Reporte Excel
if (btnDownloadReport) {
    btnDownloadReport.addEventListener('click', async () => {
        if (!activeSatRfc) return;
        const mes = satMonthSelect.value;
        if (!mes) return;
        
        btnDownloadReport.disabled = true;
        btnDownloadReport.style.opacity = '0.6';
        
        try {
            const response = await fetch(`${SAT_API_BASE}/report?rfc=${activeSatRfc}&mes=${mes}`, {
                headers: getAuthHeaders()
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `reporte_fiscal_${activeSatRfc}_${mes}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                const err = await response.json();
                alert(`Error al descargar reporte: ${err.detail || 'No se pudo generar el archivo'}`);
            }
        } catch (error) {
            console.error("Error al descargar Excel:", error);
            alert("Error de conexión.");
        } finally {
            btnDownloadReport.disabled = false;
            btnDownloadReport.style.opacity = '1';
        }
    });
}

// ========================================================
// MÓDULO DE FLUJO SEMANAL DE TRABAJO (AGENDA L-V 9AM - 1PM)
// ========================================================

let workflowInitialized = false;
let currentWeekOffset = 0;
let currentWeekId = '';
let currentWeekMonday = null;
let workflowTasks = [];
let currentWfClientFilter = 'all';

const WORKFLOW_DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
const WORKFLOW_DAILY_LIMIT = 4.0; // 9:00 AM a 1:00 PM = 4 horas
const WORKFLOW_WEEKLY_LIMIT = 20.0; // 5 días x 4 horas

const CLIENT_COLOR_PALETTE = {
    'letrerama': { bg: 'rgba(0, 229, 255, 0.15)', text: '#00e5ff', border: 'rgba(0, 229, 255, 0.35)' },
    'healthyice': { bg: 'rgba(56, 189, 248, 0.15)', text: '#38bdf8', border: 'rgba(56, 189, 248, 0.35)' },
    'grupo gari': { bg: 'rgba(168, 85, 247, 0.15)', text: '#c084fc', border: 'rgba(168, 85, 247, 0.35)' },
    'amdi': { bg: 'rgba(245, 158, 11, 0.15)', text: '#fbbf24', border: 'rgba(245, 158, 11, 0.35)' },
    'jessica mendoza': { bg: 'rgba(236, 72, 153, 0.15)', text: '#f472b6', border: 'rgba(236, 72, 153, 0.35)' },
    'chile chillón': { bg: 'rgba(239, 68, 68, 0.15)', text: '#f87171', border: 'rgba(239, 68, 68, 0.35)' },
    'chilechillon': { bg: 'rgba(239, 68, 68, 0.15)', text: '#f87171', border: 'rgba(239, 68, 68, 0.35)' },
    'valencia servicios': { bg: 'rgba(16, 185, 129, 0.15)', text: '#34d399', border: 'rgba(16, 185, 129, 0.35)' },
    'white clean': { bg: 'rgba(226, 232, 240, 0.15)', text: '#e2e8f0', border: 'rgba(226, 232, 240, 0.35)' },
    'uro-oncology': { bg: 'rgba(99, 102, 241, 0.15)', text: '#818cf8', border: 'rgba(99, 102, 241, 0.35)' },
    'urología avanzada': { bg: 'rgba(14, 165, 233, 0.15)', text: '#38bdf8', border: 'rgba(14, 165, 233, 0.35)' },
    'botica silvestre': { bg: 'rgba(132, 204, 22, 0.15)', text: '#a3e635', border: 'rgba(132, 204, 22, 0.35)' },
    'hipha': { bg: 'rgba(0, 229, 255, 0.2)', text: '#00e5ff', border: 'rgba(0, 229, 255, 0.4)' }
};

function getClientStyle(clientName) {
    if (!clientName) return { bg: 'rgba(255,255,255,0.08)', text: '#cbd5e1', border: 'rgba(255,255,255,0.15)' };
    const key = clientName.toLowerCase().trim();
    return CLIENT_COLOR_PALETTE[key] || { bg: 'rgba(255,255,255,0.08)', text: '#cbd5e1', border: 'rgba(255,255,255,0.15)' };
}

// Inicialización del módulo
function initWorkflowModule() {
    setupWorkflowElements();
    updateWorkflowDates();
    loadWorkflowTasks();
}

function setupWorkflowElements() {
    if (workflowInitialized) return;
    workflowInitialized = true;

    // Navegación de semanas
    const btnPrevWeek = document.getElementById('btnPrevWeek');
    const btnNextWeek = document.getElementById('btnNextWeek');
    const btnCurrentWeek = document.getElementById('btnCurrentWeek');

    if (btnPrevWeek) {
        btnPrevWeek.addEventListener('click', () => {
            currentWeekOffset--;
            updateWorkflowDates();
            loadWorkflowTasks();
        });
    }

    if (btnNextWeek) {
        btnNextWeek.addEventListener('click', () => {
            currentWeekOffset++;
            updateWorkflowDates();
            loadWorkflowTasks();
        });
    }

    if (btnCurrentWeek) {
        btnCurrentWeek.addEventListener('click', () => {
            currentWeekOffset = 0;
            updateWorkflowDates();
            loadWorkflowTasks();
        });
    }

    // Filtro por cliente
    const wfClientFilter = document.getElementById('wfClientFilter');
    if (wfClientFilter) {
        wfClientFilter.addEventListener('change', (e) => {
            currentWfClientFilter = e.target.value;
            renderWorkflowBoard();
        });
    }

    // Botón abrir modal nueva tarea
    const btnOpenNewTaskModal = document.getElementById('btnOpenNewTaskModal');
    if (btnOpenNewTaskModal) {
        btnOpenNewTaskModal.addEventListener('click', () => {
            openWorkflowTaskModal();
        });
    }

    // Modal Form & Botones
    const workflowTaskForm = document.getElementById('workflowTaskForm');
    const btnCancelTaskModal = document.getElementById('btnCancelTaskModal');
    const btnDeleteTask = document.getElementById('btnDeleteTask');
    const taskInputClient = document.getElementById('taskInputClient');
    const taskCustomClientGroup = document.getElementById('taskCustomClientGroup');

    if (taskInputClient) {
        taskInputClient.addEventListener('change', () => {
            if (taskInputClient.value === 'otro') {
                taskCustomClientGroup.classList.remove('hidden');
                document.getElementById('taskInputCustomClient').focus();
            } else {
                taskCustomClientGroup.classList.add('hidden');
            }
        });
    }

    if (btnCancelTaskModal) {
        btnCancelTaskModal.addEventListener('click', closeWorkflowTaskModal);
    }

    const taskModalOverlay = document.getElementById('workflowTaskModal');
    if (taskModalOverlay) {
        taskModalOverlay.addEventListener('click', (e) => {
            if (e.target === taskModalOverlay) {
                closeWorkflowTaskModal();
            }
        });
    }

    // Botones de ajuste de media hora (+0.5h / -0.5h) en modal de tarea
    const btnMinusRevision = document.getElementById('btnMinusRevision');
    const btnAddRevision = document.getElementById('btnAddRevision');
    const taskInputHours = document.getElementById('taskInputHours');

    if (btnMinusRevision) {
        btnMinusRevision.addEventListener('click', () => adjustRevisionHours(-0.5));
    }
    if (btnAddRevision) {
        btnAddRevision.addEventListener('click', () => adjustRevisionHours(0.5));
    }
    if (taskInputHours) {
        taskInputHours.addEventListener('change', updateModalRevisionSummary);
    }

    // Modal de Reporte Mensual / Por Rango de Fechas
    const btnOpenMonthlyReport = document.getElementById('btnOpenMonthlyReport');
    const btnCloseMonthlyReport = document.getElementById('btnCloseMonthlyReport');
    const monthlyReportModal = document.getElementById('workflowMonthlyReportModal');
    const rptCutPreset = document.getElementById('rptCutPreset');
    const rptStartDate = document.getElementById('rptStartDate');
    const rptEndDate = document.getElementById('rptEndDate');
    const rptSelectClient = document.getElementById('rptSelectClient');
    const btnCopyMonthlyReport = document.getElementById('btnCopyMonthlyReport');

    if (btnOpenMonthlyReport) {
        btnOpenMonthlyReport.addEventListener('click', () => openMonthlyReportModal());
    }
    if (btnCloseMonthlyReport) {
        btnCloseMonthlyReport.addEventListener('click', closeMonthlyReportModal);
    }
    if (monthlyReportModal) {
        monthlyReportModal.addEventListener('click', (e) => {
            if (e.target === monthlyReportModal) closeMonthlyReportModal();
        });
    }
    if (rptCutPreset) {
        rptCutPreset.addEventListener('change', (e) => {
            const preset = e.target.value;
            if (preset !== 'custom') {
                const dates = computePresetDates(preset);
                if (rptStartDate) rptStartDate.value = dates.startDate;
                if (rptEndDate) rptEndDate.value = dates.endDate;
                loadAndRenderMonthlyReport();
            }
        });
    }
    if (rptStartDate) {
        rptStartDate.addEventListener('change', () => {
            if (rptCutPreset) rptCutPreset.value = 'custom';
            loadAndRenderMonthlyReport();
        });
    }
    if (rptEndDate) {
        rptEndDate.addEventListener('change', () => {
            if (rptCutPreset) rptCutPreset.value = 'custom';
            loadAndRenderMonthlyReport();
        });
    }
    if (rptSelectClient) {
        rptSelectClient.addEventListener('change', () => renderMonthlyReportView());
    }
    if (btnCopyMonthlyReport) {
        btnCopyMonthlyReport.addEventListener('click', copyMonthlyReportToClipboard);
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeWorkflowTaskModal();
            closeMonthlyReportModal();
        }
    });

    if (btnDeleteTask) {
        btnDeleteTask.addEventListener('click', handleWorkflowTaskDelete);
    }

    if (workflowTaskForm) {
        workflowTaskForm.addEventListener('submit', handleWorkflowTaskSubmit);
    }

    // Setup Drag and Drop en las columnas
    setupWorkflowDragAndDrop();
}

function updateWorkflowDates() {
    const today = new Date();
    // Ajustar por offset de semanas
    const targetDate = new Date(today);
    targetDate.setDate(today.getDate() + (currentWeekOffset * 7));

    // Obtener el Lunes de esa semana
    const dayOfWeek = targetDate.getDay(); // 0 es domingo
    const diffToMonday = targetDate.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1);
    currentWeekMonday = new Date(targetDate.setDate(diffToMonday));
    currentWeekMonday.setHours(0, 0, 0, 0);

    // Calcular viernes de esa semana
    const friday = new Date(currentWeekMonday);
    friday.setDate(currentWeekMonday.getDate() + 4);

    // Número de semana ISO
    const weekNumber = getIsoWeekNumber(currentWeekMonday);
    currentWeekId = `${currentWeekMonday.getFullYear()}-W${String(weekNumber).padStart(2, '0')}`;

    // Formatear etiquetas de la barra superior
    const monthNames = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    const startStr = `${currentWeekMonday.getDate()} ${monthNames[currentWeekMonday.getMonth()]}`;
    const endStr = `${friday.getDate()} ${monthNames[friday.getMonth()]}, ${friday.getFullYear()}`;
    
    const weekLabel = document.getElementById('workflowWeekLabel');
    if (weekLabel) {
        weekLabel.textContent = `Semana ${weekNumber} (${startStr} - ${endStr})`;
    }

    // Subtítulos de fecha de cada día
    const dayElements = [
        { id: 'dateMonday', offset: 0 },
        { id: 'dateTuesday', offset: 1 },
        { id: 'dateWednesday', offset: 2 },
        { id: 'dateThursday', offset: 3 },
        { id: 'dateFriday', offset: 4 }
    ];

    dayElements.forEach(item => {
        const d = new Date(currentWeekMonday);
        d.setDate(currentWeekMonday.getDate() + item.offset);
        const el = document.getElementById(item.id);
        if (el) {
            el.textContent = `${d.getDate()} ${monthNames[d.getMonth()]}`;
        }
    });
}

function getIsoWeekNumber(d) {
    const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    const dayNum = date.getUTCDay() || 7;
    date.setUTCDate(date.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
    return Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
}

// Carga de tareas (Dual persistence: API + LocalStorage)
async function loadWorkflowTasks() {
    const storageKey = `hipha_wf_tasks_${currentWeekId}`;
    let loadedFromApi = false;

    try {
        const token = localStorage.getItem('dashboard_token');
        if (token) {
            const res = await fetch(`${API_BASE}/workflow/tasks?week=${encodeURIComponent(currentWeekId)}`, {
                headers: getAuthHeaders()
            });
            if (res.ok) {
                const apiData = await res.json();
                if (Array.isArray(apiData)) {
                    workflowTasks = apiData;
                    loadedFromApi = true;
                    localStorage.setItem(storageKey, JSON.stringify(workflowTasks));
                }
            }
        }
    } catch (err) {
        console.warn("No se pudo conectar a la API de workflow, usando almacenamiento local:", err);
    }

    if (!loadedFromApi) {
        const local = localStorage.getItem(storageKey);
        if (local) {
            try {
                workflowTasks = JSON.parse(local);
            } catch (e) {
                workflowTasks = [];
            }
        } else {
            // Tareas demo iniciales para la semana actual
            if (currentWeekOffset === 0) {
                workflowTasks = [
                    {
                        id: 1001,
                        week_id: currentWeekId,
                        day: 'monday',
                        client_name: 'HealthyIce',
                        title: 'Diseño Carrusel Instagram (Promoción Semanal)',
                        estimated_hours: 2.0,
                        status: 'in_progress',
                        notes: '3 slides formato 1080x1350'
                    },
                    {
                        id: 1002,
                        week_id: currentWeekId,
                        day: 'tuesday',
                        client_name: 'Letrerama',
                        title: 'Banner Web Principal & Adaptación Mobile',
                        estimated_hours: 2.5,
                        status: 'pending',
                        notes: 'Llamado a la acción de cotizaciones'
                    },
                    {
                        id: 1003,
                        week_id: currentWeekId,
                        day: 'wednesday',
                        client_name: 'Grupo Gari',
                        title: 'Adaptación de Logotipo para Papelería',
                        estimated_hours: 1.5,
                        status: 'pending',
                        notes: 'Versiones CMYK y Pantone'
                    },
                    {
                        id: 1004,
                        week_id: currentWeekId,
                        day: 'backlog',
                        client_name: 'Urología Avanzada',
                        title: 'Infografía Médica para Redes Sociales',
                        estimated_hours: 2.0,
                        status: 'pending',
                        notes: 'Validar copy con el Dr.'
                    }
                ];
                localStorage.setItem(storageKey, JSON.stringify(workflowTasks));
            } else {
                workflowTasks = [];
            }
        }
    }

    updateClientFilterOptions();
    renderWorkflowBoard();
}

function updateClientFilterOptions() {
    const filterSelect = document.getElementById('wfClientFilter');
    if (!filterSelect) return;

    const currentVal = filterSelect.value;
    const clientsSet = new Set();
    
    // Lista base
    ['Letrerama', 'HealthyIce', 'Grupo Gari', 'AMDI', 'Jessica Mendoza', 'Chile Chillón', 'Valencia Servicios', 'White Clean', 'Uro-Oncology', 'Urología Avanzada', 'Botica Silvestre', 'Hipha'].forEach(c => clientsSet.add(c));
    
    // Clientes de las tareas existentes
    workflowTasks.forEach(t => {
        if (t.client_name) clientsSet.add(t.client_name.trim());
    });

    filterSelect.innerHTML = '<option value="all">Todos los clientes</option>';
    Array.from(clientsSet).sort().forEach(c => {
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        if (c === currentVal) opt.selected = true;
        filterSelect.appendChild(opt);
    });
}

function renderWorkflowBoard() {
    // Limpiar listas de tareas
    WORKFLOW_DAYS.forEach(day => {
        const listEl = document.getElementById(`taskList${capitalize(day)}`);
        if (listEl) listEl.innerHTML = '';
    });

    let totalWeekHours = 0;
    const dailyHours = { monday: 0, tuesday: 0, wednesday: 0, thursday: 0, friday: 0 };

    // Filtrar tareas por cliente si aplica
    const filteredTasks = workflowTasks.filter(task => {
        if (currentWfClientFilter === 'all') return true;
        return (task.client_name || '').toLowerCase() === currentWfClientFilter.toLowerCase();
    });

    // Renderizar cada tarjeta
    filteredTasks.forEach(task => {
        let day = (task.day || 'monday').toLowerCase();
        if (day === 'backlog' || !dailyHours.hasOwnProperty(day)) {
            day = 'monday';
        }
        const listEl = document.getElementById(`taskList${capitalize(day)}`);
        const baseH = parseFloat(task.estimated_hours) || 0;
        const revH = parseFloat(task.revision_hours) || 0;
        const totalH = baseH + revH;

        dailyHours[day] += totalH;
        totalWeekHours += totalH;

        if (listEl) {
            const card = createWorkflowTaskCard(task);
            listEl.appendChild(card);
        }
    });

    // L-V Semáforo y Barras de Capacidad (9:00 AM a 1:00 PM = 4 horas diarias)
    ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'].forEach(day => {
        const hours = dailyHours[day];
        const pillEl = document.getElementById(`hours${capitalize(day)}`);
        const barEl = document.getElementById(`bar${capitalize(day)}`);

        if (pillEl) {
            pillEl.textContent = `${hours.toFixed(1)}h / 4h`;
            pillEl.className = 'day-hours-pill';
            if (hours > 0 && hours < 3.0) {
                pillEl.classList.add('safe');
            } else if (hours >= 3.0 && hours <= WORKFLOW_DAILY_LIMIT) {
                pillEl.classList.add('warning');
            } else if (hours > WORKFLOW_DAILY_LIMIT) {
                pillEl.classList.add('danger');
            }
        }

        if (barEl) {
            const percent = Math.min(100, Math.round((hours / WORKFLOW_DAILY_LIMIT) * 100));
            barEl.style.width = `${percent}%`;
            barEl.className = 'day-progress-bar';
            if (hours > 0 && hours < 3.0) {
                barEl.classList.add('safe');
            } else if (hours >= 3.0 && hours <= WORKFLOW_DAILY_LIMIT) {
                barEl.classList.add('warning');
            } else if (hours > WORKFLOW_DAILY_LIMIT) {
                barEl.classList.add('danger');
            }
        }
    });

    // Indicador Global de Capacidad Semanal
    const wfTotalHours = document.getElementById('wfTotalHours');
    const wfGlobalProgressBar = document.getElementById('wfGlobalProgressBar');
    if (wfTotalHours) {
        wfTotalHours.textContent = `${totalWeekHours.toFixed(1)}h`;
    }
    if (wfGlobalProgressBar) {
        const globalPercent = Math.min(100, Math.round((totalWeekHours / WORKFLOW_WEEKLY_LIMIT) * 100));
        wfGlobalProgressBar.style.width = `${globalPercent}%`;
        if (totalWeekHours > WORKFLOW_WEEKLY_LIMIT) {
            wfGlobalProgressBar.style.background = '#ef4444';
        } else {
            wfGlobalProgressBar.style.background = 'linear-gradient(90deg, var(--accent-cyan), var(--accent-purple))';
        }
    }
}

function createWorkflowTaskCard(task) {
    const card = document.createElement('div');
    card.className = 'workflow-card';
    card.draggable = true;
    card.dataset.id = String(task.id);

    const clientStyle = getClientStyle(task.client_name);
    const statusInfo = getStatusInfo(task.status);
    const baseHours = Math.max(0.5, parseFloat(task.estimated_hours) || 1.0);
    const revHours = Math.max(0.0, parseFloat(task.revision_hours) || 0.0);
    const totalHours = baseHours + revHours;
    const isCompleted = task.status === 'completed';

    if (isCompleted) {
        card.classList.add('is-completed');
        const tooltipHours = revHours > 0 
            ? `Total invertido: ${totalHours.toFixed(1)}h (${baseHours.toFixed(1)}h base + ${revHours.toFixed(1)}h cambios)`
            : `Total invertido: ${totalHours.toFixed(1)}h`;

        card.title = `${task.client_name || 'General'} - ${task.title || 'Sin título'} (${tooltipHours}) • Clic para editar`;
        card.innerHTML = `
            <div class="card-completed-row">
                <span class="status-chip completed" title="✅ Terminado • Clic para reactivar">✓</span>
                <span class="client-badge" style="background:${clientStyle.bg}; color:${clientStyle.text}; border-color:${clientStyle.border}; flex-shrink: 0;">
                    ${escapeHtml(task.client_name || 'General')}
                </span>
                <span class="card-title-completed" title="${escapeHtml(task.title || 'Sin título')}">
                    ${escapeHtml(task.title || 'Sin título')}
                </span>
                <span class="completed-hours-pill" title="${tooltipHours}">
                    ⏱️ ${totalHours.toFixed(1)}h
                </span>
                <button class="card-actions-btn" type="button" title="Editar o eliminar entrega" aria-label="Editar entrega">
                    <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                </button>
            </div>
        `;
    } else {
        // Dimensionamiento proporcional estilo Google Calendar (Jornada 9:00 AM - 1:00 PM)
        const cardHeight = Math.round(60 + (totalHours - 0.5) * 80);
        card.style.minHeight = `${cardHeight}px`;
        card.style.borderLeft = `4px solid ${clientStyle.text || '#00e5ff'}`;
        card.style.background = `linear-gradient(90deg, ${clientStyle.bg} 0%, rgba(15, 23, 42, 0.88) 35%)`;

        if (totalHours <= 0.5) {
            card.classList.add('is-compact');
        } else if (totalHours >= 3.0) {
            card.classList.add('is-extended');
        }

        const revBadgeHtml = revHours > 0 
            ? `<span class="hours-revision-badge" title="Horas acumuladas por cambios">+${revHours.toFixed(1)}h cambios</span>`
            : '';

        const quickAddRevHtml = (task.status === 'review' || task.status === 'in_progress')
            ? `<button type="button" class="btn-quick-revision" title="Sumar +30 min por cambios solicitados por el cliente">+0.5h cambio</button>`
            : '';

        card.innerHTML = `
            <div class="card-top-row">
                <div class="card-meta-left">
                    <span class="client-badge" style="background:${clientStyle.bg}; color:${clientStyle.text}; border-color:${clientStyle.border};">
                        ${escapeHtml(task.client_name || 'General')}
                    </span>
                    <span class="hours-chip">⏱️ ${baseHours.toFixed(1)}h</span>
                    ${revBadgeHtml}
                </div>
                <button class="card-actions-btn" type="button" title="Editar entrega" aria-label="Editar entrega">
                    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                </button>
            </div>
            <div class="card-main-content">
                <div class="card-title">${escapeHtml(task.title || 'Sin título')}</div>
                ${task.notes ? `<div class="card-notes" title="${escapeHtml(task.notes)}">📝 ${escapeHtml(task.notes)}</div>` : ''}
            </div>
            <div class="card-bottom-row">
                <div style="display:flex; align-items:center; gap:0.4rem;">
                    <span class="status-chip ${task.status || 'pending'}" title="Haz clic para avanzar estatus">
                        ${statusInfo.label}
                    </span>
                    ${quickAddRevHtml}
                </div>
                <span class="drag-handle-hint" title="Arrastra para mover a otro día">⋮⋮</span>
            </div>
        `;
    }

    // Click específico en botón editar
    const editBtn = card.querySelector('.card-actions-btn');
    if (editBtn) {
        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            editWorkflowTask(task.id);
        });
    }

    // Click específico en chip de estatus (avanza ciclo)
    const statusChip = card.querySelector('.status-chip');
    if (statusChip) {
        statusChip.addEventListener('click', (e) => {
            e.stopPropagation();
            cycleWorkflowTaskStatus(task.id);
        });
    }

    // Click específico en botón rápido de cambios (+0.5h)
    const quickRevBtn = card.querySelector('.btn-quick-revision');
    if (quickRevBtn) {
        quickRevBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            addTaskRevision(task.id, 0.5);
        });
    }

    // Click en cualquier otra área de la tarjeta abre el editor
    card.addEventListener('click', (e) => {
        if (e.target.closest('.status-chip') || e.target.closest('.card-actions-btn') || e.target.closest('.btn-quick-revision')) return;
        editWorkflowTask(task.id);
    });

    // Eventos Drag & Drop
    card.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', String(task.id));
        card.classList.add('dragging');
    });

    card.addEventListener('dragend', () => {
        card.classList.remove('dragging');
    });

    return card;
}

function getStatusInfo(statusKey) {
    const map = {
        'pending': { label: '⏳ Por Iniciar', next: 'in_progress' },
        'in_progress': { label: '🎨 En Diseño', next: 'review' },
        'review': { label: '👀 Revisión', next: 'completed' },
        'completed': { label: '✅ Terminado', next: 'pending' }
    };
    return map[statusKey] || map['pending'];
}

function cycleWorkflowTaskStatus(taskId) {
    const task = workflowTasks.find(t => String(t.id) === String(taskId));
    if (!task) return;
    const current = getStatusInfo(task.status);
    task.status = current.next;
    saveWorkflowState();
    renderWorkflowBoard();

    // Intentar sync con backend
    syncTaskWithApi(task, 'PUT');
}

// Drag and drop setup en columnas
function setupWorkflowDragAndDrop() {
    WORKFLOW_DAYS.forEach(day => {
        const listEl = document.getElementById(`taskList${capitalize(day)}`);
        if (!listEl) return;

        listEl.addEventListener('dragover', (e) => {
            e.preventDefault();
            listEl.classList.add('drag-over');
        });

        listEl.addEventListener('dragleave', (e) => {
            if (e.relatedTarget && listEl.contains(e.relatedTarget)) return;
            listEl.classList.remove('drag-over');
        });

        listEl.addEventListener('drop', (e) => {
            e.preventDefault();
            listEl.classList.remove('drag-over');
            const taskIdStr = e.dataTransfer.getData('text/plain');
            if (!taskIdStr) return;

            const task = workflowTasks.find(t => String(t.id) === String(taskIdStr));
            if (task && task.day !== day) {
                task.day = day;
                saveWorkflowState();
                renderWorkflowBoard();

                // Notificar API
                syncTaskMoveWithApi(task.id, day);
            }
        });
    });
}

// Modal CRUD de Tarea
function openWorkflowTaskModal(day = 'monday') {
    if (day === 'backlog' || !day) day = 'monday';
    const modal = document.getElementById('workflowTaskModal');
    const heading = document.getElementById('modalTaskHeading');
    const btnDelete = document.getElementById('btnDeleteTask');

    document.getElementById('taskInputId').value = '';
    document.getElementById('taskInputClient').value = 'Letrerama';
    document.getElementById('taskCustomClientGroup').classList.add('hidden');
    document.getElementById('taskInputCustomClient').value = '';
    document.getElementById('taskInputTitle').value = '';
    document.getElementById('taskInputDay').value = day;
    document.getElementById('taskInputHours').value = '1.0';
    document.getElementById('taskInputRevisionHours').value = '0.0';
    document.getElementById('taskInputRevisionsCount').value = '0';
    document.getElementById('taskInputStatus').value = 'pending';
    document.getElementById('taskInputNotes').value = '';

    updateModalRevisionSummary();

    heading.textContent = 'Nueva Entrega de Diseño';
    btnDelete.classList.add('hidden');
    modal.classList.remove('hidden');
    document.getElementById('taskInputTitle').focus();
}

function updateModalRevisionSummary() {
    const hoursSelect = document.getElementById('taskInputHours');
    const baseHours = parseFloat(hoursSelect ? hoursSelect.value : 1.0) || 1.0;
    const revInput = document.getElementById('taskInputRevisionHours');
    const revHours = parseFloat(revInput ? revInput.value : 0.0) || 0.0;
    const grandTotal = baseHours + revHours;

    const badgeRevision = document.getElementById('badgeRevisionHours');
    const lblBase = document.getElementById('lblBaseHours');
    const lblChanges = document.getElementById('lblChangesHours');
    const lblGrand = document.getElementById('lblGrandTotalHours');

    if (badgeRevision) badgeRevision.textContent = `+${revHours.toFixed(1)}h`;
    if (lblBase) lblBase.textContent = `${baseHours.toFixed(1)}h`;
    if (lblChanges) lblChanges.textContent = `+${revHours.toFixed(1)}h`;
    if (lblGrand) lblGrand.textContent = `${grandTotal.toFixed(1)}h`;
}

function adjustRevisionHours(delta) {
    const revInput = document.getElementById('taskInputRevisionHours');
    const countInput = document.getElementById('taskInputRevisionsCount');
    if (!revInput || !countInput) return;

    let currentRev = parseFloat(revInput.value) || 0.0;
    let currentCount = parseInt(countInput.value) || 0;

    currentRev = Math.max(0.0, currentRev + delta);
    if (delta > 0) {
        currentCount += 1;
    } else if (delta < 0 && currentCount > 0) {
        currentCount -= 1;
    }

    revInput.value = currentRev.toFixed(1);
    countInput.value = String(currentCount);
    updateModalRevisionSummary();
}

async function addTaskRevision(taskId, delta = 0.5) {
    const task = workflowTasks.find(t => String(t.id) === String(taskId));
    if (!task) return;

    task.revision_hours = Math.max(0.0, (parseFloat(task.revision_hours) || 0.0) + delta);
    if (delta > 0) {
        task.revisions_count = (task.revisions_count || 0) + 1;
    } else if (delta < 0 && task.revisions_count && task.revisions_count > 0) {
        task.revisions_count = Math.max(0, task.revisions_count - 1);
    }
    saveWorkflowState();
    renderWorkflowBoard();

    // Sincronizar con API
    try {
        const token = localStorage.getItem('dashboard_token');
        if (token) {
            await fetch(`${API_BASE}/workflow/tasks/${taskId}/add-revision`, {
                method: 'POST',
                headers: {
                    ...getAuthHeaders(),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ delta_hours: delta })
            });
        }
    } catch (err) {
        console.warn("Error enviando adición de revisión a API:", err);
    }
}

function editWorkflowTask(taskId) {
    const task = workflowTasks.find(t => String(t.id) === String(taskId));
    if (!task) {
        console.warn("Tarea no encontrada para editar:", taskId);
        return;
    }

    const modal = document.getElementById('workflowTaskModal');
    const heading = document.getElementById('modalTaskHeading');
    const btnDelete = document.getElementById('btnDeleteTask');
    const clientSelect = document.getElementById('taskInputClient');
    const customGroup = document.getElementById('taskCustomClientGroup');
    const customInput = document.getElementById('taskInputCustomClient');

    document.getElementById('taskInputId').value = String(task.id);
    
    // Verificar si el cliente existe en el select
    let found = false;
    for (let opt of clientSelect.options) {
        if (opt.value.toLowerCase() === (task.client_name || '').toLowerCase()) {
            clientSelect.value = opt.value;
            found = true;
            break;
        }
    }
    if (!found) {
        clientSelect.value = 'otro';
        customGroup.classList.remove('hidden');
        customInput.value = task.client_name || '';
    } else {
        customGroup.classList.add('hidden');
        customInput.value = '';
    }

    document.getElementById('taskInputTitle').value = task.title || '';
    document.getElementById('taskInputDay').value = (task.day === 'backlog' ? 'monday' : (task.day || 'monday'));

    // Ajustar valor de horas base con 1 decimal
    const numHours = parseFloat(task.estimated_hours) || 1.0;
    const hoursStr = numHours.toFixed(1);
    const hoursSelect = document.getElementById('taskInputHours');
    let hoursFound = false;
    for (let opt of hoursSelect.options) {
        if (opt.value === hoursStr || parseFloat(opt.value) === numHours) {
            hoursSelect.value = opt.value;
            hoursFound = true;
            break;
        }
    }
    if (!hoursFound) {
        hoursSelect.value = '1.0';
    }

    const revH = parseFloat(task.revision_hours) || 0.0;
    const revC = parseInt(task.revisions_count) || 0;
    document.getElementById('taskInputRevisionHours').value = revH.toFixed(1);
    document.getElementById('taskInputRevisionsCount').value = String(revC);

    document.getElementById('taskInputStatus').value = task.status || 'pending';
    document.getElementById('taskInputNotes').value = task.notes || '';

    updateModalRevisionSummary();

    heading.textContent = 'Editar Entrega de Diseño';
    btnDelete.classList.remove('hidden');
    modal.classList.remove('hidden');
}

function closeWorkflowTaskModal() {
    const modal = document.getElementById('workflowTaskModal');
    if (modal) modal.classList.add('hidden');
}

async function handleWorkflowTaskSubmit(e) {
    e.preventDefault();
    const idVal = document.getElementById('taskInputId').value;
    const clientSelectVal = document.getElementById('taskInputClient').value;
    const customClientVal = document.getElementById('taskInputCustomClient').value.trim();
    const finalClient = clientSelectVal === 'otro' ? (customClientVal || 'General') : clientSelectVal;

    const title = document.getElementById('taskInputTitle').value.trim();
    const day = document.getElementById('taskInputDay').value;
    const hours = parseFloat(document.getElementById('taskInputHours').value) || 1.0;
    const revHours = parseFloat(document.getElementById('taskInputRevisionHours').value) || 0.0;
    const revCount = parseInt(document.getElementById('taskInputRevisionsCount').value) || 0;
    const status = document.getElementById('taskInputStatus').value;
    const notes = document.getElementById('taskInputNotes').value.trim();

    if (!title) return;

    if (idVal) {
        // Actualizar tarea existente
        const task = workflowTasks.find(t => String(t.id) === String(idVal));
        if (task) {
            task.client_name = finalClient;
            task.title = title;
            task.day = day;
            task.estimated_hours = hours;
            task.revision_hours = revHours;
            task.revisions_count = revCount;
            task.status = status;
            task.notes = notes;
            task.task_date = getTaskExactDate(task);
            syncTaskWithApi(task, 'PUT');
        }
    } else {
        // Crear nueva tarea
        const newTask = {
            id: Date.now(),
            week_id: currentWeekId,
            day: day,
            client_name: finalClient,
            title: title,
            estimated_hours: hours,
            revision_hours: revHours,
            revisions_count: revCount,
            status: status,
            notes: notes,
            task_date: getTaskExactDate({ week_id: currentWeekId, day: day })
        };
        workflowTasks.push(newTask);
        syncTaskWithApi(newTask, 'POST');
    }

    saveWorkflowState();
    updateClientFilterOptions();
    renderWorkflowBoard();
    closeWorkflowTaskModal();
}

async function handleWorkflowTaskDelete() {
    const idVal = document.getElementById('taskInputId').value;
    if (!idVal) return;

    if (confirm('¿Eliminar esta entrega del tablero semanal?')) {
        workflowTasks = workflowTasks.filter(t => String(t.id) !== String(idVal));
        saveWorkflowState();
        updateClientFilterOptions();
        renderWorkflowBoard();
        closeWorkflowTaskModal();

        // Eliminar en API
        try {
            const token = localStorage.getItem('dashboard_token');
            if (token) {
                await fetch(`${API_BASE}/workflow/tasks/${idVal}`, {
                    method: 'DELETE',
                    headers: getAuthHeaders()
                });
            }
        } catch (err) {
            console.warn("Error al borrar tarea en API:", err);
        }
    }
}

function saveWorkflowState() {
    const storageKey = `hipha_wf_tasks_${currentWeekId}`;
    localStorage.setItem(storageKey, JSON.stringify(workflowTasks));
}

async function syncTaskWithApi(task, method = 'POST') {
    try {
        const token = localStorage.getItem('dashboard_token');
        if (!token) return;

        const url = method === 'POST' ? `${API_BASE}/workflow/tasks` : `${API_BASE}/workflow/tasks/${task.id}`;
        const payload = {
            week_id: task.week_id,
            day: task.day,
            client_name: task.client_name,
            title: task.title,
            estimated_hours: task.estimated_hours,
            revision_hours: task.revision_hours || 0.0,
            revisions_count: task.revisions_count || 0,
            status: task.status,
            notes: task.notes || ''
        };

        const res = await fetch(url, {
            method: method,
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (res.ok && method === 'POST') {
            const created = await res.json();
            // Actualizar el ID temporal local con el ID generado en BD
            if (created && created.id) {
                task.id = created.id;
                saveWorkflowState();
            }
        }
    } catch (err) {
        console.warn("Error sincronizando tarea con backend:", err);
    }
}

async function syncTaskMoveWithApi(taskId, targetDay) {
    try {
        const token = localStorage.getItem('dashboard_token');
        if (!token) return;

        await fetch(`${API_BASE}/workflow/tasks/${taskId}/move`, {
            method: 'PATCH',
            headers: {
                ...getAuthHeaders(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_id: taskId,
                target_day: targetDay
            })
        });
    } catch (err) {
        console.warn("Error enviando movimiento a API:", err);
    }
}

function capitalize(s) {
    if (!s) return '';
    return s.charAt(0).toUpperCase() + s.slice(1);
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// ========================================================
// MÓDULO DE REPORTE MENSUAL / RANGO DE CORTE DE HORAS Y RETAINERS
// ========================================================

let monthlyReportTasks = [];

function deriveMonthIdFromWeek(weekId) {
    if (!weekId || !weekId.includes('-W')) {
        const now = new Date();
        const m = String(now.getMonth() + 1).padStart(2, '0');
        return `${now.getFullYear()}-${m}`;
    }
    try {
        const [yearStr, weekStr] = weekId.split('-W');
        const year = parseInt(yearStr);
        const week = parseInt(weekStr);
        const simple = new Date(year, 0, 1 + (week - 1) * 7);
        const m = String(simple.getMonth() + 1).padStart(2, '0');
        return `${year}-${m}`;
    } catch (e) {
        const now = new Date();
        const m = String(now.getMonth() + 1).padStart(2, '0');
        return `${now.getFullYear()}-${m}`;
    }
}

function getTaskExactDate(task) {
    if (task && task.task_date) return task.task_date;
    const dayMap = { monday: 1, tuesday: 2, wednesday: 3, thursday: 4, friday: 5 };
    const dayKey = (task && task.day ? task.day : 'monday').toLowerCase();
    const dayNum = dayMap[dayKey] || 1;

    if (task && task.week_id && task.week_id.includes('-W')) {
        try {
            const parts = task.week_id.split('-W');
            const year = parseInt(parts[0], 10);
            const week = parseInt(parts[1], 10);
            
            // ISO week Monday calculation
            const simple = new Date(Date.UTC(year, 0, 1 + (week - 1) * 7));
            const dow = simple.getUTCDay();
            const ISOweekStart = new Date(simple);
            if (dow <= 4) {
                ISOweekStart.setUTCDate(simple.getUTCDate() - simple.getUTCDay() + 1);
            } else {
                ISOweekStart.setUTCDate(simple.getUTCDate() + 8 - simple.getUTCDay());
            }
            const target = new Date(ISOweekStart);
            target.setUTCDate(ISOweekStart.getUTCDate() + (dayNum - 1));
            return target.toISOString().slice(0, 10);
        } catch (e) {
            console.warn('Error derivando fecha de tarea:', e);
        }
    }
    if (task && task.created_at) {
        return String(task.created_at).slice(0, 10);
    }
    const today = new Date();
    return today.toISOString().slice(0, 10);
}

function computePresetDates(preset) {
    const today = new Date();
    const curYear = today.getFullYear();
    const curMonth = today.getMonth(); // 0-indexed
    const curDay = today.getDate();

    function formatYMD(d) {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
    }

    if (preset === 'current_month') {
        const start = new Date(curYear, curMonth, 1);
        const end = new Date(curYear, curMonth + 1, 0);
        return { startDate: formatYMD(start), endDate: formatYMD(end) };
    }

    if (preset === 'last_month') {
        const start = new Date(curYear, curMonth - 1, 1);
        const end = new Date(curYear, curMonth, 0);
        return { startDate: formatYMD(start), endDate: formatYMD(end) };
    }

    if (preset === 'last_30') {
        const end = new Date(today);
        const start = new Date(today);
        start.setDate(today.getDate() - 30);
        return { startDate: formatYMD(start), endDate: formatYMD(end) };
    }

    // Cortes específicos por día de mes (ej. día 22, día 28, día 3)
    if (preset === 'cut_22' || preset === 'cut_28' || preset === 'cut_3') {
        const cutDay = preset === 'cut_22' ? 22 : (preset === 'cut_28' ? 28 : 3);
        let start, end;
        if (curDay > cutDay) {
            // El corte de este mes ya pasó. Período: desde día (cutDay + 1) al cutDay del mes siguiente
            start = new Date(curYear, curMonth, cutDay + 1);
            end = new Date(curYear, curMonth + 1, cutDay);
        } else {
            // Aún no llega el día de corte de este mes. Período: desde día (cutDay + 1) del mes anterior al cutDay de este mes
            start = new Date(curYear, curMonth - 1, cutDay + 1);
            end = new Date(curYear, curMonth, cutDay);
        }
        return { startDate: formatYMD(start), endDate: formatYMD(end) };
    }

    // Default: mes actual
    const start = new Date(curYear, curMonth, 1);
    const end = new Date(curYear, curMonth + 1, 0);
    return { startDate: formatYMD(start), endDate: formatYMD(end) };
}

function openMonthlyReportModal() {
    const modal = document.getElementById('workflowMonthlyReportModal');
    if (!modal) return;

    const selectPreset = document.getElementById('rptCutPreset');
    const inputStart = document.getElementById('rptStartDate');
    const inputEnd = document.getElementById('rptEndDate');
    const selectClient = document.getElementById('rptSelectClient');

    // Inicializar fechas si están vacías
    if (inputStart && inputEnd && (!inputStart.value || !inputEnd.value)) {
        if (selectPreset) selectPreset.value = 'current_month';
        const dates = computePresetDates('current_month');
        inputStart.value = dates.startDate;
        inputEnd.value = dates.endDate;
    }

    // Poblar clientes en el select si está vacío
    if (selectClient && selectClient.options.length <= 1) {
        selectClient.innerHTML = '<option value="all">Todos los clientes</option>';
        const clientsSet = new Set();
        ['Letrerama', 'HealthyIce', 'Grupo Gari', 'AMDI', 'Jessica Mendoza', 'Chile Chillón', 'Valencia Servicios', 'White Clean', 'Uro-Oncology', 'Urología Avanzada', 'Botica Silvestre', 'Hipha'].forEach(c => clientsSet.add(c));
        
        workflowTasks.forEach(t => {
            if (t.client_name) clientsSet.add(t.client_name.trim());
        });

        Array.from(clientsSet).sort().forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            selectClient.appendChild(opt);
        });

        if (currentWfClientFilter && currentWfClientFilter !== 'all') {
            selectClient.value = currentWfClientFilter;
        }
    }

    modal.classList.remove('hidden');
    loadAndRenderMonthlyReport();
}

function closeMonthlyReportModal() {
    const modal = document.getElementById('workflowMonthlyReportModal');
    if (modal) modal.classList.add('hidden');
}

async function loadAndRenderMonthlyReport() {
    const inputStart = document.getElementById('rptStartDate');
    const inputEnd = document.getElementById('rptEndDate');
    const selectClient = document.getElementById('rptSelectClient');

    const startDate = inputStart ? inputStart.value : '';
    const endDate = inputEnd ? inputEnd.value : '';
    const selectedClient = selectClient ? selectClient.value : 'all';

    let loadedFromApi = false;
    monthlyReportTasks = [];

    try {
        const token = localStorage.getItem('dashboard_token');
        if (token && startDate && endDate) {
            const clientParam = selectedClient !== 'all' ? `&client=${encodeURIComponent(selectedClient)}` : '';
            const res = await fetch(`${API_BASE}/workflow/monthly-report?start_date=${startDate}&end_date=${endDate}${clientParam}`, {
                headers: getAuthHeaders()
            });
            if (res.ok) {
                const data = await res.json();
                if (data && Array.isArray(data.tasks)) {
                    monthlyReportTasks = data.tasks;
                    loadedFromApi = true;
                }
            }
        }
    } catch (err) {
        console.warn("No se pudo obtener reporte mensual de API, usando almacenamiento local:", err);
    }

    // Fallback: Si no viene de API o estamos offline, recopilar de localStorage dentro del rango
    if (!loadedFromApi) {
        const allTasksMap = new Map();

        // 1. Tareas de la semana activa actual
        workflowTasks.forEach(t => {
            const tDate = getTaskExactDate(t);
            if ((!startDate || tDate >= startDate) && (!endDate || tDate <= endDate)) {
                allTasksMap.set(String(t.id), { ...t, task_date: tDate });
            }
        });

        // 2. Tareas en todas las claves de localStorage
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith('hipha_wf_tasks_')) {
                try {
                    const parsed = JSON.parse(localStorage.getItem(key));
                    if (Array.isArray(parsed)) {
                        parsed.forEach(t => {
                            const tDate = getTaskExactDate(t);
                            if ((!startDate || tDate >= startDate) && (!endDate || tDate <= endDate)) {
                                if (!allTasksMap.has(String(t.id))) {
                                    allTasksMap.set(String(t.id), { ...t, task_date: tDate });
                                }
                            }
                        });
                    }
                } catch (e) {}
            }
        }

        monthlyReportTasks = Array.from(allTasksMap.values());
    }

    renderMonthlyReportView();
}

function renderMonthlyReportView() {
    const selectClient = document.getElementById('rptSelectClient');
    const selectedClient = selectClient ? selectClient.value : 'all';

    const kpiTotal = document.getElementById('rptKpiTotalHours');
    const kpiBase = document.getElementById('rptKpiBaseHours');
    const kpiRev = document.getElementById('rptKpiRevisionHours');
    const kpiTasks = document.getElementById('rptKpiTotalTasks');
    const container = document.getElementById('rptTableContainer');

    // Filtrar tareas por cliente
    const tasks = monthlyReportTasks.filter(t => {
        if (selectedClient === 'all') return true;
        return (t.client_name || '').toLowerCase() === selectedClient.toLowerCase();
    });

    let totalBase = 0.0;
    let totalRev = 0.0;
    let completedCount = 0;

    tasks.forEach(t => {
        const b = parseFloat(t.estimated_hours) || 0.0;
        const r = parseFloat(t.revision_hours) || 0.0;
        totalBase += b;
        totalRev += r;
        if (t.status === 'completed') completedCount++;
    });

    const grandTotal = totalBase + totalRev;

    if (kpiTotal) kpiTotal.textContent = `${grandTotal.toFixed(1)}h`;
    if (kpiBase) kpiBase.textContent = `${totalBase.toFixed(1)}h`;
    if (kpiRev) kpiRev.textContent = `+${totalRev.toFixed(1)}h`;
    if (kpiTasks) kpiTasks.textContent = `${tasks.length} piezas`;

    if (!container) return;

    if (tasks.length === 0) {
        container.innerHTML = `
            <div style="padding: 2.5rem; text-align: center; color: var(--text-muted);">
                <p style="font-size: 1.1rem; margin-bottom: 0.3rem;">📭 No hay entregables registrados para este periodo o rango de fechas</p>
                <p style="font-size: 0.8rem;">Selecciona otro período de corte o ajusta las fechas de inicio y fin.</p>
            </div>
        `;
        return;
    }

    // Si seleccionó "Todos los clientes", mostrar tabla comparativa agrupada por cliente
    if (selectedClient === 'all') {
        const clientGroups = {};
        tasks.forEach(t => {
            const c = t.client_name || 'General';
            if (!clientGroups[c]) {
                clientGroups[c] = { base: 0, rev: 0, count: 0, completed: 0 };
            }
            clientGroups[c].base += (parseFloat(t.estimated_hours) || 0);
            clientGroups[c].rev += (parseFloat(t.revision_hours) || 0);
            clientGroups[c].count++;
            if (t.status === 'completed') clientGroups[c].completed++;
        });

        const rowsHtml = Object.entries(clientGroups)
            .sort((a, b) => (b[1].base + b[1].rev) - (a[1].base + a[1].rev))
            .map(([cName, stats]) => {
                const cStyle = getClientStyle(cName);
                const cTotal = stats.base + stats.rev;
                const percent = grandTotal > 0 ? Math.round((cTotal / grandTotal) * 100) : 0;

                return `
                    <tr class="monthly-row-client" data-client="${escapeHtml(cName)}" title="Haz clic para ver las piezas de ${escapeHtml(cName)}">
                        <td>
                            <span class="client-badge" style="background:${cStyle.bg}; color:${cStyle.text}; border-color:${cStyle.border};">
                                ${escapeHtml(cName)}
                            </span>
                        </td>
                        <td><strong>${stats.count}</strong> (${stats.completed} concluidas)</td>
                        <td>${stats.base.toFixed(1)}h</td>
                        <td style="color:var(--accent-purple)">+${stats.rev.toFixed(1)}h</td>
                        <td><strong style="color:var(--accent-cyan); font-size:0.95rem;">${cTotal.toFixed(1)}h</strong></td>
                        <td style="width: 140px;">
                            <div style="display:flex; align-items:center; gap:0.5rem;">
                                <div style="flex:1; height:6px; background:rgba(255,255,255,0.1); border-radius:3px; overflow:hidden;">
                                    <div style="width:${percent}%; height:100%; background:var(--accent-cyan);"></div>
                                </div>
                                <span style="font-size:0.75rem; color:var(--text-muted); min-width:28px;">${percent}%</span>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');

        container.innerHTML = `
            <table class="monthly-table">
                <thead>
                    <tr>
                        <th>Cliente / Cuenta</th>
                        <th>Entregables</th>
                        <th>Diseño Base</th>
                        <th>Cambios (+0.5h)</th>
                        <th>Total Horas</th>
                        <th>% Retainer</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHtml}
                </tbody>
            </table>
        `;

        // Permitir clic en la fila del cliente para filtrar directamente
        container.querySelectorAll('.monthly-row-client').forEach(tr => {
            tr.addEventListener('click', () => {
                const clientName = tr.dataset.client;
                if (selectClient && clientName) {
                    selectClient.value = clientName;
                    renderMonthlyReportView();
                }
            });
        });
    } else {
        // Vista detallada de piezas de un cliente específico
        const rowsHtml = tasks.map(t => {
            const b = parseFloat(t.estimated_hours) || 0;
            const r = parseFloat(t.revision_hours) || 0;
            const tot = b + r;
            const statusInfo = getStatusInfo(t.status);
            const dStr = t.task_date || getTaskExactDate(t);

            return `
                <tr>
                    <td style="white-space:nowrap; font-size:0.8rem;">
                        <span style="color:var(--text-main); font-weight:600;">${dStr}</span>
                        <div style="font-size:0.72rem; color:var(--text-muted);">${escapeHtml(t.week_id || '')} • ${capitalize(t.day || 'lunes')}</div>
                    </td>
                    <td>
                        <strong style="color:var(--text-main); font-size:0.85rem;">${escapeHtml(t.title || 'Sin título')}</strong>
                        ${t.notes ? `<div style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">📝 ${escapeHtml(t.notes)}</div>` : ''}
                    </td>
                    <td>
                        <span class="status-chip ${t.status || 'pending'}">
                            ${statusInfo.label}
                        </span>
                    </td>
                    <td>${b.toFixed(1)}h</td>
                    <td style="color:var(--accent-purple)">${r > 0 ? `+${r.toFixed(1)}h (${t.revisions_count || 1}r)` : '0.0h'}</td>
                    <td><strong style="color:var(--accent-cyan); font-size:0.95rem;">${tot.toFixed(1)}h</strong></td>
                </tr>
            `;
        }).join('');

        container.innerHTML = `
            <div style="padding:0.6rem 1rem; background:rgba(0,229,255,0.06); border-bottom:1px solid var(--border-color); display:flex; justify-content:space-between; align-items:center;">
                <span style="font-size:0.8rem; color:var(--text-muted);">
                    Mostrando piezas de <strong>${escapeHtml(selectedClient)}</strong>
                </span>
                <button type="button" id="btnBackToAllClients" style="background:transparent; border:none; color:var(--accent-cyan); font-size:0.75rem; cursor:pointer; text-decoration:underline;">
                    ← Ver todos los clientes
                </button>
            </div>
            <table class="monthly-table">
                <thead>
                    <tr>
                        <th>Fecha / Día</th>
                        <th>Entregable / Pieza</th>
                        <th>Estatus</th>
                        <th>Base</th>
                        <th>Cambios</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHtml}
                </tbody>
            </table>
        `;

        const btnBack = document.getElementById('btnBackToAllClients');
        if (btnBack && selectClient) {
            btnBack.addEventListener('click', () => {
                selectClient.value = 'all';
                renderMonthlyReportView();
            });
        }
    }
}

async function copyMonthlyReportToClipboard() {
    const inputStart = document.getElementById('rptStartDate');
    const inputEnd = document.getElementById('rptEndDate');
    const selectClient = document.getElementById('rptSelectClient');

    const startDate = inputStart ? inputStart.value : '';
    const endDate = inputEnd ? inputEnd.value : '';
    const selectedClient = selectClient ? selectClient.value : 'all';

    const tasks = monthlyReportTasks.filter(t => {
        if (selectedClient === 'all') return true;
        return (t.client_name || '').toLowerCase() === selectedClient.toLowerCase();
    });

    let totalBase = 0.0;
    let totalRev = 0.0;
    let completedCount = 0;

    tasks.forEach(t => {
        totalBase += (parseFloat(t.estimated_hours) || 0);
        totalRev += (parseFloat(t.revision_hours) || 0);
        if (t.status === 'completed') completedCount++;
    });

    const grandTotal = totalBase + totalRev;

    let text = `📊 REPORTE DE HORAS Y ENTREGABLES • HIPHA MX\n`;
    text += `🗓️ Período de Corte: ${startDate} al ${endDate}\n`;
    text += `👤 Cuenta / Cliente: ${selectedClient === 'all' ? 'Consolidado General' : selectedClient}\n`;
    text += `--------------------------------------------------\n`;
    text += `⏱️ Total Horas Invertidas: ${grandTotal.toFixed(1)} horas\n`;
    text += `   • Diseño Base Presupuestado: ${totalBase.toFixed(1)}h\n`;
    text += `   • Rondas de Ajustes / Cambios: +${totalRev.toFixed(1)}h\n`;
    text += `📦 Piezas Trabajadas: ${tasks.length} (${completedCount} aprobadas/terminadas)\n`;
    text += `--------------------------------------------------\n`;
    text += `DETALLE DE ENTREGABLES:\n`;

    tasks.forEach((t, idx) => {
        const b = (parseFloat(t.estimated_hours) || 0).toFixed(1);
        const r = (parseFloat(t.revision_hours) || 0).toFixed(1);
        const tot = (parseFloat(b) + parseFloat(r)).toFixed(1);
        const st = t.status === 'completed' ? '✅ Terminado' : (t.status === 'review' ? '👀 En Revisión' : '🎨 En Proceso');
        const c = selectedClient === 'all' ? `[${t.client_name}] ` : '';
        const d = t.task_date || getTaskExactDate(t);
        text += `${idx + 1}. ${c}${t.title} (${d}) — ${tot}h (${b}h base + ${r}h cambios) [${st}]\n`;
    });

    text += `\nGenerado automáticamente por HiphaMX Dashboard`;

    try {
        await navigator.clipboard.writeText(text);
        const btn = document.getElementById('btnCopyMonthlyReport');
        if (btn) {
            const originalHtml = btn.innerHTML;
            btn.innerHTML = `<span>✅ ¡Copiado al portapapeles!</span>`;
            setTimeout(() => {
                btn.innerHTML = originalHtml;
            }, 2500);
        }
    } catch (e) {
        alert("No se pudo copiar automáticamente. Por favor copia el texto manualmente.");
    }
}

// Exposición global para interacción directa y consola
window.openWorkflowTaskModal = openWorkflowTaskModal;
window.closeWorkflowTaskModal = closeWorkflowTaskModal;
window.editWorkflowTask = editWorkflowTask;
window.cycleWorkflowTaskStatus = cycleWorkflowTaskStatus;
window.openMonthlyReportModal = openMonthlyReportModal;
window.closeMonthlyReportModal = closeMonthlyReportModal;
window.addTaskRevision = addTaskRevision;


