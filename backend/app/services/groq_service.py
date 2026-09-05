"""
app/services/groq_service.py — Service for generating algorithmic insights using Groq AI.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


async def generate_groq_insights(
    user_code: str,
    optimal_code: Optional[str],
    problem_title: str,
    problem_description: str,
    empirical_complexity: str,
    optimal_complexity: str,
    optimal_space_complexity: Optional[str] = None,
    language: Optional[str] = "java",
    difficulty: Optional[str] = "medium",
    api_key_override: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Query Groq LLM to generate deep, multi-dimensional comparative algorithmic insights
    between user solution and optimal solution.
    """
    groq_key = api_key_override if api_key_override is not None else settings.groq_api_key
    if not groq_key or not groq_key.strip():
        raise ValueError(
            "Groq API Key is not configured. Please set GROQ_API_KEY in backend/.env or provide a key in the request."
        )

    preferred_model = settings.groq_model or "openai/gpt-oss-120b"
    candidate_models = [
        preferred_model,
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "gpt-oss-120b",
        "gpt-oss-20b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
    ]
    # Deduplicate candidate models while keeping order
    models_to_try = []
    for m in candidate_models:
        if m and m not in models_to_try:
            models_to_try.append(m)

    system_prompt = (
        "You are a world-class algorithm designer, computer science educator, and software performance engineer. "
        "Conduct an exhaustive, highly detailed comparative and asymptotic analysis between the user's submitted code and the reference optimal solution. "
        "You MUST independently and rigorously evaluate:\n"
        "1. The user's code time complexity (worst, best, average cases) and provide a step-by-step mathematical derivation.\n"
        "2. The optimal reference solution's code time complexity (worst, best, average cases) and provide a step-by-step mathematical proof of its theoretical lower bound.\n"
        "3. A detailed comparative complexity analysis contrasting the two approaches.\n\n"
        "Your output MUST be a strict JSON object with NO markdown wrapping around the JSON, matching this schema exactly:\n"
        "{\n"
        '  "summary": "Detailed 2-3 sentence executive overview explaining the fundamental differences in algorithmic strategy, paradigm, and efficiency.",\n'
        '  "user_solution_analysis": {\n'
        '    "time_complexity": "e.g., O(N^2)",\n'
        '    "best_case_time": "e.g., O(1) or O(N)",\n'
        '    "worst_case_time": "e.g., O(N^2)",\n'
        '    "average_case_time": "e.g., O(N^2)",\n'
        '    "space_complexity": "e.g., O(1) auxiliary",\n'
        '    "mathematical_derivation": "Step-by-step mathematical derivation analyzing loop bounds, nested iterations, or recursion (e.g., Sum from i=0 to N-1 of (N-i-1) = N(N-1)/2 operations).",\n'
        '    "dominating_operations": "Description of the exact lines or constructs dominating runtime."\n'
        '  },\n'
        '  "optimal_solution_analysis": {\n'
        '    "time_complexity": "e.g., O(N)",\n'
        '    "best_case_time": "e.g., O(1) or O(N)",\n'
        '    "worst_case_time": "e.g., O(N)",\n'
        '    "average_case_time": "e.g., O(N)",\n'
        '    "space_complexity": "e.g., O(N) auxiliary",\n'
        '    "mathematical_derivation": "Rigorous mathematical explanation of why the optimal reference code achieves this complexity (e.g. single pass over array with O(1) amortized hash lookups).",\n'
        '    "theoretical_lower_bound": "Why this represents the theoretical lower bound for this problem."\n'
        '  },\n'
        '  "comparative_complexity": {\n'
        '    "is_gap": true,\n'
        '    "gap_summary": "Clear statement comparing user vs optimal complexity (e.g. 1-degree polynomial gap).",\n'
        '    "speedup_factor": "Theoretical scaling speedup (e.g. O(N) speedup factor).",\n'
        '    "space_time_tradeoff": "Detailed explanation of space-time tradeoffs between both solutions.",\n'
        '    "scaling_simulation": {\n'
        '      "small_input_ops": "Approx operations count at N=10^2 for user vs optimal (e.g. User ~5,000 ops vs Optimal ~100 ops)",\n'
        '      "medium_input_ops": "Approx operations count at N=10^4 for user vs optimal (e.g. User ~5x10^7 ops vs Optimal ~10^4 ops)",\n'
        '      "large_input_ops": "Approx operations count at N=10^6 for user vs optimal (e.g. User ~5x10^11 ops [TLE] vs Optimal ~10^6 ops [<50ms])",\n'
        '      "asymptotic_verdict": "Clear conclusion on where the user solution will TLE in practice."\n'
        '    }\n'
        '  },\n'
        '  "algorithmic_paradigm": {\n'
        '    "user_approach": "e.g., Brute Force / Nested Scan",\n'
        '    "optimal_approach": "e.g., Hash Map Indexing / Two Pointers / Dynamic Programming",\n'
        '    "paradigm_comparison": "In-depth explanation of how shifting paradigms unlocks optimal performance."\n'
        '  },\n'
        '  "key_insights": [\n'
        '    {\n'
        '      "category": "Data Structure | Loop Hierarchy | Memory Footprint | Branching & Pruning",\n'
        '      "title": "Short descriptive title",\n'
        '      "observation": "What the user code specifically does",\n'
        '      "impact": "Critical | High | Moderate | Informational",\n'
        '      "recommendation": "Actionable insight to improve this aspect"\n'
        '    }\n'
        '  ],\n'
        '  "bottlenecks": [\n'
        '    {\n'
        '      "construct": "Specific line or loop construct in user code",\n'
        '      "type": "Nested Linear Scan | Redundant Computation | Memory Allocation in Loop | Lack of Early Exit",\n'
        '      "severity": "Critical | High | Moderate",\n'
        '      "explanation": "Why this construct causes an empirical performance bottleneck."\n'
        '    }\n'
        '  ],\n'
        '  "refactoring_roadmap": [\n'
        '    {\n'
        '      "step_number": 1,\n'
        '      "title": "Refactoring step title",\n'
        '      "action": "Concrete instructions on how to rewrite the code",\n'
        '      "code_snippet": "Compact code example illustrating the optimal idiom",\n'
        '      "expected_gain": "Quantified algorithmic gain (e.g. reduces inner scan from O(N) to O(1))"\n'
        '    }\n'
        '  ],\n'
        '  "pro_tips": [\n'
        '    "Specific language-level or systems optimization tip tailored to the language."\n'
        '  ]\n'
        '}'
    )

    user_prompt = f"""
Language: {language}
Problem: {problem_title} (Difficulty: {difficulty})
Empirical Benchmark Measured for User Code: {empirical_complexity}
Theoretical Optimal Target: {optimal_complexity}
Theoretical Space Target: {optimal_space_complexity or "O(1) to O(N)"}

Problem Description:
{problem_description[:1200]}

User Submitted Solution ({language}):
```{language}
{user_code}
```

Optimal Reference Solution:
```{language}
{optimal_code or "Not provided"}
```

Please analyze the user's code time complexity, analyze the optimal solution's time complexity, and produce the comprehensive comparative analysis according to the specified JSON schema.
"""

    headers = {
        "Authorization": f"Bearer {groq_key.strip()}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=35.0) as client:
        last_error = ""
        for model in models_to_try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.2,
                "max_tokens": 3000,
                "response_format": {"type": "json_object"},
            }

            try:
                response = await client.post(GROQ_API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    raw_content = result["choices"][0]["message"]["content"]
                    parsed_data = json.loads(raw_content)

                    # Sanitization helpers
                    def clean_str(val, default=""):
                        if val is None:
                            return default
                        return str(val).strip()

                    def clean_list(items):
                        if not isinstance(items, list):
                            if isinstance(items, str) and items.strip():
                                items = [items]
                            else:
                                items = []
                        cleaned = []
                        for item in items:
                            if isinstance(item, dict):
                                cleaned.append(item)
                            else:
                                s = str(item).strip()
                                if not s or s in {"]", "[", ":", "summary", "refactoring_suggestions", "complexity_analysis"}:
                                    continue
                                if s.startswith("- ") or s.startswith("* ") or s.startswith("• "):
                                    s = s[2:].strip()
                                cleaned.append(s)
                        return cleaned

                    # 1. Parse User Solution Analysis
                    raw_user_analysis = parsed_data.get("user_solution_analysis", {})
                    if not isinstance(raw_user_analysis, dict):
                        raw_user_analysis = {}
                    user_analysis = {
                        "time_complexity": clean_str(raw_user_analysis.get("time_complexity"), empirical_complexity or "O(N)"),
                        "best_case_time": clean_str(raw_user_analysis.get("best_case_time"), "O(1)"),
                        "worst_case_time": clean_str(raw_user_analysis.get("worst_case_time"), empirical_complexity or "O(N)"),
                        "average_case_time": clean_str(raw_user_analysis.get("average_case_time"), empirical_complexity or "O(N)"),
                        "space_complexity": clean_str(raw_user_analysis.get("space_complexity"), "O(1) auxiliary"),
                        "mathematical_derivation": clean_str(raw_user_analysis.get("mathematical_derivation"), ""),
                        "dominating_operations": clean_str(raw_user_analysis.get("dominating_operations"), ""),
                    }

                    # 2. Parse Optimal Solution Analysis
                    raw_opt_analysis = parsed_data.get("optimal_solution_analysis", {})
                    if not isinstance(raw_opt_analysis, dict):
                        raw_opt_analysis = {}
                    optimal_analysis = {
                        "time_complexity": clean_str(raw_opt_analysis.get("time_complexity"), optimal_complexity or "O(N)"),
                        "best_case_time": clean_str(raw_opt_analysis.get("best_case_time"), optimal_complexity or "O(N)"),
                        "worst_case_time": clean_str(raw_opt_analysis.get("worst_case_time"), optimal_complexity or "O(N)"),
                        "average_case_time": clean_str(raw_opt_analysis.get("average_case_time"), optimal_complexity or "O(N)"),
                        "space_complexity": clean_str(raw_opt_analysis.get("space_complexity"), optimal_space_complexity or "O(1) auxiliary"),
                        "mathematical_derivation": clean_str(raw_opt_analysis.get("mathematical_derivation"), ""),
                        "theoretical_lower_bound": clean_str(raw_opt_analysis.get("theoretical_lower_bound"), ""),
                    }

                    # 3. Parse Comparative Complexity
                    raw_comp_analysis = parsed_data.get("comparative_complexity", {})
                    if not isinstance(raw_comp_analysis, dict):
                        raw_comp_analysis = {}

                    raw_scale = raw_comp_analysis.get("scaling_simulation", {})
                    if not isinstance(raw_scale, dict):
                        raw_scale = parsed_data.get("complexity_deep_dive", {}).get("scaling_simulation", {})
                        if not isinstance(raw_scale, dict):
                            raw_scale = {}

                    comparative_complexity = {
                        "is_gap": bool(raw_comp_analysis.get("is_gap", user_analysis["time_complexity"] != optimal_analysis["time_complexity"])),
                        "gap_summary": clean_str(raw_comp_analysis.get("gap_summary"), ""),
                        "speedup_factor": clean_str(raw_comp_analysis.get("speedup_factor"), ""),
                        "space_time_tradeoff": clean_str(raw_comp_analysis.get("space_time_tradeoff"), ""),
                        "scaling_simulation": {
                            "small_input_ops": clean_str(raw_scale.get("small_input_ops"), ""),
                            "medium_input_ops": clean_str(raw_scale.get("medium_input_ops"), ""),
                            "large_input_ops": clean_str(raw_scale.get("large_input_ops"), ""),
                            "asymptotic_verdict": clean_str(raw_scale.get("asymptotic_verdict"), ""),
                        },
                    }

                    # 4. Parse Algorithmic Paradigm
                    raw_paradigm = parsed_data.get("algorithmic_paradigm", {})
                    if not isinstance(raw_paradigm, dict):
                        raw_paradigm = {}
                    paradigm = {
                        "user_approach": clean_str(raw_paradigm.get("user_approach"), "User Implementation"),
                        "optimal_approach": clean_str(raw_paradigm.get("optimal_approach"), "Optimal Algorithmic Approach"),
                        "paradigm_comparison": clean_str(raw_paradigm.get("paradigm_comparison"), ""),
                    }

                    # 5. Parse key_insights
                    raw_insights = parsed_data.get("key_insights", [])
                    key_insights = []
                    if isinstance(raw_insights, list):
                        for item in raw_insights:
                            if isinstance(item, dict):
                                key_insights.append({
                                    "category": clean_str(item.get("category"), "General"),
                                    "title": clean_str(item.get("title"), "Algorithmic Pattern"),
                                    "observation": clean_str(item.get("observation") or item.get("description"), ""),
                                    "impact": clean_str(item.get("impact"), "High"),
                                    "recommendation": clean_str(item.get("recommendation"), ""),
                                })
                            elif isinstance(item, str) and item.strip():
                                s = item.strip()
                                if s.startswith("- ") or s.startswith("* ") or s.startswith("• "):
                                    s = s[2:].strip()
                                key_insights.append({
                                    "category": "Algorithmic Observation",
                                    "title": "Code Pattern",
                                    "observation": s,
                                    "impact": "High",
                                    "recommendation": "",
                                })

                    # 6. Backward Compatibility for complexity_deep_dive
                    complexity_deep_dive = {
                        "time_complexity": {
                            "user_empirical": user_analysis["time_complexity"],
                            "user_best_case": user_analysis["best_case_time"],
                            "user_worst_case": user_analysis["worst_case_time"],
                            "user_derivation": user_analysis["mathematical_derivation"],
                            "optimal_target": optimal_analysis["time_complexity"],
                            "optimal_derivation": optimal_analysis["mathematical_derivation"],
                        },
                        "space_complexity": {
                            "user_space": user_analysis["space_complexity"],
                            "optimal_space": optimal_analysis["space_complexity"],
                            "tradeoff_analysis": comparative_complexity["space_time_tradeoff"],
                        },
                        "scaling_simulation": comparative_complexity["scaling_simulation"],
                    }

                    # 7. Parse bottlenecks
                    raw_bottlenecks = parsed_data.get("bottlenecks", [])
                    bottlenecks = []
                    if isinstance(raw_bottlenecks, list):
                        for item in raw_bottlenecks:
                            if isinstance(item, dict):
                                bottlenecks.append({
                                    "construct": clean_str(item.get("construct"), "Inner construct"),
                                    "type": clean_str(item.get("type"), "Time Bottleneck"),
                                    "severity": clean_str(item.get("severity"), "High"),
                                    "explanation": clean_str(item.get("explanation"), ""),
                                })
                            elif isinstance(item, str) and item.strip():
                                bottlenecks.append({
                                    "construct": "Code Loop / Lookup",
                                    "type": "Performance Bottleneck",
                                    "severity": "High",
                                    "explanation": item.strip(),
                                })

                    # 8. Parse refactoring roadmap
                    raw_roadmap = parsed_data.get("refactoring_roadmap") or parsed_data.get("refactoring_suggestions", [])
                    refactoring_roadmap = []
                    legacy_refactoring_suggestions = []
                    if isinstance(raw_roadmap, list):
                        for idx, item in enumerate(raw_roadmap):
                            if isinstance(item, dict):
                                step = {
                                    "step_number": item.get("step_number", idx + 1),
                                    "title": clean_str(item.get("title"), f"Optimization Step {idx + 1}"),
                                    "action": clean_str(item.get("action"), ""),
                                    "code_snippet": clean_str(item.get("code_snippet"), ""),
                                    "expected_gain": clean_str(item.get("expected_gain"), ""),
                                }
                                refactoring_roadmap.append(step)
                                legacy_refactoring_suggestions.append(f"{step['title']}: {step['action']}")
                            elif isinstance(item, str) and item.strip():
                                s = item.strip()
                                if s.startswith("- ") or s.startswith("* ") or s.startswith("• "):
                                    s = s[2:].strip()
                                refactoring_roadmap.append({
                                    "step_number": idx + 1,
                                    "title": f"Refactoring Step {idx + 1}",
                                    "action": s,
                                    "code_snippet": "",
                                    "expected_gain": "",
                                })
                                legacy_refactoring_suggestions.append(s)

                    # 9. Parse pro tips
                    pro_tips = clean_list(parsed_data.get("pro_tips", []))

                    legacy_complexity = clean_str(
                        parsed_data.get("complexity_analysis") or user_analysis["mathematical_derivation"]
                    )

                    return {
                        "summary": clean_str(parsed_data.get("summary"), "Algorithmic analysis complete."),
                        "user_solution_analysis": user_analysis,
                        "optimal_solution_analysis": optimal_analysis,
                        "comparative_complexity": comparative_complexity,
                        "algorithmic_paradigm": paradigm,
                        "key_insights": key_insights,
                        "complexity_deep_dive": complexity_deep_dive,
                        "bottlenecks": bottlenecks,
                        "refactoring_roadmap": refactoring_roadmap,
                        "pro_tips": pro_tips,
                        # Legacy compatibility fields
                        "refactoring_suggestions": legacy_refactoring_suggestions,
                        "complexity_analysis": legacy_complexity,
                        "model_used": model,
                    }

                error_body = response.text
                logger.warning("Groq model '%s' failed (%d): %s", model, response.status_code, error_body)
                last_error = f"Status {response.status_code}: {error_body}"

                # If it's not a model error or 404, don't try other models (e.g. 401 Unauthorized)
                if response.status_code == 401 or "invalid_api_key" in error_body:
                    raise ValueError(f"Invalid Groq API Key: {error_body}")

            except httpx.HTTPError as e:
                logger.warning("Network error with model '%s': %s", model, e)
                last_error = str(e)

        raise ValueError(f"Groq API request failed across models. Details: {last_error}")

