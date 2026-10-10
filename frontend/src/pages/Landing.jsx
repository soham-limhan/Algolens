import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import api from '../api/client';
import styles from './Landing.module.css';

// Supported execution environments & language engines
const SUPPORTED_LANGUAGES = [
  {
    id: 'python',
    name: 'Python',
    version: '3.11+',
    runtime: 'CPython Sandbox',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
        <path d="M11.927 0c-5.71 0-5.342 2.47-5.342 2.47l.006 2.56h5.422v.77H4.372s-4.372.493-4.372 5.346c0 4.854 3.82 4.697 3.82 4.697h2.28v-3.21s-.124-3.82 3.758-3.82h6.438s3.633.062 3.633-3.57c0-3.635-3.197-3.243-3.197-3.243s-.06-1.996-3.805-1.996zm-2.06 1.488a.93.93 0 1 1 0 1.86.93.93 0 0 1 0-1.86zm6.206 7.425v3.21s.124 3.82-3.758 3.82H5.877s-3.633-.062-3.633 3.57c0 3.635 3.197 3.243 3.197 3.243s.06 1.996 3.805 1.996c5.71 0 5.342-2.47 5.342-2.47l-.006-2.56H9.16v-.77h7.641s4.372-.493 4.372-5.346c0-4.854-3.82-4.697-3.82-4.697h-2.28zM14.133 20.65a.93.93 0 1 1 0 1.86.93.93 0 0 1 0-1.86z"/>
      </svg>
    ),
  },
  {
    id: 'java',
    name: 'Java',
    version: 'Java 21',
    runtime: 'OpenJDK JIT',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M18 8h1a4 4 0 0 1 0 8h-1" />
        <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z" />
        <line x1="6" y1="1" x2="6" y2="4" />
        <line x1="10" y1="1" x2="10" y2="4" />
        <line x1="14" y1="1" x2="14" y2="4" />
      </svg>
    ),
  },
  {
    id: 'cpp',
    name: 'C++',
    version: 'C++20',
    runtime: 'GCC 13 (-O3)',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M13 7a6 6 0 1 0 0 10" />
        <line x1="16" y1="10" x2="16" y2="14" />
        <line x1="14" y1="12" x2="18" y2="12" />
        <line x1="21" y1="10" x2="21" y2="14" />
        <line x1="19" y1="12" x2="23" y2="12" />
      </svg>
    ),
  },
  {
    id: 'c',
    name: 'C',
    version: 'C11',
    runtime: 'GCC 13 Native',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M16 8a6 6 0 1 0 0 8" />
      </svg>
    ),
  },
  {
    id: 'javascript',
    name: 'JavaScript',
    version: 'Node 20',
    runtime: 'V8 Engine',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="3" />
        <path d="M8 17v-4a1 1 0 0 0-1-1" />
        <path d="M13 14c.5-1 1.5-1 2-1s1 .5 1 1-1 1.5-2 2 1.5 1 2 1" />
      </svg>
    ),
  },
  {
    id: 'sql',
    name: 'SQL & MySQL',
    version: '8.0 & ANSI',
    runtime: 'Relational Sandbox',
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <ellipse cx="12" cy="5" rx="9" ry="3" />
        <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
        <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
      </svg>
    ),
  },
];

