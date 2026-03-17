from sqlmodel import create_engine, Session, SQLModel
from app.resume_model import Resume

DATABASE_URL = "sqlite:///jobpost.db"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)
