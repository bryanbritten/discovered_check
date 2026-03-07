import api from "./api";
import type { AuthTokens, User } from "../types";

const LICHESS_CLIENT_ID =
  (import.meta.env.VITE_LICHESS_CLIENT_ID as string | undefined);
const OAUTH_REDIRECT_URI =
  (import.meta.env.VITE_OAUTH_REDIRECT_URI as string | undefined) ??
  `${window.location.origin}/auth/callback`;

// ─── PKCE helpers ─────────────────────────────────────────────────────────────

function generateCodeVerifier(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "");
}

async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const digest = await crypto.subtle.digest("SHA-256", data);
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "");
}

// ─── Public API ───────────────────────────────────────────────────────────────

export async function initiateOAuth(): Promise<void> {
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);
  const state = crypto.randomUUID();

  sessionStorage.setItem("lichess_code_verifier", codeVerifier);
  sessionStorage.setItem("lichess_oauth_state", state);

  const params = new URLSearchParams({
    response_type: "code",
    client_id: LICHESS_CLIENT_ID,
    redirect_uri: OAUTH_REDIRECT_URI,
    scope: "preference:read",
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
    state,
  });

  window.location.href = `https://lichess.org/oauth?${params.toString()}`;
}

export async function exchangeOAuthCode(
  code: string,
  state: string
): Promise<{ tokens: AuthTokens; user: User }> {
  const storedState = sessionStorage.getItem("lichess_oauth_state");
  if (state !== storedState) {
    throw new Error("OAuth state mismatch — possible CSRF attack.");
  }

  const codeVerifier = sessionStorage.getItem("lichess_code_verifier");
  if (!codeVerifier) {
    throw new Error("Missing PKCE code verifier.");
  }

  const { data } = await api.post<AuthTokens & { user: User }>("/auth/lichess/", {
    code,
    code_verifier: codeVerifier,
    redirect_uri: OAUTH_REDIRECT_URI,
  });

  sessionStorage.removeItem("lichess_code_verifier");
  sessionStorage.removeItem("lichess_oauth_state");

  return { tokens: { access: data.access, refresh: data.refresh }, user: data.user };
}

export function storeTokens(tokens: AuthTokens): void {
  localStorage.setItem("access_token", tokens.access);
  localStorage.setItem("refresh_token", tokens.refresh);
}

export function clearTokens(): void {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem("access_token");
}

export async function fetchCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/auth/me/");
  return data;
}