export default function Landing() {
  const { user } = useAuth();
  const [problems, setProblems] = useState([]);
  const [loadingProblems, setLoadingProblems] = useState(true);

  useEffect(() => {
    api.get('/problems')
      .then((r) => setProblems((r.data || []).slice(0, 4)))
      .catch(() => setProblems([]))
      .finally(() => setLoadingProblems(false));
  }, []);

  return (
    <div className={styles.page}>
      {/* ── 1. Hero ────────────────────────────────────────────── */}
      <section className={styles.hero}>
        <div className={styles.heroContainer}>
          <div className={styles.heroMain}>
            <div className={styles.heroContent}>
              <h1 className={styles.headline}>
                Your solution passed.<br />
                <span className={styles.accentText}>Is it actually optimal?</span>
              </h1>

              <p className={styles.sub}>
                Traditional judges stop at pass or fail. AlgoLens benchmarks execution
                runtimes across generated inputs from N=10 to N=1,000,000 plots your empirical curve
                on log-log axes, and identifies algorithmic complexity gaps before you submit to production.
              </p>

              <div className={styles.ctas}>
                <Link to="/problems" className="btn btn-primary" style={{ fontSize: '0.95rem', padding: '0.65rem 1.75rem' }}>
                  Browse Problem Catalog
                </Link>
                {!user ? (
                  <Link to="/login" className="btn btn-secondary" style={{ fontSize: '0.95rem', padding: '0.65rem 1.5rem' }}>
                    Sign In to Submit
                  </Link>
                ) : (
                  <Link to="/history" className="btn btn-secondary" style={{ fontSize: '0.95rem', padding: '0.65rem 1.5rem' }}>
                    View Submission History
                  </Link>
                )}
                <Link to="/forum" className="btn btn-secondary" style={{ fontSize: '0.95rem', padding: '0.65rem 1.5rem' }}>
                  Community Forum
                </Link>
              </div>
            </div>

            {/* ── Floating Icons & Asymptotic Badges Cluster ─── */}
            <div className={styles.heroVisual} aria-hidden="true">
              <div className={styles.orbitalRing} />
              <div className={styles.orbitalGlow} />

              {/* 1. Python Card (Top Left) */}
              <div className={`${styles.floatingCard} ${styles.cardPython}`}>
                <span className={styles.floatingCardIcon}>{SUPPORTED_LANGUAGES[0].icon}</span>
                <div className={styles.floatingCardText}>
                  <span className={styles.floatingCardTitle}>Python</span>
                  <span className={styles.floatingCardSub}>v3.11</span>
                </div>
              </div>

              {/* 2. C++ Card (Top Right) */}
              <div className={`${styles.floatingCard} ${styles.cardCpp}`}>
                <span className={styles.floatingCardIcon}>{SUPPORTED_LANGUAGES[2].icon}</span>
                <div className={styles.floatingCardText}>
                  <span className={styles.floatingCardTitle}>C++20</span>
                  <span className={styles.floatingCardSub}>GCC 13</span>
                </div>
              </div>

              {/* 3. Center Target Asymptotic Card */}
              <div className={`${styles.floatingCard} ${styles.cardCenter}`}>
                <div className={styles.cardCenterHeader}>
                  <span className={styles.centerTagOptimal}>O(n) Optimal</span>
                  <span className={styles.centerBadgeSpeed}>102× faster</span>
                </div>
                <div className={styles.cardCenterSparkline}>
                  <svg width="110" height="22" viewBox="0 0 110 22" fill="none">
                    <path d="M 0 19 L 40 18 L 80 15 L 110 4" stroke="var(--accepted)" strokeWidth="2.5" strokeLinecap="round" />
                    <circle cx="110" cy="4" r="3.5" fill="var(--accepted)" />
                  </svg>
                  <span className={styles.cardCenterMeta}>Linear Fit · Validated</span>
                </div>
              </div>

              {/* 4. Java Card (Mid Left) */}
              <div className={`${styles.floatingCard} ${styles.cardJava}`}>
                <span className={styles.floatingCardIcon}>{SUPPORTED_LANGUAGES[1].icon}</span>
                <div className={styles.floatingCardText}>
                  <span className={styles.floatingCardTitle}>Java</span>
                  <span className={styles.floatingCardSub}>JDK 21</span>
                </div>
              </div>

              {/* 5. JavaScript Card (Mid Right) */}
              <div className={`${styles.floatingCard} ${styles.cardJs}`}>
                <span className={styles.floatingCardIcon}>{SUPPORTED_LANGUAGES[4].icon}</span>
                <div className={styles.floatingCardText}>
                  <span className={styles.floatingCardTitle}>JavaScript</span>
                  <span className={styles.floatingCardSub}>Node 20</span>
                </div>
              </div>

              {/* 6. Benchmark Pill (Bottom Left) */}
              <div className={`${styles.floatingCard} ${styles.cardBenchmark}`}>
                <span className={styles.benchmarkDot} />
                <span className={styles.benchmarkText}>N=10,000 · 1.4ms</span>
              </div>

              {/* 7. SQL Card (Bottom Right) */}
              <div className={`${styles.floatingCard} ${styles.cardSql}`}>
                <span className={styles.floatingCardIcon}>{SUPPORTED_LANGUAGES[5].icon}</span>
                <div className={styles.floatingCardText}>
                  <span className={styles.floatingCardTitle}>MySQL</span>
                  <span className={styles.floatingCardSub}>8.0 Query</span>
                </div>
              </div>
            </div>
          </div>

          {/* ── Supported Languages Horizontal Scrolling Marquee ───── */}
          <div className={styles.languagesBar}>
            <div className={styles.languagesHeader}>
              <span className={styles.languagesPulseDot} aria-hidden="true" />
              <span className={styles.languagesEyebrow}>SUPPORTED EXECUTION RUNTIMES &amp; LANGUAGES</span>
            </div>

            <div className={styles.marqueeWrapper} aria-label="Supported programming languages ticker">
              <div className={styles.marqueeTrack}>
                {[...SUPPORTED_LANGUAGES, ...SUPPORTED_LANGUAGES, ...SUPPORTED_LANGUAGES].map((lang, idx) => (
                  <div key={`${lang.id}-${idx}`} className={styles.langPill}>
                    <span className={styles.langIcon} aria-hidden="true">
                      {lang.icon}
                    </span>
                    <div className={styles.langInfo}>
                      <span className={styles.langName}>{lang.name}</span>
                      <span className={styles.langMeta}>{lang.version} · {lang.runtime}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── 2. How it works: Verification Pipeline ─────────────── */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>The Verification Pipeline</h2>
          <p className={styles.sectionSubtitle}>
            From test suite correctness to empirical Big-O classification.
          </p>
        </div>

        <div className={styles.pipelineGrid}>
          <div className={styles.pipelineCard}>
            <div className={styles.stageTag}>Stage 01</div>
            <h3 className={styles.stageTitle}>Multi-Language Editor</h3>
            <p className={styles.stageBody}>
              Write Python, Java, C++, C, or SQL solutions in an integrated Monaco editor
              with syntax validation, testcase tables, and starter boilerplate.
            </p>
          </div>

          <div className={styles.pipelineCard}>
            <div className={styles.stageTag}>Stage 02</div>
            <h3 className={styles.stageTitle}>Correctness Verification</h3>
            <p className={styles.stageBody}>
              Your solution runs in an isolated sandbox against functional test suites to verify
              correct outputs, constraints, and runtime safety.
            </p>
          </div>

          <div className={styles.pipelineCard}>
            <div className={styles.stageTag}>Stage 03</div>
            <h3 className={styles.stageTitle}>Empirical Scaling</h3>
            <p className={styles.stageBody}>
              Accepted solutions execute across generated inputs scaling from N=10 to N=10,000,
              measuring isolated wall-clock execution time at each order of magnitude.
            </p>
          </div>

          <div className={styles.pipelineCard}>
            <div className={styles.stageTag}>Stage 04</div>
            <h3 className={styles.stageTitle}>Asymptotic Classification</h3>
            <p className={styles.stageBody}>
              Curve-fitting maps measured runtimes to theoretical complexity classes and plots
              your empirical scaling curve alongside the mathematical target on log-log axes.
            </p>
          </div>
        </div>
      </section>

      {/* ── 3. Differentiation: Signature Benchmark Visual ──────── */}
      <section className={styles.section}>
        <div className={styles.diff}>
          <div className={styles.diffCopy}>
            <div className={styles.diffEyebrow}>Asymptotic Analysis</div>
            <h2 className={styles.diffTitle}>A brute-force solution and an optimal solution both receive green checkmarks</h2>
            <p className={styles.diffBody}>
              On traditional coding platforms, any solution that completes within the time limit is labeled Accepted.
              An O(n²) nested loop and an O(n) hash table look identical on the submission screen.
            </p>
            <p className={styles.diffBody}>
              AlgoLens measures how execution time grows with input size. When an Accepted solution exhibits
              higher-order polynomial scaling, AlgoLens flags the complexity gap and delivers structural
              optimization hints without spoiling the solution code.
            </p>
            <div className={styles.diffCallout}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={styles.diffCalloutIcon} aria-hidden="true">
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
              <span>Both implementations pass test suites, but only the optimal approach handles large inputs without timing out.</span>
            </div>
          </div>

          {/* Signature Moment: Log-Log Complexity Curve Graphic */}
          <div className={styles.diffVisual}>
            <div className={styles.diffVisualHeader}>
              <div>
                <span className={styles.diffProblemName}>Two Sum</span>
                <span className={styles.diffProblemSubtitle}> · Scaled Runtime Benchmark</span>
              </div>
              <span className={styles.diffBadge}>Log-Log Axes</span>
            </div>

            <div className={styles.graphContainer}>
              <svg viewBox="0 0 480 230" className={styles.graphSvg} aria-label="Runtime growth comparison chart">
                {/* Grid Lines */}
                {[
                  { y: 35, label: '100ms' },
                  { y: 80, label: '10ms' },
                  { y: 125, label: '1ms' },
                  { y: 170, label: '0.1ms' },
                ].map((grid) => (
                  <g key={grid.y}>
                    <line x1="50" y1={grid.y} x2="455" y2={grid.y} stroke="#21262D" strokeDasharray="3 3" />
                    <text x="44" y={grid.y + 3} fill="#6E7681" fontSize="9.5" textAnchor="end" fontFamily="var(--font-mono)">
                      {grid.label}
                    </text>
                  </g>
                ))}

                {/* X-axis tick labels */}
                {[
                  { x: 70, label: 'N=10' },
                  { x: 165, label: 'N=100' },
                  { x: 260, label: 'N=1k' },
                  { x: 355, label: 'N=5k' },
                  { x: 440, label: 'N=10k' },
                ].map((tick) => (
                  <text key={tick.x} x={tick.x} y="192" fill="#6E7681" fontSize="9.5" textAnchor="middle" fontFamily="var(--font-mono)">
                    {tick.label}
                  </text>
                ))}

                {/* O(n^2) Quadratic Curve (Orange) */}
                <path
                  d="M 70 170 Q 200 162, 260 130 T 440 38"
                  fill="none"
                  stroke="#F97316"
                  strokeWidth="2.5"
                />

                {/* O(n) Linear Optimal Curve (Emerald Green) */}
                <path
                  d="M 70 170 L 440 165"
                  fill="none"
                  stroke="#22C55E"
                  strokeWidth="2"
                  strokeDasharray="4 2"
                />

                {/* Data Points on O(n^2) Curve */}
                {[
                  { x: 70, y: 170 },
                  { x: 165, y: 160 },
                  { x: 260, y: 130 },
                  { x: 355, y: 85 },
                  { x: 440, y: 38, label: '142.8ms' },
                ].map((pt, i) => (
                  <g key={`quad-${i}`}>
                    <circle cx={pt.x} cy={pt.y} r="4" fill="#F97316" stroke="#0D1117" strokeWidth="1.5" />
                    {pt.label && (
                      <g>
                        <rect x={pt.x - 62} y={pt.y - 10} width="56" height="16" rx="3" fill="#21262D" stroke="#30363D" />
                        <text x={pt.x - 34} y={pt.y + 2} fill="#F0F6FC" fontSize="9" fontWeight="600" textAnchor="middle" fontFamily="var(--font-mono)">
                          {pt.label}
                        </text>
                      </g>
                    )}
                  </g>
                ))}

                {/* Data Points on O(n) Curve */}
                {[
                  { x: 70, y: 170 },
                  { x: 165, y: 168 },
                  { x: 260, y: 167 },
                  { x: 355, y: 166 },
                  { x: 440, y: 165, label: '1.4ms' },
                ].map((pt, i) => (
                  <g key={`lin-${i}`}>
                    <circle cx={pt.x} cy={pt.y} r="3.5" fill="#22C55E" stroke="#0D1117" strokeWidth="1.5" />
                    {pt.label && (
                      <g>
                        <rect x={pt.x + 8} y={pt.y - 10} width="46" height="16" rx="3" fill="#21262D" stroke="#30363D" />
                        <text x={pt.x + 31} y={pt.y + 2} fill="#22C55E" fontSize="9" fontWeight="600" textAnchor="middle" fontFamily="var(--font-mono)">
                          {pt.label}
                        </text>
                      </g>
                    )}
                  </g>
                ))}

                {/* Axis Label */}
                <text x="455" y="215" fill="#6E7681" fontSize="9.5" textAnchor="end" fontFamily="var(--font-mono)">
                  Input Size (N)
                </text>
              </svg>
            </div>

            <div className={styles.diffLegend}>
              <div className={styles.legendItem}>
                <span className={styles.legendIndicator} style={{ background: '#F97316' }} />
                <span>Your Solution: O(n²) Quadratic</span>
              </div>
              <div className={styles.legendItem}>
                <span className={styles.legendIndicator} style={{ background: '#22C55E' }} />
                <span>Optimal Target: O(n) Linear</span>
              </div>
            </div>

            <div className={styles.diffVerdictBar}>
              <span className={styles.verdictStatus}>Verdict: Accepted</span>
              <span className={styles.complexityNotice}>Optimization gap detected (102× slower at N=10,000)</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── 4. Problem Bank Preview ────────────────────────────── */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>Problem Catalog Preview</h2>
          <p className={styles.sectionSubtitle}>
            Algorithmic and database challenges configured for complexity profiling.
          </p>
        </div>

        {loadingProblems ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
            <div className="spinner" />
          </div>
        ) : problems.length > 0 ? (
          <div className={styles.problemGrid}>
            {problems.map((p) => (
              <Link key={p.id} to={`/problems/${p.id}`} className={styles.problemCard}>
                <div className={styles.problemCardHeader}>
                  <span className={`badge badge-${(p.difficulty || 'medium').toLowerCase()}`}>
                    {p.difficulty}
                  </span>
                  <span className={styles.problemMetaCat}>
                    {p.generator_key?.startsWith('sql_') ? 'SQL' : 'Algorithms'}
                  </span>
                </div>
                <h3 className={styles.problemTitle}>{p.title}</h3>
                <div className={styles.problemFooter}>
                  <span>Target:</span>
                  <span className={styles.optimalMono}>{p.optimal_time_complexity || 'O(n)'}</span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className={styles.emptyProblems}>
            <p>Connect to the backend service to load catalog problems.</p>
            <Link to="/problems" className="btn btn-secondary">
              Go to Problem Catalog
            </Link>
          </div>
        )}
      </section>

      {/* ── 5. Final CTA ──────────────────────────────────────── */}
      <section className={styles.finalCta}>
        <h2 className={styles.finalTitle}>Benchmark your code against mathematical lower bounds.</h2>
        <p className={styles.finalSubtitle}>
          Select any algorithmic or SQL challenge and verify whether your solution achieves optimal asymptotic scaling.
        </p>
        <div className={styles.finalCtas}>
          <Link to="/problems" className="btn btn-primary" style={{ fontSize: '1rem', padding: '0.7rem 2rem' }}>
            Browse Problems
          </Link>
          {!user && (
            <Link to="/register" className="btn btn-secondary" style={{ fontSize: '1rem', padding: '0.7rem 1.75rem' }}>
              Create Account
            </Link>
          )}
        </div>
      </section>

      {/* ── 6. Clean Engineering Footer ───────────────────────── */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerBrand}>
            <span className={styles.footerLogo}>AlgoLens</span>
            <p className={styles.footerTagline}>
              Empirical algorithmic complexity judge and runtime profiling workbench.
            </p>
          </div>
          <div className={styles.footerLinks}>
            <Link to="/problems" className={styles.footerLink}>Problems</Link>
            <Link to="/forum" className={styles.footerLink}>Discussion Forum</Link>
            <Link to="/login" className={styles.footerLink}>Sign In</Link>
            <Link to="/register" className={styles.footerLink}>Create Account</Link>
          </div>
        </div>
        <div className={styles.footerBottom}>
          <span>AlgoLens Competitive Judge System</span>
          <span>Shortcut: Press / to search problems anytime</span>
        </div>
      </footer>
    </div>
  );
}
