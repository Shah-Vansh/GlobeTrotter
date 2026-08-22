/**
 * configs/api.js
 * -----------------------------------------------------------------------
 * Central axios instance used by every page/slice to talk to the Flask
 * backend. Responsible for:
 *   1. Prefixing every request with VITE_BASE_URL.
 *   2. Attaching the JWT access token (from localStorage) to every request.
 *   3. Silently refreshing an expired access token (using the refresh
 *      token) and retrying the original request exactly once.
 *   4. Logging the user out (clearing tokens) if the refresh itself fails.
 *
 * Backend response envelope (see server/app/utils/responses.py):
 *   success: { success: true,  message: string, data: any }
 *   error:   { success: false, message: string, errors: any }
 * Callers can therefore always do `const { data } = await api.get(...)`
 * and read `data.data` for the payload / `data.message` for the toast text.
 */
import axios from "axios";

const ACCESS_TOKEN_KEY = "gt_access_token";
const REFRESH_TOKEN_KEY = "gt_refresh_token";

export const tokenStorage = {
  getAccessToken: () => localStorage.getItem(ACCESS_TOKEN_KEY),
  getRefreshToken: () => localStorage.getItem(REFRESH_TOKEN_KEY),
  setTokens: (access, refresh) => {
    if (access) localStorage.setItem(ACCESS_TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  },
  clearTokens: () => {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },
};

const api = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
});

// --- Attach the access token to every outgoing request ---
api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Queue of requests waiting on an in-flight token refresh so we don't
// fire /auth/refresh multiple times in parallel.
let isRefreshing = false;
let pendingQueue = [];

const resolveQueue = (error, token = null) => {
  pendingQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token);
  });
  pendingQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error.response?.status;

    // Don't try to refresh on the auth endpoints themselves.
    const isAuthRoute = originalRequest?.url?.includes("/api/auth/");

    if (status === 401 && !originalRequest._retry && !isAuthRoute) {
      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) {
        tokenStorage.clearTokens();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Wait for the in-flight refresh to finish, then retry.
        return new Promise((resolve, reject) => {
          pendingQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { data } = await axios.post(
          `${import.meta.env.VITE_BASE_URL}/api/auth/refresh`,
          {},
          { headers: { Authorization: `Bearer ${refreshToken}` } }
        );
        const newAccessToken = data?.data?.access_token;
        tokenStorage.setTokens(newAccessToken, null);
        resolveQueue(null, newAccessToken);
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        resolveQueue(refreshError, null);
        tokenStorage.clearTokens();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;
