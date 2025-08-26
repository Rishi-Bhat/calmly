
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    password: str
    moods: List["Mood"] = Relationship(back_populates="owner")

class Mood(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    mood: int
    commentary: str
    user_id: int = Field(foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="moods")
    journals: List["Journal"] = Relationship(back_populates="mood")

class Journal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    title: str
    content: str
    mood_id: int = Field(foreign_key="mood.id")
    mood: Optional["Mood"] = Relationship(back_populates="journals")