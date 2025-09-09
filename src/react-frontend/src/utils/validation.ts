/**
 * Validation utilities for form inputs
 */

// Constants
export const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
export const MIN_PASSWORD_LENGTH = 8;

/**
 * Validates email format
 * @param email - Email string to validate
 * @returns true if email format is valid, false otherwise
 */
export const validateEmail = (email: string): boolean => {
  return EMAIL_REGEX.test(email);
};

/**
 * Validates password meets minimum requirements
 * @param password - Password string to validate
 * @returns true if password meets requirements, false otherwise
 */
export const validatePassword = (password: string): boolean => {
  return password.length >= MIN_PASSWORD_LENGTH;
};

