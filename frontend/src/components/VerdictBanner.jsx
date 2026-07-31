import styles from './VerdictBanner.module.css';

const VERDICT_META = {
  'Accepted':          { label: 'Accepted',          cls: 'accepted', icon: '✓' },
  'Wrong Answer':      { label: 'Wrong Answer',       cls: 'wrong',    icon: '✗' },
  'Compilation Error': { label: 'Compilation Error',  cls: 'cere',     icon: '⚠' },
  'Runtime Error':     { label: 'Runtime Error',      cls: 'cere',     icon: '⚠' },
  'Time Limit Exceeded':{ label:'Time Limit Exceeded',cls: 'tle',      icon: '⏱' },
};

/**
 * VerdictBanner — immediate, prominent verdict display.
 * Styled per the semantic verdict colors in the design system.
 * Uses BOTH color and icon/label for TLE to avoid relying on color alone.
 */
export default function VerdictBanner({ status, empiricalComplexity, confidence, optimalComplexity }) {
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
      <div>
        <div className={styles.label}>{meta.label}</div>
        {isAccepted && empiricalComplexity && (
          <div className={styles.sub}>
            Your complexity: <strong>{empiricalComplexity}</strong>
            {confidence != null && <span className={styles.confidence}> ({Math.round(confidence * 100)}% confidence)</span>}
            {optimalComplexity && (
              <span className={styles.optimal}> · Optimal: <strong>{optimalComplexity}</strong></span>
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
