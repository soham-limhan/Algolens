import { Link, useLocation, useNavigate } from 'react-router-dom';
import styles from './NotFound.module.css';

export default function NotFound() {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className={styles.page}>
      <div className={styles.backgroundGlow} aria-hidden="true" />
      <div className={styles.card}>
        <div className={styles.badge}>
          <span className={styles.badgeDot} />
          <span>Error 404 &bull; Route Not Found</span>
        </div>

        <div className={styles.errorCode}>404</div>

        <h1 className={styles.title}>Out of Bounds Exception</h1>

        <p className={styles.sub}>
          The path <code className={styles.path}>{location.pathname}</code> does not exist in our route table or has been relocated.
        </p>

        <div className={styles.codeBox}>
          <div className={styles.codeHeader}>
            <span>Console Output</span>
            <span>AlgoLens Router</span>
          </div>
          <div className={styles.codeContent}>
            <div>
              <span className={styles.keyword}>throw new</span>{' '}
              <span className={styles.type}>RouteNotFoundException</span>(
            </div>
            <div>
              &nbsp;&nbsp;<span className={styles.comment}>// Requested path:</span>{' '}
              <span className={styles.path}>"{location.pathname}"</span>
            </div>
            <div>
              &nbsp;&nbsp;<span className={styles.comment}>// Complexity: O(&infin;) time</span>
            </div>
            <div>);</div>
          </div>
        </div>

        <div className={styles.actions}>
          <Link to="/" className="btn btn-primary">
            &larr; Return Home
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
