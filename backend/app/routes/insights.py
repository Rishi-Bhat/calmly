"""
Insights Route
Handles AI insights generation with asynchronous background processing.
"""
import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlmodel import Session, select
from app import models, schemas
from app.database import get_session
from app.auth import get_current_user
from app.services.insights_generator import generate_insights_background_task
import json

router = APIRouter(prefix="/users/{user_id}/insights", tags=["insights"])

# Configuration
INSIGHTS_FRESHNESS_HOURS = int(os.environ.get("INSIGHTS_FRESHNESS_HOURS", 24))
ANALYSIS_PERIOD_DAYS = int(os.environ.get("ANALYSIS_PERIOD_DAYS", 30))


def is_insight_fresh(generated_at: datetime) -> bool:
    """
    Check if an insight is still fresh (within freshness window).
    
    Args:
        generated_at: When the insight was generated
        
    Returns:
        True if insight is fresh, False otherwise
    """
    if not generated_at:
        return False
    
    age = datetime.utcnow() - generated_at
    return age.total_seconds() < (INSIGHTS_FRESHNESS_HOURS * 3600)


@router.get("/", response_model=schemas.InsightsResponse)
async def get_insights(
    user_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get AI insights for a user.
    
    - If fresh insights exist: Returns 200 with insights
    - If insights are stale or missing: Returns 202 and triggers background generation
    
    Args:
        user_id: User ID (must match authenticated user)
        background_tasks: FastAPI background tasks
        session: Database session
        current_user: Authenticated user from JWT
        
    Returns:
        InsightsResponse with status and data
    """
    # Verify user can only access their own insights
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own insights"
        )
    
    # Check for existing insights
    existing_insight = session.exec(
        select(models.AIInsights).where(models.AIInsights.user_id == user_id)
    ).first()
    
    # If fresh insight exists, return it immediately
    if existing_insight and existing_insight.status == "completed" and is_insight_fresh(existing_insight.generated_at):
        try:
            insights_dict = json.loads(existing_insight.insights_json)
            return schemas.InsightsResponse(
                status="completed",
                insights=insights_dict,
                generated_at=existing_insight.generated_at,
                analysis_period_start=existing_insight.analysis_period_start,
                analysis_period_end=existing_insight.analysis_period_end
            )
        except json.JSONDecodeError:
            # If JSON is invalid, regenerate
            pass
    
    # If insight is stale, missing, or failed, trigger background generation
    # Update or create record with generating status
    if existing_insight:
        existing_insight.status = "generating"
    else:
        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=ANALYSIS_PERIOD_DAYS)
        existing_insight = models.AIInsights(
            user_id=user_id,
            insights_json="{}",
            status="generating",
            analysis_period_start=period_start,
            analysis_period_end=period_end
        )
        session.add(existing_insight)
    
    session.commit()
    session.refresh(existing_insight)
    
    # Add background task to generate insights
    # FastAPI BackgroundTasks runs after response is sent
    # The background task will create its own database session
    background_tasks.add_task(
        generate_insights_background_task,
        user_id=user_id,
        analysis_days=ANALYSIS_PERIOD_DAYS
    )
    
    # Return 202 Accepted with generating status
    return schemas.InsightsResponse(
        status="generating",
        message="Generating your insights... This may take a few moments.",
        generated_at=None,
        analysis_period_start=existing_insight.analysis_period_start,
        analysis_period_end=existing_insight.analysis_period_end
    )
