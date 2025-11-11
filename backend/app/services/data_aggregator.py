"""
Data Aggregator Service
Efficiently fetches and pre-processes user data for AI analysis.
Uses single JOIN query to avoid N+1 problem.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from sqlmodel import Session, select
from sqlalchemy import func
from app import models


def fetch_user_data_efficiently(
    session: Session,
    user_id: int,
    days: int = 30
) -> Tuple[List[models.Mood], List[models.Journal]]:
    """
    Fetch all moods and journals for a user within the specified period using efficient JOIN.
    
    Args:
        session: Database session
        user_id: User ID
        days: Number of days to look back (default 30)
        
    Returns:
        Tuple of (moods list, journals list)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Fetch moods within the period
    mood_statement = select(models.Mood).where(
        models.Mood.user_id == user_id,
        models.Mood.date >= cutoff_date
    ).order_by(models.Mood.date)
    
    moods = list(session.exec(mood_statement).all())
    
    # Fetch all journals for these moods in one query
    mood_ids = [mood.id for mood in moods] if moods else []
    journals = []
    
    if mood_ids:
        journal_statement = select(models.Journal).where(
            models.Journal.mood_id.in_(mood_ids)
        ).order_by(models.Journal.date)
        journals = list(session.exec(journal_statement).all())
    
    return moods, journals


def calculate_mood_statistics(
    moods: List[models.Mood],
    previous_period_moods: List[models.Mood] = None
) -> Dict[str, Any]:
    """
    Calculate mood statistics from mood entries.
    
    Args:
        moods: List of mood entries
        previous_period_moods: Optional list of moods from previous period for comparison
        
    Returns:
        Dictionary of mood statistics
    """
    if not moods:
        return {
            "average": 0,
            "min": 0,
            "max": 0,
            "trend": "no_data",
            "previous_average": 0,
            "day_patterns": {},
            "total_entries": 0
        }
    
    mood_values = [mood.mood for mood in moods]
    avg_mood = sum(mood_values) / len(mood_values)
    min_mood = min(mood_values)
    max_mood = max(mood_values)
    
    # Calculate trend (comparing first half vs second half)
    trend_diff = 0
    if len(moods) >= 4:
        mid_point = len(moods) // 2
        first_half_avg = sum(mood_values[:mid_point]) / mid_point
        second_half_avg = sum(mood_values[mid_point:]) / (len(moods) - mid_point)
        trend_diff = second_half_avg - first_half_avg
        
        if trend_diff > 0.5:
            trend = "improving"
        elif trend_diff < -0.5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    # Calculate previous period average if provided
    prev_avg = 0
    if previous_period_moods:
        prev_values = [mood.mood for mood in previous_period_moods]
        prev_avg = sum(prev_values) / len(prev_values) if prev_values else 0
    
    # Calculate day-of-week patterns
    day_patterns = {}
    for mood in moods:
        day_name = mood.date.strftime('%A')
        if day_name not in day_patterns:
            day_patterns[day_name] = []
        day_patterns[day_name].append(mood.mood)
    
    # Average mood per day
    day_averages = {
        day: sum(values) / len(values)
        for day, values in day_patterns.items()
    }
    
    return {
        "average": round(avg_mood, 2),
        "min": min_mood,
        "max": max_mood,
        "trend": trend,
        "trend_difference": round(trend_diff, 2),
        "previous_average": round(prev_avg, 2) if prev_avg > 0 else None,
        "day_patterns": day_averages,
        "total_entries": len(moods)
    }


def extract_journal_themes(journals: List[models.Journal]) -> Dict[str, int]:
    """
    Extract recurring themes from journal entries using basic keyword analysis.
    
    Args:
        journals: List of journal entries
        
    Returns:
        Dictionary mapping themes to frequency counts
    """
    if not journals:
        return {}
    
    # Common wellness-related keywords/themes
    theme_keywords = {
        "work": ["work", "job", "office", "colleague", "project", "deadline", "meeting"],
        "sleep": ["sleep", "tired", "rest", "insomnia", "wake", "dream"],
        "exercise": ["exercise", "workout", "gym", "run", "walk", "fitness", "sport"],
        "family": ["family", "parent", "sibling", "relative", "mom", "dad", "brother", "sister"],
        "friends": ["friend", "social", "hangout", "party", "gathering"],
        "health": ["health", "doctor", "medical", "pain", "illness", "medication"],
        "stress": ["stress", "anxious", "worried", "overwhelmed", "pressure"],
        "hobby": ["hobby", "interest", "creative", "art", "music", "reading"],
        "food": ["food", "eat", "meal", "cooking", "restaurant", "hungry"],
        "travel": ["travel", "trip", "vacation", "journey", "flight"]
    }
    
    theme_counts = {theme: 0 for theme in theme_keywords.keys()}
    
    # Count theme occurrences in journal titles and content
    all_text = " ".join([
        f"{journal.title} {journal.content}".lower()
        for journal in journals
    ])
    
    for theme, keywords in theme_keywords.items():
        for keyword in keywords:
            theme_counts[theme] += all_text.count(keyword)
    
    # Filter out themes with zero occurrences
    return {theme: count for theme, count in theme_counts.items() if count > 0}


