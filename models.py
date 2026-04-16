from sqlalchemy import Column, Integer, String, Float, Text
from database import Base

class EntryLog(Base):
    __tablename__ = "entry_logs"

    id = Column(Integer, primary_key=True, index=True)
    material_name = Column(String, index=True, nullable=False)
    task_type = Column(String, nullable=False) # "Cutting" or "Engraving"
    speed = Column(Float, nullable=False)
    power = Column(Float, nullable=False)
    frequency_passes = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)

