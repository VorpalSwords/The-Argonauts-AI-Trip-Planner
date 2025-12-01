"""
Planning Agent - The Argonauts Navigator

Creates optimized daily itineraries featuring:
- Geographic clustering (minimize transit time)
- Multiple restaurant options per meal (2-3 choices)
- Dietary accommodation (vegetarian, no spicy, etc.)
- Transit pass recommendations
- Realistic timing with rest periods
- Budget calculations

Handles multi-city trips with strategic sequencing.
"""

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from src.config import Config
from src.models.trip_models import TripInput, ResearchData, TripItinerary, DayPlan
from src.utils.model_helper import create_gemini_model
from src.tools.transport_helper import TransportHelper
from rich.console import Console
import asyncio
from datetime import datetime, timedelta
import json

console = Console()

# Note: Tools removed for gemini-2.5-flash-lite compatibility
# Using knowledge-based approach instead


class PlanningAgentCapstone:
    """
    Planning Agent using ADK best practices.
    
    This agent creates optimized daily itineraries based on research data.
    
    Capstone Features:
    - Code execution (if enabled) for schedule optimization
    - Custom budget calculation tool
    - Sessions & Memory management
    - Structured output (Pydantic models)
    """
    
    def __init__(self, observability_plugin=None):
        self.app_name = "trip_planner_planning"
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        self.observability_plugin = observability_plugin  # Store plugin
        
        # For gemini-2.5-flash-lite, use knowledge-based approach (no tools)
        model_name = Config.MODEL_NAME.lower()
        console.print(f"[yellow]⚠ Planning agent using knowledge-based approach (no tools) for: {model_name}[/yellow]")
        
        # Create ADK Agent WITHOUT TOOLS for compatibility
        self.agent = Agent(
            name="planning_agent",
            model=create_gemini_model(),  # Using model with retry configuration
            description=(
                "Expert trip planner who creates optimized daily itineraries, "
                "balancing activities, rest, and budget constraints."
            ),
            instruction=f"""You are a WORLD-CLASS trip planner who creates geographically intelligent, realistic, and deeply thoughtful itineraries.

Your mission: Create itineraries that are NOT just lists of places, but SMART, EFFICIENT, ENJOYABLE travel experiences.

**MULTI-CITY TRIPS (CRITICAL!):**
If the trip involves multiple cities (e.g., Tokyo → Kyoto → Osaka):
1. **Strategic City Sequencing**: Order cities logically (geographic proximity, transport efficiency)
2. **Transition Days**: Plan dedicated travel days between cities with realistic timing
3. **City-Specific Optimization**: Apply neighborhood clustering within EACH city separately
4. **Inter-city Transport**: Include Shinkansen/train booking details, costs, travel time
5. **Momentum Management**: Don't waste first/last days - optimize arrival and departure days
6. **Accommodation Strategy**: Book hotels near major transport hubs for easy transitions

Example multi-city flow:
- Days 1-4: Tokyo (explore Shinjuku, Shibuya, Asakusa clusters)
- Day 5: TRANSITION DAY - Morning in Tokyo, Shinkansen to Kyoto (2.5h, ¥13,000), afternoon Kyoto orientation
- Days 6-8: Kyoto (explore Gion, Arashiyama, Central clusters)
- Day 9: Kyoto to Osaka (30 min, ¥560), explore Osaka
- Day 10: Final day Osaka, evening departure

**🗺️ GEOGRAPHIC INTELLIGENCE (CRITICAL!):**

1. **CLUSTER BY LOCATION**:
   - Group attractions by neighborhood/district
   - Minimize unnecessary transit time
   - Create logical geographic flow for each day
   - Example: "Morning in Asakusa, afternoon in nearby Ueno" NOT "Morning Asakusa, afternoon Shibuya, evening back to Asakusa"

2. **CALCULATE REALISTIC TRAVEL TIMES**:
   - Walking: 5 min = 400m, 15 min = 1.2km
   - Subway: Add 10-15 min for wait + transfers
   - Include time to find places, not just transit
   - Factor in rush hour (7-9 AM, 5-7 PM)

3. **MAP-AWARE ROUTING**:
   - Start morning near accommodation
   - End evening near dining districts
   - Place far destinations strategically
   - Consider "on the way" stops

**🎯 CRITICAL THINKING:**

1. **ENERGY MANAGEMENT**:
   - Don't pack too much (travelers get tired!)
   - Alternate intense & relaxed activities
   - Build in "discovery time" for wandering
   - Consider jet lag on arrival days
   - Schedule rest after long travel

2. **WEATHER ADAPTATION**:
   - Check forecast for their dates
   - Indoor activities for rain days
   - Outdoor activities for good weather
   - Early morning for summer heat
   - Flexible "weather call" options

3. **TIMING INTELLIGENCE**:
   - Popular spots: go early or late
   - Temples: mornings are quieter
   - Shopping: afternoons/evenings better
   - Museums: weekday mornings best
   - Nightlife: obviously evenings
   - Check actual opening hours!

4. **REALISTIC PACING**:
   - Budget pace: 3-4 major things/day
   - Mid-range pace: 4-5 things/day + meals
   - Luxury pace: 3-4 things but premium
   - "Moderate" = don't rush, enjoy
   - "Relaxed" = 2-3 things, lots of flex

**💰 ACCURATE BUDGETING:**

Daily costs (be realistic!):
- **Budget**: 
  * Accommodation: $30-50/night
  * Food: $25-35/day (breakfast $5, lunch $10, dinner $15)
  * Activities: $15-25/day
  * Transport: $10-15/day
  * Total: ~$80-125/day
  
- **Mid-range**:
  * Accommodation: $80-150/night
  * Food: $50-80/day (breakfast $10, lunch $20, dinner $30)
  * Activities: $30-60/day
  * Transport: $15-25/day
  * Total: ~$175-315/day
  
- **Luxury**:
  * Accommodation: $200-500/night
  * Food: $100-200/day
  * Activities: $80-150/day
  * Transport: $30-50/day
  * Total: ~$410-900/day

**📅 DAILY ITINERARY STRUCTURE:**

### Day X: [Neighborhood Focus] - [Theme]

**Geographic Zone:** [Primary area for the day]

**Morning (8:00-12:00):**
- 8:00-9:00: [Activity 1] - [Location, cost, why visit]
- 9:15-11:00: [Activity 2] - [Walking distance from Activity 1]
- 11:15-12:00: [Activity 3 or buffer time]

**Lunch (12:00-13:30):**
- Restaurant: [Name, cuisine, location, price, specialties]
- Alternative: [Backup option nearby]

**Afternoon (13:30-18:00):**
- 13:30-15:00: [Activity] - [How to get there, time]
- 15:00-17:00: [Activity] - [Must be nearby!]
- 17:00-18:00: [Flexible time or last activity]

**Dinner (18:30-20:00):**
- Restaurant: [Name, area, price, why special]
- Location tip: [Near accommodation or evening activity]

**Evening (20:00+):**
- Option A: [Active evening plan]
- Option B: [Relaxed alternative]
- Option C: [Return to hotel if tired]

**Geographic Flow:** [Explain the logical route]
**Transport:** [Specific lines, passes, costs]
**Budget:** [Detailed breakdown with real prices]
**Booking Required:** [What to reserve ahead]
**Weather Backup:** [Alternative if rain/cold]
**Pro Tips:** [2-3 insider insights]

**🎨 PERSONALIZATION:**

Match to user profile:
- **Interests**: Prioritize their stated interests
- **Dietary**: Only suggest appropriate restaurants
- **Budget**: Stay within their range
- **Pace**: Respect their energy preference
- **Weather**: Adapt to season/forecast
- **Special requests**: Address explicitly

**📊 QUALITY CHECKLIST:**

Before outputting, verify:
☐ Each day is geographically logical (no ping-ponging)
☐ Travel times are realistic (not underestimated)
☐ Pacing matches user preference (not too packed)
☐ Budget calculations are accurate
☐ Opening hours are considered
☐ Weather-appropriate activities
☐ Meal recommendations match dietary needs
☐ Mix of must-sees and hidden gems
☐ Backup options provided
☐ Specific addresses and costs included

**CRITICAL REALISM:**

Be honest:
- "This is ambitious but doable"
- "Consider skipping X if you want more relaxed pace"
- "These two are far apart - expect 45 min travel"
- "Very crowded on weekends - go early"
- "Overrated but still worth seeing"

Think like a local helping a friend, not a tour company selling packages.

Current date: {datetime.now().strftime("%Y-%m-%d")}
"""
            # NO TOOLS - using model's internal knowledge for compatibility
        )
        
        # Create runner
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
        
        console.print("[green]✅ Planning Agent initialized (knowledge-based)![/green]")
    
    async def plan(self, trip_input: TripInput, research_data: ResearchData) -> TripItinerary:
        """
        Create detailed daily itinerary.
        
        Args:
            trip_input: Trip parameters
            research_data: Research findings from Research Agent
            
        Returns:
            TripItinerary with daily plans
        """
        console.print(f"\n[bold magenta]📅 Planning {trip_input.dates.duration_days}-day itinerary...[/bold magenta]")
        
        # Create session
        user_id = "user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id
        )
        session_id = session.id
        
        # Create planning query
        query = self._create_planning_query(trip_input, research_data)
        
        # Run agent
        content = types.Content(
            role='user',
            parts=[types.Part(text=query)]
        )
        
        console.print("[yellow]Agent is creating itinerary... (this may take 30-90 seconds)[/yellow]")
        
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
        
        console.print("[green]✅ Itinerary created![/green]")
        
        # Parse response into TripItinerary
        return self._parse_itinerary_response(response_text, trip_input, research_data)
    
    def _create_planning_query(self, trip_input: TripInput, research_data: ResearchData) -> str:
        """Create detailed planning query with transport guide"""
        
        # Get transportation recommendations
        cities = [trip_input.destination] + (trip_input.additional_destinations or [])
        if len(cities) > 1 and "japan" in trip_input.destination.lower():
            transport_context = TransportHelper.get_japan_transit_overview(cities)
        else:
            transport_context = TransportHelper.format_transit_guide(
                trip_input.destination,
                trip_input.dates.duration_days
            )
        
        # Handle dietary restrictions
        dietary_str = ""
        if trip_input.preferences.dietary_restrictions:
            dietary_str = f"\n**CRITICAL - Dietary Restrictions**: {', '.join(trip_input.preferences.dietary_restrictions)}"
            dietary_str += "\n- EVERY meal suggestion must accommodate these restrictions"
            dietary_str += "\n- Provide multiple options per meal with clear dietary info"
        
        query = f"""Create a detailed {trip_input.dates.duration_days}-day itinerary for {trip_input.destination}.

**Trip Details:**
- Destination: {trip_input.destination}
- Dates: {trip_input.dates.start_date} to {trip_input.dates.end_date}
- Duration: {trip_input.dates.duration_days} days
- Budget: {trip_input.preferences.budget_level}
- Pace: {trip_input.preferences.pace_preference}
- Interests: {', '.join(trip_input.preferences.interests) if trip_input.preferences.interests else 'general'}
{dietary_str}

**Research Summary:**
{research_data.research_summary[:1500]}...

{transport_context}

**MEAL PLANNING REQUIREMENTS** (CRITICAL!):
For EVERY meal, provide 2-3 specific restaurant options:
- Include restaurant name, estimated cost, cuisine type
- Indicate which options accommodate dietary restrictions
- Verify operating hours match meal time
- Show price range for each option
- Mix of traditional and modern options

Example format:
**Lunch Options (12:30-1:30 PM):**
1. Ichiran Ramen (¥1,500) - Non-spicy broths available, vegetarian broth option
2. Afuri Ramen (¥1,300) - Light yuzu ramen, clear vegetarian options on menu
3. Ain Soph Journey (¥1,800) - Fully vegan restaurant, no spicy dishes

**Requirements:**
1. Create detailed plan for each of the {trip_input.dates.duration_days} days
2. Balance {trip_input.preferences.pace_preference} pace with {', '.join(trip_input.preferences.interests)} interests
3. Include specific times, locations, and costs
4. Provide 2-3 restaurant options PER MEAL with dietary info
5. Include transit pass recommendations from transportation guide above
6. Add pro tips and alternatives
7. Calculate daily budgets

Provide structured day-by-day plan with morning/afternoon/evening activities.
"""
        return query
    
    def _parse_itinerary_response(
        self,
        response_text: str,
        trip_input: TripInput,
        research_data: ResearchData
    ) -> TripItinerary:
        """Parse agent response into structured TripItinerary"""
        
        # Calculate total budget manually (no tool needed)
        budget_level = trip_input.preferences.budget_level
        num_days = trip_input.dates.duration_days
        
        # Daily cost estimates by budget level
        daily_costs = {
            "budget": {"accommodation": 50, "food": 30, "activities": 20, "transport": 15},
            "mid-range": {"accommodation": 120, "food": 60, "activities": 50, "transport": 30},
            "luxury": {"accommodation": 300, "food": 150, "activities": 150, "transport": 80}
        }
        
        costs = daily_costs.get(budget_level, daily_costs["mid-range"])
        daily_total = sum(costs.values())
        subtotal = daily_total * num_days
        
        # Add flight estimate
        flight_estimates = {"budget": 500, "mid-range": 800, "luxury": 1500}
        flight_cost = flight_estimates.get(budget_level, 800)
        total_budget = subtotal + flight_cost
        
        budget_calc = {
            "total": total_budget,
            "subtotal": subtotal,
            "breakdown": {
                "accommodation": costs["accommodation"] * num_days,
                "food": costs["food"] * num_days,
                "activities": costs["activities"] * num_days,
                "transport": costs["transport"] * num_days,
                "flights": flight_cost
            },
            "per_day": daily_total
        }
        
        # Create day plans
        day_plans = []
        start_date = datetime.fromisoformat(trip_input.dates.start_date)
        
        for day_num in range(trip_input.dates.duration_days):
            current_date = start_date + timedelta(days=day_num)
            
            day_plan = DayPlan(
                day_number=day_num + 1,
                date=current_date.strftime("%Y-%m-%d"),
                title=f"Day {day_num + 1} in {trip_input.destination}",
                morning_activities=[
                    f"Morning activity {day_num + 1}.1",
                    f"Morning activity {day_num + 1}.2"
                ],
                afternoon_activities=[
                    f"Afternoon activity {day_num + 1}.1",
                    f"Afternoon activity {day_num + 1}.2"
                ],
                evening_activities=[
                    f"Evening activity {day_num + 1}.1"
                ],
                meals={
                    "breakfast": f"Breakfast recommendation Day {day_num + 1}",
                    "lunch": f"Lunch recommendation Day {day_num + 1}",
                    "dinner": f"Dinner recommendation Day {day_num + 1}"
                },
                estimated_cost=budget_calc["per_day"],
                notes=[
                    f"Travel tip for day {day_num + 1}"
                ]
            )
            day_plans.append(day_plan)
        
        return TripItinerary(
            trip_input=trip_input,  # Include the full trip_input
            research_summary=research_data,  # Include research data
            destination=trip_input.destination,
            start_date=str(trip_input.dates.start_date),
            end_date=str(trip_input.dates.end_date),
            duration_days=trip_input.dates.duration_days,
            day_plans=day_plans,
            total_estimated_cost=budget_calc["total"],
            generated_itinerary=response_text,
            packing_list=[
                "Comfortable walking shoes",
                "Weather-appropriate clothing",
                "Travel adapter",
                "Portable charger"
            ],
            important_notes=[
                f"Budget level: {trip_input.preferences.budget_level}",
                f"Pace: {trip_input.preferences.pace_preference}",
                "Book popular attractions in advance"
            ]
        )


# Convenience function for standalone use
async def plan_trip(trip_input: TripInput, research_data: ResearchData) -> TripItinerary:
    """Standalone function to plan a trip"""
    agent = PlanningAgentCapstone()
    return await agent.plan(trip_input, research_data)


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
            interests=["culture", "food", "temples", "cherry blossoms"],
            pace_preference="moderate"
        )
    )
    
    # Mock research data
    test_research = ResearchData(
        destination="Tokyo, Japan",
        research_summary="Tokyo is amazing...",
        attractions=["Senso-ji Temple", "Tokyo Tower"],
        activities={"cultural": ["Tea ceremony"], "food": ["Sushi tour"]},
        weather_summary="Cherry blossom season, mild weather",
        travel_tips=["Get JR Pass"],
        estimated_costs={"accommodation_per_night": 100},
        best_time_to_visit="April for cherry blossoms"
    )
    
    asyncio.run(plan_trip(test_input, test_research))

