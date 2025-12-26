"""Train Search Endpoints"""
from fastapi import APIRouter, Query, HTTPException
from typing import List
from datetime import date

from app.models import Train, TrainSearchParams
from app.database import db

router = APIRouter()


@router.get("", response_model=List[Train])
async def search_trains(
    origin: str = Query(..., description="Origin station"),
    destination: str = Query(..., description="Destination station"),
    date: date = Query(..., description="Journey date (YYYY-MM-DD)")
):
    """
    Search for available trains by route and date.
    
    Returns a list of trains matching the search criteria with available seats.
    """
    trains = db.search_trains(origin, destination, date)
    
    if not trains:
        return []
    
    return trains


@router.get("/all", response_model=List[Train])
async def get_all_trains():
    """
    Get all available trains.
    
    Returns a list of all trains in the system.
    """
    trains = db.get_all_trains()
    return trains


@router.get("/{train_number}", response_model=Train)
async def get_train(train_number: str):
    """
    Get details of a specific train.
    
    Args:
        train_number: Unique train identifier
        
    Returns:
        Train details
    """
    train = db.get_train(train_number)
    
    if not train:
        raise HTTPException(
            status_code=404,
            detail=f"Train {train_number} not found"
        )
    
    return train

