import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useResetPassword } from '../auth/AuthContext';
import styles from './ForgotPass.module.css';

export default function ResetPassword() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email || '';
  const otp = location.state?.otp || '';
  const resetPassword = useResetPassword();

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');

    if (!email) {
      navigate('/forgetpassword', { replace: true });
      return;
    }

    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await resetPassword(email, otp, password);
      navigate('/login', { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(d => d.message).join('. '));
      } else {
        setError(typeof detail === 'string' ? detail : 'Password reset failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>⬡ AlgoLens</div>
        <h1 className={styles.title}>Create New Password</h1>
        <p className={styles.sub}>Set a new password for {email || 'your account'}.</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="password">New Password</label>
            <input
              id="password"
              type="password"
              value={password}
              required
              autoComplete="new-password"
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          <div className={styles.field}>
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              required
              autoComplete="new-password"
              onChange={e => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
          {error && <div className={styles.error}>{error}</div>}
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}
          >
            {loading ? <span className="spinner" /> : 'Reset Password'}
          </button>
        </form>
        <p className={styles.link}>
          <Link to="/forgetpassword">Back</Link>
        </p>
      </div>
    </div>
  );
}
