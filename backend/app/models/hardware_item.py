from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, text
from sqlalchemy.orm import relationship
from app.database import Base


class HardwareItem(Base):
    __tablename__ = "hardware_items"

    id = Column(Integer, primary_key=True, index=True)
    hwtype = Column(String, nullable=False)
    main_metric = Column(String, nullable=False)
    secondary_metric = Column(String)
    length = Column(Float)
    storage_element = Column(String)
    reorder = Column(Boolean)
    reorder_link = Column(String)
    storage_element_id = Column(
        Integer, ForeignKey("storage_element.id"), nullable=False
    )
    storage_element = relationship("StorageElement", back_populates="hardware_items")
    queued_for_printing = Column(
        Boolean, default=False, nullable=False, server_default=text("0")
    )
