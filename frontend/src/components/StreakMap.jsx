import { useState, useEffect } from 'react';
import styles from './StreakMap.module.css';

export default function StreakMap({
  initialStreakDay = 30,
  initialCheckedDays = [30],
  initialDiamonds = 0,
  monthNumber = 7,
  monthName = 'Jul',
  startDayOffset = 0, // 0 offset so Day 1 starts under Sunday (S)
}) {
  const [checkedDays, setCheckedDays] = useState(() => new Set(initialCheckedDays));
  const [diamonds, setDiamonds] = useState(initialDiamonds);
  const [showRules, setShowRules] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const [timeLeft, setTimeLeft] = useState('07:41:58');

  // Days of week header
  const weekDays = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

  // July has 31 days
  const totalDays = 31;

  // Countdown timer simulation to end of day
  useEffect(() => {
    let secondsTotal = 7 * 3600 + 41 * 60 + 58;

    const timer = setInterval(() => {
      secondsTotal = secondsTotal > 0 ? secondsTotal - 1 : 86400;
      const h = String(Math.floor(secondsTotal / 3600)).padStart(2, '0');
      const m = String(Math.floor((secondsTotal % 3600) / 60)).padStart(2, '0');
      const s = String(secondsTotal % 60).padStart(2, '0');
      setTimeLeft(`${h}:${m}:${s}`);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleDayClick = (day) => {
    setCheckedDays((prev) => {
      const updated = new Set(prev);
      if (updated.has(day)) {
        updated.delete(day);
      } else {
        updated.add(day);
        setDiamonds((d) => d + 10);
      }
      return updated;
    });
  };

  const handleRedeem = () => {
    alert(`Redeemed! Current Diamond balance: ${diamonds} 💎`);
  };

  // Build calendar cells (empty offset cells + day numbers)
  const calendarCells = [];
  for (let i = 0; i < startDayOffset; i++) {
    calendarCells.push({ isBlank: true, id: `empty-${i}` });
  }
  for (let day = 1; day <= totalDays; day++) {
    calendarCells.push({ isBlank: false, day, id: `day-${day}` });
  }

  return (
    <div className={styles.streakCard}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.titleContainer}>
          <h2 className={styles.dayTitle}>Day {initialStreakDay}</h2>
          <span className={styles.timerSubtitle}>{timeLeft} left</span>
        </div>
        <div className={styles.monthBadge}>
          <span className={styles.monthNum}>{monthNumber}</span>
          <span className={styles.monthText}>{monthName}</span>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className={styles.calendarContainer}>
        <div className={styles.weekDaysHeader}>
          {weekDays.map((wd, index) => (
            <span key={index} className={styles.weekDayName}>
              {wd}
            </span>
          ))}
        </div>

        <div className={styles.daysGrid}>
          {calendarCells.map((cell) => {
            if (cell.isBlank) {
              return <div key={cell.id} className={`${styles.dayCell} ${styles.emptyCell}`} />;
            }

            const isChecked = checkedDays.has(cell.day);
            const isToday = cell.day === initialStreakDay && !isChecked;

            return (
              <div
                key={cell.id}
                onClick={() => handleDayClick(cell.day)}
                className={`${styles.dayCell} ${isChecked ? styles.checkedCell : ''} ${
                  isToday ? styles.todayCell : ''
                }`}
                title={`Day ${cell.day} ${isChecked ? '(Checked in)' : ''}`}
              >
                {isChecked ? (
                  <svg className={styles.checkmarkIcon} viewBox="0 0 24 24">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  cell.day
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className={styles.divider} />

      {/* Weekly Premium Section */}
      <div className={styles.weeklySection}>
        <div className={styles.weeklyLabel}>
          <span>Weekly Premium</span>
          <button
            className={styles.infoBtn}
            onClick={() => setShowInfo(!showInfo)}
            title="Weekly info"
          >
            ⓘ
          </button>
        </div>

        <div className={styles.weeksList}>
          <span className={styles.weekBadge}>W1</span>
          <span className={styles.weekBadge}>W2</span>
          <span className={styles.weekBadge}>W3</span>
          <span className={styles.weekBadge}>W4</span>
          <span className={`${styles.weekBadge} ${styles.weekBadgeActive}`}>W5</span>
        </div>
      </div>

      {/* Footer Action Bar */}
      <div className={styles.footerBar}>
        <button className={styles.redeemBtn} onClick={handleRedeem}>
          💎 {diamonds} Redeem
        </button>

        <button className={styles.rulesLink} onClick={() => setShowRules(true)}>
          Rules
        </button>
      </div>

      {/* Rules Modal */}
      {showRules && (
        <div className={styles.modalOverlay}>
          <div>
            <div className={styles.modalTitle}>Streak Rules</div>
            <ul className={styles.rulesList}>
              <li>Check in daily to build and preserve your solving streak!</li>
              <li>Every successful check-in grants +10 💎 diamonds.</li>
              <li>Complete 7 consecutive days to unlock Weekly Premium rewards.</li>
              <li>Use your earned diamonds to redeem streak freeze cards or exclusive badges.</li>
            </ul>
          </div>
          <button className={styles.closeBtn} onClick={() => setShowRules(false)}>
            Close
          </button>
        </div>
      )}

      {/* Info Modal */}
      {showInfo && (
        <div className={styles.modalOverlay}>
          <div>
            <div className={styles.modalTitle}>Weekly Premium Rewards</div>
            <p style={{ fontSize: '11px', color: '#cbd5e1', lineHeight: '1.4' }}>
              Maintain check-in streaks across all weeks (W1-W5) to claim bonus diamonds, profile themes, and double XP boosters at the end of the month!
            </p>
          </div>
          <button className={styles.closeBtn} onClick={() => setShowInfo(false)}>
            Got it
          </button>
        </div>
      )}
    </div>
  );
}
