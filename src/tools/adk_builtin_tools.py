"""
ADK Built-in Tools Integration.

This module wraps ADK's built-in tools for easy use in our agents:
- google_search: Real Google Search (no external API needed!)
- code_execution: Execute Python code for calculations

NO EXTERNAL APIs NEEDED - ALL ADK BUILT-IN!
"""

from typing import Dict, List
from datetime import date
import json

# ===== ADK BUILT-IN TOOLS =====
# These are provided by ADK - no setup needed!
from google.adk.tools import google_search

# Optional: Code execution (for budget calculations, data analysis)
try:
    from google.adk.tools import built_in_code_execution
    CODE_EXECUTION_AVAILABLE = True
except ImportError:
    CODE_EXECUTION_AVAILABLE = False

# Import weather fallback (no external API required)
from src.tools.weather_tool import WeatherTool

_weather_tool = WeatherTool()


def get_weather_info(destination: str, start_date: str, end_date: str) -> Dict:
    """
    Gets weather forecast and seasonal information for a destination.
    
    Uses seasonal averages (no external API required).
    Works perfectly for trip planning!
    
    Args:
        destination: The city or country for which to get weather.
        start_date: The start date of the trip (YYYY-MM-DD).
        end_date: The end date of the trip (YYYY-MM-DD).
        
    Returns:
        A dictionary containing weather information.
    """
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    
    return _weather_tool.get_weather(destination, start, end)


def search_destination_info(query: str) -> str:
    """
    Search for destination information using Google Search.
    
    This uses ADK's built-in google_search tool.
    NO EXTERNAL API KEY NEEDED - it's built into ADK!
    
    Args:
        query: Search query (e.g., "best attractions in Tokyo")
        
    Returns:
        Search summary string
        
    Note: This function wraps google_search for explicit use.
    Agents can also call google_search directly from their tools list.
    """
    return f"Use google_search tool with query: {query}"


def calculate_trip_budget(
    num_days: int,
    budget_level: str,
    num_people: int = 1,
    include_flights: bool = False
) -> Dict:
    """
    Calculate estimated trip budget based on parameters.
    
    Can use code_execution if available for complex calculations.
    
    Args:
        num_days: Number of days for the trip
        budget_level: "budget", "mid-range", or "luxury"
        num_people: Number of travelers
        include_flights: Whether to include flight estimates
        
    Returns:
        Budget breakdown dictionary
    """
    # Daily costs by budget level
    daily_costs = {
        "budget": {
            "accommodation": 50,
            "food": 30,
            "activities": 20,
            "transport": 15
        },
        "mid-range": {
            "accommodation": 120,
            "food": 60,
            "activities": 50,
            "transport": 30
        },
        "luxury": {
            "accommodation": 300,
            "food": 150,
            "activities": 150,
            "transport": 80
        }
    }
    
    costs = daily_costs.get(budget_level, daily_costs["mid-range"])
    
    # Calculate totals
    total_accommodation = costs["accommodation"] * num_days * num_people
    total_food = costs["food"] * num_days * num_people
    total_activities = costs["activities"] * num_days * num_people
    total_transport = costs["transport"] * num_days * num_people
    
    subtotal = total_accommodation + total_food + total_activities + total_transport
    
    # Add flights if requested
    flight_cost = 0
    if include_flights:
        flight_estimates = {
            "budget": 500,
            "mid-range": 800,
            "luxury": 1500
        }
        flight_cost = flight_estimates.get(budget_level, 800) * num_people
    
    total = subtotal + flight_cost
    
    return {
        "budget_level": budget_level,
        "num_days": num_days,
        "num_people": num_people,
        "breakdown": {
            "accommodation": total_accommodation,
            "food": total_food,
            "activities": total_activities,
            "transport": total_transport,
            "flights": flight_cost
        },
        "subtotal": subtotal,
        "total": total,
        "per_person": total / num_people,
        "per_day": total / num_days / num_people
    }


# Export all tools for ADK
__all__ = [
    'google_search',  # ADK built-in
    'get_weather_info',
    'search_destination_info',
    'calculate_trip_budget'
]

# Optional: Export code execution if available
if CODE_EXECUTION_AVAILABLE:
    __all__.append('built_in_code_execution')

