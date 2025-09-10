# Sidebar Navigation System

A modern, accessible, and responsive sidebar navigation system for the React frontend.

## Features

### Core Functionality
- **Collapsible Sidebar**: Toggle between expanded and collapsed states with smooth animations
- **Navigation Menu**: Organized menu items with icons and labels
- **Active Route Highlighting**: Visual indication of the current page
- **User Context Display**: Shows authenticated user information
- **Logout Functionality**: Integrated logout button in sidebar

### Responsive Design
- **Desktop Mode**: 
  - Sidebar is visible by default
  - Can be collapsed to icon-only view
  - Smooth width transitions (256px expanded, 64px collapsed)
- **Mobile Mode** (< 768px):
  - Sidebar hidden by default
  - Opens as overlay with backdrop
  - Tap outside or press Escape to close
  - Full-screen navigation experience

### Accessibility
- **ARIA Labels**: Proper semantic markup and ARIA attributes
- **Keyboard Navigation**: 
  - Tab through menu items
  - Ctrl+B to toggle sidebar
  - Escape to close on mobile
- **Screen Reader Support**: Announces state changes and current page
- **Focus Management**: Proper focus trap on mobile overlay
- **Tooltips**: Shows labels when sidebar is collapsed

### Performance
- **Smooth Animations**: Hardware-accelerated CSS transitions
- **Optimized Re-renders**: Uses React hooks efficiently
- **Lazy State Updates**: Debounced window resize handling

## Components

### Layout
Main wrapper component that orchestrates the sidebar and content area.

```tsx
import { Layout } from './components/layout';

<Layout>
  {/* Your page content */}
</Layout>
```

### Sidebar
The collapsible navigation sidebar with user info and menu items.

**Props:**
- `isOpen?: boolean` - Controls mobile sidebar visibility
- `onClose?: () => void` - Callback when mobile sidebar closes
- `isCollapsed?: boolean` - Controls desktop sidebar collapse state
- `onToggleCollapse?: () => void` - Callback for collapse toggle

### Navigation
Renders the navigation menu items with active state highlighting.

**Props:**
- `items: NavigationItem[]` - Array of navigation items
- `isCollapsed: boolean` - Whether sidebar is collapsed

**NavigationItem structure:**
```tsx
interface NavigationItem {
  path: string;    // Route path
  label: string;   // Display text
  icon: string;    // Icon identifier
}
```

## Usage Example

```tsx
import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Layout } from './components/layout';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/record" element={<Record />} />
            {/* More routes... */}
          </Routes>
        </Layout>
      </AuthProvider>
    </BrowserRouter>
  );
}
```

## Styling

The components use Tailwind CSS for styling with a consistent design system:

- **Colors**: Blue/purple gradient for branding
- **Shadows**: Subtle elevation for depth
- **Transitions**: 300ms duration for smooth animations
- **Breakpoints**: `md` (768px) for responsive behavior

## Testing

Comprehensive test coverage with React Testing Library:

```bash
npm test -- --testPathPattern="layout"
```

Test categories:
- Rendering and structure
- Collapsible behavior
- Mobile responsiveness
- Accessibility features
- User interactions
- Keyboard shortcuts

## Keyboard Shortcuts

- **Ctrl+B**: Toggle sidebar collapse/expand
- **Escape**: Close mobile sidebar
- **Tab**: Navigate through menu items

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Requires JavaScript enabled
- CSS Grid and Flexbox support

## Future Enhancements

- [ ] Nested menu items support
- [ ] Search functionality in sidebar
- [ ] Customizable theme colors
- [ ] Persistent collapse state (localStorage)
- [ ] Animated menu item icons
- [ ] Badge notifications on menu items