/**
 * Key Management Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    loadKeys();
    loadKeyStats();
});

async function loadKeyStats() {
    try {
        const res = await api('/api/keys/stats');
        if (!res) return;
        const data = await res.json();

        animateValue(document.getElementById('stat-total-keys'), data.total_keys);
        animateValue(document.getElementById('stat-active-keys'), data.active_keys);
        animateValue(document.getElementById('stat-inactive-keys'), data.inactive_keys);
        animateValue(document.getElementById('stat-expiring'), data.expiring_soon);
    } catch (e) {
        console.error('Failed to load key stats:', e);
    }
}

async function loadKeys() {
    try {
        const res = await api('/api/keys');
        if (!res) return;
        const data = await res.json();
        renderKeys(data.keys || []);
    } catch (e) {
        console.error('Failed to load keys:', e);
    }
}

function renderKeys(keys) {
    const tbody = document.getElementById('keys-table');

    if (!keys.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted" style="padding:30px;">No encryption keys found</td></tr>';
        return;
    }

    tbody.innerHTML = keys.map(key => {
        const statusBadge = key.is_active
            ? '<span class="badge badge-success">Active</span>'
            : '<span class="badge badge-danger">Inactive</span>';

        const isExpired = key.expires_at && new Date(key.expires_at) < new Date();
        const expiryDisplay = key.expires_at
            ? (isExpired ? `<span class="text-danger">${formatDate(key.expires_at)}</span>` : formatDate(key.expires_at))
            : '<span class="text-muted">Never</span>';

        return `
            <tr>
                <td class="mono">${key.id}</td>
                <td style="font-weight:600;">${key.key_name}</td>
                <td class="mono" style="font-size:11px;">${key.key_preview}</td>
                <td><span class="badge badge-purple">${key.algorithm}</span></td>
                <td>${statusBadge}</td>
                <td style="font-size:12px;">${formatDate(key.created_at)}</td>
                <td style="font-size:12px;">${expiryDisplay}</td>
                <td>
                    ${window.currentUserRole === 'admin' && key.is_active ? `<button class="btn btn-outline btn-sm" onclick="deactivateKey(${key.id})" title="Deactivate">⏸</button>` : ''}
                    ${window.currentUserRole === 'admin' ? `<button class="btn btn-outline btn-sm" onclick="deleteKey(${key.id})" title="Delete" style="margin-left:4px;">🗑</button>` : ''}
                </td>
            </tr>
        `;
    }).join('');
}

function openGenerateModal() {
    document.getElementById('key-name').value = '';
    document.getElementById('key-expiry').value = '30';
    openModal('modal-generate');
}

async function generateKey() {
    const name = document.getElementById('key-name').value.trim() || 'unnamed-key';
    const expiresIn = parseInt(document.getElementById('key-expiry').value) || 30;

    try {
        const res = await api('/api/keys', {
            method: 'POST',
            body: { name, expires_in_days: expiresIn }
        });
        const data = await res.json();

        if (data.success) {
            showToast(`Key "${name}" generated successfully`);
            closeModal('modal-generate');
            loadKeys();
            loadKeyStats();
        } else {
            showToast(data.error || 'Failed to generate key', 'error');
        }
    } catch (e) {
        showToast('Error generating key', 'error');
    }
}

async function rotateKeys() {
    if (!confirm('This will deactivate ALL current keys and generate a new one. Continue?')) return;

    try {
        const res = await api('/api/keys/rotate', { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            showToast('Key rotation complete — new key active');
            loadKeys();
            loadKeyStats();
        } else {
            showToast(data.error || 'Rotation failed', 'error');
        }
    } catch (e) {
        showToast('Error rotating keys', 'error');
    }
}

async function deactivateKey(keyId) {
    if (!confirm('Deactivate this key?')) return;

    try {
        const res = await api(`/api/keys/${keyId}/deactivate`, { method: 'POST' });
        const data = await res.json();

        if (data.success) {
            showToast('Key deactivated');
            loadKeys();
            loadKeyStats();
        } else {
            showToast(data.error || 'Failed to deactivate', 'error');
        }
    } catch (e) {
        showToast('Error deactivating key', 'error');
    }
}

async function deleteKey(keyId) {
    if (!confirm('Permanently delete this key? This action cannot be undone.')) return;

    try {
        const res = await api(`/api/keys/${keyId}`, { method: 'DELETE' });
        const data = await res.json();

        if (data.success) {
            showToast('Key deleted');
            loadKeys();
            loadKeyStats();
        } else {
            showToast(data.error || 'Failed to delete', 'error');
        }
    } catch (e) {
        showToast('Error deleting key', 'error');
    }
}
