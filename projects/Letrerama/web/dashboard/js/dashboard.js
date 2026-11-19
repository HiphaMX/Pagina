/**
 * LETRERAMA · PANEL DE OPERACIÓN Y TALLER
 * Lógica modular para Directorio de Proyectos y Agenda Semanal de Fabricación
 */

// ==========================================
// ESTADO GLOBAL Y PERSISTENCIA
// ==========================================
const STORAGE_KEY_PROJECTS = 'letrerama_dashboard_projects_v1';
const STORAGE_KEY_TASKS = 'letrerama_dashboard_tasks_v1';

const WORKFLOW_DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
const DAILY_HOURS_LIMIT = 8.0;

let currentTab = 'projects';
let currentWeekOffset = 0;
let currentWfProjectFilter = 'all';

let projectsData = [];
let workflowTasks = [];

// ==========================================
// DATOS DE MUESTRA INICIALES (SEEDED DEMO)
// ==========================================
const INITIAL_DEMO_PROJECTS = [
    {
        id: 1,
        client: 'Burger House 77',
        work_type: 'neon_flex',
        contact_name: 'Carlos Mendoza',
        phone: '33 1450 8892',
        budget: 8200.0,
        deadline: getFutureDateStr(3),
        in_agenda: true,
        est_hours: 6.0,
        status: 'active',
        notes: 'Neón flex rojo y amarillo cálido sobre acrílico transparente 6mm de 1.80 x 0.90m con eliminador 12V 10A.',
        created_at: new Date().toISOString()
    },
    {
        id: 2,
        client: 'Café La Floresta',
        work_type: 'letras_3d',
        contact_name: 'Lucía Aréchiga',
        phone: '33 3676 2545',
        budget: 14500.0,
        deadline: getFutureDateStr(5),
        in_agenda: true,
        est_hours: 12.0,
        status: 'active',
        notes: 'Letras 3D tipo canal de 35cm altura, frente acrílico blanco 3mm, cantos aluminio negro 8cm, luz LED blanca fría 6500K.',
        created_at: new Date().toISOString()
    },
    {
        id: 3,
        client: 'Clínica Dental San Ángel',
        work_type: 'caja_luz',
        contact_name: 'Dra. Patricia Reyes',
        phone: '33 1890 4421',
        budget: 19800.0,
        deadline: getFutureDateStr(8),
        in_agenda: true,
        est_hours: 14.0,
        status: 'prospect',
        notes: 'Gabinete de aluminio 3.0 x 1.2m doble cara con lona translúcida e iluminación perimetral LED alto flujo.',
        created_at: new Date().toISOString()
    },
    {
        id: 4,
        client: 'AutoZone Plaza Norte',
        work_type: 'fachada',
        contact_name: 'Ing. Fernando Soto',
        phone: '33 2200 9911',
        budget: 32000.0,
        deadline: getFutureDateStr(14),
        in_agenda: false,
        est_hours: 20.0,
        status: 'inactive',
        notes: 'Forro de bastidor con panel de Alucobond color naranja corporativo y preparación eléctrica para letras.',
        created_at: new Date().toISOString()
    }
];

const INITIAL_DEMO_TASKS = [
    {
        id: 101,
        week_id: getWeekId(0),
        day: 'monday',
        project_client: 'Burger House 77',
        title: 'Corte CNC de base acrílica y router de trazo',
        hours: 2.5,
        status: 'approved',
        notes: 'Broca 1/8 para acrílico colado 6mm.'
    },
    {
        id: 102,
        week_id: getWeekId(0),
        day: 'tuesday',
        project_client: 'Burger House 77',
        title: 'Montaje de manguera Neón Flex y cableado 12V',
        hours: 3.5,
        status: 'in_production',
        notes: 'Pegamento cianoacrilato y soldadura con termofit.'
    },
    {
        id: 103,
        week_id: getWeekId(0),
        day: 'wednesday',
        project_client: 'Café La Floresta',
        title: 'Rolado de cantos de aluminio para letras 3D',
        hours: 4.0,
        status: 'in_progress',
        notes: 'Dobladora manual para cantos de 8cm.'
    },
    {
        id: 104,
        week_id: getWeekId(0),
        day: 'thursday',
        project_client: 'Café La Floresta',
        title: 'Instalación de módulos LED Samsung en fondos',
        hours: 3.5,
        status: 'budget_approved',
        notes: 'Módulos 3 LEDs IP65 blanco frío.'
    },
    {
        id: 105,
        week_id: getWeekId(0),
        day: 'friday',
        project_client: 'Clínica Dental San Ángel',
        title: 'Levantamiento técnico y cotización para fachada',
        hours: 4.5,
        status: 'quote',
        notes: 'Perfil PTR 1x1 calibre 18 con pintura anticorrosiva.'
    },
    {
        id: 106,
        week_id: getWeekId(0),
        day: 'saturday',
        project_client: 'Burger House 77',
        title: 'Instalación y montaje final en restaurante',
        hours: 3.0,
        status: 'pending',
        notes: 'Llevar taquetes expansivos, nivel láser y cable uso rudo.'
    }
];

// ==========================================
// INICIALIZACIÓN
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    initLetreramaDashboard();
});

function initLetreramaDashboard() {
    initPinSecurity();
    loadStoredData();
    setupEventListeners();
    updateDatesAndWeek();
    renderProjectsDirectory();
    syncProjectDropdowns();
    renderWorkflowBoard();
    loadQuotationsHistory();
    updateQuotationsHistoryBadge();
}

function loadStoredData() {
    try {
        const storedProjects = localStorage.getItem(STORAGE_KEY_PROJECTS);
        if (storedProjects) {
            projectsData = JSON.parse(storedProjects);
            // Normalizar estatus anteriores si existen
            let updated = false;
            projectsData.forEach(p => {
                if (p.status === 'paused') {
                    p.status = 'prospect';
                    updated = true;
                } else if (p.status === 'completed') {
                    p.status = 'active';
                    updated = true;
                }
            });
            if (updated) saveProjects();
        } else {
            projectsData = INITIAL_DEMO_PROJECTS;
            saveProjects();
        }
    } catch (e) {
        projectsData = INITIAL_DEMO_PROJECTS;
    }

    try {
        const storedTasks = localStorage.getItem(STORAGE_KEY_TASKS);
        if (storedTasks) {
            workflowTasks = JSON.parse(storedTasks);
        } else {
            workflowTasks = INITIAL_DEMO_TASKS;
            saveTasks();
        }
    } catch (e) {
        workflowTasks = INITIAL_DEMO_TASKS;
    }
}

function saveProjects() {
    localStorage.setItem(STORAGE_KEY_PROJECTS, JSON.stringify(projectsData));
}

function saveTasks() {
    localStorage.setItem(STORAGE_KEY_TASKS, JSON.stringify(workflowTasks));
}

// ==========================================
// NAVEGACIÓN ENTRE PESTAÑAS
// ==========================================
function switchDashboardTab(tabName) {
    currentTab = tabName;
    const btnProjects = document.getElementById('btnTabProjects');
    const btnWorkflow = document.getElementById('btnTabWorkflow');
    const btnQuotations = document.getElementById('btnTabQuotations');
    const secProjects = document.getElementById('sectionProjects');
    const secWorkflow = document.getElementById('sectionWorkflow');
    const secQuotations = document.getElementById('sectionQuotations');

    btnProjects?.classList.remove('active');
    btnWorkflow?.classList.remove('active');
    btnQuotations?.classList.remove('active');
    secProjects?.classList.remove('active');
    secWorkflow?.classList.remove('active');
    secQuotations?.classList.remove('active');

    if (tabName === 'projects') {
        btnProjects?.classList.add('active');
        secProjects?.classList.add('active');
        renderProjectsDirectory();
    } else if (tabName === 'workflow') {
        btnWorkflow?.classList.add('active');
        secWorkflow?.classList.add('active');
        syncProjectDropdowns();
        renderWorkflowBoard();
    } else if (tabName === 'quotations') {
        btnQuotations?.classList.add('active');
        secQuotations?.classList.add('active');
        initQuotationsModule();
    }
}

