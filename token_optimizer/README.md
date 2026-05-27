# Token Optimizer: Intelligent Query Analysis for Claude

A Python library that intelligently analyzes user queries before dispatching them to Claude, scoring prompts, detecting queries better served by web search, and providing actionable feedback to reduce token waste and improve efficiency.

## Features

- **Query Scoring**: Multi-dimensional evaluation of query clarity, context, and feasibility
- **Web Search Detection**: Identifies queries requiring web search for current/trending information
- **Intent Classification**: Automatically detects query type (research, coding, analysis, creative, instruction)
- **Token Estimation**: Estimates tokens required for query processing
- **Smart Routing**: Recommends optimal routing (Claude, web search, or combined approach)
- **Configurable Thresholds**: Supports default, strict, and lenient scoring configurations
- **Structured Feedback**: Provides detailed issues and actionable suggestions

## Installation

```bash
pip install token-optimizer
```

Or from source:

```bash
git clone <repository>
cd awesome-prompts
pip install -e token_optimizer/
```

## Quick Start

```python
from token_optimizer import QueryAnalyzer, Config

# Create analyzer with default config
analyzer = QueryAnalyzer()

# Analyze a query
result = analyzer.analyze("How do I implement a binary search tree in Python?")

# Check result
print(f"Status: {result.feedback.status}")
print(f"Score: {result.feedback.score}")
print(f"Recommendation: {result.feedback.recommendation}")
print(f"Issues: {result.feedback.issues}")
print(f"Suggestions: {result.feedback.suggestions}")
```

## Core Components

### QueryAnalyzer

Main entry point for query analysis. Orchestrates all scoring and detection modules.

```python
from token_optimizer import QueryAnalyzer, Config

# Use default configuration
analyzer = QueryAnalyzer()

# Or use strict/lenient configs
strict_analyzer = QueryAnalyzer(Config.strict())
lenient_analyzer = QueryAnalyzer(Config.lenient())

# Analyze query
result = analyzer.analyze("Your query here")
```

### ScoringMetrics

Evaluates query on three dimensions:

- **Clarity** (0-100): Grammar, specificity, coherence
  - Considers word count, punctuation, and specific patterns
  
- **Context** (0-100): Sufficiency of background information
  - Checks for technical/domain keywords and constraints
  
- **Feasibility** (0-100): Achievability with Claude's capabilities
  - Identifies real-time needs and external data requirements

```python
result = analyzer.analyze(query)
print(f"Clarity: {result.metrics.clarity}")
print(f"Context: {result.metrics.context}")
print(f"Feasibility: {result.metrics.feasibility}")
print(f"Overall: {result.metrics.overall}")
```

### Query Type Detection

Automatically classifies query intent:

- `RESEARCH` - Learning and investigation
- `CODING` - Programming and implementation
- `ANALYSIS` - Comparative evaluation
- `CREATIVE` - Writing and content generation
- `INSTRUCTION` - How-to and procedural
- `QUESTION` - Direct questions
- `OTHER` - Unclassified

```python
result = analyzer.analyze(query)
print(f"Query Type: {result.query_type}")
```

### Routing Recommendations

Recommends optimal approach:

