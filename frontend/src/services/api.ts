import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
  withCredentials: true, // required to send/receive the persistent session cookie
});

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401: try JWT refresh → session resume → redirect to login
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      // 1. Try JWT refresh token
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post("/api/auth/token/refresh/", { refresh });
          localStorage.setItem("access_token", data.access);
          original.headers.Authorization = `Bearer ${data.access}`;
          return api(original);
        } catch {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
      }

      // 2. Try session resume via persistent cookie (no Lichess OAuth needed)
      try {
        const { data } = await axios.post(
          "/api/auth/session/resume/",
          {},
          { withCredentials: true }
        );
        localStorage.setItem("access_token", data.access);
        localStorage.setItem("refresh_token", data.refresh);
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
