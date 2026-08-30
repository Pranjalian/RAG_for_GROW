import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../../config';

export default function AdminLogin() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/admin/login`, {
        username,
        password
      });
      localStorage.setItem('admin_token', response.data.access_token);
      navigate('/admin/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen flex flex-col items-center justify-center p-lg" style={{ width: '100vw' }}>
      <div className="glass-panel w-[400px] max-w-full p-xl rounded-2xl flex flex-col gap-lg shadow-[0_0_15px_rgba(0,0,0,0.5)]">
        <div className="text-center">
          <span className="material-symbols-outlined text-primary text-5xl mb-2">admin_panel_settings</span>
          <h2 className="font-headline-md text-headline-md font-bold text-on-surface">Admin Access</h2>
          <p className="font-caption text-caption text-on-surface-variant">Log in to manage knowledge sources</p>
        </div>

        {error && (
          <div className="bg-error-container text-on-error-container p-3 rounded-lg text-sm border border-error/20">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label className="font-title-md text-sm text-on-surface-variant">Username</label>
            <input 
              type="text" 
              className="bg-surface-container-highest border border-white/10 rounded-lg p-3 text-on-surface focus:border-primary focus:outline-none transition-colors"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>
          
          <div className="flex flex-col gap-1">
            <label className="font-title-md text-sm text-on-surface-variant">Password</label>
            <input 
              type="password" 
              className="bg-surface-container-highest border border-white/10 rounded-lg p-3 text-on-surface focus:border-primary focus:outline-none transition-colors"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>

          <button 
            type="submit" 
            disabled={isLoading}
            className="mt-2 bg-primary-container text-black font-title-md font-bold py-3 rounded-lg hover:bg-primary transition-colors flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <span className="material-symbols-outlined animate-spin">refresh</span>
            ) : (
              <>
                <span>Login</span>
                <span className="material-symbols-outlined text-sm">arrow_forward</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
