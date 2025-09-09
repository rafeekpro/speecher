import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { LoginForm, RegisterForm, ProtectedRoute } from './components/auth';
import { useAuth } from './hooks/useAuth';
import { setupAxiosInterceptors } from './utils/axiosInterceptors';

// Example Dashboard component (protected)
const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  
  return (
    <div>
      <h1>Dashboard</h1>
      <p>Welcome, {user?.email}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

// Example Home component (public)
const Home: React.FC = () => {
  const { isAuthenticated } = useAuth();
  
  return (
    <div>
      <h1>Home</h1>
      {isAuthenticated ? (
        <p>You are logged in. <Link to="/dashboard">Go to Dashboard</Link></p>
      ) : (
        <p>Please <Link to="/login">login</Link> or <Link to="/register">register</Link>.</p>
      )}
    </div>
  );
};

// Login page
const LoginPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  
  if (isAuthenticated) {
    window.location.href = '/dashboard';
    return null;
  }
  
  return (
    <div style={{ maxWidth: '400px', margin: '2rem auto' }}>
      <h1>Login</h1>
      <LoginForm onSuccess={() => window.location.href = '/dashboard'} />
      <p>Don't have an account? <Link to="/register">Register</Link></p>
    </div>
  );
};

// Register page
const RegisterPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  
  if (isAuthenticated) {
    window.location.href = '/dashboard';
    return null;
  }
  
  return (
    <div style={{ maxWidth: '400px', margin: '2rem auto' }}>
      <h1>Register</h1>
      <RegisterForm onSuccess={() => window.location.href = '/dashboard'} />
      <p>Already have an account? <Link to="/login">Login</Link></p>
    </div>
  );
};

// Main App component
function App() {
  useEffect(() => {
    // Set up axios interceptors for automatic token management
    const cleanup = setupAxiosInterceptors();
    
    // Cleanup interceptors on unmount
    return cleanup;
  }, []);

  return (
    <AuthProvider>
      <Router>
        <nav style={{ padding: '1rem', backgroundColor: '#f0f0f0' }}>
          <Link to="/" style={{ marginRight: '1rem' }}>Home</Link>
          <Link to="/dashboard" style={{ marginRight: '1rem' }}>Dashboard</Link>
          <Link to="/login" style={{ marginRight: '1rem' }}>Login</Link>
          <Link to="/register">Register</Link>
        </nav>
        
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;

/**
 * USAGE NOTES:
 * 
 * 1. Wrap your app with AuthProvider at the root level
 * 2. Use ProtectedRoute to protect authenticated-only routes
 * 3. Use useAuth hook to access auth state and methods:
 *    - user: Current user object
 *    - isAuthenticated: Boolean auth status
 *    - loading: Loading state
 *    - login(credentials): Login method
 *    - register(data): Register method
 *    - logout(): Logout method
 *    - refreshToken(): Manual token refresh
 * 
 * 4. The system automatically:
 *    - Adds Authorization header to all axios requests
 *    - Refreshes tokens when they expire
 *    - Retries failed requests after token refresh
 *    - Clears tokens and redirects on auth failure
 * 
 * 5. Token storage:
 *    - Access token: Short-lived (30 minutes)
 *    - Refresh token: Long-lived
 *    - Both stored in localStorage (consider using httpOnly cookies in production)
 * 
 * 6. API Endpoints used:
 *    - POST /api/auth/register
 *    - POST /api/auth/login
 *    - POST /api/auth/refresh
 *    - POST /api/auth/logout
 */