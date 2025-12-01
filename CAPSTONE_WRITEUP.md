# The Argonauts: AI Trip Planner

*Your AI crew for planning epic journeys*

**Course**: 5-Days AI Agents  
**Framework**: Google Agent Development Kit (ADK)  
**GitHub**: [your-repo-link-here]

**Project name inspiration**: The Argonauts were Jason's legendary crew on the quest for the Golden Fleece. This project uses a specialized crew of AI agents - Research, Planning, Review, and Orchestrator - working together to chart your journey.

---

## Project overview

I'm planning a trip to Japan in April to see the cherry blossoms, and several friends sent me their trip plans - PDFs, Excel sheets, Word documents, and text files with Google Maps links. I thought it would be interesting to build an AI system that could learn from these different sources and create a comprehensive itinerary.

Most trip planning tools just provide lists of places to visit. That's not particularly useful when you need to know what order to visit them in, where to eat, how much it will cost, and how to avoid spending hours on transit. This project attempts to solve those problems using a multi-agent architecture.

**Recent improvements**: Added multi-city support (Tokyo→Kyoto→Osaka transitions), Google Maps link generation, and real-time weather API integration with intelligent fallback.

**Project status**: This is a work in progress. The core functionality works, but there are areas that need more testing and refinement, particularly around cost estimates and the accuracy of recommendations. Consider this a proof of concept rather than a production-ready application.

## System architecture

The system uses four specialized AI agents working in sequence with iterative refinement:

**Research Agent** → Gathers information about the destination, weather patterns, attractions, and local customs

**Planning Agent** → Creates day-by-day schedules with geographic optimization to minimize transit time

**Review Agent** → Evaluates the itinerary quality using strict criteria. Requires a minimum score of 8/10 to approve

**Orchestrator** → Coordinates the workflow and manages communication between agents

The workflow follows this pattern:

```
Research → Plan → Review → (if score < 8) → Refine → Review again (up to 3 cycles)
```

This is implemented using ADK's LoopAgent pattern for iterative refinement.

## Agent implementation details

### Research Agent

The Research Agent is responsible for gathering destination information. I gave it a structured analytical framework:

```
Analyze user profile:
- Budget constraints and what they realistically allow
- Interests and how they map to available activities
- Travel dates and their implications (weather, crowds, seasonal events)

Think geographically:
- Which neighborhoods are located near each other
- Realistic travel times between locations
- Strategic base locations for accommodation

Consider weather patterns:
- Seasonal conditions for the specific dates
- How weather affects outdoor activities
- Appropriate packing recommendations
```

The agent doesn't just search randomly - it applies critical thinking to determine what information matters for the specific trip.

### Planning Agent

This is where route optimization happens. The agent creates schedules that keep you in one geographic area rather than having you criss-cross the city unnecessarily.

For example, instead of:
- Morning: Shinjuku
- Lunch: Asakusa (45 minutes away)
- Afternoon: Back to Shinjuku (45 minutes)
- Dinner: Shibuya (30 minutes)

It creates:
- Full day in Shinjuku area
- Next day in adjacent areas like Harajuku-Shibuya
- Following day in Asakusa-Ueno region

The agent follows optimization rules like:
- Cluster attractions by neighborhood
- Include realistic travel time estimates
- Consider opening hours and reservation requirements
- Avoid over-scheduling (people get tired)
- Have backup plans for weather

Budget calculation is handled inline without external APIs:

```python
daily_costs = {
    "budget": {"accommodation": 50, "food": 30, "activities": 20, "transport": 15},
    "mid-range": {"accommodation": 120, "food": 60, "activities": 50, "transport": 30},
    "luxury": {"accommodation": 300, "food": 150, "activities": 150, "transport": 80}
}

total_cost = (daily_costs × number_of_days) + estimated_flights
```

### Review Agent

The Review Agent applies strict quality criteria:

1. **Geographic logic** - Checks if the route makes sense or wastes time
2. **Realistic timing** - Verifies activities aren't over-packed
3. **Budget accuracy** - Confirms cost estimates align with budget level
4. **Personalization** - Ensures the itinerary matches stated interests

Minimum approval threshold is 8/10. Uses LoopAgent to run up to 3 refinement cycles if needed.

## Sample output

For a 10-day Tokyo trip in cherry blossom season, the system generates output like this:

