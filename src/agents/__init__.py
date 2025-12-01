"""
Agents module - Model-aware multi-agent system

This module provides the orchestrator and model-specific agent implementations.
"""

# Main orchestrator (auto-loads appropriate agents based on model)
from .orchestrator_capstone import OrchestratorAgentCapstone

# Exploration agent
from .exploration_agent import ExplorationAgent

# Note: Individual agents (Research, Planning, Review) are NOT imported here
# They are dynamically loaded by the orchestrator based on model tier:
# - lite_agents/ for gemini-2.5-flash-lite
# - pro_agents/ for advanced models

__all__ = [
    'OrchestratorAgentCapstone',
    'ExplorationAgent'
]
