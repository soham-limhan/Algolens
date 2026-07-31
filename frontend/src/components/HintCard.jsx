import styles from './HintCard.module.css';

/**
 * HintCard — shown only when a complexity gap exists.
 * Never reveals the optimal solution's code.
 * Uses direct, specific language (never backend vocabulary).
 */
export default function HintCard({ hint }) {
  if (!hint) return null;
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <span className={styles.icon}>💡</span>
        <span className={styles.title}>Optimization Hint</span>
      </div>
      <p className={styles.text}>{hint}</p>
    </div>
  );
}
