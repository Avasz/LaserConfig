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

@app.post("/api/entries", response_model=schemas.EntryLog)
async def create_entry(
    material_name: str = Form(...),
    task_type: str = Form(...),
    speed: float = Form(...),
    power: float = Form(...),
    frequency_passes: str = Form(...),
    rating: int = Form(...),
    notes: Optional[str] = Form(None),
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
        material_name=material_name,
        task_type=task_type,
        speed=speed,
        power=power,
        frequency_passes=frequency_passes,
        rating=rating,
        notes=notes,
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
    query = db.query(models.EntryLog)
    if search:
        query = query.filter(models.EntryLog.material_name.ilike(f"%{search}%"))
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

