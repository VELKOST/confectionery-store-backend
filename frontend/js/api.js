// api.js
// Функции для выполнения запросов к API через fetch
// Будем добавлять токен автоматически, если он есть

function getToken() {
    return localStorage.getItem('token') || null;
}

async function apiGet(url) {
    const headers = {};
    const token = getToken();
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    const response = await fetch(url, { headers });
    if (!response.ok) {
        throw new Error(`GET ${url} failed: ` + response.statusText);
    }
    return response.json();
}

async function apiPost(url, body) {
    const headers = {'Content-Type': 'application/json'};
    const token = getToken();
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    const response = await fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(body)
    });
    if (!response.ok) {
        throw new Error(`POST ${url} failed: ` + response.statusText);
    }
    return response.json();
}

async function apiPut(url, body) {
    const headers = {'Content-Type': 'application/json'};
    const token = getToken();
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    const response = await fetch(url, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify(body)
    });
    if (!response.ok) {
        throw new Error(`PUT ${url} failed: ` + response.statusText);
    }
    return response.json();
}

async function apiDelete(url) {
    const headers = {};
    const token = getToken();
    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    const response = await fetch(url, {
        method: 'DELETE',
        headers: headers
    });
    if (!response.ok) {
        throw new Error(`DELETE ${url} failed: ` + response.statusText);
    }
    return response.json();
}