import { api } from "./api";

const auth = (token) => ({ headers: { Authorization: `Bearer ${token}` } });
export const startCheckout = async (token) => (await api.post("/payments/checkout", {}, auth(token))).data;
export const verifyTestPayment = async (token, paymentId) => (await api.post(`/payments/${paymentId}/verify-test`, {}, auth(token))).data;
export const verifyRazorpayPayment = async (token, paymentId, response) => (await api.post(`/payments/${paymentId}/verify`, { razorpay_payment_id: response.razorpay_payment_id, razorpay_signature: response.razorpay_signature }, auth(token))).data;
export const startQuickCheckout = async (token, productId) => (await api.post("/payments/quick-checkout", { product_id: productId, quantity: 1 }, auth(token))).data;
