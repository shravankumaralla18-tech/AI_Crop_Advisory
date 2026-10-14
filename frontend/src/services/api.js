import axios from "axios";
import { API_URL, TOKEN_KEY } from "../utils/constants";

const api = axios.create({ baseURL: API_URL, timeout: 30000 });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const method = error.config?.method?.toUpperCase() || "REQUEST";
    const url = `${error.config?.baseURL || ""}${error.config?.url || ""}`;
    if (!error.response) {
      console.error(
        `[API] No response from ${method} ${url}. Check backend availability, network access, and whether CORS allows ${window.location.origin}.`,
        error
      );
    } else {
      console.error(`[API] HTTP ${error.response.status} from ${method} ${url}`, error.response.data);
    }

    const onAuthPage = ["/login", "/register"].includes(window.location.pathname);
    if (error.response?.status === 401 && !onAuthPage) {
      localStorage.removeItem(TOKEN_KEY);
      window.location.assign("/login");
    }
    return Promise.reject(error);
  }
);

export default api;
