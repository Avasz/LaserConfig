from pydantic import BaseModel
from typing import Optional

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

    class Config:
        orm_mode = True
        from_attributes = True
