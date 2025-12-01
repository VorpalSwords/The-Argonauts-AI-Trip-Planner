"""
Review Agent - Optimized for gemini-2.5-flash-lite

Key optimizations:
- Simple checklist format instead of abstract criteria
- Count problems instead of complex scoring
- Concrete feedback templates
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
import re

console = Console()


class ReviewAgentLite:
    """
    Review Agent optimized for lite model with simple checklist-based review.
    """
    
    def __init__(self, observability_plugin=None):
        self.app_name = "trip_planner_review"
        self.session_service = InMemorySessionService()
        self.memory_service = InMemoryMemoryService()
        self.observability_plugin = observability_plugin
        
        # SIMPLIFIED instruction with checklist
        instruction = f"""You are an itinerary reviewer. Check the plan using this simple checklist.

**REVIEW CHECKLIST (Check each item):**

☐ **1. Geographic:** Each day stays in ONE neighborhood?
   Look for backtracking like: Asakusa → Shibuya → Asakusa
   Mark as problem if you see cross-city ping-ponging

☐ **2. Activity Count:** Max 3-4 major activities per day?
   Count major sights/experiences (don't count meals/travel)
   Mark as problem if day has 5+ major activities

☐ **3. Costs:** Prices shown for restaurants and activities?
   Look for ¥ amounts or $ amounts
   Mark as problem if most things say "budget-friendly" without numbers

☐ **4. User Interests:** Activities match their interests?
   Check if their stated interests are covered
   Mark as problem if interests ignored

☐ **5. Realistic Timing:** Enough time for each activity?
   Activities should have 2-3 hours each
   Mark as problem if rushing (30 min per major sight)

**SCORING (Simple):**
- Count total problems found
- Score = 10 minus number of problems
- If score 8+ → APPROVE ✅
- If score 7 or less → REJECT ❌

**OUTPUT FORMAT:**

## REVIEW RESULT

**QUALITY SCORE:** [X]/10
**DECISION:** [APPROVED ✅ if 8+, else NEEDS REVISION ❌]

## CHECKLIST RESULTS
☐ Geographic: [PASS/FAIL] - [why]
☐ Activity Count: [PASS/FAIL] - [why]
☐ Costs: [PASS/FAIL] - [why]
☐ Interests: [PASS/FAIL] - [why]
☐ Timing: [PASS/FAIL] - [why]

## PROBLEMS FOUND (Total: X)

**Problem 1:**
- Where: Day X
- Issue: [specific issue]
- Fix: [exact fix]

**Problem 2:**
- Where: Day Y
- Issue: [specific issue]
- Fix: [exact fix]

## IF REJECTED: What to fix for next iteration

1. [Specific fix for problem 1]
2. [Specific fix for problem 2]

**Keep feedback simple and specific!**
"""
        
        console.print(f"[green]✅ Review Agent (LITE-OPTIMIZED) for: {Config.MODEL_NAME}[/green]")
        
        self.reviewer_agent = Agent(
            name="review_agent",
            model=create_gemini_model(),
            description="Itinerary reviewer using simple checklist",
            instruction=instruction,
            tools=[]
        )
        
        self.loop_agent = LoopAgent(
            name="review_loop",
            sub_agents=[self.reviewer_agent],
            max_iterations=Config.MAX_REVIEW_ITERATIONS,
            description="Review loop"
        )
        
        plugins = []
        if self.observability_plugin:
            plugins.append(self.observability_plugin)
        
        self.runner = Runner(
            agent=self.loop_agent,
            app_name=self.app_name,
            session_service=self.session_service,
            memory_service=self.memory_service,
            plugins=plugins
        )
        
        console.print(f"[green]✅ Review Agent initialized (max {Config.MAX_REVIEW_ITERATIONS} iterations)![/green]")
    
    async def review(
        self,
        trip_input: TripInput,
        itinerary: TripItinerary,
        iteration: int = 1
    ) -> ReviewResult:
        """Review itinerary"""
        console.print(f"\n[bold blue]📋 Reviewing itinerary (iteration {iteration})...[/bold blue]")
        
        user_id = "user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        session = await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id
        )
        session_id = session.id
        
        # Create review query
        query = f"""Review this itinerary (Iteration {iteration}/{Config.MAX_REVIEW_ITERATIONS}).

**User Requirements:**
- Destination: {trip_input.destination}
- Duration: {trip_input.dates.duration_days} days
- Budget: {trip_input.preferences.budget_level}
- Interests: {', '.join(trip_input.preferences.interests) if trip_input.preferences.interests else 'general'}

**Itinerary to Review:**
{itinerary.generated_itinerary[:3000]}

**Your Task:**
1. Go through the checklist in your instructions
2. Count problems found
3. Calculate score (10 minus problems)
4. If score 8+ → APPROVE, else REJECT

Use the output format from your instructions.
"""
        
        content = types.Content(
            role='user',
            parts=[types.Part(text=query)]
        )
        
        console.print("[yellow]Agent is reviewing... (this may take 20-30 seconds)[/yellow]")
        
        response_text = ""
        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.get_function_calls():
                for fc in event.get_function_calls():
                    console.print(f"  [dim]🔧 Review tool: {fc.name}[/dim]")
            
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text
                break
        
        # Parse response
        review_result = self._parse_review_response(response_text, iteration)
        
        # Display
        if review_result.approved:
            console.print(f"[green]✅ Itinerary APPROVED! (Score: {review_result.quality_score}/10)[/green]")
        else:
            console.print(f"[yellow]⚠️  Needs revision (Score: {review_result.quality_score}/10)[/yellow]")
            console.print(f"[yellow]Issues: {len(review_result.issues_found)}[/yellow]")
        
        return review_result
    
    def _parse_review_response(self, response_text: str, iteration: int) -> ReviewResult:
        """Parse review response"""
        
        response_lower = response_text.lower()
        
        # Extract score
        score_match = re.search(r'(\d+)(?:/10| out of 10)', response_lower)
        quality_score = float(score_match.group(1)) if score_match else 7.0
        
        # Approval based strictly on score, no exceptions
        threshold = Config.get_approval_threshold()
        approved = quality_score >= threshold
        
        # Extract issues
        issues = []
        if "geographic" in response_lower and "fail" in response_lower:
            issues.append("Geographic routing issues")
        if "activity count" in response_lower and "fail" in response_lower:
            issues.append("Too many activities")
        if "cost" in response_lower and "fail" in response_lower:
            issues.append("Missing costs")
        if "interest" in response_lower and "fail" in response_lower:
            issues.append("Doesn't match interests")
        if "timing" in response_lower and "fail" in response_lower:
            issues.append("Timing unrealistic")
        
        return ReviewResult(
            approved=approved,
            quality_score=quality_score,
            issues_found=issues,
            suggestions=[response_text],
            review_summary=response_text,
            iteration_number=iteration
        )

