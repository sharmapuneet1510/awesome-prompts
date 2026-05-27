"""Main query analyzer that orchestrates all components"""

import time
from typing import Optional
from .config import Config
from .models import (
    AnalysisResult, QueryFeedback, ScoringMetrics,
    QueryStatus, QueryType, Recommendation
)
from .scoring import (
    ClarityScorer, ContextScorer, FeasibilityScorer, IntentDetector
)
from .detector import (
    WebSearchDetector, ExternalDataDetector, TokenEstimator, SimpleLookupDetector
)


class QueryAnalyzer:
    """Analyze queries and provide routing recommendations"""

    def __init__(self, config: Config = None):
        """Initialize analyzer with config"""
        self.config = config or Config.default()

    def analyze(self, query: str) -> AnalysisResult:
        """
        Analyze query and return complete analysis result
        """
        start_time = time.time()

        # Validate query
        if not query or not query.strip():
            return self._invalid_query_result(query, start_time)

        query = query.strip()

        # Score clarity, context, feasibility
        clarity = ClarityScorer.score(query)
        context = ContextScorer.score(query)
        feasibility = FeasibilityScorer.score(query)

        # Create metrics
        metrics = ScoringMetrics(
            clarity=clarity,
            context=context,
            feasibility=feasibility
        )

        # Detect query intent
        query_type_str = IntentDetector.detect(query)
        query_type = QueryType(query_type_str) if query_type_str in QueryType.__members__ else QueryType.OTHER

        # Check if web search needed
        needs_web_search, web_search_confidence, web_search_reason = WebSearchDetector.detect(query, self.config)

        # Check if simple lookup (alternative routing)
        is_simple_lookup, lookup_reason = SimpleLookupDetector.detect(query)

        # Check external data needs
        requires_external_data, external_reason = ExternalDataDetector.detect(query)

        # Estimate tokens
        estimated_tokens = TokenEstimator.estimate(query, self.config)

        # Generate feedback
        overall_score = metrics.overall
        issues, suggestions = self._generate_issues_and_suggestions(query, metrics, query_type)
        recommendation = self._determine_recommendation(
            overall_score, needs_web_search, is_simple_lookup,
            requires_external_data
        )

        # Determine status
        if overall_score < self.config.poor_threshold:
            status = QueryStatus.REJECTED
        elif overall_score < self.config.moderate_threshold:
            status = QueryStatus.IMPROVED
        else:
            status = QueryStatus.FORWARDED

        # Calculate tokens spared if routed to web search
        tokens_spared = 0
        if recommendation == Recommendation.WEB_SEARCH:
            tokens_spared = estimated_tokens

        feedback = QueryFeedback(
            status=status,
            score=overall_score,
            reason=self._generate_reason(overall_score, issues, recommendation),
            issues=issues,
            suggestions=suggestions,
            recommendation=recommendation,
            tokens_spared=tokens_spared
        )

        # Determine validity
        is_valid = overall_score >= self.config.poor_threshold

        # Calculate analysis time
        analysis_time = (time.time() - start_time) * 1000

        return AnalysisResult(
            query=query,
            query_type=query_type,
            is_valid=is_valid,
            metrics=metrics,
            feedback=feedback,
            requires_web_search=needs_web_search,
            requires_external_data=requires_external_data,
            estimated_tokens=estimated_tokens,
            analysis_time_ms=analysis_time
        )

    def _invalid_query_result(self, query: str, start_time: float) -> AnalysisResult:
        """Return result for invalid/empty query"""
        metrics = ScoringMetrics(clarity=0.0, context=0.0, feasibility=0.0)
        feedback = QueryFeedback(
            status=QueryStatus.REJECTED,
            score=0.0,
            reason="Query is empty or only whitespace",
            issues=["Empty query"],
            suggestions=["Provide a non-empty query"],
            recommendation=Recommendation.SKIP,
            tokens_spared=0
        )
        return AnalysisResult(
            query=query,
            query_type=QueryType.OTHER,
            is_valid=False,
            metrics=metrics,
            feedback=feedback,
            requires_web_search=False,
            requires_external_data=False,
            estimated_tokens=0,
            analysis_time_ms=(time.time() - start_time) * 1000
        )

    def _generate_issues_and_suggestions(
        self, query: str, metrics: ScoringMetrics, query_type: QueryType
    ) -> tuple:
        """Generate issues and suggestions based on metrics"""
        issues = []
        suggestions = []

        # Check clarity
        if metrics.clarity < 30:
            issues.append("Poor clarity: query lacks specificity")
            suggestions.append("Add more specific details or examples")
        elif metrics.clarity < 50:
            issues.append("Moderate clarity: could be more specific")
            suggestions.append("Include concrete examples or constraints")

        # Check context
        if metrics.context < 30:
            issues.append("Insufficient context: missing background information")
            suggestions.append("Provide domain, technical stack, or project context")
        elif metrics.context < 50:
            issues.append("Limited context: more background would help")
            suggestions.append("Add relevant constraints, requirements, or examples")

        # Check feasibility
        if metrics.feasibility < 30:
            issues.append("Low feasibility: may require external data or real-time information")
            suggestions.append("Consider using web search for live data or recent information")
        elif metrics.feasibility < 50:
            issues.append("Moderate feasibility: some external dependencies")
            suggestions.append("Clarify real-time vs. training-data-based requirements")

        return issues, suggestions

    def _determine_recommendation(
        self, score: float, needs_web_search: bool, is_simple_lookup: bool,
        requires_external_data: bool
    ) -> Recommendation:
        """Determine routing recommendation"""
        # Strong indicators for web search
        if needs_web_search or requires_external_data:
            return Recommendation.WEB_SEARCH

        # Simple lookups can use web search
        if is_simple_lookup:
            return Recommendation.WEB_SEARCH

        # Poor score = skip or improve
        if score < 30:
            return Recommendation.SKIP

        # Moderate = can proceed to Claude
        if score < 60:
            return Recommendation.CLAUDE

        # Good = proceed to Claude
        return Recommendation.CLAUDE

    def _generate_reason(self, score: float, issues: list, recommendation: Recommendation) -> str:
        """Generate human-readable reason for the result"""
        if score < 30:
            if not issues:
                return "Query does not meet minimum quality threshold"
            return f"Query quality is poor: {issues[0]}"

        if score < 60:
            if recommendation == Recommendation.WEB_SEARCH:
                return "Query would benefit from web search for live/recent data"
            return "Query quality is moderate; consider adding more context"

        if recommendation == Recommendation.WEB_SEARCH:
            return "Query is suitable for web search"

        return "Query is ready for Claude"
