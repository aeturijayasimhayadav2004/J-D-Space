document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
    const feedback = document.getElementById('feedback');

    async function redirectIfAuthenticated() {
        try {
            const data = await window.api.get('/api/session');
            if (data && data.authenticated) {
                localStorage.setItem('allowed', 'true');
                window.location.href = 'home.html';
            }
        } catch (error) {
            console.warn('Unable to verify session', error);
        }
    }

    redirectIfAuthenticated();

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        const password = form.password.value.trim();

        if (!password) {
            feedback.textContent = 'Please enter the secret password.';
            feedback.classList.add('error');
            return;
        }

        feedback.textContent = 'Checking password…';
        feedback.className = 'feedback';

        try {
            await window.api.post('/api/login', { password });
            localStorage.setItem('allowed', 'true');
            window.location.href = 'home.html';
        } catch (error) {
            const isNetworkError = error.message === 'Failed to fetch' || error.message === 'NetworkError when attempting to fetch resource.';
            if (isNetworkError) {
                feedback.textContent = 'Unable to reach the server. Make sure `python server.py` is running or that your deployment is live.';
            } else {
                feedback.textContent = error.message || 'Incorrect password. Try again?';
            }
            feedback.classList.add('error');
        }
    });
});
