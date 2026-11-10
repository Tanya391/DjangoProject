const BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_BASE_PATH || '/api/v1';

export const getToken = () => localStorage.getItem('access_token');
export const clearToken = () => localStorage.removeItem('access_token');

export const getAuthHeader = () => {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
};

async function request(endpoint, options = {}) {
  const isFormData = options.body instanceof FormData;
  const headers = {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...getAuthHeader(),
    ...options.headers,
  };

  const config = {
    ...options,
    headers,
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, config);

  if (response.status === 401 || response.status === 403) {
    clearToken();
    window.dispatchEvent(new Event('auth-change'));
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    let message = errorData.error || errorData.detail || errorData.message;
    if (!message && errorData && typeof errorData === 'object') {
      const firstValue = Object.values(errorData)[0];
      if (Array.isArray(firstValue) && firstValue.length > 0) message = String(firstValue[0]);
      else if (firstValue != null) message = String(firstValue);
    }
    throw new Error(message || `Request failed (${response.status})`);
  }
  return response.json();
}

export const api = {
  // Status
  getStatus: () => request('/status/'),

  // Auth
  login: (data) => request('/auth/login/', { method: 'POST', body: JSON.stringify(data) }),
  register: (data) => request('/auth/register/', { method: 'POST', body: JSON.stringify(data) }),
  logout: () => request('/auth/logout/', { method: 'POST' }),

  // Analytics
  getCashflow: () => request('/cashflow/'),
  getMonthlySummary: (year) => request(`/monthly-summary/${year ? `?year=${year}` : ''}`),
  getCategoryBreakdown: () => request('/spending-by-category/'),
  getTopMerchants: (limit = 10) => request(`/top-merchants/?limit=${limit}`),
  getSubscriptions: () => request('/subscriptions/'),

  // Transactions
  getTransactions: ({ search = '', category = '', limit = 100, offset = 0 } = {}) => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (category) params.append('category', category);
    params.append('limit', limit);
    params.append('offset', offset);
    return request(`/transactions/?${params.toString()}`);
  },

  // RAG / AI
  askQuestion: (question) => request('/ask/', { method: 'POST', body: JSON.stringify({ question }) }),
  retrieveSources: (question) => request('/retrieve/', { method: 'POST', body: JSON.stringify({ question }) }),
  getQueryHistory: () => request('/history/'),

  // Data Management
  uploadCSV: (formData) => request('/upload/', { method: 'POST', body: formData }),
  seedDemoData: () => request('/seed/', { method: 'POST' }),
};
