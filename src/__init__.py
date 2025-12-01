"""
Trip Planner Agent System - Capstone Project

Google AI Agents Intensive Course (November 2025)

A production-ready multi-agent system for intelligent trip planning
using Google's Agent Development Kit (ADK).
"""

__version__ = "2.0.0-capstone"
__author__ = "Liad C."
__course__ = "Google AI Agents Intensive - November 2025"

# Main orchestrator (auto-loads lite/pro agents based on model)
from .agents.orchestrator_capstone import OrchestratorAgentCapstone as OrchestratorAgent
from .agents.exploration_agent import ExplorationAgent

# Note: Individual agents (Research, Planning, Review) are dynamically loaded
# by the orchestrator based on model tier. See agents/README.md for details.

# Data models
from .models import TripInput, TripPreferences, TripItinerary, TripDates, DayPlan, ResearchData, ReviewResult

# Tools
from .tools.adk_builtin_tools import get_weather_info, calculate_trip_budget
from .tools.itinerary_formatter import ItineraryFormatter

# Evaluation
from .evaluation import TripPlannerEvaluator, evaluate_agent

__all__ = [
    # Agents
    'OrchestratorAgent',
    'ExplorationAgent',
    # Models
    'TripInput',
    'TripPreferences',
    'TripItinerary',
    'TripDates',
    'DayPlan',
    'ResearchData',
    'ReviewResult',
    # Tools
    'get_weather_info',
    'calculate_trip_budget',
    'ItineraryFormatter',
    # Evaluation
    'TripPlannerEvaluator',
    'evaluate_agent',
]
