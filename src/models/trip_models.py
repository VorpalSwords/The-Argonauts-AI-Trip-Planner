"""
Data models for the Trip Planner Agent system.
Defines all the structured data types used across agents.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date
from enum import Enum


class BudgetLevel(str, Enum):
    """Budget level for the trip"""
    BUDGET = "budget"
    MID_RANGE = "mid-range"
    LUXURY = "luxury"


class TripDates(BaseModel):
    """Trip date range"""
    start_date: str = Field(..., description="Trip start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="Trip end date (YYYY-MM-DD)")
    
    @property
    def duration_days(self) -> int:
        """Calculate number of days in the trip"""
        from datetime import datetime
        start = datetime.fromisoformat(self.start_date)
        end = datetime.fromisoformat(self.end_date)
        return (end - start).days + 1


class TripPreferences(BaseModel):
    """User preferences for the trip"""
    interests: List[str] = Field(
        default_factory=list,
        description="User's interests (e.g., temples, food, nature, shopping)"
    )
    pace_preference: str = Field(
        default="moderate",
        description="Travel pace: relaxed, moderate, fast-paced"
    )
    budget_level: str = Field(
        default="mid-range",
        description="Budget level: budget, mid-range, luxury"
    )
    dietary_restrictions: List[str] = Field(
        default_factory=list,
        description="Any dietary restrictions"
    )
    special_requests: Optional[str] = Field(
        default=None,
        description="Any special requests or considerations"
    )


class TripInput(BaseModel):
    """Input from user for trip planning - Capstone version"""
    destination: str = Field(..., description="Primary destination")
    dates: TripDates = Field(..., description="Trip dates")
    preferences: TripPreferences = Field(
        default_factory=TripPreferences,
        description="User preferences"
    )
    
    # Optional fields
    additional_destinations: Optional[List[str]] = Field(
        default=None,
        description="Additional cities/locations to visit"
    )
    reference_files: Optional[List[str]] = Field(
        default=None,
        description="Paths to reference files (friend's itineraries)"
    )


class DayActivity(BaseModel):
    """A single activity in the itinerary"""
    time: str = Field(..., description="Time of activity (e.g., '9:00 AM')")
    activity: str = Field(..., description="Activity description")
    location: str = Field(..., description="Location name")
    duration: str = Field(..., description="Estimated duration")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    estimated_cost: Optional[str] = Field(default=None, description="Estimated cost")


class DayPlan(BaseModel):
    """Plan for a single day - Capstone version"""
    day_number: int
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    title: str = Field(default="", description="Title for the day")
    
    # Activities by time of day
    morning_activities: List[str] = Field(default_factory=list, description="Morning activities")
    afternoon_activities: List[str] = Field(default_factory=list, description="Afternoon activities")
    evening_activities: List[str] = Field(default_factory=list, description="Evening activities")
    
    # Meals
    meals: Dict[str, str] = Field(
        default_factory=dict,
        description="Meal recommendations (breakfast, lunch, dinner)"
    )
    
    # Cost and notes
    estimated_cost: float = Field(default=0.0, description="Estimated cost for the day")
    notes: List[str] = Field(default_factory=list, description="Additional notes and tips")
    
    # Legacy fields for backward compatibility
    location: Optional[str] = Field(default=None, description="Primary location for the day")
    theme: Optional[str] = Field(default=None, description="Theme of the day")
    activities: List[DayActivity] = Field(default_factory=list)
    accommodation: Optional[str] = Field(default=None, description="Where to stay")
    transportation_notes: Optional[str] = Field(default=None, description="Transportation notes")


class WeatherInfo(BaseModel):
    """Weather information for the trip"""
    average_temp_celsius: str
    conditions: str
    recommendations: List[str] = Field(default_factory=list)
    season_notes: Optional[str] = None


class ResearchData(BaseModel):
    """Compiled research about the destination - Capstone version"""
    destination: str
    research_summary: str = Field(default="", description="Comprehensive research summary")
    
    # Key findings
    attractions: List[str] = Field(default_factory=list, description="Top attractions")
    activities: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Activities by category (cultural, outdoor, food, etc.)"
    )
    weather_summary: str = Field(default="", description="Weather information")
    travel_tips: List[str] = Field(default_factory=list, description="Travel tips")
    estimated_costs: Dict[str, float] = Field(
        default_factory=dict,
        description="Cost estimates (accommodation_per_night, food_per_day, etc.)"
    )
    best_time_to_visit: str = Field(default="", description="Best time to visit")
    safety_tips: List[str] = Field(default_factory=list, description="Safety information")
    
    # Legacy fields for backward compatibility
    weather_info: Optional[WeatherInfo] = None
    top_attractions: List[str] = Field(default_factory=list)
    local_tips: List[str] = Field(default_factory=list)
    tourist_level: str = Field(default="moderate")
    special_events: List[str] = Field(default_factory=list)
    transportation_info: Optional[str] = None
    cultural_notes: List[str] = Field(default_factory=list)
    food_recommendations: List[str] = Field(default_factory=list)


class TripItinerary(BaseModel):
    """Complete trip itinerary - Capstone version"""
    destination: str
    start_date: str
    end_date: str
    duration_days: int
    
    # Daily plans
    day_plans: List[DayPlan] = Field(default_factory=list)
    
    # Cost and logistics
    total_estimated_cost: float = Field(default=0.0, description="Total estimated cost")
    
    # Additional information
    generated_itinerary: str = Field(default="", description="Full generated itinerary text")
    packing_list: List[str] = Field(default_factory=list, description="Packing recommendations")
    important_notes: List[str] = Field(default_factory=list, description="Important notes")
    
    # Legacy fields for backward compatibility
    trip_input: Optional[TripInput] = None
    research_summary: Optional[ResearchData] = None
    general_tips: List[str] = Field(default_factory=list)
    version: int = Field(default=1, description="Iteration version")


class ReviewFeedback(BaseModel):
    """Feedback from review agent"""
    overall_quality: int = Field(..., ge=1, le=10, description="Quality score 1-10")
    strengths: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    approved: bool = Field(default=False)


class ReviewResult(BaseModel):
    """Result from review agent - Capstone version"""
    approved: bool = Field(default=False, description="Whether the itinerary is approved")
    quality_score: float = Field(default=7.0, ge=0, le=10, description="Quality score 0-10")
    issues_found: List[str] = Field(default_factory=list, description="List of issues identified")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    review_summary: str = Field(default="", description="Full review text")
    iteration_number: int = Field(default=1, description="Which iteration this is")

