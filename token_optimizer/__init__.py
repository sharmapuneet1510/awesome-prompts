"""Token-Optimized Query Client with Smart Prompt Filtering

A Python library that intelligently analyzes user queries before dispatching them to Claude,
scoring prompts, detecting queries better served by web search, and providing actionable
feedback to reduce token waste and improve efficiency.
"""

from .analyzer import QueryAnalyzer
from .models import AnalysisResult, QueryFeedback, ScoringMetrics
from .config import Config, ScoringWeights

__version__ = "1.0.0"
__author__ = "Claude Code"

__all__ = [
    "QueryAnalyzer",
    "AnalysisResult",
    "QueryFeedback",
    "ScoringMetrics",
    "Config",
    "ScoringWeights",
]
