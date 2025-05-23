# app/scripts/init_db.py

from app.database import Base, engine
import app.models  # required to register models


def init_db():
    Base.metadata.create_all(bind=engine)
