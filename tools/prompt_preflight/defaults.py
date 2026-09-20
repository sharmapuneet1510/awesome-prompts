"""Values decided by the model bake-off (plan Task 3). None means "no recommendation"."""
from typing import Optional

# Ollama model name the setup wizard recommends. None = heuristics-only is the default.
RECOMMENDED_MODEL: Optional[str] = None

# Download size in GB of RECOMMENDED_MODEL, shown before the wizard asks to pull it.
RECOMMENDED_MODEL_SIZE_GB: Optional[float] = None

# Model time limit in milliseconds, set from the bake-off's measured latency.
RECOMMENDED_BUDGET_MS: int = 2500
