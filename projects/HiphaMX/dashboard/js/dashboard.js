// Variables globales
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:8000/api/dashboard' 
    : '/api/dashboard';

const AUTH_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api/auth'
    : '/api/auth';

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