// ==========================================
// DIRECTORIO DE PROYECTOS (VISTA 1)
// ==========================================
function renderProjectsDirectory() {
    const container = document.getElementById('projectsTableContainer');
    if (!container) return;

    const searchTerm = (document.getElementById('projectSearchInput')?.value || '').toLowerCase().trim();
    const filterType = document.getElementById('filterWorkType')?.value || 'all';
    const filterStatus = document.getElementById('filterStatus')?.value || 'all';
    const filterAgenda = document.getElementById('filterAgenda')?.value || 'all';

    // Calcular KPIs
    let totalProjects = projectsData.length;
    let activeAgendaCount = 0;
    let totalBudget = 0.0;
    let upcomingDeadlines = 0;

    const now = new Date();

    projectsData.forEach(p => {
        if (p.in_agenda) activeAgendaCount++;
        totalBudget += parseFloat(p.budget) || 0;

        if (p.deadline) {
            const dDate = new Date(p.deadline + 'T23:59:59');
            const diffDays = Math.ceil((dDate - now) / (1000 * 60 * 60 * 24));
            if (diffDays >= 0 && diffDays <= 7) {
                upcomingDeadlines++;
            }
        }
    });

    // Actualizar badges en Header y KPIs
    document.getElementById('badgeProjectsCount').textContent = totalProjects;
    document.getElementById('badgeActiveWorkshopCount').textContent = `${activeAgendaCount} en taller`;
    document.getElementById('kpiTotalProjects').textContent = totalProjects;
    document.getElementById('kpiActiveAgendaCount').textContent = activeAgendaCount;
    document.getElementById('kpiTotalBudget').textContent = formatCurrencyMXN(totalBudget);
    document.getElementById('kpiUpcomingDeadlines').textContent = upcomingDeadlines;

    // Filtrar lista
    const filtered = projectsData.filter(p => {
        if (filterType !== 'all' && p.work_type !== filterType) return false;
        if (filterStatus !== 'all' && (p.status || 'active') !== filterStatus) return false;
        if (filterAgenda === 'in_agenda' && !p.in_agenda) return false;
        if (filterAgenda === 'not_in_agenda' && p.in_agenda) return false;

        if (searchTerm) {
            const matchClient = (p.client || '').toLowerCase().includes(searchTerm);
            const matchContact = (p.contact_name || '').toLowerCase().includes(searchTerm);
            const matchNotes = (p.notes || '').toLowerCase().includes(searchTerm);
            const matchPhone = (p.phone || '').includes(searchTerm);
            if (!matchClient && !matchContact && !matchNotes && !matchPhone) return false;
        }
        return true;
    });

    if (filtered.length === 0) {
        container.innerHTML = `
            <div style="padding: 3.5rem 1.5rem; text-align: center; color: var(--text-muted);">
                <div style="font-size: 2.2rem; margin-bottom: 0.75rem;">📋</div>
                <h3 style="color: var(--text-main); font-size: 1.15rem; margin-bottom: 0.4rem;">No se encontraron proyectos</h3>
                <p style="font-size: 0.85rem; max-width: 440px; margin: 0 auto 1.25rem auto;">
                    ${searchTerm || filterType !== 'all' || filterStatus !== 'all' || filterAgenda !== 'all'
                        ? 'No hay registros que coincidan con los filtros aplicados. Modifica los criterios de búsqueda.'
                        : 'Aún no tienes proyectos registrados en el taller. Comienza dando de alta tu primer trabajo.'}
                </p>
                <button type="button" class="btn-primary" onclick="openProjectModal()" style="margin: 0 auto;">
                    + Nuevo Proyecto
                </button>
            </div>
        `;
        return;
    }

    const rowsHtml = filtered.map(p => {
        const typeBadge = getWorkTypeBadge(p.work_type);
        const deadlineBadge = getDeadlineBadge(p.deadline);
        const inAgenda = Boolean(p.in_agenda);
        const estHours = parseFloat(p.est_hours) || 0;

        // Teléfono / WhatsApp
        let phoneHtml = `<span style="color:var(--text-subtle); font-size:0.75rem;">Sin teléfono</span>`;
        if (p.phone) {
            const clean = p.phone.replace(/\D/g, '');
            const waPhone = clean.startsWith('52') ? clean : (clean.length === 10 ? '52' + clean : clean);
            phoneHtml = `
                <a href="https://wa.me/${waPhone}" target="_blank" rel="noopener noreferrer" class="btn-icon wa" title="Escribir a WhatsApp (${escapeHtml(p.phone)})">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                </a>
            `;
        }

        // Switch interactivo en agenda
        const agendaToggleHtml = `
            <div style="display:flex; flex-direction:column; align-items:center; gap:0.25rem;">
                <label class="switch-agenda-toggle" title="${inAgenda ? 'Activo en Agenda de Taller (Clic para retirar)' : 'Inactivo en Agenda (Clic para activar)'}">
                    <input type="checkbox" ${inAgenda ? 'checked' : ''} onchange="handleToggleProjectAgenda(${p.id}, this.checked, '${escapeHtml(p.client)}')">
                    <span class="slider-agenda-round"></span>
                </label>
                <span class="badge-agenda-cell ${inAgenda ? 'active' : 'inactive'}">
                    ${inAgenda ? 'En Taller' : 'Fuera de Agenda'}
                </span>
                ${estHours > 0 ? `<span style="font-size:0.68rem; color:var(--accent-lime); font-weight:700;" title="Tiempo estimado">${estHours}h est.</span>` : ''}
            </div>
        `;

        let statusClass = 'active';
        let statusLabel = 'Cliente Activo';
        if (p.status === 'prospect' || p.status === 'paused') {
            statusClass = 'prospect';
            statusLabel = 'Prospecto';
        } else if (p.status === 'inactive') {
            statusClass = 'inactive';
            statusLabel = 'Cliente Inactivo';
        } else {
            statusClass = 'active';
            statusLabel = 'Cliente Activo';
        }

        return `
            <tr>
                <td>
                    <div>
                        <strong style="color:var(--text-main); font-size:0.95rem;">${escapeHtml(p.client)}</strong>
                    </div>
                    ${p.contact_name ? `<div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">👤 ${escapeHtml(p.contact_name)}</div>` : ''}
                    ${p.notes ? `<div style="font-size:0.72rem; color:var(--text-subtle); margin-top:3px; max-width:280px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${escapeHtml(p.notes)}">📝 ${escapeHtml(p.notes)}</div>` : ''}
                </td>
                <td>
                    ${typeBadge}
                </td>
                <td>
                    <strong style="color:var(--accent-cyan); font-size:0.95rem;">${formatCurrencyMXN(p.budget || 0)}</strong>
                    <div style="font-size:0.7rem; color:var(--text-subtle); margin-top:2px;">Presupuesto pactado</div>
                </td>
                <td>
                    ${deadlineBadge}
                </td>
                <td style="text-align:center;">
                    ${agendaToggleHtml}
                </td>
                <td>
                    <span class="status-chip ${statusClass}">
                        ${statusLabel}
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        ${phoneHtml}
                        <button type="button" class="btn-icon" onclick="openProjectModal(${p.id})" title="Editar especificaciones">
                            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
                        </button>
                        <button type="button" class="btn-icon del" onclick="handleDeleteProjectRow(${p.id})" title="Eliminar proyecto">
                            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    container.innerHTML = `
        <table class="projects-table">
            <thead>
                <tr>
                    <th>Cliente / Proyecto</th>
                    <th>Tipo de Trabajo</th>
                    <th>Inversión</th>
                    <th>Fecha de Entrega</th>
                    <th style="text-align:center;">🗓️ En Taller (Agenda)</th>
                    <th>Estatus</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                ${rowsHtml}
            </tbody>
        </table>
    `;
}

// Alternar switch de agenda en 1 clic
function handleToggleProjectAgenda(projectId, isChecked, clientName = '') {
    const proj = projectsData.find(p => p.id === projectId);
    if (proj) {
        proj.in_agenda = isChecked;
        saveProjects();
        renderProjectsDirectory();
        syncProjectDropdowns();
        renderWorkflowBoard();

        showToast(`🗓️ <strong>${escapeHtml(clientName || proj.client)}</strong> ${isChecked ? 'activado en la Agenda de Taller' : 'retirado de la Agenda'}`);
    }
}

// ==========================================
// FORMULARIO Y MODAL DE PROYECTO
// ==========================================
function openProjectModal(projectId = null) {
    const modal = document.getElementById('projectModal');
    const heading = document.getElementById('modalProjectHeading');
    const btnDelete = document.getElementById('btnDeleteProject');

    const inputId = document.getElementById('projectInputId');
    const inputClient = document.getElementById('projectInputClient');
    const selectType = document.getElementById('projectInputType');
    const inputContact = document.getElementById('projectInputContact');
    const inputPhone = document.getElementById('projectInputPhone');
    const inputBudget = document.getElementById('projectInputBudget');
    const inputDeadline = document.getElementById('projectInputDeadline');
    const selectStatus = document.getElementById('projectInputStatus');
    const chkInAgenda = document.getElementById('projectInputInAgenda');
    const inputEstHours = document.getElementById('projectInputEstHours');
    const inputNotes = document.getElementById('projectInputNotes');

    if (projectId) {
        const p = projectsData.find(item => item.id === projectId);
        if (p) {
            heading.textContent = `Editar Proyecto: ${p.client}`;
            inputId.value = String(p.id);
            inputClient.value = p.client || '';
            selectType.value = p.work_type || 'letras_3d';
            inputContact.value = p.contact_name || '';
            inputPhone.value = p.phone || '';
            inputBudget.value = p.budget || '';
            inputDeadline.value = p.deadline || '';
            selectStatus.value = p.status || 'active';
            chkInAgenda.checked = Boolean(p.in_agenda);
            inputEstHours.value = p.est_hours != null ? p.est_hours : 6.0;
            inputNotes.value = p.notes || '';

            btnDelete.classList.remove('hidden');
        }
    } else {
        heading.textContent = "+ Alta de Proyecto de Rotulación";
        inputId.value = '';
        inputClient.value = '';
        selectType.value = 'letras_3d';
        inputContact.value = '';
        inputPhone.value = '';
        inputBudget.value = '';
        inputDeadline.value = getFutureDateStr(7);
        selectStatus.value = 'active';
        chkInAgenda.checked = true;
        inputEstHours.value = 6.0;
        inputNotes.value = '';

        btnDelete.classList.add('hidden');
    }

    modal.classList.remove('hidden');
}

function closeProjectModal() {
    const modal = document.getElementById('projectModal');
    if (modal) modal.classList.add('hidden');
}

function handleSaveProject(e) {
    e.preventDefault();
    const id = document.getElementById('projectInputId').value;
    const client = (document.getElementById('projectInputClient').value || '').trim();
    const work_type = document.getElementById('projectInputType').value || 'letras_3d';
    const contact_name = (document.getElementById('projectInputContact').value || '').trim();
    const phone = (document.getElementById('projectInputPhone').value || '').trim();
    const budget = parseFloat(document.getElementById('projectInputBudget').value) || 0.0;
    const deadline = document.getElementById('projectInputDeadline').value || null;
    const status = document.getElementById('projectInputStatus').value || 'active';
    const in_agenda = document.getElementById('projectInputInAgenda').checked;
    const est_hours = parseFloat(document.getElementById('projectInputEstHours').value) || 0.0;
    const notes = (document.getElementById('projectInputNotes').value || '').trim();

    if (!client) {
        alert("Por favor ingresa el nombre del cliente o marca.");
        return;
    }

    const payload = {
        client,
        work_type,
        contact_name: contact_name || null,
        phone: phone || null,
        budget,
        deadline,
        status,
        in_agenda,
        est_hours,
        notes: notes || null
    };

    if (id) {
        const idx = projectsData.findIndex(p => p.id === parseInt(id));
        if (idx !== -1) {
            projectsData[idx] = { ...projectsData[idx], ...payload, updated_at: new Date().toISOString() };
        }
    } else {
        const newProj = {
            id: Date.now(),
            ...payload,
            created_at: new Date().toISOString()
        };
        projectsData.unshift(newProj);
    }

    saveProjects();
    closeProjectModal();
    renderProjectsDirectory();
    syncProjectDropdowns();
    renderWorkflowBoard();

    showToast(`✅ Proyecto <strong>${escapeHtml(client)}</strong> guardado exitosamente.`);
}

function handleDeleteProjectModal() {
    const id = parseInt(document.getElementById('projectInputId').value);
    if (!id) return;

    const proj = projectsData.find(p => p.id === id);
    if (confirm(`¿Estás seguro de eliminar el proyecto "${proj ? proj.client : ''}"?`)) {
        projectsData = projectsData.filter(p => p.id !== id);
        saveProjects();
        closeProjectModal();
        renderProjectsDirectory();
        syncProjectDropdowns();
        renderWorkflowBoard();
        showToast("🗑️ Proyecto eliminado de la base de datos.");
    }
}

function handleDeleteProjectRow(id) {
    const proj = projectsData.find(p => p.id === id);
    if (confirm(`¿Estás seguro de eliminar el proyecto "${proj ? proj.client : ''}"?`)) {
        projectsData = projectsData.filter(p => p.id !== id);
        saveProjects();
        renderProjectsDirectory();
        syncProjectDropdowns();
        renderWorkflowBoard();
        showToast("🗑️ Proyecto eliminado.");
    }
}

// ==========================================
// AGENDA DE TALLER (VISTA 2)
// ==========================================
function getActiveAgendaProjects() {
    const active = [];
    if (Array.isArray(projectsData)) {
        projectsData.forEach(p => {
            if (p.client && p.in_agenda && p.status !== 'inactive') {
                active.push(p.client.trim());
            }
        });
    }
    // Si no hay ninguno, retornar marcas base para que no quede vacío
    if (active.length === 0) {
        return ['Burger House 77', 'Café La Floresta', 'Clínica Dental San Ángel'];
    }
    return Array.from(new Set(active)).sort((a, b) => a.localeCompare(b, 'es', { sensitivity: 'base' }));
}

function syncProjectDropdowns() {
    const activeClients = getActiveAgendaProjects();

    // 1. Selector en modal de nueva tarea
    const taskProjSelect = document.getElementById('taskInputProject');
    if (taskProjSelect) {
        const cur = taskProjSelect.value;
        taskProjSelect.innerHTML = '';
        activeClients.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            if (c === cur) opt.selected = true;
            taskProjSelect.appendChild(opt);
        });
        if (!taskProjSelect.value && activeClients.length > 0) {
            taskProjSelect.value = activeClients[0];
        }
    }

    // 2. Filtro en barra de agenda
    const filterSelect = document.getElementById('wfProjectFilter');
    if (filterSelect) {
        const cur = filterSelect.value || 'all';
        filterSelect.innerHTML = '<option value="all">Todos los proyectos del taller</option>';
        activeClients.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c;
            opt.textContent = c;
            if (c === cur) opt.selected = true;
            filterSelect.appendChild(opt);
        });
    }
}

