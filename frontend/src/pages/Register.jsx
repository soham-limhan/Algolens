import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, useSendRegisterOtp } from '../auth/AuthContext';
import { useToast } from '../context/ToastContext';
import PasswordStrengthMeter from '../components/PasswordStrengthMeter';
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

export default function Register() {
  const [step, setStep] = useState(1);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({});
  const [generalError, setGeneralError] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  
  const { register } = useAuth();
  const sendRegisterOtp = useSendRegisterOtp();
  const { toast } = useToast();
  const navigate = useNavigate();

  const validateStep1 = () => {
    const errors = {};
    if (!name.trim()) errors.name = 'Name is required';
    else if (name.trim().length > 120) errors.name = 'Name must be 120 characters or less';

    if (!email.trim()) errors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) errors.email = 'Invalid email address format';

    if (password.length < 8) errors.password = 'Password must be at least 8 characters';
    else if (password.length > 128) errors.password = 'Password must not exceed 128 characters';

    if (password !== confirmPassword) errors.confirmPassword = 'Passwords do not match';

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSendOtp = async e => {
    e.preventDefault();
    setGeneralError('');
    if (!validateStep1()) return;

    setLoading(true);
    try {
      await sendRegisterOtp(email.trim(), name.trim());
      toast.success(`Verification code sent to ${email.trim()}`);
      setStep(2);
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        const errors = {};
        detail.forEach(item => {
          if (item.field) errors[item.field] = item.message;
        });
        setFieldErrors(errors);
      } else {
        setGeneralError(typeof detail === 'string' ? detail : 'Failed to send verification code');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setResending(true);
    try {
      await sendRegisterOtp(email.trim(), name.trim());
      toast.success(`New verification code sent to ${email.trim()}`);
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(typeof detail === 'string' ? detail : 'Failed to resend code');
    } finally {
      setResending(false);
    }
  };

  const handleVerifyAndRegister = async e => {
    e.preventDefault();
    setGeneralError('');

    const cleanOtp = otp.trim();
    if (cleanOtp.length !== 6) {
      setGeneralError('Please enter the 6-digit OTP.');
      return;
    }

    setLoading(true);
    try {
      await register(name.trim(), email.trim(), password, cleanOtp);
      toast.success('Registration successful! Welcome to AlgoLens.');
      navigate('/problems', { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setGeneralError(detail.map(d => d.message).join('. '));
      } else {
        setGeneralError(typeof detail === 'string' ? detail : 'Registration failed. Please check the OTP.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>⬡ AlgoLens</div>
        {step === 1 ? (
          <>
            <h1 className={styles.title}>Create account</h1>
            <p className={styles.sub}>Start measuring your solutions today</p>
            <form onSubmit={handleSendOtp} className={styles.form}>
              <div className={styles.field}>
                <label htmlFor="name">Name</label>
                <input
                  id="name"
                  type="text"
                  value={name}
                  required
                  autoComplete="name"
                  onChange={e => setName(e.target.value)}
                  placeholder="Your name"
                />
                {fieldErrors.name && <div className={styles.error}>{fieldErrors.name}</div>}
              </div>
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
                {fieldErrors.email && <div className={styles.error}>{fieldErrors.email}</div>}
              </div>
              <div className={styles.field}>
                <label htmlFor="password">Password</label>
                <div className={styles.passwordWrapper}>
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    required
                    autoComplete="new-password"
                    onChange={e => setPassword(e.target.value)}
                    placeholder="Minimum 8 characters"
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
                <PasswordStrengthMeter password={password} />
                {fieldErrors.password && <div className={styles.error}>{fieldErrors.password}</div>}
              </div>
              <div className={styles.field}>
                <label htmlFor="confirm_password">Confirm Password</label>
                <div className={styles.passwordWrapper}>
                  <input
                    id="confirm_password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    required
                    autoComplete="new-password"
                    onChange={e => setConfirmPassword(e.target.value)}
                    placeholder="Password should match the above"
                  />
                  <button
                    type="button"
                    className={styles.toggleBtn}
                    onClick={() => setShowConfirmPassword(prev => !prev)}
                    aria-label={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                    title={showConfirmPassword ? 'Hide confirm password' : 'Show confirm password'}
                  >
                    {showConfirmPassword ? <EyeOffIcon /> : <EyeIcon />}
                  </button>
                </div>
                {fieldErrors.confirmPassword && <div className={styles.error}>{fieldErrors.confirmPassword}</div>}
              </div>
              {generalError && <div className={styles.error}>{generalError}</div>}
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}
              >
                {loading ? <span className="spinner" /> : 'Continue to Verification'}
              </button>
            </form>
            <p className={styles.link}>
              Already have an account? <Link to="/login">Log in</Link>
            </p>
          </>
        ) : (
          <>
            <h1 className={styles.title}>Verify Email</h1>
            <p className={styles.sub}>
              Enter the 6-digit code sent to <strong style={{ color: 'var(--accent-light)' }}>{email}</strong>
            </p>
            <form onSubmit={handleVerifyAndRegister} className={styles.form}>
              <div className={styles.field}>
                <label htmlFor="otp">Verification Code</label>
                <input
                  id="otp"
                  type="text"
                  inputMode="numeric"
                  maxLength="6"
                  value={otp}
                  required
                  autoFocus
                  autoComplete="one-time-code"
                  onChange={e => setOtp(e.target.value.replace(/\D/g, ''))}
                  placeholder="123456"
                  style={{ textAlign: 'center', letterSpacing: '4px', fontSize: '1.25rem', fontWeight: 'bold' }}
                />
              </div>
              {generalError && <div className={styles.error}>{generalError}</div>}
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
                style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}
              >
                {loading ? <span className="spinner" /> : 'Verify & Create Account'}
              </button>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  onClick={() => { setStep(1); setGeneralError(''); }}
                  style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '0.875rem' }}
                >
                  ← Change details
                </button>
                <button
                  type="button"
                  onClick={handleResendOtp}
                  disabled={resending}
                  style={{ background: 'none', border: 'none', color: 'var(--accent)', cursor: 'pointer', fontSize: '0.875rem', fontWeight: 600 }}
                >
                  {resending ? 'Sending...' : 'Resend Code'}
                </button>
              </div>
            </form>
            <p className={styles.link}>
              Already have an account? <Link to="/login">Log in</Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
