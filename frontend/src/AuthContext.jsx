import { createContext, useContext, useEffect, useState } from "react";
import api from "./api";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!localStorage.getItem("skillmesh_token"));

  useEffect(() => {
    if (!localStorage.getItem("skillmesh_token")) return;
    api.get("/auth/me").then((r) => setUser(r.data)).catch(() => localStorage.removeItem("skillmesh_token")).finally(() => setLoading(false));
  }, []);

  const authenticate = async (path, body) => {
    const { data } = await api.post(path, body);
    localStorage.setItem("skillmesh_token", data.token);
    setUser(data.user);
    return data.user;
  };
  const logout = () => { localStorage.removeItem("skillmesh_token"); setUser(null); };

  return <Ctx.Provider value={{ user, setUser, loading, authenticate, logout }}>{children}</Ctx.Provider>;
}
