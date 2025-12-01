"""Agent implementations for Trip Planner - Capstone ADK Framework"""

# Capstone agents (current implementation)
from .research_agent_capstone import ResearchAgentCapstone
from .planning_agent_capstone import PlanningAgentCapstone
from .review_agent_capstone import ReviewAgentCapstone
from .orchestrator_capstone import OrchestratorAgentCapstone

# Convenience aliases
ResearchAgent = ResearchAgentCapstone
PlanningAgent = PlanningAgentCapstone
ReviewAgent = ReviewAgentCapstone
OrchestratorAgent = OrchestratorAgentCapstone

__all__ = [
    'ResearchAgentCapstone',
    'PlanningAgentCapstone',
    'ReviewAgentCapstone',
    'OrchestratorAgentCapstone',
    'ResearchAgent',
    'PlanningAgent',
    'ReviewAgent',
    'OrchestratorAgent'
]
