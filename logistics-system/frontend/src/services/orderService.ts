import api from "./api";
import type { Order, OrderCreate, Paginated } from "../types";

const BASE = "/api/v1/orders";

export const orderService = {
  list: async (skip = 0, limit = 20): Promise<Paginated<Order>> => {
    const { data } = await api.get(BASE, { params: { skip, limit } });
    return data;
  },

  getById: async (id: number): Promise<Order> => {
    const { data } = await api.get(`${BASE}/${id}`);
    return data;
  },

  create: async (payload: OrderCreate): Promise<Order> => {
    const { data } = await api.post(BASE, payload);
    return data;
  },

  cancel: async (id: number): Promise<Order> => {
    const { data } = await api.patch(`${BASE}/${id}/cancel`);
    return data;
  },
};
