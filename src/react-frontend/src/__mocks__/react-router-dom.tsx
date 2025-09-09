import React from 'react';

export const Link = ({ children, to, ...props }: any) => (
  <a href={to} {...props}>{children}</a>
);

export const useLocation = jest.fn(() => ({ 
  pathname: '/',
  search: '',
  hash: '',
  state: null
}));

export const MemoryRouter = ({ children }: any) => <>{children}</>;
export const BrowserRouter = ({ children }: any) => <>{children}</>;
export const Navigate = ({ to }: any) => <div>Navigate to {to}</div>;