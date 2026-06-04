import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "/",
  headers: { "Content-Type": "application/json" },
  timeout: 10_000,
});

// Normaliza todos os erros para um objeto Error com mensagem legível
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message: string =
      error.response?.data?.detail ?? error.message ?? "Erro desconhecido";
    return Promise.reject(new Error(message));
  }
);

export default api;
