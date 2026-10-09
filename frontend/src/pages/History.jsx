import { useEffect, useState, useMemo } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
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
  const navigate = useNavigate();
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

  const handleOpenInEditor = (solution) => {
    if (!solution) return;
    const problemId = solution.problem_id || solution.problemId;
    if (!problemId) return;
    const sourceCode = solution.source_code ?? solution.sourceCode ?? '';
    const lang = (solution.language || 'java').toLowerCase();
    setSelectedSolution(null);
    navigate(`/problems/${problemId}`, {
      state: {
        sourceCode,
        language: lang,
      },
    });
  };

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
    const distinctLangs = new Set(history.map(h => h.language).filter(Boolean)).size;

    return {
      total,
      acceptedCount: accepted.length,
      failedCount: failed.length,
      uniqueSolvedProblems,
      rate,
      distinctLangs: distinctLangs || 1,
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

  const displayName = user?.name || user?.email?.split('@')[0] || 'Coder';
  const userInitial = displayName.charAt(0).toUpperCase();

  // Compute complexity breakdown
  const complexityBreakdown = useMemo(() => {
    const counts = {};
    history.forEach(item => {
      const c = item.empirical_complexity || 'Unclassified';
      counts[c] = (counts[c] || 0) + 1;
    });
    return counts;
  }, [history]);

  return (
    <div className={styles.page}>
      {/* Personalized Welcome Header Hero */}
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <div className={styles.userGreetingRow}>
            <div className={styles.userAvatar}>
              <span>{userInitial}</span>
              <span className={styles.avatarOnlineDot} />
            </div>
            <div>
              <h1 className={styles.title}>
                Welcome, <span className={styles.userNameHighlight}>{displayName}</span>
              </h1>
            </div>
          </div>
          <p className={styles.subtitle}>
            Explore your empirical runtime benchmarks, verify asymptotic O(f(n)) scaling curves, and inspect past code submissions.
          </p>
        </div>
        <div className={styles.headerActions}>
          <Link to="/problems" className="btn btn-primary" style={{ fontSize: '0.9rem', padding: '0.65rem 1.25rem' }}>
            Explore Problems
          </Link>
          <Link to="/forum" className="btn btn-secondary" style={{ fontSize: '0.9rem', padding: '0.65rem 1.15rem' }}>
            Community Forum
          </Link>
        </div>
      </div>

      {/* Stats Summary Cards */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <span className={styles.statLabel}>Unique Solved</span>
            <span className={styles.statIconBadge} style={{ color: 'var(--accepted)' }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" />
                <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" />
                <path d="M4 22h16" />
                <path d="M10 14.66V17c0 .55-.45 1-1 1H7" />
                <path d="M14 14.66V17c0 .55.45 1 1 1h2" />
                <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
              </svg>
            </span>
          </div>
          <span className={styles.statValue} style={{ color: 'var(--accepted)' }}>
            {stats.uniqueSolvedProblems}
          </span>
          <span className={styles.statSub}>Problems with Accepted solutions</span>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <span className={styles.statLabel}>Total Submissions</span>
            <span className={styles.statIconBadge} style={{ color: 'var(--accent)' }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
              </svg>
            </span>
          </div>
          <span className={styles.statValue} style={{ color: 'var(--accent)' }}>
            {stats.total}
          </span>
          <div className={styles.submissionRatio}>
            <span className={styles.ratioPassed}>{stats.acceptedCount} Passed</span>
            <span className={styles.ratioDivider}>•</span>
            <span className={styles.ratioFailed}>{stats.failedCount} Failed</span>
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <span className={styles.statLabel}>Acceptance Rate</span>
            <span className={styles.statIconBadge} style={{ color: 'var(--text-primary)' }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="10" />
                <circle cx="12" cy="12" r="6" />
                <circle cx="12" cy="12" r="2" />
              </svg>
            </span>
          </div>
          <span className={styles.statValue} style={{ color: 'var(--text-primary)' }}>
            {stats.rate}%
          </span>
          <div className={styles.progressBar}>
            <div
              className={styles.progressFill}
              style={{ width: `${Math.min(stats.rate, 100)}%` }}
            />
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statTop}>
            <span className={styles.statLabel}>Languages Used</span>
            <span className={styles.statIconBadge} style={{ color: 'var(--text-secondary)' }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <polyline points="16 18 22 12 16 6" />
                <polyline points="8 6 2 12 8 18" />
              </svg>
            </span>
          </div>
          <span className={styles.statValue} style={{ color: 'var(--text-primary)' }}>
            {stats.distinctLangs}
          </span>
          <span className={styles.statSub}>Active runtime environments</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className={styles.filterBar}>
        <div className={styles.searchBox}>
          <span className={styles.searchIcon}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
          </span>
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
          <div className={styles.emptyIcon}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
          </div>
          <div style={{ fontWeight: 600, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
            No submissions yet
          </div>
          <div style={{ color: 'var(--text-secondary)' }}>Solve problems in the catalog to build your solution history and asymptotic profiles.</div>
          <Link to="/problems" className="btn btn-primary" style={{ marginTop: '0.75rem' }}>
            Start Practicing
          </Link>
        </div>
      )}

      {!loading && !error && history.length > 0 && filteredHistory.length === 0 && (
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="8" />
              <path d="M21 21l-4.35-4.35" />
            </svg>
          </div>
          <div style={{ color: 'var(--text-secondary)' }}>No submissions match your active filters.</div>
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
                  {item.empirical_complexity || 'N/A'}
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

      {/* Solution Code Modal */}
      {selectedSolution && (
        <div className={styles.modalOverlay} onClick={() => setSelectedSolution(null)}>
          <div className={styles.modalContent} onClick={e => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <div className={styles.modalTitle}>
                <CodeIcon />
                <span>{selectedSolution.problem_title}</span>
                <span className={styles.langBadge}>{selectedSolution.language || 'Java'}</span>
              </div>
              <div className={styles.modalHeaderActions}>
                {selectedSolution.problem_id && (
                  <button
                    type="button"
                    className={styles.openEditorHeaderBtn}
                    onClick={() => handleOpenInEditor(selectedSolution)}
                    title="Open this solution in code editor"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                      <polyline points="15 3 21 3 21 9" />
                      <line x1="10" y1="14" x2="21" y2="3" />
                    </svg>
                    <span>Open in Editor</span>
                  </button>
                )}
                <button
                  type="button"
                  className={styles.modalCloseBtn}
                  onClick={() => setSelectedSolution(null)}
                  aria-label="Close modal"
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>
            </div>

            <div className={styles.modalMeta}>
              <span>Status: <strong style={{ color: selectedSolution.status === 'complete' ? 'var(--accepted)' : 'var(--wrong)' }}>{selectedSolution.status === 'complete' ? 'Accepted' : 'Failed'}</strong></span>
              {selectedSolution.empirical_complexity && (
                <span>Complexity: <strong style={{ color: 'var(--accent)' }}>{selectedSolution.empirical_complexity}</strong></span>
              )}
              {selectedSolution.confidence_score != null && (
                <span style={{ opacity: 0.8 }}>({Math.round(selectedSolution.confidence_score * 100)}% confidence)</span>
              )}
              <span>Submitted on: {new Date(selectedSolution.submitted_at).toLocaleString()}</span>
            </div>

            {selectedSolution.complexity_reasoning && (
              <div style={{
                margin: '0.5rem 1.5rem',
                padding: '0.6rem 0.85rem',
                background: 'rgba(99, 102, 241, 0.08)',
                borderLeft: '3px solid var(--accent)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.82rem',
                color: 'var(--text-secondary)',
                lineHeight: 1.45,
              }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600, marginRight: '6px' }}>AI Complexity Analysis:</span>
                {selectedSolution.complexity_reasoning}
              </div>
            )}

            <div className={styles.modalBody}>
              <div className={styles.codeContainer}>
                <div className={styles.codeActions}>
                  {selectedSolution.problem_id && (
                    <button
                      type="button"
                      className={styles.codeActionBtn}
                      onClick={() => handleOpenInEditor(selectedSolution)}
                      title="Open this solution in code editor"
                    >
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                        <polyline points="15 3 21 3 21 9" />
                        <line x1="10" y1="14" x2="21" y2="3" />
                      </svg>
                      <span>Open in Editor</span>
                    </button>
                  )}
                  <button
                    type="button"
                    className={styles.codeActionBtn}
                    onClick={() => handleCopyCode(selectedSolution.source_code)}
                  >
                    {copied ? (
                      <>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: 4 }}>
                          <polyline points="20 6 9 17 4 12" />
                        </svg>
                        <span>Copied</span>
                      </>
                    ) : (
                      <>
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ display: 'inline-block', verticalAlign: 'middle', marginRight: 4 }}>
                          <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                        <span>Copy Code</span>
                      </>
                    )}
                  </button>
                </div>
                <pre className={styles.codeBlock}>
                  <code>{selectedSolution.source_code}</code>
                </pre>
              </div>
            </div>

            <div className={styles.modalFooter}>
              <span className={styles.modalFooterInfo}>
                Loads this solution code directly into the editor.
              </span>
              <div className={styles.modalFooterButtons}>
                <button
                  type="button"
                  className={styles.modalCloseFooterBtn}
                  onClick={() => setSelectedSolution(null)}
                >
                  Close
                </button>
                {selectedSolution.problem_id && (
                  <button
                    type="button"
                    className={styles.modalOpenEditorFooterBtn}
                    onClick={() => handleOpenInEditor(selectedSolution)}
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                      <polyline points="15 3 21 3 21 9" />
                      <line x1="10" y1="14" x2="21" y2="3" />
                    </svg>
                    <span>Open in Editor</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
