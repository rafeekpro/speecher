import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { tokenStorage } from './tokenStorage';
import { authService } from '../services/authService';

interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

export const setupAxiosInterceptors = () => {
  // Request interceptor to add auth token
  const requestInterceptor = axios.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = tokenStorage.getAccessToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // Response interceptor to handle 401 errors
  const responseInterceptor = axios.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalRequest = error.config as CustomAxiosRequestConfig;
      
      if (!originalRequest) {
        return Promise.reject(error);
      }

      // If we get a 401 and haven't already tried to refresh
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;
        
        const refreshToken = tokenStorage.getRefreshToken();
        
        if (refreshToken) {
          try {
            // Try to refresh the token
            await authService.refreshToken();
            
            // Get the new access token
            const newToken = tokenStorage.getAccessToken();
            
            // Update the Authorization header
            if (newToken) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
            }
            
            // Retry the original request
            return axios.request(originalRequest);
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            tokenStorage.clearTokens();
            // The app should handle this by checking isAuthenticated
            return Promise.reject(error);
          }
        } else {
          // No refresh token available
          tokenStorage.clearTokens();
        }
      }
      
      return Promise.reject(error);
    }
  );

  // Return cleanup function
  return () => {
    axios.interceptors.request.eject(requestInterceptor);
    axios.interceptors.response.eject(responseInterceptor);
  };
};