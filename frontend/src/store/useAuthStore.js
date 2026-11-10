import { create } from 'zustand';
import { api } from '../services/api';

export const useAuthStore = create((set) => ({
  token: localStorage.getItem('access_token') || null,
  user: JSON.parse(localStorage.getItem('finagent_user') || 'null'),
  isAuthenticated: !!localStorage.getItem('access_token'),

  setAuth: (token, user) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('finagent_user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },

  logout: async () => {
    try {
      await api.logout();
    } catch (_) {}
    localStorage.removeItem('access_token');
    localStorage.removeItem('finagent_user');
    set({ token: null, user: null, isAuthenticated: false });
  },
}));
