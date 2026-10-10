import { useState, useRef, useEffect, useMemo } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { useToast } from '../context/ToastContext';
import api from '../api/client';
import ProfileModal from './ProfileModal';
import algolensLogo from '../assets/algolenslogo.png';
import styles from './Navbar.module.css';

function UserIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );
}

function HistoryIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <polyline points="12 6 12 12 16 14" />
    </svg>
  );
}

function LogoutIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
      <polyline points="16 17 21 12 16 7" />
      <line x1="21" y1="12" x2="9" y2="12" />
    </svg>
  );
}

function MenuIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="3" y1="12" x2="21" y2="12" />
      <line x1="3" y1="6" x2="21" y2="6" />
      <line x1="3" y1="18" x2="21" y2="18" />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
}

export default function Navbar() {
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();

  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [profileModalOpen, setProfileModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchDropdownOpen, setSearchDropdownOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [problems, setProblems] = useState([]);

  const dropdownRef = useRef(null);
  const searchInputRef = useRef(null);
  const searchContainerRef = useRef(null);

  // Proactively fetch problem catalogue for instant search autocompletion
  useEffect(() => {
    let isMounted = true;
    api.get('/problems')
      .then((r) => {
        if (isMounted) setProblems(r.data || []);
      })
      .catch(() => {
        if (isMounted) setProblems([]);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  // Filter matching problems for dropdown preview
  const matchingProblems = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return [];
    return problems
      .filter((p, index) => {
        const title = (p.title || '').toLowerCase();
        const cleanTitle = title.replace(/^[0-9]+\.\s*/, '').trim();
        const id = String(p.id || '').toLowerCase();
        const num = String(index + 1);
        return title.includes(q) || cleanTitle.includes(q) || id.includes(q) || num === q;
      })
      .slice(0, 6);
  }, [searchQuery, problems]);

  // Close menus when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
      if (searchContainerRef.current && !searchContainerRef.current.contains(e.target)) {
        setSearchDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close on route change
  useEffect(() => {
    setMobileMenuOpen(false);
    setDropdownOpen(false);
    setSearchDropdownOpen(false);
  }, [location.pathname]);

  // Keyboard accessibility: Escape key closes menus, "/" focuses search
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setDropdownOpen(false);
        setMobileMenuOpen(false);
        setSearchDropdownOpen(false);
      }
      // Quick search shortcut "/"
      if (e.key === '/' && document.activeElement !== searchInputRef.current && !['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
        e.preventDefault();
        searchInputRef.current?.focus();
        setSearchDropdownOpen(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleLogout = () => {
    logout();
    setDropdownOpen(false);
    setMobileMenuOpen(false);
    toast.info('Logged out successfully.');
    navigate('/');
  };

  const handleSearchKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      if (!searchDropdownOpen || matchingProblems.length === 0) return;
      e.preventDefault();
      setSelectedIndex((prev) => (prev < matchingProblems.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      if (!searchDropdownOpen || matchingProblems.length === 0) return;
      e.preventDefault();
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : matchingProblems.length - 1));
    } else if (e.key === 'Escape') {
      setSearchDropdownOpen(false);
    }
  };

  const handleSelectProblem = (probId) => {
    navigate(`/problems/${probId}`);
    setSearchQuery('');
    setSearchDropdownOpen(false);
    if (searchInputRef.current) searchInputRef.current.blur();
    setMobileMenuOpen(false);
  };

  const handleSearchSubmit = (e) => {
    if (e) e.preventDefault();
    const query = searchQuery.trim();
    setSearchDropdownOpen(false);

    if (selectedIndex >= 0 && matchingProblems[selectedIndex]) {
      handleSelectProblem(matchingProblems[selectedIndex].id);
      return;
    }

    if (query) {
      navigate(`/problems?search=${encodeURIComponent(query)}`);
      setSearchQuery('');
      if (searchInputRef.current) searchInputRef.current.blur();
      setMobileMenuOpen(false);
    } else {
      navigate('/problems');
    }
  };

  const isActive = (path) => location.pathname === path;
  const displayName = user?.name || (user?.email ? user.email.split('@')[0] : 'User');
  const displayEmail = user?.email || '';
  const avatarChar = (user?.name ? user.name.charAt(0) : user?.email ? user.email.charAt(0) : 'U').toUpperCase();

  return (
    <>
      <header className={styles.navbar}>
        <div className={styles.navLeft}>
          <Link to="/" className={styles.brand} aria-label="AlgoLens Home">
            <div className={styles.brandLogoWrap}>
              <img src={algolensLogo} alt="" className={styles.brandLogoImg} />
            </div>
            <span className={styles.brandName}>AlgoLens</span>
          </Link>

          <nav className={styles.desktopNav} aria-label="Main Navigation">
            <Link
              to="/problems"
              className={`${styles.navItem} ${isActive('/problems') ? styles.active : ''}`}
            >
              Problems
            </Link>
            <Link
              to="/forum"
              className={`${styles.navItem} ${isActive('/forum') ? styles.active : ''}`}
            >
              Discuss
            </Link>
            {user && (
              <Link
                to="/history"
                className={`${styles.navItem} ${isActive('/history') || location.pathname.startsWith('/history/') ? styles.active : ''}`}
              >
                History
              </Link>
            )}
          </nav>
        </div>

        <div className={styles.navRight}>
          {/* Functional Problem Search Bar with Dropdown Preview */}
          <div className={styles.searchContainer} ref={searchContainerRef}>
            <form className={styles.searchBar} onSubmit={handleSearchSubmit}>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className={styles.searchIcon}
                aria-hidden="true"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="M21 21l-4.35-4.35" />
              </svg>
              <input
                ref={searchInputRef}
                type="text"
                placeholder="Search problems... (/)"
                className={styles.searchInput}
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setSearchDropdownOpen(true);
                  setSelectedIndex(-1);
                }}
                onFocus={() => {
                  if (searchQuery.trim()) setSearchDropdownOpen(true);
                }}
                onKeyDown={handleSearchKeyDown}
                aria-label="Search problems"
                aria-expanded={searchDropdownOpen && Boolean(searchQuery.trim())}
                aria-autocomplete="list"
              />
              {searchQuery && (
                <button
                  type="button"
                  className={styles.clearSearchBtn}
                  onClick={() => {
                    setSearchQuery('');
                    setSearchDropdownOpen(false);
                    searchInputRef.current?.focus();
                  }}
                  title="Clear search"
                  aria-label="Clear search"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              )}
            </form>

            {/* Instant Search Autocomplete Dropdown */}
            {searchDropdownOpen && searchQuery.trim() && (
              <div className={styles.searchDropdown} role="listbox">
                <div className={styles.searchDropdownHeader}>
                  <span>Matching Challenges</span>
                  <span className={styles.searchDropdownShortcut}>ESC to close</span>
                </div>

                {matchingProblems.length > 0 ? (
                  <ul className={styles.searchDropdownList}>
                    {matchingProblems.map((p, idx) => {
                      const isSql = Boolean(p.generator_key?.startsWith('sql_') || p.title?.toLowerCase().includes('sql'));
                      const diffNorm = (p.difficulty || 'Easy').toLowerCase();
                      const diffClass = diffNorm === 'hard' ? styles.diffHard : diffNorm === 'medium' || diffNorm === 'med.' ? styles.diffMedium : styles.diffEasy;
                      const isSelected = idx === selectedIndex;

                      return (
                        <li
                          key={p.id}
                          className={`${styles.searchDropdownItem} ${isSelected ? styles.searchDropdownItemSelected : ''}`}
                          onClick={() => handleSelectProblem(p.id)}
                          onMouseEnter={() => setSelectedIndex(idx)}
                          role="option"
                          aria-selected={isSelected}
                        >
                          <div className={styles.searchDropdownItemMain}>
                            <span className={styles.searchDropdownItemTitle}>{p.title}</span>
                          </div>
                          <div className={styles.searchDropdownBadges}>
                            {isSql && <span className={styles.sqlBadge}>SQL</span>}
                            <span className={`${styles.diffBadge} ${diffClass}`}>
                              {p.difficulty ? p.difficulty.charAt(0).toUpperCase() + p.difficulty.slice(1).toLowerCase() : 'Easy'}
                            </span>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <div className={styles.searchDropdownEmpty}>
                    No problems match &ldquo;{searchQuery}&rdquo;
                  </div>
                )}

                <button
                  type="button"
                  className={styles.searchDropdownFooter}
                  onClick={handleSearchSubmit}
                >
                  <span>View all results for &ldquo;{searchQuery}&rdquo;</span>
                  <span aria-hidden="true">&rarr;</span>
                </button>
              </div>
            )}
          </div>

          {user ? (
            <div className={styles.userSection} ref={dropdownRef}>
              <button
                type="button"
                className={styles.avatarBtn}
                onClick={() => setDropdownOpen((prev) => !prev)}
                title="Account menu"
                aria-label="User account menu"
                aria-haspopup="true"
                aria-expanded={dropdownOpen}
              >
                <div className={styles.welcomePill}>
                  <span className={styles.welcomeName}>{displayName}</span>
                </div>
                <div className={styles.avatarCircle}>{avatarChar}</div>
              </button>

              {/* Profile Dropdown Menu */}
              {dropdownOpen && (
                <div className={styles.profileDropdown} role="menu">
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
                    role="menuitem"
                    onClick={() => {
                      setProfileModalOpen(true);
                      setDropdownOpen(false);
                    }}
                  >
                    <UserIcon /> Account Settings
                  </button>

                  <Link
                    to="/history"
                    className={styles.dropdownItem}
                    role="menuitem"
                    onClick={() => setDropdownOpen(false)}
                  >
                    <HistoryIcon /> Submission History
                  </Link>

                  <div className={styles.dropdownDivider} />

                  <button
                    type="button"
                    className={`${styles.dropdownItem} ${styles.dropdownItemDanger}`}
                    role="menuitem"
                    onClick={handleLogout}
                  >
                    <LogoutIcon /> Log out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className={styles.authLinks}>
              <Link to="/login" className={styles.loginLink}>
                Sign In
              </Link>
              <Link to="/register" className={styles.registerLink}>
                Create Account
              </Link>
            </div>
          )}

          {/* Mobile Menu Toggle Button */}
          <button
            type="button"
            className={styles.mobileMenuBtn}
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            aria-label={mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
            aria-expanded={mobileMenuOpen}
          >
            {mobileMenuOpen ? <CloseIcon /> : <MenuIcon />}
          </button>
        </div>
      </header>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className={styles.mobileMenu} role="dialog" aria-label="Mobile Navigation">
          <form className={styles.mobileSearchForm} onSubmit={handleSearchSubmit}>
            <input
              type="text"
              placeholder="Search problems..."
              className={styles.mobileSearchInput}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              aria-label="Search problems"
            />
            <button type="submit" className="btn btn-primary" style={{ padding: '0.4rem 0.85rem' }}>
              Search
            </button>
          </form>

          <nav className={styles.mobileNavLinks}>
            <Link
              to="/problems"
              className={`${styles.mobileNavItem} ${isActive('/problems') ? styles.mobileActive : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Problems
            </Link>
            <Link
              to="/forum"
              className={`${styles.mobileNavItem} ${isActive('/forum') ? styles.mobileActive : ''}`}
              onClick={() => setMobileMenuOpen(false)}
            >
              Discuss
            </Link>
            {user ? (
              <>
                <Link
                  to="/history"
                  className={`${styles.mobileNavItem} ${isActive('/history') ? styles.mobileActive : ''}`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Submission History
                </Link>
                <button
                  type="button"
                  className={styles.mobileNavItem}
                  onClick={() => {
                    setProfileModalOpen(true);
                    setMobileMenuOpen(false);
                  }}
                >
                  Account Settings
                </button>
                <button
                  type="button"
                  className={`${styles.mobileNavItem} ${styles.mobileDanger}`}
                  onClick={handleLogout}
                >
                  Log out ({displayName})
                </button>
              </>
            ) : (
              <div className={styles.mobileAuthRow}>
                <Link
                  to="/login"
                  className="btn btn-secondary"
                  style={{ flex: 1 }}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Create Account
                </Link>
              </div>
            )}
          </nav>
        </div>
      )}

      {/* Profile & Security Modal */}
      <ProfileModal
        isOpen={profileModalOpen}
        onClose={() => setProfileModalOpen(false)}
      />
    </>
  );
}
