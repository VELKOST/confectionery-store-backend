// cart.js
async function showCart() {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const products = await getProducts();
    const productMap = {};
    for (let p of products) {
        productMap[p.id] = p;
    }

    let html = '<table border="1"><tr><th>Название</th><th>Количество</th><th>Цена</th><th></th></tr>';
    let total = 0;
    cart.forEach((item, idx) => {
        const p = productMap[item.product_id];
        if (p) {
            const cost = p.price * item.quantity;
            total += cost;
            html += `<tr>
                <td>${p.name}</td>
                <td><input type="number" value="${item.quantity}" onchange="updateQuantity(${idx}, this.value)"></td>
                <td>${cost}</td>
                <td><button onclick="removeFromCart(${idx})">Удалить</button></td>
            </tr>`;
        }
    });
    html += `<tr><td colspan="2">Итого:</td><td>${total}</td><td></td></tr>`;
    html += '</table>';
    document.getElementById('cartList').innerHTML = html;
}

function updateQuantity(index, newQty) {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    newQty = parseInt(newQty);
    if (newQty > 0) {
        cart[index].quantity = newQty;
    } else {
        cart.splice(index, 1);
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    showCart();
}

function removeFromCart(index) {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    showCart();
}

function goToCheckout() {
    window.location.href = '/checkout.html';
}