**Day 1: Shinjuku District**
- 10:00 AM: Arrive at Narita Airport, take Narita Express to Shinjuku (¥3,200, 75 minutes)
- 12:30 PM: Lunch at Ichiran Ramen Shinjuku (¥1,500)
- 1:30 PM: Tokyo Metropolitan Government Building observation deck (free admission)
- 3:00 PM: Shinjuku Gyoen National Garden (¥500 entrance) - prime cherry blossom viewing location
- 6:30 PM: Dinner at Omoide Yokocho - traditional yakitori and izakaya district (¥3,500)
- 8:00 PM: Explore Kabukicho entertainment district

**Daily cost estimate**: ¥10,700 (~$72 USD)

Note that all activities stay within the Shinjuku area for efficient planning. The itinerary includes specific restaurants with estimated prices, transportation details, and timing rather than vague suggestions.

## Technical implementation

**Production patterns demonstrated:**
- Sequential agent workflow (Research → Plan → Review)
- LoopAgent pattern for iterative refinement
- Session and Memory management (InMemorySessionService, InMemoryMemoryService)
- Asynchronous execution using run_async()
- Exponential backoff retry logic for handling API rate limits
- Proper error handling and validation

**Model configuration**: Uses gemini-2.5-flash-lite (fast and efficient) with configurable retry logic:

```python
retry_config = HttpRetryOptions(
    attempts=5,
    exp_base=7,  # Exponential backoff: 1s → 7s → 49s → 343s → 2401s
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)
```

**Unique features**:
- **File parsing**: Can parse PDF, Excel, Word, and text files from friends' trips to incorporate their experiences
- **Multi-city planning**: Handles Tokyo→Kyoto→Osaka style trips with optimized city sequencing and transition days
- **Google Maps integration**: Auto-generates searchable links for all locations (no API key needed)
- **Weather API with fallback**: Uses OpenWeatherMap when available, gracefully falls back to seasonal knowledge otherwise

## Technical challenges encountered

**Challenge 1: Model compatibility**  
The gemini-2.5-flash-lite model doesn't support function calling (tools). I adapted the agents to use a knowledge-based approach with detailed prompting instead of external tool calls. This works well for common destinations.

**Challenge 2: Placeholder output**  
Initially the system ran without errors but generated placeholder data like "Location: None" and "Activity 1.1". The Planning Agent was correctly generating detailed content, but the output formatter was displaying empty structured fields instead of the actual generated text. Fixed by prioritizing the `generated_itinerary` field which contains the model's full response.

**Challenge 3: API rate limiting**  
Google's free tier has strict rate limits. Implemented exponential backoff retry logic so the system handles 429 errors gracefully rather than failing.

**Challenge 4: Geographic optimization**  
Getting an LLM to think spatially requires explicit guidance. I added instructions like "5 minute walk = 400 meters" and "cluster attractions by district". The models have geographic knowledge from training data, but they need structured prompts to apply it consistently.

## Evaluation results

The automated evaluator provides these scores:

| Metric | Score | Explanation |
|--------|-------|-------------|
| Performance | 5.5/10 | Takes 3-4 minutes for thorough analysis |
| Quality | 6.6/10 | Conservative scoring mechanism |
| Feature Coverage | 5.7/10 | Knowledge-based approach without external tools |
| User Satisfaction | 10/10 | Generates actionable, detailed itineraries |

**Why the moderate scores?**

The evaluation measures technical metrics rather than output usefulness. The system prioritizes thoroughness over speed, taking 3-4 minutes to research, plan, and refine. The actual itineraries are detailed and specific - the scores don't fully capture the practical utility of having a well-planned trip with specific restaurants, realistic schedules, and optimized routing.

## Limitations and future improvements

**Current limitations:**

Weather API is optional - works with or without it. Cost estimates are approximations derived from the model's knowledge and should be independently verified. There's no real-time checking for restaurant availability or attraction hours. Google Maps links are searches rather than direct place links. The system works best for well-known destinations where the model has good training data.

**Testing needs:**

The project would benefit from more extensive testing, particularly around:
- Cost estimate accuracy across different budget levels
- Recommendation relevance for various destination types
- Geographic optimization for different city layouts
- Handling of edge cases (holidays, special events, unusual requests)

**Potential improvements:**

- ✅ ~~Multi-city itineraries~~ (implemented!)
- ✅ ~~Weather API integration~~ (implemented!)
- ✅ ~~Google Maps links~~ (implemented!)
- Interactive refinement through conversational interface
- Real-time pricing APIs for flights and hotels
- Live availability checking for restaurants and attractions
- Direct Google Maps place links (requires Places API)
- User feedback loop to improve recommendations
- Expanded validation for current information accuracy

## What I learned