function updateDatesAndWeek() {
    const now = new Date();
    const target = new Date(now.getTime() + (currentWeekOffset * 7 * 24 * 60 * 60 * 1000));
    
    // Obtener lunes de la semana objetivo
    const dayOfWeek = target.getDay(); // 0 Dom, 1 Lun...
    const diffToMonday = (dayOfWeek === 0 ? -6 : 1) - dayOfWeek;
    const mondayDate = new Date(target);
    mondayDate.setDate(target.getDate() + diffToMonday);

    const weekNumber = getISOWeekNumber(mondayDate);
    const year = mondayDate.getFullYear();
    const weekId = `${year}-W${String(weekNumber).padStart(2, '0')}`;

    const titleEl = document.getElementById('workflowWeekTitle');
    if (titleEl) {
        const endSaturday = new Date(mondayDate);
        endSaturday.setDate(mondayDate.getDate() + 5);
        titleEl.textContent = `Semana ${weekNumber} · ${formatDateShort(mondayDate)} al ${formatDateShort(endSaturday)} (${year})`;
    }

    // Actualizar encabezados de los 6 días
    WORKFLOW_DAYS.forEach((day, idx) => {
        const dayDate = new Date(mondayDate);
        dayDate.setDate(mondayDate.getDate() + idx);
        const dateEl = document.getElementById(`date${capitalize(day)}`);
        if (dateEl) {
            dateEl.textContent = `${dayDate.getDate()} ${getMonthNameShort(dayDate.getMonth())}`;
        }
    });

    return weekId;
}

function getDayAbbr(dayKey) {
    switch (dayKey) {
        case 'monday': return 'Lun';
        case 'tuesday': return 'Mar';
        case 'wednesday': return 'Mié';
        case 'thursday': return 'Jue';
        case 'friday': return 'Vie';
        case 'saturday': return 'Sáb';
        default: return 'Lun';
    }
}

function getDaySpanishName(dayKey) {
    switch (dayKey) {
        case 'monday': return 'Lunes';
        case 'tuesday': return 'Martes';
        case 'wednesday': return 'Miércoles';
        case 'thursday': return 'Jueves';
        case 'friday': return 'Viernes';
        case 'saturday': return 'Sábado';
        default: return 'Día';
    }
}

function renderWorkflowBoard() {
    const currentWeekId = getWeekId(currentWeekOffset);

    // Limpiar columnas y registrar zonas de drop
    WORKFLOW_DAYS.forEach(day => {
        const listEl = document.getElementById(`taskList${capitalize(day)}`);
        if (listEl) {
            listEl.innerHTML = '';
            listEl.ondragover = (e) => handleColumnDragOver(e, day);
            listEl.ondragleave = (e) => handleColumnDragLeave(e, day);
            listEl.ondrop = (e) => handleColumnDrop(e, day);
        }
    });

    let totalWeekHours = 0;
    const dailyHours = { monday: 0, tuesday: 0, wednesday: 0, thursday: 0, friday: 0, saturday: 0 };

    // Filtrar tareas de la semana y proyecto
    const currentTasks = workflowTasks.filter(t => {
        if (t.week_id && t.week_id !== currentWeekId) return false;
        if (currentWfProjectFilter !== 'all' && (t.project_client || '').toLowerCase() !== currentWfProjectFilter.toLowerCase()) return false;
        return true;
    });

    currentTasks.forEach(task => {
        const day = task.day || 'monday';
        const hrs = parseFloat(task.hours) || 1.0;
        dailyHours[day] = (dailyHours[day] || 0) + hrs;
        totalWeekHours += hrs;

        const listEl = document.getElementById(`taskList${capitalize(day)}`);
        if (listEl) {
            listEl.appendChild(createTaskCardElement(task));
        }
    });

    // Actualizar barras de progreso y capacidad diaria
    WORKFLOW_DAYS.forEach(day => {
        const h = dailyHours[day] || 0;
        const capEl = document.getElementById(`colHours${capitalize(day)}`);
        const fillEl = document.getElementById(`fill${capitalize(day)}`);
        if (capEl) capEl.textContent = `${h}h`;
        if (fillEl) {
            const pct = Math.min(Math.round((h / DAILY_HOURS_LIMIT) * 100), 100);
            fillEl.style.width = `${pct}%`;
            if (h > DAILY_HOURS_LIMIT) {
                fillEl.style.backgroundColor = '#ef4444';
            } else {
                fillEl.style.backgroundColor = (day === 'saturday' ? 'var(--accent-lime)' : 'var(--accent-cyan)');
            }
        }
    });

    // Barra total semanal (48h max)
    const capTotalEl = document.getElementById('capTotalWeekHours');
    const capBarEl = document.getElementById('capWeekProgressBar');
    if (capTotalEl) capTotalEl.textContent = `${totalWeekHours.toFixed(1)} hrs`;
    if (capBarEl) {
        const pct = Math.min(Math.round((totalWeekHours / 48.0) * 100), 100);
        capBarEl.style.width = `${pct}%`;
    }
}

function createTaskCardElement(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.id = `taskCard_${task.id}`;
    card.setAttribute('draggable', 'true');
    card.ondragstart = (e) => handleTaskDragStart(e, task.id);
    card.ondragend = handleTaskDragEnd;

    const statusInfo = getTaskStatusInfo(task.status);
    const clientColor = getProjectBrandColor(task.project_client);
    const dayAbbr = getDayAbbr(task.day || 'monday');

    card.innerHTML = `
        <div class="task-card-header">
            <span class="task-client-chip" style="background:${clientColor.bg}; color:${clientColor.text}; border:1px solid ${clientColor.border};">
                ${escapeHtml(task.project_client || 'Proyecto')}
            </span>

            <!-- Control para mover de día al dar clic -->
            <div class="task-day-mover" onclick="event.stopPropagation()">
                <button type="button" class="btn-day-arrow" onclick="shiftTaskDay(${task.id}, -1, event)" title="Mover a día anterior (1 clic)">◀</button>
                <button type="button" class="btn-day-pill" onclick="toggleTaskDayPopover(${task.id}, event)" title="Clic para elegir cualquier día">
                    <span>${dayAbbr}</span>
                    <span class="pill-caret">▾</span>
                </button>
                <button type="button" class="btn-day-arrow" onclick="shiftTaskDay(${task.id}, 1, event)" title="Mover a día siguiente (1 clic)">▶</button>
            </div>

            <span class="task-hours-badge">
                ⏱️ ${task.hours || 1}h
            </span>
        </div>
        <div class="task-card-title">${escapeHtml(task.title)}</div>
        ${task.notes ? `<div class="task-card-notes">📝 ${escapeHtml(task.notes)}</div>` : ''}
        <div class="task-card-footer">
            <span class="status-chip ${statusInfo.key}" onclick="cycleTaskStatus(${task.id})" title="Clic para avanzar a la siguiente fase de taller">
                ${statusInfo.icon} ${statusInfo.label}
            </span>
            <button type="button" class="btn-card-edit" onclick="openTaskModal('${task.day}', ${task.id})" title="Editar tarea">
                <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
            </button>
        </div>
    `;

    return card;
}

// 8 Fases de Operación y Taller
function getTaskStatusInfo(statusKey) {
    switch (statusKey) {
        case 'pending':
            return { key: 'pending', label: 'Por iniciar', next: 'quote', icon: '⏳' };
        case 'quote':
            return { key: 'quote', label: 'Cotización', next: 'budget_approved', icon: '📝' };
        case 'budget_approved':
            return { key: 'budget_approved', label: 'Presupuesto autorizado', next: 'in_progress', icon: '💵' };
        case 'in_progress':
            return { key: 'in_progress', label: 'En proceso / Trazo', next: 'review', icon: '🎨' };
        case 'review':
            return { key: 'review', label: 'Revisión técnica', next: 'approved', icon: '👀' };
        case 'approved':
            return { key: 'approved', label: 'Diseño autorizado', next: 'in_production', icon: '✨' };
        case 'in_production':
            return { key: 'in_production', label: 'En taller / Producción', next: 'completed', icon: '⚙️' };
        case 'completed':
            return { key: 'completed', label: 'Instalado / Entregado', next: 'pending', icon: '🚚' };
        default:
            return { key: 'pending', label: 'Por iniciar', next: 'quote', icon: '⏳' };
    }
}

// Ciclo continuo de fases en 1 clic
function cycleTaskStatus(taskId) {
    const task = workflowTasks.find(t => t.id === taskId);
    if (!task) return;

    const currentInfo = getTaskStatusInfo(task.status);
    task.status = currentInfo.next;
    saveTasks();
    renderWorkflowBoard();

    const newInfo = getTaskStatusInfo(task.status);
    showToast(`⚙️ <strong>${escapeHtml(task.title)}</strong> avanzó a: <strong>${newInfo.icon} ${newInfo.label}</strong>`);
}

