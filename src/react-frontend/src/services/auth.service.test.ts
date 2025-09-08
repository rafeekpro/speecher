import axios from 'axios';
import { AuthService } from './auth.service';
import { LoginRequest, RegisterRequest } from '../types/auth.types';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('AuthService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('login', () => {
    it('should login successfully and store tokens', async () => {
      const loginData: LoginRequest = {
        email: 'test@example.com',
        password: 'TestPass123!'
      };

      const mockResponse = {
        data: {
          accessToken: 'mock-access-token',
          refreshToken: 'mock-refresh-token',
          tokenType: 'Bearer',
          user: {
            id: '123',
            email: 'test@example.com',
            fullName: 'Test User',
            role: 'user',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        }
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const result = await AuthService.login(loginData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/login', loginData);
      expect(result).toEqual(mockResponse.data);
      expect(localStorage.getItem('accessToken')).toBe('mock-access-token');
      expect(localStorage.getItem('refreshToken')).toBe('mock-refresh-token');
    });

    it('should handle login error', async () => {
      const loginData: LoginRequest = {
        email: 'test@example.com',
        password: 'wrong-password'
      };

      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { message: 'Invalid credentials' }
        }
      });

      await expect(AuthService.login(loginData)).rejects.toThrow('Invalid credentials');
      expect(localStorage.getItem('accessToken')).toBeNull();
    });
  });

  describe('register', () => {
    it('should register successfully', async () => {
      const registerData: RegisterRequest = {
        email: 'new@example.com',
        password: 'NewPass123!',
        fullName: 'New User'
      };

      const mockResponse = {
        data: {
          accessToken: 'mock-access-token',
          refreshToken: 'mock-refresh-token',
          tokenType: 'Bearer',
          user: {
            id: '456',
            email: 'new@example.com',
            fullName: 'New User',
            role: 'user',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
          }
        }
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const result = await AuthService.register(registerData);

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/register', registerData);
      expect(result).toEqual(mockResponse.data);
      expect(localStorage.getItem('accessToken')).toBe('mock-access-token');
    });

    it('should handle registration error for duplicate email', async () => {
      const registerData: RegisterRequest = {
        email: 'existing@example.com',
        password: 'Pass123!',
        fullName: 'Existing User'
      };

      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 409,
          data: { message: 'Email already registered' }
        }
      });

      await expect(AuthService.register(registerData)).rejects.toThrow('Email already registered');
    });
  });

  describe('logout', () => {
    it('should clear tokens and call logout endpoint', async () => {
      localStorage.setItem('accessToken', 'token-to-remove');
      localStorage.setItem('refreshToken', 'refresh-to-remove');

      mockedAxios.post.mockResolvedValueOnce({ data: { message: 'Logged out' } });

      await AuthService.logout();

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/logout');
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });
  });

  describe('refreshToken', () => {
    it('should refresh tokens successfully', async () => {
      localStorage.setItem('refreshToken', 'old-refresh-token');

      const mockResponse = {
        data: {
          accessToken: 'new-access-token',
          refreshToken: 'new-refresh-token',
          tokenType: 'Bearer'
        }
      };

      mockedAxios.post.mockResolvedValueOnce(mockResponse);

      const result = await AuthService.refreshToken();

      expect(mockedAxios.post).toHaveBeenCalledWith('/api/auth/refresh', {
        refreshToken: 'old-refresh-token'
      });
      expect(result).toEqual(mockResponse.data);
      expect(localStorage.getItem('accessToken')).toBe('new-access-token');
      expect(localStorage.getItem('refreshToken')).toBe('new-refresh-token');
    });

    it('should handle refresh token error', async () => {
      localStorage.setItem('refreshToken', 'invalid-token');

      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { message: 'Invalid refresh token' }
        }
      });

      await expect(AuthService.refreshToken()).rejects.toThrow('Invalid refresh token');
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(localStorage.getItem('refreshToken')).toBeNull();
    });
  });

  describe('getCurrentUser', () => {
    it('should get current user successfully', async () => {
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'user',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };

      mockedAxios.get.mockResolvedValueOnce({ data: mockUser });

      const result = await AuthService.getCurrentUser();

      expect(mockedAxios.get).toHaveBeenCalledWith('/api/users/profile');
      expect(result).toEqual(mockUser);
    });

    it('should return null when not authenticated', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { message: 'Not authenticated' }
        }
      });

      const result = await AuthService.getCurrentUser();

      expect(result).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true when access token exists', () => {
      localStorage.setItem('accessToken', 'valid-token');
      expect(AuthService.isAuthenticated()).toBe(true);
    });

    it('should return false when no access token', () => {
      expect(AuthService.isAuthenticated()).toBe(false);
    });
  });

  describe('getAuthHeader', () => {
    it('should return authorization header when token exists', () => {
      localStorage.setItem('accessToken', 'my-token');
      expect(AuthService.getAuthHeader()).toEqual({
        Authorization: 'Bearer my-token'
      });
    });

    it('should return empty object when no token', () => {
      expect(AuthService.getAuthHeader()).toEqual({});
    });
  });
});