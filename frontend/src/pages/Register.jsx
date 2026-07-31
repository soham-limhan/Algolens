import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import styles from './Auth.module.css';

export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState({});
  const [generalError, setGeneralError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const validate = () => {
    const errors = {};
    if (!name.trim()) errors.name = 'Name is required';
    else if (name.trim().length > 120) errors.name = 'Name must be 120 characters or less';

    if (!email.trim()) errors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) errors.email = 'Invalid email address format';

    if (password.length < 8) errors.password = 'Password must be at least 8 characters';
    else if (password.length > 128) errors.password = 'Password must be 128 characters or less';

    if (password !== confirmPassword) errors.confirmPassword = 'Passwords do not match';

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setGeneralError('');
    if (!validate()) return;

    setLoading(true);
    try {
      await register(name.trim(), email.trim(), password);
      navigate('/problems', { replace: true });
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        const errors = {};
        detail.forEach(item => {
          if (item.field) errors[item.field] = item.message;
        });
        setFieldErrors(errors);
      } else {
        setGeneralError(typeof detail === 'string' ? detail : 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.logo}>⬡ AlgoLens</div>
        <h1 className={styles.title}>Create account</h1>
        <p className={styles.sub}>Start measuring your solutions today</p>
        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="name">Name</label>
            <input
              id="name" type="text" value={name} required autoComplete="name"
              onChange={e => setName(e.target.value)}
              placeholder="Your name"
            />
            {fieldErrors.name && <div className={styles.error}>{fieldErrors.name}</div>}
          </div>
          <div className={styles.field}>
            <label htmlFor="email">Email</label>
            <input
              id="email" type="email" value={email} required autoComplete="email"
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
            {fieldErrors.email && <div className={styles.error}>{fieldErrors.email}</div>}
          </div>
          <div className={styles.field}>
            <label htmlFor="password">Password</label>
            <input
              id="password" type="password" value={password} required autoComplete="new-password"
              onChange={e => setPassword(e.target.value)}
              placeholder="Minimum 8 characters"
            />
            {fieldErrors.password && <div className={styles.error}>{fieldErrors.password}</div>}
          </div>
          <div className={styles.field}>
            <label htmlFor="confirm_password">Confirm Password</label>
            <input
              id="confirm_password" type="password" value={confirmPassword} required autoComplete="new-password"
              onChange={e => setConfirmPassword(e.target.value)}
              placeholder="Password should match the above"
            />
            {fieldErrors.confirmPassword && <div className={styles.error}>{fieldErrors.confirmPassword}</div>}
          </div>
          {generalError && <div className={styles.error}>{generalError}</div>}
          <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}>
            {loading ? <span className="spinner" /> : 'Create account'}
          </button>
        </form>
        <p className={styles.link}>
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}
