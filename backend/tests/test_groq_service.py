import pytest
from unittest.mock import AsyncMock, patch
from app.services.groq_service import generate_groq_insights


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_generate_groq_insights_missing_key():
    with pytest.raises(ValueError, match="Groq API Key is not configured"):
        await generate_groq_insights(
            user_code="print('hello')",
            optimal_code="print('hello')",
            problem_title="Two Sum",
            problem_description="Find two numbers that add up to target.",
            empirical_complexity="O(N)",
            optimal_complexity="O(N)",
            api_key_override="",
        )


@pytest.mark.anyio
async def test_generate_groq_insights_success():
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [
            {
                "message": {
                    "content": """{
                        "summary": "Great O(N) hashmap approach versus nested O(N^2) scan.",
                        "algorithmic_paradigm": {
                            "user_approach": "Brute Force Nested Loops",
                            "optimal_approach": "Single Pass Hash Table",
                            "paradigm_comparison": "Trading O(N) space for O(N) speedup."
                        },
                        "key_insights": [
                            {
                                "category": "Data Structure",
                                "title": "Inner Search",
                                "observation": "Linear scan on each element",
                                "impact": "Critical",
                                "recommendation": "Use HashMap for O(1) lookups"
                            }
                        ],
                        "complexity_deep_dive": {
                            "time_complexity": {
                                "user_empirical": "O(N^2)",
                                "user_best_case": "O(1)",
                                "user_worst_case": "O(N^2)",
                                "user_derivation": "Nested loops execute N*(N-1)/2 operations.",
                                "optimal_target": "O(N)",
                                "optimal_derivation": "Single pass with O(1) hash map operations."
                            },
                            "space_complexity": {
                                "user_space": "O(1) auxiliary",
                                "optimal_space": "O(N) auxiliary",
                                "tradeoff_analysis": "O(N) auxiliary memory stores complement values."
                            },
                            "scaling_simulation": {
                                "small_input_ops": "10^4 vs 10^2",
                                "medium_input_ops": "10^8 vs 10^4",
                                "large_input_ops": "10^12 vs 10^6",
                                "asymptotic_verdict": "Quadratic growth triggers TLE at N=10^5."
                            }
                        },
                        "bottlenecks": [
                            {
                                "construct": "for (int j = i + 1; j < n; j++)",
                                "type": "Nested Linear Scan",
                                "severity": "Critical",
                                "explanation": "Performs redundant inner scans."
                            }
                        ],
                        "refactoring_roadmap": [
                            {
                                "step_number": 1,
                                "title": "Introduce HashMap",
                                "action": "Store complements in map",
                                "code_snippet": "Map<Integer, Integer> map = new HashMap<>();",
                                "expected_gain": "Reduces inner scan to O(1)"
                            }
                        ],
                        "pro_tips": [
                            "Pre-size HashMap with new HashMap<>(n * 4 / 3) to prevent rehash."
                        ]
                    }"""
                }
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await generate_groq_insights(
            user_code="def twoSum(): pass",
            optimal_code="def twoSum(): pass",
            problem_title="Two Sum",
            problem_description="Find target pair.",
            empirical_complexity="O(N^2)",
            optimal_complexity="O(N)",
            optimal_space_complexity="O(N)",
            language="java",
            difficulty="easy",
            api_key_override="gsk_mock_key_12345",
        )

        assert "Great O(N)" in result["summary"]
        assert result["algorithmic_paradigm"]["user_approach"] == "Brute Force Nested Loops"
        assert len(result["key_insights"]) == 1
        assert result["key_insights"][0]["impact"] == "Critical"
        assert result["complexity_deep_dive"]["time_complexity"]["user_empirical"] == "O(N^2)"
        assert len(result["bottlenecks"]) == 1
        assert len(result["refactoring_roadmap"]) == 1
        assert len(result["pro_tips"]) == 1
        assert result["model_used"] == "openai/gpt-oss-120b"


@pytest.mark.anyio
async def test_generate_groq_insights_legacy_fallback_format():
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [
            {
                "message": {
                    "content": '{"summary": "Legacy string array format.", "key_insights": ["Simple insight string."], "refactoring_suggestions": ["Simple refactor step."], "complexity_analysis": "O(N^2) explanation."}'
                }
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await generate_groq_insights(
            user_code="def twoSum(): pass",
            optimal_code="def twoSum(): pass",
            problem_title="Two Sum",
            problem_description="Find target pair.",
            empirical_complexity="O(N)",
            optimal_complexity="O(N)",
            api_key_override="gsk_mock_key_12345",
        )

        assert result["summary"] == "Legacy string array format."
        assert len(result["key_insights"]) == 1
        assert result["key_insights"][0]["observation"] == "Simple insight string."
        assert len(result["refactoring_roadmap"]) == 1
        assert result["refactoring_roadmap"][0]["action"] == "Simple refactor step."


@pytest.mark.anyio
async def test_generate_groq_insights_dual_complexity_analysis():
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = lambda: {
        "choices": [
            {
                "message": {
                    "content": """{
                        "summary": "Dual AI complexity evaluation comparing quadratic user scan to linear hash table.",
                        "user_solution_analysis": {
                            "time_complexity": "O(N^2)",
                            "best_case_time": "O(1)",
                            "worst_case_time": "O(N^2)",
                            "average_case_time": "O(N^2)",
                            "space_complexity": "O(1) auxiliary",
                            "mathematical_derivation": "Sum of (N-i-1) from i=0 to N-1 = N*(N-1)/2 iterations.",
                            "dominating_operations": "Nested for-loops scanning array indices."
                        },
                        "optimal_solution_analysis": {
                            "time_complexity": "O(N)",
                            "best_case_time": "O(1)",
                            "worst_case_time": "O(N)",
                            "average_case_time": "O(N)",
                            "space_complexity": "O(N) auxiliary",
                            "mathematical_derivation": "Single pass of N elements with amortized O(1) hash map operations.",
                            "theoretical_lower_bound": "Must inspect at least N elements to find complement pairs."
                        },
                        "comparative_complexity": {
                            "is_gap": true,
                            "gap_summary": "1-degree polynomial gap: O(N^2) vs O(N)",
                            "speedup_factor": "O(N) speedup factor (~1000x at N=1000)",
                            "space_time_tradeoff": "Trading O(N) memory for quadratic time reduction.",
                            "scaling_simulation": {
                                "small_input_ops": "User ~5,000 ops vs Optimal ~100 ops",
                                "medium_input_ops": "User ~5x10^7 ops vs Optimal ~10^4 ops",
                                "large_input_ops": "User ~5x10^11 ops (TLE) vs Optimal ~10^6 ops",
                                "asymptotic_verdict": "User code times out for N >= 20,000."
                            }
                        },
                        "algorithmic_paradigm": {
                            "user_approach": "Brute Force",
                            "optimal_approach": "Hash Map"
                        },
                        "key_insights": [],
                        "bottlenecks": [],
                        "refactoring_roadmap": [],
                        "pro_tips": []
                    }"""
                }
            }
        ]
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        result = await generate_groq_insights(
            user_code="for i in range(n): for j in range(i+1, n): ...",
            optimal_code="seen = {}; for i, num in enumerate(nums): ...",
            problem_title="Two Sum",
            problem_description="Find target indices.",
            empirical_complexity="O(N^2)",
            optimal_complexity="O(N)",
            optimal_space_complexity="O(N)",
            language="python",
            difficulty="easy",
            api_key_override="gsk_mock_key_12345",
        )

        assert result["user_solution_analysis"]["time_complexity"] == "O(N^2)"
        assert result["user_solution_analysis"]["worst_case_time"] == "O(N^2)"
        assert "N*(N-1)/2" in result["user_solution_analysis"]["mathematical_derivation"]

        assert result["optimal_solution_analysis"]["time_complexity"] == "O(N)"
        assert "Single pass" in result["optimal_solution_analysis"]["mathematical_derivation"]
        assert "Must inspect" in result["optimal_solution_analysis"]["theoretical_lower_bound"]

        assert result["comparative_complexity"]["is_gap"] is True
        assert "1-degree polynomial gap" in result["comparative_complexity"]["gap_summary"]
        assert result["complexity_deep_dive"]["time_complexity"]["user_empirical"] == "O(N^2)"
        assert result["complexity_deep_dive"]["time_complexity"]["optimal_target"] == "O(N)"


