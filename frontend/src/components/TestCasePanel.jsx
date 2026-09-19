import SqlTableOutput from './SqlTableOutput';
import styles from './TestCasePanel.module.css';

/**
 * TestCasePanel — shows per-test-case input/expected/actual results.
 * Appears directly beneath the VerdictBanner, in the results screen order.
 */
export default function TestCasePanel({ testResults }) {
  if (!testResults || testResults.length === 0) return null;

  return (
    <div className={styles.panel}>
      <h3 className={styles.title}>Test Cases</h3>
      <div className={styles.cases}>
        {testResults.map((tc, idx) => {
          const isSqlCase = (tc.input && (tc.input.includes('CREATE TABLE') || tc.input.includes('INSERT INTO'))) ||
                            (typeof tc.actual === 'string' && tc.actual.includes('"type": "sql_table"')) ||
                            (typeof tc.expected === 'string' && tc.expected.includes('"type": "sql_table"'));

          if (isSqlCase) {
            return (
              <div key={tc.test_case_id || idx} style={{ marginBottom: '16px' }}>
                <SqlTableOutput
                  testCaseInput={tc.input}
                  userOutput={tc.actual}
                  expectedOutput={tc.expected}
                  passed={tc.passed}
                />
              </div>
            );
          }

          return (
            <div key={tc.test_case_id || idx} className={styles.case} data-passed={tc.passed}>
              <div className={styles.caseHeader}>
                <span className={styles.caseNum}>Case {idx + 1}</span>
                <span className={styles.caseBadge} data-passed={tc.passed}>
                  {tc.passed ? 'Passed' : 'Failed'}
                </span>
              </div>
              <div className={styles.grid}>
                <div>
                  <div className={styles.label}>Input</div>
                  <pre className={styles.code}>{tc.input}</pre>
                </div>
                <div>
                  <div className={styles.label}>Expected</div>
                  <pre className={styles.code}>{tc.expected}</pre>
                </div>
                <div>
                  <div className={styles.label}>Output</div>
                  <pre className={styles.code} data-wrong={!tc.passed}>{tc.actual || '(empty)'}</pre>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
