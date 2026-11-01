import axios from "axios";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("skillmesh_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const errorText = (e) => {
  const d = e?.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) return d.map((x) => x.msg).join(". ");
  return "Could not reach the server. Is the backend running?";
};

export default api;
