import { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../context/ToastContext';
import ProfileModal from './ProfileModal';
import styles from './Navbar.module.css';

function UserIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

function HistoryIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function LogoutIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [profileModalOpen, setProfileModalOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = e => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [dropdownOpen]);

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    toast.info('Logged out successfully.');
    navigate('/');
  };

  const isActive = path => location.pathname === path;

  const displayName = user?.name || (user?.email ? user.email.split('@')[0] : 'User');
  const displayEmail = user?.email || '';
  const avatarChar = (user?.name ? user.name.charAt(0) : user?.email ? user.email.charAt(0) : 'U').toUpperCase();


  return (
    <>
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
            <Link to="/forum" className={`${styles.navItem} ${isActive('/forum') ? styles.active : ''}`}>
              Discuss
            </Link>
            {user && (
              <Link to="/history" className={`${styles.navItem} ${isActive('/history') || location.pathname.startsWith('/history/') ? styles.active : ''}`}>
                History
              </Link>
            )}
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

          {user ? (
            <div className={styles.userSection} ref={dropdownRef}>
              <button
                type="button"
                className={styles.avatarBtn}
                onClick={() => setDropdownOpen(prev => !prev)}
                title="Profile & Settings"
                aria-expanded={dropdownOpen}
              >
                <div className={styles.avatarCircle}>
                  {avatarChar}
                </div>
              </button>

              {/* Profile Dropdown Menu */}
              {dropdownOpen && (
                <div className={styles.profileDropdown}>
                  <div className={styles.dropdownHeader}>
                    <div className={styles.dropdownAvatar}>{avatarChar}</div>
                    <div className={styles.dropdownUserText}>
                      <span className={styles.dropdownUserName}>{displayName}</span>
                      {displayEmail && <span className={styles.dropdownUserEmail}>{displayEmail}</span>}
                    </div>

                  </div>

                  <button
                    type="button"
                    className={styles.dropdownItem}
                    onClick={() => { setProfileModalOpen(true); setDropdownOpen(false); }}
                  >
                    <UserIcon /> Account Settings
                  </button>

                  <Link
                    to="/history"
                    className={styles.dropdownItem}
                    onClick={() => setDropdownOpen(false)}
                  >
                    <HistoryIcon /> Submission History
                  </Link>

                  <div className={styles.dropdownDivider} />

                  <button
                    type="button"
                    className={`${styles.dropdownItem} ${styles.dropdownItemDanger}`}
                    onClick={handleLogout}
                  >
                    <LogoutIcon /> Log out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className={styles.authLinks}>
              <Link to="/login" className={styles.loginLink}>Sign In</Link>
            </div>
          )}
        </div>
      </header>

      {/* Profile & Security Modal */}
      <ProfileModal
        isOpen={profileModalOpen}
        onClose={() => setProfileModalOpen(false)}
      />
    </>
  );
}

