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
        status: 'active',
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
        status: 'active',
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
    loadStoredData();
    setupEventListeners();
    updateDatesAndWeek();
    renderProjectsDirectory();
    syncProjectDropdowns();
    renderWorkflowBoard();
}

function loadStoredData() {
    try {
        const storedProjects = localStorage.getItem(STORAGE_KEY_PROJECTS);
        if (storedProjects) {
            projectsData = JSON.parse(storedProjects);
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
    const secProjects = document.getElementById('sectionProjects');
    const secWorkflow = document.getElementById('sectionWorkflow');

    if (tabName === 'projects') {
        btnProjects.classList.add('active');
        btnWorkflow.classList.remove('active');
        secProjects.classList.add('active');
        secWorkflow.classList.remove('active');
        renderProjectsDirectory();
    } else {
        btnProjects.classList.remove('active');
        btnWorkflow.classList.add('active');
        secProjects.classList.remove('active');
        secWorkflow.classList.add('active');
        syncProjectDropdowns();
        renderWorkflowBoard();
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
        let statusLabel = 'Activo';
        if (p.status === 'paused') {
            statusClass = 'paused';
            statusLabel = 'En Pausa';
        } else if (p.status === 'completed') {
            statusClass = 'completed';
            statusLabel = 'Entregado';
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
                    <span class="status-chip ${statusClass === 'completed' ? 'completed' : (statusClass === 'paused' ? 'review' : 'in_production')}">
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
            if (p.client && p.in_agenda && (p.status || 'active') !== 'completed') {
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

function renderWorkflowBoard() {
    const currentWeekId = getWeekId(currentWeekOffset);

    // Limpiar columnas
    WORKFLOW_DAYS.forEach(day => {
        const listEl = document.getElementById(`taskList${capitalize(day)}`);
        if (listEl) listEl.innerHTML = '';
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

    const statusInfo = getTaskStatusInfo(task.status);
    const clientColor = getProjectBrandColor(task.project_client);

    card.innerHTML = `
        <div class="task-card-header">
            <span class="task-client-chip" style="background:${clientColor.bg}; color:${clientColor.text}; border:1px solid ${clientColor.border};">
                ${escapeHtml(task.project_client || 'Proyecto')}
            </span>
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
