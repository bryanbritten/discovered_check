import axios from "axios";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "./tokenStore";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // required to send/receive the persistent session cookie
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth endpoints are allowed to return 401 naturally — the interceptor must not
// attempt recovery for them or it causes infinite loops (e.g. session/resume/
// returning 401 → interceptor calls session/resume/ again → repeat).
const AUTH_ENDPOINTS = ["/auth/session/resume/", "/auth/token/refresh/", "/auth/lichess/"];

// On 401: try JWT refresh → session resume → redirect to login
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;
    const isAuthEndpoint = AUTH_ENDPOINTS.some((ep) => original.url?.includes(ep));

    if (error.response?.status === 401 && !original._retry && !isAuthEndpoint) {
      original._retry = true;

      // 1. Try JWT refresh token
      const refresh = getRefreshToken();
      if (refresh) {
        try {
          const { data } = await axios.post("/api/auth/token/refresh/", { refresh });
          setTokens(data.access, data.refresh ?? refresh);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          clearTokens();
        }
      }

      // 2. Try session resume via persistent cookie (no Lichess OAuth needed)
      try {
        const { data } = await axios.post(
          "/api/auth/session/resume/",
          {},
          { withCredentials: true }
        );
        setTokens(data.access, data.refresh);
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch {
        // Session invalid or expired — full login required
      }

      window.location.href = "/login";
    }

    return Promise.reject(error);
  }
);

export default api;
