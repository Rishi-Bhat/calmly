import os
from uuid import uuid4
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, create_engine, Session
from app.schemas import ResourceBase, ResourceCreate, ResourceRead

# Database setup
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./calmly_resources.db")
engine = create_engine(DATABASE_URL, echo=False)

# Model
class Resource(ResourceBase, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Session dependency
def get_session():
    with Session(engine) as session:
        yield session

# Helper: match mood tags
def _matches_mood_tags(resource_mood_tags: Optional[str], target_mood: str) -> bool:
    if not resource_mood_tags:
        return False
    tags = [t.strip().lower() for t in resource_mood_tags.split(",")]
    return target_mood.lower() in tags

# Seed data
SEED_DATA = [
    {
        "title": "4-4-8 Breathing",
        "type": "breathing",
        "url": "https://example.com/4-4-8.mp3",
        "duration_seconds": 60,
        "mood_tags": "stressed,anxious",
        "description": "A calming 1-minute breathing exercise.",
    },
    {
        "title": "Soothing Piano",
        "type": "music",
        "url": "https://youtu.be/example-piano",
        "duration_seconds": 600,
        "mood_tags": "stressed,sad,tired",
        "description": "Relaxing 10-minute piano music.",
    },
    {
        "title": "Grounding 5-4-3-2-1",
        "type": "exercise",
        "url": "https://example.com/54321",
        "duration_seconds": 180,
        "mood_tags": "anxious,panic",
        "description": "A 3-minute grounding technique.",
    },
]

def init_db_and_seed():
    """Create tables and seed data if empty."""
    SQLModel.metadata.create_all(bind=engine)
    
    with Session(engine) as session:
        count = session.query(Resource).count()
        if count == 0:
            for data in SEED_DATA:
                resource = Resource(**data)
                session.add(resource)
            session.commit()

# Business logic functions
def list_resources_logic(session: Session, limit: int = 50, mood: Optional[str] = None) -> List[Resource]:
    """Fetch all resources, optionally filter by mood."""
    query = session.query(Resource).limit(limit)
    resources = query.all()
    
    if mood:
        resources = [r for r in resources if _matches_mood_tags(r.mood_tags, mood)]
    
    return resources

def recommend_resources_logic(session: Session, mood: Optional[str] = None, limit: int = 5) -> List[Resource]:
    """Recommend resources based on mood."""
    fallback_types = {
        "stressed": ["breathing", "music", "exercise"],
        "anxious": ["breathing", "exercise", "guided_meditation"],
        "sad": ["music", "guided_meditation", "article"],
        "tired": ["music", "sleep"],
    }
    
    all_resources = session.query(Resource).all()
    
    # Try to match mood tags
    if mood:
        matched = [r for r in all_resources if _matches_mood_tags(r.mood_tags, mood)]
        if matched:
            return matched[:limit]
    
    # Fallback by type
    types = fallback_types.get(mood.lower() if mood else "", ["music", "breathing", "exercise"])
    filtered = [r for r in all_resources if r.type in types]
    return filtered[:limit]

def create_resource_logic(session: Session, resource: ResourceCreate) -> Resource:
    """Create and save a new resource."""
    db_resource = Resource(**resource.dict())
    session.add(db_resource)
    session.commit()
    session.refresh(db_resource)
    return db_resource

def get_resource_logic(session: Session, resource_id: str) -> Optional[Resource]:
    """Fetch a single resource by ID."""
    return session.query(Resource).filter(Resource.id == resource_id).first()

def delete_resource_logic(session: Session, resource_id: str) -> bool:
    """Delete a resource by ID."""
    resource = session.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        return False
    session.delete(resource)
    session.commit()
    return True

# Initialize on import
init_db_and_seed()