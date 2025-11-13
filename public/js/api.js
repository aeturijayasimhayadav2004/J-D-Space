(function () {
    async function request(path, options = {}) {
        const config = Object.assign({
            credentials: 'include',
            headers: {}
        }, options);

        if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
            config.headers['Content-Type'] = 'application/json';
            config.body = JSON.stringify(config.body);
        }

        const response = await fetch(path, config);
        let payload = null;
        const contentType = response.headers.get('Content-Type') || '';
        if (contentType.includes('application/json')) {
            try {
                payload = await response.json();
            } catch (error) {
                console.error('Unable to parse JSON response', error);
            }
        } else {
            payload = await response.text();
        }

        if (!response.ok) {
            const message = payload && payload.message ? payload.message : 'Request failed';
            throw new Error(message);
        }

        return payload;
    }

    window.api = {
        get(path) {
            return request(path, { method: 'GET' });
        },
        post(path, body) {
            return request(path, { method: 'POST', body });
        },
        del(path) {
            return request(path, { method: 'DELETE' });
        }
    };
})();
