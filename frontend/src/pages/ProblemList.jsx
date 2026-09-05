import { useEffect, useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import api from '../api/client';
import styles from './ProblemList.module.css';

// Canonical metadata mapping for LeetCode catalog numbers, acceptance rates, and topic tags
const PROBLEM_METADATA = {
  'two sum': { num: 1, acceptance: '57.9%', topics: ['Array', 'Hash Table'] },
  'add two numbers': { num: 2, acceptance: '49.0%', topics: ['Linked List', 'Math'] },
  'longest substring without repeating characters': { num: 3, acceptance: '39.6%', topics: ['Hash Table', 'String', 'Sliding Window'] },
  'median of two sorted arrays': { num: 4, acceptance: '47.2%', topics: ['Array', 'Binary Search'] },
  'longest palindromic substring': { num: 5, acceptance: '38.3%', topics: ['String', 'Dynamic Programming'] },
  'zigzag conversion': { num: 6, acceptance: '54.7%', topics: ['String'] },
  'reverse integer': { num: 7, acceptance: '32.3%', topics: ['Math'] },
  'string to integer (atoi)': { num: 8, acceptance: '21.5%', topics: ['String'] },
  'palindrome number': { num: 9, acceptance: '60.8%', topics: ['Math'] },
  'regular expression matching': { num: 10, acceptance: '31.4%', topics: ['String', 'Dynamic Programming'] },
  'container with most water': { num: 11, acceptance: '60.5%', topics: ['Array', 'Greedy', 'Two Pointers'] },
  'integer to roman': { num: 12, acceptance: '71.4%', topics: ['Math', 'String'] },
  'roman to integer': { num: 13, acceptance: '67.0%', topics: ['Math', 'String'] },
  '3sum': { num: 15, acceptance: '34.8%', topics: ['Array', 'Two Pointers', 'Sorting'] },
  '3sum closest': { num: 16, acceptance: '45.8%', topics: ['Array', 'Two Pointers', 'Sorting'] },
  'valid parentheses': { num: 20, acceptance: '41.2%', topics: ['String', 'Stack'] },
  'merge two sorted lists': { num: 21, acceptance: '65.4%', topics: ['Linked List', 'Recursion'] },
  'search in rotated sorted array': { num: 33, acceptance: '41.8%', topics: ['Array', 'Binary Search'] },
  'trapping rain water': { num: 42, acceptance: '63.4%', topics: ['Array', 'Two Pointers', 'Dynamic Programming', 'Stack'] },
  'group anagrams': { num: 49, acceptance: '69.5%', topics: ['Array', 'Hash Table', 'String', 'Sorting'] },
  'maximum subarray': { num: 53, acceptance: '51.3%', topics: ['Array', 'Dynamic Programming', 'Divide and Conquer'] },
  'merge intervals': { num: 56, acceptance: '47.9%', topics: ['Array', 'Sorting'] },
  'climbing stairs': { num: 70, acceptance: '53.2%', topics: ['Math', 'Dynamic Programming', 'Memoization'] },
  'best time to buy and sell stock': { num: 121, acceptance: '54.8%', topics: ['Array', 'Dynamic Programming'] },
  'valid palindrome': { num: 125, acceptance: '48.9%', topics: ['Two Pointers', 'String'] },
  'house robber': { num: 198, acceptance: '51.8%', topics: ['Array', 'Dynamic Programming'] },
  'number of islands': { num: 200, acceptance: '60.2%', topics: ['Array', 'DFS / BFS', 'Graph'] },
  'reverse linked list': { num: 206, acceptance: '78.1%', topics: ['Linked List', 'Recursion'] },
  'contains duplicate': { num: 217, acceptance: '62.1%', topics: ['Array', 'Hash Table', 'Sorting'] },
  'product of array except self': { num: 238, acceptance: '66.8%', topics: ['Array', 'Prefix Sum'] },
  'valid anagram': { num: 242, acceptance: '65.0%', topics: ['Hash Table', 'String', 'Sorting'] },
  'coin change': { num: 322, acceptance: '45.7%', topics: ['Array', 'Dynamic Programming', 'BFS'] },
  'binary search': { num: 704, acceptance: '58.4%', topics: ['Array', 'Binary Search'] },
  'daily temperatures': { num: 739, acceptance: '67.3%', topics: ['Array', 'Stack', 'Monotonic Stack'] },
  'minimum number of pushes to type word i': { num: 3014, acceptance: '75.7%', topics: ['String', 'Greedy', 'Math'] },
};



const CATEGORIES = [
  { id: 'all', name: 'All Topics', icon: '⬚' },
  { id: 'algo', name: 'Algorithms', icon: '⚙' },
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
      const num = meta?.num || (index + 1);
      const status = solvedTitles.has(lookupKey)
        ? 'solved'
        : attemptedTitles.has(lookupKey)
        ? 'attempted'
        : 'unsolved';

      const diffCapitalized = p.difficulty
        ? p.difficulty.charAt(0).toUpperCase() + p.difficulty.slice(1).toLowerCase()
        : 'Easy';

      uniqueMap.set(lookupKey, {
        id: p.id,
        rawId: p.id,
        num,
        cleanTitle,
        title: `${num}. ${cleanTitle}`,
        acceptance: meta?.acceptance || '65.0%',
        difficulty: diffCapitalized,
        status,
        hasSolution: true,
        topics: meta?.topics || ['Array', 'Algorithms'],
        category: 'algo',
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
        if (p.category !== activeCategory) {
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
