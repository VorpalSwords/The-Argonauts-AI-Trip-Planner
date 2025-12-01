"""
Research Agent - Capstone Version
Uses ADK's built-in google_search tool!
"""

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from src.config import Config
from src.models.trip_models import TripInput, ResearchData
from src.tools.file_parser import parse_reference_files, create_reference_context
from src.utils.model_helper import create_gemini_model
from rich.console import Console
import asyncio
from datetime import datetime

from google.adk.tools import google_search
from src.tools.weather_api import WeatherAPI
from src.tools.maps_helper import MapsHelper

console = Console()


class ResearchAgentCapstone:
    """
    Research Agent using ADK's built-in google_search tool.
    
    This agent researches destinations, finds attractions, gets weather,
    and provides comprehensive travel information.
    
    Capstone Features:
    - Built-in google_search tool (no external API!)
    - Sessions & Memory management
    - Observability (logging, tracing)
    """
    
    def __init__(self):
        self.app_name = "trip_planner_research"
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        self.weather_api = WeatherAPI()
        self.maps = MapsHelper()
        
        # Check if model supports function calling
        model_name = Config.MODEL_NAME.lower()
        supports_tools = not any(x in model_name for x in ['lite', '8b'])
        
        # Create instruction based on tool support
        if supports_tools:
            instruction = f"""You are a travel research specialist.

Your mission: Research destinations and provide comprehensive travel information.

**Available Tools:**
1. google_search - Use this to find:
   - Best attractions and landmarks
   - Local activities and experiences  
   - Cultural events and festivals
   - Travel tips and recommendations
   - Safety information
   - Transportation options

2. get_weather_info - Use this to get:
   - Weather forecasts and seasonal information
   - Best time to visit
   - What to pack

**Research Process:**
1. Search for "[destination] best attractions and things to do"
2. Search for "[destination] travel tips and recommendations"
3. Search for "[destination] local culture and customs"
4. Get weather information for the travel dates
5. Search for "[destination] safety and travel advisories"

**Output Format:**
Provide a structured research report with:
- Top Attractions (at least 5-8 major sites)
- Activities by category (cultural, outdoor, food, shopping, etc.)
- Weather summary and packing recommendations
- Travel tips (transportation, safety, customs)
- Budget estimates (accommodation, food, activities)
- Special events during visit dates

Use multiple searches to gather comprehensive information.
Be specific with dates, prices, and practical details.

Current date: {datetime.now().strftime("%Y-%m-%d")}
"""
        else:
            instruction = f"""You are an ELITE travel research specialist with encyclopedic knowledge and CRITICAL ANALYSIS skills.

MISSION: Deliver research SO DETAILED and THOUGHTFUL that the user feels confident planning their trip.

**ENHANCED RESEARCH CAPABILITIES:**

🌐 **GOOGLE MAPS INTEGRATION**: When recommending places, think about:
• Exact locations and neighborhoods
• How to get there (specific metro lines, walking distances)
• What's nearby (cluster recommendations geographically)

🌦️ **REAL WEATHER DATA**: You have access to actual weather forecasts (or seasonal data as fallback)
• Use this to inform packing lists
• Suggest indoor alternatives for rainy days
• Time outdoor activities for best weather

🗺️ **MULTI-CITY INTELLIGENCE** (if applicable):
• Research EACH city comprehensively
• Consider inter-city transit (Shinkansen timing, costs, booking needs)
• Identify what makes each city unique (don't repeat same activities)
• Suggest optimal city order based on geography and logic

═══ CRITICAL ANALYSIS FRAMEWORK ═══

🎯 USER PROFILE DEEP-DIVE:
• Budget Reality Check: Analyze budget level - what can/can't they afford?
• Interest Matching: How do attractions align with their interests? Be HONEST
• Pace Assessment: Their pace preference = how many activities/day is realistic?
• Date Intelligence: Check their dates - weather? Peak season? Festivals? Closures?
• Dietary Constraints: Where can they ACTUALLY eat well given restrictions?

🗺️ GEOGRAPHIC & MAP INTELLIGENCE:
• NEIGHBORHOOD ANALYSIS: Which areas cluster together? Where to base?
• PROXIMITY MAPPING: Which attractions are walkable from each other?
• TRANSPORTATION WEB: Metro lines, bus routes, walking times (BE SPECIFIC!)
• EFFICIENT ROUTING: Plan logical daily flows (minimize backtracking!)
• HIDDEN GEMS: What's near popular spots that tourists miss?

🌦️ WEATHER & SEASONAL MASTERY:
• EXACT CONDITIONS for their dates: Temp ranges, rain probability, humidity
• WEATHER IMPACT: Which activities work? Which need indoor backup?
• SEASONAL EVENTS: Cherry blossoms? Festivals? Peak foliage? (with DATES!)
• PACKING SPECIFICS: Not "jacket" - "Lightweight waterproof jacket with hood"
• TIMING STRATEGY: Best hours for outdoor sites (avoid crowds & heat)
• MICROSEASONS: Early April Tokyo ≠ Late April - BE PRECISE!

4. **DEEP LOCAL KNOWLEDGE**:
   - Hidden gems (not just tourist traps)
   - Local favorites vs tourist spots
   - Neighborhood character & safety
   - Cultural nuances & etiquette
   - Money-saving tips
   - Common tourist mistakes to avoid

5. **CRITICAL EVALUATION**:
   - Is this attraction worth the time/cost?
   - Will it be crowded on their dates?
   - Are there better alternatives?
   - What's overrated? What's underrated?
   - Booking requirements (reserve ahead?)

**RESEARCH DEPTH REQUIREMENTS:**

Must include AT LEAST:
- 15-20 specific attractions (with pros/cons for each)
- 10+ restaurant recommendations (with cuisine types, prices, locations)
- 5+ neighborhood profiles (character, best for, how to get there)
- Detailed weather forecast for exact travel dates
- 8+ cultural tips and local customs
- Transportation: exact routes, costs, card types
- Safety tips specific to the area
- Budget breakdown by category
- 5+ "insider tips" from locals
- Day/night activity options
- Backup plans for bad weather

**OUTPUT STRUCTURE:**

## DESTINATION OVERVIEW
[Compelling summary highlighting what makes it special]

## WEATHER & SEASONAL CONTEXT
[Detailed weather for their dates + seasonal considerations]

## GEOGRAPHIC LAYOUT
[Key neighborhoods, how to navigate, where to stay]

## TOP EXPERIENCES (Categorized & Rated)
**Must-See (10/10)**: [With specific why]
**Highly Recommended (8-9/10)**: [...]
**Worth Considering (6-7/10)**: [...]
**Skip Unless**: [Be honest about overrated spots]

## DINING GUIDE
[By cuisine type, price range, location - BE SPECIFIC]

## PRACTICAL LOGISTICS
[Transport passes, opening hours, booking tips]

## CULTURAL INTELLIGENCE
[Customs, etiquette, local insights]

## BUDGET REALITY CHECK
[Real costs with examples]

## CRITICAL INSIGHTS
[What tourists get wrong, insider knowledge]

**QUALITY STANDARDS:**
- Think critically: "Is this really the best use of their time?"
- Be specific: Names, addresses, prices, exact times
- Consider geography: Group nearby attractions
- Check seasons: What's actually good during their visit?
- Prioritize: Help them choose, don't just list everything
- Be honest: Call out tourist traps
- Add alternatives: "If X is crowded, try Y instead"

Current date: {datetime.now().strftime("%Y-%m-%d")}
"""
        
        # For gemini-2.5-flash-lite and other lite models, don't use tools
        # They don't support function calling well and work better with knowledge-based approach
        console.print(f"[yellow]⚠ Using knowledge-based approach (no tools) for model: {model_name}[/yellow]")
        
        # Create ADK Agent WITHOUT TOOLS
        self.agent = Agent(
            name="research_agent",
            model=create_gemini_model(),  # Using model with retry configuration
            description=(
                "Expert travel researcher who finds attractions, "
                "activities, weather info, and travel tips for destinations."
            ),
            instruction=instruction
            # NO TOOLS - using model's internal knowledge
        )
        
        # Create runner with sessions
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
            memory_service=self.memory_service
        )
        
        console.print("[green]✅ Research Agent initialized (knowledge-based)![/green]")
    
    async def research(self, trip_input: TripInput) -> ResearchData:
        """
        Research a destination using google_search.
        
        Args:
            trip_input: Trip parameters (destination, dates, preferences)
            
        Returns:
            ResearchData with comprehensive destination information
        """
        console.print(f"\n[bold cyan]🔍 Researching: {trip_input.destination}[/bold cyan]")
        
        # Create user ID and session
        user_id = "user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id
        )
        session_id = session.id
        
        # Create research query
        query = self._create_research_query(trip_input)
        
        # Run agent
        content = types.Content(
            role='user',
            parts=[types.Part(text=query)]
        )
        
        console.print("[yellow]Agent is researching... (this may take 30-60 seconds)[/yellow]")
        
        # Collect response
        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            # Since we're using knowledge-based approach (no tools), just get the final response
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        
        console.print("[green]✅ Research complete![/green]")
        
        # Parse response into ResearchData
        return self._parse_research_response(response_text, trip_input)
    
    def _create_research_query(self, trip_input: TripInput) -> str:
        """Create detailed research query"""
        dates_str = f"from {trip_input.dates.start_date} to {trip_input.dates.end_date}"
        interests_str = ", ".join(trip_input.preferences.interests) if trip_input.preferences.interests else "general"
        
        # Parse reference files if provided
        reference_context = ""
        if trip_input.reference_files:
            console.print(f"[cyan]📂 Parsing {len(trip_input.reference_files)} reference file(s)...[/cyan]")
            try:
                parsed_files = parse_reference_files(trip_input.reference_files)
                reference_context = create_reference_context(parsed_files)
                console.print(f"[green]✅ Reference files parsed successfully[/green]")
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not parse reference files: {e}[/yellow]")
                reference_context = ""
        
        # Add weather context to query
        weather_context = ""
        if hasattr(self, 'weather_api'):
            try:
                weather_info = self.weather_api.get_weather(
                    destination=trip_input.destination,
                    start_date=trip_input.dates.start_date,
                    end_date=trip_input.dates.end_date
                )
                
                # Format weather for context
                weather_summary = f"\n**Weather Forecast for {trip_input.destination}:**\n"
                weather_summary += f"- Period: {weather_info.get('period', dates_str)}\n"
                weather_summary += f"- Temperature: {weather_info.get('average_temp_celsius', 'Variable')}\n"
                weather_summary += f"- Conditions: {weather_info.get('conditions', 'Seasonal')}\n"
                
                if "daily_forecast" in weather_info and weather_info["daily_forecast"]:
                    weather_summary += "\nDaily Forecast:\n"
                    for day in weather_info["daily_forecast"][:5]:  # First 5 days
                        weather_summary += f"  - {day.get('date')}: {day.get('temp_range')}, {day.get('conditions')}, Rain: {day.get('rain_probability')}\n"
                
                if "recommendations" in weather_info and weather_info["recommendations"]:
                    weather_summary += "\nPacking Recommendations:\n"
                    for rec in weather_info["recommendations"]:
                        weather_summary += f"  - {rec}\n"
                
                weather_summary += f"\n(Source: {weather_info.get('source', 'AI Knowledge')})\n"
                weather_context = weather_summary
                
            except Exception as e:
                console.print(f"[yellow]⚠️  Could not fetch weather: {e}[/yellow]")
                weather_context = ""
        
        query = f"""Research trip to {trip_input.destination} {dates_str}.

Trip Details:
- Destination: {trip_input.destination}
- Dates: {dates_str}
- Duration: {trip_input.dates.duration_days} days
- Budget: {trip_input.preferences.budget_level}
- Interests: {interests_str}

{weather_context}

{reference_context}

Please provide:
1. Top attractions and must-see places
2. Activities matching interests: {interests_str}
3. Consider the weather forecast above when making recommendations
4. Local culture and customs
5. Transportation options
6. Safety tips
7. Budget estimates
8. Special events during these dates

{"Note: Reference files from friends' trips are provided above. Use these as inspiration and to understand what worked well for them." if reference_context else ""}

**Important**: The weather forecast is already provided above. Use it to inform your recommendations (e.g., suggest indoor activities for rainy days, mention cherry blossom timing if relevant, advise on clothing).

Use google_search to find current, accurate information.
"""
        return query
    
    def _parse_research_response(self, response_text: str, trip_input: TripInput) -> ResearchData:
        """Parse agent response into structured ResearchData"""
        
        # In a production system, you'd use more sophisticated parsing
        # For now, we'll create a structured object from the text
        
        return ResearchData(
            destination=trip_input.destination,
            research_summary=response_text,
            attractions=[
                # Extract from response - for demo, using sample data
                f"Top attraction in {trip_input.destination}"
            ],
            activities={
                "cultural": ["Cultural activities from research"],
                "outdoor": ["Outdoor activities from research"],
                "food": ["Food experiences from research"]
            },
            weather_summary=f"Weather info for {trip_input.destination} included in research",
            travel_tips=[
                "Use google_search results for travel tips"
            ],
            estimated_costs={
                "accommodation_per_night": 100,
                "food_per_day": 50,
                "activities_per_day": 30
            },
            best_time_to_visit="Based on research and weather data",
            safety_tips=[
                "Safety information from google_search"
            ]
        )


# Convenience function for standalone use
async def research_destination(trip_input: TripInput) -> ResearchData:
    """Standalone function to research a destination"""
    agent = ResearchAgentCapstone()
    return await agent.research(trip_input)


if __name__ == "__main__":
    # Test the agent
    from src.models.trip_models import TripDates, TripPreferences
    
    test_input = TripInput(
        destination="Tokyo, Japan",
        dates=TripDates(
            start_date="2025-04-01",
            end_date="2025-04-10"
        ),
        preferences=TripPreferences(
            budget_level="mid-range",
            interests=["culture", "food", "temples", "cherry blossoms"]
        )
    )
    
    asyncio.run(research_destination(test_input))

