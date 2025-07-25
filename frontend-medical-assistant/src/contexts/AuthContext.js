'use client';
import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '@/lib/auth';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [paciente, setPaciente] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await authAPI.checkAuth();
      if (response.authenticated) {
        setPaciente(response.paciente);
      }
    } catch (error) {
      console.error('Error verificando autenticación:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (correoElectronico, contraseña) => {
    try {
      const response = await authAPI.login(correoElectronico, contraseña);
      if (response.success) {
        console.log("Login response:", response.paciente);
        setPaciente(response.paciente);
        console.log("Paciente en el contexto:", paciente);
        return { success: true, message: response.message };
      } else {
        return { success: false, message: response.message };
      }
    } catch (error) {
      console.error('Error de login:', error);
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  };

  const register = async (datosRegistro) => {
    try {
      const {
        nombres,
        apellidos,
        correo_electronico,
        numero_telefono,
        edad,
        contraseña
      } = datosRegistro;

      console.log(datosRegistro);

      const response = await authAPI.register({
        nombres,
        apellidos,
        correo_electronico,
        numero_telefono,
        edad,
        contraseña
      });

      if (response.success) {
        setPaciente(response.paciente);
        return { success: true, message: response.message };
      } else {
        return { success: false, message: response.message };
      }
    } catch (error) {
      console.error('Error de registro:', error);
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
      setPaciente(null);
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
      // Aún así limpiamos el estado local
      setPaciente(null);
    }
  };

  const actualizarPerfil = async () => {
    try {
      const response = await authAPI.obtenerPerfil();
      if (response.success) {
        setPaciente(response.paciente);
        return { success: true, paciente: response.paciente };
      }
      return { success: false, message: response.message };
    } catch (error) {
      console.error('Error actualizando perfil:', error);
      return { success: false, message: 'Error de conexión con el servidor' };
    }
  };

  // Función auxiliar para obtener el nombre completo del paciente
  const getNombreCompleto = () => {
    if (!paciente) return '';
    return `${paciente.nombres} ${paciente.apellidos}`;
  };

  // Función auxiliar para obtener las iniciales del paciente
  const getIniciales = () => {
    if (!paciente) return '';
    const nombres = paciente.nombres?.split(' ')[0] || '';
    const apellidos = paciente.apellidos?.split(' ')[0] || '';
    return `${nombres.charAt(0)}${apellidos.charAt(0)}`.toUpperCase();
  };

  const value = {
    // Estado principal
    paciente,
    loading,
    isAuthenticated: !!paciente,
    
    // Funciones principales
    login,
    register,
    logout,
    actualizarPerfil,
    
    // Funciones auxiliares
    getNombreCompleto,
    getIniciales,
    
    // Datos específicos del paciente para fácil acceso
    pacienteId: paciente?.id,
    nombres: paciente?.nombres,
    apellidos: paciente?.apellidos,
    correoElectronico: paciente?.correo_electronico,
    numeroTelefono: paciente?.numero_telefono,
    edad: paciente?.edad,
    fechaRegistro: paciente?.fecha_registro,
    
    // Compatibilidad con la estructura anterior (deprecated)
    user: paciente, // Para mantener compatibilidad
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe ser usado dentro de AuthProvider');
  }
  return context;
};

// Hook específico para datos del paciente
export const usePaciente = () => {
  const { paciente, isAuthenticated, getNombreCompleto, getIniciales } = useAuth();
  
  return {
    paciente,
    isAuthenticated,
    nombreCompleto: getNombreCompleto(),
    iniciales: getIniciales(),
    id: paciente?.id,
    nombres: paciente?.nombres,
    apellidos: paciente?.apellidos,
    correoElectronico: paciente?.correo_electronico,
    numeroTelefono: paciente?.numero_telefono,
    edad: paciente?.edad,
    fechaRegistro: paciente?.fecha_registro
  };
};

// Hook para manejo de autenticación
export const useAuthActions = () => {
  const { login, register, logout, loading, actualizarPerfil } = useAuth();
  
  return {
    login,
    register,
    logout,
    actualizarPerfil,
    loading
  };
};