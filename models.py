from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, index=True)
    base_type = Column(String, nullable=False) # Solid Wood, Plywood, MDF, Acrylic, Leather, Other
    name_brand = Column(String, nullable=True) # Optional for generic MDF
    thickness_mm = Column(Float, nullable=True)
    grade = Column(String, nullable=True) # Optional, mostly for Ply
    
    entries = relationship("EntryLog", back_populates="material", cascade="all, delete-orphan")

class EntryLog(Base):
    __tablename__ = "entry_logs"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    is_pinned = Column(Integer, default=False) # SQLite boolean
    task_type = Column(String, nullable=False) # "Cutting" or "Engraving"
    speed = Column(Float, nullable=False)
    power = Column(Float, nullable=False)
    frequency_passes = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)
    holding_tabs = Column(Text, nullable=True)
    
    comments = relationship("Comment", back_populates="entry", cascade="all, delete-orphan")
    material = relationship("Material", back_populates="entries")

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(Integer, ForeignKey("entry_logs.id"))
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    entry = relationship("EntryLog", back_populates="comments")
