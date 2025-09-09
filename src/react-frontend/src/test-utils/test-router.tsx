import React from 'react';

// Mock router components for testing
export const MemoryRouter: React.FC<{ children: React.ReactNode; initialEntries?: string[] }> = ({ children }) => {
  return <>{children}</>;
};

export const Link: React.FC<{ to: string; children: React.ReactNode; className?: string; 'aria-current'?: string; 'aria-label'?: string; title?: string }> = ({ 
  to, 
  children, 
  ...props 
}) => {
  return <a href={to} {...props}>{children}</a>;
};

export const useLocation = () => ({
  pathname: '/',
  search: '',
  hash: '',
  state: null
});