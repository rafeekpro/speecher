import { tokenStorage } from '../tokenStorage';

describe('tokenStorage', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
    jest.clearAllMocks();
  });

  describe('setAccessToken', () => {
    it('should store access token in localStorage', () => {
      const token = 'test-access-token-123';
      tokenStorage.setAccessToken(token);
      
      expect(localStorage.getItem('accessToken')).toBe(token);
    });

    it('should handle null token by removing from storage', () => {
      localStorage.setItem('accessToken', 'existing-token');
      tokenStorage.setAccessToken(null);
      
      expect(localStorage.getItem('accessToken')).toBeNull();
    });
  });

  describe('getAccessToken', () => {
    it('should retrieve access token from localStorage', () => {
      const token = 'test-access-token-456';
      localStorage.setItem('accessToken', token);
      
      const result = tokenStorage.getAccessToken();
      expect(result).toBe(token);
    });

    it('should return null when no token exists', () => {
      const result = tokenStorage.getAccessToken();
      expect(result).toBeNull();
    });
  });

  describe('setRefreshToken', () => {
    it('should store refresh token in localStorage', () => {
      const token = 'test-refresh-token-789';
      tokenStorage.setRefreshToken(token);
      
      expect(localStorage.getItem('refreshToken')).toBe(token);
    });

    it('should handle null token by removing from storage', () => {
      localStorage.setItem('refreshToken', 'existing-refresh');
      tokenStorage.setRefreshToken(null);
      
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });
  });

  describe('getRefreshToken', () => {
    it('should retrieve refresh token from localStorage', () => {
      const token = 'test-refresh-token-000';
      localStorage.setItem('refreshToken', token);
      
      const result = tokenStorage.getRefreshToken();
      expect(result).toBe(token);
    });

    it('should return null when no refresh token exists', () => {
      const result = tokenStorage.getRefreshToken();
      expect(result).toBeNull();
    });
  });

  describe('clearTokens', () => {
    it('should remove both tokens from localStorage', () => {
      localStorage.setItem('accessToken', 'access-123');
      localStorage.setItem('refreshToken', 'refresh-456');
      
      tokenStorage.clearTokens();
      
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });

    it('should not throw error when tokens don\'t exist', () => {
      expect(() => tokenStorage.clearTokens()).not.toThrow();
    });
  });

  describe('isTokenExpired', () => {
    it('should return true for expired token', () => {
      // Token expired 1 hour ago
      const expiredToken = createMockJWT(Date.now() / 1000 - 3600);
      
      expect(tokenStorage.isTokenExpired(expiredToken)).toBe(true);
    });

    it('should return false for valid token', () => {
      // Token expires in 1 hour
      const validToken = createMockJWT(Date.now() / 1000 + 3600);
      
      expect(tokenStorage.isTokenExpired(validToken)).toBe(false);
    });

    it('should return true for null token', () => {
      expect(tokenStorage.isTokenExpired(null)).toBe(true);
    });

    it('should return true for invalid token format', () => {
      expect(tokenStorage.isTokenExpired('invalid-token')).toBe(true);
    });

    it('should consider token expiring within buffer time as expired', () => {
      // Token expires in 30 seconds (within 60 second buffer)
      const soonToExpireToken = createMockJWT(Date.now() / 1000 + 30);
      
      expect(tokenStorage.isTokenExpired(soonToExpireToken, 60)).toBe(true);
    });
  });

  describe('getTokenPayload', () => {
    it('should decode and return token payload', () => {
      const payload = { sub: 'user123', email: 'test@example.com', exp: Date.now() / 1000 + 3600 };
      const token = createMockJWT(payload.exp, payload);
      
      const result = tokenStorage.getTokenPayload(token);
      expect(result).toEqual(payload);
    });

    it('should return null for invalid token', () => {
      expect(tokenStorage.getTokenPayload('invalid')).toBeNull();
    });

    it('should return null for null token', () => {
      expect(tokenStorage.getTokenPayload(null)).toBeNull();
    });
  });
});

// Helper function to create mock JWT tokens
function createMockJWT(exp: number, payload: any = {}): string {
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const body = btoa(JSON.stringify({ ...payload, exp }));
  const signature = 'mock-signature';
  return `${header}.${body}.${signature}`;
}