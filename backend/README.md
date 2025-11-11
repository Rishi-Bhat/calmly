# Calmly - Mood Tracker API

A backend API built with FastAPI, SQLModel, and PostgreSQL that allows users to track their moods and link them to journal entries.

## Features

- **User Management**: Create, update, and delete users
- **Mood Tracking**: Users can log moods with a numeric value and a commentary
- **Journal Entries**: Link journal entries to specific moods
- **Resources**: Curated soothing content (music, breathing exercises, articles) with mood-based recommendations
- **AI Insights**: Personalized mood analysis and pattern recognition using Google Gemini AI (optional)
- **Game Sessions**: Track therapeutic games and activities (breathing exercises, matching games, etc.)
- **Authentication**: JWT-based authentication for secure access
- **Database**: PostgreSQL for persistent storage
- **Testing**: Comprehensive test suite using pytest (28 tests)

## Installation and Usage

### 1. Clone the repository

```bash
git clone https://github.com/Rishi-Bhat/calmly.git
cd calmly
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL database

Make sure PostgreSQL is installed and running, then create a database:

```bash
# On macOS/Linux
psql -U postgres
CREATE DATABASE calmly;
\q

# On Windows (using psql in Command Prompt)
psql -U postgres
CREATE DATABASE calmly;
\q
```

### 5. Set up environment variables

Copy the example environment file and update with your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/calmly
SECRET_KEY=generate-a-secure-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Optional: For AI Insights (get free key at https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.2
INSIGHTS_FRESHNESS_HOURS=24
ANALYSIS_PERIOD_DAYS=30
```

**Important:** Never commit your `.env` file to version control!

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

### 7. API Documentation

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 8. Running Tests

```bash
pytest -v
```

## API Overview

### Authentication

- **POST /auth/register**: Register a new user
- **POST /auth/login**: Obtain JWT token

### Users

- **GET /users/**: List users (auth required)
- **GET /users/{user_id}**: Get user details (auth required)
- **PUT /users/{user_id}**: Update user (auth required)
- **DELETE /users/{user_id}**: Delete user (auth required)

### Moods

- **POST /users/{user_id}/moods/**: Create mood entry (auth required)
- **GET /users/{user_id}/moods/**: List user's moods (auth required)
- **GET /users/{user_id}/moods/{mood_id}**: Get specific mood (auth required)
- **PUT /users/{user_id}/moods/{mood_id}**: Update mood (auth required)
- **DELETE /users/{user_id}/moods/{mood_id}**: Delete mood (auth required)

### Journals

- **POST /users/{user_id}/moods/{mood_id}/journals/**: Create journal entry (auth required)
- **GET /users/{user_id}/moods/{mood_id}/journals/**: List journals for mood (auth required)
- **GET /users/{user_id}/moods/{mood_id}/journals/{journal_id}**: Get specific journal (auth required)
- **PUT /users/{user_id}/moods/{mood_id}/journals/{journal_id}**: Update journal (auth required)
- **DELETE /users/{user_id}/moods/{mood_id}/journals/{journal_id}**: Delete journal (auth required)

### Resources

- **GET /resources/**: List all resources (public)
- **GET /resources/?mood=stressed**: Filter resources by mood (public)
- **GET /resources/recommend?mood=stressed&limit=5**: Get mood-based recommendations (public)
- **GET /resources/{resource_id}**: Get specific resource (public)
- **POST /resources/**: Create resource (public)
- **DELETE /resources/{resource_id}**: Delete resource (public)

### AI Insights (Requires API Key)

- **GET /users/{user_id}/insights/**: Get AI-powered mood insights (auth required)
  - Analyzes mood trends, patterns, and themes
  - Returns personalized recommendations
  - Background processing with caching

### Games

- **POST /users/{user_id}/games/**: Create game session (auth required)
- **GET /users/{user_id}/games/**: List user's game sessions (auth required)
- **GET /users/{user_id}/games/{game_id}**: Get specific game session (auth required)

## Security Notes

- All user-specific endpoints require JWT authentication
- JWT tokens must be included in the `Authorization: Bearer <token>` header
- Users can only access their own data (ownership validation)
- Passwords are hashed using bcrypt
- Resources endpoints are public (consider adding admin protection for POST/DELETE)

## AI Insights (Optional)

The AI insights feature uses Google Gemini to analyze mood and journal data. To enable:

1. Get a free API key: https://makersuite.google.com/app/apikey
2. Add to `.env`: `GEMINI_API_KEY=your-key-here`
3. Restart the server

**Without API key:** All features work except AI insights (returns friendly error message)

**With API key:** Full AI-powered mood analysis and personalized recommendations

## Testing

Run the test suite:

```bash
pytest test_main.py -v
```

**Test Coverage:**

- 28 tests covering all endpoints
- Auth, users, moods, journals, resources, games, insights
- 100% pass rate

---

Feel free to contribute or open issues!
