import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token nas requisições
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth
export const authAPI = {
  login: (username, password) =>
    api.post('/api/auth/login', { username, password }),

  getMe: () =>
    api.get('/api/auth/me'),

  logout: () =>
    api.post('/api/auth/logout'),
};

// Dashboard
export const dashboardAPI = {
  getTodayMetrics: () =>
    api.get('/api/dashboard/metrics/today'),

  getPeriodMetrics: (startDate, endDate) =>
    api.get('/api/dashboard/metrics/period', {
      params: { start_date: startDate, end_date: endDate },
    }),

  getSummary: () =>
    api.get('/api/dashboard/stats/summary'),

  getRecentCustomers: (limit = 10) =>
    api.get('/api/dashboard/customers/recent', { params: { limit } }),

  updateMetrics: () =>
    api.post('/api/dashboard/metrics/update'),
};

// Conversations & Trials
export const conversationsAPI = {
  getCustomerHistory: (customerId, limit = 50) =>
    api.get(`/api/conversations/history/${customerId}`, { params: { limit } }),

  getRecentConversations: (limit = 20) =>
    api.get('/api/conversations/recent', { params: { limit } }),

  getGroupedConversations: (limit = 20) =>
    api.get('/api/conversations/grouped', { params: { limit } }),

  getActiveTrials: () =>
    api.get('/api/conversations/trials/active'),

  getExpiredTrials: () =>
    api.get('/api/conversations/trials/expired'),

  getAllTrials: (status = null, limit = 50) =>
    api.get('/api/conversations/trials/all', {
      params: { status, limit },
    }),

  getTrialDetails: (trialId) =>
    api.get(`/api/conversations/trials/${trialId}`),

  updateTrialStatus: (trialId, status, notes = null) =>
    api.patch(`/api/conversations/trials/${trialId}/status`, {
      status,
      notes,
    }),

  convertTrial: (trialId, planName) =>
    api.post(`/api/conversations/trials/${trialId}/convert`, {
      plan_name: planName,
    }),

  getRecentMessages: (limit = 50, direction = null) =>
    api.get('/api/conversations/messages/recent', {
      params: { limit, direction },
    }),
};

// QR Code
export const qrcodeAPI = {
  generate: () =>
    api.get('/api/qrcode/generate', { responseType: 'blob' }),

  getStatus: () =>
    api.get('/api/qrcode/status'),

  disconnect: () =>
    api.post('/api/qrcode/disconnect'),

  restart: () =>
    api.post('/api/qrcode/restart'),

  health: () =>
    api.get('/api/qrcode/health'),
};

export default api;
