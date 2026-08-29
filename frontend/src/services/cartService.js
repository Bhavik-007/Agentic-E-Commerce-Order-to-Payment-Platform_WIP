import { api } from "./api";

const config = (token) => ({ headers: { Authorization: `Bearer ${token}` } });
export const getCart = async (token) => (await api.get("/cart", config(token))).data;
export const addCartItem = async (token, productId) => (await api.post("/cart/items", { product_id: productId, quantity: 1 }, config(token))).data;
export const removeCartItem = async (token, itemId) => api.delete(`/cart/items/${itemId}`, config(token));
