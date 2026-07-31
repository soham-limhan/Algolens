import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useVerifyOtp } from '../auth/AuthContext';
import styles from './ForgotPass.module.css';

export default function VerifyOtp() {
  const [otp, setOtp] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const email = location.state?.email || '';
  const verifyOtp = useVerifyOtp();

  const handleSubmit = async e => {
    e.preventDefault();
    setError('');

    if (!email) {
      navigate('/forgetpassword', { replace: true });
      return;
    }

    const cleanOtp = otp.trim();
    if (cleanOtp.length !== 6) {
      setError('Please enter the 6-digit OTP.');
      return;
    }

    setLoading(true);

    try {
      await verifyOtp(email, cleanOtp);
      navigate('/reset-password', {
        replace: true,
        state: { email, otp: cleanOtp },
      });
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(d => d.message).join('. '));
      } else {
        setError(typeof detail === 'string' ? detail : 'Verification failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>⬡ AlgoLens</div>
        <h1 className={styles.title}>Verify OTP</h1>
        <p className={styles.sub}>Enter the 6-digit code sent to {email || 'your email'}.</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="otp">OTP</label>
            <input
              id="otp"
              type="text"
              inputMode="numeric"
              maxLength="6"
              value={otp}
              required
              autoComplete="one-time-code"
              onChange={e => setOtp(e.target.value.replace(/\D/g, ''))}
              placeholder="123456"
            />
          </div>
          {error && <div className={styles.error}>{error}</div>}
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}
          >
            {loading ? <span className="spinner" /> : 'Verify OTP'}
          </button>
        </form>
        <p className={styles.link}>
          <Link to="/forgetpassword">Back</Link>
        </p>
      </div>
    </div>
  );
}
