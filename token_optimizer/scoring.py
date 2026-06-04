"""Scoring engines for query analysis"""

import re
from typing import Tuple, List


class ClarityScorer:
    """Score query clarity: grammar, specificity, coherence"""

    @staticmethod
    def score(query: str) -> float:
        """Score clarity 0-100"""
        score = 0.0

        # Length check (specificity)
        word_count = len(query.split())
        if word_count < 3:
            score += 10  # Too short
        elif word_count < 10:
            score += 30  # Somewhat short
        elif word_count < 50:
            score += 50  # Good length
        else:
            score += 40  # Too long, may be rambling

        # Punctuation check
        if "?" in query or "." in query or "!" in query:
            score += 15

        # Specificity indicators
        specific_patterns = [
            r"\b(specific|exact|detailed|example|such as)\b",
            r"\b(when|where|what|why|how)\b",
            r"\b\d+\b",  # Numbers
        ]
        for pattern in specific_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 5

        # Grammar check (basic)
        if len(query) > 0 and query[0].isupper():
            score += 10

        # Avoid spam patterns
        if query.count("???") > 0 or query.count("!!!") > 0:
            score -= 10

        return min(100, max(0, score))


class ContextScorer:
    """Score query context: sufficient information provided"""

    @staticmethod
    def score(query: str) -> float:
        """Score context sufficiency 0-100"""
        score = 0.0

        # Technical context indicators
        tech_keywords = [
            "python", "javascript", "java", "database", "api",
            "library", "framework", "package", "module",
        ]
        for keyword in tech_keywords:
            if keyword in query.lower():
                score += 5

        # Domain context
        domain_keywords = [
            "business", "medical", "legal", "finance", "education",
            "user", "customer", "employee", "market", "product",
        ]
        for keyword in domain_keywords:
            if keyword in query.lower():
                score += 5

        # Constraint/requirement indicators
        constraint_patterns = [
            r"\b(need|require|want|expect|must|should)\b",
            r"\b(constraint|limitation|requirement)\b",
            r"\b(budget|timeline|resources|team)\b",
        ]
        for pattern in constraint_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 10

        # Example/reference indicators
        if re.search(r"\b(example|like|such as|similar)\b", query, re.IGNORECASE):
            score += 10

        # Background context
        if "background" in query.lower() or "context" in query.lower():
            score += 15

        return min(100, max(0, score))


class FeasibilityScorer:
    """Score query feasibility: achievable with Claude's capabilities"""

    @staticmethod
    def score(query: str) -> float:
        """Score feasibility 0-100"""
        score = 50  # Start at baseline

        # Check for real-time requirements (infeasible)
        realtime_keywords = [
            "live", "current", "now", "today", "real-time",
            "trending", "latest news", "stock price",
        ]
        for keyword in realtime_keywords:
            if keyword in query.lower():
                score -= 15

        # Check for external data needs
        external_keywords = [
            "weather", "stock", "sports", "score", "api",
            "current price", "real-time data",
        ]
        for keyword in external_keywords:
            if keyword in query.lower():
                score -= 10

        # Check for feasible Claude tasks
        feasible_keywords = [
            "explain", "summarize", "analyze", "write", "generate",
            "create", "design", "plan", "list", "compare",
            "translate", "code", "debug", "refactor", "document",
        ]
        for keyword in feasible_keywords:
            if keyword in query.lower():
                score += 10

        # Check for code-related queries
        if any(lang in query.lower() for lang in ["python", "javascript", "java", "sql"]):
            score += 10

        # Check for creative/analysis tasks
        if any(task in query.lower() for task in ["brainstorm", "ideate", "brainstorming"]):
            score += 5

        return min(100, max(0, score))


class IntentDetector:
    """Detect query intent/type"""

    INTENT_PATTERNS = {
        "research": [
            r"\b(research|investigate|find|discover|learn|background)\b",
            r"\b(what is|how does|why|explain)\b",
        ],
        "coding": [
            r"\b(code|script|program|function|implement|debug|fix)\b",
            r"\b(python|javascript|java|sql|api)\b",
        ],
        "analysis": [
            r"\b(analyze|compare|contrast|evaluate|assess|review)\b",
            r"\b(pattern|trend|insight|implication)\b",
        ],
        "creative": [
            r"\b(write|compose|create|generate|brainstorm|ideate)\b",
            r"\b(story|poem|content|idea|concept)\b",
        ],
        "instruction": [
            r"\b(how to|steps|process|procedure|guide)\b",
            r"\b(teach|show|demonstrate|explain)\b",
        ],
    }

    @staticmethod
    def detect(query: str) -> str:
        """Detect query intent"""
        query_lower = query.lower()

        for intent, patterns in IntentDetector.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    return intent

        return "other"
