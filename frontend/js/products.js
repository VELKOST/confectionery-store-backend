// frontend/js/products.js
async function getProducts() {
    return apiGet('/products/');
}

function addToCart(productId) {
    let cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const idx = cart.findIndex(i => i.product_id === productId);
    if (idx >= 0) {
        cart[idx].quantity += 1;
    } else {
        cart.push({product_id: productId, quantity: 1});
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    alert('Товар добавлен в корзину');
}
