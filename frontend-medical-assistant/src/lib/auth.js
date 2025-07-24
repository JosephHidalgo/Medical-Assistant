const API_BASE_URL = 'http://localhost:8000/api'; // URL de Django

export const authAPI = {
  async login(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Importante para cookies
      body: JSON.stringify({ email, password }),
    });
    
    return await response.json();
  },

  async register(username, password, email) {
    const response = await fetch(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ username, password, email }),
    });
    
    return await response.json();
  },

  async logout() {
    const response = await fetch(`${API_BASE_URL}/auth/logout/`, {
      method: 'POST',
      credentials: 'include',
    });
    
    return await response.json();
  },

  async checkAuth() {
    const response = await fetch(`${API_BASE_URL}/auth/check/`, {
      method: 'GET',
      credentials: 'include',
    });
    
    return await response.json();
  },

  async fetchProtected() {
    const response = await fetch(`${API_BASE_URL}/auth/protected/`, {
      method: 'GET',
      credentials: 'include',
    });
    
    return await response.json();
  }
};