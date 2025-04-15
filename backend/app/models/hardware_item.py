from sqlalchemy import Boolean, Column, Integer, String, Float
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