import api from "./api";
import type { Dashboard } from "../types";

export const dashboardService = {
  get: async (): Promise<Dashboard> => {
    const { data } = await api.get("/api/v1/dashboard");
    return data;
  },
};
