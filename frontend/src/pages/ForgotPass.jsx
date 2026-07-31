import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useForgetpassword } from '../auth/AuthContext';
import styles from './ForgotPass.module.css';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/forgetpassword';
  const forgetPassword = useForgetpassword();

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await forgetPassword(email.trim());
      navigate('/verify-otp', {
        replace: true,
        state: { email: email.trim() },
      });
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(d => d.message).join('. '));
      } else {
        setError(typeof detail === 'string' ? detail : 'Failed to send the OTP');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>⬡ AlgoLens</div>
        <h1 className={styles.title}>Forgot Password</h1>
        <p className={styles.sub}>Enter your email to send the One-Time-Passcode (OTP)</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              required
              autoComplete="email"
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </div>
          {error && <div className={styles.error}>{error}</div>}
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}
          >
            {loading ? <span className="spinner" /> : 'Send OTP'}
          </button>
        </form>
      </div>
    </div>
  );
}