"""
AI Service for Gemini Integration
Handles communication with Google Gemini API using JSON mode for reliable output.
"""
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Try to import genai, but don't fail if not installed
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

# Configuration
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_TEMPERATURE = float(os.environ.get("GEMINI_TEMPERATURE", "0.2"))

# Initialize Gemini
if GEMINI_API_KEY and GENAI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)


def get_insights_schema() -> Dict[str, Any]:
    """
    Define the expected JSON schema for insights response.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "overview": {
                "type": "string",
                "description": "A brief, supportive summary of the user's emotional journey"
            },
            "patterns": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string"},
                        "description": {"type": "string"},
                        "observation": {"type": "string"}
                    },
                    "required": ["type", "description", "observation"]
                }
            },
            "themes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "theme": {"type": "string"},
                        "frequency": {"type": "integer"},
                        "description": {"type": "string"}
                    },
                    "required": ["theme", "frequency", "description"]
                }
            },
            "personalized_message": {
                "type": "string",
                "description": "A warm, encouraging, non-judgmental message"
            },
            "key_insights": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5 key observations"
            }
        },
        "required": ["overview", "patterns", "themes", "personalized_message", "key_insights"]
    }


def format_prompt_for_gemini(data_summary: Dict[str, Any]) -> str:
    """
    Format pre-processed statistics into a prompt for Gemini.
    
    Args:
        data_summary: Pre-processed statistics from data_aggregator
        
    Returns:
        Formatted prompt string
    """
    mood_stats = data_summary.get("mood_statistics", {})
    journal_stats = data_summary.get("journal_statistics", {})
    themes = data_summary.get("themes", {})
    correlations = data_summary.get("correlations", [])
    
    # Format themes
    themes_text = "\n".join([
        f"- '{theme}': {count} mentions"
        for theme, count in sorted(themes.items(), key=lambda x: x[1], reverse=True)[:10]
    ]) if themes else "No recurring themes identified"
    
    # Format correlations
    correlations_text = "\n".join([
        f"- {corr.get('description', '')}"
        for corr in correlations[:5]
    ]) if correlations else "No significant correlations identified"
    
    # Format day patterns
    day_patterns = mood_stats.get("day_patterns", {})
    day_patterns_text = "\n".join([
        f"- {day}: Average mood {avg:.1f}/10"
        for day, avg in sorted(day_patterns.items(), key=lambda x: x[1])
    ]) if day_patterns else "Insufficient data for day patterns"
    
    # Trend description
    trend = mood_stats.get("trend", "stable")
    trend_desc = {
        "improving": "showing an upward trend",
        "declining": "showing a downward trend",
        "stable": "relatively stable",
        "insufficient_data": "insufficient data to determine trend",
        "no_data": "no data available"
    }.get(trend, "stable")
    
    # Previous period comparison
    prev_avg = mood_stats.get("previous_average")
    comparison_text = ""
    if prev_avg:
        current_avg = mood_stats.get("average", 0)
        diff = current_avg - prev_avg
        if diff > 0.3:
            comparison_text = f" (improved from {prev_avg:.1f} in the previous period)"
        elif diff < -0.3:
            comparison_text = f" (down from {prev_avg:.1f} in the previous period)"
        else:
            comparison_text = f" (similar to {prev_avg:.1f} in the previous period)"
    
    prompt = f"""You are a compassionate, non-judgmental wellness assistant analyzing mood and journal data.

ANALYSIS PERIOD: {data_summary.get('period_start', 'N/A')} to {data_summary.get('period_end', 'N/A')}
TIME SPAN: Last {data_summary.get('analysis_days', 30)} days

MOOD STATISTICS:
- Average Mood: {mood_stats.get('average', 0):.1f}/10{comparison_text}
- Mood Range: {mood_stats.get('min', 0)}-{mood_stats.get('max', 0)}/10
- Trend: {trend_desc}
- Total Mood Entries: {mood_stats.get('total_entries', 0)}

DAY-OF-WEEK PATTERNS:
{day_patterns_text}

JOURNAL STATISTICS:
- Total Journal Entries: {journal_stats.get('total_entries', 0)}
- Average Entry Length: {journal_stats.get('average_length', 0):.0f} characters
- Entry Frequency: Approximately every {journal_stats.get('entry_frequency_days', 0):.1f} days

RECURRING THEMES (from journal analysis):
{themes_text}

CORRELATIONS OBSERVED:
{correlations_text}

Please provide insights in a supportive, non-judgmental manner. Focus on patterns and observations rather than diagnoses. Be encouraging and emphasize that mood fluctuations are normal.

Provide your response as a JSON object with the following structure:
- overview: A brief summary of their emotional journey
- patterns: Array of observed patterns with type, description, and observation
- themes: Array of recurring themes with theme name, frequency, and description
- personalized_message: A warm, encouraging message
- key_insights: Array of 3-5 key observations as strings
"""
    
    return prompt


def generate_insights_from_stats(data_summary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate insights from pre-processed statistics using Gemini API.
    
    Args:
        data_summary: Pre-processed statistics from data_aggregator
        
    Returns:
        Dictionary containing AI-generated insights
        
    Raises:
        Exception: If API call fails
    """
    if not GENAI_AVAILABLE:
        raise ValueError("google-generativeai package not installed. Install with: pip install google-generativeai")
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured in .env file")
    
    # Check if there's any data to analyze
    mood_stats = data_summary.get("mood_statistics", {})
    if mood_stats.get("total_entries", 0) == 0:
        # Return default insights for users with no data
        return {
            "overview": "You're just starting your wellness journey. As you track your moods and write journal entries, personalized insights will appear here to help you understand your emotional patterns.",
            "patterns": [],
            "themes": [],
            "personalized_message": "Welcome to your wellness tracking journey! Start by logging your first mood entry to begin building insights about your emotional patterns.",
            "key_insights": [
                "No data available yet - start tracking to see insights",
                "Regular mood tracking helps identify patterns over time",
                "Journal entries provide context for understanding your moods"
            ]
        }
    
    try:
        # Initialize model
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config={
                "temperature": GEMINI_TEMPERATURE
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )
        
        # Format prompt with explicit JSON format instructions
        prompt = format_prompt_for_gemini(data_summary)
        
        # Add explicit JSON format requirement to prompt
        json_schema = get_insights_schema()
        prompt += f"""

IMPORTANT: You must respond with ONLY valid JSON, no additional text. The JSON must match this exact structure:
{json.dumps(json_schema, indent=2)}

Respond with ONLY the JSON object, nothing else."""
        
        # Generate response
        response = model.generate_content(prompt)
        
        # Parse JSON response
        insights_json = response.text.strip()
        
        # Remove markdown code blocks if present
        if insights_json.startswith("```json"):
            insights_json = insights_json[7:]
        if insights_json.startswith("```"):
            insights_json = insights_json[3:]
        if insights_json.endswith("```"):
            insights_json = insights_json[:-3]
        insights_json = insights_json.strip()
        
        # Try to extract JSON if there's extra text
        start_idx = insights_json.find('{')
        end_idx = insights_json.rfind('}')
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            insights_json = insights_json[start_idx:end_idx + 1]
        
        # Parse to dict
        insights = json.loads(insights_json)
        
        # Validate required fields
        required_fields = ["overview", "patterns", "themes", "personalized_message", "key_insights"]
        for field in required_fields:
            if field not in insights:
                raise ValueError(f"Missing required field in response: {field}")
        
        return insights
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON response from Gemini: {e}")
    except Exception as e:
        raise Exception(f"Gemini API error: {str(e)}")
