import api from "./api";
import type {
  Product,
  ProductCreate,
  ProductUpdate,
  Paginated,
} from "../types";

export const productService = {
  list: async (skip = 0, limit = 20): Promise<Paginated<Product>> => {
    const { data } = await api.get("/products", { params: { skip, limit } });
    return data;
  },

  create: async (payload: ProductCreate): Promise<Product> => {
    const { data } = await api.post("/products", payload);
    return data;
  },

  update: async (id: number, payload: ProductUpdate): Promise<Product> => {
    const { data } = await api.patch(`/products/${id}`, payload);
    return data;
  },

  remove: async (id: number): Promise<void> => {
    await api.delete(`/products/${id}`);
  },
};
