import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import api from '../api/client';
import styles from './History.module.css';

const STATUS_STYLE = {
  complete: { color: 'var(--accepted)', label: 'Accepted' },
  failed:   { color: 'var(--wrong)',    label: 'Failed' },
  pending:  { color: 'var(--text-dim)', label: 'Pending' },
};

export default function History() {
  const { userId } = useParams();
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const id = userId || user?.id;
    if (!id) return;
    api.get(`/users/${id}/history`)
      .then(r => setHistory(r.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load history'))
      .finally(() => setLoading(false));
  }, [userId, user]);

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Submission History</h1>
        <Link to="/problems" className="btn btn-secondary" style={{ fontSize: '0.85rem' }}>
          Browse problems
        </Link>
      </div>

      {loading && <div className={styles.center}><div className="spinner" /></div>}
      {error && <div className={styles.error}>{error}</div>}

      {!loading && !error && history.length === 0 && (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>📋</div>
          <div>No submissions yet.</div>
          <Link to="/problems" className="btn btn-primary" style={{ marginTop: '1rem' }}>
            Start practicing
          </Link>
        </div>
      )}

      {!loading && history.length > 0 && (
        <div className={styles.table}>
          <div className={styles.tableHead}>
            <span>Problem</span>
            <span>Verdict</span>
            <span>Complexity</span>
            <span>Date</span>
          </div>
          {history.map(item => {
            const status = STATUS_STYLE[item.status] || STATUS_STYLE.pending;
            return (
              <Link key={item.id} to={`/results/${item.id}`} className={styles.row}>
                <span className={styles.problem}>{item.problem_title}</span>
                <span style={{ color: status.color, fontWeight: 600, fontSize: '0.88rem' }}>
                  {status.label}
                </span>
                <span className={styles.mono}>
                  {item.empirical_complexity || '—'}
                </span>
                <span className={styles.date}>
                  {new Date(item.submitted_at).toLocaleDateString('en-GB', {
                    day: 'numeric', month: 'short', year: 'numeric',
                  })}
                </span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
