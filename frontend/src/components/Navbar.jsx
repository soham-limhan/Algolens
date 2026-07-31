import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import styles from './Navbar.module.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchOpen, setSearchOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = path => location.pathname === path;

  return (
    <header className={styles.navbar}>
      <div className={styles.navLeft}>
        <Link to="/" className={styles.brand}>
          <svg className={styles.brandLogo} viewBox="0 0 24 24" width="22" height="22" fill="none">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#ffa116" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span className={styles.brandName}>AlgoLens</span>
        </Link>

        <nav className={styles.mainNav}>
          <Link to="/problems" className={`${styles.navItem} ${isActive('/problems') ? styles.active : ''}`}>
            Problems
          </Link>
          <a href="#contest" className={styles.navItem} onClick={e => e.preventDefault()}>Contest</a>
          <Link to="/forum" className={`${styles.navItem} ${isActive('/forum') ? styles.active : ''}`}>
            Discuss
          </Link>
          <div className={styles.navDropdown}>
            <span className={styles.navItem}>
              Interview <span className={styles.caret}>▾</span>
            </span>
          </div>
        </nav>
      </div>

      <div className={styles.navRight}>
        <div className={styles.searchBar}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
          </svg>
          <input type="text" placeholder="Search" className={styles.searchInput} />
        </div>

        <button className={styles.iconBtn} title="Notifications">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0"/>
          </svg>
        </button>

        <div className={styles.streakBadge} title="Daily Streak">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="#ffa116">
            <path d="M12 23c-4.97 0-9-4.03-9-9 0-4.97 4.03-9 9-9s9 4.03 9 9c0 4.97-4.03 9-9 9zm0-16c-3.86 0-7 3.14-7 7 0 3.86 3.14 7 7 7s7-3.14 7-7c0-3.86-3.14-7-7-7z"/>
            <path d="M12 2c.55 0 1 .45 1 1v2c0 .55-.45 1-1 1s-1-.45-1-1V3c0-.55.45-1 1-1z"/>
          </svg>
          <span className={styles.streakCount}>0</span>
        </div>

        {user ? (
          <div className={styles.userSection}>
            <Link to={`/history/${user.id}`} className={styles.userAvatar} title="User Profile">
              <div className={styles.avatarCircle}>
                {user.email ? user.email.charAt(0).toUpperCase() : 'U'}
              </div>
            </Link>
            <button onClick={handleLogout} className={styles.logoutBtn} title="Log out">
              Log out
            </button>
          </div>
        ) : (
          <div className={styles.authLinks}>
            <Link to="/login" className={styles.loginLink}>Sign In</Link>
          </div>
        )}

        <button className={styles.premiumBtn}>
          Premium
        </button>
      </div>
    </header>
  );
}
