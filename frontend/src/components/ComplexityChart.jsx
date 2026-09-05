import { useState } from 'react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  Cell,
  Legend,
} from 'recharts';
import styles from './ComplexityChart.module.css';

const BIG_O_CLASSES = [
  { name: 'O(1)', rank: 1, label: 'Constant O(1)' },
  { name: 'O(log n)', rank: 2, label: 'Logarithmic O(log n)' },
  { name: 'O(n)', rank: 3, label: 'Linear O(n)' },
  { name: 'O(n log n)', rank: 4, label: 'Linearithmic O(n log n)' },
  { name: 'O(n^2)', rank: 5, label: 'Quadratic O(n²)' },
  { name: 'O(n^3)', rank: 6, label: 'Cubic O(n³)' },
  { name: 'O(2^n)', rank: 7, label: 'Exponential O(2ⁿ)' },
];

export default function ComplexityChart({ benchmarkCurve, empiricalClass, optimalClass }) {
  const [activeTab, setActiveTab] = useState('growth'); // 'growth' | 'hierarchy' | 'runtime'
  const [scaleMode, setScaleMode] = useState('log'); // 'log' | 'linear'

  if (!benchmarkCurve || benchmarkCurve.length === 0) return null;

  const usable = benchmarkCurve.filter(p => !p.timed_out && p.runtime_ms > 0);
  if (usable.length === 0) return null;

  // 1. Data for Growth Curve
  const logPoints = usable.map(p => ({
    x: Math.log10(p.input_size),
    y: Math.log10(p.runtime_ms),
    n: p.input_size,
    ms: p.runtime_ms.toFixed(2),
  }));

  const linearPoints = usable.map(p => ({
    x: p.input_size,
    y: p.runtime_ms,
    n: p.input_size,
    ms: p.runtime_ms.toFixed(2),
  }));

  const userPoints = scaleMode === 'log' ? logPoints : linearPoints;
  const refPoints = scaleMode === 'log' 
    ? generateRefCurve(optimalClass, usable)
    : generateLinearRefCurve(optimalClass, usable);

  // 2. Data for Hierarchy Bar Chart
  const hierarchyData = BIG_O_CLASSES.map(cls => {
    const isUser = empiricalClass && (cls.name === empiricalClass || isClassMatch(cls.name, empiricalClass));
    const isOpt = optimalClass && (cls.name === optimalClass || isClassMatch(cls.name, optimalClass));
    return {
      name: cls.name,
      label: cls.label,
      rank: cls.rank,
      isUser,
      isOpt,
      fill: isUser && isOpt ? '#3b82f6' : isUser ? '#f97316' : isOpt ? '#22c55e' : '#3c3c3c',
    };
  });

  // 3. Data for Runtime Distribution
  const runtimeData = usable.map(p => ({
    inputSize: `n=${p.input_size.toLocaleString()}`,
    n: p.input_size,
    runtime: Number(p.runtime_ms.toFixed(2)),
  }));

  return (
    <div className={styles.wrapper}>
      <div className={styles.topBar}>
        <div>
          <h3 className={styles.title}>Visual Complexity Analysis</h3>
          <p className={styles.subtitle}>
            Empirical runtime performance profiling & asymptotic scaling metrics
          </p>
        </div>

        {/* Tab Controls */}
        <div className={styles.tabGroup}>
          <button
            className={`${styles.tabBtn} ${activeTab === 'growth' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('growth')}
          >
            Growth Scaling Curve
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === 'hierarchy' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('hierarchy')}
          >
            Hierarchy Comparison
          </button>
          <button
            className={`${styles.tabBtn} ${activeTab === 'runtime' ? styles.tabActive : ''}`}
            onClick={() => setActiveTab('runtime')}
          >
            Runtime Breakdown
          </button>
        </div>
      </div>

      {/* ── TAB 1: Growth Curve ────────────────────────────────────────── */}
      {activeTab === 'growth' && (
        <div>
          <div className={styles.subHeader}>
            <div className={styles.legend}>
              <span className={styles.dot} style={{ background: '#f97316' }} />
              <span>Your solution ({empiricalClass || 'Measured'})</span>
              {optimalClass && (
                <>
                  <span className={styles.dot} style={{ background: '#22c55e' }} />
                  <span>Optimal Target ({optimalClass})</span>
                </>
              )}
            </div>

            <div className={styles.scaleSwitch}>
              <button
                className={`${styles.scaleBtn} ${scaleMode === 'log' ? styles.scaleActive : ''}`}
                onClick={() => setScaleMode('log')}
              >
                Log-Log Scale
              </button>
              <button
                className={`${styles.scaleBtn} ${scaleMode === 'linear' ? styles.scaleActive : ''}`}
                onClick={() => setScaleMode('linear')}
              >
                Linear Scale
              </button>
            </div>
          </div>

          <div className={styles.axisNote}>
            {scaleMode === 'log' ? (
              <span>
                <strong>Log-Log Scale:</strong> In log-log space, polynomial growth O(n<sup>k</sup>) manifests as a straight line with slope = k.
              </span>
            ) : (
              <span>
                <strong>Linear Scale:</strong> Shows absolute execution time in milliseconds as test input size n scales up.
              </span>
            )}
          </div>

          <ResponsiveContainer width="100%" height={320}>
            <ScatterChart margin={{ top: 15, right: 20, bottom: 25, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis
                dataKey="x"
                type="number"
                name={scaleMode === 'log' ? 'log₁₀(n)' : 'n'}
                label={{
                  value: scaleMode === 'log' ? 'log₁₀(input size n)' : 'Input Size (n)',
                  position: 'insideBottom',
                  offset: -12,
                  fill: '#8b90a8',
                  fontSize: 12,
                }}
                tick={{ fill: '#8b90a8', fontSize: 11 }}
                domain={['auto', 'auto']}
              />
              <YAxis
                dataKey="y"
                type="number"
                name={scaleMode === 'log' ? 'log₁₀(ms)' : 'ms'}
                label={{
                  value: scaleMode === 'log' ? 'log₁₀(runtime ms)' : 'Runtime (ms)',
                  angle: -90,
                  position: 'insideLeft',
                  fill: '#8b90a8',
                  fontSize: 12,
                }}
                tick={{ fill: '#8b90a8', fontSize: 11 }}
                domain={['auto', 'auto']}
              />
              <Tooltip content={<CustomTooltip scaleMode={scaleMode} />} />
              {refPoints.length > 0 && (
                <Scatter
                  name={`Optimal (${optimalClass})`}
                  data={refPoints}
                  fill="#22c55e"
                  opacity={0.65}
                  line={{ stroke: '#22c55e', strokeWidth: 2, strokeDasharray: '4 2' }}
                  shape="circle"
                  r={3}
                />
              )}
              <Scatter
                name={`Your solution (${empiricalClass})`}
                data={userPoints}
                fill="#f97316"
                line={{ stroke: '#f97316', strokeWidth: 2.5 }}
                shape="circle"
                r={5}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* ── TAB 2: Complexity Hierarchy ────────────────────────────────── */}
      {activeTab === 'hierarchy' && (
        <div>
          <div className={styles.subHeader}>
            <div className={styles.legend}>
              <span className={styles.dot} style={{ background: '#f97316' }} />
              <span>Your Solution ({empiricalClass || 'N/A'})</span>
              <span className={styles.dot} style={{ background: '#22c55e', marginLeft: '0.5rem' }} />
              <span>Optimal Solution ({optimalClass || 'N/A'})</span>
            </div>
          </div>

          <div className={styles.axisNote}>
            Ranks complexity growth from fastest O(1) to slowest O(2ⁿ). Lower rank indicates superior scaling efficiency.
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={hierarchyData} margin={{ top: 20, right: 20, bottom: 25, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="name" tick={{ fill: '#eff1f6', fontSize: 12 }} />
              <YAxis
                label={{ value: 'Complexity Severity Rank', angle: -90, position: 'insideLeft', fill: '#8b90a8', fontSize: 11 }}
                tick={{ fill: '#8b90a8', fontSize: 11 }}
                domain={[0, 8]}
              />
              <Tooltip content={<HierarchyTooltip />} />
              <Bar dataKey="rank" radius={[4, 4, 0, 0]}>
                {hierarchyData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          <div className={styles.hierarchyFooter}>
            <div className={styles.hierarchyCard} style={{ borderColor: 'rgba(249, 115, 22, 0.4)' }}>
              <span className={styles.hLabel} style={{ color: '#f97316' }}>Your Solution</span>
              <span className={styles.hVal}>{empiricalClass || 'N/A'}</span>
            </div>
            <div className={styles.hierarchyCard} style={{ borderColor: 'rgba(34, 197, 94, 0.4)' }}>
              <span className={styles.hLabel} style={{ color: '#22c55e' }}>Optimal Solution</span>
              <span className={styles.hVal}>{optimalClass || 'N/A'}</span>
            </div>
          </div>
        </div>
      )}

      {/* ── TAB 3: Runtime Distribution ───────────────────────────────── */}
      {activeTab === 'runtime' && (
        <div>
          <div className={styles.axisNote}>
            Measured execution runtime in milliseconds across each benchmark test suite input size n.
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={runtimeData} margin={{ top: 20, right: 20, bottom: 25, left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="inputSize" tick={{ fill: '#eff1f6', fontSize: 12 }} />
              <YAxis
                label={{ value: 'Runtime (ms)', angle: -90, position: 'insideLeft', fill: '#8b90a8', fontSize: 12 }}
                tick={{ fill: '#8b90a8', fontSize: 11 }}
              />
              <Tooltip content={<RuntimeTooltip />} />
              <Bar dataKey="runtime" fill="#ffa116" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

function CustomTooltip({ active, payload, scaleMode }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div className={styles.tooltipBox}>
      {d.n && <div>n = {d.n.toLocaleString()}</div>}
      {d.ms && <div>time = {d.ms} ms</div>}
      {scaleMode === 'log' && (
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginTop: 4 }}>
          ({Number(d.x).toFixed(2)}, {Number(d.y).toFixed(2)}) log-log
        </div>
      )}
    </div>
  );
}

function HierarchyTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div className={styles.tooltipBox}>
      <div style={{ fontWeight: 'bold' }}>{d.label}</div>
      {d.isUser && <div style={{ color: '#f97316' }}>✓ Your Empirical Solution</div>}
      {d.isOpt && <div style={{ color: '#22c55e' }}>✓ Optimal Target Solution</div>}
    </div>
  );
}

function RuntimeTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div className={styles.tooltipBox}>
      <div>{d.inputSize}</div>
      <div style={{ color: '#ffa116', fontWeight: 'bold' }}>{d.runtime} ms</div>
    </div>
  );
}

function generateRefCurve(complexityClass, usable) {
  if (!complexityClass || usable.length < 2) return [];
  const ns = usable.map(p => p.input_size);
  const minN = Math.min(...ns);
  const maxN = Math.max(...ns);
  const ref = usable[0];
  const anchor_n = ref.input_size;
  const anchor_t = ref.runtime_ms;

  const fn = complexityFn(complexityClass);
  const scale = anchor_t / fn(anchor_n);

  const points = [];
  const steps = 25;
  for (let i = 0; i <= steps; i++) {
    const n = minN * Math.pow(maxN / minN, i / steps);
    const t = scale * fn(n);
    if (t > 0) {
      points.push({ x: Math.log10(n), y: Math.log10(t), n, ms: t.toFixed(2) });
    }
  }
  return points;
}

function generateLinearRefCurve(complexityClass, usable) {
  if (!complexityClass || usable.length < 2) return [];
  const ns = usable.map(p => p.input_size);
  const minN = Math.min(...ns);
  const maxN = Math.max(...ns);
  const ref = usable[0];
  const anchor_n = ref.input_size;
  const anchor_t = ref.runtime_ms;

  const fn = complexityFn(complexityClass);
  const scale = anchor_t / fn(anchor_n);

  const points = [];
  const steps = 25;
  for (let i = 0; i <= steps; i++) {
    const n = minN + ((maxN - minN) * i) / steps;
    const t = scale * fn(n);
    if (t >= 0) {
      points.push({ x: n, y: t, n, ms: t.toFixed(2) });
    }
  }
  return points;
}

function complexityFn(cls) {
  switch (cls) {
    case 'O(1)':       return () => 1;
    case 'O(log n)':   return n => Math.log2(n);
    case 'O(n)':       return n => n;
    case 'O(n log n)': return n => n * Math.log2(n);
    case 'O(n^2)':     return n => n * n;
    case 'O(n^3)':     return n => n * n * n;
    default:           return n => n;
  }
}

function isClassMatch(c1, c2) {
  if (!c1 || !c2) return false;
  return c1.replace(/\s+/g, '').toLowerCase() === c2.replace(/\s+/g, '').toLowerCase();
}
