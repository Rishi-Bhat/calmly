

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def init_session():
    SQLModel.metadata.create_all(bind=engine)

def get_session():
    with Session(engine) as session:
        yield session