// ==========================================
// FORMULARIO Y MODAL DE TAREA
// ==========================================
function openTaskModal(day = 'monday', taskId = null) {
    const modal = document.getElementById('taskModal');
    const heading = document.getElementById('modalTaskHeading');
    const btnDelete = document.getElementById('btnDeleteTask');

    const inputId = document.getElementById('taskInputId');
    const selectProject = document.getElementById('taskInputProject');
    const inputTitle = document.getElementById('taskInputTitle');
    const selectDay = document.getElementById('taskInputDay');
    const inputHours = document.getElementById('taskInputHours');
    const selectStatus = document.getElementById('taskInputStatus');
    const inputNotes = document.getElementById('taskInputNotes');

    syncProjectDropdowns();

    if (taskId) {
        const task = workflowTasks.find(t => t.id === taskId);
        if (task) {
            heading.textContent = "Editar Tarea de Taller";
            inputId.value = String(task.id);
            
            // Si el proyecto no está en el select, agregarlo para no perderlo
            if (task.project_client && !Array.from(selectProject.options).some(o => o.value === task.project_client)) {
                const opt = document.createElement('option');
                opt.value = task.project_client;
                opt.textContent = task.project_client;
                selectProject.appendChild(opt);
            }
            selectProject.value = task.project_client || '';
            inputTitle.value = task.title || '';
            selectDay.value = task.day || day;
            inputHours.value = task.hours || 1.5;
            selectStatus.value = task.status || 'pending';
            inputNotes.value = task.notes || '';

            btnDelete.classList.remove('hidden');
        }
    } else {
        heading.textContent = "+ Programar Tarea en Taller";
        inputId.value = '';
        inputTitle.value = '';
        selectDay.value = day;
        inputHours.value = '1.5';
        selectStatus.value = 'pending';
        inputNotes.value = '';

        btnDelete.classList.add('hidden');
    }

    modal.classList.remove('hidden');
}

function closeTaskModal() {
    const modal = document.getElementById('taskModal');
    if (modal) modal.classList.add('hidden');
}

function handleSaveTask(e) {
    e.preventDefault();
    const id = document.getElementById('taskInputId').value;
    const project_client = document.getElementById('taskInputProject').value;
    const title = (document.getElementById('taskInputTitle').value || '').trim();
    const day = document.getElementById('taskInputDay').value || 'monday';
    const hours = parseFloat(document.getElementById('taskInputHours').value) || 1.5;
    const status = document.getElementById('taskInputStatus').value || 'pending';
    const notes = (document.getElementById('taskInputNotes').value || '').trim();

    if (!title) {
        alert("Por favor ingresa la actividad operativa.");
        return;
    }

    const week_id = getWeekId(currentWeekOffset);

    const payload = {
        week_id,
        project_client,
        title,
        day,
        hours,
        status,
        notes: notes || null
    };

    if (id) {
        const idx = workflowTasks.findIndex(t => t.id === parseInt(id));
        if (idx !== -1) {
            workflowTasks[idx] = { ...workflowTasks[idx], ...payload, updated_at: new Date().toISOString() };
        }
    } else {
        const newTask = {
            id: Date.now(),
            ...payload,
            created_at: new Date().toISOString()
        };
        workflowTasks.push(newTask);
    }

    saveTasks();
    closeTaskModal();
    renderWorkflowBoard();

    showToast(`✅ Actividad <strong>${escapeHtml(title)}</strong> programada para el ${capitalize(day)}.`);
}

function handleDeleteTaskModal() {
    const id = parseInt(document.getElementById('taskInputId').value);
    if (!id) return;

    if (confirm("¿Estás seguro de eliminar esta tarea operativa?")) {
        workflowTasks = workflowTasks.filter(t => t.id !== id);
        saveTasks();
        closeTaskModal();
        renderWorkflowBoard();
        showToast("🗑️ Tarea eliminada de la agenda.");
    }
}

// ==========================================
// REPORTE WHATSAPP DEL TALLER
// ==========================================
function copyWorkshopWhatsAppReport() {
    const currentWeekId = getWeekId(currentWeekOffset);
    const tasks = workflowTasks.filter(t => (t.week_id || currentWeekId) === currentWeekId);

    const titleEl = document.getElementById('workflowWeekTitle');
    const weekTitle = titleEl ? titleEl.textContent : `Semana ${currentWeekId}`;

    let text = `*LETRERAMA · AVANCE DE TALLER & PRODUCCIÓN*\n`;
    text += `📅 _${weekTitle}_\n\n`;

    const dayLabels = {
        monday: 'LUNES',
        tuesday: 'MARTES',
        wednesday: 'MIÉRCOLES',
        thursday: 'JUEVES',
        friday: 'VIERNES',
        saturday: 'SÁBADO (INSTALACIONES)'
    };

    let totalHrs = 0;

    WORKFLOW_DAYS.forEach(day => {
        const dayTasks = tasks.filter(t => t.day === day);
        if (dayTasks.length > 0) {
            text += `*▶ ${dayLabels[day]}*\n`;
            dayTasks.forEach(t => {
                const s = getTaskStatusInfo(t.status);
                totalHrs += parseFloat(t.hours) || 0;
                text += `• ${s.icon} *[${t.project_client}]* ${t.title} (${t.hours}h) - _${s.label}_\n`;
                if (t.notes) text += `   ↳ _Nota: ${t.notes}_\n`;
            });
            text += `\n`;
        }
    });

    text += `📊 *Total horas programadas:* ${totalHrs.toFixed(1)} hrs\n`;
    text += `⚡ _Reporte generado automáticamente desde el Panel Letrerama_`;

    navigator.clipboard.writeText(text).then(() => {
        showToast("📲 ¡Reporte de WhatsApp copiado al portapapeles!");
    }).catch(() => {
        alert("Reporte generado:\n\n" + text);
    });
}

// ==========================================
// HELPERS Y EVENT LISTENERS
// ==========================================
function setupEventListeners() {
    // Búsqueda y filtros de proyectos
    document.getElementById('projectSearchInput')?.addEventListener('input', renderProjectsDirectory);
    document.getElementById('filterWorkType')?.addEventListener('change', renderProjectsDirectory);
    document.getElementById('filterStatus')?.addEventListener('change', renderProjectsDirectory);
    document.getElementById('filterAgenda')?.addEventListener('change', renderProjectsDirectory);

    // Formularios
    document.getElementById('projectForm')?.addEventListener('submit', handleSaveProject);
    document.getElementById('taskForm')?.addEventListener('submit', handleSaveTask);

    // Navegación semanal
    document.getElementById('btnPrevWeek')?.addEventListener('click', () => {
        currentWeekOffset--;
        updateDatesAndWeek();
        renderWorkflowBoard();
    });

    document.getElementById('btnNextWeek')?.addEventListener('click', () => {
        currentWeekOffset++;
        updateDatesAndWeek();
        renderWorkflowBoard();
    });

    document.getElementById('btnCurrentWeek')?.addEventListener('click', () => {
        currentWeekOffset = 0;
        updateDatesAndWeek();
        renderWorkflowBoard();
    });

    document.getElementById('wfProjectFilter')?.addEventListener('change', (e) => {
        currentWfProjectFilter = e.target.value;
        renderWorkflowBoard();
    });
}

function getWorkTypeBadge(type) {
    switch (type) {
        case 'letras_3d':
            return `<span class="work-type-badge letras_3d">🔤 Letras 3D</span>`;
        case 'neon_flex':
            return `<span class="work-type-badge neon_flex">💡 Neón Flex</span>`;
        case 'caja_luz':
            return `<span class="work-type-badge caja_luz">📦 Caja de Luz</span>`;
        case 'fachada':
            return `<span class="work-type-badge fachada">🏢 Fachada Alucobond</span>`;
        case 'rotulacion':
            return `<span class="work-type-badge rotulacion">🚗 Rotulación</span>`;
        case 'gran_formato':
            return `<span class="work-type-badge gran_formato">📐 Gran Formato</span>`;
        case 'senaletica':
            return `<span class="work-type-badge senaletica">🛑 Señalética</span>`;
        default:
            return `<span class="work-type-badge letras_3d">⚡ Letrero</span>`;
    }
}

function getDeadlineBadge(deadlineStr) {
    if (!deadlineStr) return `<span style="color:var(--text-subtle); font-size:0.75rem;">Sin fecha fija</span>`;
    
    const now = new Date();
    const dDate = new Date(deadlineStr + 'T23:59:59');
    const diffDays = Math.ceil((dDate - now) / (1000 * 60 * 60 * 24));

    let tagClass = 'normal';
    let label = `${diffDays} días`;
    if (diffDays < 0) {
        tagClass = 'urgent';
        label = `⚠️ Venció hace ${Math.abs(diffDays)}d`;
    } else if (diffDays <= 3) {
        tagClass = 'urgent';
        label = `🚨 Entrega en ${diffDays}d`;
    } else if (diffDays <= 7) {
        tagClass = 'warning';
        label = `⏳ ${diffDays} días restantes`;
    }

    return `
        <div class="deadline-badge">
            <span class="deadline-tag ${tagClass}">${label}</span>
            <span class="deadline-date-sub">${formatDateShort(dDate)}</span>
        </div>
    `;
}

function getProjectBrandColor(clientName) {
    if (!clientName) return { bg: 'rgba(51, 241, 255, 0.12)', text: '#33f1ff', border: 'rgba(51, 241, 255, 0.3)' };

    const palettes = [
        { bg: 'rgba(51, 241, 255, 0.14)', text: '#33f1ff', border: 'rgba(51, 241, 255, 0.35)' }, // Cian Letrerama
        { bg: 'rgba(145, 252, 6, 0.14)', text: '#91fc06', border: 'rgba(145, 252, 6, 0.35)' },   // Lima Letrerama
        { bg: 'rgba(192, 132, 252, 0.14)', text: '#c084fc', border: 'rgba(192, 132, 252, 0.35)' }, // Púrpura
        { bg: 'rgba(251, 191, 36, 0.14)', text: '#fbbf24', border: 'rgba(251, 191, 36, 0.35)' },   // Ámbar
        { bg: 'rgba(244, 114, 182, 0.14)', text: '#f472b6', border: 'rgba(244, 114, 182, 0.35)' }, // Rosa Neón
        { bg: 'rgba(56, 189, 248, 0.14)', text: '#38bdf8', border: 'rgba(56, 189, 248, 0.35)' }    // Azul
    ];

    let hash = 0;
    for (let i = 0; i < clientName.length; i++) {
        hash = clientName.charCodeAt(i) + ((hash << 5) - hash);
    }
    const idx = Math.abs(hash) % palettes.length;
    return palettes[idx];
}

function showToast(message, type = 'success') {
    let container = document.getElementById('letreramaToastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'letreramaToastContainer';
        container.style.cssText = 'position:fixed; bottom:24px; right:24px; z-index:99999; display:flex; flex-direction:column; gap:8px; pointer-events:none;';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    const isError = (type === 'error');
    toast.style.cssText = `
        background: ${isError ? 'rgba(239, 68, 68, 0.95)' : 'rgba(15, 22, 36, 0.95)'};
        color: #fff;
        border: 1px solid ${isError ? '#f87171' : 'rgba(51, 241, 255, 0.5)'};
        padding: 0.65rem 1.15rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transform: translateY(10px);
        opacity: 0;
        transition: all 0.25s ease;
        pointer-events: auto;
    `;
    toast.innerHTML = message;
    container.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
    });

    setTimeout(() => {
        toast.style.transform = 'translateY(10px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 250);
    }, 3200);
}

