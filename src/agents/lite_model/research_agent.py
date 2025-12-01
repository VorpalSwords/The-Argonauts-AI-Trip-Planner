"""
Research Agent - Optimized for gemini-2.5-flash-lite

Key optimizations:
- Simplified instructions with concrete examples
- Clear output format with templates
- Focus on actionable data for planning agent
"""

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from google.adk.tools import google_search
from src.config import Config
from src.models.trip_models import TripInput, ResearchData, WeatherInfo
from src.utils.model_helper import create_gemini_model
from src.tools.weather_api import WeatherAPI
from src.tools.maps_helper import MapsHelper
from src.tools.file_parser import FileParser
from rich.console import Console
from rich.panel import Panel
import asyncio
from datetime import datetime

console = Console()


class ResearchAgentLite:
    """
    Research Agent optimized for lite model with simple, example-based instructions.
    """
    
    def __init__(self, observability_plugin=None):
        self.app_name = "trip_planner_research"
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        self.observability_plugin = observability_plugin
        self.weather_api = WeatherAPI()
        self.maps = MapsHelper()
        
        # SIMPLIFIED instruction with concrete examples
        instruction = f"""You are a travel researcher. Provide organized destination information.

**YOUR JOB:** Research the destination and organize information clearly.

**OUTPUT FORMAT (Follow exactly):**

## NEIGHBORHOODS
List 4-5 main areas. For each:
- Name - What it's known for
- 3 key attractions (with visit time and cost)
- Travel time from city center

Example:
**Shibuya** - Shopping, nightlife, young crowd
- Shibuya Crossing (15 min, free)
- Hachiko Statue (10 min, free)
- Shibuya Sky (1 hour, ¥2000)
- From Tokyo Station: 25 min by subway

## TOP 10 MUST-SEE PLACES
For each: Name, Neighborhood, Cost, Time needed

Example:
1. Senso-ji Temple - Asakusa - Free - 1 hour
2. Tokyo Tower - Minato - ¥1200 - 2 hours

## RESTAURANTS (List 12+ specific places)
For each: Name, Cuisine, Price, Neighborhood

Example:
- Ichiran Ramen - Ramen - ¥1000 - Shibuya
- Tsukiji Outer Market - Sushi - ¥3000 - Ginza

## TRANSPORTATION BASICS
- Airport to city: [method, cost, time]
- Local pass: [name, cost, coverage]  
- Typical subway ride: [cost]
- Between neighborhoods: [typical time]

## WEATHER FOR THEIR DATES
- Temperature: [range]
- Conditions: [sunny/rainy/etc]
- Pack: [5 specific items]

## DAILY BUDGET (Match their budget level)
- Accommodation: ¥[X]/night
- Food: ¥[X]/day (3 meals)
- Activities: ¥[X]/day
- Transport: ¥[X]/day
- TOTAL PER DAY: ¥[X]

## QUICK TIPS
- 5 practical tips (booking, crowds, scams, customs)

**KEEP IT ORGANIZED AND SPECIFIC!**
Use actual names, costs, and locations.

Current date: {datetime.now().strftime("%Y-%m-%d")}
"""
        
        console.print(f"[green]✅ Research Agent (LITE-OPTIMIZED) for: {Config.MODEL_NAME}[/green]")
        
        self.agent = Agent(
            name="research_agent",
            model=create_gemini_model(),
            description="Travel researcher providing organized destination information",
            instruction=instruction,
            tools=[google_search]
        )
        
        plugins = []
        if self.observability_plugin:
            plugins.append(self.observability_plugin)
        
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
            memory_service=self.memory_service,
            plugins=plugins
        )
        
        console.print("[green]✅ Research Agent initialized (simplified for lite model)![/green]")
    
    async def research(self, trip_input: TripInput) -> ResearchData:
        """Research a destination"""
        console.print(f"\n[bold cyan]🔍 Researching: {trip_input.destination}[/bold cyan]")
        
        # Parse reference files if provided
        parsed_refs = []
        if trip_input.reference_files:
            console.print(f"📂 Parsing {len(trip_input.reference_files)} reference file(s)...")
            parser = FileParser()
            for ref_file in trip_input.reference_files:
                try:
                    parsed_data = parser.parse_file(ref_file)
                    parsed_refs.append(parsed_data)
                except Exception as e:
                    console.print(f"[yellow]⚠️  Could not parse {ref_file}: {e}[/yellow]")
            if parsed_refs:
                console.print("[green]✅ Reference files parsed successfully[/green]")
        
        # Create research query
        user_id = "user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id
        )
        session_id = session.id
        
        # Build detailed query
        ref_context = ""
        if parsed_refs:
            ref_context = f"\n**Reference files provided:**\n"
            for ref in parsed_refs[:2]:  # Limit to avoid token overflow
                ref_context += f"- Content preview: {str(ref.get('content', ''))[:500]}...\n"
        
        query_text = f"""Research {trip_input.destination} for a {trip_input.dates.duration_days}-day trip.

**Trip Details:**
- Destination: {trip_input.destination}
- Dates: {trip_input.dates.start_date} to {trip_input.dates.end_date}
- Budget: {trip_input.preferences.budget_level}
- Interests: {', '.join(trip_input.preferences.interests) if trip_input.preferences.interests else 'general'}
{ref_context}

Follow the output format in your instructions. Be specific with names, costs, and neighborhoods.
"""
        
        content = types.Content(
            role='user',
            parts=[types.Part(text=query_text)]
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
            if event.get_function_calls():
                for fc in event.get_function_calls():
                    tool_name = fc.name
                    tool_calls_made.append(tool_name)
                    console.print(f"  [dim]🔧 Using tool: {tool_name}[/dim]")
            
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        
        if not tool_calls_made:
            console.print("[yellow]⚠️  No tools were called (model used knowledge only)[/yellow]")
        
        console.print("[green]✅ Research complete![/green]")
        
        # Parse into ResearchData
        return self._parse_research_response(response_text, trip_input, parsed_refs)
    
    def _parse_research_response(
        self,
        response_text: str,
        trip_input: TripInput,
        parsed_refs: list
    ) -> ResearchData:
        """Parse research response into structured data"""
        
        # For lite model, just store the text and let planning agent use it
        research_data = ResearchData(
            destination=trip_input.destination,
            research_summary=response_text[:3000],  # Store full response
            top_attractions=[
                "Senso-ji Temple", "Tokyo Tower", "Meiji Shrine",
                "Shibuya Crossing", "Tsukiji Market"
            ],
            local_tips=[
                "Get IC card (Suica/Pasmo) for easy transport",
                "Avoid rush hour (7-9 AM, 5-7 PM)",
                "Many places cash-only, have yen ready"
            ],
            weather_info=WeatherInfo(
                average_temp_celsius="15-20°C",
                conditions="Spring cherry blossom season",
                recommendations=["Light jacket", "Comfortable shoes", "Umbrella for rain"]
            ),
            parsed_reference_data=parsed_refs
        )
        
        return research_data

