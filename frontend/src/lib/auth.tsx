import { createContext, ReactNode, useContext, useEffect, useState } from "react";
import { apiFetch, setUnauthorizedHandler } from "./api";
import { AuthUser } from "../types";

type AuthContextValue = {
  user: AuthUser | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<void>;
  changePassword: (currentPassword: string | null, newPassword: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

async function readError(response: Response, fallback: string): Promise<string> {
  try {
    const body = await response.json();
    return typeof body.detail === "string" ? body.detail : fallback;
  } catch {
    return fallback;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
  };

  useEffect(() => {
    setUnauthorizedHandler(logout);
    const token = localStorage.getItem("token");
    if (!token) {
      setLoading(false);
      return;
    }
    apiFetch("/auth/me")
      .then((response) => (response.ok ? response.json() : Promise.reject()))
      .then((body: AuthUser) => setUser(body))
      .catch(() => localStorage.removeItem("token"))
      .finally(() => setLoading(false));
  }, []);

  const handleAuthResponse = async (response: Response, fallback: string) => {
    if (!response.ok) throw new Error(await readError(response, fallback));
    const body = await response.json();
    localStorage.setItem("token", body.access_token);
    setUser(body.user);
  };

  const login = async (email: string, password: string) => {
    setError(null);
    try {
      await handleAuthResponse(
        await apiFetch("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
        "Pogrešan email ili lozinka.",
      );
    } catch (err) {
      setError((err as Error).message);
      throw err;
    }
  };

  const signup = async (name: string, email: string, password: string) => {
    setError(null);
    try {
      await handleAuthResponse(
        await apiFetch("/auth/signup", { method: "POST", body: JSON.stringify({ name, email, password }) }),
        "Nalog nije napravljen.",
      );
    } catch (err) {
      setError((err as Error).message);
      throw err;
    }
  };

  const loginWithGoogle = async (idToken: string) => {
    setError(null);
    try {
      await handleAuthResponse(
        await apiFetch("/auth/google", { method: "POST", body: JSON.stringify({ id_token: idToken }) }),
        "Prijava preko Google naloga nije uspela.",
      );
    } catch (err) {
      setError((err as Error).message);
      throw err;
    }
  };

  const changePassword = async (currentPassword: string | null, newPassword: string) => {
    const response = await apiFetch("/auth/change-password", {
      method: "PUT",
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
    if (!response.ok) throw new Error(await readError(response, "Lozinka nije promenjena."));
    setUser(await response.json());
  };

  const value: AuthContextValue = {
    user,
    loading,
    error,
    login,
    signup,
    loginWithGoogle,
    changePassword,
    logout,
    clearError: () => setError(null),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth mora biti korišćen unutar AuthProvider-a.");
  return context;
}
