import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5003';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = () => api.get('/api/health');

export const getConfig = () => api.get('/api/config');

export const uploadOrders = (orders) => 
  api.post('/api/orders/upload', { orders });

export const getOrdersStatus = () => api.get('/api/orders/status');

/** Get orders from Supabase (synced data) */
export const getOrdersFromSupabase = () => api.get('/api/orders/supabase');

export default api;
