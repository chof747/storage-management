from sqlalchemy import Column, Integer, String
from app.database import Base


class StorageType(Base):
    __tablename__ = "storage_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    printing_strategy = Column(String, nullable=False)
    description = Column(String)
