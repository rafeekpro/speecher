const ACCESS_TOKEN_KEY = 'accessToken';
const REFRESH_TOKEN_KEY = 'refreshToken';

interface TokenPayload {
  sub?: string;
  email?: string;
  exp?: number;
  [key: string]: any;
}

export const tokenStorage = {
  setAccessToken(token: string | null): void {
    if (token === null) {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
    } else {
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
    }
  },

  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  },

  setRefreshToken(token: string | null): void {
    if (token === null) {
      localStorage.removeItem(REFRESH_TOKEN_KEY);
    } else {
      localStorage.setItem(REFRESH_TOKEN_KEY, token);
    }
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  },

  clearTokens(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  },

  isTokenExpired(token: string | null, bufferSeconds: number = 60): boolean {
    if (!token) return true;

    try {
      const payload = this.getTokenPayload(token);
      if (!payload || !payload.exp) return true;

      const now = Date.now() / 1000;
      return payload.exp < now + bufferSeconds;
    } catch {
      return true;
    }
  },

  getTokenPayload(token: string | null): TokenPayload | null {
    if (!token) return null;

    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;

      const payload = JSON.parse(atob(parts[1]));
      return payload;
    } catch {
      return null;
    }
  }
};