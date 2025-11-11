
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app import crud, schemas, models
from app.database import get_session
from app.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[schemas.UserRead])
def get_users(
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_users(session)

@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user(session, user_id)

@router.get("/name/{name}", response_model=schemas.UserRead)
def get_user_by_name(
    name: str, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_user_by_username(session, name)

@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: int, 
    user_update: schemas.UserCreate, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    session_user = crud.update_user(session, user_id, user_update)
    if session_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return session_user

@router.delete("/{user_id}", response_model=schemas.UserRead)
def delete_user(
    user_id: int, 
    session: Session = Depends(get_session),
    current_user: models.User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")
    session_user = crud.delete_user(session, user_id)
    if session_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return session_user
