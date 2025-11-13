(function () {
    const currentScript = document.currentScript;
    const skipGuard = currentScript && currentScript.dataset.skipGuard === 'true';

    async function checkSession() {
        try {
            const data = await window.api.get('/api/session');
            if (data && data.authenticated) {
                localStorage.setItem('allowed', 'true');
                return true;
            }
        } catch (error) {
            console.error('Session check failed', error);
        }

        localStorage.removeItem('allowed');
        return false;
    }

    if (!skipGuard) {
        checkSession().then(isAllowed => {
            if (!isAllowed) {
                window.location.href = 'index.html';
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        const logoutLink = document.querySelector('[data-logout]');
        if (logoutLink) {
            logoutLink.addEventListener('click', async function (event) {
                event.preventDefault();
                try {
                    await window.api.post('/api/logout');
                } catch (error) {
                    console.error('Failed to log out', error);
                }
                localStorage.removeItem('allowed');
                window.location.href = 'index.html';
            });
        }
    });
})();
