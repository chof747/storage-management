from app.database import SessionLocal


def get_db():
    """Ingest the database into an API endpoint"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
