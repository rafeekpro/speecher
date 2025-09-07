import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const transcribeAudio = async (formData) => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/transcribe`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        timeout: 60000 // 60 second timeout
      }
    );
    
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Server error');
    } else if (error.request) {
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      throw new Error('Failed to send request');
    }
  }
};

export const getTranscriptionHistory = async (limit = 50) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/history`, {
      params: { limit }
    });
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch history');
  }
};

export const getTranscriptionById = async (id) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/transcription/${id}`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch transcription');
  }
};

export const deleteTranscription = async (id) => {
  try {
    const response = await axios.delete(`${API_BASE_URL}/transcription/${id}`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to delete transcription');
  }
};

export const getStatistics = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/stats`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to fetch statistics');
  }
};

export const checkHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`);
    return response.data;
  } catch (error) {
    return { status: 'unhealthy', error: error.message };
  }
};

export const getProviders = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/keys`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch providers:', error);
    return [];
  }
};