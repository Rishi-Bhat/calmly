
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    name: str
    email: str
    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class UserInDB(UserRead):
    password: str

# Mood Schemas
class MoodBase(BaseModel):
    mood: int
    commentary: str
    model_config = ConfigDict(from_attributes=True)

class MoodCreate(MoodBase):
    user_id: int

class MoodRead(MoodBase):
    id: int
    date: datetime
    user_id: int

# Journal Schemas
class JournalBase(BaseModel):
    title: str
    content: str
    model_config = ConfigDict(from_attributes=True)

class JournalCreate(JournalBase):
    mood_id: int

class JournalRead(JournalBase):
    id: int
    date: datetime
    mood_id: int