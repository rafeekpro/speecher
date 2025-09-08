import axios, { AxiosError } from 'axios';
import { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  AuthTokens, 
  User,
  ApiError 
} from '../types/auth.types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

class AuthServiceClass {
  private readonly ACCESS_TOKEN_KEY = 'accessToken';
  private readonly REFRESH_TOKEN_KEY = 'refreshToken';

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>('/api/auth/login', credentials);
      this.storeTokens(response.data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await axios.post<AuthResponse>('/api/auth/register', userData);
      this.storeTokens(response.data);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout(): Promise<void> {
    try {
      await axios.post('/api/auth/logout');
    } finally {
      this.clearTokens();
    }
  }

  async refreshToken(): Promise<AuthTokens> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await axios.post<AuthTokens>('/api/auth/refresh', {
        refreshToken
      });
      this.storeTokens(response.data);
      return response.data;
    } catch (error) {
      this.clearTokens();
      throw this.handleError(error);
    }
  }

  async getCurrentUser(): Promise<User | null> {
    try {
      const response = await axios.get<User>('/api/users/profile');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        return null;
      }
      throw this.handleError(error);
    }
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  getAuthHeader(): Record<string, string> {
    const token = this.getAccessToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  private storeTokens(tokens: AuthTokens | AuthResponse): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, tokens.accessToken);
    localStorage.setItem(this.REFRESH_TOKEN_KEY, tokens.refreshToken);
  }

  private clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  private handleError(error: unknown): Error {
    if (axios.isAxiosError(error)) {
      const message = error.response?.data?.message || error.response?.data?.detail || 'An error occurred';
      return new Error(message);
    }
    return error instanceof Error ? error : new Error('Unknown error occurred');
  }
}

export const AuthService = new AuthServiceClass();

// Setup axios interceptors
axios.interceptors.request.use(
  (config) => {
    const token = AuthService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        await AuthService.refreshToken();
        return axios(originalRequest);
      } catch (refreshError) {
        // Redirect to login or handle as needed
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);