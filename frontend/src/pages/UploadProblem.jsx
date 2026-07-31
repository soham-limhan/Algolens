import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import styles from './UploadProblem.module.css';

const initialForm = {
  title: '',
  description: '',
  difficulty: 'Easy',
  optimal_time_complexity: 'O(n)',
  optimal_space_complexity: 'O(1)',
  examples: '',
  constraints: '',
};

export default function UploadProblem() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState(initialForm);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!formData.title.trim() || !formData.description.trim()) {
      setError('Please provide a problem title and description.');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Build test cases from examples if provided
      const testCases = [];
      if (formData.examples.trim()) {
        const parts = formData.examples.split(/Input:?/i).filter(Boolean);
        for (const p of parts) {
          const lines = p.split(/Output:?/i);
          if (lines.length >= 2) {
            testCases.push({
              input: lines[0].trim(),
              expected_output: lines[1].trim(),
            });
          }
        }
      }

      const fullDesc = [
        formData.description.trim(),
        formData.examples.trim() ? `\n\n### Examples\n${formData.examples.trim()}` : '',
        formData.constraints.trim() ? `\n\n### Constraints\n${formData.constraints.trim()}` : '',
      ].join('');

      const payload = {
        title: formData.title.trim(),
        description: fullDesc,
        difficulty: formData.difficulty.toLowerCase(),
        optimal_time_complexity: formData.optimal_time_complexity.trim() || 'O(n)',
        optimal_space_complexity: formData.optimal_space_complexity.trim() || 'O(1)',
        generator_key: 'two_sum',
        test_cases: testCases,
      };

      const res = await api.post('/problems', payload);
      navigate(`/problems/${res.data.id}`);
    } catch (err) {
      const msg = err.response?.data?.detail;
      setError(typeof msg === 'string' ? msg : 'Failed to publish problem. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <span className={styles.eyebrow}>CONTRIBUTOR WORKSPACE</span>
          <h1 className={styles.title}>Create New Problem</h1>
          <p className={styles.sub}>
            Add a problem to the AlgoLens catalog with title, description, constraints, and test cases.
          </p>
        </div>
        <button type="button" className={styles.backBtn} onClick={() => navigate('/problems')}>
          ← Back to problems
        </button>
      </div>

      <form className={styles.formCard} onSubmit={handleSubmit}>
        {error && <div className={styles.errorBanner}>{error}</div>}

        <div className={styles.rowGrid}>
          <div className={styles.fieldGroup}>
            <label htmlFor="title">Problem Title *</label>
            <input
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g. 3Sum Closest"
              required
            />
          </div>

          <div className={styles.fieldGroup}>
            <label htmlFor="difficulty">Difficulty *</label>
            <select id="difficulty" name="difficulty" value={formData.difficulty} onChange={handleChange}>
              <option value="Easy">Easy</option>
              <option value="Medium">Medium</option>
              <option value="Hard">Hard</option>
            </select>
          </div>
        </div>

        <div className={styles.rowGrid}>
          <div className={styles.fieldGroup}>
            <label htmlFor="optimal_time_complexity">Optimal Time Complexity</label>
            <input
              id="optimal_time_complexity"
              name="optimal_time_complexity"
              value={formData.optimal_time_complexity}
              onChange={handleChange}
              placeholder="O(n log n)"
            />
          </div>

          <div className={styles.fieldGroup}>
            <label htmlFor="optimal_space_complexity">Optimal Space Complexity</label>
            <input
              id="optimal_space_complexity"
              name="optimal_space_complexity"
              value={formData.optimal_space_complexity}
              onChange={handleChange}
              placeholder="O(1)"
            />
          </div>
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="description">Problem Statement *</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Given an integer array nums of length n..."
            rows={5}
            required
          />
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="examples">Examples & Test Cases</label>
          <textarea
            id="examples"
            name="examples"
            value={formData.examples}
            onChange={handleChange}
            placeholder="Input: nums = [-1,2,1,-4], target = 1&#10;Output: 2"
            rows={4}
          />
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="constraints">Constraints</label>
          <textarea
            id="constraints"
            name="constraints"
            value={formData.constraints}
            onChange={handleChange}
            placeholder="3 <= nums.length <= 500&#10;-1000 <= nums[i] <= 1000"
            rows={3}
          />
        </div>

        <div className={styles.actionsRow}>
          <button type="button" className={styles.cancelBtn} onClick={() => navigate('/problems')}>
            Cancel
          </button>
          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? <span className="spinner" /> : 'Publish Problem'}
          </button>
        </div>
      </form>
    </div>
  );
}