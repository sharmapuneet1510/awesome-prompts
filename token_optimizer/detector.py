"""Detectors for alternative solutions"""

import re
from typing import Tuple
from .config import Config


class WebSearchDetector:
    """Detect queries that would benefit from web search"""

    # Patterns that strongly suggest web search is needed
    STRONG_PATTERNS = [
        r"\b(latest|current|today|yesterday|tomorrow)\b.*\b(news|weather|stock|score|event)\b",
        r"\b(what'?s trending|what'?s happening|what'?s new)\b",
        r"\b(current (price|rate|weather|time|status))\b",
        r"\b(real-time|live|now)\b",
        r"\b(breaking|just happened|just occurred)\b",
    ]

    # Moderate patterns
    MODERATE_PATTERNS = [
        r"\b(latest|recent|new)\b",
        r"\b(trending|popular|viral)\b",
        r"\b(weather|news|sports|score)\b",
        r"\b(stock|price|rate|exchange)\b",
        r"\b(event|conference|release)\b",
    ]

    @staticmethod
    def detect(query: str, config: Config = None) -> Tuple[bool, float, str]:
        """
        Detect if query needs web search
        Returns: (needs_web_search, confidence, reason)
        """
        if config is None:
            config = Config.default()

        query_lower = query.lower()

        # Check strong patterns
        for pattern in WebSearchDetector.STRONG_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True, 0.95, "Strong web search indicator detected"

        # Check moderate patterns
        moderate_count = 0
        for pattern in WebSearchDetector.MODERATE_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                moderate_count += 1

        if moderate_count >= 2:
            return True, 0.80, "Multiple web search indicators detected"

        # Check configured keywords
        keyword_count = sum(
            1 for keyword in config.web_search_keywords
            if keyword in query_lower
        )
        if keyword_count >= 2:
            return True, 0.70, "Web search keywords present"

        return False, 0.0, ""


class ExternalDataDetector:
    """Detect if query requires external/real-time data"""

    EXTERNAL_DATA_PATTERNS = [
        r"\b(real-time|live|current|latest)\b",
        r"\b(api|endpoint|webhook)\b",
        r"\b(database|query|sql)\b.*\b(external|remote)\b",
        r"\b(fetch|retrieve|pull)\b.*\b(data|information|records)\b",
    ]

    @staticmethod
    def detect(query: str) -> Tuple[bool, str]:
        """
        Detect if query requires external data
        Returns: (requires_external_data, reason)
        """
        query_lower = query.lower()

        for pattern in ExternalDataDetector.EXTERNAL_DATA_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True, "External data access required"

        return False, ""


class TokenEstimator:
    """Estimate tokens required for query"""

    @staticmethod
    def estimate(query: str, config: Config = None) -> int:
        """
        Estimate tokens for query
        Uses average tokens per word: ~1.3
        """
        if config is None:
            config = Config.default()

        word_count = len(query.split())
        estimated_tokens = int(word_count * config.avg_tokens_per_word)

        return estimated_tokens


class SimpleLookupDetector:
    """Detect simple lookup queries that could use search instead"""

    SIMPLE_PATTERNS = [
        r"\b(what is|who is|when was|where is)\b",
        r"\b(definition|meaning|biography|overview)\b",
        r"\b(capital of|population of|area of)\b",
        r"\b(list of|members of|categories of)\b",
    ]

    @staticmethod
    def detect(query: str) -> Tuple[bool, str]:
        """
        Detect simple lookup queries
        Returns: (is_simple_lookup, reason)
        """
        query_lower = query.lower()

        # Query must be short and simple
        word_count = len(query.split())
        if word_count > 15:
            return False, ""

        # Check patterns
        for pattern in SimpleLookupDetector.SIMPLE_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return True, "Simple lookup query - web search recommended"

        return False, ""
