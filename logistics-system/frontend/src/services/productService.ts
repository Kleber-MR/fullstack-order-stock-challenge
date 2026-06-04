import api from "./api";
import type {
  Product,
  ProductCreate,
  ProductUpdate,
  ProductLowStock,
  Paginated,
} from "../types";

const BASE = "/api/v1/products";

export const productService = {
  list: async (
    skip = 0,
    limit = 20,
    params?: {
      search?: string;
      min_price?: number;
      max_price?: number;
      in_stock?: boolean;
    }
  ): Promise<Paginated<Product>> => {
    const { data } = await api.get(BASE, {
      params: { skip, limit, ...params },
    });
    return data;
  },

  getById: async (id: number): Promise<Product> => {
    const { data } = await api.get(`${BASE}/${id}`);
    return data;
  },

  create: async (payload: ProductCreate): Promise<Product> => {
    const { data } = await api.post(BASE, payload);
    return data;
  },

  update: async (id: number, payload: ProductUpdate): Promise<Product> => {
    const { data } = await api.patch(`${BASE}/${id}`, payload);
    return data;
  },

  remove: async (id: number): Promise<void> => {
    await api.delete(`${BASE}/${id}`);
  },

  lowStock: async (threshold = 10): Promise<ProductLowStock[]> => {
    const { data } = await api.get(`${BASE}/low-stock`, {
      params: { threshold },
    });
    return data;
  },
};
