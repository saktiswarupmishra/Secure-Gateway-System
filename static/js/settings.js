/**
 * Settings Page Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
});

async function loadSettings() {
    try {
        const res = await api('/api/settings');
        if (!res) return;
        const data = await res.json();

        // Map settings to inputs
        const mappings = {
            'encryption_algorithm': 'set-algorithm',
            'key_rotation_days': 'set-key-rotation',
            'gateway_listen_port': 'set-listen-port',
            'gateway_forward_host': 'set-forward-host',
            'gateway_forward_port': 'set-forward-port',
            'log_retention_days': 'set-log-retention',
            'log_level': 'set-log-level'
        };

        for (const [key, inputId] of Object.entries(mappings)) {
            const el = document.getElementById(inputId);
            if (el && data[key] !== undefined) {
                el.value = data[key];
            }
        }
    } catch (e) {
        console.error('Failed to load settings:', e);
    }
}

async function saveSettings() {
    const inputs = document.querySelectorAll('[data-key]');
    const settings = {};

    inputs.forEach(input => {
        const key = input.getAttribute('data-key');
        settings[key] = input.value;
    });

    try {
        const res = await api('/api/settings', {
            method: 'POST',
            body: settings
        });
        const data = await res.json();

        if (data.success) {
            showToast('Settings saved successfully');
        } else {
            showToast(data.error || 'Failed to save settings', 'error');
        }
    } catch (e) {
        showToast('Error saving settings', 'error');
    }
}
