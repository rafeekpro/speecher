import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import {
  validateEmail,
  validatePassword,
  MIN_PASSWORD_LENGTH,
} from "../../utils/validation";

interface RegisterFormProps {
  onSuccess?: () => void;
}

interface FormData {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  name?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  general?: string;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess }) => {
  const { register } = useAuth();
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState(false);

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name) {
      newErrors.name = "Name is required";
    }

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!validateEmail(formData.email)) {
      newErrors.email = "Invalid email format";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (!validatePassword(formData.password)) {
      newErrors.password = `Password must be at least ${MIN_PASSWORD_LENGTH} characters`;
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = "Password confirmation is required";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = "Passwords do not match";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error for this field when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      await register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
      });
      // Clear form on success
      setFormData({
        name: "",
        email: "",
        password: "",
        confirmPassword: "",
      });
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      setErrors({
        general: error instanceof Error ? error.message : "Registration failed",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} aria-label="Registration form" role="form">
      <div style={{ marginBottom: "1rem" }}>
        <label
          htmlFor="name"
          style={{ display: "block", marginBottom: "0.5rem" }}
        >
          Name
        </label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.5rem",
            border: errors.name ? "1px solid red" : "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        {errors.name && (
          <span style={{ color: "red", fontSize: "0.875rem" }}>
            {errors.name}
          </span>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label
          htmlFor="email"
          style={{ display: "block", marginBottom: "0.5rem" }}
        >
          Email
        </label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          required
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.5rem",
            border: errors.email ? "1px solid red" : "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        {errors.email && (
          <span style={{ color: "red", fontSize: "0.875rem" }}>
            {errors.email}
          </span>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label
          htmlFor="password"
          style={{ display: "block", marginBottom: "0.5rem" }}
        >
          Password
        </label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          required
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.5rem",
            border: errors.password ? "1px solid red" : "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        {errors.password && (
          <span style={{ color: "red", fontSize: "0.875rem" }}>
            {errors.password}
          </span>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <label
          htmlFor="confirmPassword"
          style={{ display: "block", marginBottom: "0.5rem" }}
        >
          Confirm Password
        </label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          required
          disabled={loading}
          style={{
            width: "100%",
            padding: "0.5rem",
            border: errors.confirmPassword ? "1px solid red" : "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        {errors.confirmPassword && (
          <span style={{ color: "red", fontSize: "0.875rem" }}>
            {errors.confirmPassword}
          </span>
        )}
      </div>

      {errors.general && (
        <div style={{ color: "red", marginBottom: "1rem" }}>
          {errors.general}
        </div>
      )}

      <button
        type="submit"
        disabled={loading}
        style={{
          width: "100%",
          padding: "0.75rem",
          backgroundColor: loading ? "#ccc" : "#28a745",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: loading ? "not-allowed" : "pointer",
          fontSize: "1rem",
        }}
      >
        {loading ? "Registering..." : "Register"}
      </button>
    </form>
  );
};

