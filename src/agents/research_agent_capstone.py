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
    
    def __init__(self, observability_plugin=None):
        self.app_name = "trip_planner_research"
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        self.observability_plugin = observability_plugin  # Store plugin
        self.weather_api = WeatherAPI()
        self.maps = MapsHelper()
        
        # gemini-2.5-flash-lite DOES support tools! (confirmed in Day 2a notebook)
        instruction = f"""You are a travel research specialist with access to real-time information.

Your mission: Research destinations and provide comprehensive travel information using the tools available to you.

**IMPORTANT - Use Your Tools:**
1. **google_search** - ALWAYS use this to find current information about:
   - Best attractions and landmarks
   - Local activities and experiences  
   - Cultural events and festivals during the travel dates
   - Travel tips and local recommendations
   - Safety information and travel advisories
   - Transportation options and costs
   - Food recommendations and popular restaurants
   - Hidden gems and off-the-beaten-path spots

2. **get_weather_info** - Use this to get accurate weather data for the exact travel dates

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
        
        console.print(f"[green]✅ Research Agent using google_search tool for model: {Config.MODEL_NAME}[/green]")
        
        # Create ADK Agent WITH TOOLS
        self.agent = Agent(
            name="research_agent",
            model=create_gemini_model(),
            description=(
                "Expert travel researcher who uses google_search to find current "
                "information about destinations, attractions, and travel tips."
            ),
            instruction=instruction,
            tools=[google_search]  # ✅ gemini-2.5-flash-lite supports this!
        )
        
        # Create runner with sessions
        # Register observability plugin if provided
        plugins = []
        if self.observability_plugin:
            plugins.append(self.observability_plugin)
        
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
            memory_service=self.memory_service,
            plugins=plugins  # ✅ Plugin registered - auto-tracks all agent/tool calls!
        )
        
        console.print("[green]✅ Research Agent initialized with google_search tool![/green]")
    
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
        
        # Collect response and track tool usage
        response_text = ""
        tool_calls_made = []
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            # Track tool calls using get_function_calls() method
            if event.get_function_calls():
                for fc in event.get_function_calls():
                    tool_name = fc.name
                    tool_calls_made.append(tool_name)
                    console.print(f"  [dim]🔧 Using tool: {tool_name}[/dim]")
            
            # Get final response
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text
                break
        
        if tool_calls_made:
            console.print(f"[green]✅ Research used {len(tool_calls_made)} tool call(s): {', '.join(set(tool_calls_made))}[/green]")
        else:
            console.print("[yellow]⚠️  No tools were called (model used knowledge only)[/yellow]")
        
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

**CRITICAL**: You MUST use the google_search tool to find current information. 
Examples of searches you should make:
- "best things to do in {trip_input.destination}"
- "top restaurants in {trip_input.destination}"
- "{trip_input.destination} travel tips 2025"
- "{trip_input.destination} cultural customs"
- "{trip_input.destination} transportation guide"

Make multiple searches to gather comprehensive information!
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

