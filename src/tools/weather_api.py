"""
Real-time weather API integration with fallback to model knowledge.
Uses OpenWeatherMap API when available, falls back gracefully when not.
"""

import requests
from datetime import date, datetime, timedelta
from typing import Dict, Any, Optional
from src.config import Config
from src.tools.weather_tool import WeatherTool


class WeatherAPI:
    """
    Weather information provider with API and fallback support.
    
    If OPENWEATHER_API_KEY is set, uses real-time weather data.
    Otherwise falls back to seasonal knowledge from WeatherTool.
    """
    
    BASE_URL = "http://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        self.api_key = Config.OPENWEATHER_API_KEY
        self.fallback = WeatherTool()
        self.has_api = bool(self.api_key)
    
    def get_weather(
        self,
        destination: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Get weather information for destination and dates.
        
        Tries API first, falls back to seasonal knowledge on error.
        
        Args:
            destination: Destination city
            start_date: Trip start date
            end_date: Trip end date
            
        Returns:
            Weather information dictionary with source indicator
        """
        if not self.has_api:
            # No API key, use fallback
            result = self.fallback.get_weather(destination, start_date, end_date)
            result["source"] = "AI Knowledge (No API key provided)"
            result["note"] = "Using seasonal patterns from training data. For real-time weather, add OPENWEATHER_API_KEY to .env"
            return result
        
        try:
            # Try to get real-time forecast
            weather_data = self._fetch_forecast(destination, start_date, end_date)
            weather_data["source"] = "OpenWeatherMap API (Real-time)"
            return weather_data
        
        except Exception as e:
            # API failed, use fallback
            print(f"⚠️  Weather API error: {e}. Using AI knowledge fallback.")
            result = self.fallback.get_weather(destination, start_date, end_date)
            result["source"] = "AI Knowledge (API error)"
            result["note"] = f"Weather API unavailable. Using seasonal patterns."
            return result
    
    def _fetch_forecast(
        self,
        destination: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Fetch weather forecast from OpenWeatherMap API.
        
        Uses the 5-day/3-hour forecast API (free tier).
        """
        # Get coordinates first (geocoding)
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct"
        geo_params = {
            "q": destination,
            "limit": 1,
            "appid": self.api_key
        }
        
        geo_response = requests.get(geo_url, params=geo_params, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()
        
        if not geo_data:
            raise ValueError(f"Location not found: {destination}")
        
        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]
        
        # Get forecast
        forecast_url = f"{self.BASE_URL}/forecast"
        forecast_params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric"  # Celsius
        }
        
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        
        # Process forecast for date range
        return self._process_forecast(
            forecast_data,
            destination,
            start_date,
            end_date
        )
    
    def _process_forecast(
        self,
        forecast_data: Dict,
        destination: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Process API forecast data into usable format."""
        # Ensure dates are date objects
        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)
        
        forecasts_by_date = {}
        
        for item in forecast_data.get("list", []):
            dt = datetime.fromtimestamp(item["dt"]).date()
            
            # Only include dates in our range
            if start_date <= dt <= end_date:
                if dt not in forecasts_by_date:
                    forecasts_by_date[dt] = []
                
                forecasts_by_date[dt].append({
                    "temp": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "temp_min": item["main"]["temp_min"],
                    "temp_max": item["main"]["temp_max"],
                    "humidity": item["main"]["humidity"],
                    "weather": item["weather"][0]["description"],
                    "rain_probability": item.get("pop", 0) * 100,  # Probability of precipitation
                    "wind_speed": item["wind"]["speed"]
                })
        
        # Calculate daily summaries
        daily_summaries = []
        for dt, forecasts in sorted(forecasts_by_date.items()):
            if not forecasts:  # Skip if no forecast data for this date
                continue
            
            temps = [f["temp"] for f in forecasts]
            avg_temp = sum(temps) / len(temps) if temps else 0
            min_temp = min(f["temp_min"] for f in forecasts) if forecasts else 0
            max_temp = max(f["temp_max"] for f in forecasts) if forecasts else 0
            rain_prob = max(f["rain_probability"] for f in forecasts) if forecasts else 0
            
            # Most common weather condition
            conditions = [f["weather"] for f in forecasts]
            main_condition = max(set(conditions), key=conditions.count)
            
            daily_summaries.append({
                "date": dt.strftime("%Y-%m-%d"),
                "avg_temp": f"{avg_temp:.1f}°C",
                "temp_range": f"{min_temp:.1f}°C - {max_temp:.1f}°C",
                "conditions": main_condition,
                "rain_probability": f"{rain_prob:.0f}%"
            })
        
        # Generate recommendations
        recommendations = self._generate_recommendations(daily_summaries)
        
        # Calculate average for summary
        all_temps = [float(d["avg_temp"].replace("°C", "")) for d in daily_summaries]
        avg_temp_overall = sum(all_temps) / len(all_temps) if all_temps and len(all_temps) > 0 else 0
        
        return {
            "destination": destination,
            "period": f"{start_date.strftime('%B %d')} to {end_date.strftime('%B %d, %Y')}",
            "average_temp_celsius": f"{avg_temp_overall:.1f}°C",
            "conditions": f"Varied - see daily forecast",
            "daily_forecast": daily_summaries,
            "recommendations": recommendations
        }
    
    def _generate_recommendations(self, daily_summaries: list) -> list:
        """Generate packing and planning recommendations from forecast."""
        recommendations = []
        
        # Check if we have any data
        if not daily_summaries or len(daily_summaries) == 0:
            recommendations.append("Check local forecast closer to travel date")
            return recommendations
        
        # Temperature-based
        temps = [float(d["avg_temp"].replace("°C", "")) for d in daily_summaries]
        avg_temp = sum(temps) / len(temps) if temps else 15  # Default to mild temp
        
        if avg_temp < 10:
            recommendations.append("Pack warm layers, jacket, and gloves")
        elif avg_temp < 20:
            recommendations.append("Bring light jacket and layers for variable weather")
        else:
            recommendations.append("Light, breathable clothing recommended")
        
        # Rain-based
        max_rain = max(
            float(d["rain_probability"].replace("%", "")) 
            for d in daily_summaries
        )
        
        if max_rain > 50:
            recommendations.append("High chance of rain - bring umbrella and waterproof jacket")
        elif max_rain > 30:
            recommendations.append("Pack a compact umbrella just in case")
        
        # Planning recommendations
        recommendations.append("Check forecast day before for any changes")
        recommendations.append("Plan indoor activities for rainy days")
        recommendations.append("Comfortable walking shoes essential")
        
        return recommendations[:6]

