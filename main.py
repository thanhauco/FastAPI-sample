from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os
from typing import List, Optional

# Database setup
DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class DBItem(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    image_src = Column(String, nullable=True)

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class ItemBase(BaseModel):
    name: str
    quantity: int

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    image_src: Optional[str] = None

    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="Inventory API")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Routes
@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: SessionLocal = Depends(get_db)):
    db_item = DBItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
    items = db.query(DBItem).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: SessionLocal = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate, db: SessionLocal = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: SessionLocal = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

# File upload endpoint
@app.post("/items/{item_id}/upload-image")
async def upload_item_image(item_id: int, file: UploadFile = File(...), db: SessionLocal = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save the file
    file_path = os.path.join("uploads", file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Update item with image path
    db_item.image_src = file.filename
    db.commit()
    db.refresh(db_item)
    
    return {"filename": file.filename} 