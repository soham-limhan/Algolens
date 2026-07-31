import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import api from '../api/client';
import styles from './ProblemDetail.module.css';

const CODE_TEMPLATES = {
  java: `import java.util.*;

public class Solution {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        // Read input and write your solution here
    }
}
`,
  python: `import sys

def main():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    # Read input and write your solution here

if __name__ == "__main__":
    main()
`,
  cpp: `#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(NULL);
    // Read input and write your solution here
    return 0;
}
`,
  c: `#include <stdio.h>
#include <stdlib.h>

int main() {
    // Read input and write your solution here
    return 0;
}
`,
  javascript: `const fs = require('fs');

function main() {
    const input = fs.readFileSync(0, 'utf-8');
    // Read input and write your solution here
}

main();
`,
};

export default function ProblemDetail() {
  const { id } = useParams();
  const [problem, setProblem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState('java');
  const [code, setCode] = useState(CODE_TEMPLATES.java);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [activeTestCaseTab, setActiveTestCaseTab] = useState(0);

  const [submissionState, setSubmissionState] = useState('idle'); // 'idle' | 'running' | 'result'
  const [submissionData, setSubmissionData] = useState(null);
  const [simulationStep, setSimulationStep] = useState(1);
  const pollIntervalRef = useRef(null);

  useEffect(() => {
    api.get(`/problems/${id}`)
      .then(r => setProblem(r.data))
      .catch(() => setError('Problem not found'))
      .finally(() => setLoading(false));

    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, [id]);

  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    setCode(CODE_TEMPLATES[newLang] || '');
  };

  const handleSubmit = async () => {
    if (!code.trim()) { setError('Please write some code first.'); return; }
    setError('');
    setSubmitting(true);
    setSubmissionState('running');
    setSimulationStep(1);
    setActiveTestCaseTab(0);
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);

    const step1 = setTimeout(() => setSimulationStep(2), 600);
    const step2 = setTimeout(() => setSimulationStep(3), 1200);

    try {
      const { data } = await api.post('/submissions', {
        problem_id: id,
        source_code: code,
        language: language,
      });

      const subId = data.id;

      pollIntervalRef.current = setInterval(async () => {
        try {
          const res = await api.get(`/submissions/${subId}`);
          if (res.data.status === 'complete' || res.data.status === 'failed') {
            clearInterval(pollIntervalRef.current);
            clearTimeout(step1);
            clearTimeout(step2);
            setSubmissionData(res.data);
            setSubmissionState('result');
            setSubmitting(false);
          }
        } catch (err) {
          clearInterval(pollIntervalRef.current);
          clearTimeout(step1);
          clearTimeout(step2);
          setError(err.response?.data?.detail || 'Failed to fetch submission results');
          setSubmissionState('idle');
          setSubmitting(false);
        }
      }, 1000);
    } catch (err) {
      clearTimeout(step1);
      clearTimeout(step2);
      setError(err.response?.data?.detail || 'Submission failed');
      setSubmissionState('idle');
      setSubmitting(false);
    }
  };

  if (loading) return <div className={styles.center}><div className="spinner" /></div>;
  if (error && !problem) return <div className={styles.center} style={{ color: 'var(--wrong)' }}>{error}</div>;

  const isPassed = submissionData?.status === 'complete';
  const rawTestResults = submissionData?.test_results;
  const sampleCases = problem?.test_cases || [];

  let resultCases = [];
  if (rawTestResults && rawTestResults.length > 0) {
    resultCases = rawTestResults;
  } else if (sampleCases.length > 0) {
    resultCases = sampleCases.map((tc) => ({
      test_case_id: tc.id,
      passed: isPassed,
      input: tc.input,
      expected: tc.expected_output,
      actual: isPassed ? tc.expected_output : (submissionData?.failure_detail || 'Error'),
    }));
  }
  const activeResultCase = resultCases[activeTestCaseTab] || resultCases[0];

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

          <div className={styles.languageBox}>
            <span className={styles.languageBoxLabel}>Language</span>
            <div className={styles.selectWrapper}>
              <select
                value={language}
                onChange={e => handleLanguageChange(e.target.value)}
                className={styles.languageSelect}
              >
                <option value="java">Java 21</option>
                <option value="python">Python 3</option>
                <option value="cpp">C++20 (GCC)</option>
                <option value="c">C11 (GCC)</option>
                <option value="javascript">JavaScript (Node.js)</option>
              </select>
            </div>
          </div>
        </div>
        <div className={styles.monacoWrapper}>
          <Editor
            height="100%"
            language={language === 'cpp' || language === 'c' ? 'cpp' : language}
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

        {/* ── State 1: Simulation Mode ─────────────────────── */}
        {submissionState === 'running' && (
          <div className={styles.simulationPanel}>
            <div className={styles.simulationHeader}>
              <div className="spinner" style={{ width: 14, height: 14 }} />
              <span>Running Solution Simulation...</span>
            </div>
            <div className={styles.simulationSteps}>
              <div className={`${styles.simStep} ${simulationStep >= 1 ? styles.simStepActive : ''}`}>
                <span className={styles.stepDot}>{simulationStep > 1 ? '✓' : '1'}</span>
                <span>Compiling {language.toUpperCase()} source code</span>
              </div>
              <div className={`${styles.simStep} ${simulationStep >= 2 ? styles.simStepActive : ''}`}>
                <span className={styles.stepDot}>{simulationStep > 2 ? '✓' : '2'}</span>
                <span>Executing testcases in isolated sandbox environment</span>
              </div>
              <div className={`${styles.simStep} ${simulationStep >= 3 ? styles.simStepActive : ''}`}>
                <span className={styles.stepDot}>{simulationStep > 3 ? '✓' : '3'}</span>
                <span>Measuring empirical time & space complexity</span>
              </div>
            </div>
          </div>
        )}

        {/* ── State 2: Live Results View ────────────────────── */}
        {submissionState === 'result' && (
          <div className={styles.resultsPanel}>
            <div className={styles.resultsHeader}>
              <div className={styles.verdictGroup}>
                <span className={`${styles.verdictBadge} ${submissionData?.status === 'complete' ? styles.verdictPassed : styles.verdictFailed}`}>
                  {submissionData?.status === 'complete' ? '✓ Accepted' : (submissionData?.failure_detail ? '✗ Failed' : '✗ Wrong Answer')}
                </span>
                {submissionData?.empirical_complexity && (
                  <span className={styles.complexityTag}>
                    Empirical: <strong>{submissionData.empirical_complexity}</strong>
                  </span>
                )}
              </div>

              <div className={styles.caseTabs}>
                {resultCases.map((tc, idx) => (
                  <button
                    key={idx}
                    className={`${styles.caseTab} ${activeTestCaseTab === idx ? styles.caseTabActive : ''} ${tc.passed ? styles.tabPassed : styles.tabFailed}`}
                    onClick={() => setActiveTestCaseTab(idx)}
                  >
                    Case {idx + 1} {tc.passed ? '✓' : '✗'}
                  </button>
                ))}
              </div>

              <button
                className={styles.resetBtn}
                onClick={() => setSubmissionState('idle')}
              >
                Sample Cases
              </button>
            </div>

            <div className={styles.caseBody}>
              {submissionData?.failure_detail && submissionData?.status !== 'complete' && (
                <div className={styles.failureBox}>
                  <span className={styles.failureTitle}>Execution Log / Error:</span>
                  <pre className={styles.failurePre}>{submissionData.failure_detail}</pre>
                </div>
              )}

              {activeResultCase && (
                <div className={styles.caseGrid3}>
                  <div className={styles.caseField}>
                    <span className={styles.caseLabel}>Input</span>
                    <pre className={styles.caseCode}>{activeResultCase.input}</pre>
                  </div>
                  <div className={styles.caseField}>
                    <span className={styles.caseLabel}>Expected Output</span>
                    <pre className={styles.caseCode}>{activeResultCase.expected}</pre>
                  </div>
                  <div className={styles.caseField}>
                    <span className={styles.caseLabel}>Your Output</span>
                    <pre className={`${styles.caseCode} ${activeResultCase.passed ? styles.outputPassed : styles.outputFailed}`}>
                      {activeResultCase.actual || '(empty)'}
                    </pre>
                  </div>
                </div>
              )}

              {submissionData?.structural_hint && (
                <div className={styles.hintBox}>
                  <span className={styles.hintTitle}>💡 Optimization Hint:</span>
                  <p className={styles.hintText}>{submissionData.structural_hint}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ── State 3: Sample Testcases (Idle state) ────────── */}
        {submissionState === 'idle' && problem?.test_cases?.length > 0 && (
          <div className={styles.testCasesPanel}>
            <div className={styles.testCasesHeader}>
              <div className={styles.testCasesTitle}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent)' }}>
                  <polyline points="9 11 12 14 22 4"></polyline>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
                </svg>
                <span>Testcases</span>
              </div>
              <div className={styles.caseTabs}>
                {problem.test_cases.map((tc, idx) => (
                  <button
                    key={tc.id || idx}
                    className={`${styles.caseTab} ${activeTestCaseTab === idx ? styles.caseTabActive : ''}`}
                    onClick={() => setActiveTestCaseTab(idx)}
                  >
                    Case {idx + 1}
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.caseBody}>
              <div className={styles.caseGrid}>
                <div className={styles.caseField}>
                  <span className={styles.caseLabel}>Input =</span>
                  <pre className={styles.caseCode}>{problem.test_cases[activeTestCaseTab]?.input}</pre>
                </div>
                <div className={styles.caseField}>
                  <span className={styles.caseLabel}>Expected Output =</span>
                  <pre className={styles.caseCode}>{problem.test_cases[activeTestCaseTab]?.expected_output}</pre>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className={styles.submitBar}>
          <span style={{ fontSize: '0.85rem', color: code.length > 18000 ? 'var(--wrong)' : 'var(--text-muted)' }}>
            {code.length.toLocaleString()} / 20,000 chars
          </span>
          {error && <span className={styles.submitError} style={{ marginLeft: '1rem' }}>{error}</span>}
          <button
            id="submit-btn"
            className="btn btn-primary"
            onClick={handleSubmit}
            disabled={submitting || !code.trim() || code.length > 20000}
            style={{ marginLeft: 'auto' }}
          >
            {submitting ? <><span className="spinner" style={{ width: 16, height: 16 }} /> Submitting…</> : 'Submit'}
          </button>
        </div>
      </div>
    </div>
  );
}

/** Very minimal markdown → HTML for problem descriptions. */
function markdownToHtml(md) {
  return md
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/^/, '<p>').replace(/$/, '</p>')
    .replace(/<p>\s*<\/p>/g, '');
}
