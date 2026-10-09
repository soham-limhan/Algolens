import styles from '../pages/Auth.module.css';

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

export default function AuthShowcase() {
  return (
    <div className={styles.showcaseSide}>
      <h1 className={styles.headline}>
        Your solution passed.<br />
        <span className={styles.accentText}>Is it actually optimal?</span>
      </h1>

      <p className={styles.subText}>
        Traditional judges stop at pass or fail. AlgoLens benchmarks execution
        runtimes across generated inputs from N=10 to N=10,000, plots your empirical curve
        on log-log axes, and identifies algorithmic complexity gaps before you submit to production.
      </p>

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
  );
}
