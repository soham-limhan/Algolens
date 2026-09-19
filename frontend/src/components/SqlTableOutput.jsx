import React, { useState, useMemo } from 'react';
import styles from './SqlTableOutput.module.css';

/**
 * Parses raw SQL setup statements (CREATE TABLE & INSERT INTO) into structured table objects.
 */
function parseSqlInputTables(rawInput) {
  if (!rawInput || typeof rawInput !== 'string') return [];
  const tables = [];
  
  // Split statements by semicolon
  const statements = rawInput.split(';').map(s => s.trim()).filter(Boolean);
  
  let currentTable = null;

  for (const stmt of statements) {
    const createMatch = stmt.match(/CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`"'\w]+)\s*\(([\s\S]+)\)/i);
    if (createMatch) {
      const tableName = createMatch[1].replace(/[`"']/g, '');
      const columnDefs = createMatch[2].split(',').map(c => c.trim()).filter(Boolean);
      const columns = [];
      
      for (const colDef of columnDefs) {
        if (/^(PRIMARY\s+KEY|FOREIGN\s+KEY|KEY|CONSTRAINT|UNIQUE)/i.test(colDef)) continue;
        const colParts = colDef.split(/\s+/);
        if (colParts.length > 0 && colParts[0]) {
          columns.push(colParts[0].replace(/[`"']/g, ''));
        }
      }
      
      currentTable = {
        name: tableName,
        columns: columns,
        rows: []
      };
      tables.push(currentTable);
      continue;
    }

    const insertMatch = stmt.match(/INSERT\s+INTO\s+([`"'\w]+)(?:\s*\(([^)]+)\))?\s+VALUES\s*([\s\S]+)/i);
    if (insertMatch) {
      const tableName = insertMatch[1].replace(/[`"']/g, '');
      let targetTable = tables.find(t => t.name.toLowerCase() === tableName.toLowerCase());
      if (!targetTable) {
        targetTable = { name: tableName, columns: [], rows: [] };
        tables.push(targetTable);
      }

      // Parse values tuples: (val1, val2), (val3, val4)
      const valuesStr = insertMatch[3];
      const tupleRegex = /\(([^)]+)\)/g;
      let tupleMatch;
      while ((tupleMatch = tupleRegex.exec(valuesStr)) !== null) {
        const rawValues = tupleMatch[1].split(',').map(v => {
          let val = v.trim();
          if (val.startsWith("'") && val.endsWith("'")) return val.slice(1, -1);
          if (val.startsWith('"') && val.endsWith('"')) return val.slice(1, -1);
          if (val.toUpperCase() === 'NULL') return null;
          if (!isNaN(val) && val !== '') return Number(val);
          return val;
        });
        targetTable.rows.push(rawValues);
      }
    }
  }

  return tables;
}

/**
 * Safely parses table data from string or JSON object.
 */
function parseTableData(data) {
  if (!data) return null;
  if (typeof data === 'object' && data.type === 'sql_table') {
    return data;
  }
  if (typeof data === 'string') {
    const trimmed = data.trim();
    if (trimmed.startsWith('{') && trimmed.endsWith('}')) {
      try {
        const parsed = JSON.parse(trimmed);
        if (parsed && (parsed.type === 'sql_table' || (parsed.columns && Array.isArray(parsed.rows)))) {
          return parsed;
        }
      } catch {
        // Not valid JSON table
      }
    }
  }
  return null;
}

export default function SqlTableOutput({
  testCaseInput = '',
  userOutput = '',
  expectedOutput = '',
  passed = false,
  runtimeMs = null,
  rawError = '',
  isEvaluating = false,
}) {
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'raw'
  const [layoutMode, setLayoutMode] = useState('side-by-side'); // 'side-by-side' | 'stacked'
  const [activeTab, setActiveTab] = useState('output'); // 'output' | 'input-tables'

  const inputTables = useMemo(() => parseSqlInputTables(testCaseInput), [testCaseInput]);
  const parsedUserOutput = useMemo(() => parseTableData(userOutput), [userOutput]);
  const parsedExpectedOutput = useMemo(() => parseTableData(expectedOutput), [expectedOutput]);

  const userColumns = parsedUserOutput?.columns || [];
  const userRows = parsedUserOutput?.rows || [];
  const expectedColumns = parsedExpectedOutput?.columns || [];
  const expectedRows = parsedExpectedOutput?.rows || [];

  return (
    <div className={styles.container}>
      {/* Header Bar */}
      <div className={styles.headerBar}>
        <div className={styles.headerLeft}>
          <div className={styles.tabs}>
            <button
              className={`${styles.tabBtn} ${activeTab === 'output' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('output')}
            >
              <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="18" rx="2" />
                <path d="M3 9h18M9 21V9" />
              </svg>
              Query Results
            </button>
            <button
              className={`${styles.tabBtn} ${activeTab === 'input-tables' ? styles.activeTab : ''}`}
              onClick={() => setActiveTab('input-tables')}
            >
              <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <ellipse cx="12" cy="5" rx="9" ry="3" />
                <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
                <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
              </svg>
              Input Tables ({inputTables.length})
            </button>
          </div>
        </div>

        <div className={styles.headerRight}>
          {runtimeMs !== null && runtimeMs !== undefined && (
            <span className={styles.statBadge}>
              <svg className={styles.statIcon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              {typeof runtimeMs === 'number' ? `${runtimeMs.toFixed(1)} ms` : runtimeMs}
            </span>
          )}

          {activeTab === 'output' && parsedUserOutput && (
            <>
              <div className={styles.buttonGroup}>
                <button
                  className={`${styles.toggleBtn} ${layoutMode === 'side-by-side' ? styles.activeToggle : ''}`}
                  onClick={() => setLayoutMode('side-by-side')}
                  title="Side-by-Side View"
                >
                  Side-by-Side
                </button>
                <button
                  className={`${styles.toggleBtn} ${layoutMode === 'stacked' ? styles.activeToggle : ''}`}
                  onClick={() => setLayoutMode('stacked')}
                  title="Stacked View"
                >
                  Stacked
                </button>
              </div>

              <div className={styles.buttonGroup}>
                <button
                  className={`${styles.toggleBtn} ${viewMode === 'grid' ? styles.activeToggle : ''}`}
                  onClick={() => setViewMode('grid')}
                >
                  Table Grid
                </button>
                <button
                  className={`${styles.toggleBtn} ${viewMode === 'raw' ? styles.activeToggle : ''}`}
                  onClick={() => setViewMode('raw')}
                >
                  Raw ASCII
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className={styles.contentArea}>
        {isEvaluating ? (
          <div className={styles.loadingState}>
            <div className={styles.spinner}></div>
            <p>Executing SQL query in sandbox...</p>
          </div>
        ) : activeTab === 'input-tables' ? (
          /* Input Tables Visualizer */
          <div className={styles.inputTablesGrid}>
            {inputTables.length === 0 ? (
              <div className={styles.emptyState}>No input schema or tables found for this test case.</div>
            ) : (
              inputTables.map((tbl, idx) => (
                <div key={idx} className={styles.tableCard}>
                  <div className={styles.tableCardHeader}>
                    <span className={styles.tableName}>
                      <span className={styles.tableIcon}>📋</span> {tbl.name}
                    </span>
                    <span className={styles.rowCountBadge}>{tbl.rows.length} rows</span>
                  </div>
                  <div className={styles.tableWrapper}>
                    <table className={styles.dataTable}>
                      <thead>
                        <tr>
                          {tbl.columns.map((col, cIdx) => (
                            <th key={cIdx}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {tbl.rows.length === 0 ? (
                          <tr>
                            <td colSpan={tbl.columns.length || 1} className={styles.emptyRow}>
                              (Empty Table)
                            </td>
                          </tr>
                        ) : (
                          tbl.rows.map((row, rIdx) => (
                            <tr key={rIdx}>
                              {row.map((cell, cIdx) => (
                                <td key={cIdx}>
                                  {cell === null || cell === undefined ? (
                                    <span className={styles.nullValue}>null</span>
                                  ) : (
                                    String(cell)
                                  )}
                                </td>
                              ))}
                            </tr>
                          ))
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          /* Output Comparison */
          <div>
            {rawError ? (
              <div className={styles.errorBanner}>
                <div className={styles.errorTitle}>
                  <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" fill="none" strokeWidth="2">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  SQL Execution Error
                </div>
                <pre className={styles.errorPre}>{rawError}</pre>
              </div>
            ) : null}

            {viewMode === 'raw' ? (
              <div className={styles.rawOutputContainer}>
                <div className={styles.rawColumn}>
                  <div className={styles.rawHeader}>Your Output (Raw)</div>
                  <pre className={styles.rawPre}>
                    {parsedUserOutput?.ascii_table || userOutput || '(No Output)'}
                  </pre>
                </div>
                <div className={styles.rawColumn}>
                  <div className={styles.rawHeader}>Expected Output (Raw)</div>
                  <pre className={styles.rawPre}>
                    {parsedExpectedOutput?.ascii_table || expectedOutput || '(No Expected Output)'}
                  </pre>
                </div>
              </div>
            ) : (
              <div
                className={`${styles.gridComparison} ${
                  layoutMode === 'stacked' ? styles.stackedLayout : styles.sideBySideLayout
                }`}
              >
                {/* User Output Table */}
                <div className={`${styles.tableCard} ${passed ? styles.passedCard : styles.failedCard}`}>
                  <div className={styles.tableCardHeader}>
                    <div className={styles.headerTitleGroup}>
                      <span className={styles.tableName}>Your Query Output</span>
                      <span className={`${styles.statusPill} ${passed ? styles.statusPassed : styles.statusFailed}`}>
                        {passed ? '✓ Matches Expected' : '✗ Output Mismatch'}
                      </span>
                    </div>
                    <span className={styles.rowCountBadge}>{userRows.length} rows</span>
                  </div>

                  <div className={styles.tableWrapper}>
                    {parsedUserOutput && userColumns.length > 0 ? (
                      <table className={styles.dataTable}>
                        <thead>
                          <tr>
                            {userColumns.map((col, idx) => (
                              <th key={idx}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {userRows.length === 0 ? (
                            <tr>
                              <td colSpan={userColumns.length} className={styles.emptyRow}>
                                (0 rows returned)
                              </td>
                            </tr>
                          ) : (
                            userRows.map((row, rIdx) => (
                              <tr key={rIdx}>
                                {row.map((cell, cIdx) => (
                                  <td key={cIdx}>
                                    {cell === null || cell === undefined ? (
                                      <span className={styles.nullValue}>null</span>
                                    ) : (
                                      String(cell)
                                    )}
                                  </td>
                                ))}
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    ) : (
                      <div className={styles.emptyOutputMessage}>
                        {userOutput ? <pre className={styles.rawPre}>{userOutput}</pre> : 'Run query to see output'}
                      </div>
                    )}
                  </div>
                </div>

                {/* Expected Output Table */}
                <div className={`${styles.tableCard} ${styles.expectedCard}`}>
                  <div className={styles.tableCardHeader}>
                    <span className={styles.tableName}>Expected Output</span>
                    <span className={styles.rowCountBadge}>{expectedRows.length} rows</span>
                  </div>

                  <div className={styles.tableWrapper}>
                    {parsedExpectedOutput && expectedColumns.length > 0 ? (
                      <table className={styles.dataTable}>
                        <thead>
                          <tr>
                            {expectedColumns.map((col, idx) => (
                              <th key={idx}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {expectedRows.length === 0 ? (
                            <tr>
                              <td colSpan={expectedColumns.length} className={styles.emptyRow}>
                                (0 rows expected)
                              </td>
                            </tr>
                          ) : (
                            expectedRows.map((row, rIdx) => (
                              <tr key={rIdx}>
                                {row.map((cell, cIdx) => (
                                  <td key={cIdx}>
                                    {cell === null || cell === undefined ? (
                                      <span className={styles.nullValue}>null</span>
                                    ) : (
                                      String(cell)
                                    )}
                                  </td>
                                ))}
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    ) : (
                      <div className={styles.emptyOutputMessage}>
                        {expectedOutput ? (
                          <pre className={styles.rawPre}>{expectedOutput}</pre>
                        ) : (
                          'No expected output data'
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
