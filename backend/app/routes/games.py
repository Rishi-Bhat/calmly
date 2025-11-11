
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app import crud, schemas
from app.database import get_session
from app.auth import get_current_user
from app import models

router = APIRouter(prefix="/users/{user_id}/games", tags=["games"])

@router.post("/", response_model=schemas.GameSessionRead)
def create_game_session(
    user_id: int, 
    game_session: schemas.GameSessionCreate, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Create a new game session"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only create game sessions for yourself")
    return crud.create_game_session(user_id, session, game_session)

@router.get("/", response_model=List[schemas.GameSessionRead])
def get_all_game_sessions(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Get all game sessions for a user"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only access your own game sessions")
    return crud.get_all_game_sessions_by_user(session, user_id)

@router.get("/{game_id}", response_model=schemas.GameSessionRead)
def get_game_session(
    user_id: int,
    game_id: int,
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    """Get a specific game session"""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="You can only access your own game sessions")
    game_session = crud.get_game_session(session, user_id, game_id)
    if game_session is None:
        raise HTTPException(status_code=404, detail="Game session not found")
    return game_session
