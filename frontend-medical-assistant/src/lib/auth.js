const API_BASE_URL = 'http://localhost:8000/api'; // URL de Django

export const authAPI = {
  async login(correoElectronico, contraseña) {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Importante para sesiones
        body: JSON.stringify({ 
          correo_electronico: correoElectronico, 
          contraseña: contraseña 
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error en el login');
      }
      
      return data;
    } catch (error) {
      console.error('Error en login:', error);
      throw error;
    }
  },

  async register(datosRegistro) {
    try {
      console.log("Datos de registro:", datosRegistro);
      const response = await fetch(`${API_BASE_URL}/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(datosRegistro),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error en el registro');
      }
      
      return data;
    } catch (error) {
      console.error('Error en registro:', error);
      throw error;
    }
  },

  async logout() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/logout/`, {
        method: 'POST',
        credentials: 'include',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error al cerrar sesión');
      }
      
      return data;
    } catch (error) {
      console.error('Error en logout:', error);
      throw error;
    }
  },

  async checkAuth() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/check-auth/`, {
        method: 'GET',
        credentials: 'include',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error('Error verificando autenticación');
      }
      
      return data;
    } catch (error) {
      console.error('Error verificando auth:', error);
      throw error;
    }
  },

  async obtenerPerfil() {
    try {
      const response = await fetch(`${API_BASE_URL}/paciente/perfil/`, {
        method: 'GET',
        credentials: 'include',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error obteniendo perfil');
      }
      
      return data;
    } catch (error) {
      console.error('Error obteniendo perfil:', error);
      throw error;
    }
  }
};

// API específica para funcionalidades médicas
export const medicoAPI = {
  async obtenerEspecialidades() {
    try {
      const response = await fetch(`${API_BASE_URL}/medico/especialidades/`, {
        method: 'GET',
        credentials: 'include',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error obteniendo especialidades');
      }
      
      return data;
    } catch (error) {
      console.error('Error obteniendo especialidades:', error);
      throw error;
    }
  },

  async obtenerDoctores(especialidad = null) {
    try {
      let url = `${API_BASE_URL}/medico/doctores/`;
      if (especialidad) {
        url += `?especialidad=${encodeURIComponent(especialidad)}`;
      }
      
      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error obteniendo doctores');
      }
      
      return data;
    } catch (error) {
      console.error('Error obteniendo doctores:', error);
      throw error;
    }
  },

  async crearCita(datosCita) {
    try {
      const response = await fetch(`${API_BASE_URL}/medico/crear-cita/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(datosCita),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error creando cita');
      }
      
      return data;
    } catch (error) {
      console.error('Error creando cita:', error);
      throw error;
    }
  },

  async obtenerMisCitas() {
    try {
      const response = await fetch(`${API_BASE_URL}/medico/mis-citas/`, {
        method: 'GET',
        credentials: 'include',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error obteniendo citas');
      }
      
      return data;
    } catch (error) {
      console.error('Error obteniendo citas:', error);
      throw error;
    }
  },

  async cancelarCita(citaId) {
    try {
      const response = await fetch(`${API_BASE_URL}/medico/cancelar-cita/${citaId}/`, {
        method: 'POST',
        credentials: 'include',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error cancelando cita');
      }
      
      return data;
    } catch (error) {
      console.error('Error cancelando cita:', error);
      throw error;
    }
  }
};

// API para funcionalidades de IA médica (futuras)
export const iaAPI = {
  async consultarSintomas(sintomas) {
    try {
      const response = await fetch(`${API_BASE_URL}/ia/analizar-sintomas/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ sintomas }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error analizando síntomas');
      }
      
      return data;
    } catch (error) {
      console.error('Error analizando síntomas:', error);
      throw error;
    }
  },

  async obtenerRecomendaciones(pacienteId) {
    try {
      const response = await fetch(`${API_BASE_URL}/ia/recomendaciones/${pacienteId}/`, {
        method: 'GET',
        credentials: 'include',
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error obteniendo recomendaciones');
      }
      
      return data;
    } catch (error) {
      console.error('Error obteniendo recomendaciones:', error);
      throw error;
    }
  },

  async chatMedico(mensaje, contexto = null) {
    try {
      const response = await fetch(`${API_BASE_URL}/ia/chat-medico/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ 
          mensaje,
          contexto 
        }),
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Error en chat médico');
      }
      
      return data;
    } catch (error) {
      console.error('Error en chat médico:', error);
      throw error;
    }
  }
};

// Utilidades para manejo de errores y respuestas
export const apiUtils = {
  handleApiError(error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      return 'Error de conexión. Verifique su conexión a internet.';
    }
    
    return error.message || 'Ha ocurrido un error inesperado.';
  },

  async makeRequest(url, options = {}) {
    const defaultOptions = {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    try {
      const response = await fetch(url, { ...defaultOptions, ...options });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `Error HTTP: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`Error en petición a ${url}:`, error);
      throw error;
    }
  }
};

// Compatibilidad con la versión anterior
export const legacyAuthAPI = {
  async login(email, password) {
    return authAPI.login(email, password);
  },

  async register(username, password, email) {
    return authAPI.register({
      nombres: username.split(' ')[0] || username,
      apellidos: username.split(' ').slice(1).join(' ') || 'Usuario',
      correo_electronico: email,
      numero_telefono: '',
      edad: 25, // Edad por defecto
      contraseña: password
    });
  },

  async logout() {
    return authAPI.logout();
  },

  async checkAuth() {
    return authAPI.checkAuth();
  },

  async fetchProtected() {
    return authAPI.obtenerPerfil();
  }
};