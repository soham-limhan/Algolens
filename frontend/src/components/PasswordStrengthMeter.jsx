import styles from './PasswordStrengthMeter.module.css';

function CheckIcon() {
  return (
    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function CircleIcon() {
  return (
    <svg width="8" height="8" viewBox="0 0 24 24" fill="currentColor">
      <circle cx="12" cy="12" r="6" />
    </svg>
  );
}

const CRITERIA = [
  { id: 'length', label: 'At least 8 characters', test: p => p.length >= 8 },
  { id: 'uppercase', label: 'At least one uppercase letter (A-Z)', test: p => /[A-Z]/.test(p) },
  { id: 'lowercase', label: 'At least one lowercase letter (a-z)', test: p => /[a-z]/.test(p) },
  { id: 'number', label: 'At least one number (0-9)', test: p => /[0-9]/.test(p) },
  { id: 'special', label: 'At least one special character (!@#$...)', test: p => /[^A-Za-z0-9]/.test(p) },
];

export default function PasswordStrengthMeter({ password = '' }) {
  if (!password) return null;

  const results = CRITERIA.map(criterion => ({
    ...criterion,
    passed: criterion.test(password),
  }));

  const passedCount = results.filter(r => r.passed).length;

  const getStrengthInfo = () => {
    switch (passedCount) {
      case 0:
      case 1:
        return { label: 'Very Weak', color: '#ff375f', activeBars: 1 };
      case 2:
        return { label: 'Weak', color: '#ff7849', activeBars: 2 };
      case 3:
        return { label: 'Medium', color: '#ffc01e', activeBars: 3 };
      case 4:
        return { label: 'Strong', color: '#00b8a3', activeBars: 4 };
      case 5:
        return { label: 'Very Strong', color: '#10b981', activeBars: 4 };
      default:
        return { label: '', color: 'transparent', activeBars: 0 };
    }
  };

  const { label, color, activeBars } = getStrengthInfo();

  return (
    <div className={styles.container}>
      <div className={styles.meterHeader}>
        <span>Password strength</span>
        <span className={styles.strengthLabel} style={{ color }}>
          {label}
        </span>
      </div>

      <div className={styles.bars}>
        {[1, 2, 3, 4].map(barIndex => (
          <div
            key={barIndex}
            className={styles.bar}
            style={{
              backgroundColor: barIndex <= activeBars ? color : undefined,
              boxShadow: barIndex <= activeBars ? `0 0 6px ${color}40` : undefined,
            }}
          />
        ))}
      </div>

      <ul className={styles.checklist}>
        {results.map(item => (
          <li
            key={item.id}
            className={`${styles.item} ${item.passed ? styles.passed : ''}`}
          >
            <span className={styles.iconWrapper}>
              {item.passed ? <CheckIcon /> : <CircleIcon />}
            </span>
            <span>{item.label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
