# The Argonauts: AI Trip Planner

*Your AI crew for planning epic journeys*

A multi-agent system for trip planning using Google's Agent Development Kit. Built as a capstone project for the 5-Days AI Agents course.

**Why "The Argonauts"?** In Greek mythology, the Argonauts were Jason's heroic crew on the quest for the Golden Fleece. Like that legendary voyage, this system uses a crew of specialized AI agents working together to plan your journey.

I'm planning a trip to Japan in April and wanted a tool that could actually help me plan it properly - not just generic "visit temples" suggestions. So I built this multi-agent system that creates detailed, day-by-day itineraries with real recommendations, geographic optimization, and budget tracking.

**Status**: Work in progress. While the core functionality works, this project would benefit from more testing and refinement, especially around cost estimates and recommendation accuracy.

## What it does

Takes your trip preferences (destination, dates, interests, budget) and generates a complete day-by-day itinerary with:

- **Multi-city support** - Handles trips like Tokyo→Kyoto→Osaka with optimized transitions
- **Google Maps integration** - Auto-generates searchable links for all locations and directions
- **Real-time weather** - Uses OpenWeatherMap API when available, falls back to seasonal knowledge
- Specific restaurant recommendations with estimated prices
- Geographically optimized routes (keeps you in the same area instead of wasting time on transit)
- Realistic schedules that include travel time and rest periods
- Daily budget breakdowns

## How it works

The system uses 4 AI agents working together:

1. **Research Agent** - Gathers destination information, analyzes weather patterns, finds attractions and restaurants
2. **Planning Agent** - Creates day-by-day schedules with geographic clustering to minimize travel time
3. **Review Agent** - Quality checks the itinerary (realistic timing? sensible routing? accurate budget?). Sends it back for revision if score is below 8/10
4. **Orchestrator** - Coordinates the workflow between agents

The Review Agent runs up to 3 refinement cycles to ensure quality meets minimum standards (8/10 score required for approval).

## Setup

**1. Create a virtual environment (recommended):**

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Get your Google API key:**

Visit https://aistudio.google.com/app/api-keys and create a free API key.

**4. Create a .env file in the project root:**

```bash
# Required
GOOGLE_API_KEY=your_key_here

# Optional - Weather API (for real-time forecasts)
OPENWEATHER_API_KEY=your_openweather_key  # Get free at openweathermap.org/api

# Optional (defaults shown)
MODEL_NAME=gemini-2.5-flash-lite
TEMPERATURE=0.7
MAX_REVIEW_ITERATIONS=3
ENABLE_GOOGLE_MAPS_LINKS=true  # Adds Maps links to output
```

**Weather API setup (optional but recommended):**
1. Go to https://openweathermap.org/api
2. Sign up for free account
3. Get your API key
4. Add to `.env` as `OPENWEATHER_API_KEY`

Without the weather API, the system uses seasonal patterns from the AI model's knowledge (still works, just less precise).

**Configuration options:**

- `MODEL_NAME`: Which Gemini model to use (default: gemini-2.5-flash-lite)
  - `gemini-2.5-flash-lite` - Fast and free (no tool support)
  - `gemini-1.5-flash` - Balanced, supports tools
  - `gemini-1.5-pro` - Most capable, slower
  
- `TEMPERATURE`: Controls response creativity, 0.0-1.0 (default: 0.7)
  - Lower = more focused and consistent
  - Higher = more creative and varied

- `MAX_REVIEW_ITERATIONS`: How many times the Review Agent refines the itinerary (default: 3)

**5. Run the planner:**

```bash
python3 -m src.main_capstone examples/sample_input.yaml
```

The process takes 3-5 minutes as the agents research, plan, and refine the itinerary.

**6. Check your results:**

Find your itinerary in `output/itinerary_YYYYMMDD_HHMMSS.md`

## Input format

Edit `examples/sample_input.yaml` or create your own:

```yaml
destination: "Tokyo"

dates:
  start_date: "2026-03-20"
  end_date: "2026-04-05"

additional_destinations:
  - "Kyoto"
  - "Osaka"

preferences:
  interests:
    - "temples and shrines"
    - "traditional culture"
    - "food"
    - "cherry blossoms"
  
  pace_preference: "moderate"  # relaxed | moderate | fast
  budget_level: "mid-range"    # budget | mid-range | luxury
  dietary_restrictions: []     # e.g., ["vegetarian", "gluten-free"]
  
  special_requests: "Want to see cherry blossoms at their peak!"

# Optional: reference files from friends' trips
reference_files:
  - "examples/japan_trips/friend_tokyo.pdf"
```

## Key features

**Multi-city itineraries**: Properly handles trips to multiple cities (e.g., Tokyo → Kyoto → Osaka). The Planning Agent:
- Sequences cities logically based on geography
- Plans dedicated transition days with Shinkansen details
- Applies neighborhood clustering within each city separately
- Optimizes arrival and departure days

**Google Maps integration**: Automatically generates clickable Maps links for:
- Overview of each city/area
- Directions between locations
- Specific attraction and restaurant searches
- No API key required - just URL generation

**Real-time weather**: Uses OpenWeatherMap API when configured (free tier):
- Actual 5-day forecasts for your travel dates
- Temperature ranges, rain probability, conditions
- Falls back to seasonal knowledge if API unavailable
- Clear indication of data source ("API" vs "AI Knowledge")

**Geographic optimization**: The Planning Agent groups attractions by neighborhood to minimize transit time. For example, Day 1 stays in Shinjuku area, Day 2 explores Harajuku→Shibuya (adjacent neighborhoods), rather than bouncing around the city inefficiently.

