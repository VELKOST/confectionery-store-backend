// frontend/js/payments.js

async function createPayment(paymentData) {
    return apiPost('/payments', paymentData);
}

async function getPayment(paymentId) {
    return apiGet(`/payments/${paymentId}`);
}
