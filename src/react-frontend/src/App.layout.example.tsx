import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Layout } from './components/layout';

// Example page components
const Dashboard = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-2">Recent Recordings</h2>
        <p className="text-gray-600">View and manage your recent audio recordings</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-2">Statistics</h2>
        <p className="text-gray-600">Track your transcription usage and accuracy</p>
      </div>
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-2">Quick Actions</h2>
        <p className="text-gray-600">Start recording or upload files quickly</p>
      </div>
    </div>
  </div>
);

const Record = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Record Audio</h1>
    <div className="bg-white p-6 rounded-lg shadow">
      <p>Audio recording interface will go here</p>
    </div>
  </div>
);

const Upload = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Upload Files</h1>
    <div className="bg-white p-6 rounded-lg shadow">
      <p>File upload interface will go here</p>
    </div>
  </div>
);

const History = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Transcription History</h1>
    <div className="bg-white p-6 rounded-lg shadow">
      <p>History list will go here</p>
    </div>
  </div>
);

const Statistics = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Statistics</h1>
    <div className="bg-white p-6 rounded-lg shadow">
      <p>Statistics charts will go here</p>
    </div>
  </div>
);

const Settings = () => (
  <div className="p-6">
    <h1 className="text-3xl font-bold mb-4">Settings</h1>
    <div className="bg-white p-6 rounded-lg shadow">
      <p>Settings interface will go here</p>
    </div>
  </div>
);

/**
 * Example App demonstrating the sidebar navigation system
 * 
 * Features:
 * - Collapsible sidebar with smooth animations
 * - Navigation menu with active route highlighting
 * - User context display in sidebar
 * - Mobile responsive design with overlay
 * - Full accessibility with ARIA labels and keyboard navigation
 * - Keyboard shortcut (Ctrl+B) to toggle sidebar
 */
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/record" element={<Record />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/history" element={<History />} />
            <Route path="/statistics" element={<Statistics />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;