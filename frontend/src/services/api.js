import axios from 'axios';

const getBaseURL = () => {
  if (process.env.REACT_APP_API_URL) return process.env.REACT_APP_API_URL;
  if (process.env.NODE_ENV === 'production') return '';
  return 'http://localhost:5000';
};

const api = axios.create({
  baseURL: getBaseURL(),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Agent API calls
export const agentAPI = {
  executeTask: (task, agentType = 'auto', options = {}) => 
    api.post('/api/agents/execute', { task, agent_type: agentType, ...options }),
  
  getHistory: () => 
    api.get('/api/agents/history'),
  
  getAgentStatus: () => 
    api.get('/api/agents/status'),
};

// User settings API
export const settingsAPI = {
  getSettings: () => 
    api.get('/api/settings'),
  
  updateSettings: (settings) => 
    api.put('/api/settings', settings),
  
  updateProfile: (profile) => 
    api.put('/api/profile', profile),
};
