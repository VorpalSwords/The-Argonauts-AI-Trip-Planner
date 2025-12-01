# Example Output

This directory contains sample output from The Argonauts trip planner.

## Files

- `example_tokyo_trip.md` - Full itinerary for 10-day Tokyo trip (April 2025)
- `example_tokyo_trip.json` - Same itinerary in JSON format (machine-readable)
- `example_tokyo_trip.txt` - Plain text version (no markdown formatting)

## How These Were Generated

These outputs were created by running:

```bash
python3 -m src.planner_main examples/sample_input.yaml
```

With the following configuration:
- **Destination**: Tokyo, Japan
- **Dates**: April 1-10, 2025 (cherry blossom season)
- **Budget**: Mid-range
- **Interests**: Culture, food, temples, cherry blossoms
- **Dietary**: Vegetarian, no spicy food
- **Reference file**: Friend's 7-day Tokyo trip (examples/reference/example_tokyo_trip.txt)

## What to Look For

### Research Quality
- Weather forecast integration (cherry blossom timing)
- Recommendations learned from reference file (e.g., TeamLab Borderless, Shibuya Sky)
- Geographic clustering (activities grouped by neighborhood)

### Planning Intelligence
- Multiple restaurant options per meal (2-3 choices)
- Dietary accommodations clearly marked
- Transit recommendations (Suica card, day passes)
- Realistic timing with rest periods

### Multi-Format Export
All three formats are generated simultaneously from the same planning session.

