import { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import api from '../api/client';
import styles from './ProblemList.module.css';

// Canonical metadata mapping for LeetCode catalog numbers, acceptance rates, categories, and topic tags
const PROBLEM_METADATA = {
  // ── 35 Algorithmic Problems ──────────────────────────────────────────────
  'two sum': { num: 1, acceptance: '57.9%', topics: ['Array', 'Hash Table'], category: 'algo' },
  'add two numbers': { num: 2, acceptance: '49.0%', topics: ['Linked List', 'Math', 'Recursion'], category: 'algo' },
  'longest substring without repeating characters': { num: 3, acceptance: '39.6%', topics: ['Hash Table', 'String', 'Sliding Window'], category: 'algo' },
  'median of two sorted arrays': { num: 4, acceptance: '47.2%', topics: ['Array', 'Binary Search', 'Divide and Conquer'], category: 'algo' },
  'longest palindromic substring': { num: 5, acceptance: '38.3%', topics: ['String', 'Dynamic Programming'], category: 'algo' },
  'zigzag conversion': { num: 6, acceptance: '54.7%', topics: ['String'], category: 'algo' },
  'reverse integer': { num: 7, acceptance: '32.3%', topics: ['Math'], category: 'algo' },
  'string to integer (atoi)': { num: 8, acceptance: '21.5%', topics: ['String'], category: 'algo' },
  'palindrome number': { num: 9, acceptance: '60.8%', topics: ['Math'], category: 'algo' },
  'regular expression matching': { num: 10, acceptance: '31.4%', topics: ['String', 'Dynamic Programming', 'Recursion'], category: 'algo' },
  'container with most water': { num: 11, acceptance: '60.5%', topics: ['Array', 'Greedy', 'Two Pointers'], category: 'algo' },
  'integer to roman': { num: 12, acceptance: '71.4%', topics: ['Math', 'String'], category: 'algo' },
  'roman to integer': { num: 13, acceptance: '67.0%', topics: ['Math', 'String'], category: 'algo' },
  '3sum': { num: 15, acceptance: '34.8%', topics: ['Array', 'Two Pointers', 'Sorting'], category: 'algo' },
  '3sum closest': { num: 16, acceptance: '45.8%', topics: ['Array', 'Two Pointers', 'Sorting'], category: 'algo' },
  'valid parentheses': { num: 20, acceptance: '41.2%', topics: ['String', 'Stack'], category: 'algo' },
  'merge two sorted lists': { num: 21, acceptance: '65.4%', topics: ['Linked List', 'Recursion'], category: 'algo' },
  'search in rotated sorted array': { num: 33, acceptance: '41.8%', topics: ['Array', 'Binary Search'], category: 'algo' },
  'trapping rain water': { num: 42, acceptance: '63.4%', topics: ['Array', 'Two Pointers', 'Dynamic Programming', 'Stack'], category: 'algo' },
  'group anagrams': { num: 49, acceptance: '69.5%', topics: ['Array', 'Hash Table', 'String', 'Sorting'], category: 'algo' },
  'maximum subarray': { num: 53, acceptance: '51.3%', topics: ['Array', 'Dynamic Programming', 'Divide and Conquer'], category: 'algo' },
  'merge intervals': { num: 56, acceptance: '47.9%', topics: ['Array', 'Sorting'], category: 'algo' },
  'climbing stairs': { num: 70, acceptance: '53.2%', topics: ['Math', 'Dynamic Programming', 'Memoization'], category: 'algo' },
  'best time to buy and sell stock': { num: 121, acceptance: '54.8%', topics: ['Array', 'Dynamic Programming'], category: 'algo' },
  'valid palindrome': { num: 125, acceptance: '48.9%', topics: ['Two Pointers', 'String'], category: 'algo' },
  'house robber': { num: 198, acceptance: '51.8%', topics: ['Array', 'Dynamic Programming'], category: 'algo' },
  'number of islands': { num: 200, acceptance: '60.2%', topics: ['Array', 'DFS / BFS', 'Graph'], category: 'algo' },
  'reverse linked list': { num: 206, acceptance: '78.1%', topics: ['Linked List', 'Recursion'], category: 'algo' },
  'contains duplicate': { num: 217, acceptance: '62.1%', topics: ['Array', 'Hash Table', 'Sorting'], category: 'algo' },
  'product of array except self': { num: 238, acceptance: '66.8%', topics: ['Array', 'Prefix Sum'], category: 'algo' },
  'valid anagram': { num: 242, acceptance: '65.0%', topics: ['Hash Table', 'String', 'Sorting'], category: 'algo' },
  'coin change': { num: 322, acceptance: '45.7%', topics: ['Array', 'Dynamic Programming', 'BFS'], category: 'algo' },
  'binary search': { num: 704, acceptance: '58.4%', topics: ['Array', 'Binary Search'], category: 'algo' },
  'daily temperatures': { num: 739, acceptance: '67.3%', topics: ['Array', 'Stack', 'Monotonic Stack'], category: 'algo' },
  'minimum number of pushes to type word i': { num: 3014, acceptance: '75.7%', topics: ['String', 'Greedy', 'Math'], category: 'algo' },

  // ── 15 SQL / Database Problems ───────────────────────────────────────────
  'combine two tables': { num: 175, acceptance: '74.2%', topics: ['Database', 'SQL', 'Join'], category: 'sql' },
  'second highest salary': { num: 176, acceptance: '39.4%', topics: ['Database', 'SQL', 'Subquery', 'Limit'], category: 'sql' },
  'rank scores': { num: 178, acceptance: '61.3%', topics: ['Database', 'SQL', 'Window Function', 'Dense Rank'], category: 'sql' },
  'consecutive numbers': { num: 180, acceptance: '46.7%', topics: ['Database', 'SQL', 'Self Join', 'Window Function'], category: 'sql' },
  'employees earning more than their managers': { num: 181, acceptance: '69.8%', topics: ['Database', 'SQL', 'Self Join'], category: 'sql' },
  'duplicate emails': { num: 182, acceptance: '71.5%', topics: ['Database', 'SQL', 'Group By', 'Aggregation'], category: 'sql' },
  'customers who never order': { num: 183, acceptance: '68.1%', topics: ['Database', 'SQL', 'Subquery', 'Left Join'], category: 'sql' },
  'department highest salary': { num: 184, acceptance: '51.2%', topics: ['Database', 'SQL', 'Group By', 'Subquery'], category: 'sql' },
  'department top three salaries': { num: 185, acceptance: '52.1%', topics: ['Database', 'SQL', 'Window Function', 'Dense Rank'], category: 'sql' },
  'delete duplicate emails': { num: 196, acceptance: '58.6%', topics: ['Database', 'SQL', 'DML', 'Delete'], category: 'sql' },
  'rising temperature': { num: 197, acceptance: '47.8%', topics: ['Database', 'SQL', 'Date Functions', 'Self Join'], category: 'sql' },
  'trips and users': { num: 262, acceptance: '38.9%', topics: ['Database', 'SQL', 'Join', 'Conditional Aggregation'], category: 'sql' },
  'investments in 2016': { num: 585, acceptance: '46.1%', topics: ['Database', 'SQL', 'Subquery', 'Group By'], category: 'sql' },
  'tree node classification': { num: 608, acceptance: '72.0%', topics: ['Database', 'SQL', 'Case When', 'Subquery'], category: 'sql' },
  'tree node': { num: 608, acceptance: '72.0%', topics: ['Database', 'SQL', 'Case When', 'Subquery'], category: 'sql' },
  'market analysis i': { num: 1158, acceptance: '59.4%', topics: ['Database', 'SQL', 'Left Join', 'Group By'], category: 'sql' },
};

const CATEGORIES = [
  { id: 'all', name: 'All Topics', icon: '⬚' },
  { id: 'algo', name: 'Algorithms', icon: '⚙' },
  { id: 'sql', name: 'Database / SQL', icon: '🗄' },
  { id: 'dp', name: 'Dynamic Programming', icon: '⚡' },
  { id: 'ds', name: 'Data Structures', icon: '🧱' },
  { id: 'math', name: 'Math & Logic', icon: '📐' },
];

export default function ProblemList() {
  const { user } = useAuth();
  const [dbProblems, setDbProblems] = useState([]);
  const [userHistory, setUserHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('all');
  const [selectedTag, setSelectedTag] = useState('');
  const [statusFilter, setStatusFilter] = useState('all'); // all | solved | unsolved | attempted
  const [difficultyFilter, setDifficultyFilter] = useState('all'); // all | Easy | Medium | Hard
  const [sortField, setSortField] = useState('num'); // num | title | acceptance | difficulty
  const [sortDirection, setSortDirection] = useState('asc'); // asc | desc

  useEffect(() => {
    setLoading(true);
    api.get('/problems')
      .then(r => setDbProblems(r.data || []))
      .catch(() => setDbProblems([]))
      .finally(() => setLoading(false));
  }, []);

  // Fetch user submission history to reflect real solve/attempt statuses
  useEffect(() => {
    if (!user?.id) {
      setUserHistory([]);
      return;
    }
    api.get(`/users/${user.id}/history`)
      .then(r => setUserHistory(r.data || []))
      .catch(() => setUserHistory([]));
  }, [user]);

  // Compute solved and attempted sets
  const { solvedTitles, attemptedTitles } = useMemo(() => {
    const solved = new Set();
    const attempted = new Set();

    userHistory.forEach(item => {
      const titleClean = (item.problem_title || '').toLowerCase().replace(/^[0-9]+\.\s*/, '').trim();
      if (item.status === 'complete') {
        solved.add(titleClean);
      } else if (item.status === 'failed') {
        attempted.add(titleClean);
      }
    });

    return { solvedTitles: solved, attemptedTitles: attempted };
  }, [userHistory]);

  // Strictly deduplicate problems by clean title and assign official numbers
  const formattedProblems = useMemo(() => {
    const uniqueMap = new Map();

    dbProblems.forEach((p, index) => {
      const cleanTitle = p.title.replace(/^[0-9]+\.\s*/, '').trim();
      const lookupKey = cleanTitle.toLowerCase();

      // Only take the first instance if duplicate exists in DB response
      if (uniqueMap.has(lookupKey)) return;

      const meta = PROBLEM_METADATA[lookupKey];
      const isSql = Boolean(
        p.generator_key?.startsWith('sql_') ||
        meta?.category === 'sql' ||
        lookupKey.includes('sql') ||
        meta?.topics?.includes('SQL') ||
        meta?.topics?.includes('Database')
      );

      const num = meta?.num || (index + 1);
      const status = solvedTitles.has(lookupKey)
        ? 'solved'
        : attemptedTitles.has(lookupKey)
        ? 'attempted'
        : 'unsolved';

      const diffCapitalized = p.difficulty
        ? p.difficulty.charAt(0).toUpperCase() + p.difficulty.slice(1).toLowerCase()
        : 'Easy';

      const category = isSql ? 'sql' : (meta?.category || 'algo');
      const defaultTopics = isSql ? ['Database', 'SQL'] : ['Array', 'Algorithms'];

      uniqueMap.set(lookupKey, {
        id: p.id,
        rawId: p.id,
        num,
        cleanTitle,
        title: `${num}. ${cleanTitle}`,
        acceptance: meta?.acceptance || (isSql ? '62.0%' : '65.0%'),
        difficulty: diffCapitalized,
        status,
        hasSolution: true,
        topics: meta?.topics || defaultTopics,
        category,
        isSql,
      });
    });

    return Array.from(uniqueMap.values());
  }, [dbProblems, solvedTitles, attemptedTitles]);

  // Dynamically compute topic tags and problem counts matching the actual problems
  const topicTags = useMemo(() => {
    const counts = {};
    formattedProblems.forEach(p => {
      (p.topics || []).forEach(topic => {
        counts[topic] = (counts[topic] || 0) + 1;
      });
    });

    return Object.entries(counts)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
  }, [formattedProblems]);

  // Filter & sort problems
  const filteredAndSortedProblems = useMemo(() => {
    let result = formattedProblems.filter(p => {
      // Filter by search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const matchesTitle = p.title.toLowerCase().includes(query);
        const matchesId = String(p.num).includes(query);
        if (!matchesTitle && !matchesId) {
          return false;
        }
      }

      // Filter by status
      if (statusFilter !== 'all') {
        if (p.status !== statusFilter) {
          return false;
        }
      }

      // Filter by difficulty
      if (difficultyFilter !== 'all') {
        const diffNormalized = p.difficulty === 'Med.' ? 'Medium' : p.difficulty;
        if (diffNormalized !== difficultyFilter) {
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
        if (activeCategory === 'sql') {
          if (!p.isSql && p.category !== 'sql') return false;
        } else if (activeCategory === 'algo') {
          if (p.isSql || p.category === 'sql') return false;
        } else if (activeCategory === 'dp') {
          if (p.isSql || !p.topics?.some(t => t.toLowerCase().includes('dynamic programming') || t.toLowerCase().includes('memoization'))) {
            return false;
          }
        } else if (activeCategory === 'ds') {
          const dsTags = ['Array', 'Linked List', 'Stack', 'Hash Table', 'Graph', 'Binary Search', 'Sliding Window', 'Monotonic Stack', 'Two Pointers', 'Prefix Sum'];
          if (p.isSql || !p.topics?.some(t => dsTags.includes(t))) {
            return false;
          }
        } else if (activeCategory === 'math') {
          if (p.isSql || !p.topics?.some(t => t.toLowerCase().includes('math'))) {
            return false;
          }
        } else if (p.category !== activeCategory) {
          return false;
        }
      }

      return true;
    });

    // Apply Sorting with stable secondary sort on problem number
    result.sort((a, b) => {
      let comparison = 0;

      if (sortField === 'title') {
        comparison = a.cleanTitle.localeCompare(b.cleanTitle);
      } else if (sortField === 'acceptance') {
        const valA = parseFloat(a.acceptance) || 0;
        const valB = parseFloat(b.acceptance) || 0;
        comparison = valA - valB;
      } else if (sortField === 'difficulty') {
        const diffWeight = { Easy: 1, Medium: 2, 'Med.': 2, Hard: 3 };
        const valA = diffWeight[a.difficulty] || 1;
        const valB = diffWeight[b.difficulty] || 1;
        comparison = valA - valB;
      } else {
        // Default sort by problem number
        comparison = a.num - b.num;
      }

      if (comparison !== 0) {
        return sortDirection === 'asc' ? comparison : -comparison;
      }

      // Secondary tiebreaker: problem number ascending
      return a.num - b.num;
    });

    return result;
  }, [formattedProblems, searchQuery, selectedTag, activeCategory, statusFilter, difficultyFilter, sortField, sortDirection]);

  const solvedCount = useMemo(() => {
    return formattedProblems.filter(p => p.status === 'solved').length;
  }, [formattedProblems]);

  const toggleSort = field => {
    if (sortField === field) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const shuffleProblems = () => {
    if (filteredAndSortedProblems.length === 0) return;
    const randomItem = filteredAndSortedProblems[Math.floor(Math.random() * filteredAndSortedProblems.length)];
    window.location.href = `/problems/${randomItem.rawId || randomItem.id}`;
  };

  return (
    <div className={styles.container}>
      {/* Main Workspace */}
      <main className={styles.mainContent}>
        {/* Tag Filter Pills Bar */}
        <div className={styles.tagFilterBar}>
          {topicTags.map(tag => (
            <button
              key={tag.name}
              className={`${styles.tagPill} ${selectedTag === tag.name ? styles.tagPillActive : ''}`}
              onClick={() => setSelectedTag(selectedTag === tag.name ? '' : tag.name)}
            >
              <span>{tag.name}</span>
              <span className={styles.tagCount}>{tag.count}</span>
            </button>
          ))}
          {selectedTag && (
            <button className={styles.expandTagBtn} onClick={() => setSelectedTag('')}>
              Clear
            </button>
          )}
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
              placeholder="Search questions by name or number"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className={styles.questionsSearchInput}
            />
          </div>

          <div className={styles.controlsRight}>
            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={e => setStatusFilter(e.target.value)}
              className={styles.filterSelect}
              title="Filter by solve status"
            >
              <option value="all">All Status</option>
              <option value="solved">Solved</option>
              <option value="attempted">Attempted</option>
              <option value="unsolved">Unsolved</option>
            </select>

            {/* Difficulty Filter */}
            <select
              value={difficultyFilter}
              onChange={e => setDifficultyFilter(e.target.value)}
              className={styles.filterSelect}
              title="Filter by difficulty"
            >
              <option value="all">All Difficulties</option>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>

            <button
              className={styles.controlBtn}
              title="Toggle sort order"
              onClick={() => toggleSort(sortField === 'difficulty' ? 'acceptance' : sortField === 'acceptance' ? 'num' : 'difficulty')}
            >
              ⚡ Sort: {sortField.toUpperCase()} ({sortDirection})
            </button>

            <button className={styles.controlBtn} title="Random Shuffle" onClick={shuffleProblems}>
              🔀 Pick Random
            </button>

            {user ? (
              <Link to="/history" className={styles.solvedCountLink} title="View your full submission history">
                <span className={styles.solvedIcon}>✓</span> {solvedCount}/{formattedProblems.length} Solved ↗
              </Link>
            ) : (
              <span className={styles.solvedCount}>
                <span className={styles.solvedIcon}>◯</span> {solvedCount}/{formattedProblems.length} Solved
              </span>
            )}
          </div>
        </div>

        {/* Table Container */}
        <div className={styles.tableContainer}>
          {/* Column Header */}
          <div className={styles.tableHeaderRow}>
            <span className={styles.colHeaderStatus}>Status</span>
            <span className={styles.colHeaderTitle} onClick={() => toggleSort('title')}>Title ↕</span>
            <span className={styles.colHeaderAcc} onClick={() => toggleSort('acceptance')}>Acceptance ↕</span>
            <span className={styles.colHeaderDiff} onClick={() => toggleSort('difficulty')}>Difficulty ↕</span>
          </div>

          {/* Problem List Rows */}
          <div className={styles.problemsTable}>
            {loading ? (
              <div style={{ padding: '3rem', display: 'flex', justifyContent: 'center' }}>
                <div className="spinner" />
              </div>
            ) : filteredAndSortedProblems.length === 0 ? (
              <div style={{ padding: '2.5rem', textAlign: 'center', color: '#9da0a8' }}>
                No problems match your current filters.
              </div>
            ) : (
              filteredAndSortedProblems.map(p => (
                <div key={p.id} className={styles.tableRow}>
                  <div className={styles.colStatus}>
                    {p.status === 'solved' ? (
                      <span className={styles.solvedCheck} title="Solved">✓</span>
                    ) : p.status === 'attempted' ? (
                      <span className={styles.attemptedDot} title="Attempted"></span>
                    ) : (
                      <span className={styles.unsolvedDot} title="Unsolved"></span>
                    )}
                  </div>

                  <div className={styles.colTitle}>
                    <Link to={`/problems/${p.rawId || p.id}`} className={styles.problemLink}>
                      {p.title}
                    </Link>
                    {p.isSql && (
                      <span className={styles.sqlBadge} title="SQL Database Problem">
                        SQL
                      </span>
                    )}
                  </div>

                  <div className={styles.colAcceptance}>
                    {p.acceptance}
                  </div>

                  <div className={styles.colDifficulty}>
                    <span className={`${styles.diffBadge} ${styles['diff' + (p.difficulty === 'Med.' ? 'Medium' : (p.difficulty || 'Easy'))]}`}>
                      {p.difficulty === 'Medium' ? 'Med.' : p.difficulty}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
