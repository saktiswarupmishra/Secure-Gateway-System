/**
 * Login Page Logic
 */

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const errorEl = document.getElementById('login-error');
    const btn = document.getElementById('btn-login');

    if (!username || !password) {
        errorEl.textContent = 'Please enter both username and password.';
        errorEl.style.display = 'block';
        return;
    }

    btn.disabled = true;
    btn.textContent = 'Signing in...';
    errorEl.style.display = 'none';

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'same-origin'
        });

        const data = await res.json();

        if (res.ok && data.success) {
            window.location.href = '/dashboard';
        } else {
            errorEl.textContent = data.error || 'Invalid credentials';
            errorEl.style.display = 'block';
            // Re-trigger shake animation
            errorEl.style.animation = 'none';
            void errorEl.offsetHeight;
            errorEl.style.animation = 'shakeError 0.4s ease';
        }
    } catch (err) {
        errorEl.textContent = 'Connection error. Please try again.';
        errorEl.style.display = 'block';
    } finally {
        btn.disabled = false;
        btn.textContent = 'Sign In';
    }
}

// Auto-focus username field
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('username');
    if (input) input.focus();
});
