"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { useRouter } from "next/navigation";
import { api, login as apiLogin, setToken } from "./api";
import { User } from "./types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    api
      .get<User>("/auth/me")
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const token = await apiLogin(email, password);
    setToken(token);
    const me = await api.get<User>("/auth/me");
    setUser(me);
    router.push("/dashboard");
  }

  async function signup(email: string, password: string, fullName?: string) {
    await api.post("/auth/signup", { email, password, full_name: fullName });
    await login(email, password);
  }

  function logout() {
    setToken(null);
    setUser(null);
    router.push("/login");
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout }}>{children}</AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
