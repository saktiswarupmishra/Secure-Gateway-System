/**
 * Audit Logs Page Logic
 */

let currentPage = 1;
let searchTimeout = null;

document.addEventListener('DOMContentLoaded', () => {
    loadEventTypes();
    loadLogs();
    loadLogStats();
});

async function loadEventTypes() {
    try {
        const res = await api('/api/logs/event-types');
        if (!res) return;
        const data = await res.json();
        const select = document.getElementById('filter-event-type');
        (data.event_types || []).forEach(type => {
            const opt = document.createElement('option');
            opt.value = type;
            opt.textContent = type;
            select.appendChild(opt);
        });
    } catch (e) {}
}

async function loadLogStats() {
    try {
        const res = await api('/api/logs/stats');
        if (!res) return;
        const data = await res.json();

        animateValue(document.getElementById('stat-total-events'), data.total_events);
        animateValue(document.getElementById('stat-success'), data.success_count);
        animateValue(document.getElementById('stat-failures'), data.failure_count);
        animateValue(document.getElementById('stat-warnings'), data.warning_count);
    } catch (e) {}
}

async function loadLogs(page) {
    if (page) currentPage = page;

    const eventType = document.getElementById('filter-event-type').value;
    const status = document.getElementById('filter-status').value;
    const search = document.getElementById('filter-search').value;

    let url = `/api/logs?page=${currentPage}&per_page=20`;
    if (eventType) url += `&event_type=${encodeURIComponent(eventType)}`;
    if (status) url += `&status=${encodeURIComponent(status)}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;

    try {
        const res = await api(url);
        if (!res) return;
        const data = await res.json();
        renderLogs(data.logs || []);
        renderPagination(data);
    } catch (e) {
        console.error('Failed to load logs:', e);
    }
}

function renderLogs(logs) {
    const tbody = document.getElementById('logs-table');

    if (!logs.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted" style="padding:30px;">No logs found</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const statusClass = log.status === 'SUCCESS' ? 'badge-success' :
                          log.status === 'FAILURE' ? 'badge-danger' : 'badge-warning';

        return `
            <tr>
                <td class="mono">${log.id}</td>
                <td class="mono" style="font-size:11px;white-space:nowrap;">${formatDate(log.timestamp)}</td>
                <td><span class="badge badge-info">${log.event_type}</span></td>
                <td><span class="badge ${statusClass}">${log.status}</span></td>
                <td class="mono">${log.source_ip || '—'}</td>
                <td class="mono">${log.dest_ip || '—'}</td>
                <td style="max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${log.message || '—'}</td>
            </tr>
        `;
    }).join('');
}

function renderPagination(data) {
    const container = document.getElementById('pagination');
    if (!data.pages || data.pages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    html += `<button class="page-btn" onclick="loadLogs(${data.page - 1})" ${!data.has_prev ? 'disabled' : ''}>‹</button>`;

    for (let i = 1; i <= data.pages; i++) {
        if (i === data.page) {
            html += `<button class="page-btn active">${i}</button>`;
        } else if (i === 1 || i === data.pages || Math.abs(i - data.page) <= 2) {
            html += `<button class="page-btn" onclick="loadLogs(${i})">${i}</button>`;
        } else if (Math.abs(i - data.page) === 3) {
            html += `<button class="page-btn" disabled>…</button>`;
        }
    }

    html += `<button class="page-btn" onclick="loadLogs(${data.page + 1})" ${!data.has_next ? 'disabled' : ''}>›</button>`;

    container.innerHTML = html;
}

function debounceSearch() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        currentPage = 1;
        loadLogs();
    }, 400);
}

function exportLogs() {
    const eventType = document.getElementById('filter-event-type').value;
    const status = document.getElementById('filter-status').value;

    let url = '/api/logs/export?';
    if (eventType) url += `event_type=${encodeURIComponent(eventType)}&`;
    if (status) url += `status=${encodeURIComponent(status)}&`;

    window.location.href = url;
}