// Utilidades
function formatCurrencyMXN(val) {
    return `$${Number(val || 0).toLocaleString('es-MX', { minimumFractionDigits: 0, maximumFractionDigits: 2 })} MXN`;
}

function formatDateShort(d) {
    if (!d) return '';
    const date = new Date(d);
    return `${date.getDate()} ${getMonthNameShort(date.getMonth())} ${date.getFullYear()}`;
}

function getFutureDateStr(days) {
    const d = new Date();
    d.setDate(d.getDate() + days);
    return d.toISOString().split('T')[0];
}

function getMonthNameShort(monthIdx) {
    const months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
    return months[monthIdx] || '';
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function getISOWeekNumber(d) {
    const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
    const dayNum = date.getUTCDay() || 7;
    date.setUTCDate(date.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1));
    return Math.ceil((((date - yearStart) / 86400000) + 1) / 7);
}

function getWeekId(offset = 0) {
    const now = new Date();
    const target = new Date(now.getTime() + (offset * 7 * 24 * 60 * 60 * 1000));
    const dayOfWeek = target.getDay();
    const diffToMonday = (dayOfWeek === 0 ? -6 : 1) - dayOfWeek;
    const monday = new Date(target);
    monday.setDate(target.getDate() + diffToMonday);
    const weekNum = getISOWeekNumber(monday);
    return `${monday.getFullYear()}-W${String(weekNum).padStart(2, '0')}`;
}

// ==========================================
// SEGURIDAD POR PIN (TALLER PRIVADO)
// ==========================================
const TALLER_PIN = '1709';
const PIN_SESSION_KEY = 'letrerama_taller_unlocked';

function initPinSecurity() {
    const isUnlocked = sessionStorage.getItem(PIN_SESSION_KEY) === 'true';
    const overlay = document.getElementById('pinLockOverlay');
    if (!overlay) return;

    if (isUnlocked) {
        overlay.classList.add('unlocked');
    } else {
        overlay.classList.remove('unlocked');
        setupPinInputs();
    }
}

function setupPinInputs() {
    const digits = [
        document.getElementById('pinDigit1'),
        document.getElementById('pinDigit2'),
        document.getElementById('pinDigit3'),
        document.getElementById('pinDigit4')
    ];

    if (!digits[0]) return;

    // Focus inicial en el primer campo
    setTimeout(() => {
        digits[0].focus();
    }, 150);

    digits.forEach((input, idx) => {
        // Al escribir dígito
        input.addEventListener('input', (e) => {
            const val = e.target.value.replace(/\D/g, '');
            e.target.value = val ? val[0] : '';

            hidePinError();

            if (val && idx < 3) {
                digits[idx + 1].focus();
            } else if (idx === 3 && val) {
                // Al ingresar el 4to dígito, validar automáticamente
                checkAndUnlockPin();
            }
        });

        // Manejo de Backspace y flechas
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && !input.value && idx > 0) {
                digits[idx - 1].focus();
                digits[idx - 1].value = '';
            } else if (e.key === 'ArrowLeft' && idx > 0) {
                digits[idx - 1].focus();
            } else if (e.key === 'ArrowRight' && idx < 3) {
                digits[idx + 1].focus();
            }
        });

        // Pegar (Paste) PIN de 4 dígitos
        input.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
            if (text.length >= 4) {
                for (let i = 0; i < 4; i++) {
                    if (digits[i]) digits[i].value = text[i];
                }
                digits[3].focus();
                checkAndUnlockPin();
            } else if (text.length > 0) {
                input.value = text[0];
                if (idx < 3) digits[idx + 1].focus();
            }
        });
    });
}

function handlePinSubmit(e) {
    if (e) e.preventDefault();
    checkAndUnlockPin();
}

function checkAndUnlockPin() {
    const d1 = document.getElementById('pinDigit1')?.value || '';
    const d2 = document.getElementById('pinDigit2')?.value || '';
    const d3 = document.getElementById('pinDigit3')?.value || '';
    const d4 = document.getElementById('pinDigit4')?.value || '';
    const entered = `${d1}${d2}${d3}${d4}`;

    const overlay = document.getElementById('pinLockOverlay');
    const card = overlay?.querySelector('.pin-lock-card');
    const errorMsg = document.getElementById('pinErrorMessage');
    const digits = [
        document.getElementById('pinDigit1'),
        document.getElementById('pinDigit2'),
        document.getElementById('pinDigit3'),
        document.getElementById('pinDigit4')
    ];

    if (entered === TALLER_PIN) {
        sessionStorage.setItem(PIN_SESSION_KEY, 'true');
        hidePinError();
        
        // Animación visual de éxito
        if (card) {
            card.style.borderColor = 'var(--accent-lime)';
            card.style.boxShadow = '0 0 40px rgba(145, 252, 6, 0.4)';
        }

        setTimeout(() => {
            overlay?.classList.add('unlocked');
            showToast("🔓 Acceso concedido al Taller Letrerama.");
        }, 180);
    } else {
        // Efecto de error y shake
        if (card) {
            card.classList.remove('pin-card-shake');
            void card.offsetWidth; // trigger reflow
            card.classList.add('pin-card-shake');
        }

        digits.forEach(d => {
            if (d) {
                d.classList.add('error');
                d.value = '';
            }
        });

        if (errorMsg) errorMsg.classList.remove('hidden');

        setTimeout(() => {
            digits[0]?.focus();
        }, 250);
    }
}

function hidePinError() {
    const errorMsg = document.getElementById('pinErrorMessage');
    if (errorMsg) errorMsg.classList.add('hidden');
    const digits = document.querySelectorAll('.pin-digit');
    digits.forEach(d => d.classList.remove('error'));
}

function lockTallerSession() {
    sessionStorage.removeItem(PIN_SESSION_KEY);
    const overlay = document.getElementById('pinLockOverlay');
    if (overlay) {
        overlay.classList.remove('unlocked');
        hidePinError();
        const digits = [
            document.getElementById('pinDigit1'),
            document.getElementById('pinDigit2'),
            document.getElementById('pinDigit3'),
            document.getElementById('pinDigit4')
        ];
        digits.forEach(d => {
            if (d) d.value = '';
        });
        setTimeout(() => {
            digits[0]?.focus();
        }, 200);
        showToast("🔒 Sesión bloqueada por seguridad.");
    }
}

// ==========================================================================
// LÓGICA DE MOVIMIENTO DE FICHAS DE TRABAJO (1 CLIC & DRAG AND DROP)
// ==========================================================================

let activePopoverTaskId = null;
let draggedTaskId = null;

function shiftTaskDay(taskId, delta, event) {
    if (event) event.stopPropagation();
    closeDayPickerPopover();

    const task = workflowTasks.find(t => t.id === taskId);
    if (!task) return;

    const curDay = task.day || 'monday';
    const curIdx = WORKFLOW_DAYS.indexOf(curDay);
    if (curIdx === -1) return;

    let newIdx = curIdx + delta;
    if (newIdx < 0) newIdx = WORKFLOW_DAYS.length - 1;
    if (newIdx >= WORKFLOW_DAYS.length) newIdx = 0;

    const newDay = WORKFLOW_DAYS[newIdx];
    task.day = newDay;

    saveTasks();
    renderWorkflowBoard();
    showToast(`➡️ Ficha movida a <strong>${getDaySpanishName(newDay)}</strong>`);
}

function moveTaskToDay(taskId, targetDay) {
    const task = workflowTasks.find(t => t.id === taskId);
    if (!task) return;

    task.day = targetDay;
    saveTasks();
    renderWorkflowBoard();
    showToast(`📅 Ficha asignada a <strong>${getDaySpanishName(targetDay)}</strong>`);
}

function toggleTaskDayPopover(taskId, event) {
    if (event) event.stopPropagation();
    const popover = document.getElementById('taskDayPickerPopover');
    if (!popover) return;

    if (activePopoverTaskId === taskId && !popover.classList.contains('hidden')) {
        closeDayPickerPopover();
        return;
    }

    activePopoverTaskId = taskId;
    const task = workflowTasks.find(t => t.id === taskId);
    const targetEl = event.currentTarget;
    const rect = targetEl.getBoundingClientRect();

    popover.style.top = `${rect.bottom + window.scrollY + 6}px`;
    popover.style.left = `${Math.max(10, rect.left + window.scrollX - 40)}px`;
    popover.classList.remove('hidden');

    // Resaltar día actual en el popover
    popover.querySelectorAll('.btn-popover-day').forEach(btn => {
        if (task && btn.getAttribute('data-day') === task.day) {
            btn.style.borderColor = 'var(--accent-cyan)';
            btn.style.background = 'rgba(51, 241, 255, 0.2)';
        } else {
            btn.style.borderColor = 'var(--border-subtle)';
            btn.style.background = 'rgba(255, 255, 255, 0.04)';
        }
    });
}

function selectDayFromPopover(targetDay) {
    if (activePopoverTaskId) {
        moveTaskToDay(activePopoverTaskId, targetDay);
    }
    closeDayPickerPopover();
}

function closeDayPickerPopover() {
    const popover = document.getElementById('taskDayPickerPopover');
    if (popover) popover.classList.add('hidden');
    activePopoverTaskId = null;
}

// Drag & Drop nativo entre columnas de días
function handleTaskDragStart(e, taskId) {
    draggedTaskId = taskId;
    e.dataTransfer.setData('text/plain', String(taskId));
    e.dataTransfer.effectAllowed = 'move';
    const card = e.currentTarget;
    setTimeout(() => {
        card.classList.add('dragging');
    }, 10);
}

function handleTaskDragEnd(e) {
    e.currentTarget.classList.remove('dragging');
    document.querySelectorAll('.task-list').forEach(l => l.classList.remove('drag-over'));
    draggedTaskId = null;
}

function handleColumnDragOver(e, day) {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    e.currentTarget.classList.add('drag-over');
}

function handleColumnDragLeave(e, day) {
    e.currentTarget.classList.remove('drag-over');
}

function handleColumnDrop(e, day) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    const taskIdStr = e.dataTransfer.getData('text/plain') || draggedTaskId;
    const taskId = parseInt(taskIdStr);
    if (taskId && day) {
        moveTaskToDay(taskId, day);
    }
}

// Cerrar selector flotante al hacer clic fuera
document.addEventListener('click', (e) => {
    if (!e.target.closest('#taskDayPickerPopover') && !e.target.closest('.btn-day-pill')) {
        closeDayPickerPopover();
    }
});

