import os
import shutil
import uuid
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
import schemas

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

app = FastAPI(title="Laser Settings Vault")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/api/materials", response_model=List[schemas.Material])
def get_materials(db: Session = Depends(get_db)):
    return db.query(models.Material).all()

@app.post("/api/materials", response_model=schemas.Material)
def create_material(material: schemas.MaterialCreate, db: Session = Depends(get_db)):
    db_material = models.Material(**material.dict())
    db.add(db_material)
    db.commit()
    db.refresh(db_material)
    return db_material

@app.put("/api/materials/{material_id}", response_model=schemas.Material)
def update_material(material_id: int, material: schemas.MaterialCreate, db: Session = Depends(get_db)):
    db_material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    for k, v in material.dict().items():
        setattr(db_material, k, v)
    db.commit()
    db.refresh(db_material)
    return db_material

@app.delete("/api/materials/{material_id}")
def delete_material(material_id: int, db: Session = Depends(get_db)):
    db_material = db.query(models.Material).filter(models.Material.id == material_id).first()
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    db.delete(db_material)
    db.commit()
    return {"ok": True}

@app.post("/api/entries", response_model=schemas.EntryLog)
async def create_entry(
    material_id: int = Form(...),
    task_type: str = Form(...),
    speed: float = Form(...),
    power: float = Form(...),
    frequency_passes: str = Form(...),
    rating: int = Form(...),
    holding_tabs: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    is_pinned: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    image_path = None
    if image and image.filename:
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        image_path = f"uploads/{filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    db_entry = models.EntryLog(
        material_id=material_id,
        task_type=task_type,
        speed=speed,
        power=power,
        frequency_passes=frequency_passes,
        rating=rating,
        holding_tabs=holding_tabs,
        notes=notes,
        is_pinned=is_pinned,
        image_path=image_path
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get("/api/entries", response_model=List[schemas.EntryLog])
def read_entries(
    skip: int = 0, limit: int = 100, 
    search: Optional[str] = None, 
    task_type: Optional[str] = None,
    rating: Optional[int] = None,
    db: Session = Depends(get_db)
):
    from sqlalchemy.orm import joinedload
    query = db.query(models.EntryLog).options(joinedload(models.EntryLog.material))
    
    if search:
        query = query.join(models.Material).filter(
            models.Material.base_type.ilike(f"%{search}%") | 
            models.Material.name_brand.ilike(f"%{search}%")
        )
    if task_type:
        query = query.filter(models.EntryLog.task_type == task_type)
    if rating:
        query = query.filter(models.EntryLog.rating == rating)
    
    entries = query.order_by(models.EntryLog.id.desc()).offset(skip).limit(limit).all()
    return entries

@app.get("/api/entries/{entry_id}", response_model=schemas.EntryLog)
def read_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.EntryLog).filter(models.EntryLog.id == entry_id).first()
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return db_entry

@app.put("/api/entries/{entry_id}", response_model=schemas.EntryLog)
async def update_entry(
    entry_id: int,
    material_id: int = Form(...),
    task_type: str = Form(...),
    speed: float = Form(...),
    power: float = Form(...),
    frequency_passes: str = Form(...),
    rating: int = Form(...),
    holding_tabs: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    is_pinned: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    db_entry = db.query(models.EntryLog).filter(models.EntryLog.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if image and image.filename:
        if db_entry.image_path and os.path.exists(db_entry.image_path):
            os.remove(db_entry.image_path)
            
        ext = image.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        image_path = f"uploads/{filename}"
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        db_entry.image_path = image_path

    db_entry.material_id = material_id
    db_entry.task_type = task_type
    db_entry.speed = speed
    db_entry.power = power
    db_entry.frequency_passes = frequency_passes
    db_entry.rating = rating
    db_entry.holding_tabs = holding_tabs
    db_entry.notes = notes
    db_entry.is_pinned = is_pinned

    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.put("/api/entries/{entry_id}/pin", response_model=schemas.EntryLog)
def toggle_pin(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.EntryLog).filter(models.EntryLog.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db_entry.is_pinned = not db_entry.is_pinned
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.post("/api/entries/{entry_id}/comments", response_model=schemas.Comment)
def create_comment(entry_id: int, comment: schemas.CommentCreate, db: Session = Depends(get_db)):
    db_entry = db.query(models.EntryLog).filter(models.EntryLog.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    db_comment = models.Comment(entry_id=entry_id, text=comment.text)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@app.delete("/api/entries/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    db_entry = db.query(models.EntryLog).filter(models.EntryLog.id == entry_id).first()
    if not db_entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    if db_entry.image_path and os.path.exists(db_entry.image_path):
        os.remove(db_entry.image_path)
    db.delete(db_entry)
    db.commit()
    return {"ok": True}

# Serve standard HTML file at root
from fastapi.responses import FileResponse
@app.get("/")
def read_index():
    return FileResponse("static/index.html")

