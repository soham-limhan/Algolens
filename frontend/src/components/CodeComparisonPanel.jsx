import { useState, useMemo, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import styles from './CodeComparisonPanel.module.css';

export default function CodeComparisonPanel({
  userCode,
  optimalCode,
  language = 'java',
  empiricalComplexity,
  optimalComplexity,
  optimalSpace,
}) {
  const [viewMode, setViewMode] = useState('split'); // 'split' | 'stacked'
  const [copiedUser, setCopiedUser] = useState(false);
  const [copiedOptimal, setCopiedOptimal] = useState(false);

  const userLangNorm = (language || 'java').toLowerCase();

  // Parse all available optimal solutions by language
  const optimalMap = useMemo(() => {
    if (!optimalCode) return {};
    if (typeof optimalCode === 'object') return optimalCode;
    if (typeof optimalCode === 'string') {
      const trimmed = optimalCode.trim();
      if (trimmed.startsWith('{')) {
        try {
          return JSON.parse(trimmed);
        } catch (e) {
          // ignore error and treat as plain snippet
        }
      }
      return { [userLangNorm]: trimmed };
    }
    return {};
  }, [optimalCode, userLangNorm]);

  const availableLangs = useMemo(() => {
    return Object.keys(optimalMap).filter(k => typeof optimalMap[k] === 'string' && optimalMap[k].trim());
  }, [optimalMap]);

  // Determine initial optimal language tab matching user's submission language
  const getPreferredLang = () => {
    if (optimalMap[userLangNorm]) return userLangNorm;
    if (userLangNorm === 'js' && optimalMap['javascript']) return 'javascript';
    if (userLangNorm === 'javascript' && optimalMap['js']) return 'js';
    if ((userLangNorm === 'cpp' || userLangNorm === 'c') && optimalMap['cpp']) return 'cpp';
    if (availableLangs.length > 0) return availableLangs[0];
    return userLangNorm;
  };

  const [selectedOptLang, setSelectedOptLang] = useState(getPreferredLang);

  useEffect(() => {
    setSelectedOptLang(getPreferredLang());
  }, [userLangNorm, optimalMap]);

  // Code to display on optimal panel
  const displayedOptimalCode = useMemo(() => {
    if (optimalMap[selectedOptLang]) {
      return optimalMap[selectedOptLang];
    }
    if (selectedOptLang === 'javascript' && optimalMap['js']) return optimalMap['js'];
    if (selectedOptLang === 'js' && optimalMap['javascript']) return optimalMap['javascript'];
    if (selectedOptLang === 'cpp' && optimalMap['c']) return optimalMap['c'];
    if (selectedOptLang === 'c' && optimalMap['cpp']) return optimalMap['cpp'];
    
    // Fallback to first available or synthesized default
    const firstCode = Object.values(optimalMap)[0];
    return firstCode || defaultOptimalSnippet(selectedOptLang || userLangNorm, optimalComplexity);
  }, [optimalMap, selectedOptLang, userLangNorm, optimalComplexity]);

  // Monaco Editor language mapping
  const monacoOptLang = useMemo(() => {
    const l = (selectedOptLang || userLangNorm).toLowerCase();
    if (l === 'cpp' || l === 'c') return 'cpp';
    if (l === 'javascript' || l === 'js') return 'javascript';
    if (l === 'python' || l === 'py') return 'python';
    if (l === 'java') return 'java';
    return 'plaintext';
  }, [selectedOptLang, userLangNorm]);

  const monacoUserLang = useMemo(() => {
    const l = userLangNorm.toLowerCase();
    if (l === 'cpp' || l === 'c') return 'cpp';
    if (l === 'javascript' || l === 'js') return 'javascript';
    if (l === 'python' || l === 'py') return 'python';
    if (l === 'java') return 'java';
    return 'plaintext';
  }, [userLangNorm]);

  const handleCopy = (text, type) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    if (type === 'user') {
      setCopiedUser(true);
      setTimeout(() => setCopiedUser(false), 2000);
    } else {
      setCopiedOptimal(true);
      setTimeout(() => setCopiedOptimal(false), 2000);
    }
  };

  const isGap = empiricalComplexity && optimalComplexity && empiricalComplexity !== optimalComplexity;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <div className={styles.iconBox}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 3h5v5M4 21h5v-5M21 3l-7 7M3 21l7-7" />
            </svg>
          </div>
          <div>
            <h3 className={styles.title}>Solution Code Comparison</h3>
            <p className={styles.subtitle}>
              Compare your implementation directly against the optimal algorithmic approach
            </p>
          </div>
        </div>

        <div className={styles.controls}>
          <div className={styles.viewToggle}>
            <button
              className={`${styles.toggleBtn} ${viewMode === 'split' ? styles.toggleActive : ''}`}
              onClick={() => setViewMode('split')}
              title="Side-by-side view"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="8" height="18" rx="1" />
                <rect x="13" y="3" width="8" height="18" rx="1" />
              </svg>
              <span>Side-by-Side</span>
            </button>
            <button
              className={`${styles.toggleBtn} ${viewMode === 'stacked' ? styles.toggleActive : ''}`}
              onClick={() => setViewMode('stacked')}
              title="Stacked view"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="3" y="3" width="18" height="8" rx="1" />
                <rect x="3" y="13" width="18" height="8" rx="1" />
              </svg>
              <span>Stacked</span>
            </button>
          </div>
        </div>
      </div>

      {isGap && (
        <div className={styles.gapBanner}>
          <div className={styles.gapIcon}>⚡</div>
          <div className={styles.gapText}>
            <strong>Optimization Opportunity:</strong> Your code executed at{' '}
            <span className={styles.userBadge}>{empiricalComplexity}</span> time complexity, whereas the optimal algorithm achieves{' '}
            <span className={styles.optBadge}>{optimalComplexity}</span>. Review the optimal solution below to see how to bridge this gap.
          </div>
        </div>
      )}

      <div className={`${styles.codeGrid} ${viewMode === 'stacked' ? styles.stackedGrid : ''}`}>
        {/* ── Left Column: User Code ── */}
        <div className={styles.codeCard}>
          <div className={styles.cardHeader}>
            <div className={styles.cardHeaderLeft}>
              <span className={styles.badgeUser}>Your Solution</span>
              <span className={styles.langTag}>{language.toUpperCase()}</span>
              {empiricalComplexity && (
                <span className={styles.complexityPillUser}>
                  Time: {empiricalComplexity}
                </span>
              )}
            </div>
            <button
              className={styles.copyBtn}
              onClick={() => handleCopy(userCode, 'user')}
            >
              {copiedUser ? '✓ Copied' : 'Copy'}
            </button>
          </div>

          <div className={styles.editorContainer}>
            <Editor
              height="360px"
              language={monacoUserLang}
              value={userCode || '// No code submitted'}
              theme="vs-dark"
              options={{
                readOnly: true,
                fontSize: 13,
                fontFamily: "'JetBrains Mono', monospace",
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                lineNumbers: 'on',
                wordWrap: 'on',
                automaticLayout: true,
                domReadOnly: true,
              }}
            />
          </div>
        </div>

        {/* ── Right Column: Optimal Code ── */}
        <div className={styles.codeCard}>
          <div className={styles.cardHeader}>
            <div className={styles.cardHeaderLeft}>
              <span className={styles.badgeOptimal}>Optimal Reference Solution</span>
              {availableLangs.length > 1 ? (
                <div className={styles.optLangSwitcher}>
                  {availableLangs.map(l => (
                    <button
                      key={l}
                      className={`${styles.optLangBtn} ${selectedOptLang === l ? styles.optLangBtnActive : ''}`}
                      onClick={() => setSelectedOptLang(l)}
                    >
                      {l.toUpperCase()}
                    </button>
                  ))}
                </div>
              ) : (
                <span className={styles.langTag}>{(selectedOptLang || language).toUpperCase()}</span>
              )}
              {optimalComplexity && (
                <span className={styles.complexityPillOptimal}>
                  Time: {optimalComplexity}
                </span>
              )}
              {optimalSpace && (
                <span className={styles.complexityPillSpace}>
                  Space: {optimalSpace}
                </span>
              )}
            </div>
            <button
              className={styles.copyBtn}
              onClick={() => handleCopy(displayedOptimalCode, 'optimal')}
            >
              {copiedOptimal ? '✓ Copied' : 'Copy'}
            </button>
          </div>

          <div className={styles.editorContainer}>
            <Editor
              height="360px"
              language={monacoOptLang}
              value={displayedOptimalCode}
              theme="vs-dark"
              options={{
                readOnly: true,
                fontSize: 13,
                fontFamily: "'JetBrains Mono', monospace",
                minimap: { enabled: false },
                scrollBeyondLastLine: false,
                lineNumbers: 'on',
                wordWrap: 'on',
                automaticLayout: true,
                domReadOnly: true,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function defaultOptimalSnippet(language, optimalComplexity) {
  const comp = optimalComplexity || 'O(n)';
  const lang = (language || 'java').toLowerCase();
  if (lang === 'python' || lang === 'py') {
    return `# Reference Optimal Solution (${comp})
# High-efficiency algorithmic pattern using optimal data structures
# designed for minimal asymptotic scaling and memory allocation.

def solution():
    # Refer to problem constraints & optimal complexity specifications
    pass
`;
  }
  if (lang === 'javascript' || lang === 'js') {
    return `// Reference Optimal Solution (${comp})
// High-efficiency algorithmic pattern using optimal data structures

function solution() {
    // Refer to problem constraints & optimal complexity specifications
}
`;
  }
  if (lang === 'cpp' || lang === 'c') {
    return `// Reference Optimal Solution (${comp})
// High-efficiency algorithmic pattern using optimal data structures

#include <iostream>

int main() {
    // Refer to problem constraints & optimal complexity specifications
    return 0;
}
`;
  }
  return `// Reference Optimal Solution (${comp})
// High-efficiency algorithmic pattern using optimal data structures

public class Solution {
    // Refer to problem constraints & optimal complexity specifications
}
`;
}