// ==========================================================================
// MÓDULO COTIZADOR DE TALLER & PROPUESTAS LETRERAMA
// ==========================================================================

const STORAGE_KEY_QUOTATIONS = 'letrerama_quotations_history';
const STORAGE_KEY_QUOTE_DRAFT = 'letrerama_quotation_draft';

const LETRERAMA_CATALOG = [
    { id: 'letras-3d', name: 'Letras Corpóreas 3D', category: 'Volumétricos', description: 'Aluminio rolado con cantos soldados y cara de acrílico traslúcido 3mm con iluminación LED interna.', price: 3500.0, unit_label: 'x pz' },
    { id: 'caja-luz', name: 'Caja de Luz LED', category: 'Iluminados', description: 'Gabinete de aluminio extruido con lona traslúcida o acrílico e iluminación LED 6500K de alto brillo.', price: 4800.0, unit_label: 'x m²' },
    { id: 'acrilico-backlit', name: 'Acrílico Retroiluminado Neón', category: 'Backlit', description: 'Placa de acrílico cristal pulido con halo perimetral LED Neón Flex y separadores de acero.', price: 4200.0, unit_label: 'x pz' },
    { id: 'bastidor-fachada', name: 'Bastidor 3D y Fachada', category: 'Estructuras', description: 'Estructura en PTR y panel de aluminio acanalado/alucobond para recubrimiento comercial.', price: 6500.0, unit_label: 'x módulo' },
    { id: 'banderola', name: 'Banderola Comercial Doble Cara', category: 'Banderolas', description: 'Letrero proyectado 2 vistas con iluminación interior LED y anclajes estructurales a muro.', price: 3800.0, unit_label: 'x pz' },
    { id: 'impresion-3d', name: 'Impresión 3D & Aluminio', category: 'Híbridos', description: 'Modelado aditivo volumétrico con acabados automotrices de alta resistencia a intemperie.', price: 3200.0, unit_label: 'x pz' },
    { id: 'trofeos', name: 'Trofeos Multimaterial', category: 'Especiales', description: 'Combinación de madera fina, mármol, acrílico y placa metálica grabada con corte láser.', price: 950.0, unit_label: 'x pz' },
    { id: 'dtf-textil', name: 'DTF Textil & Vinil', category: 'Textil', description: 'Estampado digital térmico de alta durabilidad en uniformes, playeras o mandiles de taller.', price: 450.0, unit_label: 'x pz' },
    { id: 'instalacion-altura', name: 'Montaje & Instalación en Altura', category: 'Servicio', description: 'Maniobra con andamios de 2 cuerpos o canastilla, anclajes estructurales y cableado.', price: 1800.0, unit_label: 'x jornada' },
    { id: 'mantenimiento', name: 'Mantenimiento & Cambio LED', category: 'Servicio', description: 'Revisión y sustitución de fuentes de poder 12V, módulos LED IP67 y sellado perimetral.', price: 1200.0, unit_label: 'x servicio' }
];

let currentQuotationItems = [];
let quotationsHistory = [];
let quotationsModuleInitialized = false;

function initQuotationsModule() {
    loadQuotationsHistory();
    syncQuotationsClientDropdown();
    renderQuotationCatalog();

    if (!quotationsModuleInitialized) {
        restoreQuoteDraft();
        quotationsModuleInitialized = true;
    } else {
        renderQuoteItemsList();
        recalculateQuoteTotals();
    }

    updateQuotationsHistoryBadge();
}

function loadQuotationsHistory() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY_QUOTATIONS);
        if (stored) {
            quotationsHistory = JSON.parse(stored);
        } else {
            quotationsHistory = [
                {
                    id: 17090001,
                    folio: 'LET-2026-0001',
                    date: '2026-11-18',
                    client_name: 'Burger House 77',
                    client_contact: 'Lic. Javier Vega',
                    client_phone: '33 9876 5432',
                    client_email: 'javier@burgerhouse77.com',
                    validity_days: 30,
                    apply_tax: true,
                    require_down_payment: true,
                    notes: 'Letrero 3D en fachada principal con iluminación cálida 3000K. Entrega en 8 días hábiles.',
                    items: [
                        { id: 1, name: 'Letras Corpóreas 3D', description: 'Logo hamburguesa y tipografía en aluminio rolado negro mate con acrílico frontal.', quantity: 1, unit_price: 12500.0 },
                        { id: 2, name: 'Montaje & Instalación en Altura', description: 'Instalación sobre marquesina a 4.5m con anclajes químicos.', quantity: 1, unit_price: 2000.0 }
                    ],
                    subtotal: 14500.0,
                    tax: 2320.0,
                    total: 16820.0,
                    down_payment: 8410.0,
                    status: 'Aprobada'
                }
            ];
            saveQuotationsHistory();
        }
    } catch (e) {
        quotationsHistory = [];
    }
}

function saveQuotationsHistory() {
    localStorage.setItem(STORAGE_KEY_QUOTATIONS, JSON.stringify(quotationsHistory));
    updateQuotationsHistoryBadge();
}

function updateQuotationsHistoryBadge() {
    const badge = document.getElementById('quotationsHistoryBadge');
    if (badge) badge.textContent = quotationsHistory.length;
    const mainBadge = document.getElementById('badgeQuotationsCount');
    if (mainBadge) mainBadge.textContent = quotationsHistory.length;
}

function syncQuotationsClientDropdown() {
    const select = document.getElementById('quoteClientSelect');
    if (!select) return;

    const cur = select.value;
    select.innerHTML = '<option value="">-- O escribir cliente / prospecto nuevo --</option>';

    if (Array.isArray(projectsData)) {
        projectsData.forEach(p => {
            if (p.client) {
                const opt = document.createElement('option');
                opt.value = p.client;
                opt.textContent = `${p.client} (${p.status === 'active' ? 'Cliente Activo' : 'Prospecto'})`;
                if (p.client === cur) opt.selected = true;
                select.appendChild(opt);
            }
        });
    }
}

function handleSelectClientForQuote(clientName) {
    if (!clientName) return;
    const proj = projectsData.find(p => p.client === clientName);
    if (!proj) return;

    const inputName = document.getElementById('quoteClientName');
    const inputContact = document.getElementById('quoteClientContact');
    const inputPhone = document.getElementById('quoteClientPhone');
    const inputNotes = document.getElementById('quoteNotes');

    if (inputName) inputName.value = proj.client;
    if (inputContact && proj.contact_name) inputContact.value = proj.contact_name;
    if (inputPhone && proj.phone) inputPhone.value = proj.phone;
    if (inputNotes && proj.notes) inputNotes.value = proj.notes;

    // Si tiene tipo de trabajo y no hay items, sugerir el primer item
    if (currentQuotationItems.length === 0) {
        const matchingCatalog = LETRERAMA_CATALOG.find(c => c.name.toLowerCase().includes(proj.work_type) || proj.work_type.includes(c.id));
        if (matchingCatalog) {
            addCatalogItemToQuote(matchingCatalog.id);
        }
    }

    recalculateQuoteTotals();
}

function renderQuotationCatalog() {
    const container = document.getElementById('catalogQuickChips');
    if (!container) return;

    container.innerHTML = '';
    LETRERAMA_CATALOG.forEach(item => {
        const chip = document.createElement('button');
        chip.type = 'button';
        chip.className = 'catalog-chip';
        chip.innerHTML = `
            <span>${item.name}</span>
            <span class="chip-price">$${item.price.toLocaleString('es-MX')}</span>
        `;
        chip.onclick = () => addCatalogItemToQuote(item.id);
        container.appendChild(chip);
    });
}

function addCatalogItemToQuote(catalogId) {
    const itemDef = LETRERAMA_CATALOG.find(c => c.id === catalogId);
    if (!itemDef) return;

    const newItem = {
        id: Date.now() + Math.floor(Math.random() * 1000),
        name: itemDef.name,
        description: itemDef.description,
        quantity: 1,
        unit_price: itemDef.price,
        is_custom: false
    };

    currentQuotationItems.push(newItem);
    renderQuoteItemsList();
    recalculateQuoteTotals();
    showToast(`✨ Añadido <strong>${escapeHtml(itemDef.name)}</strong> al presupuesto.`);
}

function addCustomQuoteItem() {
    const newItem = {
        id: Date.now() + Math.floor(Math.random() * 1000),
        name: 'Letrero / Concepto Personalizado',
        description: 'Especificaciones técnicas de aluminio, acrílico, calibre y sistema de iluminación.',
        quantity: 1,
        unit_price: 2500.0,
        is_custom: true
    };

    currentQuotationItems.push(newItem);
    renderQuoteItemsList();
    recalculateQuoteTotals();
    showToast("✨ Concepto personalizado agregado.");
}

function removeQuoteItem(itemId) {
    currentQuotationItems = currentQuotationItems.filter(it => it.id !== itemId);
    renderQuoteItemsList();
    recalculateQuoteTotals();
}

