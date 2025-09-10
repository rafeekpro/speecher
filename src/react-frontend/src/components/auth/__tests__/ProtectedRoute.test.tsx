import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ProtectedRoute } from '../ProtectedRoute';
import { AuthProvider } from '../../../contexts/AuthContext';
import { authService } from '../../../services/authService';

// Mock authService
jest.mock('../../../services/authService');
const mockedAuthService = authService as jest.Mocked<typeof authService>;

// Mock react-router-dom Navigate
jest.mock('react-router-dom', () => ({
  MemoryRouter: ({ children }: any) => <div>{children}</div>,
  Route: ({ children }: any) => <div>{children}</div>,
  Routes: ({ children }: any) => <div>{children}</div>,
  Navigate: ({ to }: { to: string }) => <div>Redirected to {to}</div>
}));

describe('ProtectedRoute', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const ProtectedContent = () => <div>Protected Content</div>;
  const LoginPage = () => <div>Login Page</div>;

  const renderWithRouter = (
    isAuthenticated: boolean,
    loading: boolean = false,
    redirectTo: string = '/login'
  ) => {
    mockedAuthService.isAuthenticated.mockReturnValue(isAuthenticated);
    mockedAuthService.getCurrentUser.mockReturnValue(
      isAuthenticated ? { id: '123', email: 'test@example.com' } : null
    );

    // Mock loading state
    if (loading) {
      jest.spyOn(React, 'useContext').mockImplementationOnce(() => ({
        loading: true,
        isAuthenticated: false,
        user: null,
        login: jest.fn(),
        register: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn()
      }));
    }

    return render(
      <MemoryRouter initialEntries={['/protected']}>
        <AuthProvider>
          <Routes>
            <Route
              path="/protected"
              element={
                <ProtectedRoute redirectTo={redirectTo}>
                  <ProtectedContent />
                </ProtectedRoute>
              }
            />
            <Route path="/login" element={<LoginPage />} />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );
  };

  it('should render protected content when authenticated', async () => {
    renderWithRouter(true);
    
    expect(await screen.findByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByText(/Redirected to/)).not.toBeInTheDocument();
  });

  it('should redirect to login when not authenticated', async () => {
    renderWithRouter(false);
    
    expect(await screen.findByText('Redirected to /login')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should show loading state while checking authentication', () => {
    renderWithRouter(false, true);
    
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    expect(screen.queryByText(/Redirected to/)).not.toBeInTheDocument();
  });

  it('should redirect to custom path when specified', async () => {
    renderWithRouter(false, false, '/custom-login');
    
    expect(await screen.findByText('Redirected to /custom-login')).toBeInTheDocument();
  });

  it('should render multiple children when authenticated', async () => {
    mockedAuthService.isAuthenticated.mockReturnValue(true);
    mockedAuthService.getCurrentUser.mockReturnValue({
      id: '123',
      email: 'test@example.com'
    });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <AuthProvider>
          <Routes>
            <Route
              path="/protected"
              element={
                <ProtectedRoute>
                  <div>Child 1</div>
                  <div>Child 2</div>
                  <div>Child 3</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );
    
    expect(await screen.findByText('Child 1')).toBeInTheDocument();
    expect(screen.getByText('Child 2')).toBeInTheDocument();
    expect(screen.getByText('Child 3')).toBeInTheDocument();
  });

  it('should handle authentication status change', async () => {
    const { rerender } = renderWithRouter(false);
    
    // Initially not authenticated
    expect(await screen.findByText('Redirected to /login')).toBeInTheDocument();
    
    // Change to authenticated
    mockedAuthService.isAuthenticated.mockReturnValue(true);
    mockedAuthService.getCurrentUser.mockReturnValue({
      id: '123',
      email: 'test@example.com'
    });
    
    rerender(
      <MemoryRouter initialEntries={['/protected']}>
        <AuthProvider>
          <Routes>
            <Route
              path="/protected"
              element={
                <ProtectedRoute>
                  <ProtectedContent />
                </ProtectedRoute>
              }
            />
          </Routes>
        </AuthProvider>
      </MemoryRouter>
    );
    
    expect(await screen.findByText('Protected Content')).toBeInTheDocument();
  });
});