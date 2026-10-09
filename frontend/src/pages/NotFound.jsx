import { Link, useLocation, useNavigate } from 'react-router-dom';
import styles from './NotFound.module.css';

export default function NotFound() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.errorCode}>404</div>

        <h1 className={styles.title}>Page not found</h1>

        <p className={styles.sub}>
          The requested path <code className={styles.path}>{location.pathname}</code> does not exist or has been moved.
        </p>

        <div className={styles.actions}>
          <Link to="/" className="btn btn-primary">
            Return Home
          </Link>
          <Link to="/problems" className="btn btn-secondary">
            Browse Problems
          </Link>
          <button
            type="button"
            onClick={() => navigate(-1)}
            className={`btn ${styles.backBtn}`}
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  );
}
