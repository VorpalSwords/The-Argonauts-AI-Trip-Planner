# Reference Files for Trip Planning

Place your reference files here to help the agent learn from friends' trips!

## Supported File Types

1. **Text Files** (`.txt`)
   - Simple itineraries
   - Day-by-day plans
   - Notes from friends

2. **PDF Documents** (`.pdf`)
   - Printed itineraries
   - Travel guides
   - Booking confirmations

3. **Excel Spreadsheets** (`.xlsx`)
   - Budget breakdowns
   - Day-by-day schedules
   - Cost tracking

4. **Word Documents** (`.docx`)
   - Detailed trip reports
   - Recommendations
   - Packing lists

5. **Link Files** (`.txt` containing URLs)
   - Google Maps saved places
   - Wanderlog shared itineraries
   - Other travel planning links

## How to Use

1. Add your reference files to this folder
2. Update `examples/sample_input.yaml`:

```yaml
reference_files:
  - "examples/reference/friend_tokyo_trip.pdf"
  - "examples/reference/budget_spreadsheet.xlsx"
  - "examples/reference/google_maps_tokyo.txt"
```

3. Run the agent - it will parse these files and use them for context!

## Example Files

Create files like:

### `friend_tokyo_trip.txt`
```
Tokyo Trip - March 2024
Day 1: Shibuya crossing, Meiji Shrine, shopping
Day 2: Senso-ji Temple, Asakusa, Tokyo Skytree
Day 3: Day trip to Mount Fuji
...
```

### `google_maps_tokyo.txt`
```
https://www.google.com/maps/@35.6762,139.6503,12z
My Tokyo saved places - check out these amazing restaurants!
```

### `wanderlog_itinerary.txt`
```
https://wanderlog.com/view/abc123
My 10-day Japan itinerary with day-by-day plans
```

## Installation (Optional)

For full file parsing support, install:

```bash
pip install PyPDF2 openpyxl python-docx
```

Or it's already in `requirements.txt`!

## Benefits

✅ **Learn from Experience** - See what worked for friends
✅ **Avoid Mistakes** - Learn what to skip
✅ **Get Ideas** - Discover hidden gems
✅ **Budget Better** - Real cost examples
✅ **Save Time** - Don't reinvent the wheel!

The agent will analyze these files and incorporate the best ideas into your personalized itinerary! 🎉

