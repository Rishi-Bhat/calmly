from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.resources_logic import (
    get_session,
    list_resources_logic,
    recommend_resources_logic,
    create_resource_logic,
    get_resource_logic,
    delete_resource_logic,
)
from app.schemas import ResourceCreate, ResourceRead

router = APIRouter(prefix="/resources", tags=["resources"])

@router.get("/", response_model=list[ResourceRead])
def list_resources(limit: int = 50, mood: Optional[str] = None, session: Session = Depends(get_session)):
    """List all resources, optionally filter by mood."""
    return list_resources_logic(session, limit, mood)

@router.get("/recommend", response_model=list[ResourceRead])
def recommend_resources(mood: Optional[str] = None, limit: int = 5, session: Session = Depends(get_session)):
    """Recommend resources based on mood."""
    return recommend_resources_logic(session, mood, limit)

@router.post("/", response_model=ResourceRead)
def create_resource(resource: ResourceCreate, session: Session = Depends(get_session)):
    """Add a new resource."""
    return create_resource_logic(session, resource)

@router.get("/{resource_id}", response_model=ResourceRead)
def get_resource(resource_id: str, session: Session = Depends(get_session)):
    """Fetch a single resource."""
    resource = get_resource_logic(session, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource

@router.delete("/{resource_id}")
def delete_resource(resource_id: str, session: Session = Depends(get_session)):
    """Delete a resource."""
    if not delete_resource_logic(session, resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"status": "ok"}