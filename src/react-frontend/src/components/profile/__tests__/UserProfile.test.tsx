import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserProfile } from '../UserProfile';
import { AuthProvider } from '../../../contexts/AuthContext';
import { profileService } from '../../../services/profileService';
import { useAuth } from '../../../hooks/useAuth';

// Mock services
jest.mock('../../../services/profileService');
jest.mock('../../../hooks/useAuth');

const mockedProfileService = profileService as jest.Mocked<typeof profileService>;
const mockedUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

describe('UserProfile', () => {
  const mockUser = {
    id: '123',
    email: 'test@example.com',
    name: 'Test User'
  };

  const mockProfile = {
    id: '123',
    email: 'test@example.com',
    name: 'Test User',
    bio: 'Test bio',
    phone: '+1234567890',
    location: 'New York, NY',
    language: 'en',
    timezone: 'America/New_York',
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockedUseAuth.mockReturnValue({
      user: mockUser,
      loading: false,
      isAuthenticated: true,
      login: jest.fn(),
      register: jest.fn(),
      logout: jest.fn(),
      refreshToken: jest.fn()
    });
  });

  const renderWithAuth = (component: React.ReactElement) => {
    return render(
      <AuthProvider>
        {component}
      </AuthProvider>
    );
  };

  describe('View Mode', () => {
    it('should render user profile information in view mode', async () => {
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByText('User Profile')).toBeInTheDocument();
        expect(screen.getByText('test@example.com')).toBeInTheDocument();
        expect(screen.getByText('Test User')).toBeInTheDocument();
        expect(screen.getByText('Test bio')).toBeInTheDocument();
        expect(screen.getByText('+1234567890')).toBeInTheDocument();
        expect(screen.getByText('New York, NY')).toBeInTheDocument();
      });
    });

    it('should display loading state while fetching profile', () => {
      mockedProfileService.getProfile.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 1000))
      );
      
      renderWithAuth(<UserProfile />);
      
      expect(screen.getByText(/loading profile/i)).toBeInTheDocument();
    });

    it('should display error message when profile fetch fails', async () => {
      const errorMessage = 'Failed to load profile';
      mockedProfileService.getProfile.mockRejectedValue(new Error(errorMessage));
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('should show edit button in view mode', async () => {
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
    });

    it('should display formatted dates for created and updated times', async () => {
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByText(/member since/i)).toBeInTheDocument();
        expect(screen.getByText(/last updated/i)).toBeInTheDocument();
      });
    });
  });

  describe('Edit Mode', () => {
    beforeEach(async () => {
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
    });

    it('should switch to edit mode when edit button is clicked', async () => {
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/bio/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/phone/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/location/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /cancel/i })).toBeInTheDocument();
    });

    it('should populate form fields with current profile data', async () => {
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      const nameInput = screen.getByLabelText(/name/i) as HTMLInputElement;
      const bioInput = screen.getByLabelText(/bio/i) as HTMLTextAreaElement;
      const phoneInput = screen.getByLabelText(/phone/i) as HTMLInputElement;
      const locationInput = screen.getByLabelText(/location/i) as HTMLInputElement;
      
      expect(nameInput.value).toBe('Test User');
      expect(bioInput.value).toBe('Test bio');
      expect(phoneInput.value).toBe('+1234567890');
      expect(locationInput.value).toBe('New York, NY');
    });

    it('should successfully update profile when valid data is submitted', async () => {
      const updatedProfile = { ...mockProfile, name: 'Updated Name', bio: 'Updated bio' };
      mockedProfileService.updateProfile.mockResolvedValue(updatedProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      const nameInput = screen.getByLabelText(/name/i);
      const bioInput = screen.getByLabelText(/bio/i);
      
      fireEvent.change(nameInput, { target: { value: 'Updated Name' } });
      fireEvent.change(bioInput, { target: { value: 'Updated bio' } });
      
      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(mockedProfileService.updateProfile).toHaveBeenCalledWith({
          name: 'Updated Name',
          bio: 'Updated bio',
          phone: '+1234567890',
          location: 'New York, NY',
          language: 'en',
          timezone: 'America/New_York'
        });
        expect(screen.getByText('Updated Name')).toBeInTheDocument();
        expect(screen.getByText('Updated bio')).toBeInTheDocument();
      });
    });

    it('should show validation errors for invalid inputs', async () => {
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      const nameInput = screen.getByLabelText(/name/i);
      const phoneInput = screen.getByLabelText(/phone/i);
      
      fireEvent.change(nameInput, { target: { value: '' } });
      fireEvent.change(phoneInput, { target: { value: 'invalid-phone' } });
      
      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(screen.getByText(/name is required/i)).toBeInTheDocument();
        expect(screen.getByText(/invalid phone number/i)).toBeInTheDocument();
      });
    });

    it('should cancel edit mode and revert changes', async () => {
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      const nameInput = screen.getByLabelText(/name/i);
      fireEvent.change(nameInput, { target: { value: 'Changed Name' } });
      
      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelButton);
      
      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument();
        expect(screen.queryByText('Changed Name')).not.toBeInTheDocument();
      });
    });

    it('should display error message when profile update fails', async () => {
      const errorMessage = 'Failed to update profile';
      mockedProfileService.updateProfile.mockRejectedValue(new Error(errorMessage));
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('should disable save button while updating', async () => {
      mockedProfileService.updateProfile.mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 1000))
      );
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);
      
      expect(saveButton).toBeDisabled();
      expect(screen.getByText(/saving/i)).toBeInTheDocument();
    });
  });

  describe('Language and Timezone Settings', () => {
    it('should display language and timezone selectors in edit mode', async () => {
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      expect(screen.getByLabelText(/language/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/timezone/i)).toBeInTheDocument();
    });

    it('should update language and timezone preferences', async () => {
      const updatedProfile = { ...mockProfile, language: 'es', timezone: 'Europe/Madrid' };
      mockedProfileService.updateProfile.mockResolvedValue(updatedProfile);
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      const languageSelect = screen.getByLabelText(/language/i);
      const timezoneSelect = screen.getByLabelText(/timezone/i);
      
      fireEvent.change(languageSelect, { target: { value: 'es' } });
      fireEvent.change(timezoneSelect, { target: { value: 'Europe/Madrid' } });
      
      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        expect(mockedProfileService.updateProfile).toHaveBeenCalledWith(
          expect.objectContaining({
            language: 'es',
            timezone: 'Europe/Madrid'
          })
        );
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', async () => {
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('article', { name: /user profile/i })).toBeInTheDocument();
      });
    });

    it('should have proper form labels in edit mode', async () => {
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      expect(screen.getByLabelText(/name/i)).toHaveAttribute('id');
      expect(screen.getByLabelText(/bio/i)).toHaveAttribute('id');
      expect(screen.getByLabelText(/phone/i)).toHaveAttribute('id');
      expect(screen.getByLabelText(/location/i)).toHaveAttribute('id');
    });

    it('should announce success/error messages to screen readers', async () => {
      const updatedProfile = { ...mockProfile, name: 'Updated Name' };
      mockedProfileService.updateProfile.mockResolvedValue(updatedProfile);
      mockedProfileService.getProfile.mockResolvedValue(mockProfile);
      
      renderWithAuth(<UserProfile />);
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /edit profile/i })).toBeInTheDocument();
      });
      
      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);
      
      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);
      
      await waitFor(() => {
        const successMessage = screen.getByText(/profile updated successfully/i);
        expect(successMessage).toHaveAttribute('role', 'alert');
      });
    });
  });

  describe('Permission Checks', () => {
    it('should not show edit button for non-authenticated users', () => {
      mockedUseAuth.mockReturnValue({
        user: null,
        loading: false,
        isAuthenticated: false,
        login: jest.fn(),
        register: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn()
      });
      
      renderWithAuth(<UserProfile />);
      
      expect(screen.queryByRole('button', { name: /edit profile/i })).not.toBeInTheDocument();
    });

    it('should redirect to login if user is not authenticated', () => {
      mockedUseAuth.mockReturnValue({
        user: null,
        loading: false,
        isAuthenticated: false,
        login: jest.fn(),
        register: jest.fn(),
        logout: jest.fn(),
        refreshToken: jest.fn()
      });
      
      const onRedirect = jest.fn();
      renderWithAuth(<UserProfile onRedirect={onRedirect} />);
      
      expect(onRedirect).toHaveBeenCalledWith('/login');
    });
  });
});