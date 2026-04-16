from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommentBase(BaseModel):
    text: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    entry_id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class EntryLogBase(BaseModel):
    material_name: str
    task_type: str
    speed: float
    power: float
    frequency_passes: str
    rating: int
    notes: Optional[str] = None
    image_path: Optional[str] = None

class EntryLogCreate(EntryLogBase):
    pass

class EntryLog(EntryLogBase):
    id: int
    comments: List[Comment] = []

    class Config:
        orm_mode = True
        from_attributes = True
