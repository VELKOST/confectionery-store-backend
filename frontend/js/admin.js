// admin.js
// Логика для административных действий: управление продуктами, заказами, пользователями
async function loadUserInfo() {
    try {
        const user = await apiGet('/auth/me'); // Предполагаемый эндпоинт для получения текущего пользователя
        localStorage.setItem('user_role', user.role);
        localStorage.setItem('user_id', user.id);
    } catch (error) {
        console.error('Ошибка загрузки информации о пользователе:', error);
        alert('Не удалось загрузить информацию о пользователе. Пожалуйста, войдите в систему снова.');
        window.location.href = '/login.html';
    }
}

async function loadAdminUI() {
    const role = localStorage.getItem('user_role');
    if (!role || (role !== 'admin' && role !== 'seller')) {
        alert('У вас нет доступа к админ-панели');
        window.location.href = '/';
        return;
    }
    await loadProductsForAdmin();
    await loadOrdersForAdmin();
    if (role === 'admin') {
        await loadUsers(); // Загружаем пользователей только для администраторов
    }
}

async function loadProductsForAdmin() {
    try {
        const products = await apiGet('/products/');
        const productList = document.getElementById('adminProductList');
        if (products.length === 0) {
            productList.innerHTML = '<tr><td colspan="7">Нет доступных продуктов.</td></tr>';
            return;
        }
        productList.innerHTML = products.map(p => `
            <tr>
                <td>${p.id}</td>
                <td>${p.name}</td>
                <td>${p.price} руб.</td>
                <td>${p.category || ''}</td>
                <td>${p.description || ''}</td>
                <td><button onclick="editProduct(${p.id}, '${escapeHtml(p.name)}', ${p.price}, '${escapeHtml(p.category || '')}', '${escapeHtml(p.description || '')}')">Изменить</button></td>
                <td><button onclick="deleteProduct(${p.id})">Удалить</button></td>
            </tr>
        `).join('');
    } catch (e) {
        alert('Ошибка загрузки продуктов: ' + e.message);
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

async function createProduct(name, price, category, description) {
    const seller_id = localStorage.getItem('user_id');
    const data = {
        name,
        price: parseFloat(price),
        category,
        description,
        seller_id: parseInt(seller_id)
    };
    await apiPost('/products/', data);
    loadProductsForAdmin();
}

async function editProduct(id, oldName, oldPrice, oldCategory, oldDesc) {
    const name = prompt('Название:', oldName);
    if (name === null) return;
    const price = prompt('Цена:', oldPrice);
    if (price === null) return;
    const category = prompt('Категория:', oldCategory);
    if (category === null) return;
    const description = prompt('Описание:', oldDesc);
    if (description === null) return;

    if (name.trim() === '' || price === '') {
        alert('Название и Цена не могут быть пустыми.');
        return;
    }

    try {
        await apiPut(`/products/${id}`, {
            name: name.trim(),
            price: parseFloat(price),
            category: category.trim(),
            description: description.trim()
        });
        alert('Продукт успешно обновлён');
        loadProductsForAdmin();
    } catch (error) {
        alert('Ошибка обновления продукта: ' + error.message);
    }
}

async function deleteProduct(id) {
    if (!confirm('Вы уверены, что хотите удалить этот продукт?')) return;
    try {
        await apiDelete(`/products/${id}`);
        alert('Продукт успешно удалён');
        loadProductsForAdmin();
    } catch (error) {
        alert('Ошибка удаления продукта: ' + error.message);
    }
}

// Управление заказами

async function loadOrdersForAdmin() {
    try {
        const orders = await apiGet('/order/orders');
        const orderList = document.getElementById('adminOrderList');
        if (orders.length === 0) {
            orderList.innerHTML = '<tr><td colspan="5">Нет доступных заказов.</td></tr>';
            return;
        }
        orderList.innerHTML = orders.map(o => `
            <tr>
                <td>${o.order_id}</td>
                <td>${o.status}</td>
                <td>${o.total_price} руб.</td>
                <td>${new Date(o.created_at).toLocaleString()}</td>
                <td><button onclick="updateOrderStatus(${o.order_id})">Изменить статус</button></td>
            </tr>
        `).join('');
    } catch (e) {
        alert('Ошибка загрузки заказов: ' + e.message);
    }
}

async function updateOrderStatus(order_id) {
    const status = prompt('Новый статус (например: shipped, completed):', 'shipped');
    if (status === null || status.trim() === '') {
        alert('Статус не может быть пустым.');
        return;
    }
    try {
        await apiPut(`/order/orders/${order_id}/status`, {status: status.trim()});
        alert('Статус заказа успешно обновлён');
        loadOrdersForAdmin();
    } catch (error) {
        alert('Ошибка обновления статуса заказа: ' + error.message);
    }
}

// Управление пользователями (если API доступен)

async function loadUsers() {
    try {
        const users = await apiGet('/auth/users');  // Предполагаемый эндпоинт
        const userList = document.getElementById('userList');
        if (!userList) {
            console.error("Элемент с ID 'userList' не найден в DOM.");
            return;
        }

        if (users.length === 0) {
            userList.innerHTML = '<tr><td colspan="5">Нет доступных пользователей.</td></tr>';
            return;
        }
        userList.innerHTML = users.map(u => `
            <tr>
                <td>${u.id}</td>
                <td>${u.name}</td>
                <td>${u.email}</td>
                <td>${u.role}</td>
                <td><button onclick="changeRole(${u.id}, '${u.role}')">Изменить роль</button></td>
            </tr>
        `).join('');
    } catch (e) {
        console.error('Ошибка загрузки пользователей:', e);
        alert('Ошибка загрузки пользователей: ' + e.message);
    }
}

async function changeRole(user_id, oldRole) {
    const role = prompt('Новая роль (user/admin/seller):', oldRole);
    if (role === null || role.trim() === '') {
        alert('Роль не может быть пустой.');
        return;
    }
    const validRoles = ['user', 'admin', 'seller'];
    if (!validRoles.includes(role.trim())) {
        alert('Неверная роль. Доступны: user, admin, seller.');
        return;
    }
    try {
        await apiPut(`/auth/users/${user_id}/role`, {role: role.trim()});
        alert('Роль пользователя успешно обновлена');
        loadUsers();
    } catch (error) {
        alert('Ошибка обновления роли пользователя: ' + error.message);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', async () => {
    await loadUserInfo();
    await loadAdminUI();
    await loadProductsForAdmin();
    await loadOrdersForAdmin();
    await loadUsers();  // Если API доступен
});