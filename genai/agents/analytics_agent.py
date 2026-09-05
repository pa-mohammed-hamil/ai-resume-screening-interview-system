"""
genai/agents/analytics_agent.py

AI Analytics Agent
==================

LLM-powered analytics assistant responsible for:

- Recruitment analytics
- Hiring funnel analysis
- Candidate statistics
- Resume screening analytics
- Interview analytics
- Job performance analysis
- Time-to-hire insights
- Skill demand analysis
- Candidate ranking insights
- Trend analysis
- Anomaly identification
- Recruiter-facing recommendations

Important:
The Analytics Agent does not directly access the database.

Database queries and authoritative calculations should be handled by:

    backend/app/services/analytics_service.py

The Analytics Agent receives already-computed analytics/context and
uses the LLM to explain, summarize, interpret, and recommend actions.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from genai.llm.client import LLMClient
from genai.llm.model_config import ModelConfig
from genai.llm.prompts import ANALYTICS_SYSTEM_PROMPT


logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass
class AnalyticsContext:
    """
    Analytics data supplied to the analytics agent.
    """

    date_range: Optional[Dict[str, Any]] = None

    organization: Optional[Dict[str, Any]] = None

    jobs: List[Dict[str, Any]] = field(
        default_factory=list
    )

    candidates: List[Dict[str, Any]] = field(
        default_factory=list
    )

    interviews: List[Dict[str, Any]] = field(
        default_factory=list
    )

    resumes: List[Dict[str, Any]] = field(
        default_factory=list
    )

    funnel: Optional[Dict[str, Any]] = None

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    trends: Dict[str, Any] = field(
        default_factory=dict
    )

    ranking_data: Optional[Dict[str, Any]] = None

    fairness_data: Optional[Dict[str, Any]] = None

    additional_context: Optional[str] = None


@dataclass
class AnalyticsResponse:
    """
    Standardized analytics-agent response.
    """

    answer: str

    insights: List[str] = field(
        default_factory=list
    )

    recommendations: List[str] = field(
        default_factory=list
    )

    trends: List[str] = field(
        default_factory=list
    )

    anomalies: List[str] = field(
        default_factory=list
    )

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    warnings: List[str] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


# ============================================================================
# ANALYTICS AGENT
# ============================================================================


class AnalyticsAgent:
    """
    LLM-powered recruitment analytics assistant.

    Example:

        agent = AnalyticsAgent()

        context = AnalyticsContext(
            metrics={
                "applications": 450,
                "screened": 220,
                "interviews": 75,
                "offers": 12,
                "hires": 9,
            }
        )

        result = await agent.analyze(
            context=context
        )
    """

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        model_config: Optional[ModelConfig] = None,
    ) -> None:

        self.model_config = model_config or ModelConfig()

        self.llm = llm_client or LLMClient(
            model_config=self.model_config
        )

    # ========================================================================
    # GENERAL ANALYTICS
    # ========================================================================

    async def ask(
        self,
        query: str,
        context: Optional[AnalyticsContext] = None,
    ) -> AnalyticsResponse:
        """
        Process a general analytics request.
        """

        if not query or not query.strip():
            raise ValueError(
                "Analytics query cannot be empty."
            )

        context = context or AnalyticsContext()

        prompt = self._build_prompt(
            query=query.strip(),
            context=context,
        )

        try:

            result = await self._generate(prompt)

            return self._parse_response(
                result=result,
                query=query,
            )

        except Exception as exc:

            logger.exception(
                "Analytics agent failed: %s",
                exc,
            )

            return AnalyticsResponse(
                answer=(
                    "I couldn't process the analytics request "
                    "right now. Please try again."
                ),
                warnings=[
                    "Analytics AI service is temporarily unavailable."
                ],
                metadata={
                    "error": str(exc),
                },
            )

    # ========================================================================
    # COMPLETE ANALYSIS
    # ========================================================================

    async def analyze(
        self,
        context: AnalyticsContext,
    ) -> AnalyticsResponse:
        """
        Perform a complete recruitment analytics analysis.
        """

        query = """
Analyze the supplied recruitment analytics.

Identify:

- major performance indicators;
- important trends;
- recruitment bottlenecks;
- candidate funnel performance;
- interview performance;
- job performance;
- unusual changes;
- areas requiring attention;
- actionable recommendations.

