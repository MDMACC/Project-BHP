import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  register: (userData) => api.post('/auth/register', userData),
  getMe: () => api.get('/auth/me'),
};

// Parts API
export const partsAPI = {
  getAll: (params) => api.get('/parts', { params }),
  getById: (id) => api.get(`/parts/${id}`),
  create: (data) => api.post('/parts', data),
  update: (id, data) => api.put(`/parts/${id}`, data),
  delete: (id) => api.delete(`/parts/${id}`),

  restock: (id, quantity) => api.post(`/parts/${id}/restock`, { quantity }),
};

// Orders API
export const ordersAPI = {
  getAll: (params) => api.get('/orders', { params }),
  getById: (id) => api.get(`/orders/${id}`),
  create: (data) => api.post('/orders', data),
  update: (id, data) => api.put(`/orders/${id}`, data),
  cancel: (id) => api.delete(`/orders/${id}`),
  getOverdue: () => api.get('/orders/shipping/overdue'),
  getUrgent: () => api.get('/orders/shipping/urgent'),
  receive: (id) => api.post(`/orders/${id}/receive`),
};

// Contacts API
export const contactsAPI = {
  getAll: (params) => api.get('/contacts', { params }),
  getById: (id) => api.get(`/contacts/${id}`),
  create: (data) => api.post('/contacts', data),
  update: (id, data) => api.put(`/contacts/${id}`, data),
  delete: (id) => api.delete(`/contacts/${id}`),
  getSuppliers: () => api.get('/contacts/type/suppliers'),
  getCustomers: () => api.get('/contacts/type/customers'),
  rate: (id, rating) => api.post(`/contacts/${id}/rate`, { rating }),
};

// Schedule API
export const scheduleAPI = {
  getAll: (params) => api.get('/schedule', { params }),
  getById: (id) => api.get(`/schedule/${id}`),
  create: (data) => api.post('/schedule', data),
  update: (id, data) => api.put(`/schedule/${id}`, data),
  cancel: (id) => api.delete(`/schedule/${id}`),
  getByDate: (date) => api.get(`/schedule/calendar/${date}`),
  getByTechnician: (technicianId, params) => api.get(`/schedule/technician/${technicianId}`, { params }),
  start: (id) => api.post(`/schedule/${id}/start`),
  complete: (id, data) => api.post(`/schedule/${id}/complete`, data),
};

// Dashboard API
export const dashboardAPI = {
  getStats: () => api.get('/dashboard/stats'),
  getRecentActivity: () => api.get('/dashboard/activity'),
};

// Shop API
export const shopAPI = {
  getInfo: () => api.get('/shop'),
  updateInfo: (data) => api.put('/shop', data),
};

export default api;
