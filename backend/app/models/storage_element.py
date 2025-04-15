from sqlalchemy import Boolean, Column, Integer, String, Float
from app.database import Base

class StorageElement(Base):
    __tablename__ = "storage_element"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    position = Column(String, nullable=False)
    storage_type = Column(String, nullable=False)
    description = Column(String)
