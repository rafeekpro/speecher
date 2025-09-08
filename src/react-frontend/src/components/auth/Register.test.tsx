import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Register } from './Register';
import { AuthService } from '../../services/auth.service';

jest.mock('../../services/auth.service');

const renderRegister = () => {
  return render(
    <BrowserRouter>
      <Register />
    </BrowserRouter>
  );
};

describe('Register Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render registration form', () => {
    renderRegister();
    
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
    expect(screen.getByText(/already have an account/i)).toBeInTheDocument();
  });

  it('should validate full name is not empty', async () => {
    renderRegister();
    
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/full name is required/i)).toBeInTheDocument();
    });
  });

  it('should validate email format', async () => {
    renderRegister();
    
    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    
    await userEvent.type(emailInput, 'invalid-email');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
    });
  });

  it('should validate password strength', async () => {
    renderRegister();
    
    const passwordInput = screen.getByLabelText(/^password/i);
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    
    await userEvent.type(passwordInput, 'weak');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    });
  });

  it('should validate passwords match', async () => {
    renderRegister();
    
    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    
    await userEvent.type(passwordInput, 'ValidPass123!');
    await userEvent.type(confirmPasswordInput, 'DifferentPass123!');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    });
  });

  it('should call AuthService.register with correct data', async () => {
    const mockRegister = jest.spyOn(AuthService, 'register').mockResolvedValueOnce({
      accessToken: 'token',
      refreshToken: 'refresh',
      tokenType: 'Bearer',
      user: {
        id: '123',
        email: 'new@example.com',
        fullName: 'New User',
        role: 'user',
        createdAt: new Date(),
        updatedAt: new Date()
      }
    });

    renderRegister();
    
    const fullNameInput = screen.getByLabelText(/full name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    
    await userEvent.type(fullNameInput, 'New User');
    await userEvent.type(emailInput, 'new@example.com');
    await userEvent.type(passwordInput, 'ValidPass123!');
    await userEvent.type(confirmPasswordInput, 'ValidPass123!');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockRegister).toHaveBeenCalledWith({
        fullName: 'New User',
        email: 'new@example.com',
        password: 'ValidPass123!'
      });
    });
  });

  it('should display error message on registration failure', async () => {
    jest.spyOn(AuthService, 'register').mockRejectedValueOnce(
      new Error('Email already registered')
    );

    renderRegister();
    
    const fullNameInput = screen.getByLabelText(/full name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    
    await userEvent.type(fullNameInput, 'Existing User');
    await userEvent.type(emailInput, 'existing@example.com');
    await userEvent.type(passwordInput, 'ValidPass123!');
    await userEvent.type(confirmPasswordInput, 'ValidPass123!');
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/email already registered/i)).toBeInTheDocument();
    });
  });

  it('should show loading state during registration', async () => {
    jest.spyOn(AuthService, 'register').mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 1000))
    );

    renderRegister();
    
    const fullNameInput = screen.getByLabelText(/full name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/^password/i);
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i);
    const submitButton = screen.getByRole('button', { name: /sign up/i });
    
    await userEvent.type(fullNameInput, 'New User');
    await userEvent.type(emailInput, 'new@example.com');
    await userEvent.type(passwordInput, 'ValidPass123!');
    await userEvent.type(confirmPasswordInput, 'ValidPass123!');
    fireEvent.click(submitButton);
    
    expect(screen.getByText(/creating account/i)).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  it('should navigate to login page when clicking sign in link', () => {
    renderRegister();
    
    const signInLink = screen.getByText(/sign in/i);
    expect(signInLink).toHaveAttribute('href', '/login');
  });

  it('should display password strength indicator', async () => {
    renderRegister();
    
    const passwordInput = screen.getByLabelText(/^password/i);
    
    // Weak password
    await userEvent.type(passwordInput, 'weak');
    expect(screen.getByText(/weak/i)).toBeInTheDocument();
    
    // Clear and type medium password
    await userEvent.clear(passwordInput);
    await userEvent.type(passwordInput, 'Medium123');
    expect(screen.getByText(/medium/i)).toBeInTheDocument();
    
    // Clear and type strong password
    await userEvent.clear(passwordInput);
    await userEvent.type(passwordInput, 'StrongPass123!@#');
    expect(screen.getByText(/strong/i)).toBeInTheDocument();
  });
});