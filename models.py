from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
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
    comments = relationship("Comment", back_populates="entry", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entry_logs.id"))
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    entry = relationship("EntryLog", back_populates="comments")
