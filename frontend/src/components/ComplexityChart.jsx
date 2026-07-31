import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';
import styles from './ComplexityChart.module.css';

/**
 * ComplexityChart — the product's signature visual.
 *
 * Shows the learner's measured runtime curve vs. the theoretical reference curve
 * on shared log-log axes. This is the key differentiator from a standard judge.
 *
 * Log-log axes: if the growth is polynomial (O(n^k)), the line is straight with
 * slope k. This makes complexity class visually obvious.
 */
export default function ComplexityChart({ benchmarkCurve, empiricalClass, optimalClass }) {
  if (!benchmarkCurve || benchmarkCurve.length === 0) return null;

  const usable = benchmarkCurve.filter(p => !p.timed_out && p.runtime_ms > 0);
  if (usable.length === 0) return null;

  // Build log-log data for the user's curve
  const userPoints = usable.map(p => ({
    x: Math.log10(p.input_size),
    y: Math.log10(p.runtime_ms),
    n: p.input_size,
    ms: p.runtime_ms.toFixed(2),
  }));

  // Generate a smooth reference curve for the optimal complexity
  const refPoints = generateRefCurve(optimalClass, usable);

  const hasGap = empiricalClass && optimalClass && empiricalClass !== optimalClass;

  return (
    <div className={styles.wrapper}>
      <div className={styles.header}>
        <h3 className={styles.title}>Complexity Comparison</h3>
        <div className={styles.legend}>
          <span className={styles.dot} style={{ background: '#f97316' }} />
          <span>Your solution ({empiricalClass || '…'})</span>
          {optimalClass && (
            <>
              <span className={styles.dot} style={{ background: '#22c55e' }} />
              <span>Optimal ({optimalClass})</span>
            </>
          )}
        </div>
      </div>
      <div className={styles.axisNote}>
        Log-log scale — a straight line indicates a power-law growth O(n<sup>k</sup>),
        slope = k.
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis
            dataKey="x"
            type="number"
            name="log₁₀(n)"
            label={{ value: 'log₁₀(input size)', position: 'insideBottom', offset: -10, fill: '#8b90a8', fontSize: 12 }}
            tick={{ fill: '#8b90a8', fontSize: 11 }}
            domain={['auto', 'auto']}
          />
          <YAxis
            dataKey="y"
            type="number"
            name="log₁₀(ms)"
            label={{ value: 'log₁₀(ms)', angle: -90, position: 'insideLeft', fill: '#8b90a8', fontSize: 12 }}
            tick={{ fill: '#8b90a8', fontSize: 11 }}
            domain={['auto', 'auto']}
          />
          <Tooltip content={<CustomTooltip />} />
          {refPoints.length > 0 && (
            <Scatter
              name={`Optimal (${optimalClass})`}
              data={refPoints}
              fill="#22c55e"
              opacity={0.6}
              line={{ stroke: '#22c55e', strokeWidth: 2, strokeDasharray: '4 2' }}
              shape="circle"
              r={3}
            />
          )}
          <Scatter
            name={`Your solution (${empiricalClass})`}
            data={userPoints}
            fill="#f97316"
            line={{ stroke: '#f97316', strokeWidth: 2 }}
            shape="circle"
            r={4}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  return (
    <div style={{
      background: 'var(--surface-2)',
      border: '1px solid var(--border)',
      borderRadius: 8,
      padding: '0.6rem 0.9rem',
      fontSize: '0.82rem',
      fontFamily: 'var(--font-mono)',
    }}>
      {d.n && <div>n = {d.n.toLocaleString()}</div>}
      {d.ms && <div>time = {d.ms} ms</div>}
      <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginTop: 4 }}>
        ({Number(d.x).toFixed(2)}, {Number(d.y).toFixed(2)}) log-log
      </div>
    </div>
  );
}

/**
 * Generate reference curve points for the optimal complexity class,
 * scaled to roughly match the user's data range.
 */
function generateRefCurve(complexityClass, usable) {
  if (!complexityClass || usable.length < 2) return [];

  const ns = usable.map(p => p.input_size);
  const minN = Math.min(...ns);
  const maxN = Math.max(...ns);
  const ref = usable[0];
  // Scale factor: anchor the reference to the smallest data point
  const anchor_n = ref.input_size;
  const anchor_t = ref.runtime_ms;

  const fn = complexityFn(complexityClass);
  const scale = anchor_t / fn(anchor_n);

  const points = [];
  const steps = 20;
  for (let i = 0; i <= steps; i++) {
    const n = minN * Math.pow(maxN / minN, i / steps);
    const t = scale * fn(n);
    if (t > 0) {
      points.push({ x: Math.log10(n), y: Math.log10(t) });
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
