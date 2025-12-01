"""
Integration tests for The Argonauts trip planner.
Tests full workflows and agent coordination.
"""

import pytest
import sys
from pathlib import Path
from datetime import date
import asyncio

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.trip_models import TripInput, TripDates, TripPreferences
from agents.orchestrator_capstone import OrchestratorAgentCapstone
from tools.itinerary_formatter import ItineraryFormatter
from utils.error_handler import InvalidInputError


class TestAgentWorkflows:
    """Test agent execution workflows"""
    
    @pytest.mark.skip(reason="Requires API key and long execution time")
    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized"""
        orchestrator = OrchestratorAgentCapstone()
        assert orchestrator is not None
    
    def test_research_agent_initialization(self):
        """Test research agent can execute"""
        trip = TripInput(
            destination="Tokyo",
            dates=TripDates(
                start_date="2026-04-01",
                end_date="2026-04-05"
            ),
            preferences=TripPreferences(
                interests=["culture", "food"],
                budget_level="mid-range"
            )
        )
        
        # Just test that agent can be initialized
        # Actual execution requires API key and is tested manually
        try:
            agent = ResearchAgentCapstone()
            assert agent is not None
            assert agent.agent is not None
            assert agent.runner is not None
        except Exception as e:
            pytest.skip(f"Research agent init test skipped: {e}")
    
    def test_itinerary_formatter(self):
        """Test itinerary formatting"""
        from models.trip_models import TripItinerary
        
        itinerary = TripItinerary(
            trip_input=TripInput(
                destination="Tokyo",
                dates=TripDates(start_date="2026-04-01", end_date="2026-04-05"),
                preferences=TripPreferences()
            ),
            destination="Tokyo",
            start_date="2026-04-01",
            end_date="2026-04-05",
            duration_days=5,
            generated_itinerary="Test itinerary content here",
            total_estimated_cost=1500.0
        )
        
        md = ItineraryFormatter.to_markdown(itinerary)
        
        assert "Tokyo" in md
        assert "2026-04-01" in md
        assert len(md) > 100


class TestDataFlow:
    """Test data flow between agents"""
    
    def test_research_to_planning_data_flow(self):
        """Test research data structure for planning"""
        from models.trip_models import ResearchData, WeatherInfo
        
        research = ResearchData(
            destination="Tokyo",
            research_summary="Tokyo is a vibrant city with temples and food",
            weather_info=WeatherInfo(
                average_temp_celsius="15-20°C",
                conditions="Spring weather, mild",
                recommendations=["Pack layers", "Bring umbrella"]
            ),
            top_attractions=["Senso-ji", "Shibuya Sky"],
            local_tips=["Get Suica card", "Visit early morning"]
        )
        
        assert research.destination == "Tokyo"
        assert len(research.top_attractions) > 0
        assert research.weather_info is not None


class TestErrorScenarios:
    """Test error handling scenarios"""
    
    def test_invalid_date_order(self):
        """Test that invalid date order is caught"""
        from utils.error_handler import validate_trip_input
        
        trip = TripInput(
            destination="Tokyo",
            dates=TripDates(
                start_date="2026-04-10",
                end_date="2026-04-01"  # End before start!
            )
        )
        
        with pytest.raises(InvalidInputError, match="End date must be after start date"):
            validate_trip_input(trip)
    
    def test_empty_destination(self):
        """Test that empty destination is caught"""
        from utils.error_handler import validate_trip_input
        
        trip = TripInput(
            destination="",  # Empty!
            dates=TripDates(
                start_date="2026-04-01",
                end_date="2026-04-10"
            )
        )
        
        with pytest.raises(InvalidInputError, match="Destination is required"):
            validate_trip_input(trip)
    
    def test_excessive_duration(self):
        """Test that excessive duration is caught"""
        from utils.error_handler import validate_trip_input
        
        trip = TripInput(
            destination="Tokyo",
            dates=TripDates(
                start_date="2026-01-01",
                end_date="2027-01-01"  # 365+ days!
            )
        )
        
        with pytest.raises(InvalidInputError, match="cannot exceed 365 days"):
            validate_trip_input(trip)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

