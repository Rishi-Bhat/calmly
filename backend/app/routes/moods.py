
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app import crud, schemas, models
from app.database import get_session
from app.auth import get_current_user

router = APIRouter(prefix="/users/{user_id}/moods", tags=["moods"])

@router.post("/", response_model=schemas.MoodRead)
def create_mood(
    user_id: int, 
    mood: schemas.MoodCreate, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to create mood for this user")
    return crud.create_mood(user_id, session, mood)

@router.get("/", response_model=List[schemas.MoodRead])
def get_all_moods_by_user(
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view moods for this user")
    return crud.get_all_moods_by_user(session, user_id)

@router.get("/{id}/", response_model=schemas.MoodRead)
def get_mood(
    user_id: int, 
    id: int, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.get_mood(session, user_id, id)

@router.put("/{id}/", response_model=schemas.MoodRead)
def update_mood(
    user_id: int, 
    id: int, 
    mood_update: schemas.MoodCreate, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return crud.update_mood(session, user_id, id, mood_update)

@router.delete("/{id}", response_model=schemas.MoodRead)
def delete_mood(
    user_id: int, 
    id: int, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    session_mood = crud.delete_mood(session, user_id, id)
    if session_mood is None:
        raise HTTPException(status_code=404, detail="Mood not found")
    return session_mood

