import api from "./api";
import type { Log, Paginated } from "../types";

export const logService = {
  list: async (
    skip = 0,
    limit = 50,
    params?: { entidade_tipo?: string }
  ): Promise<Paginated<Log>> => {
    const { data } = await api.get("/api/v1/logs", {
      params: { skip, limit, ...params },
    });
    return data;
  },
};