**Budget tracking**: Provides estimated costs broken down by day, including accommodation, meals, activities, and transport. Note that these are estimates based on the model's knowledge and should be verified.

**Reference file support**: Can parse PDF, Excel, Word, and text files from friends' trips to learn from their experiences. Also extracts Google Maps and Wanderlog links.

**Quality assurance**: The Review Agent checks each itinerary against strict criteria (geographic logic, realistic timing, budget accuracy, personalization). Minimum score of 8/10 required for approval.

**Automatic retry**: Handles API rate limits gracefully with exponential backoff (5 attempts: 1s → 7s → 49s → 343s → 2401s).

## Example output

For a 10-day Tokyo trip in cherry blossom season:

**Day 1: Shinjuku Area**
- 10:00 AM: Arrive Narita Airport, take Narita Express to Shinjuku (¥3,200, 75 minutes)
- 12:30 PM: Lunch at Ichiran Ramen Shinjuku (¥1,500)
- 1:30 PM: Tokyo Metropolitan Government Building observation deck (free)
- 3:00 PM: Shinjuku Gyoen National Garden (¥500) - prime cherry blossom viewing
- 6:30 PM: Dinner at Omoide Yokocho - yakitori and izakaya (¥3,500)
- 8:00 PM: Explore Kabukicho nightlife district

**Estimated daily cost**: ¥10,700 (~$72 USD)

All activities remain in the Shinjuku area for efficiency. The itinerary includes specific locations, transportation details, estimated costs, and timing.

## Technical implementation

**Framework**: Google ADK (Agent Development Kit)  
**Model**: Gemini 2.5 Flash Lite (configurable)  
**Language**: Python 3.10+

**Production patterns used:**
- Sequential agent workflow (Research → Plan → Review)
- LoopAgent for iterative refinement
- Sessions and Memory (InMemorySessionService, InMemoryMemoryService)
- Async execution (run_async)
- Exponential backoff retry logic
- Proper error handling

**Project structure:**
```
src/
├── agents/              # 4 specialized agents
├── models/              # Pydantic data models
├── tools/               # File parser, weather estimator, formatter
├── utils/               # Model helper with retry logic
├── evaluation/          # Quality metrics
├── config.py           # Configuration management
└── main_capstone.py    # Entry point
```

## Evaluation scores

The automated evaluator rates the system:

| Metric | Score | Notes |
|--------|-------|-------|
| Performance | 5.5/10 | Takes 3-4 minutes for thorough planning |
| Quality | 6.6/10 | Conservative scoring - actual output quality is higher |
| Feature Coverage | 5.7/10 | Knowledge-based approach (no external APIs) |
| User Satisfaction | 10/10 | Generates actionable, detailed itineraries |

The scores measure technical aspects. The actual user experience - receiving a detailed, specific, actionable itinerary - is quite good despite the moderate technical scores. The system prioritizes thoroughness over speed.

## Limitations and areas for improvement

**Current limitations:**
- Weather API is optional - without it, uses seasonal patterns from training data
- Cost estimates are approximations and should be verified with actual prices
- No real-time availability checking for restaurants or attractions
- Limited to destinations the model has good knowledge about
- Google Maps links are searches, not direct place links
- Recommendations need more validation against current information

**Potential improvements:**
- ✅ ~~Multi-city trip planning~~ (implemented!)
- ✅ ~~Weather API integration~~ (implemented!)
- ✅ ~~Google Maps links~~ (implemented!)
- Interactive mode with user feedback during planning
- Real-time price APIs for flights and hotels
- Actual booking links (not just searches)
- Direct Google Maps place links (requires API key)
- More extensive testing and validation
- User feedback loop for improving recommendations

## Why moderate evaluation scores?

**Performance (5.5/10)**: The system takes 3-4 minutes to generate an itinerary. This is slower than instant results but allows for thorough research and multiple refinement cycles.

**Quality (6.6/10)**: The scoring is conservative. The itineraries are detailed and specific, but the evaluator checks for structured completeness rather than content usefulness.

**Feature Coverage (5.7/10)**: Using gemini-2.5-flash-lite means no function calling support. The system relies on the model's internal knowledge rather than external tools.

**User Satisfaction (10/10)**: The actual output - specific restaurants with prices, optimized routes, realistic schedules - is useful for real trip planning.

## Technical challenges solved

**Model compatibility**: gemini-2.5-flash-lite doesn't support function calling, so agents use a knowledge-based approach with detailed prompting instead of tools.

**Output formatting**: Initially generated placeholder data. Fixed by using the `generated_itinerary` field which contains the model's actual response rather than structured placeholders.

**Rate limiting**: Implemented exponential backoff retry logic to handle API rate limits gracefully.

**Geographic optimization**: Added explicit instructions for calculating travel times and clustering by neighborhood, helping the model think geographically.

## Future directions

If I continue developing this:
- Real-time data integration (weather, prices, availability)
- Support for complex multi-city itineraries
- Interactive planning mode with conversational refinement
- Mobile application interface
- Integration with booking platforms
- User feedback system to improve recommendations
- Expanded destination coverage with local expert validation

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Built for the 5-Days AI Agents course capstone project. Thanks to the course creators, Google for the ADK framework, and friends who shared their trip plans as reference material.

---

**Note**: This is a learning project and work in progress. While functional, it would benefit from additional testing and validation, particularly around cost accuracy and current recommendations. Always verify information before making travel decisions.
