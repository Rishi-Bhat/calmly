# Calmly - Mood Tracker API

A backend API built with FastAPI, SQLModel, and PostgreSQL that allows users to track their moods and link them to journal entries.

## Features

- **User Management**: Create, update, and delete users
- **Mood Tracking**: Users can log moods with a numeric value and a commentary
- **Journal Entries**: Link journal entries to specific moods
- **Authentication**: JWT-based authentication for secure access
- **Database**: PostgreSQL for persistent storage
- **Testing**: Comprehensive test suite using pytest

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

- **/auth/register**: Register a new user
- **/auth/login**: Obtain JWT token
- **/users/**: List users (auth required)
- **/users/{user_id}**: Get, update, or delete a user (auth required)
- **/users/{user_id}/moods/**: Create/list moods for a user (auth required)
- **/users/{user_id}/moods/{mood_id}/journals/**: Create/list journals for a mood (auth required)

## Security Notes

- All endpoints except registration and login require authentication.
- JWT tokens must be included in the `Authorization: Bearer <token>` header.

---

Feel free to contribute or open issues!
