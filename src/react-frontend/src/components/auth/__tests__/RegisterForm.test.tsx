import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RegisterForm } from '../RegisterForm';
import { AuthProvider } from '../../../contexts/AuthContext';
import { authService } from '../../../services/authService';

// Mock authService
jest.mock('../../../services/authService');
const mockedAuthService = authService as jest.Mocked<typeof authService>;

describe('RegisterForm', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  const renderWithAuth = (component: React.ReactElement) => {
    return render(
      <AuthProvider>
        {component}
      </AuthProvider>
    );
  };

  it('should render registration form with all fields', () => {
    renderWithAuth(<RegisterForm />);
    
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /register/i })).toBeInTheDocument();
  });

  it('should show validation errors for empty fields', async () => {
    renderWithAuth(<RegisterForm />);
    
    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getAllByText(/password is required/i)[0]).toBeInTheDocument();
    });
  });

  it('should validate email format', async () => {
    renderWithAuth(<RegisterForm />);
    
    const emailInput = screen.getByLabelText(/email/i);
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    
    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/invalid email format/i)).toBeInTheDocument();
    });
  });

  it('should validate password minimum length of 8 characters', async () => {
    renderWithAuth(<RegisterForm />);
    
    const passwordInput = screen.getByLabelText(/^password$/i);
    fireEvent.change(passwordInput, { target: { value: 'short' } });
    
    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });

  it('should validate password confirmation match', async () => {
    renderWithAuth(<RegisterForm />);
    
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password456' } });
    
    const submitButton = screen.getByRole('button', { name: /register/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  it('should successfully submit form with valid data', async () => {
    mockedAuthService.register.mockResolvedValue({
      message: 'User registered successfully',
      user: { id: '123', email: 'test@example.com', name: 'Test User' }
    });
    mockedAuthService.login.mockResolvedValue({
      access_token: 'token',
      refresh_token: 'refresh',
      token_type: 'Bearer'
    });
    mockedAuthService.getCurrentUser.mockReturnValue({
      id: '123',
      email: 'test@example.com',
      name: 'Test User'
    });
    
    const onSuccess = jest.fn();
    renderWithAuth(<RegisterForm onSuccess={onSuccess} />);
    
    const nameInput = screen.getByLabelText(/name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /register/i });
    
    fireEvent.change(nameInput, { target: { value: 'Test User' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockedAuthService.register).toHaveBeenCalledWith({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it('should display error message on registration failure', async () => {
    const errorMessage = 'Email already exists';
    mockedAuthService.register.mockRejectedValue(new Error(errorMessage));
    
    renderWithAuth(<RegisterForm />);
    
    const nameInput = screen.getByLabelText(/name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /register/i });
    
    fireEvent.change(nameInput, { target: { value: 'Test User' } });
    fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });
  });

  it('should disable submit button while loading', async () => {
    mockedAuthService.register.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 1000))
    );
    
    renderWithAuth(<RegisterForm />);
    
    const nameInput = screen.getByLabelText(/name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /register/i });
    
    fireEvent.change(nameInput, { target: { value: 'Test User' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/registering/i)).toBeInTheDocument();
  });

  it('should clear form on successful registration', async () => {
    mockedAuthService.register.mockResolvedValue({
      message: 'User registered successfully',
      user: { id: '123', email: 'test@example.com', name: 'Test User' }
    });
    mockedAuthService.login.mockResolvedValue({
      access_token: 'token',
      refresh_token: 'refresh',
      token_type: 'Bearer'
    });
    mockedAuthService.getCurrentUser.mockReturnValue({
      id: '123',
      email: 'test@example.com',
      name: 'Test User'
    });
    
    renderWithAuth(<RegisterForm />);
    
    const nameInput = screen.getByLabelText(/name/i) as HTMLInputElement;
    const emailInput = screen.getByLabelText(/email/i) as HTMLInputElement;
    const passwordInput = screen.getByLabelText(/^password$/i) as HTMLInputElement;
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i) as HTMLInputElement;
    const submitButton = screen.getByRole('button', { name: /register/i });
    
    fireEvent.change(nameInput, { target: { value: 'Test User' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(nameInput.value).toBe('');
      expect(emailInput.value).toBe('');
      expect(passwordInput.value).toBe('');
      expect(confirmPasswordInput.value).toBe('');
    });
  });

  it('should have proper accessibility attributes', () => {
    renderWithAuth(<RegisterForm />);
    
    const nameInput = screen.getByLabelText(/name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password$/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const form = screen.getByRole('form');
    
    expect(nameInput).toHaveAttribute('type', 'text');
    expect(nameInput).toHaveAttribute('required');
    expect(emailInput).toHaveAttribute('type', 'email');
    expect(emailInput).toHaveAttribute('required');
    expect(passwordInput).toHaveAttribute('type', 'password');
    expect(passwordInput).toHaveAttribute('required');
    expect(confirmPasswordInput).toHaveAttribute('type', 'password');
    expect(confirmPasswordInput).toHaveAttribute('required');
    expect(form).toHaveAttribute('aria-label', 'Registration form');
  });
});