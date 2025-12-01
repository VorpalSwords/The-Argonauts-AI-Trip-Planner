"""
Lite Agents - Optimized for gemini-2.5-flash-lite

These agents use:
- Simplified instructions (~100-150 lines)
- Concrete examples (BAD vs GOOD)
- Lower complexity
- Realistic thresholds (7/10 approval)
- Max 3 iterations
"""

from .research_agent import ResearchAgentLite
from .planning_agent import PlanningAgentLite
from .review_agent import ReviewAgentLite

__all__ = ['ResearchAgentLite', 'PlanningAgentLite', 'ReviewAgentLite']

