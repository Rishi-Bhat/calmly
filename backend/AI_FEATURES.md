# AI Features Integration

## New Features Added

### 1. AI-Powered Insights

Analyzes user mood and journal data to provide personalized insights using Google Gemini AI.

**Endpoint:** `GET /users/{user_id}/insights`

**Features:**

- Mood trend analysis (improving, declining, stable)
- Day-of-week patterns
- Theme extraction from journal entries
- Correlation identification
- Personalized, supportive messages
- Background processing (non-blocking)

**How it works:**

1. First request triggers background analysis
2. Returns 202 (Accepted) with "generating" status
3. Subsequent requests return completed insights (cached for 24 hours)
4. Automatically regenerates when stale

### 2. Game Sessions Tracking

Track therapeutic games and activities (breathing exercises, matching games, etc.)

**Endpoints:**

- `POST /users/{user_id}/games` - Create game session
- `GET /users/{user_id}/games` - List all game sessions
- `GET /users/{user_id}/games/{game_id}` - Get specific session

**Game Types:**

- matching
- breathing
- grounding
- etc.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

New packages:

- `google-generativeai` - For Gemini AI
- `python-dateutil` - For date handling

### 2. Get Gemini API Key (Optional)

1. Visit https://makersuite.google.com/app/apikey
2. Create a free API key
3. Add to `.env`:

```
GEMINI_API_KEY=your-api-key-here
```

### 3. Configuration (Optional)

Add to `.env`:

```
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.2
INSIGHTS_FRESHNESS_HOURS=24
ANALYSIS_PERIOD_DAYS=30
```

## Without API Key

The features work gracefully without an API key:

**Games:** ✅ Fully functional (no AI needed)

**Insights:**

- Data aggregation works (mood stats, patterns, themes)
- AI generation will return friendly error message
- Add API key later to enable AI insights

## Database Changes

New tables automatically created:

- `aiinsights` - Stores generated insights
- `gamesession` - Stores game activity

## API Documentation

After starting the server, visit:

- http://localhost:8000/docs

New sections:

- **insights** - AI insights endpoints
- **games** - Game tracking endpoints

## Example Usage

### Get Insights

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/users/1/insights
```

Response (first time):

```json
{
  "status": "generating",
  "message": "Generating your insights... This may take a few moments."
}
```

Response (after generation):

```json
{
  "status": "completed",
  "insights": {
    "overview": "Your mood has been relatively stable...",
    "patterns": [...],
    "themes": [...],
    "personalized_message": "...",
    "key_insights": [...]
  },
  "generated_at": "2025-11-11T17:00:00",
  "analysis_period_start": "2025-10-12T00:00:00",
  "analysis_period_end": "2025-11-11T17:00:00"
}
```

### Track Game Session

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "game_type": "breathing",
    "score": 100,
    "duration_seconds": 300,
    "completed": true,
    "user_id": 1
  }' \
  http://localhost:8000/users/1/games
```

## Security

- All endpoints require JWT authentication
- Users can only access their own insights and games
- Ownership validation on all operations

## Performance

- Insights generation runs in background (non-blocking)
- Efficient database queries (no N+1 problem)
- Caching prevents unnecessary AI calls
- Configurable freshness window

## What's Analyzed

**Mood Statistics:**

- Average mood over period
- Mood range (min/max)
- Trend direction
- Comparison with previous period
- Day-of-week patterns

**Journal Analysis:**

- Entry frequency
- Average length
- Theme extraction (work, sleep, exercise, family, friends, health, stress, hobbies, food, travel)
- Correlations with mood levels

**Insights Generated:**

- Overview of emotional journey
- Observed patterns
- Recurring themes
- Personalized encouragement
- Key observations

## Troubleshooting

**"GEMINI_API_KEY not configured"**

- Add API key to `.env` file
- Or use without AI (games still work, insights show error message)

**"google-generativeai package not installed"**

- Run `pip install -r requirements.txt`

**Insights stuck on "generating"**

- Check application logs for errors
- Verify API key is valid
- Ensure sufficient mood/journal data exists

## Future Enhancements

- More game types
- Mood prediction
- Personalized resource recommendations based on insights
- Export insights as PDF
- Insights history/timeline
