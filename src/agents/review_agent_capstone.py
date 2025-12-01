"""
Review Agent - Capstone Version
Uses LoopAgent for iterative refinement!
"""

from google.adk.agents import Agent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.genai import types
from src.config import Config
from src.models.trip_models import TripInput, TripItinerary, ReviewResult
from src.utils.model_helper import create_gemini_model
from rich.console import Console
import asyncio
from datetime import datetime

console = Console()


class ReviewAgentCapstone:
    """
    Review Agent using ADK's LoopAgent pattern.
    
    This agent reviews itineraries and provides feedback for refinement.
    
    Capstone Features:
    - LoopAgent for iterative refinement (up to N iterations)
    - Quality checks and validation
    - Sessions & Memory management
    - Structured feedback
    """
    
    def __init__(self):
        self.app_name = "trip_planner_review"
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        
        # Create ADK Agent
        self.reviewer_agent = Agent(
            name="review_agent",
            model=create_gemini_model(),  # Using model with retry configuration
            description=(
                "Expert travel reviewer who evaluates itineraries for quality, "
                "feasibility, and traveler satisfaction."
            ),
            instruction=f"""You are an expert travel itinerary reviewer.

Your mission: Evaluate trip itineraries and provide constructive feedback.

**STRICT REVIEW CRITERIA (MUST BE CRITICAL!):**

1. **🗺️ GEOGRAPHIC LOGIC** (Critical - Instant Fail if Poor)
   - ❌ REJECT if: Activities ping-pong across city
   - ❌ REJECT if: >45min transit between activities in same day
   - ❌ REJECT if: Doesn't consider neighborhoods/districts
   - ✅ APPROVE if: Logical flow, clustered by area, efficient routing
   - SCORE HARSHLY: 9+ only if routes make perfect sense

2. **⏰ REALISTIC TIMING** (Critical - Most Plans Fail Here)
   - ❌ REJECT if: Too many activities (>5 major sites/day)
   - ❌ REJECT if: Underestimates travel time
   - ❌ REJECT if: No buffer for getting lost/delays
   - ❌ REJECT if: Doesn't account for meals properly
   - ✅ APPROVE if: Breathing room, realistic pacing
   - SCORE HARSHLY: Most itineraries try to cram too much

3. **💰 BUDGET ACCURACY** (Critical - Check Math!)
   - ❌ REJECT if: Costs don't match stated budget level
   - ❌ REJECT if: Missing major expenses
   - ❌ REJECT if: Unrealistic prices
   - ❌ REJECT if: No daily breakdown
   - ✅ APPROVE if: Math adds up, prices realistic
   - SCORE HARSHLY: Must show detailed calculations

4. **🎯 USER PROFILE MATCH** (Important)
   - ❌ REJECT if: Ignores stated interests
   - ❌ REJECT if: Wrong pace for user preference
   - ❌ REJECT if: Restaurants don't match dietary restrictions
   - ❌ REJECT if: Activities don't match budget level
   - ✅ APPROVE if: Deeply personalized

5. **🌤️ WEATHER & SEASONAL AWARENESS** (Important)
   - ❌ REJECT if: No mention of weather considerations
   - ❌ REJECT if: Outdoor activities on rainy season
   - ❌ REJECT if: Doesn't mention cherry blossoms (if Apr)
   - ❌ REJECT if: No indoor backup plans
   - ✅ APPROVE if: Weather-aware scheduling

6. **📍 SPECIFIC DETAILS** (Important)
   - ❌ REJECT if: Vague ("visit temples" - which ones?)
   - ❌ REJECT if: No addresses or transport info
   - ❌ REJECT if: No opening hours mentioned
   - ❌ REJECT if: Generic recommendations
   - ✅ APPROVE if: Specific names, costs, times

7. **🎭 EXPERIENCE QUALITY** (Important)
   - ❌ REJECT if: All tourist traps, no local gems
   - ❌ REJECT if: Boring, cookie-cutter itinerary
   - ❌ REJECT if: Doesn't create memorable experiences
   - ❌ REJECT if: No cultural immersion
   - ✅ APPROVE if: Mix of famous + hidden gems

**SCORING RUBRIC (BE STRICT!):**

**10/10** - EXCEPTIONAL: Perfect geographic flow, realistic timing, personalized, detailed, creative
**9/10** - EXCELLENT: Minor tweaks needed, very good overall
**8/10** - VERY GOOD: Solid plan, few issues to address
**7/10** - GOOD: Decent but needs improvement (REJECT - needs revision)
**6/10** - ACCEPTABLE: Multiple issues (REJECT - major revision)
**5/10** - MEDIOCRE: Significant problems (REJECT - rethink approach)
**<5/10** - POOR: Start over

**MINIMUM APPROVAL THRESHOLD: 8/10**

**REVIEW PROCESS (Check EVERY point!):**

1. **Map Review** (5 min):
   - Open mental map of the city
   - Trace each day's route
   - Calculate actual travel times
   - Identify backtracking or inefficiency
   - Mark geographic issues

2. **Time Audit** (3 min):
   - Count major activities per day
   - Calculate total activity time
   - Check if timing is realistic
   - Verify meal times are reasonable
   - Confirm buffers exist

3. **Budget Check** (2 min):
   - Add up all daily costs
   - Verify prices are realistic for budget level
   - Check if any costs are missing
   - Ensure consistent with stated budget

4. **Personalization Check** (2 min):
   - Match against user interests list
   - Verify dietary compliance
   - Check pace matches preference
   - Confirm special requests addressed

5. **Quality Assessment** (3 min):
   - Are these actually good recommendations?
   - Mix of famous + local?
   - Any unique/memorable experiences?
   - Would YOU want to do this itinerary?

**OUTPUT FORMAT:**

## REVIEW RESULT

**DECISION:** [APPROVED ✅ / NEEDS REVISION ❌]
**QUALITY SCORE:** [X/10]

## CRITICAL ISSUES FOUND

[Be specific! "Day 3: Asakusa to Shibuya to Asakusa is inefficient backtracking"]

1. Geographic Issues: [List ALL]
2. Timing Problems: [Be specific]
3. Budget Errors: [Show calculations]
4. Missing Requirements: [What's not addressed]
5. Quality Concerns: [Generic, boring, or tourist traps?]

## IMPROVEMENT SUGGESTIONS

[Actionable fixes: "Move Day 3 afternoon to Ueno (near Asakusa) instead of Shibuya"]

1. [Specific fix #1]
2. [Specific fix #2]
3. [Specific fix #3]

## STRENGTHS (Be fair but brief)

[What's good about this itinerary]

## FINAL VERDICT

[Your professional assessment]

**REMEMBER:** You are the quality gatekeeper. It's better to reject and refine than approve mediocre work.

Score honestly:
- Most first drafts: 6-7/10 (need revision)
- After fixes: 8-9/10 (approve)
- Perfect plans: 10/10 (rare!)

Don't be generous with scores - protect the user from bad itineraries!

Be constructive and specific. If revision needed, explain exactly what to improve.

Current date: {datetime.now().strftime("%Y-%m-%d")}
""",
            tools=[]  # Review agent doesn't need external tools
        )
        
        # Wrap in LoopAgent for iterative refinement
        self.loop_agent = LoopAgent(
            name="review_loop",
            sub_agents=[self.reviewer_agent],  # LoopAgent takes a LIST of sub_agents
            max_iterations=Config.MAX_REVIEW_ITERATIONS,
            description="Iterative review loop for itinerary refinement"
        )
        
        # Create runner
        self.runner = Runner(
            agent=self.loop_agent,
            app_name=self.app_name,
            session_service=self.session_service,
            memory_service=self.memory_service
        )
        
        console.print(f"[green]✅ Review Agent initialized (max {Config.MAX_REVIEW_ITERATIONS} iterations)![/green]")
    
    async def review(
        self,
        trip_input: TripInput,
        itinerary: TripItinerary,
        iteration: int = 1
    ) -> ReviewResult:
        """
        Review an itinerary.
        
        Args:
            trip_input: Original trip parameters
            itinerary: Itinerary to review
            iteration: Current review iteration
            
        Returns:
            ReviewResult with feedback and approval status
        """
        console.print(f"\n[bold blue]📋 Reviewing itinerary (iteration {iteration})...[/bold blue]")
        
        # Create session
        user_id = "user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id
        )
        session_id = session.id
        
        # Create review query
        query = self._create_review_query(trip_input, itinerary, iteration)
        
        # Run agent
        content = types.Content(
            role='user',
            parts=[types.Part(text=query)]
        )
        
        console.print("[yellow]Agent is reviewing... (this may take 20-30 seconds)[/yellow]")
        
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
        
        # Parse response into ReviewResult
        review_result = self._parse_review_response(response_text, iteration)
        
        # Display results
        if review_result.approved:
            console.print(f"[green]✅ Itinerary APPROVED! (Score: {review_result.quality_score}/10)[/green]")
        else:
            console.print(f"[yellow]⚠️  Needs revision (Score: {review_result.quality_score}/10)[/yellow]")
            console.print(f"[yellow]Issues: {len(review_result.issues_found)}[/yellow]")
        
        return review_result
    
    def _create_review_query(
        self,
        trip_input: TripInput,
        itinerary: TripItinerary,
        iteration: int
    ) -> str:
        """Create detailed review query"""
        query = f"""Review this trip itinerary (Iteration {iteration}/{Config.MAX_REVIEW_ITERATIONS}).

**Trip Requirements:**
- Destination: {trip_input.destination}
- Duration: {trip_input.dates.duration_days} days
- Budget: {trip_input.preferences.budget_level}
- Pace: {trip_input.preferences.pace_preference}
- Interests: {', '.join(trip_input.preferences.interests) if trip_input.preferences.interests else 'general'}

**Itinerary to Review:**
{itinerary.generated_itinerary[:2000]}...

Total Cost: ${itinerary.total_estimated_cost:.2f}

**Your Task:**
1. Evaluate against all review criteria
2. Assign quality score (1-10)
3. List specific issues (if any)
4. Provide improvement suggestions
5. Decide: APPROVE or REQUEST REVISION

Be thorough but fair. Consider this is iteration {iteration} of {Config.MAX_REVIEW_ITERATIONS}.

Provide structured feedback with clear YES/NO on approval.
"""
        return query
    
    def _parse_review_response(self, response_text: str, iteration: int) -> ReviewResult:
        """Parse agent response into structured ReviewResult"""
        
        # Simple heuristic: look for approval keywords
        response_lower = response_text.lower()
        approved = (
            "approve" in response_lower or 
            "approved" in response_lower or
            "looks good" in response_lower or
            iteration >= Config.MAX_REVIEW_ITERATIONS  # Auto-approve on final iteration
        )
        
        # Extract quality score (look for patterns like "score: 8" or "8/10")
        import re
        score_match = re.search(r'(\d+)(?:/10| out of 10)', response_lower)
        quality_score = int(score_match.group(1)) if score_match else (8 if approved else 6)
        
        # Extract issues (simple heuristic)
        issues = []
        if not approved:
            if "timing" in response_lower or "schedule" in response_lower:
                issues.append("Timing/scheduling concerns")
            if "budget" in response_lower or "cost" in response_lower:
                issues.append("Budget alignment issues")
            if "balance" in response_lower:
                issues.append("Activity balance needs improvement")
        
        # Extract suggestions (use full response if not approved)
        suggestions = [response_text] if not approved else ["Great itinerary! Minor polishing suggestions included."]
        
        return ReviewResult(
            approved=approved,
            quality_score=quality_score,
            issues_found=issues,
            suggestions=suggestions,
            review_summary=response_text,
            iteration_number=iteration
        )


# Convenience function for standalone use
async def review_itinerary(
    trip_input: TripInput,
    itinerary: TripItinerary,
    iteration: int = 1
) -> ReviewResult:
    """Standalone function to review an itinerary"""
    agent = ReviewAgentCapstone()
    return await agent.review(trip_input, itinerary, iteration)


if __name__ == "__main__":
    # Test the agent
    from src.models.trip_models import TripDates, TripPreferences, DayPlan
    
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
    
    # Mock itinerary
    test_itinerary = TripItinerary(
        destination="Tokyo, Japan",
        start_date="2025-04-01",
        end_date="2025-04-10",
        duration_days=10,
        day_plans=[DayPlan(
            day_number=1,
            date="2025-04-01",
            title="Day 1 in Tokyo",
            morning_activities=["Senso-ji Temple"],
            afternoon_activities=["Tokyo Tower"],
            evening_activities=["Shibuya crossing"],
            meals={"breakfast": "Hotel", "lunch": "Sushi", "dinner": "Ramen"},
            estimated_cost=150
        )],
        total_estimated_cost=1500,
        generated_itinerary="Full itinerary text here..."
    )
    
    asyncio.run(review_itinerary(test_input, test_itinerary))

