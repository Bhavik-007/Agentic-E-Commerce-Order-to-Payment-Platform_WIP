import { api } from "./api";

export async function getProducts(params = {}) {
  const { data } = await api.get("/products", { params });
  return data;
}