**Agent specialization is effective**: Breaking the problem into Research, Planning, and Review roles makes each agent simpler and more focused. Each agent does one thing well rather than trying to handle everything.

**Iterative refinement matters**: First drafts often have issues. The LoopAgent pattern with 2-3 refinement cycles significantly improves quality. The Review Agent catches problems that would make an itinerary impractical.

**Prompt engineering is critical**: There's a large difference between "plan a trip" and providing detailed frameworks with explicit rules. Clear instructions about clustering by neighborhood and calculating realistic travel times make LLMs much more useful.

**Production patterns add robustness**: Using proper sessions, memory, async patterns, and retry logic requires more initial effort but creates a system that handles errors gracefully rather than breaking on the first problem.

**LLMs have surprising geographic knowledge**: Gemini understands Tokyo's layout reasonably well - it knows which neighborhoods are adjacent, which metro lines connect different areas, and where major landmarks are located. With the right prompting, it can apply this knowledge effectively.

## Technical stack

**Framework**: Google ADK (Agent Development Kit)  
**Model**: Gemini 2.5 Flash Lite (configurable)  
**Language**: Python 3.10+

**Key libraries:**
- `google-adk` - Multi-agent orchestration
- `pydantic` - Data validation and type safety
- `rich` - Terminal UI formatting
- `PyPDF2`, `openpyxl`, `python-docx` - File parsing

**Project structure:**
```
src/
├── agents/       # Four specialized agents
├── models/       # Pydantic data models
├── tools/        # File parser, weather estimator, formatter
├── utils/        # Model helper with retry logic
├── evaluation/   # Quality metrics
├── config.py     # Configuration management
└── main_capstone.py  # Entry point
```

The codebase is organized with about 35 files total - focused and maintainable.

## Course requirements demonstrated

✅ Multi-agent system (4 agents)  
✅ Sequential workflow pattern  
✅ Loop agent implementation (Review with refinement)  
✅ Sessions and Memory management  
✅ Asynchronous execution patterns  
✅ Error handling and retry logic  
✅ Observability (metrics and logging)  
✅ Automated evaluation  
✅ Clean, organized code structure  
✅ Comprehensive documentation  

## How to use

**Quick setup:**

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Get Google API key from:
# https://aistudio.google.com/app/api-keys

# Optional: Get weather API key from:
# https://openweathermap.org/api (free tier)

# Create .env file
GOOGLE_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_weather_key  # optional

# Run the planner
python3 -m src.main_capstone examples/sample_input.yaml
```

Processing takes 3-5 minutes. Results are saved to `output/itinerary_*.md`.

**Input format:**

```yaml
destination: "Tokyo"
dates:
  start_date: "2026-03-20"
  end_date: "2026-04-05"

preferences:
  interests: ["temples", "food", "cherry blossoms"]
  pace_preference: "moderate"
  budget_level: "mid-range"
  
reference_files:  # optional
  - "examples/japan_trips/friend_tokyo.pdf"
```

## Performance characteristics

Typical execution for a 10-day trip:
- Research: 45 seconds
- Planning: 60 seconds
- Review: 3 iterations at ~20 seconds each
- Total: ~260 seconds (4-5 minutes)

The system generates:
- 10 days of detailed plans
- 4-6 activities per day
- Specific restaurant recommendations with estimated prices
- Geographic clustering for efficient routing
- Daily budget breakdowns
- Practical tips and backup options

## Final thoughts

This project solves a real problem - I actually need this for my upcoming trip. Most course projects are demonstrations, but this one has practical utility despite its current limitations.

The multi-agent approach works well. Each agent has a clear responsibility, and the LoopAgent pattern catches issues that would otherwise produce impractical itineraries.

Main takeaway: LLMs are powerful but need structure. The agents work because they have clear frameworks and explicit rules, not just general instructions.

I also learned that gemini-2.5-flash-lite is quite capable even without tool support. The knowledge-based approach with detailed prompting produces good results for well-known destinations.

The moderate evaluation scores reflect technical limitations (speed, lack of real-time data) rather than practical usefulness. For planning a real trip, having a detailed itinerary with specific recommendations and optimized routing is valuable even if it takes a few minutes to generate.

---

**Project repository**: [your-repo-link-here]

**Note**: This is a learning project and work in progress. Consider it a proof of concept that demonstrates multi-agent patterns rather than a production-ready travel planning service. Always verify information (especially costs and availability) before making travel decisions.

Built for the 5-Days AI Agents course capstone. If it helps with your trip planning, that's excellent.