Do not invent metrics.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ========================================================================
    # DASHBOARD SUMMARY
    # ========================================================================

    async def dashboard_summary(
        self,
        context: AnalyticsContext,
    ) -> AnalyticsResponse:
        """
        Generate a concise dashboard summary.
        """

        query = """
Create a concise recruiter dashboard summary.

Highlight:

- total candidates;
- active jobs;
- applications;
- screened candidates;
- interviews;
- offers;
- hires;
- conversion rates;
- major changes compared with previous periods;
- the most important action for the recruiter.

Use supplied metrics only.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ========================================================================
    # RECRUITMENT FUNNEL
    # ========================================================================

    async def analyze_funnel(
        self,
        funnel: Dict[str, Any],
        date_range: Optional[Dict[str, Any]] = None,
    ) -> AnalyticsResponse:
        """
        Analyze the recruitment funnel.
        """

        context = AnalyticsContext(
            funnel=funnel,
            date_range=date_range,
        )

        query = """
Analyze the recruitment funnel.

Evaluate:

- applications;
- screening;
- shortlisted candidates;
- interviews;
- offers;
- hires;
- conversion rates;
- largest drop-off points;
- possible bottlenecks;
- practical improvements.

Do not invent missing conversion rates.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ========================================================================
    # CANDIDATE ANALYTICS
    # ========================================================================

    async def analyze_candidates(
        self,
        candidates: List[Dict[str, Any]],
        context: Optional[AnalyticsContext] = None,
    ) -> AnalyticsResponse:
        """
        Analyze candidate-level or aggregate candidate data.
        """

        analytics_context = context or AnalyticsContext()

        analytics_context.candidates = candidates

        query = """
Analyze the supplied candidate analytics.

Identify:

- candidate volume;
- candidate quality patterns;
- common skills;
- skill gaps;
- screening outcomes;
- candidate source patterns;
- ranking patterns;
- potential bottlenecks.

Focus on job-relevant information.
""".strip()

        return await self.ask(
            query=query,
            context=analytics_context,
        )

    # ========================================================================
    # INTERVIEW ANALYTICS
    # ========================================================================

    async def analyze_interviews(
        self,
        interviews: List[Dict[str, Any]],
        context: Optional[AnalyticsContext] = None,
    ) -> AnalyticsResponse:
        """
        Analyze interview performance.
        """

        analytics_context = context or AnalyticsContext()

        analytics_context.interviews = interviews

        query = """
Analyze interview analytics.

Evaluate:

- number of interviews;
- completion rates;
- average interview scores;
- technical performance;
- communication performance;
- confidence-related evaluation metrics;
- question difficulty;
- candidate drop-off;
- interview bottlenecks;
- trends.

Identify areas that may require process improvement.
""".strip()

        return await self.ask(
            query=query,
            context=analytics_context,
        )

    # ========================================================================
    # JOB ANALYTICS
    # ========================================================================

    async def analyze_jobs(
        self,
        jobs: List[Dict[str, Any]],
        context: Optional[AnalyticsContext] = None,
    ) -> AnalyticsResponse:
        """
        Analyze job-level recruitment performance.
        """

        analytics_context = context or AnalyticsContext()

        analytics_context.jobs = jobs

        query = """
Analyze job-level recruitment performance.

For each relevant job, consider:

- applications;
- qualified candidates;
- screening rate;
- interview rate;
- offer rate;
- hiring rate;
- time-to-hire;
- candidate quality;
- difficult-to-fill roles.

Identify which roles may need attention and explain why.
""".strip()

        return await self.ask(
            query=query,
            context=analytics_context,
        )

    # ========================================================================
    # TIME-TO-HIRE
    # ========================================================================

    async def analyze_time_to_hire(
        self,
        metrics: Dict[str, Any],
        context: Optional[AnalyticsContext] = None,
    ) -> AnalyticsResponse:
        """
        Analyze time-to-hire and recruitment speed.
        """

        analytics_context = context or AnalyticsContext()

        analytics_context.metrics.update(metrics)

        query = """
Analyze recruitment speed and time-to-hire metrics.

Identify:

- average time-to-hire;
- median time-to-hire if available;
- slow recruitment stages;
- roles with long hiring cycles;
- potential process bottlenecks;
- practical ways to reduce delays.

Use only supplied metrics.
""".strip()

        return await self.ask(
            query=query,
            context=analytics_context,
        )

    # ========================================================================
    # TREND ANALYSIS
    # ========================================================================

    async def analyze_trends(
        self,
        trends: Dict[str, Any],
        context: Optional[AnalyticsContext] = None,
    ) -> AnalyticsResponse:
        """
        Analyze historical recruitment trends.
        """

        analytics_context = context or AnalyticsContext()

        analytics_context.trends = trends

        query = """
Analyze the historical recruitment trends.

Identify:

- upward trends;
- downward trends;
- stable metrics;
- significant changes;
- possible recruitment bottlenecks;
- areas requiring investigation.

Do not claim causation unless the supplied data supports it.
""".strip()

        return await self.ask(
            query=query,
            context=analytics_context,
        )

    # ========================================================================
    # ANOMALY DETECTION
    # ========================================================================

    async def detect_anomalies(
        self,
        metrics: Dict[str, Any],
        trends: Optional[Dict[str, Any]] = None,
    ) -> AnalyticsResponse:
        """
        Identify unusual changes in recruitment metrics.

        This is an interpretation layer. Statistical anomaly detection
        should preferably happen before calling this agent.
        """

        context = AnalyticsContext(
            metrics=metrics,
            trends=trends or {},
        )

        query = """
Review the supplied recruitment metrics for unusual patterns.

Identify:

- unexpected spikes;
- unexpected drops;
- unusually high or low conversion rates;
- sudden changes in interview performance;
- unusual candidate volumes;
- metrics that require investigation.

Do not label something an anomaly without sufficient evidence.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ========================================================================
    # SKILL ANALYTICS
    # ========================================================================

    async def analyze_skill_demand(
        self,
        candidates: List[Dict[str, Any]],
        jobs: List[Dict[str, Any]],
    ) -> AnalyticsResponse:
        """
        Analyze skills across candidates and job descriptions.
        """

        context = AnalyticsContext(
            candidates=candidates,
            jobs=jobs,
        )

        query = """
