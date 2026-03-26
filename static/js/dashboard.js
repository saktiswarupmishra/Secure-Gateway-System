/**
 * Dashboard Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
    loadGatewayStatus();
});

async function loadDashboardStats() {
    try {
        const res = await api('/api/dashboard/stats');
        if (!res) return;
        const data = await res.json();

        // Animate stat counters
        animateValue(document.getElementById('stat-active-keys'), data.keys.active_keys);
        animateValue(document.getElementById('stat-encryptions'), data.logs.encryption_count);
        animateValue(document.getElementById('stat-total-logs'), data.logs.total_events);
        animateValue(document.getElementById('stat-failures'), data.logs.failure_count);

        // Recent activity table
        renderRecentLogs(data.logs.recent_events || []);
    } catch (e) {
        console.error('Failed to load dashboard stats:', e);
    }
}

async function loadGatewayStatus() {
    try {
        const res = await api('/api/gateway/status');
        if (!res) return;
        const data = await res.json();
        updateGatewayUI(data);
    } catch (e) {
        console.error('Failed to load gateway status:', e);
    }
}

function updateGatewayUI(data) {
    const orb = document.getElementById('gw-orb');
    const statusText = document.getElementById('gw-status-text');
    const uptimeEl = document.getElementById('gw-uptime');
    const startBtn = document.getElementById('btn-gw-start');
    const stopBtn = document.getElementById('btn-gw-stop');

    if (data.is_running) {
        orb.className = 'gw-status-orb active';
        orb.textContent = '🟢';
        statusText.textContent = 'Online — Securing Traffic';
        statusText.style.color = 'var(--accent-green)';
        uptimeEl.textContent = 'Uptime: ' + (data.uptime || '—');
        if (startBtn) startBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = '';
    } else {
        orb.className = 'gw-status-orb inactive';
        orb.textContent = '🔌';
        statusText.textContent = 'Offline';
        statusText.style.color = 'var(--text-muted)';
        uptimeEl.textContent = 'Gateway is not running';
        if (startBtn) startBtn.style.display = '';
        if (stopBtn) stopBtn.style.display = 'none';
    }

    document.getElementById('gw-port').textContent = data.listen_port;
    document.getElementById('gw-forward').textContent = data.forward_host + ':' + data.forward_port;
    document.getElementById('gw-sessions').textContent = data.total_sessions;
    document.getElementById('gw-bytes').textContent = formatBytes(data.total_bytes_transferred || 0);
}

async function startGateway() {
    try {
        const res = await api('/api/gateway/start', { method: 'POST', body: {} });
        const data = await res.json();
        if (data.success) {
            showToast('Gateway started successfully');
            loadGatewayStatus();
        } else {
            showToast(data.error || 'Failed to start gateway', 'error');
        }
    } catch (e) {
        showToast('Error starting gateway', 'error');
    }
}

async function stopGateway() {
    try {
        const res = await api('/api/gateway/stop', { method: 'POST', body: {} });
        const data = await res.json();
        if (data.success) {
            showToast('Gateway stopped');
            loadGatewayStatus();
        } else {
            showToast(data.error || 'Failed to stop gateway', 'error');
        }
    } catch (e) {
        showToast('Error stopping gateway', 'error');
    }
}

async function runTest() {
    const input = document.getElementById('test-input').value;
    const resultEl = document.getElementById('test-result');

    if (!input.trim()) {
        showToast('Enter test data first', 'warning');
        return;
    }

    try {
        const res = await api('/api/gateway/test', {
            method: 'POST',
            body: { data: input }
        });
        const data = await res.json();

        resultEl.classList.remove('hidden');
        if (data.success) {
            resultEl.className = 'test-result';
            resultEl.innerHTML = `
                <div style="margin-bottom:8px;"><strong>✅ Round-trip successful — integrity verified</strong></div>
                <div class="mono" style="margin-bottom:4px;"><strong>Encrypted:</strong> ${data.encrypted.substring(0, 60)}...</div>
                <div class="mono" style="margin-bottom:4px;"><strong>Decrypted:</strong> ${data.decrypted}</div>
                <div style="font-size:12px;color:var(--text-muted);margin-top:6px;">
                    Original: ${data.original_size} bytes → Encrypted: ${data.encrypted_size} bytes
                </div>
            `;
        } else {
            resultEl.className = 'test-result error';
            resultEl.innerHTML = `<strong>❌ Test failed:</strong> ${data.error}`;
        }
    } catch (e) {
        resultEl.classList.remove('hidden');
        resultEl.className = 'test-result error';
        resultEl.innerHTML = '<strong>❌ Connection error</strong>';
    }
}

function renderRecentLogs(logs) {
    const tbody = document.getElementById('recent-logs');
    if (!logs.length) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted" style="padding:30px;">No recent activity</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const statusClass = log.status === 'SUCCESS' ? 'badge-success' :
                          log.status === 'FAILURE' ? 'badge-danger' : 'badge-warning';
        return `
            <tr>
                <td class="mono" style="font-size:11px;">${formatDate(log.timestamp)}</td>
                <td><span class="badge badge-info">${log.event_type}</span></td>
                <td><span class="badge ${statusClass}">${log.status}</span></td>
                <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${log.message || '—'}</td>
                <td class="mono">${log.source_ip || '—'}</td>
            </tr>
        `;
    }).join('');
}
