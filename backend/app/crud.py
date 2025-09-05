from sqlmodel import Session, select
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ------------------ User ------------------------------
def get_users(session: Session):
    statement = select(models.User)
    return session.exec(statement).all()

def get_user(session: Session, user_id: int):
    return session.get(models.User, user_id)

def get_user_by_username(session: Session, name: str):
    statement = select(models.User).where(models.User.name == name)
    return session.exec(statement).first()

def create_user(session: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(name=user.name, email=user.email, password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def update_user(session: Session, user_id: int, user_update: schemas.UserCreate):
    user = session.get(models.User, user_id)
    if user is None:
        return None
    user.name = user_update.name
    user.email = user_update.email
    user.password = pwd_context.hash(user_update.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

def delete_user(session: Session, user_id: int):
    user = session.get(models.User, user_id)
    if user is None:
        return None
    session.delete(user)
    session.commit()
    return user

# ----------------- Mood -----------------------------
def create_mood(user_id: int, session: Session, mood: schemas.MoodCreate):
    session_mood = models.Mood(
        mood=mood.mood,
        commentary=mood.commentary,
        user_id=user_id
    )
    session.add(session_mood)
    session.commit()
    session.refresh(session_mood)
    return session_mood

def get_all_moods_by_user(session: Session, user_id: int):
    statement = select(models.Mood).where(models.Mood.user_id == user_id)
    return session.exec(statement).all()

def get_mood(session: Session, user_id: int, id: int):
    statement = select(models.Mood).where(models.Mood.user_id == user_id, models.Mood.id == id)
    return session.exec(statement).first()

def update_mood(session: Session, user_id: int, id: int, mood_update: schemas.MoodCreate):
    statement = select(models.Mood).where(models.Mood.id == id, models.Mood.user_id == user_id)
    mood = session.exec(statement).first()
    if mood is None:
        return None
    mood.mood = mood_update.mood
    mood.commentary = mood_update.commentary
    session.add(mood)
    session.commit()
    session.refresh(mood)
    return mood

def delete_mood(session: Session, user_id: int, id: int):
    statement = select(models.Mood).where(models.Mood.id == id, models.Mood.user_id == user_id)
    mood = session.exec(statement).first()
    if mood is None:
        return None
    session.delete(mood)
    session.commit()
    return mood

# ----------------------- Journal -----------------------------
def create_journal(mood_id: int, session: Session, journal: schemas.JournalCreate):
    session_journal = models.Journal(
        title=journal.title,
        content=journal.content,
        mood_id=mood_id
    )
    session.add(session_journal)
    session.commit()
    session.refresh(session_journal)
    return session_journal

def get_all_journals_by_mood(session: Session, mood_id: int):
    statement = select(models.Journal).where(models.Journal.mood_id == mood_id)
    return session.exec(statement).all()

def get_journal(session: Session, mood_id: int, id: int):
    statement = select(models.Journal).where(models.Journal.mood_id == mood_id, models.Journal.id == id)
    return session.exec(statement).first()

def update_journal(session: Session, mood_id: int, id: int, journal_update: schemas.JournalCreate):
    statement = select(models.Journal).where(models.Journal.id == id, models.Journal.mood_id == mood_id)
    journal = session.exec(statement).first()
    if journal is None:
        return None
    journal.title = journal_update.title
    journal.content = journal_update.content
    session.add(journal)
    session.commit()
    session.refresh(journal)
    return journal

def delete_journal(session: Session, mood_id: int, id: int):
    statement = select(models.Journal).where(models.Journal.id == id, models.Journal.mood_id == mood_id)
    journal = session.exec(statement).first()
    if journal is None:
        return None
    session.delete(journal)
    session.commit()
    return journal