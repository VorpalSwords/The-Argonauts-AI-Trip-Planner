"""
Pro Agents - Optimized for gemini-2.5-flash, gemini-1.5-pro, gemini-2.0-flash-exp

These agents use:
- Detailed instructions (~300-500 lines)
- Abstract reasoning + concrete examples
- Higher complexity
- Strict thresholds (8/10 approval)
- Max 5 iterations
- Comprehensive feedback
"""

from .research_agent import ResearchAgentPro
from .planning_agent import PlanningAgentPro
from .review_agent import ReviewAgentPro

__all__ = ['ResearchAgentPro', 'PlanningAgentPro', 'ReviewAgentPro']