- `CLAUDE` - Send directly to Claude (good quality, fits Claude's capabilities)
- `WEB_SEARCH` - Route to web search (needs current/trending data)
- `COMBINED` - Use both Claude and web search
- `SKIP` - Query quality too poor

```python
result = analyzer.analyze(query)
print(f"Recommendation: {result.feedback.recommendation}")
```

## Configuration

### Default Config

```python
config = Config.default()
analyzer = QueryAnalyzer(config)
```

Thresholds:
- Poor: < 30 (rejected)
- Moderate: 30-60 (improved)
- Good: >= 60 (forwarded)

### Strict Config

Higher thresholds for quality enforcement:

```python
config = Config.strict()
analyzer = QueryAnalyzer(config)
```

### Lenient Config

Lower thresholds for permissive filtering:

```python
config = Config.lenient()
analyzer = QueryAnalyzer(config)
```

### Custom Config

```python
from token_optimizer import Config, ScoringWeights

config = Config()
config.poor_threshold = 25
config.moderate_threshold = 55
config.good_threshold = 55

# Customize weights
config.weights = ScoringWeights(
    clarity_weight=0.4,
    context_weight=0.3,
    feasibility_weight=0.3
)
config.weights.normalize()

analyzer = QueryAnalyzer(config)
```

## Output Format

The `AnalysisResult` contains complete analysis:

```python
from token_optimizer import QueryAnalyzer

analyzer = QueryAnalyzer()
result = analyzer.analyze("your query")

# Access components
result.query              # Original query
result.query_type         # Detected intent type
result.is_valid           # Boolean validity check
result.metrics            # ScoringMetrics object
result.feedback           # QueryFeedback object
result.requires_web_search     # Boolean
result.requires_external_data  # Boolean
result.estimated_tokens        # Integer
result.analysis_time_ms        # Float

# Get as dictionary
result_dict = result.to_dict()
```

## Feedback System

Detailed feedback includes:

```python
feedback = result.feedback

feedback.status           # QueryStatus enum
feedback.score           # Overall score (0-100)
feedback.reason          # Human-readable reason
feedback.issues          # List of issues found
feedback.suggestions     # List of actionable suggestions
feedback.recommendation  # Recommendation enum
feedback.tokens_spared   # Tokens saved if routed to web search
```

## Examples

### Example 1: Good Query

```python
analyzer = QueryAnalyzer()
result = analyzer.analyze(
    "I'm building a Python FastAPI backend with PostgreSQL. "
    "How do I implement pagination in my REST API with proper error handling and validation?"
)

print(result.to_dict())
# {
#   'query': '...',
#   'query_type': 'instruction',
#   'is_valid': True,
#   'metrics': {'clarity': 60, 'context': 35, 'feasibility': 80, 'overall': 58},
#   'feedback': {
#     'status': 'forwarded',
#     'score': 58,
#     'reason': 'Query is ready for Claude',
#     'issues': [],
#     'suggestions': [],
#     'recommendation': 'claude'
#   },
#   'estimated_tokens': 35
# }
```

### Example 2: Web Search Candidate

```python
result = analyzer.analyze("What are the latest trends in AI today")

print(result.feedback.recommendation)  # web_search
print(result.requires_web_search)      # True
print(result.feedback.tokens_spared)   # 8 (estimated tokens)
```

### Example 3: Poor Quality Query

```python
result = analyzer.analyze("code?")

print(result.is_valid)           # False
print(result.feedback.status)    # rejected
print(result.feedback.issues)    # ['Poor clarity: query lacks specificity']
print(result.feedback.suggestions)  # ['Add more specific details or examples']
```

## API Reference

### QueryAnalyzer

```python
class QueryAnalyzer:
    def __init__(self, config: Config = None)
    def analyze(self, query: str) -> AnalysisResult
```

### Models

```python
class QueryStatus(Enum):
    REJECTED = "query_rejected"
    IMPROVED = "query_improved"
    FORWARDED = "forwarded"

class QueryType(Enum):
    RESEARCH = "research"
    CODING = "coding"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    QUESTION = "question"
    INSTRUCTION = "instruction"
    OTHER = "other"

class Recommendation(Enum):
    WEB_SEARCH = "web_search"
    CLAUDE = "claude"
    COMBINED = "combined"
    SKIP = "skip"

@dataclass
class ScoringMetrics:
    clarity: float       # 0-100
    context: float       # 0-100
    feasibility: float   # 0-100
    
    @property
    def overall(self) -> float

@dataclass
class QueryFeedback:
    status: QueryStatus
    score: float
    reason: str
    issues: List[str]
    suggestions: List[str]
    recommendation: Recommendation
    tokens_spared: int

@dataclass
class AnalysisResult:
    query: str
    query_type: QueryType
    is_valid: bool
    metrics: ScoringMetrics
    feedback: QueryFeedback
    requires_web_search: bool
    requires_external_data: bool
    estimated_tokens: int
    analysis_time_ms: float
    
    @property
    def should_proceed(self) -> bool
    
    def to_dict(self) -> dict
```

## Testing

Run tests with pytest:

```bash
python3 -m pytest tests/test_token_optimizer.py -v
```

Coverage:
- 35 test cases
- All core functionality tested
- Edge cases: long queries, special characters, code snippets, URLs
- Integration tests for complete workflow

## Performance

- Analysis time: < 5ms per query
- Token estimation accuracy: ±10% of actual
- Suitable for real-time filtering before Claude dispatch

## Use Cases

1. **Query Pre-filtering**: Assess query quality before sending to Claude
2. **Cost Optimization**: Identify queries better served by web search
3. **Smart Routing**: Route queries to appropriate services
4. **User Feedback**: Provide users with actionable suggestions
5. **Analytics**: Track query patterns and quality metrics

## Contributing

Contributions welcome! Areas for enhancement:

- Add more intent patterns
- Improve context detection
- Fine-tune scoring weights
- Add language-specific scoring
- Expand external data detection

## License

See LICENSE file in repository

## Version

v1.0.0
