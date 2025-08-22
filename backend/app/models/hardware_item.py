from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base
from .printable import Printable


class HardwareItem(Base, Printable):
    __tablename__ = "hardware_items"

    id = Column(Integer, primary_key=True, index=True)
    hwtype = Column(String, nullable=False)
    label = Column(String)
    main_metric = Column(String, nullable=False)
    secondary_metric = Column(String)
    length = Column(Float)
    reorder = Column(Boolean)
    reorder_link = Column(String)
    detailed_description = Column(String)
    storage_element_id = Column(
        Integer, ForeignKey("storage_element.id"), nullable=False
    )
    storage_element = relationship("StorageElement", back_populates="hardware_items")
