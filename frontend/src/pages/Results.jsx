import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useLocation, useParams } from 'react-router-dom';
import api from '../api/client';
import VerdictBanner from '../components/VerdictBanner';
import TestCasePanel from '../components/TestCasePanel';
import ComplexityChart from '../components/ComplexityChart';
import HintCard from '../components/HintCard';
import styles from './Results.module.css';

const TERMINAL_STATES = new Set(['complete', 'failed']);
const POLL_INTERVAL_MS = 1500;

export default function Results() {
  const { id } = useParams();
  const location = useLocation();
  const optimalComplexity = location.state?.optimalComplexity;

  const [submission, setSubmission] = useState(null);
  const [problem, setProblem] = useState(null);
  const [error, setError] = useState('');
  const pollRef = useRef(null);

  const fetchSubmission = useCallback(async () => {
    try {
      const { data } = await api.get(`/submissions/${id}`);
      setSubmission(data);
      if (TERMINAL_STATES.has(data.status)) {
        clearInterval(pollRef.current);
        // Fetch problem for context
        if (data.problem_id) {
          api.get(`/problems/${data.problem_id}`).then(r => setProblem(r.data)).catch(() => {});
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load results');
      clearInterval(pollRef.current);
    }
  }, [id]);

  useEffect(() => {
    fetchSubmission();
    pollRef.current = setInterval(fetchSubmission, POLL_INTERVAL_MS);
    return () => clearInterval(pollRef.current);
  }, [fetchSubmission]);

  const isComplete = submission?.status === 'complete';
  const isFailed = submission?.status === 'failed';
  const isTerminal = isComplete || isFailed;

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <Link to="/problems" className={styles.back}>← Back to Problems</Link>
        {submission && problem && (
          <div className={styles.problemRef}>
            <Link to={`/problems/${problem.id}`} className={styles.problemLink}>
              {problem.title}
            </Link>
            <span className={`badge badge-${problem.difficulty}`}>{problem.difficulty}</span>
          </div>
        )}
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {/* ── 1. Verdict banner (always first, always prominent) ── */}
      <VerdictBanner
        status={isComplete ? 'complete' : (isFailed ? submission?.failure_detail?.split(' ')[0] : submission?.status)}
        empiricalComplexity={submission?.empirical_complexity}
        confidence={submission?.confidence_score}
        optimalComplexity={optimalComplexity || problem?.optimal_time_complexity}
      />

      {/* Failure detail card */}
      {isFailed && submission?.failure_detail && (
        <div className={styles.failureDetail}>
          <div className={styles.failureLabel}>Details</div>
          <pre className={styles.failurePre}>{submission.failure_detail}</pre>
        </div>
      )}

      {/* ── 2. Test case results panel ─────────────────────── */}
      {submission?.test_results && (
        <TestCasePanel testResults={submission.test_results} />
      )}

      {/* ── 3. Complexity comparison (Accepted only) ───────── */}
      {isComplete && submission?.benchmark_curve && (
        <ComplexityChart
          benchmarkCurve={submission.benchmark_curve}
          empiricalClass={submission.empirical_complexity}
          optimalClass={optimalComplexity || problem?.optimal_time_complexity}
        />
      )}

      {/* ── 4. Structural hint (gap only) ──────────────────── */}
      {isComplete && submission?.structural_hint && (
        <HintCard hint={submission.structural_hint} />
      )}

      {/* Action buttons */}
      {isTerminal && (
        <div className={styles.actions}>
          {problem && (
            <Link to={`/problems/${problem.id}`} className="btn btn-secondary">
              Try again
            </Link>
          )}
          <Link to="/problems" className="btn btn-primary">
            Browse problems
          </Link>
        </div>
      )}
    </div>
  );
}
