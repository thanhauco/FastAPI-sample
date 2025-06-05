from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import List, Optional
import os
import jwt
from jose import JWTError, jwt

# Security configurations
SECRET_KEY = "your-secret-key-keep-it-secret"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database setup
DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    items = relationship("DBItem", back_populates="owner")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    items = relationship("DBItem", back_populates="category")

class DBItem(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    quantity = Column(Integer)
    image_src = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("Category", back_populates="items")
    owner = relationship("User", back_populates="items")

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class ItemBase(BaseModel):
    name: str
    quantity: int
    category_id: Optional[int] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    image_src: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="Inventory API")

# Security functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/users/", response_model=User)
def create_user(user: UserCreate, db: SessionLocal = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Category routes
@app.post("/categories/", response_model=Category)
def create_category(category: CategoryCreate, db: SessionLocal = Depends(get_db)):
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@app.get("/categories/", response_model=List[Category])
def read_categories(skip: int = 0, limit: int = 100, db: SessionLocal = Depends(get_db)):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

# Item routes with authentication
@app.post("/items/", response_model=Item)
def create_item(
    item: ItemCreate,
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = DBItem(**item.model_dump(), owner_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=List[Item])
def read_items(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(DBItem).filter(DBItem.owner_id == current_user.id)
    
    if category_id:
        query = query.filter(DBItem.category_id == category_id)
    if search:
        query = query.filter(DBItem.name.ilike(f"%{search}%"))
    
    items = query.offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=Item)
def read_item(
    item_id: int,
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(DBItem).filter(
        DBItem.id == item_id,
        DBItem.owner_id == current_user.id
    ).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=Item)
def update_item(
    item_id: int,
    item: ItemCreate,
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(DBItem).filter(
        DBItem.id == item_id,
        DBItem.owner_id == current_user.id
    ).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(DBItem).filter(
        DBItem.id == item_id,
        DBItem.owner_id == current_user.id
    ).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}

# Statistics endpoint
@app.get("/statistics/")
def get_statistics(
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_items = db.query(func.count(DBItem.id)).filter(
        DBItem.owner_id == current_user.id
    ).scalar()
    
    total_quantity = db.query(func.sum(DBItem.quantity)).filter(
        DBItem.owner_id == current_user.id
    ).scalar() or 0
    
    category_stats = db.query(
        Category.name,
        func.count(DBItem.id).label('item_count'),
        func.sum(DBItem.quantity).label('total_quantity')
    ).join(DBItem).filter(
        DBItem.owner_id == current_user.id
    ).group_by(Category.name).all()
    
    return {
        "total_items": total_items,
        "total_quantity": total_quantity,
        "category_statistics": [
            {
                "category": stat.name,
                "item_count": stat.item_count,
                "total_quantity": stat.total_quantity
            }
            for stat in category_stats
        ]
    }

# File upload endpoint
@app.post("/items/{item_id}/upload-image")
async def upload_item_image(
    item_id: int,
    file: UploadFile = File(...),
    db: SessionLocal = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_item = db.query(DBItem).filter(
        DBItem.id == item_id,
        DBItem.owner_id == current_user.id
    ).first()
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