"""
Insights Generator Background Task
Handles the background generation of AI insights.
"""
import os
import json
from datetime import datetime, timedelta
from sqlmodel import Session, select
from app import models, database
from app.services.data_aggregator import prepare_data_for_ai
from app.services.ai_service import generate_insights_from_stats


def generate_insights_background_task(
    user_id: int,
    analysis_days: int = 30
) -> None:
    """
    Background task to generate AI insights for a user.
    This function does the slow work: fetches data, pre-processes, calls Gemini, and saves results.
    
    Args:
        user_id: User ID
        analysis_days: Number of days to analyze (default 30)
    """
    # Create a new database session for the background task
    with Session(database.engine) as session:
        try:
            # Update status to generating
            existing_insight = session.exec(
                select(models.AIInsights).where(models.AIInsights.user_id == user_id)
            ).first()
            
            if existing_insight:
                existing_insight.status = "generating"
            else:
                # Create new record with generating status
                period_end = datetime.utcnow()
                period_start = period_end - timedelta(days=analysis_days)
                existing_insight = models.AIInsights(
                    user_id=user_id,
                    insights_json="{}",
                    status="generating",
                    analysis_period_start=period_start,
                    analysis_period_end=period_end
                )
                session.add(existing_insight)
            
            session.commit()
            
            # Fetch and pre-process data
            data_summary = prepare_data_for_ai(session, user_id, analysis_days)
            
            # Generate insights using Gemini
            insights = generate_insights_from_stats(data_summary)
            
            # Update period boundaries from actual data
            period_start = datetime.fromisoformat(data_summary.get("period_start", datetime.utcnow().isoformat()))
            period_end = datetime.fromisoformat(data_summary.get("period_end", datetime.utcnow().isoformat()))
            
            # Save insights to database
            existing_insight.insights_json = json.dumps(insights)
            existing_insight.generated_at = datetime.utcnow()
            existing_insight.status = "completed"
            existing_insight.analysis_period_start = period_start
            existing_insight.analysis_period_end = period_end
            
            session.add(existing_insight)
            session.commit()
            
        except Exception as e:
            # Update status to failed
            try:
                existing_insight = session.exec(
                    select(models.AIInsights).where(models.AIInsights.user_id == user_id)
                ).first()
                
                if existing_insight:
                    existing_insight.status = "failed"
                    # Store error message in insights_json
                    error_insights = {
                        "error": True,
                        "message": f"Failed to generate insights: {str(e)}",
                        "overview": "We encountered an issue generating your insights. Please try again later.",
                        "patterns": [],
                        "themes": [],
                        "personalized_message": "We're having trouble generating insights right now. Please try refreshing in a moment.",
                        "key_insights": []
                    }
                    existing_insight.insights_json = json.dumps(error_insights)
                    session.add(existing_insight)
                    session.commit()
            except:
                pass  # If we can't update, just log the error
            
            # Re-raise to log in application logs
            raise