Analyze skill demand across the supplied candidates and jobs.

Identify:

- frequently requested skills;
- frequently available skills;
- common skill gaps;
- hard-to-find skills;
- emerging skill requirements;
- opportunities for candidate development.

Focus on evidence in the supplied data.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ========================================================================
    # RANKING ANALYTICS
    # ========================================================================

    async def analyze_ranking(
        self,
        ranking_data: Dict[str, Any],
        context: Optional[AnalyticsContext] = None,
    ) -> AnalyticsResponse:
        """
        Explain candidate-ranking analytics.
        """

        analytics_context = context or AnalyticsContext()

        analytics_context.ranking_data = ranking_data

        query = """
Analyze the candidate ranking data.

Explain:

- ranking distribution;
- strongest candidates according to supplied scores;
- important scoring factors;
- large score differences;
- candidates requiring manual review;
- possible data-quality issues.

Do not create a new ranking.
Explain the supplied ranking instead.
""".strip()

        return await self.ask(
            query=query,
            context=analytics_context,
        )

    # ========================================================================
    # FAIRNESS ANALYTICS
    # ========================================================================

    async def analyze_fairness(
        self,
        fairness_data: Dict[str, Any],
        context: Optional[AnalyticsContext] = None,
    ) -> AnalyticsResponse:
        """
        Explain fairness metrics supplied by the fairness subsystem.
        """

        analytics_context = context or AnalyticsContext()

        analytics_context.fairness_data = fairness_data

        query = """
Explain the supplied recruitment fairness metrics.

Identify:

- important disparities;
- metrics outside expected ranges;
- stages where disparities appear;
- areas requiring investigation;
- practical monitoring recommendations.

Do not infer protected characteristics from names or other
candidate information.

Do not claim discrimination solely from an unexplained metric.
""".strip()

        return await self.ask(
            query=query,
            context=analytics_context,
        )

    # ========================================================================
    # RECRUITER RECOMMENDATIONS
    # ========================================================================

    async def generate_recommendations(
        self,
        context: AnalyticsContext,
    ) -> AnalyticsResponse:
        """
        Generate actionable recruiter recommendations.
        """

        query = """
Based on the supplied recruitment analytics, generate actionable
recommendations.

Prioritize recommendations by:

1. Business impact
2. Evidence strength
3. Urgency
4. Implementation effort

For each recommendation, explain which metric or trend supports it.
""".strip()

        return await self.ask(
            query=query,
            context=context,
        )

    # ========================================================================
    # LLM GENERATION
    # ========================================================================

    async def _generate(
        self,
        prompt: str,
    ) -> Any:
        """
        Call the configured LLM client.
        """

        if hasattr(self.llm, "generate"):

            return await self.llm.generate(
                prompt=prompt,
                system_prompt=ANALYTICS_SYSTEM_PROMPT,
            )

        if hasattr(self.llm, "complete"):

            return await self.llm.complete(
                prompt=prompt,
                system_prompt=ANALYTICS_SYSTEM_PROMPT,
            )

        raise AttributeError(
            "LLMClient must implement generate() or complete()."
        )

    # ========================================================================
    # PROMPT BUILDING
    # ========================================================================

    def _build_prompt(
        self,
        query: str,
        context: AnalyticsContext,
    ) -> str:
        """
        Build a structured analytics prompt.
        """

        context_payload = {
            "date_range": context.date_range,
            "organization": context.organization,
            "jobs": context.jobs,
            "candidates": context.candidates,
            "interviews": context.interviews,
            "resumes": context.resumes,
            "funnel": context.funnel,
            "metrics": context.metrics,
            "trends": context.trends,
            "ranking_data": context.ranking_data,
            "fairness_data": context.fairness_data,
            "additional_context": context.additional_context,
        }

        serialized_context = json.dumps(
            context_payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

        return f"""
RECRUITMENT ANALYTICS REQUEST
=============================

{query}


ANALYTICS CONTEXT
=================

{serialized_context}


INSTRUCTIONS
============

1. Use only supplied analytics data.
2. Never invent metrics.
3. Never invent trends.
4. Clearly distinguish facts from interpretation.
5. Do not claim causation without evidence.
6. Identify missing data when necessary.
7. Focus on recruitment and job-related information.
8. Do not infer protected characteristics.
9. Do not make employment decisions.
10. Recommendations must be evidence-based.
11. Explain important conclusions.
12. Flag suspicious or incomplete data.


RETURN JSON
===========

{{
    "answer": "main analytics explanation",

    "insights": [
        "important insight 1",
        "important insight 2"
    ],

    "recommendations": [
        "actionable recommendation 1"
    ],

    "trends": [
        "trend 1"
    ],

    "anomalies": [
        "anomaly or unusual pattern 1"
    ],

    "metrics": {{
        "metric_name": "value"
    }},

    "warnings": [
        "data limitation or warning"
    ]
}}
""".strip()

    # ========================================================================
    # RESPONSE PARSING
    # ========================================================================

    def _parse_response(
        self,
        result: Any,
        query: str,
    ) -> AnalyticsResponse:
        """
        Convert LLM response into AnalyticsResponse.
        """

        text = self._extract_text(result)

        if not text:

            return AnalyticsResponse(
                answer="The AI model returned an empty response.",
                warnings=[
                    "Empty model response."
                ],
            )

        parsed = self._try_parse_json(text)

        if isinstance(parsed, dict):

            return AnalyticsResponse(
                answer=str(
                    parsed.get(
                        "answer",
                        "No analytics explanation was generated.",
                    )
                ),

                insights=self._as_string_list(
                    parsed.get(
                        "insights",
                        [],
                    )
                ),

                recommendations=self._as_string_list(
                    parsed.get(
                        "recommendations",
                        [],
                    )
                ),

                trends=self._as_string_list(
                    parsed.get(
                        "trends",
                        [],
                    )
                ),

                anomalies=self._as_string_list(
                    parsed.get(
                        "anomalies",
                        [],
                    )
                ),

                metrics=self._as_dict(
                    parsed.get(
                        "metrics",
                        {},
                    )
                ),

                warnings=self._as_string_list(
                    parsed.get(
                        "warnings",
                        [],
                    )
                ),

                metadata={
                    "query": query,
                    "structured_response": True,
                },
            )

        return AnalyticsResponse(
            answer=text,
            metadata={
                "query": query,
                "structured_response": False,
            },
        )

    # ========================================================================
    # TEXT EXTRACTION
    # ========================================================================

    @staticmethod
    def _extract_text(
        result: Any,
    ) -> str:
        """
        Extract text from common LLM response formats.
        """

        if result is None:
            return ""

        if isinstance(result, str):
            return result.strip()

        if isinstance(result, dict):

            for key in (
                "text",
                "content",
                "response",
                "output",
            ):

                value = result.get(key)

                if isinstance(value, str):
                    return value.strip()

            choices = result.get("choices")

            if isinstance(choices, list) and choices:

                first = choices[0]

                if isinstance(first, dict):

                    message = first.get("message")

                    if isinstance(message, dict):

                        content = message.get("content")

                        if isinstance(content, str):
                            return content.strip()

                    content = first.get("text")

                    if isinstance(content, str):
                        return content.strip()

        return str(result).strip()

    # ========================================================================
    # JSON PARSING
    # ========================================================================

    @staticmethod
    def _try_parse_json(
        text: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Safely parse JSON returned by an LLM.
        """

        cleaned = text.strip()

        if cleaned.startswith("```"):

            lines = cleaned.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            cleaned = "\n".join(lines).strip()

        try:

            parsed = json.loads(cleaned)

            if isinstance(parsed, dict):
                return parsed

        except json.JSONDecodeError:

            pass

        return None

    # ========================================================================
    # TYPE HELPERS
    # ========================================================================

    @staticmethod
    def _as_string_list(
        value: Any,
    ) -> List[str]:
        """
        Convert arbitrary values to a list of strings.
        """

        if value is None:
            return []

        if isinstance(value, str):
            return [value]

        if isinstance(value, list):

            return [
                str(item)
                for item in value
                if item is not None
            ]

        return [str(value)]

    @staticmethod
    def _as_dict(
        value: Any,
    ) -> Dict[str, Any]:
        """
        Convert an arbitrary value to a dictionary.
        """

        if isinstance(value, dict):
            return value

        return {}