// auth.js
// Регистрация, логин, получение информации о пользователе

async function register(name, email, password, role) {
    const data = await apiPost('/auth/register', {name, email, password, role});
    localStorage.setItem('token', data.token);
    // Можно также запросить /auth/me чтобы узнать роль пользователя
    await loadUserInfo();
    window.location.href = '/'; // перенаправим на главную
}

async function login(email, password) {
    const data = await apiPost('/auth/login', {email, password});
    localStorage.setItem('token', data.token);
    await loadUserInfo();
    window.location.href = '/';
}

async function loadUserInfo() {
    try {
        const user = await apiGet('/auth/me');
        localStorage.setItem('user_id', user.id);
        localStorage.setItem('user_role', user.role);
        localStorage.setItem('user_name', user.name);
    } catch (e) {
        // Если нет токена или он не валидный, очистим данные
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_role');
        localStorage.removeItem('user_name');
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_role');
    localStorage.removeItem('user_name');
    window.location.href = '/';
}