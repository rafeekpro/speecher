import axios from 'axios';
import { tokenStorage } from '../utils/tokenStorage';

interface RegisterData {
  email: string;
  password: string;
  name: string;
}

interface LoginData {
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

interface User {
  id: string;
  email: string;
  name?: string;
}

class AuthService {
  async register(data: RegisterData): Promise<any> {
    try {
      const response = await axios.post('/api/auth/register', data);
      return response.data;
    } catch (error: any) {
      if (error?.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Registration failed');
    }
  }

  async login(credentials: LoginData): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>('/api/auth/login', credentials);
      const { access_token, refresh_token } = response.data;
      
      tokenStorage.setAccessToken(access_token);
      if (refresh_token) {
        tokenStorage.setRefreshToken(refresh_token);
      }
      
      return response.data;
    } catch (error: any) {
      if (error?.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Login failed');
    }
  }

  async logout(): Promise<void> {
    try {
      const token = tokenStorage.getAccessToken();
      if (token) {
        await axios.post('/api/auth/logout', {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
    } catch (error) {
      // Log error but continue with logout
      console.error('Logout API call failed:', error);
    } finally {
      tokenStorage.clearTokens();
    }
  }

  async refreshToken(): Promise<AuthResponse> {
    const refreshToken = tokenStorage.getRefreshToken();
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post<AuthResponse>('/api/auth/refresh', {
        refresh_token: refreshToken
      });
      
      const { access_token } = response.data;
      tokenStorage.setAccessToken(access_token);
      
      return response.data;
    } catch (error: any) {
      tokenStorage.clearTokens();
      if (error?.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw new Error('Token refresh failed');
    }
  }

  getCurrentUser(): User | null {
    const token = tokenStorage.getAccessToken();
    if (!token) return null;

    const payload = tokenStorage.getTokenPayload(token);
    if (!payload) return null;

    return {
      id: payload.sub || '',
      email: payload.email || '',
      name: payload.name
    };
  }

  isAuthenticated(): boolean {
    const token = tokenStorage.getAccessToken();
    if (!token) return false;
    
    return !tokenStorage.isTokenExpired(token);
  }
}

export const authService = new AuthService();