import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import styles from './Landing.module.css';

export default function Landing() {
  const [problems, setProblems] = useState([]);

  useEffect(() => {
    api.get('/problems').then(r => setProblems(r.data.slice(0, 4))).catch(() => {});
  }, []);

  return (
    <div className={styles.page}>
      {/* ── Hero ────────────────────────────────────────────── */}
      <section className={styles.hero}>
        <div className={styles.heroGlow} aria-hidden="true" />
        <div className={styles.heroContent}>
          <div className={styles.pill}>Complexity-aware judging</div>
          <h1 className={styles.headline}>
            Your solution passed.<br />
            <span className={styles.headline}>But is it fast enough?</span>
          </h1>
          <p className={styles.sub}>
            AlgoLens judges your Java solution for correctness — then measures how your 
            runtime actually grows as input scales, compares it to the known optimum, 
            and shows you exactly what to reconsider.
          </p>
          <div className={styles.ctas}>
            <Link to="/register" className="btn btn-primary" style={{ fontSize: '1rem', padding: '0.75rem 1.75rem' }}>
              Get started free
            </Link>
            <Link to="/login" className="btn btn-secondary" style={{ fontSize: '1rem', padding: '0.75rem 1.5rem' }}>
              Log in
            </Link>
            <Link to="/forum" className="btn btn-secondary" style={{ fontSize: '1rem', padding: '0.75rem 1.5rem' }}>
              Forum
            </Link>
          </div>
        </div>
      </section>

      {/* ── How it works ────────────────────────────────────── */}
      <section className={styles.section}>
        <h2 className={styles.sectionTitle}>How it works</h2>
        <div className={styles.steps}>
          {[
            { n: '01', title: 'Submit your solution', body: 'Write Java code in the browser. Hit Submit.' },
            { n: '02', title: 'Get judged', body: 'Standard verdict — Accepted, Wrong Answer, Compilation Error — against fixed hidden test cases.' },
            { n: '03', title: 'See your complexity', body: 'Your runtime is measured across scaled inputs. Your empirical O() is compared to the optimal on a shared log-log chart.' },
          ].map(s => (
            <div key={s.n} className={styles.step}>
              <div className={styles.stepNum}>{s.n}</div>
              <h3 className={styles.stepTitle}>{s.title}</h3>
              <p className={styles.stepBody}>{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Differentiation ─────────────────────────────────── */}
      <section className={styles.section}>
        <div className={styles.diff}>
          <div>
            <h2 className={styles.diffTitle}>Not just pass/fail</h2>
            <p className={styles.diffBody}>
              Most practice platforms give every correct solution a green checkmark — whether it 
              runs in O(n) or O(n²). AlgoLens closes that gap: a brute-force Two Sum and an 
              optimal HashMap solution both pass the test cases, but only one gets classified 
              as O(n) and shown the clean chart.
            </p>
          </div>
          <div className={styles.diffVisual}>
            <div className={styles.diffVisualHeader}>
              <div className={styles.diffVisualTitle}>
                <span>Two Sum</span>
                <span style={{ color: 'var(--text-dim)', fontWeight: 400 }}>· Empirical Benchmark</span>
              </div>
              <span className={styles.diffVisualBadge}>Runtime vs. Input (N)</span>
            </div>

            <div className={styles.graphContainer}>
              <svg viewBox="0 0 480 230" className={styles.graphSvg}>
                <defs>
                  {/* Gradients */}
                  <linearGradient id="quadGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ff375f" stopOpacity="0.35" />
                    <stop offset="100%" stopColor="#ff375f" stopOpacity="0.0" />
                  </linearGradient>
                  <linearGradient id="linGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#00b8a3" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#00b8a3" stopOpacity="0.0" />
                  </linearGradient>
                  <filter id="glowRed" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                  <filter id="glowGreen" x="-20%" y="-20%" width="140%" height="140%">
                    <feGaussianBlur stdDeviation="3" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>

                {/* Horizontal Grid lines */}
                {[
                  { y: 30, label: '150ms' },
                  { y: 75, label: '100ms' },
                  { y: 125, label: '50ms' },
                  { y: 175, label: '0ms' },
                ].map(grid => (
                  <g key={grid.y}>
                    <line x1="50" y1={grid.y} x2="460" y2={grid.y} stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
                    <text x="42" y={grid.y + 4} fill="#888" fontSize="10" textAnchor="end" fontFamily="var(--font-mono)">
                      {grid.label}
                    </text>
                  </g>
                ))}

                {/* X-axis tick labels */}
                {[
                  { x: 60, label: '1k' },
                  { x: 155, label: '2.5k' },
                  { x: 260, label: '5k' },
                  { x: 360, label: '7.5k' },
                  { x: 450, label: '10k' },
                ].map(tick => (
                  <text key={tick.x} x={tick.x} y="195" fill="#888" fontSize="10" textAnchor="middle" fontFamily="var(--font-mono)">
                    N={tick.label}
                  </text>
                ))}

                {/* Shaded Areas */}
                {/* O(n^2) area: (60,174) -> (155, 166) -> (260, 138) -> (360, 92) -> (450, 36) -> (450,175) -> (60,175) */}
                <path
                  d="M 60 174 Q 200 170, 260 138 T 450 36 L 450 175 L 60 175 Z"
                  fill="url(#quadGrad)"
                />
                {/* O(n) area: (60,174) -> (450, 172) -> (450,175) -> (60,175) */}
                <path
                  d="M 60 174 L 450 172 L 450 175 L 60 175 Z"
                  fill="url(#linGrad)"
                />

                {/* O(n^2) Quadratic Curve */}
                <path
                  d="M 60 174 Q 200 170, 260 138 T 450 36"
                  fill="none"
                  stroke="#ff375f"
                  strokeWidth="2.5"
                  filter="url(#glowRed)"
                />

                {/* O(n) Linear Curve */}
                <path
                  d="M 60 174 L 450 172"
                  fill="none"
                  stroke="#00b8a3"
                  strokeWidth="2.5"
                  filter="url(#glowGreen)"
                />

                {/* Data Points on O(n^2) curve */}
                {[
                  { x: 60, y: 174 },
                  { x: 155, y: 166 },
                  { x: 260, y: 138 },
                  { x: 360, y: 92 },
                  { x: 450, y: 36, label: '142.8ms', top: true },
                ].map((pt, i) => (
                  <g key={`quad-pt-${i}`}>
                    <circle cx={pt.x} cy={pt.y} r="4" fill="#ff375f" stroke="#1a1a1a" strokeWidth="1.5" />
                    {pt.label && (
                      <g>
                        <rect x={pt.x - 64} y={pt.y - 12} width="58" height="18" rx="4" fill="#ff375f" />
                        <text x={pt.x - 35} y={pt.y} fill="#fff" fontSize="9.5" fontWeight="700" textAnchor="middle" fontFamily="var(--font-mono)">
                          {pt.label}
                        </text>
                      </g>
                    )}
                  </g>
                ))}

                {/* Data Points on O(n) curve */}
                {[
                  { x: 60, y: 174 },
                  { x: 155, y: 173.5 },
                  { x: 260, y: 173 },
                  { x: 360, y: 172.5 },
                  { x: 450, y: 172, label: '1.4ms' },
                ].map((pt, i) => (
                  <g key={`lin-pt-${i}`}>
                    <circle cx={pt.x} cy={pt.y} r="4" fill="#00b8a3" stroke="#1a1a1a" strokeWidth="1.5" />
                    {pt.label && (
                      <g>
                        <rect x={pt.x - 48} y={pt.y + 7} width="44" height="18" rx="4" fill="#00b8a3" />
                        <text x={pt.x - 26} y={pt.y + 19} fill="#1a1a1a" fontSize="9.5" fontWeight="700" textAnchor="middle" fontFamily="var(--font-mono)">
                          {pt.label}
                        </text>
                      </g>
                    )}
                  </g>
                ))}

                {/* Axis Titles */}
                <text x="460" y="218" fill="#666" fontSize="9.5" textAnchor="end" fontFamily="var(--font-mono)">
                  Scale Input Size (N) →
                </text>
              </svg>
            </div>

            <div className={styles.diffLegend}>
              <div className={styles.legendItem}>
                <span className={styles.legendDot} style={{ background: '#ff375f', boxShadow: '0 0 8px rgba(255, 55, 95, 0.6)' }} />
                <span style={{ color: '#ff375f', fontWeight: 600 }}>O(n²) Brute Force</span>
              </div>
              <div className={styles.legendItem}>
                <span className={styles.legendDot} style={{ background: '#00b8a3', boxShadow: '0 0 8px rgba(0, 184, 163, 0.6)' }} />
                <span style={{ color: '#00b8a3', fontWeight: 600 }}>O(n) Optimal HashMap</span>
              </div>
            </div>

            <div className={styles.diffMeta}>
              <span>Classification verdict:</span>
              <span style={{ color: 'var(--easy)', fontWeight: 600 }}>✓ Optimal O(n) Detected (102× faster)</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Problem bank preview ─────────────────────────────── */}
      {problems.length > 0 && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Problem bank</h2>
          <div className={styles.problemGrid}>
            {problems.map(p => (
              <div key={p.id} className={styles.problemCard}>
                <span className={`badge badge-${p.difficulty}`}>{p.difficulty}</span>
                <div className={styles.problemTitle}>{p.title}</div>
              </div>
            ))}
          </div>
          <div style={{ textAlign: 'center', marginTop: '1.5rem' }}>
            <Link to="/register" className="btn btn-primary">Start practicing</Link>
          </div>
        </section>
      )}

      {/* ── Final CTA ────────────────────────────────────────── */}
      <section className={styles.finalCta}>
        <h2>Ready to level up your solutions?</h2>
        <Link to="/register" className="btn btn-primary" style={{ fontSize: '1rem', padding: '0.75rem 1.75rem' }}>
          Create free account
        </Link>
      </section>
    </div>
  );
}
