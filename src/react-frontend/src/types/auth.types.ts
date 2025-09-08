export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'admin' | 'user';
  createdAt: Date;
  updatedAt: Date;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  fullName: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
}

export interface AuthResponse extends AuthTokens {
  user: User;
}

export interface ApiError {
  message: string;
  status?: number;
  errors?: Record<string, string[]>;
}