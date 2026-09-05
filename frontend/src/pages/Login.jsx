import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../context/ToastContext';
import styles from './Auth.module.css';

function EyeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeOffIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
      <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
      <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
      <line x1="2" y1="2" x2="22" y2="22" />
    </svg>
  );
}

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/problems';

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email.trim(), password);
      toast.success('Login successful! Welcome back.');
      navigate(from, { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(d => d.message).join('. '));
      } else {
        setError(typeof detail === 'string' ? detail : 'Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>⬡ AlgoLens</div>
        <h1 className={styles.title}>Welcome back</h1>
        <p className={styles.sub}>Log in to continue practicing</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="email">Email</label>
            <input
              id="email" type="email" value={email} required autoComplete="email"
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          <div className={styles.field}>
            <label htmlFor="password">Password</label>
            <div className={styles.passwordWrapper}>
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                required
                autoComplete="current-password"
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
              />
              <button
                type="button"
                className={styles.toggleBtn}
                onClick={() => setShowPassword(prev => !prev)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                title={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOffIcon /> : <EyeIcon />}
              </button>
            </div>
            <p className={styles.link} style={{ marginTop: '0.4rem', textAlign: 'right' }}>
              <Link to="/forgetpassword">Forget Password?</Link>
            </p>
          </div>
          {error && <div className={styles.error}>{error}</div>}
          <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}>
            {loading ? <span className="spinner" /> : 'Log in'}
          </button>
        </form>
        <p className={styles.link}>
          No account? <Link to="/register">Sign up for free</Link>
        </p>
      </div>
    </div>
  );
}
