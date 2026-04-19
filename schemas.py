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

class MaterialBase(BaseModel):
    base_type: str
    name_brand: Optional[str] = None
    thickness_mm: Optional[float] = None
    grade: Optional[str] = None

class MaterialCreate(MaterialBase):
    pass

class Material(MaterialBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True

class EntryLogBase(BaseModel):
    material_id: int
    is_pinned: bool = False
    task_type: str
    speed: float
    power: float
    frequency_passes: str
    rating: int
    notes: Optional[str] = None
    image_path: Optional[str] = None
    holding_tabs: Optional[str] = None

class EntryLogCreate(EntryLogBase):
    pass

class EntryLog(EntryLogBase):
    id: int
    comments: List[Comment] = []
    material: Optional[Material] = None

    class Config:
        orm_mode = True
        from_attributes = True
