"""
Itinerary formatter tool for creating beautiful output.
Converts trip itinerary to markdown and other formats.
"""

from src.models.trip_models import TripItinerary, DayPlan
from typing import List


class ItineraryFormatter:
    """Formats itinerary for output in various formats"""
    
    @staticmethod
    def to_markdown(itinerary: TripItinerary) -> str:
        """
        Convert itinerary to markdown format.
        
        Args:
            itinerary: Complete trip itinerary
            
        Returns:
            Formatted markdown string
        """
        trip = itinerary.trip_input
        num_days = trip.dates.duration_days
        
        # Header
        md = f"# 🗺️ Trip Itinerary: {trip.destination}"
        if trip.additional_destinations:
            md += f" + {', '.join(trip.additional_destinations)}"
        md += "\n\n"
        
        # Trip Overview
        md += "## 📋 Trip Overview\n\n"
        md += f"- **Primary Destination**: {trip.destination}\n"
        
        if trip.additional_destinations:
            md += f"- **Also Visiting**: {', '.join(trip.additional_destinations)}\n"
        
        md += f"- **Dates**: {trip.dates.start_date} to {trip.dates.end_date}\n"
        md += f"- **Duration**: {num_days} days\n"
        md += f"- **Budget Level**: {trip.preferences.budget_level.title()}\n"
        md += f"- **Pace**: {trip.preferences.pace_preference.title()}\n"
        
        if trip.preferences.interests:
            md += f"- **Interests**: {', '.join(trip.preferences.interests)}\n"
        
        if trip.preferences.dietary_restrictions:
            md += f"- **Dietary Restrictions**: {', '.join(trip.preferences.dietary_restrictions)}\n"
        
        # Research Summary
        if itinerary.research_summary:
            research = itinerary.research_summary
            md += "\n## 🔍 Destination Insights\n\n"
            
            # Weather
            if research.weather_info:
                weather = research.weather_info
                md += "### 🌤️ Weather & Climate\n\n"
                md += f"- **Temperature**: {weather.average_temp_celsius}\n"
                md += f"- **Conditions**: {weather.conditions}\n"
                if weather.season_notes:
                    md += f"- **Season Notes**: {weather.season_notes}\n"
                if weather.recommendations:
                    md += "\n**Packing Recommendations:**\n"
                    for rec in weather.recommendations:
                        md += f"- {rec}\n"
                md += "\n"
            
            # Special Events
            if research.special_events:
                md += "### 🎉 Special Events\n\n"
                for event in research.special_events:
                    md += f"- {event}\n"
                md += "\n"
            
            # Top Attractions
            if research.top_attractions:
                md += "### ⭐ Top Attractions\n\n"
                for i, attraction in enumerate(research.top_attractions[:10], 1):
                    md += f"{i}. {attraction}\n"
                md += "\n"
            
            # Cultural Notes
            if research.cultural_notes:
                md += "### 🏮 Cultural Notes\n\n"
                for note in research.cultural_notes[:5]:
                    md += f"- {note}\n"
                md += "\n"
            
            # Transportation
            if research.transportation_info:
                md += "### 🚇 Transportation\n\n"
                md += f"{research.transportation_info}\n\n"
            
            # Local Tips
            if research.local_tips:
                md += "### 💡 Local Tips\n\n"
                for tip in research.local_tips[:8]:
                    md += f"- {tip}\n"
                md += "\n"
        
        # Daily Itinerary
        md += "## 📅 Daily Itinerary\n\n"
        
        # Use generated itinerary if available (contains LLM's actual response)
        if itinerary.generated_itinerary and len(itinerary.generated_itinerary.strip()) > 100:
            md += itinerary.generated_itinerary + "\n\n"
        else:
            # Fallback to structured day_plans
            for day in itinerary.day_plans:
                # Handle both string and datetime date objects
                from datetime import datetime
                if isinstance(day.date, str):
                    date_obj = datetime.fromisoformat(day.date)
                    date_str = date_obj.strftime('%A, %B %d, %Y')
                else:
                    date_str = day.date.strftime('%A, %B %d, %Y')
                md += f"### Day {day.day_number}: {date_str}"
                if day.theme:
                    md += f" - _{day.theme}_"
                md += f"\n\n**📍 Location**: {day.location}\n\n"
                
                # Activities
                if day.morning_activities or day.afternoon_activities or day.evening_activities:
                    md += "#### Activities\n\n"
                for activity in day.activities:
                    md += f"- **{activity.time}** | {activity.activity}\n"
                    md += f"  - 📍 Location: {activity.location}\n"
                    if activity.duration:
                        md += f"  - ⏱️ Duration: {activity.duration}\n"
                    if activity.estimated_cost:
                        md += f"  - 💰 Estimated Cost: {activity.estimated_cost}\n"
                    if activity.notes:
                        md += f"  - 📝 Notes: {activity.notes}\n"
                    md += "\n"
            
                # Meals
                if day.meals:
                    md += "#### 🍽️ Meals\n\n"
                    meal_emojis = {
                        "breakfast": "🥐",
                        "lunch": "🍱", 
                        "dinner": "🍜"
                    }
                    for meal_type, restaurant in day.meals.items():
                        emoji = meal_emojis.get(meal_type.lower(), "🍴")
                        md += f"- {emoji} **{meal_type.title()}**: {restaurant}\n"
                    md += "\n"
                
                # Accommodation
                if day.accommodation:
                    md += f"#### 🏨 Accommodation\n\n"
                    md += f"{day.accommodation}\n\n"
                
                # Transportation
                if day.transportation_notes:
                    md += f"#### 🚇 Transportation\n\n"
                    md += f"{day.transportation_notes}\n\n"
                
                # Daily cost estimate
                if day.estimated_cost:
                    md += f"**💰 Estimated Daily Cost**: {day.estimated_cost}\n\n"
                
                md += "---\n\n"
        
        # General Tips
        if itinerary.general_tips:
            md += "## 💡 General Travel Tips\n\n"
            for tip in itinerary.general_tips:
                md += f"- {tip}\n"
            md += "\n"
        
        # Food Recommendations
        if itinerary.research_summary and itinerary.research_summary.food_recommendations:
            md += "## 🍜 Must-Try Foods\n\n"
            for food in itinerary.research_summary.food_recommendations:
                md += f"- {food}\n"
            md += "\n"
        
        # Total Cost
        if itinerary.total_estimated_cost:
            md += "## 💰 Estimated Total Cost\n\n"
            md += f"${itinerary.total_estimated_cost:.2f}\n\n"
        
        # Footer
        md += "---\n\n"
        md += f"_✨ Itinerary version {itinerary.version} - Created by Trip Planner Agent_\n"
        md += f"_Generated with ❤️ using Gemini 2.0_\n"
        
        return md
    
    @staticmethod
    def to_plain_text(itinerary: TripItinerary) -> str:
        """
        Convert itinerary to plain text format.
        
        Args:
            itinerary: Complete trip itinerary
            
        Returns:
            Formatted plain text string
        """
        # Strip markdown formatting for plain text version
        md = ItineraryFormatter.to_markdown(itinerary)
        # Remove markdown symbols (simplified version)
        plain = md.replace('#', '').replace('**', '').replace('_', '')
        plain = plain.replace('- ', '  • ')
        return plain

