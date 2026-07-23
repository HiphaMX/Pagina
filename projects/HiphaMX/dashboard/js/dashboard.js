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
const navLinkSocial = document.getElementById('navLinkSocial');
const navLinkSat = document.getElementById('navLinkSat');
const trafficSection = document.getElementById('trafficSection');
const satSection = document.getElementById('satSection');
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
            trafficDateSelector.classList.remove('hidden');
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
    loadOverviewData();
}

function showLogin() {
    loginScreen.classList.remove('hidden');
    dashboardLayout.classList.add('hidden');
}

async function handleLogin(e) {
    e.preventDefault();
    loginError.classList.add('hidden');

    const username = usernameInput.value;
    const password = passwordInput.value;

    // Usar FormData para OAuth2PasswordRequestForm
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch(`${AUTH_BASE}/login`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('dashboard_token', data.access_token);
            showDashboard();
        } else {
            loginError.textContent = "Usuario o contraseña incorrectos.";
            loginError.classList.remove('hidden');
        }
    } catch (error) {
        console.error("Error al iniciar sesión:", error);
        loginError.textContent = "Error de conexión con el servidor.";
        loginError.classList.remove('hidden');
    }
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
    
    const range = dateSelect.value;
    try {
        const response = await fetch(`${API_BASE}/metrics/overview?start_date=${range}`, {
            headers: getAuthHeaders()
        });

        if (response.status === 401) {
            // Token expirado o inválido, redirigir a login
            localStorage.removeItem('dashboard_token');
            showLogin();
            return;
        }

        const result = await response.json();
        renderClientList(result.data);
    } catch (error) {
        console.error("Error al cargar overview:", error);
        clientListContainer.innerHTML = '<p style="color: #ff4444; text-align:center;">Error de conexión con el servidor.</p>';
    }
}

function renderClientList(clients) {
    clientListContainer.innerHTML = '';
    
    if(!clients || clients.length === 0) {
        clientListContainer.innerHTML = '<p>No hay datos disponibles.</p>';
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

        if (response.status === 401) {
            localStorage.removeItem('dashboard_token');
            showLogin();
            return;
        }

        const data = await response.json();
        renderDetails(data);
    } catch (error) {
        console.error("Error cargando detalles", error);
        elClientName.textContent = "Error al cargar datos";
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
        
        if (response.status === 401) {
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
        
        if (response.status === 401) {
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
