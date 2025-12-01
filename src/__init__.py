"""
Trip Planner Agent System - Capstone Project

Google AI Agents Intensive Course (November 2025)

A production-ready multi-agent system for intelligent trip planning
using Google's Agent Development Kit (ADK).
"""

__version__ = "2.0.0-capstone"
__author__ = "Liad C."
__course__ = "Google AI Agents Intensive - November 2025"

# Capstone agents
from .agents.orchestrator_capstone import OrchestratorAgentCapstone as OrchestratorAgent
from .agents.research_agent_capstone import ResearchAgentCapstone as ResearchAgent
from .agents.planning_agent_capstone import PlanningAgentCapstone as PlanningAgent
from .agents.review_agent_capstone import ReviewAgentCapstone as ReviewAgent

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
    'ResearchAgent',
    'PlanningAgent',
    'ReviewAgent',
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
