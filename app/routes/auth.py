from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from app import models, schemas, database
from app.auth import get_user_by_email, get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserRead)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_session)):
	db_user = get_user_by_email(db, user.email)
	if db_user:
		raise HTTPException(status_code=400, detail="Email already registered")
	hashed_password = get_password_hash(user.password)
	new_user = models.User(name=user.name, email=user.email, password=hashed_password)
	db.add(new_user)
	db.commit()
	db.refresh(new_user)
	return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_session)):
	user = get_user_by_email(db, form_data.username)
	if not user or not verify_password(form_data.password, user.password):
		raise HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
	access_token = create_access_token(data={"sub": user.email})
	return {"access_token": access_token, "token_type": "bearer"}
