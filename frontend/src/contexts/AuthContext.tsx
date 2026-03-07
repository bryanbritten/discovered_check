import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { User } from "../types";
import {
  clearTokens,
  fetchCurrentUser,
  isAuthenticated,
  resumeSession,
  serverLogout,
  storeTokens,
} from "../services/auth";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const init = async () => {
      // 1. If we have a JWT, try to use it directly.
      if (isAuthenticated()) {
        try {
          setUser(await fetchCurrentUser());
          return;
        } catch {
          clearTokens();
          // Fall through to session resume.
        }
      }

      // 2. No valid JWT — try the persistent session cookie. If the user has
      //    logged in before and their Lichess token is still valid, this will
      //    succeed and they won't need to go through OAuth again.
      const result = await resumeSession();
      if (result) {
        storeTokens(result.tokens);
        setUser(result.user);
      }
    };

    init().finally(() => setIsLoading(false));
  }, []);

  const logout = async () => {
    // Invalidate the session cookie on the server so the user must go through
    // OAuth again on their next visit.
    await serverLogout();
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, setUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
