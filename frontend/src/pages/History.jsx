import { useEffect, useState, useMemo } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import api from '../api/client';
import styles from './History.module.css';

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function CrossIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

function ClockIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function CodeIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="16 18 22 12 16 6" />
      <polyline points="8 6 2 12 8 18" />
    </svg>
  );
}

function ChartIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  );
}

export default function History() {
  const { userId } = useParams();
  const { user } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all | complete | failed
  const [langFilter, setLangFilter] = useState('all');

  // Solution Preview Modal
  const [selectedSolution, setSelectedSolution] = useState(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const id = userId || user?.id;
    if (!id) return;
    setLoading(true);
    api.get(`/users/${id}/history`)
      .then(r => setHistory(r.data))
      .catch(err => setError(err.response?.data?.detail || 'Failed to load submission history'))
      .finally(() => setLoading(false));
  }, [userId, user]);

  // Unique languages in history
  const availableLanguages = useMemo(() => {
    const langs = new Set(history.map(item => item.language).filter(Boolean));
    return ['all', ...Array.from(langs)];
  }, [history]);

  // Statistics
  const stats = useMemo(() => {
    const total = history.length;
    const accepted = history.filter(h => h.status === 'complete');
    const failed = history.filter(h => h.status === 'failed');
    const uniqueSolvedProblems = new Set(accepted.map(h => h.problem_title)).size;
    const rate = total > 0 ? Math.round((accepted.length / total) * 100) : 0;

    return {
      total,
      acceptedCount: accepted.length,
      failedCount: failed.length,
      uniqueSolvedProblems,
      rate,
    };
  }, [history]);

  // Filtered submissions
  const filteredHistory = useMemo(() => {
    return history.filter(item => {
      // Search by title
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        if (!item.problem_title.toLowerCase().includes(q)) {
          return false;
        }
      }

      // Filter by status
      if (statusFilter !== 'all') {
        if (item.status !== statusFilter) {
          return false;
        }
      }

      // Filter by language
      if (langFilter !== 'all') {
        if (item.language?.toLowerCase() !== langFilter.toLowerCase()) {
          return false;
        }
      }

      return true;
    });
  }, [history, searchQuery, statusFilter, langFilter]);

  const handleCopyCode = (code) => {
    if (!code) return;
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={styles.page}>
      {/* Page Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>
            Submission & Solution History
            <span className={styles.titleBadge}>{stats.total} total</span>
          </h1>
        </div>
        <Link to="/problems" className="btn btn-primary" style={{ fontSize: '0.88rem' }}>
          Explore Problems
        </Link>
      </div>

      {/* Stats Summary Cards */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <span className={styles.statLabel}>Unique Solved</span>
          <span className={styles.statValue} style={{ color: '#00b8a3' }}>
            {stats.uniqueSolvedProblems}
          </span>
          <span className={styles.statSub}>Problems with Accepted solutions</span>
        </div>

        <div className={styles.statCard}>
          <span className={styles.statLabel}>Total Submissions</span>
          <span className={styles.statValue}>
            {stats.total}
          </span>
          <span className={styles.statSub}>{stats.acceptedCount} Passed / {stats.failedCount} Failed</span>
        </div>

        <div className={styles.statCard}>
          <span className={styles.statLabel}>Acceptance Rate</span>
          <span className={styles.statValue} style={{ color: 'var(--accent)' }}>
            {stats.rate}%
          </span>
          <span className={styles.statSub}>Overall success ratio</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className={styles.filterBar}>
        <div className={styles.searchBox}>
          <span className={styles.searchIcon}>🔍</span>
          <input
            type="text"
            placeholder="Search problems in history..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className={styles.searchInput}
          />
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <div className={styles.filterTabs}>
            <button
              className={`${styles.tabBtn} ${statusFilter === 'all' ? styles.tabBtnActive : ''}`}
              onClick={() => setStatusFilter('all')}
            >
              All ({history.length})
            </button>
            <button
              className={`${styles.tabBtn} ${statusFilter === 'complete' ? styles.tabBtnActive : ''}`}
              onClick={() => setStatusFilter('complete')}
            >
              Accepted ({stats.acceptedCount})
            </button>
            <button
              className={`${styles.tabBtn} ${statusFilter === 'failed' ? styles.tabBtnActive : ''}`}
              onClick={() => setStatusFilter('failed')}
            >
              Failed ({stats.failedCount})
            </button>
          </div>

          {availableLanguages.length > 2 && (
            <select
              value={langFilter}
              onChange={e => setLangFilter(e.target.value)}
              className={styles.langSelect}
            >
              {availableLanguages.map(lang => (
                <option key={lang} value={lang}>
                  {lang === 'all' ? 'All Languages' : lang.toUpperCase()}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {/* Content State */}
      {loading && (
        <div className={styles.center}>
          <div className="spinner" />
        </div>
      )}

      {error && <div className={styles.error}>{error}</div>}

      {!loading && !error && history.length === 0 && (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>📋</div>
          <div style={{ fontWeight: 600, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
            No submissions yet
          </div>
          <div>Solve problems to start building your solution library!</div>
          <Link to="/problems" className="btn btn-primary" style={{ marginTop: '0.75rem' }}>
            Start Practicing
          </Link>
        </div>
      )}

      {!loading && !error && history.length > 0 && filteredHistory.length === 0 && (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>🔍</div>
          <div>No submissions match your active filters.</div>
          <button
            className="btn btn-secondary"
            onClick={() => { setSearchQuery(''); setStatusFilter('all'); setLangFilter('all'); }}
            style={{ marginTop: '0.75rem' }}
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Submissions Table */}
      {!loading && filteredHistory.length > 0 && (
        <div className={styles.tableContainer}>
          <div className={styles.tableHead}>
            <span>Verdict</span>
            <span>Problem</span>
            <span>Language</span>
            <span>Complexity</span>
            <span>Date</span>
            <span style={{ textAlign: 'right' }}>Actions</span>
          </div>

          {filteredHistory.map(item => {
            const isAccepted = item.status === 'complete';
            const isFailed = item.status === 'failed';

            return (
              <div key={item.id} className={styles.row}>
                {/* Status Verdict */}
                <div>
                  {isAccepted ? (
                    <span className={styles.badgeAccepted}>
                      <CheckIcon /> Accepted
                    </span>
                  ) : isFailed ? (
                    <span className={styles.badgeFailed}>
                      <CrossIcon /> Failed
                    </span>
                  ) : (
                    <span className={styles.badgePending}>
                      <ClockIcon /> Pending
                    </span>
                  )}
                </div>

                {/* Problem Title Link */}
                <div>
                  <Link
                    to={item.problem_id ? `/problems/${item.problem_id}` : `/results/${item.id}`}
                    state={item.problem_id ? {
                      sourceCode: item.source_code,
                      language: item.language?.toLowerCase(),
                    } : undefined}
                    className={styles.problemLink}
                    title={item.problem_title}
                  >
                    {item.problem_title}
                  </Link>
                </div>

                {/* Language */}
                <div>
                  <span className={styles.langBadge}>{item.language || 'Java'}</span>
                </div>

                {/* Empirical Complexity */}
                <div className={styles.mono}>
                  {item.empirical_complexity || '—'}
                </div>

                {/* Submission Date */}
                <div className={styles.date}>
                  {new Date(item.submitted_at).toLocaleDateString('en-GB', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  })}
                </div>

                {/* Action Buttons */}
                <div className={styles.actions}>
                  {item.source_code && (
                    <button
                      type="button"
                      className={styles.viewBtn}
                      onClick={() => { setSelectedSolution(item); setCopied(false); }}
                      title="View submitted solution code"
                    >
                      <CodeIcon /> Solution
                    </button>
                  )}
                  <Link
                    to={`/results/${item.id}`}
                    className={styles.resultsBtn}
                    title="View benchmark curve and AI insights"
                  >
                    <ChartIcon /> Benchmark
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Solution Preview Modal */}
      {selectedSolution && (
        <div className={styles.modalOverlay} onClick={() => setSelectedSolution(null)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitle}>
                <CodeIcon />
                <span>{selectedSolution.problem_title}</span>
              </div>
              <button
                type="button"
                className={styles.modalCloseBtn}
                onClick={() => setSelectedSolution(null)}
                aria-label="Close solution modal"
              >
                ✕
              </button>
            </div>

            <div className={styles.modalMeta}>
              <span>Status: <strong style={{ color: selectedSolution.status === 'complete' ? '#00b8a3' : '#ff375f' }}>{selectedSolution.status === 'complete' ? 'Accepted' : 'Failed'}</strong></span>
              <span>Language: <strong>{selectedSolution.language?.toUpperCase() || 'JAVA'}</strong></span>
              {selectedSolution.empirical_complexity && (
                <span>Complexity: <strong className={styles.mono}>{selectedSolution.empirical_complexity}</strong></span>
              )}
              <span>Submitted: {new Date(selectedSolution.submitted_at).toLocaleString()}</span>
            </div>

            <div className={styles.modalBody}>
              <div className={styles.codeContainer}>
                <button
                  type="button"
                  className={styles.copyCodeBtn}
                  onClick={() => handleCopyCode(selectedSolution.source_code)}
                >
                  {copied ? '✓ Copied!' : 'Copy Code'}
                </button>
                <pre className={styles.codeBlock}>
                  <code>{selectedSolution.source_code}</code>
                </pre>
              </div>
            </div>

            <div className={styles.modalFooter}>
              <Link
                to={`/results/${selectedSolution.id}`}
                className="btn btn-secondary"
                style={{ fontSize: '0.85rem' }}
              >
                View Full Benchmark Results ↗
              </Link>
              {selectedSolution.problem_id && (
                <Link
                  to={`/problems/${selectedSolution.problem_id}`}
                  state={{
                    sourceCode: selectedSolution.source_code,
                    language: selectedSolution.language?.toLowerCase(),
                  }}
                  className="btn btn-primary"
                  style={{ fontSize: '0.85rem' }}
                >
                  Open in Workspace ↗
                </Link>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
