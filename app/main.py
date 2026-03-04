from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Destination

app = FastAPI(title="Travel Without Barriers API")


@app.get("/")
def root():
    return {"message": "Travel Without Barriers API"}


# GET /destinations
@app.get("/destinations")
def get_destinations(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    destinations = db.query(Destination).offset(offset).limit(limit).all()
    return destinations


# GET /destinations/{id}
@app.get("/destinations/{destination_id}")
def get_destination(destination_id: int, db: Session = Depends(get_db)):

    destination = db.query(Destination).filter(
        Destination.id == destination_id
    ).first()

    if not destination:
        raise HTTPException(status_code=404, detail="Destination not found")

    return destination