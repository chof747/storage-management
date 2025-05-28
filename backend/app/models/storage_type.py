from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class StorageType(Base):
    __tablename__ = "storage_type"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    printing_strategy = Column(String, nullable=True)
    description = Column(String)
    storage_elements = relationship("StorageElement", back_populates="storage_type")
