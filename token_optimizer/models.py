"""Data models for Token Optimizer"""

from dataclasses import dataclass, field
from typing import List, Literal
from enum import Enum


class QueryStatus(str, Enum):
    """Query status enum"""
    REJECTED = "query_rejected"
    IMPROVED = "query_improved"
    FORWARDED = "forwarded"


class QueryType(str, Enum):
    """Query type classification"""
    RESEARCH = "research"
    CODING = "coding"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    QUESTION = "question"
    INSTRUCTION = "instruction"
    OTHER = "other"


class Recommendation(str, Enum):
    """Routing recommendation"""
    WEB_SEARCH = "web_search"
    CLAUDE = "claude"
    COMBINED = "combined"
    SKIP = "skip"


@dataclass
class ScoringMetrics:
    """Individual scoring metrics"""
    clarity: float  # 0-100: Grammar, specificity, coherence
    context: float  # 0-100: Sufficient context provided
    feasibility: float  # 0-100: Achievability with Claude

    @property
    def overall(self) -> float:
        """Calculate composite score"""
        return (self.clarity + self.context + self.feasibility) / 3


@dataclass
class QueryFeedback:
    """Structured feedback for query"""
    status: QueryStatus
    score: float
    reason: str
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    recommendation: Recommendation = Recommendation.CLAUDE
    tokens_spared: int = 0


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    query: str
    query_type: QueryType
    is_valid: bool

    # Metrics
    metrics: ScoringMetrics

    # Feedback
    feedback: QueryFeedback

    # Additional analysis
    requires_web_search: bool
    requires_external_data: bool
    estimated_tokens: int

    # Metadata
    analysis_time_ms: float

    @property
    def should_proceed(self) -> bool:
        """Determine if query should proceed to Claude"""
        return self.feedback.status == QueryStatus.FORWARDED and self.feedback.score >= 30

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "query": self.query,
            "query_type": self.query_type.value,
            "is_valid": self.is_valid,
            "metrics": {
                "clarity": self.metrics.clarity,
                "context": self.metrics.context,
                "feasibility": self.metrics.feasibility,
                "overall": self.metrics.overall,
            },
            "feedback": {
                "status": self.feedback.status.value,
                "score": self.feedback.score,
                "reason": self.feedback.reason,
                "issues": self.feedback.issues,
                "suggestions": self.feedback.suggestions,
                "recommendation": self.feedback.recommendation.value,
                "tokens_spared": self.feedback.tokens_spared,
            },
            "requires_web_search": self.requires_web_search,
            "requires_external_data": self.requires_external_data,
            "estimated_tokens": self.estimated_tokens,
            "analysis_time_ms": self.analysis_time_ms,
        }
