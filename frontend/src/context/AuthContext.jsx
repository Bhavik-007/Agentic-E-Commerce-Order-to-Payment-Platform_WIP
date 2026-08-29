import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => JSON.parse(localStorage.getItem("shoppilot_session") ?? "null"));

  useEffect(() => {
    if (session) localStorage.setItem("shoppilot_session", JSON.stringify(session));
    else localStorage.removeItem("shoppilot_session");
  }, [session]);

  const value = useMemo(() => ({
    user: session?.user ?? null,
    token: session?.access_token ?? null,
    authenticated: Boolean(session?.access_token),
    async signIn(payload) { const { data } = await api.post("/auth/login", payload); setSession(data); },
    async register(payload) { const { data } = await api.post("/auth/register", payload); setSession(data); },
    signOut() { setSession(null); },
  }), [session]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider.");
  return context;
}
