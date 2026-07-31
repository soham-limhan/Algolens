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
            <span className={styles.accent}>But is it fast enough?</span>
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
            <div className={styles.fakeChart}>
              <div className={styles.fakeBar} style={{ height: '80%', background: 'var(--wrong)' }}>
                <span>O(n²)</span>
              </div>
              <div className={styles.fakeBar} style={{ height: '30%', background: 'var(--accepted)' }}>
                <span>O(n)</span>
              </div>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textAlign: 'center', marginTop: '0.5rem' }}>
              runtime growth comparison
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