def identify_correlations(
    moods: List[models.Mood],
    journals: List[models.Journal],
    themes: Dict[str, int]
) -> List[Dict[str, Any]]:
    """
    Identify correlations between moods and other factors.
    
    Args:
        moods: List of mood entries
        journals: List of journal entries
        themes: Dictionary of theme frequencies
        
    Returns:
        List of correlation observations
    """
    correlations = []
    
    if not moods:
        return correlations
    
    # Create mood-to-journal mapping
    mood_journals = {mood.id: [] for mood in moods}
    for journal in journals:
        if journal.mood_id in mood_journals:
            mood_journals[journal.mood_id].append(journal)
    
    # Find correlations between low moods and themes
    low_mood_threshold = 5
    high_mood_threshold = 7
    
    low_mood_themes = {}
    high_mood_themes = {}
    
    for mood in moods:
        journals_for_mood = mood_journals.get(mood.id, [])
        mood_text = " ".join([
            f"{j.title} {j.content}".lower()
            for j in journals_for_mood
        ])
        
        if mood.mood <= low_mood_threshold:
            for theme in themes.keys():
                if theme in mood_text:
                    low_mood_themes[theme] = low_mood_themes.get(theme, 0) + 1
        elif mood.mood >= high_mood_threshold:
            for theme in themes.keys():
                if theme in mood_text:
                    high_mood_themes[theme] = high_mood_themes.get(theme, 0) + 1
    
    # Add correlation observations
    for theme, count in low_mood_themes.items():
        if count >= 2:
            correlations.append({
                "type": "negative_correlation",
                "description": f"Mood dips (≤5) correlate with journal entries mentioning '{theme}'",
                "frequency": count
            })
    
    for theme, count in high_mood_themes.items():
        if count >= 2:
            correlations.append({
                "type": "positive_correlation",
                "description": f"Higher moods (≥7) correlate with journal entries mentioning '{theme}'",
                "frequency": count
            })
    
    # Day-of-week correlations
    day_patterns = {}
    for mood in moods:
        day_name = mood.date.strftime('%A')
        if day_name not in day_patterns:
            day_patterns[day_name] = []
        day_patterns[day_name].append(mood.mood)
    
    avg_mood = sum(m.mood for m in moods) / len(moods)
    for day, mood_values in day_patterns.items():
        day_avg = sum(mood_values) / len(mood_values)
        if day_avg < avg_mood - 1:
            correlations.append({
                "type": "day_pattern",
                "description": f"Average mood on {day}s is {day_avg:.1f}/10 (below overall average of {avg_mood:.1f})",
                "day": day,
                "average": round(day_avg, 1)
            })
    
    return correlations


def prepare_data_for_ai(
    session: Session,
    user_id: int,
    analysis_days: int = 30
) -> Dict[str, Any]:
    """
    Main function to fetch, process, and prepare user data for AI analysis.
    
    Args:
        session: Database session
        user_id: User ID
        analysis_days: Number of days to analyze (default 30)
        
    Returns:
        Dictionary of pre-processed statistics ready for AI
    """
    # Fetch current period data
    moods, journals = fetch_user_data_efficiently(session, user_id, analysis_days)
    
    # Fetch previous period data for comparison
    previous_cutoff = datetime.utcnow() - timedelta(days=analysis_days * 2)
    previous_moods, _ = fetch_user_data_efficiently(
        session,
        user_id,
        analysis_days * 2
    )
    previous_period_moods = [
        m for m in previous_moods
        if m.date < (datetime.utcnow() - timedelta(days=analysis_days))
    ]
    
    # Calculate statistics
    mood_stats = calculate_mood_statistics(moods, previous_period_moods)
    themes = extract_journal_themes(journals)
    correlations = identify_correlations(moods, journals, themes)
    
    # Determine period boundaries
    period_start = min(mood.date for mood in moods) if moods else datetime.utcnow()
    period_end = max(mood.date for mood in moods) if moods else datetime.utcnow()
    
    # Prepare summary data
    summary = {
        "period_start": period_start.isoformat(),
        "period_end": period_end.isoformat(),
        "analysis_days": analysis_days,
        "mood_statistics": mood_stats,
        "journal_statistics": {
            "total_entries": len(journals),
            "average_length": sum(len(j.content) for j in journals) / len(journals) if journals else 0,
            "entry_frequency_days": analysis_days / len(journals) if journals else 0
        },
        "themes": themes,
        "correlations": correlations
    }
    
    return summary
