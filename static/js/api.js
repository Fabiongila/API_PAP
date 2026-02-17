/**
 * AgroCaua API Client
 * Handles all HTTP requests to the Flask backend with JWT authentication
 */

const API_BASE = window.location.origin;

/**
 * Get JWT token from localStorage
 */
function getToken() {
  return localStorage.getItem('agrocaua_token');
}

/**
 * Save JWT token to localStorage
 */
function saveToken(token) {
  localStorage.setItem('agrocaua_token', token);
}

/**
 * Remove JWT token from localStorage
 */
function clearToken() {
  localStorage.removeItem('agrocaua_token');
}

/**
 * Fetch with JWT authentication
 */
async function authenticatedFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers
    });
    
    // Handle 401 Unauthorized
    if (response.status === 401) {
      clearToken();
      window.location.href = '/login';
      throw new Error('Authentication required');
    }
    
    return response;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

/**
 * API Endpoints
 */
const API = {
  // Authentication
  login: async (email, password) => {
    const response = await fetch(`${API_BASE}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return response;
  },
  
  register: async (nome, email, password) => {
    const response = await fetch(`${API_BASE}/api/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome, email, password })
    });
    return response;
  },
  
  logout: async () => {
    const response = await authenticatedFetch('/api/logout', { 
      method: 'POST' 
    });
    return response;
  },
  
  deleteAccount: async () => {
    const response = await authenticatedFetch('/api/delete-account', { 
      method: 'DELETE' 
    });
    return response;
  },

  // User Profile
  getProfile: async () => {
    const response = await authenticatedFetch('/api/profile');
    return response;
  },
  
  // Sensor Data
  getAllData: async () => {
    const response = await authenticatedFetch('/api/dados_sensores');
    return response;
  },
  
  getGPS: async () => {
    const response = await authenticatedFetch('/api/gps');
    return response;
  },
  
  getBME280: async () => {
    const response = await authenticatedFetch('/api/bme280');
    return response;
  },
  
  getSolo: async () => {
    const response = await authenticatedFetch('/api/solo');
    return response;
  },
  
  getVibracao: async () => {
    const response = await authenticatedFetch('/api/vibracao');
    return response;
  },
  
  getVisao: async () => {
    const response = await authenticatedFetch('/api/visao');
    return response;
  },

  getAlertas: async () => {
    const response = await authenticatedFetch('/api/alertas');
    return response;
  }
};
