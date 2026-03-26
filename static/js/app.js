/**
 * Secure Gateway System — Shared Utilities
 */

// ---- API Helper ----
async function api(url, options = {}) {
    const defaults = {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin'
    };
    const config = { ...defaults, ...options };
    if (options.body && typeof options.body === 'object') {
        config.body = JSON.stringify(options.body);
    }

    const response = await fetch(url, config);

    if (response.status === 401) {
        window.location.href = '/login';
        return null;
    }

    return response;
}

// ---- Toast Notifications ----
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = { success: '✅', error: '❌', warning: '⚠️' };
    toast.innerHTML = `<span>${icons[type] || ''}</span> ${message}`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(20px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ---- Modal Helpers ----
function openModal(id) {
    document.getElementById(id).classList.add('show');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}

// ---- Formatting ----
function formatDate(isoStr) {
    if (!isoStr) return '—';
    const d = new Date(isoStr);
    return d.toLocaleString('en-IN', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// ---- Counter Animation ----
function animateValue(el, target, duration = 600) {
    if (!el) return;
    const start = parseInt(el.textContent) || 0;
    const diff = target - start;
    if (diff === 0) { el.textContent = target; return; }

    const startTime = performance.now();
    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
        el.textContent = Math.round(start + diff * eased);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}

// ---- Load Current User Info ----
async function loadUser() {
    try {
        const res = await api('/api/me');
        if (!res) return;
        const data = await res.json();
        if (data.user) {
            window.currentUserRole = data.user.role;
            const nameEl = document.getElementById('display-username');
            const roleEl = document.getElementById('display-role');
            const avatarEl = document.getElementById('user-avatar');
            if (nameEl) nameEl.textContent = data.user.username;
            if (roleEl) roleEl.textContent = data.user.role;
            if (avatarEl) avatarEl.textContent = data.user.username.charAt(0).toUpperCase();
        }
    } catch (e) {
        console.error('Failed to load user:', e);
    }
}

// ---- Logout ----
async function logout() {
    try {
        await api('/api/logout', { method: 'POST' });
    } catch (e) {}
    window.location.href = '/login';
}

// ---- Highlight Active Nav ----
function setActiveNav() {
    const path = window.location.pathname;
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('href') === path) {
            item.classList.add('active');
        }
    });
}

// ---- Init ----
document.addEventListener('DOMContentLoaded', () => {
    loadUser();
    setActiveNav();
});
