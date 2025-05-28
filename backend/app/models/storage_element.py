from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class StorageElement(Base):
    __tablename__ = "storage_element"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    position = Column(String, nullable=False)
    storage_type_id = Column(Integer, ForeignKey("storage_type.id"), nullable=False)
    description = Column(String)
    hardware_items = relationship("HardwareItem", back_populates="storage_element")
    storage_type = relationship("StorageType", back_populates="storage_elements")
