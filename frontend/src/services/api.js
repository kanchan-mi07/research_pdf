import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    const url = error.config?.url || "";
    const isAuthCall =
      url.includes("/auth/login") || url.includes("/auth/signup");

    // Expired token: log out. Wrong password on the login page should NOT redirect.
    if (error.response?.status === 401 && !isAuthCall) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// Turns any backend error into a readable string
export function getErrorMessage(error) {
  const detail = error.response?.data?.detail;

  if (typeof detail === "string") return detail;

  // FastAPI validation errors (422) come as an array
  if (Array.isArray(detail) && detail.length > 0) {
    return detail[0].msg?.replace("Value error, ", "") || "Invalid input";
  }

  if (!error.response)
    return "Cannot reach the server. Is the backend running?";
  return "Something went wrong. Please try again.";
}

export default api;
