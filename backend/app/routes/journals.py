
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from app import crud, schemas
from app.database import get_session

router = APIRouter(prefix="/users/{user_id}/moods/{mood_id}/journals", tags=["journals"])

@router.post("/", response_model=schemas.JournalRead)
def create_journal(user_id: int, mood_id: int, journal: schemas.JournalCreate, session: Session = Depends(get_session)):
    return crud.create_journal(mood_id, session, journal)

@router.get("/", response_model=List[schemas.JournalRead])
def get_all_journals_by_mood(user_id: int, mood_id: int, session: Session = Depends(get_session)):
    return crud.get_all_journals_by_mood(session, mood_id)

@router.get("/{id}", response_model=schemas.JournalRead)
def get_journal(user_id: int, mood_id: int, id: int, session: Session = Depends(get_session)):
    return crud.get_journal(session, mood_id, id)

@router.put("/{id}", response_model=schemas.JournalRead)
def update_journal(user_id: int, mood_id: int, id: int, journal_update: schemas.JournalCreate, session: Session = Depends(get_session)):
    return crud.update_journal(session, mood_id, id, journal_update)

@router.delete("/{id}", response_model=schemas.JournalRead)
def delete_journal(user_id: int, mood_id: int, id: int, session: Session = Depends(get_session)):
    session_journal = crud.delete_journal(session, mood_id, id)
    if session_journal is None:
        raise HTTPException(status_code=404, detail="journal not found")
    return session_journal