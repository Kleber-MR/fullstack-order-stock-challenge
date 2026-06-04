import api from "./api";
import type { Order, OrderCreate, Paginated } from "../types";

export const orderService = {
  list: async (skip = 0, limit = 20): Promise<Paginated<Order>> => {
    const { data } = await api.get("/orders", { params: { skip, limit } });
    return data;
  },

  create: async (payload: OrderCreate): Promise<Order> => {
    const { data } = await api.post("/orders", payload);
    return data;
  },

  cancel: async (id: number): Promise<Order> => {
    const { data } = await api.patch(`/orders/${id}/cancel`);
    return data;
  },
};
