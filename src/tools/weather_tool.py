"""
Weather information tool for trip planning.
Provides seasonal information and weather forecasts.
"""

from typing import Dict
from datetime import date
import requests
from src.config import Config


class WeatherTool:
    """Tool for fetching weather information"""
    
    def __init__(self):
        self.name = "get_weather_info"
        self.description = (
            "Gets weather forecast and seasonal information for a destination. "
            "Provides temperature ranges, typical conditions, and packing recommendations."
        )
        self.api_key = Config.OPENWEATHER_API_KEY
    
    def get_seasonal_info(self, destination: str, month: int) -> Dict[str, any]:
        """
        Get seasonal information for a destination.
        This is a knowledge-based fallback when API is not available.
        """
        
        # Seasonal data for common destinations (fallback knowledge base)
        seasonal_data = {
            "tokyo": {
                1: {"temp": "5-10°C", "conditions": "Cold, clear skies", "season": "Winter"},
                2: {"temp": "5-12°C", "conditions": "Cold, occasional snow", "season": "Winter"},
                3: {"temp": "10-15°C", "conditions": "Mild, cherry blossom season begins", "season": "Spring"},
                4: {"temp": "14-20°C", "conditions": "Pleasant spring weather, cherry blossoms", "season": "Spring"},
                5: {"temp": "18-24°C", "conditions": "Warm, occasional rain", "season": "Spring/Summer"},
                6: {"temp": "21-27°C", "conditions": "Humid, rainy season begins", "season": "Summer"},
                7: {"temp": "25-31°C", "conditions": "Hot and humid", "season": "Summer"},
                8: {"temp": "26-31°C", "conditions": "Very hot and humid", "season": "Summer"},
                9: {"temp": "22-27°C", "conditions": "Warm, typhoon season", "season": "Fall"},
                10: {"temp": "17-22°C", "conditions": "Pleasant, clear skies", "season": "Fall"},
                11: {"temp": "12-17°C", "conditions": "Cool, fall foliage", "season": "Fall"},
                12: {"temp": "7-12°C", "conditions": "Cold, dry", "season": "Winter"},
            },
            "kyoto": {
                3: {"temp": "8-14°C", "conditions": "Mild, cherry blossom season", "season": "Spring"},
                4: {"temp": "13-20°C", "conditions": "Pleasant, peak cherry blossoms", "season": "Spring"},
                11: {"temp": "10-17°C", "conditions": "Cool, stunning fall foliage", "season": "Fall"},
            },
            "osaka": {
                3: {"temp": "9-15°C", "conditions": "Mild spring weather", "season": "Spring"},
                4: {"temp": "14-21°C", "conditions": "Pleasant, cherry blossoms", "season": "Spring"},
            }
        }
        
        dest_lower = destination.lower()
        
        # Try to find specific data
        if dest_lower in seasonal_data and month in seasonal_data[dest_lower]:
            return seasonal_data[dest_lower][month]
        
        # Try Tokyo as default for Japan
        if "japan" in dest_lower and month in seasonal_data["tokyo"]:
            return seasonal_data["tokyo"][month]
        
        # Generic fallback
        seasons = {
            (12, 1, 2): {"temp": "Variable", "conditions": "Winter", "season": "Winter"},
            (3, 4, 5): {"temp": "Variable", "conditions": "Spring", "season": "Spring"},
            (6, 7, 8): {"temp": "Variable", "conditions": "Summer", "season": "Summer"},
            (9, 10, 11): {"temp": "Variable", "conditions": "Fall/Autumn", "season": "Fall"},
        }
        
        for months, info in seasons.items():
            if month in months:
                return info
        
        return {"temp": "Variable", "conditions": "Check local forecast", "season": "Unknown"}
    
    def get_weather(
        self, 
        destination: str, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, any]:
        """
        Get weather information for destination and dates.
        
        Args:
            destination: Destination city or country
            start_date: Trip start date
            end_date: Trip end date
            
        Returns:
            Dictionary with weather information and recommendations
        """
        month = start_date.month
        seasonal_info = self.get_seasonal_info(destination, month)
        
        # Generate recommendations based on season and destination
        recommendations = []
        
        temp_lower = seasonal_info.get("temp", "").lower()
        conditions_lower = seasonal_info.get("conditions", "").lower()
        
        # Temperature-based recommendations
        if "cold" in temp_lower or "cold" in conditions_lower or month in [12, 1, 2]:
            recommendations.extend([
                "Pack warm layers and a winter jacket",
                "Bring gloves and scarf for cold weather",
                "Indoor attractions are popular - book ahead"
            ])
        elif "hot" in temp_lower or "hot" in conditions_lower:
            recommendations.extend([
                "Light, breathable clothing recommended",
                "Sunscreen and hat essential",
                "Stay hydrated in hot weather",
                "Consider indoor activities during peak heat"
            ])
        else:
            recommendations.append("Comfortable layers recommended for varying temperatures")
        
        # Condition-based recommendations
        if "rain" in conditions_lower or month in [6, 7]:
            recommendations.append("Pack umbrella - rainy season")
        
        if "cherry blossom" in conditions_lower or (destination.lower() in ["tokyo", "kyoto", "japan"] and month in [3, 4]):
            recommendations.extend([
                "Cherry blossom season - book accommodations early",
                "Popular hanami spots will be crowded",
                "Perfect time for outdoor photography"
            ])
        
        if "fall foliage" in conditions_lower or "autumn" in conditions_lower:
            recommendations.append("Beautiful fall colors - great for photography")
        
        # General recommendations
        recommendations.append("Check weather forecast closer to departure")
        recommendations.append("Comfortable walking shoes essential for sightseeing")
        
        return {
            "destination": destination,
            "period": f"{start_date.strftime('%B %d')} to {end_date.strftime('%B %d, %Y')}",
            "average_temp_celsius": seasonal_info.get("temp", "Variable"),
            "conditions": seasonal_info.get("conditions", "Seasonal"),
            "season": seasonal_info.get("season", ""),
            "recommendations": recommendations[:6]  # Top 6 recommendations
        }
    
    def get_tool_spec(self) -> Dict:
        """Get tool specification for agent framework"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {
                        "type": "string",
                        "description": "Destination city or country"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Trip start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Trip end date (YYYY-MM-DD)"
                    }
                },
                "required": ["destination", "start_date", "end_date"]
            }
        }

