import { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import styles from './ProblemList.module.css';

// Default LeetCode catalog problems with assigned topics and categories
const LEETCODE_DEFAULT_PROBLEMS = [
  { id: '3014', title: '3014. Minimum Number of Pushes to Type Word I', acceptance: '75.7%', difficulty: 'Easy', status: 'unsolved', isPinned: true, topics: ['String', 'Greedy', 'Math'], category: 'algo' },
  { id: '1', title: '1. Two Sum', acceptance: '57.9%', difficulty: 'Easy', status: 'solved', hasSolution: true, topics: ['Array', 'Hash Table'], category: 'algo' },
  { id: '2', title: '2. Add Two Numbers', acceptance: '49.0%', difficulty: 'Medium', status: 'unsolved', hasSolution: true, topics: ['Linked List', 'Math'], category: 'algo' },
  { id: '3', title: '3. Longest Substring Without Repeating Characters', acceptance: '39.6%', difficulty: 'Medium', status: 'unsolved', hasSolution: true, topics: ['Hash Table', 'String', 'Sliding Window'], category: 'algo' },
  { id: '4', title: '4. Median of Two Sorted Arrays', acceptance: '47.2%', difficulty: 'Hard', status: 'unsolved', hasSolution: true, topics: ['Array', 'Binary Search'], category: 'algo' },
  { id: '5', title: '5. Longest Palindromic Substring', acceptance: '38.3%', difficulty: 'Medium', status: 'unsolved', hasSolution: true, topics: ['String', 'Dynamic Programming'], category: 'algo' },
  { id: '6', title: '6. Zigzag Conversion', acceptance: '54.7%', difficulty: 'Medium', status: 'unsolved', hasSolution: true, topics: ['String'], category: 'algo' },
  { id: '7', title: '7. Reverse Integer', acceptance: '32.3%', difficulty: 'Medium', status: 'unsolved', hasSolution: true, topics: ['Math'], category: 'algo' },
  { id: '8', title: '8. String to Integer (atoi)', acceptance: '21.5%', difficulty: 'Medium', status: 'unsolved', hasSolution: true, topics: ['String'], category: 'algo' },
  { id: '9', title: '9. Palindrome Number', acceptance: '60.8%', difficulty: 'Easy', status: 'unsolved', hasSolution: true, topics: ['Math'], category: 'algo' },
  { id: '10', title: '10. Regular Expression Matching', acceptance: '31.4%', difficulty: 'Hard', status: 'unsolved', hasSolution: true, topics: ['String', 'Dynamic Programming'], category: 'algo' },
  { id: '11', title: '11. Container With Most Water', acceptance: '60.5%', difficulty: 'Medium', status: 'solved', hasSolution: true, topics: ['Array', 'Greedy', 'Two Pointers'], category: 'algo' },
  { id: '12', title: '12. Integer to Roman', acceptance: '71.4%', difficulty: 'Medium', status: 'unsolved', hasSolution: true, topics: ['Math', 'String'], category: 'algo' },
  { id: '13', title: '13. Roman to Integer', acceptance: '67.0%', difficulty: 'Easy', status: 'unsolved', hasSolution: true, topics: ['Math', 'String'], category: 'algo' },
];

const TOPIC_TAGS = [
  { name: 'Array', count: '2197' },
  { name: 'String', count: '880' },
  { name: 'Hash Table', count: '825' },
  { name: 'Math', count: '684' },
  { name: 'Dynamic Programming', count: '666' },
  { name: 'Sorting', count: '527' },
  { name: 'Greedy', count: '470' },
  { name: 'Depth-First Search', count: '344' },
  { name: 'Binary Search', count: '321' },
];

const CATEGORIES = [
  { id: 'all', name: 'All Topics', icon: '⬚' },
  { id: 'algo', name: 'Algorithms', icon: '⚙' },
  { id: 'db', name: 'Database', icon: '🗄' },
  { id: 'shell', name: 'Shell', icon: '>$' },
  { id: 'concurrency', name: 'Concurrency', icon: '⚡' },
  { id: 'javascript', name: 'JavaScript', icon: 'JS' },
  { id: 'pandas', name: 'pandas', icon: '🐼' },
];

const TRENDING_COMPANIES = [
  { name: 'Google', count: '2331' },
  { name: 'Amazon', count: '1906' },
  { name: 'Apple', count: '304' },
  { name: 'Bloomberg', count: '1214' },
  { name: 'Microsoft', count: '1385' },
  { name: 'Meta', count: '1395' },
  { name: 'Infosys', count: '195' },
  { name: 'Citadel', count: '67' },
  { name: 'Uber', count: '359' },
  { name: 'Oracle', count: '309' },
  { name: 'Adobe', count: '150' },
  { name: 'Salesforce', count: '191' },
  { name: 'TikTok', count: '349' },
  { name: 'Pinterest', count: '46' },
  { name: 'Airbnb', count: '64' },
  { name: 'LinkedIn', count: '176' },
  { name: 'Goldman Sachs', count: '264' },
  { name: 'TCS', count: '252' },
  { name: 'Walmart Labs', count: '133' },
  { name: 'Capital One', count: '63' },
];

export default function ProblemList() {
  const [dbProblems, setDbProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedTag, setSelectedTag] = useState('');
  const [selectedCompany, setSelectedCompany] = useState('');
  const [companySearch, setCompanySearch] = useState('');
  const [sortField, setSortField] = useState('id'); // id | title | acceptance | difficulty
  const [sortDirection, setSortDirection] = useState('asc'); // asc | desc

  useEffect(() => {
    api.get('/problems')
      .then(r => setDbProblems(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // Merge database problems with default list
  const combinedProblems = useMemo(() => {
    if (!dbProblems || dbProblems.length === 0) {
      return LEETCODE_DEFAULT_PROBLEMS;
    }

    const defaultMap = new Map(LEETCODE_DEFAULT_PROBLEMS.map(p => [p.title.toLowerCase().replace(/^[0-9]+\.\s*/, ''), p]));

    const formattedDb = dbProblems.map((p, idx) => {
      const cleanTitle = p.title.toLowerCase();
      const existing = defaultMap.get(cleanTitle);
      return {
        id: p.id,
        rawId: p.id,
        title: p.title.match(/^[0-9]+\./) ? p.title : `${idx + 1}. ${p.title}`,
        acceptance: existing ? existing.acceptance : '65.0%',
        difficulty: p.difficulty ? p.difficulty.charAt(0).toUpperCase() + p.difficulty.slice(1) : 'Easy',
        status: idx % 4 === 0 ? 'solved' : 'unsolved',
        hasSolution: true,
        topics: existing ? existing.topics : ['Array', 'Algorithms'],
        category: 'algo',
      };
    });

    const dbTitles = new Set(dbProblems.map(p => p.title.toLowerCase()));
    const remainingDefaults = LEETCODE_DEFAULT_PROBLEMS.filter(p => {
      const clean = p.title.toLowerCase().replace(/^[0-9]+\.\s*/, '');
      return !dbTitles.has(clean);
    });

    return [...formattedDb, ...remainingDefaults];
  }, [dbProblems]);

  // Filter & sort problems
  const filteredAndSortedProblems = useMemo(() => {
    let result = combinedProblems.filter(p => {
      // Filter by search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        if (!p.title.toLowerCase().includes(query) && !p.id.toLowerCase().includes(query)) {
          return false;
        }
      }

      // Filter by selected topic tag
      if (selectedTag) {
        if (!p.topics || !p.topics.includes(selectedTag)) {
          return false;
        }
      }

      // Filter by category
      if (activeCategory !== 'all') {
        if (p.category !== activeCategory) {
          return false;
        }
      }

      return true;
    });

    // Apply Sorting
    result.sort((a, b) => {
      let valA = a[sortField];
      let valB = b[sortField];

      if (sortField === 'acceptance') {
        valA = parseFloat(a.acceptance) || 0;
        valB = parseFloat(b.acceptance) || 0;
      } else if (sortField === 'difficulty') {
        const diffWeight = { Easy: 1, Medium: 2, 'Med.': 2, Hard: 3 };
        valA = diffWeight[a.difficulty] || 1;
        valB = diffWeight[b.difficulty] || 1;
      } else if (sortField === 'id') {
        valA = parseInt(a.id, 10) || 99999;
        valB = parseInt(b.id, 10) || 99999;
      }

      if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [combinedProblems, searchQuery, selectedTag, activeCategory, sortField, sortDirection]);

  const pinnedProblem = LEETCODE_DEFAULT_PROBLEMS.find(p => p.isPinned) || combinedProblems[0];
  const listProblemsOnly = filteredAndSortedProblems.filter(p => !p.isPinned);

  const filteredCompanies = useMemo(() => {
    if (!companySearch.trim()) return TRENDING_COMPANIES;
    return TRENDING_COMPANIES.filter(c => c.name.toLowerCase().includes(companySearch.toLowerCase()));
  }, [companySearch]);

  const toggleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const shuffleProblems = () => {
    if (listProblemsOnly.length === 0) return;
    const randomItem = listProblemsOnly[Math.floor(Math.random() * listProblemsOnly.length)];
    window.location.href = `/problems/${randomItem.rawId || randomItem.id}`;
  };

  return (
    <div className={styles.container}>
      {/* Left Sidebar — Quest removed per user directive */}
      <aside className={styles.leftSidebar}>
        <div className={styles.sidebarGroup}>
          <div className={`${styles.sidebarItem} ${styles.sidebarActive}`}>
            <span className={styles.sidebarIcon}>📚</span>
            <span>Library</span>
          </div>
          <div className={styles.sidebarItem}>
            <span className={styles.sidebarIcon}>🗺</span>
            <span>Explore</span>
          </div>
          <div className={styles.sidebarItem}>
            <span className={styles.sidebarIcon}>📖</span>
            <span>Study Plan</span>
          </div>
        </div>

        <div className={styles.sidebarDivider} />

        <div className={styles.sidebarSection}>
          <div className={styles.sidebarSectionHeader}>
            <span className={styles.sidebarSectionTitle}>My Lists</span>
            <div className={styles.sidebarSectionActions}>
              <span>+</span>
              <span>▾</span>
            </div>
          </div>
          <div className={styles.sidebarItem}>
            <span className={styles.sidebarIcon}>★</span>
            <span className={styles.sidebarText}>Favorite</span>
            <span className={styles.lockIcon}>🔒</span>
          </div>
          <div className={styles.sidebarItem}>
            <span className={styles.sidebarIcon}>📄</span>
            <span className={styles.sidebarText}>Python Developer</span>
            <span className={styles.globeIcon}>🌐</span>
          </div>
        </div>
      </aside>

      {/* Main Workspace (Center) */}
      <main className={styles.mainContent}>
        {/* Top 4 Featured Banner Cards */}
        <div className={styles.bannersGrid}>
          <div className={`${styles.bannerCard} ${styles.bannerGold}`}>
            <div className={styles.bannerBadge}>👑</div>
            <h3 className={styles.bannerTitle}>Unlock Full Experience on AlgoLens</h3>
            <div className={styles.bannerPricePill}>
              ₹583.25 <span className={styles.perMonth}>/mo</span> <span className={styles.discountTag}>Save over 68%</span>
            </div>
          </div>

          <div className={`${styles.bannerCard} ${styles.bannerPurple}`}>
            <div className={styles.bannerLogo}>⬡</div>
            <h3 className={styles.bannerTitle}>AlgoLens at Your Fingertips</h3>
            <p className={styles.bannerSub}>Mobile App Available</p>
          </div>

          <div className={`${styles.bannerCard} ${styles.bannerGreen}`}>
            <h3 className={styles.bannerTitle}>AlgoLens's Interview Crash Course:</h3>
            <p className={styles.bannerCourseSub}>System Design for Interviews and Beyond</p>
          </div>

          <div className={`${styles.bannerCard} ${styles.bannerViolet}`}>
            <h3 className={styles.bannerTitle}>AlgoLens's Interview Crash Course:</h3>
            <p className={styles.bannerCourseSub}>Data Structures and Algorithms</p>
          </div>
        </div>

        {/* Tag Filter Pills Bar */}
        <div className={styles.tagFilterBar}>
          {TOPIC_TAGS.map(tag => (
            <button
              key={tag.name}
              className={`${styles.tagPill} ${selectedTag === tag.name ? styles.tagPillActive : ''}`}
              onClick={() => setSelectedTag(selectedTag === tag.name ? '' : tag.name)}
            >
              <span>{tag.name}</span>
              <span className={styles.tagCount}>{tag.count}</span>
            </button>
          ))}
          <button className={styles.expandTagBtn} onClick={() => setSelectedTag('')}>
            {selectedTag ? 'Clear Filter ✕' : 'Expand ▾'}
          </button>
        </div>

        {/* Category Tabs */}
        <div className={styles.categoryTabsBar}>
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              className={`${styles.categoryTab} ${activeCategory === cat.id ? styles.categoryTabActive : ''}`}
              onClick={() => setActiveCategory(cat.id)}
            >
              <span className={styles.catIcon}>{cat.icon}</span>
              <span>{cat.name}</span>
            </button>
          ))}
        </div>

        {/* Controls Bar */}
        <div className={styles.controlsBar}>
          <div className={styles.searchWrapper}>
            <span className={styles.searchIcon}>🔍</span>
            <input
              type="text"
              placeholder="Search questions"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className={styles.questionsSearchInput}
            />
          </div>

          <div className={styles.controlsRight}>
            <button
              className={styles.controlBtn}
              title="Sort by Title / Difficulty / Acceptance"
              onClick={() => toggleSort(sortField === 'difficulty' ? 'acceptance' : 'difficulty')}
            >
              ⚡ Sort: {sortField.toUpperCase()} ({sortDirection})
            </button>
            <button className={styles.controlBtn} title="Random Shuffle" onClick={shuffleProblems}>
              🔀 Pick Random
            </button>

            <span className={styles.solvedCount}>
              <span className={styles.solvedIcon}>◯</span> 16/4005 Solved
            </span>
          </div>
        </div>

        {/* Table & Pinned Problem */}
        <div className={styles.tableContainer}>
          {/* Pinned Card */}
          {pinnedProblem && !selectedTag && activeCategory === 'all' && (
            <div className={styles.pinnedRow}>
              <div className={styles.pinnedLeft}>
                <span className={styles.pinnedIcon}>📅</span>
                <Link to={`/problems/${pinnedProblem.rawId || pinnedProblem.id}`} className={styles.pinnedTitle}>
                  {pinnedProblem.title}
                </Link>
              </div>
              <div className={styles.pinnedRight}>
                <span className={styles.accRate}>{pinnedProblem.acceptance}</span>
                <span className={`${styles.diffBadge} ${styles['diff' + (pinnedProblem.difficulty || 'Easy')]}`}>
                  {pinnedProblem.difficulty}
                </span>
                <span className={styles.solutionIcon}>🎥</span>
              </div>
            </div>
          )}

          {/* Column Header */}
          <div className={styles.tableHeaderRow}>
            <span className={styles.colHeaderStatus}>Status</span>
            <span className={styles.colHeaderTitle} onClick={() => toggleSort('title')}>Title ↕</span>
            <span className={styles.colHeaderAcc} onClick={() => toggleSort('acceptance')}>Acceptance ↕</span>
            <span className={styles.colHeaderDiff} onClick={() => toggleSort('difficulty')}>Difficulty ↕</span>
            <span className={styles.colHeaderSol}>Solution</span>
          </div>

          {/* Problem List Rows */}
          <div className={styles.problemsTable}>
            {listProblemsOnly.map(p => (
              <div key={p.id} className={styles.tableRow}>
                <div className={styles.colStatus}>
                  {p.status === 'solved' ? (
                    <span className={styles.solvedCheck}>✓</span>
                  ) : (
                    <span className={styles.unsolvedDot}></span>
                  )}
                </div>

                <div className={styles.colTitle}>
                  <Link to={`/problems/${p.rawId || p.id}`} className={styles.problemLink}>
                    {p.title}
                  </Link>
                </div>

                <div className={styles.colAcceptance}>
                  {p.acceptance}
                </div>

                <div className={styles.colDifficulty}>
                  <span className={`${styles.diffBadge} ${styles['diff' + (p.difficulty === 'Med.' ? 'Medium' : (p.difficulty || 'Easy'))]}`}>
                    {p.difficulty === 'Medium' ? 'Med.' : p.difficulty}
                  </span>
                </div>

                <div className={styles.colSolution}>
                  <span className={styles.solutionIcon} title="Video Solution">🎥</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Right Sidebar */}
      <aside className={styles.rightSidebar}>
        {/* Calendar Widget */}
        <div className={styles.widgetCard}>
          <div className={styles.calHeader}>
            <div className={styles.calHeaderTitle}>
              <span>Day 30</span>
              <span className={styles.timerSub}>07:41:58 left</span>
            </div>
            <div className={styles.julBadge}>
              <span className={styles.julNum}>7</span>
              <span className={styles.julMonth}>Jul</span>
            </div>
          </div>

          {/* Days Grid */}
          <div className={styles.calGridHead}>
            <span>S</span><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span>
          </div>
          <div className={styles.calGrid}>
            {Array.from({ length: 31 }, (_, i) => i + 1).map(day => (
              <div
                key={day}
                className={`${styles.calDayCell} ${day === 30 ? styles.calDayActive : ''}`}
              >
                {day === 30 ? '✓' : day}
              </div>
            ))}
          </div>

          {/* Weekly Premium Row */}
          <div className={styles.weeklyPremiumRow}>
            <span className={styles.weeklyLabel}>Weekly Premium ⓘ</span>
            <div className={styles.weeklyBadges}>
              <span>W1</span><span>W2</span><span>W3</span><span>W4</span>
              <span className={styles.wActive}>W5</span>
            </div>
          </div>

          {/* Redeem Row */}
          <div className={styles.redeemRow}>
            <button className={styles.redeemBtn}>
              <span className={styles.gemIcon}>💎</span> 0 Redeem
            </button>
            <span className={styles.rulesLink}>Rules</span>
          </div>
        </div>

        {/* Trending Companies Widget */}
        <div className={styles.widgetCard}>
          <div className={styles.companyHeader}>
            <span className={styles.widgetTitle}>Trending Companies</span>
            <div className={styles.navArrows}>
              <span>‹</span><span>›</span>
            </div>
          </div>

          <div className={styles.companySearchBox}>
            <span className={styles.searchIcon}>🔍</span>
            <input
              type="text"
              placeholder="Search for a company..."
              value={companySearch}
              onChange={e => setCompanySearch(e.target.value)}
              className={styles.companyInput}
            />
          </div>

          <div className={styles.companyTagsList}>
            {filteredCompanies.map(c => (
              <button
                key={c.name}
                className={`${styles.companyPill} ${selectedCompany === c.name ? styles.companyPillActive : ''}`}
                onClick={() => setSelectedCompany(selectedCompany === c.name ? '' : c.name)}
              >
                <span>{c.name}</span>
                <span className={styles.companyCount}>{c.count}</span>
              </button>
            ))}
          </div>
        </div>
      </aside>
    </div>
  );
}
