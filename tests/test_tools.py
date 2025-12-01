"""
Tests for tool functionality.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.file_parser import parse_reference_files, create_reference_context
from src.tools.export_formats import ItineraryExporter
from tools.weather_api import WeatherAPI
from models.trip_models import TripInput, TripDates, TripPreferences, TripItinerary, DayPlan


class TestFileParser:
    """Test file parsing functionality"""
    
    def test_parse_reference_files_with_text(self):
        """Test parsing text files"""
        # Create a temporary text file
        test_file = Path("test_temp.txt")
        test_content = "This is a test file\nWith multiple lines\nFor testing"
        
        try:
            test_file.write_text(test_content)
            results = parse_reference_files([str(test_file)])
            
            assert len(results) == 1
            # FileParser returns: file_name, file_type, content, links, destinations, dates, costs, activities
            assert "file_name" in results[0]
            assert "content" in results[0]
            assert "This is a test file" in results[0]["content"]
        finally:
            if test_file.exists():
                test_file.unlink()
    
    def test_parse_nonexistent_file(self):
        """Test handling of nonexistent files"""
        results = parse_reference_files(["nonexistent_file_xyz123.txt"])
        
        assert len(results) == 1
        # FileParser returns error key for nonexistent files
        assert "error" in results[0]
        assert "not found" in results[0]["error"].lower()
    
    def test_parse_empty_list(self):
        """Test handling empty file list"""
        results = parse_reference_files([])
        assert results == []
    
    def test_create_reference_context(self):
        """Test creating reference context from parsed files"""
        parsed_files = [
            {
                "file_path": "test1.txt",
                "content": "Content from file 1",
                "status": "success",
                "type": "txt"
            },
            {
                "file_path": "test2.txt",
                "content": "Content from file 2",
                "status": "success",
                "type": "txt"
            }
        ]
        
        context = create_reference_context(parsed_files)
        
        assert isinstance(context, str)
        assert len(context) > 0
        # Context should contain file info
        assert "test1.txt" in context or "Content from file 1" in context


class TestExportFormats:
    """Test export format functionality"""
    
    def setup_method(self):
        """Create sample itinerary for testing"""
        self.itinerary = TripItinerary(
            trip_input=TripInput(
                destination="Tokyo",
                dates=TripDates(start_date="2026-04-01", end_date="2026-04-05"),
                preferences=TripPreferences(interests=["food", "culture"])
            ),
            destination="Tokyo",
            start_date="2026-04-01",
            end_date="2026-04-05",
            duration_days=5,
            day_plans=[
                DayPlan(
                    day_number=1,
                    date="2026-04-01",
                    title="Day 1: Arrival",
                    morning_activities=["Check in hotel"],
                    afternoon_activities=["Explore neighborhood"],
                    evening_activities=["Dinner"],
                    meals={"dinner": "Local ramen"},
                    estimated_cost=100.0
                )
            ],
            generated_itinerary="Test itinerary content",
            total_estimated_cost=1500.0
        )
    
    def test_export_to_json(self):
        """Test JSON export"""
        json_str = ItineraryExporter.to_json(self.itinerary)
        
        assert isinstance(json_str, str)
        assert "Tokyo" in json_str
        assert "2026-04-01" in json_str
        assert len(json_str) > 100
    
    def test_export_to_plain_text(self):
        """Test plain text export"""
        text = ItineraryExporter.to_plain_text(self.itinerary)
        
        assert isinstance(text, str)
        assert "Tokyo" in text
        assert "Day 1" in text or "itinerary" in text.lower()
        assert len(text) > 50
    
    def test_export_module_has_functions(self):
        """Test that export module has expected functions"""
        assert hasattr(ItineraryExporter, 'to_json')
        assert hasattr(ItineraryExporter, 'to_plain_text')
        assert hasattr(ItineraryExporter, 'to_markdown')
        assert callable(ItineraryExporter.to_json)
        assert callable(ItineraryExporter.to_plain_text)


class TestWeatherAPI:
    """Test weather API functionality"""
    
    def test_weather_api_initialization(self):
        """Test that WeatherAPI can be initialized"""
        api = WeatherAPI()
        assert api is not None
    
    def test_weather_response_structure(self):
        """Test that weather response has correct structure"""
        api = WeatherAPI()
        result = api.get_weather("Tokyo", "2026-04-01", "2026-04-05")
        
        assert isinstance(result, dict)
        # Should have these keys even if using fallback
        assert "destination" in result or "error" in result or "period" in result
    
    def test_weather_handles_invalid_dates(self):
        """Test weather API handles invalid dates gracefully"""
        api = WeatherAPI()
        
        # Should not crash, should return some response
        result = api.get_weather("Tokyo", "invalid-date", "2026-04-05")
        assert isinstance(result, dict)


class TestModelHelpers:
    """Test model helper utilities"""
    
    def test_trip_dates_duration_calculation(self):
        """Test that trip duration is calculated correctly"""
        dates = TripDates(
            start_date="2026-04-01",
            end_date="2026-04-10"
        )
        
        assert dates.duration_days == 10
    
    def test_trip_dates_validation(self):
        """Test trip date validation"""
        # Valid dates
        dates = TripDates(start_date="2026-04-01", end_date="2026-04-10")
        assert dates.duration_days > 0
        
        # Single day trip
        single_day = TripDates(start_date="2026-04-01", end_date="2026-04-01")
        assert single_day.duration_days == 1
    
    def test_trip_input_with_all_fields(self):
        """Test TripInput with all optional fields"""
        trip = TripInput(
            destination="Tokyo, Japan",
            dates=TripDates(start_date="2026-04-01", end_date="2026-04-05"),
            preferences=TripPreferences(
                budget_level="luxury",
                interests=["food", "culture", "temples"],
                dietary_restrictions=["vegetarian", "no spicy"],
                pace_preference="relaxed"
            ),
            additional_destinations=["Kyoto", "Osaka"],
            reference_files=["trip1.txt", "trip2.pdf"]
        )
        
        assert trip.destination == "Tokyo, Japan"
        assert len(trip.preferences.interests) == 3
        assert len(trip.preferences.dietary_restrictions) == 2
        assert len(trip.additional_destinations) == 2
        assert len(trip.reference_files) == 2
    
    def test_day_plan_structure(self):
        """Test DayPlan model structure"""
        day = DayPlan(
            day_number=1,
            date="2026-04-01",
            title="Day 1 in Tokyo",
            morning_activities=["Activity 1", "Activity 2"],
            afternoon_activities=["Activity 3"],
            evening_activities=["Activity 4"],
            meals={"breakfast": "Hotel", "lunch": "Sushi", "dinner": "Ramen"},
            estimated_cost=150.0,
            notes=["Book in advance", "Bring umbrella"]
        )
        
        assert day.day_number == 1
        assert len(day.morning_activities) == 2
        assert len(day.afternoon_activities) == 1
        assert len(day.evening_activities) == 1
        assert len(day.meals) == 3
        assert day.estimated_cost == 150.0
        assert len(day.notes) == 2

