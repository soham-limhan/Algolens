import styles from './HintCard.module.css';

/**
 * HintCard - shown only when a complexity gap exists.
 * Never reveals the optimal solution's code.
 * Uses direct, specific language (never backend vocabulary).
 */
export default function HintCard({ hint }) {
  if (!hint) return null;
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={styles.icon} aria-hidden="true">
          <path d="M12 2a7 7 0 0 0-7 7c0 2.38 1.19 4.47 3 5.74V17a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-2.26c1.81-1.27 3-3.36 3-5.74a7 7 0 0 0-7-7z" />
          <line x1="9" y1="21" x2="15" y2="21" />
        </svg>
        <span className={styles.title}>Optimization Hint</span>
      </div>
      <p className={styles.text}>{hint}</p>
    </div>
  );
}
