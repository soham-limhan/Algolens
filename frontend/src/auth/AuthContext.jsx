import { createContext, useContext, useState, useEffect } from 'react';
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from '../api/client';
import api from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUserProfile = async () => {
    try {
      const { data } = await api.get('/auth/me');
      setUser(data);
      return data;
    } catch {
      return null;
    }
  };

  // On mount — check if we have a valid token; if so, load user profile
  useEffect(() => {
    const token = getAccessToken();
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.exp * 1000 > Date.now()) {
          setUser({
            id: payload.sub,
            name: payload.name || '',
            email: payload.email || '',
          });
          fetchUserProfile();
        } else {
          clearTokens();
        }
      } catch {
        clearTokens();
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password });
    setTokens(data.access_token, data.refresh_token);
    if (data.user) {
      setUser(data.user);
    } else {
      const payload = JSON.parse(atob(data.access_token.split('.')[1]));
      setUser({ id: payload.sub, name: payload.name || '', email: payload.email || email });
      fetchUserProfile();
    }
    return data;
  };

  const register = async (name, email, password) => {
    const { data } = await api.post('/auth/register', { name, email, password });
    setTokens(data.access_token, data.refresh_token);
    if (data.user) {
      setUser(data.user);
    } else {
      const payload = JSON.parse(atob(data.access_token.split('.')[1]));
      setUser({ id: payload.sub, name: name || payload.name, email: email || payload.email });
      fetchUserProfile();
    }
    return data;
  };


  const updateProfile = async (name) => {
    const { data } = await api.patch('/auth/profile', { name });
    setUser(prev => ({ ...prev, ...data }));
    return data;
  };

  const changePassword = async (currentPassword, newPassword) => {
    const { data } = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return data;
  };

  const forgetPassword = async (email) => {
    const { data } = await api.post('/auth/forgot-password', { email });
    return data;
  };

  const verifyOtp = async (email, otp) => {
    const { data } = await api.post('/auth/verify-otp', { email, otp });
    return data;
  };

  const resetPassword = async (email, otp, newPassword) => {
    const { data } = await api.post('/auth/reset-password', { email, otp, new_password: newPassword });
    return data;
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, updateProfile, changePassword, forgetPassword, verifyOtp, resetPassword, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);


export const useForgetpassword = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useForgetpassword must be used within an AuthProvider');
  }
  return context.forgetPassword;
};

export const useVerifyOtp = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useVerifyOtp must be used within an AuthProvider');
  }
  return context.verifyOtp;
};

export const useResetPassword = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useResetPassword must be used within an AuthProvider');
  }
  return context.resetPassword;
};
