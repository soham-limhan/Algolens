import styles from './VerdictBanner.module.css';

const VERDICT_META = {
  'Accepted': {
    label: 'Accepted',
    cls: 'accepted',
    icon: (
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <polyline points="20 6 9 17 4 12" />
      </svg>
    ),
  },
  'Wrong Answer': {
    label: 'Wrong Answer',
    cls: 'wrong',
    icon: (
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    ),
  },
  'Compilation Error': {
    label: 'Compilation Error',
    cls: 'cere',
    icon: (
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
  },
  'Runtime Error': {
    label: 'Runtime Error',
    cls: 'cere',
    icon: (
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    ),
  },
  'Time Limit Exceeded': {
    label: 'Time Limit Exceeded',
    cls: 'tle',
    icon: (
      <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
      </svg>
    ),
  },
};

/**
 * VerdictBanner - immediate, prominent verdict display.
 * Styled per the semantic verdict colors in the design system.
 * Uses BOTH color and icon/label for TLE to avoid relying on color alone.
 */
export default function VerdictBanner({ status, empiricalComplexity, confidence, optimalComplexity, complexityReasoning }) {
  if (!status || status === 'pending' || status === 'running_correctness' || status === 'benchmarking') {
    return (
      <div className={styles.banner} data-variant="pending">
        <span className={styles.icon}>
          <span className="spinner" style={{ display: 'inline-block' }} />
        </span>
        <div>
          <div className={styles.label}>Judging…</div>
          <div className={styles.sub}>{statusLabel(status)}</div>
        </div>
      </div>
    );
  }

  const isAccepted = status === 'complete';
  const verdictKey = isAccepted ? 'Accepted' : status;
  const meta = VERDICT_META[verdictKey] || { label: verdictKey, cls: 'wrong', icon: '!' };

  return (
    <div className={styles.banner} data-variant={meta.cls}>
      <span className={styles.icon}>{meta.icon}</span>
      <div style={{ flex: 1 }}>
        <div className={styles.label}>{meta.label}</div>
        {isAccepted && empiricalComplexity && (
          <div className={styles.sub}>
            <div className={styles.complexityRow}>
              <span>Your complexity: <strong>{empiricalComplexity}</strong></span>
              {confidence != null && <span className={styles.confidence}> ({Math.round(confidence * 100)}% confidence)</span>}
              {optimalComplexity && (
                <span className={styles.optimal}> · Optimal: <strong>{optimalComplexity}</strong></span>
              )}
              <span className={styles.aiTag}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
                </svg>
                AI Evaluated
              </span>
            </div>
            {complexityReasoning && (
              <div className={styles.reasoningRow}>
                {complexityReasoning}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function statusLabel(s) {
  const map = {
    pending: 'Waiting to start…',
    running_correctness: 'Checking test cases…',
    benchmarking: 'Benchmarking performance…',
  };
  return map[s] || '';
}
