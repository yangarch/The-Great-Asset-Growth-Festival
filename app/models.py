from sqlalchemy import Column, Integer, String, Date, Float
from .database import Base
from pydantic import BaseModel
from datetime import date as date_type

# SQLAlchemy Model
class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(Date)
    amount = Column(Float)

# Pydantic Models for API
class AssetBase(BaseModel):
    name: str
    date: date_type
    amount: float

class AssetCreate(BaseModel):
    name: str
    date: date_type
    amount: float

class AssetResponse(AssetCreate):
    id: int

    class Config:
        orm_mode = True
