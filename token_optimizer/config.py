"""Configuration for Token Optimizer"""

from dataclasses import dataclass


@dataclass
class ScoringWeights:
    """Weights for scoring metrics"""
    clarity_weight: float = 0.35  # Grammar, specificity, coherence
    context_weight: float = 0.35  # Sufficient context
    feasibility_weight: float = 0.30  # Achievability

    def normalize(self):
        """Ensure weights sum to 1.0"""
        total = self.clarity_weight + self.context_weight + self.feasibility_weight
        if total > 0:
            self.clarity_weight /= total
            self.context_weight /= total
            self.feasibility_weight /= total


@dataclass
class Config:
    """Configuration for QueryAnalyzer"""

    # Scoring thresholds
    poor_threshold: float = 30  # Score < 30: Poor
    moderate_threshold: float = 60  # Score 30-60: Moderate
    good_threshold: float = 60  # Score > 60: Good

    # Weights
    weights: ScoringWeights = None

    # Performance
    max_analysis_time_ms: float = 200  # Max analysis latency

    # Web search patterns
    web_search_keywords: list = None

    # Token estimation
    avg_tokens_per_word: float = 1.3  # Approximate tokens per word

    def __post_init__(self):
        if self.weights is None:
            self.weights = ScoringWeights()
            self.weights.normalize()

        if self.web_search_keywords is None:
            self.web_search_keywords = [
                "latest", "current", "recent", "today", "yesterday",
                "trending", "happening", "news", "weather", "stock",
                "price", "rate", "live", "real-time", "now",
            ]

    @staticmethod
    def default() -> "Config":
        """Get default configuration"""
        return Config()

    @staticmethod
    def strict() -> "Config":
        """Strict configuration - higher thresholds"""
        config = Config()
        config.poor_threshold = 40
        config.moderate_threshold = 70
        config.good_threshold = 70
        return config

    @staticmethod
    def lenient() -> "Config":
        """Lenient configuration - lower thresholds"""
        config = Config()
        config.poor_threshold = 20
        config.moderate_threshold = 50
        config.good_threshold = 50
        return config
