import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import api from '../api/client';
import NotFound from './NotFound';
import { getStarterSnippet } from '../utils/starterSnippets';
import SqlTableOutput from '../components/SqlTableOutput';
import styles from './ProblemDetail.module.css';

export default function ProblemDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [problem, setProblem] = useState(null);
  const [loading, setLoading] = useState(true);

  const initialLanguage = (location.state?.language || 'java').toLowerCase();
  const initialCode = location.state?.sourceCode ?? location.state?.code ?? getStarterSnippet(null, initialLanguage);

  const [language, setLanguage] = useState(initialLanguage);
  const [code, setCode] = useState(initialCode);
  const [running, setRunning] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [runError, setRunError] = useState('');
  const [runResults, setRunResults] = useState(null);
  const [activeTestCaseTab, setActiveTestCaseTab] = useState(0);
  const [testCasesHeight, setTestCasesHeight] = useState(210);
  const [isTestCasesOpen, setIsTestCasesOpen] = useState(true);
  const isDraggingRef = useRef(false);

  useEffect(() => {
    if (location.state?.sourceCode !== undefined || location.state?.code !== undefined) {
      const passedCode = location.state?.sourceCode ?? location.state?.code;
      const passedLang = (location.state?.language || 'java').toLowerCase();
      setLanguage(passedLang);
      setCode(passedCode);
    }
  }, [id, location.state]);

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDraggingRef.current) return;
      const windowHeight = window.innerHeight;
      // 55px submit bar offset
      const newHeight = windowHeight - e.clientY - 55;
      if (newHeight >= 38 && newHeight <= windowHeight * 0.75) {
        setTestCasesHeight(newHeight);
        if (newHeight > 50) {
          setIsTestCasesOpen(true);
        }
      }
    };

    const handleMouseUp = () => {
      if (isDraggingRef.current) {
        isDraggingRef.current = false;
        document.body.style.cursor = 'default';
        document.body.style.userSelect = 'auto';
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, []);

  const startResizing = (e) => {
    e.preventDefault();
    isDraggingRef.current = true;
    document.body.style.cursor = 'row-resize';
    document.body.style.userSelect = 'none';
  };

  useEffect(() => {
    api.get(`/problems/${id}`)
      .then(r => {
        setProblem(r.data);
        const isSql = r.data.generator_key?.startsWith('sql_');
        let currentLang = language;
        if (isSql && language !== 'mysql' && language !== 'sql') {
          currentLang = 'mysql';
          setLanguage('mysql');
        }
        if (location.state?.sourceCode === undefined && location.state?.code === undefined) {
          setCode(getStarterSnippet(r.data, currentLang));
        }
      })
      .catch(() => setError('Problem not found'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    setCode(getStarterSnippet(problem, newLang));
    setRunResults(null);
  };

  const handleResetCode = () => {
    setCode(getStarterSnippet(problem, language));
  };

  const handleRun = async () => {
    if (!code.trim()) { setError('Please write some code first.'); return; }
    setError('');
    setRunError('');
    setRunning(true);
    setIsTestCasesOpen(true);

    try {
      const { data } = await api.post('/submissions/run', {
        problem_id: id,
        source_code: code,
        language: language,
      });
      setRunResults(data);
    } catch (err) {
      setRunError(err.response?.data?.detail || 'Run execution failed');
    } finally {
      setRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!code.trim()) { setError('Please write some code first.'); return; }
    setError('');
    setRunError('');
    setSubmitting(true);

    try {
      const { data } = await api.post('/submissions', {
        problem_id: id,
        source_code: code,
        language: language,
      });

      // Redirect immediately to the comparison & complexity page
      navigate(`/results/${data.id}`, { state: { optimalComplexity: problem?.optimal_time_complexity } });
    } catch (err) {
      setError(err.response?.data?.detail || 'Submission failed');
      setSubmitting(false);
    }
  };

  if (loading) return <div className={styles.center}><div className="spinner" /></div>;
  if (error && !problem) return <NotFound />;

  const isDatabaseProblem = problem?.generator_key?.startsWith('sql_') || language === 'mysql' || language === 'sql';

  return (
    <div className={styles.layout}>
      {/* ── Left: problem description ─────────────────────── */}
      <div className={styles.description}>
        <div className={styles.problemHeader}>
          <h1 className={styles.title}>{problem?.title}</h1>
          <span className={`badge badge-${problem?.difficulty}`}>{problem?.difficulty}</span>
        </div>
        <div className={styles.complexity}>
          <span>Optimal: <strong>{problem?.optimal_time_complexity}</strong></span>
          <span className={styles.sep}>·</span>
          <span>Space: <strong>{problem?.optimal_space_complexity}</strong></span>
        </div>
        <div
          className={styles.desc}
          dangerouslySetInnerHTML={{ __html: markdownToHtml(problem?.description || '') }}
        />
      </div>

      {/* ── Right: editor + submit ────────────────────────── */}
      <div className={styles.editorPanel}>
        <div className={styles.editorHeader}>
          <div className={styles.editorTitle}>
            <svg className={styles.codeIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="16 18 22 12 16 6"></polyline>
              <polyline points="8 6 2 12 8 18"></polyline>
            </svg>
            <span>Solution Editor</span>
          </div>

          <div className={styles.editorActions}>
            <button
              type="button"
              className={styles.resetBtn}
              onClick={handleResetCode}
              title="Reset code to problem starter snippet"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              <span>Reset Starter</span>
            </button>

            <div className={styles.languageBox}>
              <span className={styles.languageBoxLabel}>Language</span>
              <div className={styles.selectWrapper}>
                <select
                  value={language}
                  onChange={e => handleLanguageChange(e.target.value)}
                  className={styles.languageSelect}
                >
                  {isDatabaseProblem ? (
                    <>
                      <option value="mysql">MySQL 8.0</option>
                      <option value="sql">Standard SQL</option>
                    </>
                  ) : (
                    <>
                      <option value="java">Java 21</option>
                      <option value="python">Python 3</option>
                      <option value="cpp">C++20 (GCC)</option>
                      <option value="c">C11 (GCC)</option>
                      <option value="javascript">JavaScript (Node.js)</option>
                      <option value="mysql">MySQL 8.0</option>
                      <option value="sql">Standard SQL</option>
                    </>
                  )}
                </select>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.monacoWrapper}>
          <Editor
            height="100%"
            language={
              language === 'mysql' || language === 'sql'
                ? 'sql'
                : language === 'cpp' || language === 'c'
                ? 'cpp'
                : language
            }
            value={code}
            onChange={v => setCode(v || '')}
            theme="vs-dark"
            options={{
              fontSize: 13,
              fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              lineNumbers: 'on',
              wordWrap: 'on',
              tabSize: 4,
              automaticLayout: true,
            }}
          />
        </div>

        {/* ── Resizer Drag Handle ─────────────── */}
        {problem?.test_cases?.length > 0 && (
          <div
            className={styles.resizerHandle}
            onMouseDown={startResizing}
            title="Drag to adjust testcase window height"
          >
            <div className={styles.resizerGrip} />
          </div>
        )}

        {/* ── Sample Testcases & Run Results Panel ────────── */}
        {problem?.test_cases?.length > 0 && (
          <div
            className={styles.testCasesPanel}
            style={{ height: isTestCasesOpen ? `${testCasesHeight}px` : '38px' }}
          >
            <div className={styles.testCasesHeader}>
              <button
                className={styles.collapseToggleBtn}
                onClick={() => setIsTestCasesOpen(prev => !prev)}
                title={isTestCasesOpen ? 'Collapse Testcases (▲)' : 'Expand Testcases (▼)'}
              >
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  style={{
                    transform: isTestCasesOpen ? 'rotate(180deg)' : 'rotate(0deg)',
                    transition: 'transform 0.2s ease',
                  }}
                >
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </button>

              <div className={styles.testCasesTitle}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent)' }}>
                  <polyline points="9 11 12 14 22 4"></polyline>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                </svg>
                <span>{runResults ? 'Test Results' : isDatabaseProblem ? 'Database Testcases & Tables' : 'Sample Testcases'}</span>
              </div>

              <div className={styles.caseTabs}>
                {problem.test_cases.map((tc, idx) => {
                  const outcome = runResults?.test_cases?.[idx];
                  const tabResultClass = outcome
                    ? outcome.passed
                      ? styles.caseResultPassed
                      : styles.caseResultFailed
                    : '';

                  return (
                    <button
                      key={tc.id || idx}
                      className={`${styles.caseTab} ${activeTestCaseTab === idx ? styles.caseTabActive : ''} ${tabResultClass}`}
                      onClick={() => setActiveTestCaseTab(idx)}
                    >
                      {outcome ? (outcome.passed ? '✓ ' : '✕ ') : ''}Case {idx + 1}
                    </button>
                  );
                })}
              </div>

              {runResults && (
                <div className={styles.verdictHeader}>
                  {runResults.verdict === 'Accepted' ? (
                    <span className={`${styles.verdictPill} ${styles.verdictAccepted}`}>✓ Accepted</span>
                  ) : runResults.verdict === 'Wrong Answer' ? (
                    <span className={`${styles.verdictPill} ${styles.verdictWrong}`}>✕ Wrong Answer</span>
                  ) : (
                    <span className={`${styles.verdictPill} ${styles.verdictError}`}>⚠️ {runResults.verdict}</span>
                  )}
                </div>
              )}
            </div>

            {isTestCasesOpen && (
              <div className={styles.caseBody}>
                {runError && !isDatabaseProblem && (
                  <div className={styles.failureBox}>
                    <span className={styles.failureTitle}>Execution Error</span>
                    <pre className={styles.failurePre}>{runError}</pre>
                  </div>
                )}

                {runResults?.failure_detail && !isDatabaseProblem && (
                  <div className={styles.failureBox}>
                    <span className={styles.failureTitle}>{runResults.verdict}</span>
                    <pre className={styles.failurePre}>{runResults.failure_detail}</pre>
                  </div>
                )}

                {isDatabaseProblem ? (
                  <SqlTableOutput
                    testCaseInput={problem.test_cases[activeTestCaseTab]?.input}
                    userOutput={runResults?.test_cases?.[activeTestCaseTab]?.actual_output}
                    expectedOutput={problem.test_cases[activeTestCaseTab]?.expected_output}
                    passed={runResults?.test_cases?.[activeTestCaseTab]?.passed}
                    runtimeMs={runResults?.test_cases?.[activeTestCaseTab]?.runtime_ms}
                    rawError={runError || runResults?.failure_detail}
                    isEvaluating={running}
                  />
                ) : (
                  <div className={runResults?.test_cases?.[activeTestCaseTab] ? styles.caseGrid3 : styles.caseGrid}>
                    <div className={styles.caseField}>
                      <span className={styles.caseLabel}>Input =</span>
                      <pre className={styles.caseCode}>{problem.test_cases[activeTestCaseTab]?.input}</pre>
                    </div>
                    {runResults?.test_cases?.[activeTestCaseTab] && (
                      <div className={styles.caseField}>
                        <span className={styles.caseLabel}>Your Output =</span>
                        <pre className={`${styles.caseCode} ${runResults.test_cases[activeTestCaseTab].passed ? styles.outputPassed : styles.outputFailed}`}>
                          {runResults.test_cases[activeTestCaseTab]?.actual_output || '<no output>'}
                        </pre>
                      </div>
                    )}
                    <div className={styles.caseField}>
                      <span className={styles.caseLabel}>Expected Output =</span>
                      <pre className={styles.caseCode}>{problem.test_cases[activeTestCaseTab]?.expected_output}</pre>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <div className={styles.submitBar}>
          <div className={styles.submitBarLeft}>
            <span style={{ fontSize: '0.85rem', color: code.length > 18000 ? 'var(--wrong)' : 'var(--text-muted)' }}>
              {code.length.toLocaleString()} / 20,000 chars
            </span>
            {error && <span className={styles.submitError}>{error}</span>}
          </div>

          <div className={styles.btnGroup}>
            {/* Run Button */}
            <button
              id="run-btn"
              className={styles.runBtn}
              onClick={handleRun}
              disabled={running || submitting || !code.trim() || code.length > 20000}
              title="Run code against sample test cases (doesn't submit to benchmark)"
            >
              {running ? (
                <><span className="spinner" style={{ width: 13, height: 13 }} /> Running…</>
              ) : (
                <>
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                  </svg>
                  <span>Run</span>
                </>
              )}
            </button>

            {/* Submit Button */}
            <button
              id="submit-btn"
              className={styles.submitBtn}
              onClick={handleSubmit}
              disabled={running || submitting || !code.trim() || code.length > 20000}
              title="Submit code for full correctness verification, empirical benchmarking & complexity analysis"
            >
              {submitting ? (
                <><span className="spinner" style={{ width: 14, height: 14 }} /> Submitting…</>
              ) : (
                <>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
                    <polyline points="12 13 12 7 9 10"/>
                    <polyline points="12 7 15 10"/>
                  </svg>
                  <span>Submit</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/** Comprehensive markdown → HTML renderer for problem descriptions, examples, constraints & hints. */
function markdownToHtml(md) {
  if (!md) return '';

  // 1. Preserve code blocks
  const codeBlocks = [];
  let text = md.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    codeBlocks.push(`<pre><code class="lang-${lang}">${escapeHtml(code.trim())}</code></pre>`);
    return `__CODE_BLOCK_${codeBlocks.length - 1}__`;
  });

  // 2. Preserve details / summary blocks (hints)
  const detailsBlocks = [];
  text = text.replace(/<details>\s*<summary>(.*?)<\/summary>([\s\S]*?)<\/details>/gi, (_, summary, body) => {
    detailsBlocks.push(
      `<details class="${styles.hintAccordion}">` +
        `<summary class="${styles.hintSummary}"><span class="${styles.hintIcon}">💡</span><span>${summary.replace(/💡\s*/, '')}</span></summary>` +
        `<div class="${styles.hintContent}"><p>${body.trim()}</p></div>` +
      `</details>`
    );
    return `__DETAILS_BLOCK_${detailsBlocks.length - 1}__`;
  });

  // 3. Convert headers
  text = text.replace(/^### (.*$)/gim, `<h3 class="${styles.heading3}">$1</h3>`);
  text = text.replace(/^## (.*$)/gim, `<h2 class="${styles.heading2}">$1</h2>`);
  text = text.replace(/^# (.*$)/gim, `<h1 class="${styles.heading1}">$1</h1>`);

  // 4. Convert bold and inline code
  text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>');

  // 5. Convert lists (- item)
  text = text.replace(/(?:^[ \t]*-[ \t]+.+$\n?)+/gm, (match) => {
    const items = match.trim().split('\n').map(line => {
      const content = line.replace(/^[ \t]*-[ \t]+/, '');
      return `<li>${content}</li>`;
    }).join('');
    return `<ul class="${styles.bulletList}">${items}</ul>`;
  });

  // 6. Convert tables (| col | col |)
  text = text.replace(/(?:^\|.+\|$\n?)+/gm, (match) => {
    const rows = match.trim().split('\n').filter(r => !r.includes('---'));
    if (rows.length === 0) return '';
    const headerRow = rows[0].split('|').filter(c => c.trim()).map(c => `<th>${c.trim()}</th>`).join('');
    const bodyRows = rows.slice(1).map(r => {
      const cells = r.split('|').filter(c => c.trim()).map(c => `<td>${c.trim()}</td>`).join('');
      return `<tr>${cells}</tr>`;
    }).join('');
    return `<table class="${styles.descTable}"><thead><tr>${headerRow}</tr></thead><tbody>${bodyRows}</tbody></table>`;
  });

  // 7. Paragraphs
  const paragraphs = text.split(/\n{2,}/);
  text = paragraphs.map(p => {
    p = p.trim();
    if (!p) return '';
    if (p.startsWith('<h') || p.startsWith('<ul') || p.startsWith('<table') || p.startsWith('__DETAILS_BLOCK_') || p.startsWith('__CODE_BLOCK_')) {
      return p;
    }
    return `<p>${p.replace(/\n/g, '<br/>')}</p>`;
  }).join('');

  // 8. Restore details blocks
  text = text.replace(/__DETAILS_BLOCK_(\d+)__/g, (_, idx) => detailsBlocks[parseInt(idx, 10)]);

  // 9. Restore code blocks
  text = text.replace(/__CODE_BLOCK_(\d+)__/g, (_, idx) => codeBlocks[parseInt(idx, 10)]);

  return text;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

