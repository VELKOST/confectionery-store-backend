// orders.js
// Логика для просмотра заказов пользователем или админом/продавцом

async function loadOrders() {
    const token = localStorage.getItem('token');
    if (!token) {
        alert('Сначала войдите в систему');
        window.location.href = '/login.html';
        return;
    }

    try {
        // Используем новый эндпоинт для получения только своих заказов
        const orders = await apiGet('/order/orders/me');
        const orderList = document.getElementById('orderList');
        orderList.innerHTML = orders.map(o => `
            <tr>
                <td>${o.order_id}</td>
                <td>${o.status}</td>
                <td>${o.total_price}</td>
                <td>${new Date(o.created_at).toLocaleString()}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Ошибка загрузки заказов:', error);
        alert('Не удалось загрузить заказы. Пожалуйста, попробуйте позже.');
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    await loadUserInfo();
    await loadOrders();
});