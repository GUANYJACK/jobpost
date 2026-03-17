from sqlmodel import create_engine, Session, SQLModel
from app.resume_model import Resume

DATABASE_URL = "sqlite:///jobpost.db"
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)
    # Ensure schema updates for columns added later (simple sqlite migration)
    with engine.connect() as conn:
        # sqlite does not automatically add new columns on metadata changes; ensure scraped_at exists
        result = conn.execute("PRAGMA table_info('application')")
        columns = [row[1] for row in result.fetchall()]
        if 'scraped_at' not in columns:
            conn.execute("ALTER TABLE application ADD COLUMN scraped_at DATETIME")


def get_session():
    return Session(engine)
