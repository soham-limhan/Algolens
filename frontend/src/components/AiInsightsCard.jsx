import { useState } from 'react';
import api from '../api/client';
import styles from './AiInsightsCard.module.css';

export default function AiInsightsCard({ submissionId, userCode, optimalCode, empiricalComplexity, optimalComplexity }) {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('summary'); // 'summary' | 'bottlenecks' | 'refactoring' | 'protips'
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError('');

    try {
      const { data } = await api.post(`/submissions/${submissionId}/ai-insights`);
      setInsights(data);
    } catch (err) {
      const msg = err.response?.data?.detail || err.message || 'Failed to generate AI insights';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const userAnalysis = insights?.user_solution_analysis || {};
  const optAnalysis = insights?.optimal_solution_analysis || {};
  const compAnalysis = insights?.comparative_complexity || {};
  const timeComp = insights?.complexity_deep_dive?.time_complexity || {};
  const spaceComp = insights?.complexity_deep_dive?.space_complexity || {};
  const scaleSim = compAnalysis?.scaling_simulation || insights?.complexity_deep_dive?.scaling_simulation || {};
  const paradigm = insights?.algorithmic_paradigm || {};
  const keyInsights = insights?.key_insights || [];
  const bottlenecks = insights?.bottlenecks || [];
  const roadmap = insights?.refactoring_roadmap || [];
  const proTips = insights?.pro_tips || [];

  const userTimeDisplay = userAnalysis.time_complexity || timeComp.user_empirical || empiricalComplexity || 'O(N)';
  const optTimeDisplay = optAnalysis.time_complexity || timeComp.optimal_target || optimalComplexity || 'O(N)';
  const isGap = compAnalysis.is_gap !== undefined 
    ? compAnalysis.is_gap 
    : (userTimeDisplay !== optTimeDisplay);

  const handleCopyInsights = () => {
    if (!insights) return;

    const text = `# 🧠 ALGOLENS AI TIME COMPLEXITY & COMPARATIVE ANALYSIS REPORT
Powered by Groq AI (${insights.model_used || 'Groq LLM Engine'})

---

## 1. Executive Summary & Algorithmic Paradigm
${insights.summary || 'N/A'}

- **User Approach:** ${paradigm.user_approach || 'N/A'}
- **Optimal Target:** ${paradigm.optimal_approach || 'N/A'}
${paradigm.paradigm_comparison ? `\n**Paradigm Shift:** ${paradigm.paradigm_comparison}` : ''}

---

## 2. AI Time Complexity Evaluation & Side-by-Side Comparison

### Your Solution (AI Evaluated):
- **Time Complexity:** ${userTimeDisplay} (Worst: ${userAnalysis.worst_case_time || timeComp.user_worst_case || userTimeDisplay}, Best: ${userAnalysis.best_case_time || 'O(1)'}, Average: ${userAnalysis.average_case_time || userTimeDisplay})
- **Auxiliary Space:** ${userAnalysis.space_complexity || spaceComp.user_space || 'O(1)'}
${userAnalysis.mathematical_derivation || timeComp.user_derivation ? `\n**Mathematical Derivation:**\n${userAnalysis.mathematical_derivation || timeComp.user_derivation}` : ''}
${userAnalysis.dominating_operations ? `\n**Dominating Operations:** ${userAnalysis.dominating_operations}` : ''}

### Optimal Reference Solution (AI Evaluated):
- **Time Complexity:** ${optTimeDisplay} (Worst: ${optAnalysis.worst_case_time || optTimeDisplay}, Best: ${optAnalysis.best_case_time || optTimeDisplay})
- **Auxiliary Space:** ${optAnalysis.space_complexity || spaceComp.optimal_space || 'O(1)'}
${optAnalysis.mathematical_derivation || timeComp.optimal_derivation ? `\n**Optimal Mathematical Proof:**\n${optAnalysis.mathematical_derivation || timeComp.optimal_derivation}` : ''}
${optAnalysis.theoretical_lower_bound ? `\n**Theoretical Lower Bound:** ${optAnalysis.theoretical_lower_bound}` : ''}

### Comparative Assessment:
- **Status:** ${isGap ? '⚡ Asymptotic Complexity Gap Detected' : '✓ Optimal Complexity Matched'}
${compAnalysis.gap_summary ? `- **Gap Summary:** ${compAnalysis.gap_summary}` : ''}
${compAnalysis.speedup_factor ? `- **Expected Speedup:** ${compAnalysis.speedup_factor}` : ''}
${compAnalysis.space_time_tradeoff || spaceComp.tradeoff_analysis ? `- **Space-Time Tradeoff:** ${compAnalysis.space_time_tradeoff || spaceComp.tradeoff_analysis}` : ''}

---

## 3. Scaling Simulation
- Small Input (N = 10^2): ${scaleSim.small_input_ops || 'Fast'}
- Medium Input (N = 10^4): ${scaleSim.medium_input_ops || 'Warning'}
- Large Input (N = 10^6): ${scaleSim.large_input_ops || 'TLE'}
${scaleSim.asymptotic_verdict ? `\n**Verdict:** ${scaleSim.asymptotic_verdict}` : ''}

---

## 4. Key Observations
${keyInsights.length > 0 
  ? keyInsights.map(i => {
      if (typeof i === 'object') {
        return `### [${i.impact || 'Note'}] ${i.title || i.category || 'Observation'}
- **Observation:** ${i.observation || ''}
${i.recommendation ? `- **Recommendation:** ${i.recommendation}` : ''}`;
      }
      return `• ${i}`;
    }).join('\n\n')
  : 'No specific observations recorded.'}

---

## 5. Code Bottlenecks
${bottlenecks.length > 0
  ? bottlenecks.map(b => `### ⚠️ ${b.type || 'Bottleneck'} (${b.severity || 'High'})
- **Construct:** \`${b.construct || 'N/A'}\`
- **Explanation:** ${b.explanation || ''}`).join('\n\n')
  : 'No critical bottlenecks detected.'}

---

## 6. Step-by-Step Refactoring Roadmap
${roadmap.length > 0
  ? roadmap.map((step, idx) => `### Step ${step.step_number || idx + 1}: ${step.title || 'Optimization'}
- **Action:** ${step.action || ''}
${step.code_snippet ? `\`\`\`\n${step.code_snippet}\n\`\`\`` : ''}
${step.expected_gain ? `- **Expected Gain:** ${step.expected_gain}` : ''}`).join('\n\n')
  : (insights.refactoring_suggestions || []).map(r => `• ${r}`).join('\n')}

---

## 7. Language & Pro-Level Optimizations
${proTips.length > 0
  ? proTips.map(p => `• ${p}`).join('\n')
  : 'Standard optimizations apply.'}
`;

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getImpactBadgeClass = (impact) => {
    const imp = String(impact || '').toLowerCase();
    if (imp.includes('crit')) return styles.impactCritical;
    if (imp.includes('high')) return styles.impactHigh;
    if (imp.includes('mod')) return styles.impactModerate;
    return styles.impactInfo;
  };

  const getSeverityBadgeClass = (severity) => {
    const sev = String(severity || '').toLowerCase();
    if (sev.includes('crit')) return styles.severityCritical;
    if (sev.includes('high')) return styles.severityHigh;
    return styles.severityModerate;
  };

  return (
    <div className={styles.card}>
      {/* ── Header ────────────────────────────────────────────── */}
      <div className={styles.header}>
        <div className={styles.titleGroup}>
          <div className={styles.aiBadge}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z" />
              <path d="M12 6v6l4 2" />
            </svg>
            <span>GROQ DUAL AI PROFILER</span>
          </div>
          <div>
            <h3 className={styles.title}>AI Time Complexity & Asymptotic Profiler</h3>
            <p className={styles.subtitle}>
              AI evaluation of your code vs. optimal reference solution • Mathematical derivations & proofs
            </p>
          </div>
        </div>

        <div className={styles.headerActions}>
          {!insights && !loading && (
            <button className={styles.generateBtn} onClick={handleGenerate}>
              <span>⚡ Check Complexity with AI</span>
            </button>
          )}
        </div>
      </div>

      {error && <div className={styles.errorBox}>{error}</div>}

      {/* ── Loading State ────────────────────────────────────── */}
      {loading && (
        <div className={styles.loadingBox}>
          <div className={styles.pulseSpinner} />
          <div>
            <h4 className={styles.loadingTitle}>Evaluating Time Complexity with AI...</h4>
            <p className={styles.loadingSub}>
              Analyzing loop hierarchies, deriving mathematical bounds for both user and optimal solutions, and computing asymptotic scaling
            </p>
          </div>
        </div>
      )}

      {/* ── Main Insights View ───────────────────────────────── */}
      {insights && !loading && (
        <div className={styles.contentBody}>
          {/* Dual AI Complexity Comparison Hero Banner */}
          <div className={styles.dualComplexityHero}>
            <div className={styles.heroUserCard}>
              <div className={styles.heroCardBadge}>YOUR SOLUTION (AI ANALYZED)</div>
              <div className={styles.heroBigComplexity}>{userTimeDisplay}</div>
              <div className={styles.heroDetailsGrid}>
                <div><span>Worst Case:</span> <strong>{userAnalysis.worst_case_time || timeComp.user_worst_case || userTimeDisplay}</strong></div>
                <div><span>Best Case:</span> <strong>{userAnalysis.best_case_time || timeComp.user_best_case || 'O(1)'}</strong></div>
                <div><span>Aux Space:</span> <strong>{userAnalysis.space_complexity || spaceComp.user_space || 'O(1)'}</strong></div>
              </div>
            </div>

            <div className={styles.heroGapCenter}>
              <div className={isGap ? styles.gapStatusPillWarn : styles.gapStatusPillSuccess}>
                {isGap ? '⚡ COMPLEXITY GAP' : '✓ OPTIMAL MATCH'}
              </div>
              <div className={styles.gapExplanationText}>
                {compAnalysis.gap_summary || (isGap ? `User ${userTimeDisplay} vs Optimal ${optTimeDisplay}` : `Both match ${optTimeDisplay}`)}
              </div>
              {compAnalysis.speedup_factor && (
                <div className={styles.speedupPill}>{compAnalysis.speedup_factor}</div>
              )}
            </div>

            <div className={styles.heroOptCard}>
              <div className={styles.heroCardBadgeOpt}>OPTIMAL REFERENCE (AI ANALYZED)</div>
              <div className={styles.heroBigComplexityOpt}>{optTimeDisplay}</div>
              <div className={styles.heroDetailsGrid}>
                <div><span>Worst Case:</span> <strong>{optAnalysis.worst_case_time || optTimeDisplay}</strong></div>
                <div><span>Best Case:</span> <strong>{optAnalysis.best_case_time || optTimeDisplay}</strong></div>
                <div><span>Aux Space:</span> <strong>{optAnalysis.space_complexity || spaceComp.optimal_space || 'O(1)'}</strong></div>
              </div>
            </div>
          </div>

          <div className={styles.topBar}>
            <div className={styles.tabGroup}>
              <button
                className={`${styles.tabBtn} ${activeTab === 'summary' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('summary')}
              >
                💡 Summary & Paradigm
              </button>
              <button
                className={`${styles.tabBtn} ${activeTab === 'bottlenecks' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('bottlenecks')}
              >
                ⚡ Derivations & Bottlenecks
                {bottlenecks.length > 0 && <span className={styles.tabCount}>{bottlenecks.length}</span>}
              </button>
              <button
                className={`${styles.tabBtn} ${activeTab === 'refactoring' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('refactoring')}
              >
                🛠️ Refactoring Roadmap
                {roadmap.length > 0 && <span className={styles.tabCount}>{roadmap.length}</span>}
              </button>
              <button
                className={`${styles.tabBtn} ${activeTab === 'protips' ? styles.tabActive : ''}`}
                onClick={() => setActiveTab('protips')}
              >
                🚀 Pro Optimizations
                {proTips.length > 0 && <span className={styles.tabCount}>{proTips.length}</span>}
              </button>
            </div>

            <div className={styles.rightActions}>
              <button className={styles.copyBtn} onClick={handleCopyInsights}>
                {copied ? '✓ Copied Full Report' : '📋 Copy Report'}
              </button>
              <button className={styles.regenBtn} onClick={handleGenerate}>
                🔄 Re-analyze
              </button>
            </div>
          </div>

          {/* Tab 1: Summary & Paradigm */}
          {activeTab === 'summary' && (
            <div className={styles.tabPanel}>
              {/* Paradigm Comparison Card */}
              <div className={styles.paradigmCard}>
                <div className={styles.paradigmHeader}>
                  <span className={styles.paradigmIcon}>🧭</span>
                  <h4 className={styles.paradigmTitle}>Algorithmic Paradigm Shift</h4>
                </div>
                <div className={styles.paradigmFlow}>
                  <div className={styles.paradigmBoxUser}>
                    <span className={styles.paradigmRole}>Your Approach</span>
                    <span className={styles.paradigmName}>{paradigm.user_approach || 'User Approach'}</span>
                  </div>
                  <div className={styles.paradigmArrow}>➔</div>
                  <div className={styles.paradigmBoxOpt}>
                    <span className={styles.paradigmRole}>Optimal Target</span>
                    <span className={styles.paradigmName}>{paradigm.optimal_approach || 'Optimal Approach'}</span>
                  </div>
                </div>
                {paradigm.paradigm_comparison && (
                  <p className={styles.paradigmDesc}>{paradigm.paradigm_comparison}</p>
                )}
              </div>

              {/* Executive Summary */}
              <div className={styles.summaryCallout}>
                <span className={styles.calloutIcon}>💬</span>
                <div>
                  <div className={styles.calloutTitle}>Executive Analysis</div>
                  <p className={styles.summaryText}>{insights.summary}</p>
                </div>
              </div>

              {/* Categorized Key Observations */}
              <div className={styles.sectionHeader}>Detailed Key Observations</div>
              <div className={styles.insightsGrid}>
                {keyInsights.map((item, idx) => {
                  const isObj = typeof item === 'object';
                  const title = isObj ? item.title || item.category : `Observation #${idx + 1}`;
                  const category = isObj ? item.category : 'General';
                  const impact = isObj ? item.impact : 'High';
                  const obs = isObj ? item.observation : item;
                  const rec = isObj ? item.recommendation : null;

                  return (
                    <div key={idx} className={styles.insightCard}>
                      <div className={styles.insightCardHeader}>
                        <div className={styles.categoryTag}>{category}</div>
                        <span className={`${styles.impactBadge} ${getImpactBadgeClass(impact)}`}>
                          {impact} Impact
                        </span>
                      </div>
                      <h5 className={styles.insightCardTitle}>{title}</h5>
                      <p className={styles.insightCardText}>{obs}</p>
                      {rec && (
                        <div className={styles.recBox}>
                          <span className={styles.recIcon}>💡</span>
                          <span className={styles.recText}><strong>Action:</strong> {rec}</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tab 2: Derivations & Bottlenecks */}
          {activeTab === 'bottlenecks' && (
            <div className={styles.tabPanel}>
              {/* Mathematical Loop & Asymptotic Derivation */}
              <div className={styles.sectionHeader}>Mathematical Derivations & Proofs</div>
              <div className={styles.derivationCard}>
                <div className={styles.derivationRow}>
                  <div className={styles.derivationCol}>
                    <div className={styles.derivationBadgeUser}>YOUR SOLUTION DERIVATION</div>
                    <h5 className={styles.derivationColTitle}>Loop Counters & Asymptotic Recurrence</h5>
                    <p className={styles.derivationText}>
                      {userAnalysis.mathematical_derivation || timeComp.user_derivation || insights.complexity_analysis || 'Mathematical loop analysis completed.'}
                    </p>
                    {userAnalysis.dominating_operations && (
                      <div className={styles.dominatingOpsBox}>
                        <strong>Dominating Operations:</strong> {userAnalysis.dominating_operations}
                      </div>
                    )}
                  </div>
                  <div className={styles.derivationCol}>
                    <div className={styles.derivationBadgeOpt}>OPTIMAL SOLUTION PROOF</div>
                    <h5 className={styles.derivationColTitle}>Theoretical Lower Bound & Proof</h5>
                    <p className={styles.derivationText}>
                      {optAnalysis.mathematical_derivation || timeComp.optimal_derivation || 'Optimal approach eliminates redundant iterations through direct algorithmic transformations.'}
                    </p>
                    {optAnalysis.theoretical_lower_bound && (
                      <div className={styles.lowerBoundBox}>
                        <strong>Lower Bound Justification:</strong> {optAnalysis.theoretical_lower_bound}
                      </div>
                    )}
                  </div>
                </div>
                {(compAnalysis.space_time_tradeoff || spaceComp.tradeoff_analysis) && (
                  <div className={styles.tradeoffBox}>
                    <strong>Space-Time Tradeoff:</strong> {compAnalysis.space_time_tradeoff || spaceComp.tradeoff_analysis}
                  </div>
                )}
              </div>

              {/* Asymptotic Scaling Simulation */}
              {(scaleSim.small_input_ops || scaleSim.medium_input_ops || scaleSim.large_input_ops) && (
                <div className={styles.scaleContainer}>
                  <div className={styles.sectionHeader}>Asymptotic Scaling Simulation (Projected Operations)</div>
                  <div className={styles.scaleGrid}>
                    <div className={styles.scaleCard}>
                      <div className={styles.scaleCardSize}>Small (N = 10²)</div>
                      <div className={styles.scaleCardOps}>{scaleSim.small_input_ops || 'Negligible diff'}</div>
                    </div>
                    <div className={styles.scaleCard}>
                      <div className={styles.scaleCardSize}>Medium (N = 10⁴)</div>
                      <div className={styles.scaleCardOps}>{scaleSim.medium_input_ops || 'Measurable lag'}</div>
                    </div>
                    <div className={styles.scaleCard}>
                      <div className={styles.scaleCardSize}>Large (N = 10⁶)</div>
                      <div className={styles.scaleCardOps}>{scaleSim.large_input_ops || 'Time Limit Exceeded'}</div>
                    </div>
                  </div>
                  {scaleSim.asymptotic_verdict && (
                    <div className={styles.verdictCallout}>
                      <span className={styles.verdictIcon}>⚠️</span>
                      <span><strong>Asymptotic Verdict:</strong> {scaleSim.asymptotic_verdict}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Identified Code Bottlenecks */}
              <div className={styles.sectionHeader} style={{ marginTop: '1.5rem' }}>
                Identified Code Construct Bottlenecks
              </div>
              {bottlenecks.length > 0 ? (
                <div className={styles.bottleneckList}>
                  {bottlenecks.map((item, idx) => (
                    <div key={idx} className={styles.bottleneckCard}>
                      <div className={styles.bottleneckTop}>
                        <code className={styles.constructCode}>{item.construct}</code>
                        <span className={`${styles.severityBadge} ${getSeverityBadgeClass(item.severity)}`}>
                          {item.severity} Severity
                        </span>
                      </div>
                      <div className={styles.bottleneckType}>{item.type}</div>
                      <p className={styles.bottleneckDesc}>{item.explanation}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className={styles.emptyState}>No severe structural bottlenecks detected in submission.</div>
              )}
            </div>
          )}

          {/* Tab 3: Refactoring Roadmap */}
          {activeTab === 'refactoring' && (
            <div className={styles.tabPanel}>
              <div className={styles.sectionHeader}>Step-by-Step Optimization Roadmap</div>
              <div className={styles.roadmapList}>
                {roadmap.map((step, idx) => (
                  <div key={idx} className={styles.roadmapCard}>
                    <div className={styles.roadmapStepHeader}>
                      <div className={styles.stepCircle}>{step.step_number || idx + 1}</div>
                      <div className={styles.stepTitleGroup}>
                        <h5 className={styles.stepTitle}>{step.title}</h5>
                        {step.expected_gain && (
                          <span className={styles.gainBadge}>⚡ {step.expected_gain}</span>
                        )}
                      </div>
                    </div>
                    <p className={styles.stepAction}>{step.action}</p>
                    {step.code_snippet && (
                      <div className={styles.codeSnippetBox}>
                        <div className={styles.snippetLabel}>Recommended Idiom</div>
                        <pre className={styles.snippetPre}>
                          <code>{step.code_snippet}</code>
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tab 4: Pro Optimizations */}
          {activeTab === 'protips' && (
            <div className={styles.tabPanel}>
              <div className={styles.sectionHeader}>Engine, Compiler & Language-Level Pro Tips</div>
              <div className={styles.proTipsGrid}>
                {proTips.map((tip, idx) => (
                  <div key={idx} className={styles.proTipCard}>
                    <span className={styles.proTipIcon}>💎</span>
                    <p className={styles.proTipText}>{tip}</p>
                  </div>
                ))}
                {proTips.length === 0 && (
                  <div className={styles.emptyState}>No language-specific micro-optimizations needed.</div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

