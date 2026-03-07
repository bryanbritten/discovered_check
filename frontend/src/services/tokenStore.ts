/**
 * In-memory JWT store.
 *
 * Tokens live only for the lifetime of the current page. On every fresh page
 * load AuthContext calls session/resume/ to rehydrate them from the httpOnly
 * dc_session cookie — so they never need to touch localStorage or the DOM.
 */

let _accessToken: string | null = null;
let _refreshToken: string | null = null;

export function getAccessToken(): string | null {
  return _accessToken;
}

export function getRefreshToken(): string | null {
  return _refreshToken;
}

export function setTokens(access: string, refresh: string): void {
  _accessToken = access;
  _refreshToken = refresh;
}

export function clearTokens(): void {
  _accessToken = null;
  _refreshToken = null;
}

export function hasAccessToken(): boolean {
  return _accessToken !== null;
}
