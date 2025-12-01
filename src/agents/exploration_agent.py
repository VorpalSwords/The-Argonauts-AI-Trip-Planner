"""
Exploration Agent - The Argonauts Pathfinder

High-level destination discovery before detailed planning.

Use when you:
- Don't know much about a destination
- Want to understand what a country/region offers
- Need help choosing which cities to visit
- Want recommended trip structures

Provides:
- Destination overview and vibe
- Top cities/regions with highlights
- 2-3 suggested trip structures for your duration
- Seasonal considerations and practical info
- Next steps for detailed planning

Typical runtime: 20-60 seconds
"""

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from src.config import Config
from src.utils.model_helper import create_gemini_model
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

console = Console()


class ExplorationAgent:
    """
    Exploration Agent for preliminary destination research.
    
    Use this before full trip planning when you want to:
    - Discover what a country/region offers
    - Get recommendations for which cities to visit
    - Understand time allocation between locations
    - Get a feel for what's available before committing
    """
    
    def __init__(self):
        self.app_name = "argonauts_exploration"
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        
        instruction = """You are an EXPLORATION SPECIALIST - helping travelers discover destinations.

Your mission: Help people WHO DON'T KNOW MUCH about a destination understand what it offers and how to structure their trip.

**EXPLORATION FRAMEWORK:**

1. **DESTINATION OVERVIEW** (1-2 paragraphs):
   - What makes this place special?
   - Who is it for? (culture lovers, beach goers, adventurers, foodies)
   - Overall vibe and character

2. **TOP REGIONS/CITIES TO VISIT**:
   For each recommended location:
   - Why visit? (unique offerings)
   - How many days needed?
   - Best for what type of traveler?
   - Main highlights (3-5 key things)
   - Difficulty level (easy/moderate/challenging access)

3. **SUGGESTED TRIP STRUCTURES**:
   Provide 2-3 different itinerary structures based on duration:
   
   Example for 10-day Japan trip:
   - Option A (Depth): Tokyo 6 days + Kyoto 4 days
   - Option B (Breadth): Tokyo 4 days + Kyoto 3 days + Osaka 2 days + Nara 1 day
   - Option C (Focus): Tokyo 10 days (really get to know the city)

4. **SEASONAL CONSIDERATIONS**:
   - Best time to visit
   - What's special about their travel dates?
   - Weather expectations
   - Crowds and peak season info

5. **PRACTICAL INFO**:
   - General budget expectations (cheap, moderate, expensive?)
   - Language barriers (easy/moderate/hard for English speakers?)
   - Transportation between cities (train, bus, flight options)
   - Visa requirements if any

6. **NEXT STEPS**:
   Based on the user's interests, recommend:
   - Which cities to include in full planning
   - How many days to allocate per city
   - What to prioritize

**OUTPUT FORMAT:**
Provide a clear, structured exploration report that helps the user make informed decisions about their trip structure before diving into detailed day-by-day planning.

Be honest about trade-offs: "More cities = less depth in each" or "Kyoto needs at least 3 days to appreciate properly"

Current date: {datetime.now().strftime("%Y-%m-%d")}
"""
        
        self.agent = Agent(
            name="exploration_agent",
            model=create_gemini_model(),
            description=(
                "Exploration specialist who helps travelers discover destinations "
                "and structure their trips before detailed planning."
            ),
            instruction=instruction
        )
        
        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
            memory_service=self.memory_service
        )
        
        console.print("[green]✅ Exploration Agent initialized![/green]")
    
    async def explore(
        self,
        destination: str,
        num_days: int,
        interests: Optional[List[str]] = None,
        budget_level: str = "mid-range"
    ) -> str:
        """
        Explore a destination and get high-level recommendations.
        
        Args:
            destination: Country or region to explore
            num_days: How many days for the trip
            interests: User's general interests
            budget_level: Budget constraints
            
        Returns:
            Exploration report as text
        """
        console.print(Panel(
            f"🔍 Exploring: {destination}\n"
            f"⏱️  Duration: {num_days} days\n"
            f"💰 Budget: {budget_level}\n"
            f"🎯 Interests: {', '.join(interests) if interests else 'General'}",
            title="🚢 The Argonauts - Exploration Mode",
            border_style="cyan"
        ))
        
        interests_str = ", ".join(interests) if interests else "general travel"
        
        query = f"""I'm planning a trip to {destination} for {num_days} days.

My details:
- Duration: {num_days} days
- Interests: {interests_str}
- Budget level: {budget_level}

I don't know much about {destination} yet. Help me understand:
1. What are the top regions/cities I should consider visiting?
2. How should I structure my {num_days}-day trip?
3. What makes each location special?
4. How many days should I spend in each place?
5. What's realistic given my time constraints?

Provide 2-3 different trip structure options so I can choose what fits my travel style.
"""
        
        # Create user ID and session
        user_id = "explorer_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id
        )
        session_id = session.id
        
        # Run agent
        content = types.Content(
            role='user',
            parts=[types.Part(text=query)]
        )
        
        console.print("\n[yellow]🗺️  Agent is exploring destinations... (20-60 seconds)[/yellow]\n")
        
        # Collect response
        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                break
        
        console.print("[green]✅ Exploration complete![/green]\n")
        
        return response_text


async def explore_destination(
    destination: str,
    num_days: int,
    interests: Optional[List[str]] = None,
    budget_level: str = "mid-range"
) -> str:
    """Standalone function to explore a destination"""
    agent = ExplorationAgent()
    return await agent.explore(destination, num_days, interests, budget_level)


if __name__ == "__main__":
    # Test the exploration agent
    result = asyncio.run(explore_destination(
        destination="Japan",
        num_days=10,
        interests=["culture", "food", "temples", "nature"],
        budget_level="mid-range"
    ))
    
    print("\n" + "="*80)
    print("EXPLORATION REPORT:")
    print("="*80)
    print(result)

