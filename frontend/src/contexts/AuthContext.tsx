import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { User } from "../types";
import {
  clearTokens,
  resumeSession,
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
    // Tokens are in-memory only, so every page load starts fresh.
    // Attempt to rehydrate the session from the persistent httpOnly cookie.
    // If the cookie is absent or expired, the user is sent to the login page.
    resumeSession()
      .then((result) => {
        if (result) {
          storeTokens(result.tokens);
          setUser(result.user);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  const logout = async () => {
    // Soft logout: clear in-memory tokens and UI state but leave the
    // dc_session cookie intact. The next visit to /login will resume the
    // session silently without requiring Lichess re-authorization.
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
