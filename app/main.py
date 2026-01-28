from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="The Great Asset Growth Festival API")

@app.post("/api/assets", response_model=models.AssetResponse)
def create_asset(asset: models.AssetCreate, db: Session = Depends(database.get_db)):
    db_asset = models.Asset(name=asset.name, date=asset.date, amount=asset.amount)
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return db_asset

@app.get("/api/assets", response_model=List[models.AssetResponse])
def read_assets(skip: int = 0, limit: int = 1000, db: Session = Depends(database.get_db)):
    assets = db.query(models.Asset).offset(skip).limit(limit).all()
    return assets

@app.get("/")
def read_root():
    return {"message": "Welcome to The Great Asset Growth Festival API"}