function renderQuoteItemsList() {
    const container = document.getElementById('quoteItemsListContainer');
    const emptyState = document.getElementById('quoteItemsEmptyState');
    const countBadge = document.getElementById('quoteItemsCount');

    if (countBadge) countBadge.textContent = currentQuotationItems.length;

    if (!container) return;
    container.innerHTML = '';

    if (currentQuotationItems.length === 0) {
        if (emptyState) emptyState.style.display = 'block';
        return;
    } else {
        if (emptyState) emptyState.style.display = 'none';
    }

    currentQuotationItems.forEach(it => {
        const card = document.createElement('div');
        card.className = 'quote-item-card';

        const subtotal = (it.quantity * it.unit_price) || 0;

        card.innerHTML = `
            <div class="quote-item-info">
                <input type="text" class="quote-item-name" value="${escapeHtml(it.name)}" placeholder="Nombre del concepto">
                <textarea class="quote-item-desc" rows="2" placeholder="Materiales, especificaciones y dimensiones">${escapeHtml(it.description || '')}</textarea>
            </div>
            <div class="quote-item-field-wrap">
                <span class="quote-item-field-label">Cantidad</span>
                <input type="number" class="quote-item-qty" value="${it.quantity}" min="0.5" step="0.5">
            </div>
            <div class="quote-item-field-wrap">
                <span class="quote-item-field-label">P. Unitario</span>
                <input type="number" class="quote-item-unit" value="${it.unit_price}" min="0" step="any">
            </div>
            <div class="quote-item-field-wrap" style="align-items:flex-end;">
                <span class="quote-item-field-label">Subtotal</span>
                <span class="quote-item-subtotal-disp">$${subtotal.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
            </div>
            <button type="button" class="btn-delete-quote-item" title="Eliminar concepto">&times;</button>
        `;

        // Eventos reactivos
        const inputName = card.querySelector('.quote-item-name');
        const inputDesc = card.querySelector('.quote-item-desc');
        const inputQty = card.querySelector('.quote-item-qty');
        const inputUnit = card.querySelector('.quote-item-unit');
        const btnDel = card.querySelector('.btn-delete-quote-item');

        if (inputName) inputName.oninput = (e) => { it.name = e.target.value; saveQuoteDraft(); };
        if (inputDesc) inputDesc.oninput = (e) => { it.description = e.target.value; saveQuoteDraft(); };
        if (inputQty) inputQty.oninput = (e) => {
            it.quantity = parseFloat(e.target.value) || 0;
            const newSub = it.quantity * it.unit_price;
            const disp = card.querySelector('.quote-item-subtotal-disp');
            if (disp) disp.textContent = `$${newSub.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            recalculateQuoteTotals();
        };
        if (inputUnit) inputUnit.oninput = (e) => {
            it.unit_price = parseFloat(e.target.value) || 0;
            const newSub = it.quantity * it.unit_price;
            const disp = card.querySelector('.quote-item-subtotal-disp');
            if (disp) disp.textContent = `$${newSub.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            recalculateQuoteTotals();
        };
        if (btnDel) btnDel.onclick = () => removeQuoteItem(it.id);

        container.appendChild(card);
    });
}

function recalculateQuoteTotals() {
    let subtotal = 0;
    currentQuotationItems.forEach(it => {
        subtotal += (it.quantity * it.unit_price);
    });

    const chkTax = document.getElementById('quoteApplyTax');
    const applyTax = chkTax ? chkTax.checked : true;
    const tax = applyTax ? (subtotal * 0.16) : 0.0;
    const total = subtotal + tax;

    const chkDown = document.getElementById('quoteRequireDownPayment');
    const requireDown = chkDown ? chkDown.checked : true;
    const downPayment = requireDown ? (total * 0.50) : 0.0;

    const elSub = document.getElementById('quoteSummarySubtotal');
    const rowTax = document.getElementById('quoteSummaryTaxRow');
    const elTax = document.getElementById('quoteSummaryTax');
    const elTot = document.getElementById('quoteSummaryTotal');
    const rowDown = document.getElementById('quoteSummaryDownPaymentRow');
    const elDown = document.getElementById('quoteSummaryDownPayment');
    const badgeDown = document.getElementById('quoteDownPaymentBadge');

    if (elSub) elSub.textContent = `$${subtotal.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;

    if (rowTax) {
        rowTax.style.display = applyTax ? 'flex' : 'none';
        if (elTax) elTax.textContent = applyTax ? `$${tax.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN` : '';
    }

    if (elTot) elTot.textContent = `$${total.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;

    if (rowDown) {
        rowDown.style.display = requireDown ? 'flex' : 'none';
        if (elDown) elDown.textContent = `$${downPayment.toLocaleString('es-MX', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} MXN`;
    }

    if (badgeDown) {
        badgeDown.textContent = requireDown ? '50% fabricación' : 'Sin anticipo';
    }

    saveQuoteDraft();
}

function getNextQuotationFolio() {
    const year = new Date().getFullYear();
    const count = quotationsHistory.length + 1;
    return `LET-${year}-${String(count).padStart(4, '0')}`;
}

function saveQuoteDraft() {
    try {
        const draft = {
            clientName: document.getElementById('quoteClientName')?.value || '',
            clientContact: document.getElementById('quoteClientContact')?.value || '',
            clientEmail: document.getElementById('quoteClientEmail')?.value || '',
            clientPhone: document.getElementById('quoteClientPhone')?.value || '',
            folio: document.getElementById('quoteFolio')?.value || '',
            validityDays: document.getElementById('quoteValidityDays')?.value || '30',
            applyTax: document.getElementById('quoteApplyTax')?.checked ?? true,
            requireDownPayment: document.getElementById('quoteRequireDownPayment')?.checked ?? true,
            notes: document.getElementById('quoteNotes')?.value || '',
            items: currentQuotationItems
        };
        localStorage.setItem(STORAGE_KEY_QUOTE_DRAFT, JSON.stringify(draft));
    } catch (e) {}
}

function restoreQuoteDraft() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY_QUOTE_DRAFT);
        if (stored) {
            const draft = JSON.parse(stored);
            if (document.getElementById('quoteClientName')) document.getElementById('quoteClientName').value = draft.clientName || '';
            if (document.getElementById('quoteClientContact')) document.getElementById('quoteClientContact').value = draft.clientContact || '';
            if (document.getElementById('quoteClientEmail')) document.getElementById('quoteClientEmail').value = draft.clientEmail || '';
            if (document.getElementById('quoteClientPhone')) document.getElementById('quoteClientPhone').value = draft.clientPhone || '';
            if (document.getElementById('quoteFolio')) document.getElementById('quoteFolio').value = draft.folio || getNextQuotationFolio();
            if (document.getElementById('quoteValidityDays')) document.getElementById('quoteValidityDays').value = draft.validityDays || '30';
            if (document.getElementById('quoteApplyTax')) document.getElementById('quoteApplyTax').checked = draft.applyTax ?? true;
            if (document.getElementById('quoteRequireDownPayment')) document.getElementById('quoteRequireDownPayment').checked = draft.requireDownPayment ?? true;
            if (document.getElementById('quoteNotes')) document.getElementById('quoteNotes').value = draft.notes || '';
            currentQuotationItems = draft.items || [];
        } else {
            if (document.getElementById('quoteFolio')) document.getElementById('quoteFolio').value = getNextQuotationFolio();
        }
    } catch (e) {
        if (document.getElementById('quoteFolio')) document.getElementById('quoteFolio').value = getNextQuotationFolio();
    }

    renderQuoteItemsList();
    recalculateQuoteTotals();
}

function clearQuotationForm(confirmFirst = true) {
    if (confirmFirst && !confirm("¿Deseas limpiar todos los campos y conceptos del cotizador?")) {
        return;
    }

    if (document.getElementById('quoteClientSelect')) document.getElementById('quoteClientSelect').value = '';
    if (document.getElementById('quoteClientName')) document.getElementById('quoteClientName').value = '';
    if (document.getElementById('quoteClientContact')) document.getElementById('quoteClientContact').value = '';
    if (document.getElementById('quoteClientEmail')) document.getElementById('quoteClientEmail').value = '';
    if (document.getElementById('quoteClientPhone')) document.getElementById('quoteClientPhone').value = '';
    if (document.getElementById('quoteFolio')) document.getElementById('quoteFolio').value = getNextQuotationFolio();
    if (document.getElementById('quoteValidityDays')) document.getElementById('quoteValidityDays').value = '30';
    if (document.getElementById('quoteApplyTax')) document.getElementById('quoteApplyTax').checked = true;
    if (document.getElementById('quoteRequireDownPayment')) document.getElementById('quoteRequireDownPayment').checked = true;
    if (document.getElementById('quoteNotes')) document.getElementById('quoteNotes').value = '';

    currentQuotationItems = [];
    localStorage.removeItem(STORAGE_KEY_QUOTE_DRAFT);

    renderQuoteItemsList();
    recalculateQuoteTotals();
    showToast("🧹 Formulario de cotización reiniciado.");
}

function switchQuotationSubView(subView) {
    const btnBuilder = document.getElementById('tabBtnNewQuotation');
    const btnHistory = document.getElementById('tabBtnHistoryQuotations');
    const viewBuilder = document.getElementById('quotationBuilderView');
    const viewHistory = document.getElementById('quotationHistoryView');

    if (subView === 'builder') {
        btnBuilder?.classList.add('active');
        btnHistory?.classList.remove('active');
        viewBuilder?.classList.remove('hidden');
        viewHistory?.classList.add('hidden');
    } else {
        btnBuilder?.classList.remove('active');
        btnHistory?.classList.add('active');
        viewBuilder?.classList.add('hidden');
        viewHistory?.classList.remove('hidden');
        renderQuotationHistory();
    }
}

function saveQuotationToHistory() {
    const clientName = (document.getElementById('quoteClientName')?.value || '').trim();
    if (!clientName) {
        alert("Por favor ingresa el nombre del cliente o marca antes de guardar.");
        document.getElementById('quoteClientName')?.focus();
        return;
    }

    if (currentQuotationItems.length === 0) {
        alert("Agrega al menos un concepto de taller a la cotización.");
        return;
    }

    let subtotal = 0;
    currentQuotationItems.forEach(it => { subtotal += (it.quantity * it.unit_price); });

    const applyTax = document.getElementById('quoteApplyTax')?.checked ?? true;
    const tax = applyTax ? (subtotal * 0.16) : 0;
    const total = subtotal + tax;
    const requireDown = document.getElementById('quoteRequireDownPayment')?.checked ?? true;
    const downPayment = requireDown ? (total * 0.50) : 0;

    const folio = (document.getElementById('quoteFolio')?.value || '').trim() || getNextQuotationFolio();
    const today = new Date().toISOString().split('T')[0];

    const quoteRecord = {
        id: Date.now(),
        folio: folio,
        date: today,
        client_name: clientName,
        client_contact: document.getElementById('quoteClientContact')?.value || '',
        client_phone: document.getElementById('quoteClientPhone')?.value || '',
        client_email: document.getElementById('quoteClientEmail')?.value || '',
        validity_days: parseInt(document.getElementById('quoteValidityDays')?.value || '30'),
        apply_tax: applyTax,
        require_down_payment: requireDown,
        notes: document.getElementById('quoteNotes')?.value || '',
        items: JSON.parse(JSON.stringify(currentQuotationItems)),
        subtotal: subtotal,
        tax: tax,
        total: total,
        down_payment: downPayment,
        status: 'Enviada'
    };

    // Si ya existe el folio, actualizar; si no, agregar
    const existingIdx = quotationsHistory.findIndex(q => q.folio === folio);
    if (existingIdx !== -1) {
        quotationsHistory[existingIdx] = quoteRecord;
        showToast(`💾 Cotización <strong>${folio}</strong> actualizada con éxito.`);
    } else {
        quotationsHistory.unshift(quoteRecord);
        showToast(`💾 Cotización <strong>${folio}</strong> guardada en el historial.`);
    }

    saveQuotationsHistory();
    // Preparar siguiente folio
    document.getElementById('quoteFolio').value = getNextQuotationFolio();
}

