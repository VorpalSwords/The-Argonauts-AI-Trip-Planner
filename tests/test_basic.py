"""
Basic tests for The Argonauts trip planner.
Run with: python3 -m pytest tests/
"""

import pytest
import sys
from pathlib import Path
from datetime import date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.trip_models import TripInput, TripDates, TripPreferences
from tools.maps_helper import MapsHelper
from tools.transport_helper import TransportHelper
from utils.error_handler import validate_trip_input, InvalidInputError


class TestModels:
    """Test data models"""
    
    def test_trip_dates_creation(self):
        """Test TripDates model"""
        dates = TripDates(
            start_date="2026-04-01",
            end_date="2026-04-10"
        )
        assert dates.duration_days == 10
    
    def test_trip_input_creation(self):
        """Test TripInput model"""
        trip = TripInput(
            destination="Tokyo",
            dates=TripDates(
                start_date="2026-04-01",
                end_date="2026-04-10"
            ),
            preferences=TripPreferences(
                interests=["culture", "food"],
                budget_level="mid-range"
            )
        )
        assert trip.destination == "Tokyo"
        assert trip.dates.duration_days == 10


class TestMapsHelper:
    """Test Google Maps helper"""
    
    def test_search_url_generation(self):
        """Test Maps search URL"""
        url = MapsHelper.search_url("Senso-ji Temple", "Tokyo")
        assert "google.com/maps" in url
        assert "Senso-ji" in url or "Senso%20ji" in url or "Senso-ji" in url
    
    def test_directions_url(self):
        """Test directions URL"""
        url = MapsHelper.directions_url("Shinjuku", "Asakusa")
        assert "google.com/maps/dir" in url
        assert "origin=" in url
        assert "destination=" in url


class TestTransportHelper:
    """Test transportation helper"""
    
    def test_tokyo_transit_info(self):
        """Test Tokyo transit recommendations"""
        info = TransportHelper.get_transit_recommendations("Tokyo", 5)
        assert "passes" in info
        assert len(info["passes"]) > 0
        assert any("Suica" in p["name"] for p in info["passes"])
    
    def test_japan_overview(self):
        """Test multi-city Japan transit"""
        guide = TransportHelper.get_japan_transit_overview(["Tokyo", "Kyoto", "Osaka"])
        assert "JR Pass" in guide
        assert "Shinkansen" in guide
        assert "13,320" in guide or "13320" in guide  # Tokyo-Kyoto cost


class TestErrorHandling:
    """Test error handling"""
    
    def test_validate_valid_input(self):
        """Test validation passes for valid input"""
        trip = TripInput(
            destination="Tokyo",
            dates=TripDates(
                start_date="2026-04-01",
                end_date="2026-04-10"
            )
        )
        validate_trip_input(trip)  # Should not raise
    
    def test_validate_invalid_duration(self):
        """Test validation fails for invalid duration"""
        trip = TripInput(
            destination="Tokyo",
            dates=TripDates(
                start_date="2026-04-10",
                end_date="2026-04-01"  # End before start
            )
        )
        # Should raise InvalidInputError
        with pytest.raises(InvalidInputError):
            validate_trip_input(trip)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

