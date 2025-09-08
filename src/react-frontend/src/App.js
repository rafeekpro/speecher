import React, { useState, useEffect, useCallback } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
  Paper,
  IconButton,
  Chip,
  Drawer,
  Alert,
  Snackbar,
  CircularProgress,
  Backdrop
} from '@mui/material';
import {
  Mic as MicIcon,
  CloudUpload as UploadIcon,
  Description as FileAudioIcon,
  History as HistoryIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
  GraphicEq as LogoIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

import AudioRecorder from './components/AudioRecorder';
import FileUpload from './components/FileUpload';
import TranscriptionResults from './components/TranscriptionResults';
import History from './components/History';
import Statistics from './components/Statistics';
import Settings from './components/Settings';
import { transcribeAudio, checkHealth } from './services/api';

// Create MUI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
      light: '#8b9bf0',
      dark: '#4c5cd8',
    },
    secondary: {
      main: '#764ba2',
      light: '#9166bc',
      dark: '#5a3a7e',
    },
    success: {
      main: '#48bb78',
    },
    warning: {
      main: '#ed8936',
    },
    error: {
      main: '#f56565',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    h4: {
      fontWeight: 700,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

// Tab panel component
function TabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      aria-labelledby={`tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState(0);
  const [transcriptions, setTranscriptions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [configuredProviders, setConfiguredProviders] = useState([]);
  const [providers, setProviders] = useState([]);
  const [settings, setSettings] = useState({
    provider: 'azure',
    language: 'en-US',
    enableDiarization: true,
    maxSpeakers: 4,
    includeTimestamps: true,
    showCost: true
  });
  const [showSettings, setShowSettings] = useState(false);

  const checkBackendHealth = useCallback(async () => {
    const health = await checkHealth();
    setBackendStatus(health.status === 'healthy' ? 'healthy' : 'unhealthy');
  }, []);

  const loadConfiguredProviders = useCallback(async () => {
    try {
      const response = await fetch('http://localhost:8000/api/keys');
      if (response.ok) {
        const providersData = await response.json();
        setProviders(providersData); // Store all providers for footer display
        const configured = providersData.filter(p => p.configured && p.enabled);
        setConfiguredProviders(configured);
        
        // If current provider is not configured, switch to first configured one
        if (!configured.find(p => p.provider === settings.provider)) {
          if (configured.length > 0) {
            setSettings(prev => ({ ...prev, provider: configured[0].provider }));
          }
        }
      }
    } catch (error) {
      console.error('Failed to load configured providers:', error);
    }
  }, [settings.provider]);

  useEffect(() => {
    // Check backend health on mount
    checkBackendHealth();
    loadConfiguredProviders();
    const interval = setInterval(() => {
      checkBackendHealth();
      loadConfiguredProviders();
    }, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, [checkBackendHealth, loadConfiguredProviders]);

  const handleAudioRecorded = async (audioBlob, fileName = 'recording.wav') => {
    // Check if provider is configured
    if (configuredProviders.length === 0) {
      setError('No providers configured. Please configure API keys in Settings.');
      return;
    }
    
    if (!configuredProviders.find(p => p.provider === settings.provider)) {
      setError(`${settings.provider.toUpperCase()} is not configured. Please configure API keys in Settings.`);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    console.log('Sending transcription request:');
    console.log('- File:', fileName, 'Type:', audioBlob.type, 'Size:', audioBlob.size);
    console.log('- Provider:', settings.provider);
    console.log('- Language:', settings.language);
    
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, fileName);
      formData.append('provider', settings.provider);
      formData.append('language', settings.language);
      formData.append('enable_diarization', settings.enableDiarization);
      formData.append('max_speakers', settings.maxSpeakers);
      formData.append('include_timestamps', settings.includeTimestamps);
      
      const result = await transcribeAudio(formData);
      
      const newTranscription = {
        ...result,
        timestamp: new Date().toISOString(),
        fileName: fileName,
        audioUrl: audioBlob instanceof Blob ? URL.createObjectURL(audioBlob) : null
      };
      
      setTranscriptions([newTranscription, ...transcriptions]);
      
      // Switch to results tab after successful transcription
      if (activeTab === 'record' || activeTab === 'upload') {
        setActiveTab('results');
      }
    } catch (err) {
      // Extract error message from response
      let errorMessage = 'Failed to transcribe audio';
      if (err.response) {
        const errorData = await err.response.json().catch(() => null);
        if (errorData && errorData.detail) {
          errorMessage = errorData.detail;
        } else if (err.response.status === 400) {
          errorMessage = 'Invalid request. Please check your API keys configuration.';
        } else if (err.response.status === 401) {
          errorMessage = 'Authentication failed. Please check your API keys.';
        } else if (err.response.status === 403) {
          errorMessage = 'Access denied. Please check your API keys permissions.';
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = () => {
    switch (backendStatus) {
      case 'healthy': return 'success';
      case 'unhealthy': return 'error';
      default: return 'warning';
    }
  };

  const getStatusIcon = () => {
    switch (backendStatus) {
      case 'healthy': return <CheckIcon fontSize="small" />;
      case 'unhealthy': return <ErrorIcon fontSize="small" />;
      default: return <CircularProgress size={16} />;
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        {/* App Bar */}
        <AppBar position="static" color="transparent" elevation={0}>
          <Toolbar sx={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)' }}>
            <LogoIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h4" component="h1" sx={{ color: 'text.primary' }}>
                Speecher
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                AI-Powered Speech Recognition Platform
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Chip
                icon={getStatusIcon()}
                label={`Backend: ${backendStatus}`}
                color={getStatusColor()}
                size="small"
                variant="outlined"
              />
              <IconButton color="primary" onClick={() => checkBackendHealth()}>
                <RefreshIcon />
              </IconButton>
              <IconButton color="primary" onClick={() => setShowSettings(true)}>
                <SettingsIcon />
              </IconButton>
            </Box>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          <Paper elevation={3} sx={{ borderRadius: 2 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs 
                value={activeTab} 
                onChange={(e, newValue) => setActiveTab(newValue)}
                variant="fullWidth"
              >
                <Tab icon={<MicIcon />} label="Record" />
                <Tab icon={<UploadIcon />} label="Upload" />
                <Tab icon={<FileAudioIcon />} label="Results" />
                <Tab icon={<HistoryIcon />} label="History" />
                <Tab icon={<BarChartIcon />} label="Statistics" />
              </Tabs>
            </Box>

            <TabPanel value={activeTab} index={0}>
              <AudioRecorder 
                onAudioRecorded={handleAudioRecorded}
                isLoading={isLoading}
                settings={settings}
              />
            </TabPanel>

            <TabPanel value={activeTab} index={1}>
              <FileUpload 
                onFilesUploaded={handleAudioRecorded}
                isLoading={isLoading}
                settings={settings}
              />
            </TabPanel>

            <TabPanel value={activeTab} index={2}>
              <TranscriptionResults 
                transcriptions={transcriptions}
                settings={settings}
              />
            </TabPanel>

            <TabPanel value={activeTab} index={3}>
              <History 
                onSelectTranscription={(t) => {
                  setTranscriptions([t, ...transcriptions]);
                  setActiveTab(2);
                }}
              />
            </TabPanel>

            <TabPanel value={activeTab} index={4}>
              <Statistics />
            </TabPanel>
          </Paper>
        </Container>

        {/* Settings Drawer */}
        <Drawer
          anchor="right"
          open={showSettings}
          onClose={() => setShowSettings(false)}
        >
          <Settings 
            settings={settings}
            onSettingsChange={setSettings}
            onClose={() => setShowSettings(false)}
          />
        </Drawer>

        {/* Error Snackbar */}
        <Snackbar 
          open={!!error} 
          autoHideDuration={6000} 
          onClose={() => setError(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>

        {/* Loading Backdrop */}
        <Backdrop
          sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
          open={isLoading}
        >
          <CircularProgress color="inherit" />
        </Backdrop>

        {/* Footer with API Keys Source Info */}
        <Box 
          component="footer" 
          sx={{ 
            mt: 4, 
            py: 2, 
            px: 3, 
            backgroundColor: 'background.paper',
            borderTop: 1,
            borderColor: 'divider',
            textAlign: 'center'
          }}
        >
          <Typography variant="caption" color="text.secondary">
            💡 Configuration Source: API keys are loaded from .env file (environment variables) or MongoDB database
          </Typography>
          {providers && providers.length > 0 && (
            <Box sx={{ mt: 1 }}>
              {providers.filter(p => p.configured).map(provider => (
                <Chip
                  key={provider.provider}
                  label={`${provider.provider.toUpperCase()}: ${provider.source === 'mongodb' ? '🗄️ MongoDB' : '📁 .env'}`}
                  size="small"
                  variant="outlined"
                  sx={{ mx: 0.5 }}
                />
              ))}
            </Box>
          )}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;