function renderQuotationHistory(filterTerm = '') {
    const tbody = document.getElementById('quotationHistoryTableBody');
    if (!tbody) return;

    tbody.innerHTML = '';
    const term = filterTerm.toLowerCase().trim();

    const filtered = quotationsHistory.filter(q => {
        if (!term) return true;
        return (q.folio || '').toLowerCase().includes(term) ||
               (q.client_name || '').toLowerCase().includes(term) ||
               (q.client_contact || '').toLowerCase().includes(term);
    });

    if (filtered.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align:center; padding:2rem; color:var(--text-muted);">
                    No hay cotizaciones registradas en el historial${term ? ' que coincidan con la búsqueda' : ''}.
                </td>
            </tr>
        `;
        return;
    }

    filtered.forEach(q => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-family:monospace; font-weight:700; color:var(--accent-cyan);">${escapeHtml(q.folio)}</td>
            <td style="font-size:0.8rem; color:var(--text-muted);">${q.date}</td>
            <td>
                <strong>${escapeHtml(q.client_name)}</strong>
                ${q.client_contact ? `<div style="font-size:0.75rem; color:var(--text-subtle);">${escapeHtml(q.client_contact)}</div>` : ''}
            </td>
            <td><span class="work-type-badge rotulacion">${q.items ? q.items.length : 0} conceptos</span></td>
            <td><strong style="color:var(--text-main);">$${q.total.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</strong></td>
            <td><strong style="color:var(--accent-lime);">$${q.down_payment.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</strong></td>
            <td><span class="status-chip ${q.status === 'Aprobada' ? 'approved' : 'in_progress'}">${q.status}</span></td>
            <td style="text-align:right;">
                <button type="button" class="btn-table-action" onclick="loadQuotationIntoBuilder(${q.id})" title="Editar en cotizador">✏️</button>
                <button type="button" class="btn-table-action" onclick="printQuotationFromHistory(${q.id})" title="Imprimir / PDF">🖨️</button>
                <button type="button" class="btn-table-action danger" onclick="deleteQuotationFromHistory(${q.id})" title="Eliminar cotización">🗑️</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function filterQuotationHistory(term) {
    renderQuotationHistory(term);
}

function loadQuotationIntoBuilder(id) {
    const quote = quotationsHistory.find(q => q.id === id);
    if (!quote) return;

    if (document.getElementById('quoteClientName')) document.getElementById('quoteClientName').value = quote.client_name || '';
    if (document.getElementById('quoteClientContact')) document.getElementById('quoteClientContact').value = quote.client_contact || '';
    if (document.getElementById('quoteClientEmail')) document.getElementById('quoteClientEmail').value = quote.client_email || '';
    if (document.getElementById('quoteClientPhone')) document.getElementById('quoteClientPhone').value = quote.client_phone || '';
    if (document.getElementById('quoteFolio')) document.getElementById('quoteFolio').value = quote.folio || '';
    if (document.getElementById('quoteValidityDays')) document.getElementById('quoteValidityDays').value = quote.validity_days || '30';
    if (document.getElementById('quoteApplyTax')) document.getElementById('quoteApplyTax').checked = quote.apply_tax ?? true;
    if (document.getElementById('quoteRequireDownPayment')) document.getElementById('quoteRequireDownPayment').checked = quote.require_down_payment ?? true;
    if (document.getElementById('quoteNotes')) document.getElementById('quoteNotes').value = quote.notes || '';

    currentQuotationItems = JSON.parse(JSON.stringify(quote.items || []));

    switchQuotationSubView('builder');
    renderQuoteItemsList();
    recalculateQuoteTotals();
    showToast(`📂 Cotización <strong>${quote.folio}</strong> cargada en el editor.`);
}

function deleteQuotationFromHistory(id) {
    const quote = quotationsHistory.find(q => q.id === id);
    if (!quote) return;

    if (confirm(`¿Estás seguro de eliminar la cotización ${quote.folio} para ${quote.client_name}?`)) {
        quotationsHistory = quotationsHistory.filter(q => q.id !== id);
        saveQuotationsHistory();
        renderQuotationHistory();
        showToast("🗑️ Cotización eliminada del historial.");
    }
}

function printQuotationFromHistory(id) {
    const quote = quotationsHistory.find(q => q.id === id);
    if (!quote) return;

    loadQuotationIntoBuilder(id);
    generateQuotationDocument(false);
}

function generateQuotationDocument(isPreview = false) {
    const clientName = (document.getElementById('quoteClientName')?.value || '').trim();
    if (!clientName) {
        alert("Por favor ingresa el nombre del cliente o empresa.");
        document.getElementById('quoteClientName')?.focus();
        return;
    }

    if (currentQuotationItems.length === 0) {
        alert("Por favor agrega al menos un concepto a cotizar.");
        return;
    }

    const folio = document.getElementById('quoteFolio')?.value || getNextQuotationFolio();
    const contact = document.getElementById('quoteClientContact')?.value || '';
    const email = document.getElementById('quoteClientEmail')?.value || '';
    const phone = document.getElementById('quoteClientPhone')?.value || '';
    const validity = document.getElementById('quoteValidityDays')?.value || '30';
    const notes = document.getElementById('quoteNotes')?.value || 'Tiempos de fabricación: 7 a 10 días hábiles tras recibir anticipo del 50% y vector autorizado.';

    let subtotal = 0;
    currentQuotationItems.forEach(it => { subtotal += (it.quantity * it.unit_price); });

    const applyTax = document.getElementById('quoteApplyTax')?.checked ?? true;
    const tax = applyTax ? (subtotal * 0.16) : 0.0;
    const total = subtotal + tax;
    const requireDown = document.getElementById('quoteRequireDownPayment')?.checked ?? true;
    const downPayment = requireDown ? (total * 0.50) : 0.0;

    const todayDate = new Date().toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' });

    // Construir tabla de items HTML
    let itemsRowsHtml = '';
    currentQuotationItems.forEach((it, idx) => {
        const itemSub = (it.quantity * it.unit_price);
        itemsRowsHtml += `
            <tr>
                <td style="width:40px; text-align:center; color:#94a3b8; font-weight:700;">${idx + 1}</td>
                <td>
                    <div class="sheet-item-title">${escapeHtml(it.name)}</div>
                    ${it.description ? `<div class="sheet-item-specs">${escapeHtml(it.description)}</div>` : ''}
                </td>
                <td style="width:70px; text-align:center; font-weight:700;">${it.quantity}</td>
                <td style="width:120px; text-align:right;">$${it.unit_price.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</td>
                <td style="width:130px; text-align:right; font-weight:800; color:#0f172a;">$${itemSub.toLocaleString('es-MX', { minimumFractionDigits: 2 })}</td>
            </tr>
        `;
    });

    const sheetContainer = document.getElementById('printableQuoteSheet');
    if (!sheetContainer) return;

    sheetContainer.innerHTML = `
        <div class="sheet-header">
            <div class="sheet-brand-meta">
                <div class="sheet-logo-wrap">
                    <img src="assets/logo-color.svg" alt="Letrerama">
                </div>
                <div class="sheet-brand-sub">Fabricación · Montaje · Letras Corpóreas 3D · Cajas de Luz LED</div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:0.2rem;">
                    Guadalajara, Jalisco, México · WhatsApp: 33 3676 2545 · contacto@letrerama.com
                </div>
            </div>
            <div class="sheet-doc-meta">
                <h1 class="sheet-doc-title">Cotización Formal</h1>
                <div class="sheet-doc-folio">${escapeHtml(folio)}</div>
                <div class="sheet-doc-date">Fecha de emisión: <strong>${todayDate}</strong></div>
                <div class="sheet-doc-date">Vigencia: <strong>${validity} días naturales</strong></div>
            </div>
        </div>

        <div class="sheet-client-grid">
            <div>
                <div class="sheet-client-label">Cliente / Razón Social:</div>
                <div class="sheet-client-name">${escapeHtml(clientName)}</div>
                ${contact ? `<div class="sheet-client-sub"><strong>Atención:</strong> ${escapeHtml(contact)}</div>` : ''}
            </div>
            <div>
                <div class="sheet-client-label">Datos de Contacto:</div>
                ${phone ? `<div class="sheet-client-sub"><strong>Tel / WhatsApp:</strong> ${escapeHtml(phone)}</div>` : ''}
                ${email ? `<div class="sheet-client-sub"><strong>E-mail:</strong> ${escapeHtml(email)}</div>` : ''}
                <div class="sheet-client-sub"><strong>Validez comercial:</strong> Precios sujetos a anticipo</div>
            </div>
        </div>

        <table class="sheet-table">
            <thead>
                <tr>
                    <th style="width:40px; text-align:center;">#</th>
                    <th>Descripción Técnica / Especificaciones</th>
                    <th style="width:70px; text-align:center;">Cant.</th>
                    <th style="width:120px; text-align:right;">P. Unitario</th>
                    <th style="width:130px; text-align:right;">Importe</th>
                </tr>
            </thead>
            <tbody>
                ${itemsRowsHtml}
            </tbody>
        </table>

        <div class="sheet-totals-section">
            <table class="sheet-totals-table">
                <tr>
                    <td>Subtotal:</td>
                    <td>$${subtotal.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                </tr>
                ${applyTax ? `
                <tr>
                    <td>I.V.A. (16%):</td>
                    <td>$${tax.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                </tr>
                ` : ''}
                <tr class="total-row">
                    <td>TOTAL:</td>
                    <td>$${total.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                </tr>
                ${requireDown ? `
                <tr class="anticipo-row">
                    <td>Anticipo Requerido (50%):</td>
                    <td>$${downPayment.toLocaleString('es-MX', { minimumFractionDigits: 2 })} MXN</td>
                </tr>
                ` : ''}
            </table>
        </div>

        <div class="sheet-conditions-box">
            <strong style="display:block; margin-bottom:0.25rem; color:#0f172a;">Condiciones de Taller, Fabricación & Garantía:</strong>
            ${escapeHtml(notes)}
            <div style="margin-top:0.35rem; font-size:0.72rem; color:#64748b;">
                * La fabricación inicia formalmente al recibir comprobante del anticipo acordado y visto bueno final del trazo vectorial. Todos los letreros luminosos cuentan con garantía por escrito de 12 meses en módulos LED y fuentes de poder.
            </div>
        </div>

        <div class="sheet-signatures-grid">
            <div class="sheet-sig-box">
                <strong>Ing. Alberto / Dirección de Taller</strong>
                <span>Letrerama Rótulos & Letras 3D</span>
            </div>
            <div class="sheet-sig-box">
                <strong>${escapeHtml(contact || clientName)}</strong>
                <span>Firma de Conformidad / Aceptación</span>
            </div>
        </div>
    `;

    // Actualizar badge en modal
    const badge = document.getElementById('previewModalFolioBadge');
    if (badge) badge.textContent = folio;

    // Mostrar modal
    const modal = document.getElementById('quotationPreviewModal');
    if (modal) modal.classList.remove('hidden');

    if (!isPreview) {
        setTimeout(() => {
            window.print();
        }, 300);
    }
}

function printQuotationDocument() {
    window.print();
}

function closeQuotationPreviewModal() {
    const modal = document.getElementById('quotationPreviewModal');
    if (modal) modal.classList.add('hidden');
}

