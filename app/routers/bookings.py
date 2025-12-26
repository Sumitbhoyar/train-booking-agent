"""Booking Management Endpoints"""
from fastapi import APIRouter, HTTPException, Path
from datetime import date

from app.models import (
    Booking, 
    BookingCreate, 
    BookingResponse,
    CancelBookingResponse
)
from app.database import db

router = APIRouter()


@router.post("", response_model=BookingResponse, status_code=201)
async def create_booking(booking_data: BookingCreate):
    """
    Create a new train booking.
    
    Args:
        booking_data: Booking information including train number, passenger details, and journey date
        
    Returns:
        Created booking with confirmation details
    """
    # Validate train exists
    train = db.get_train(booking_data.train_number)
    if not train:
        raise HTTPException(
            status_code=404,
            detail=f"Train {booking_data.train_number} not found"
        )
    
    # Check seat availability
    if train["available_seats"] <= 0:
        raise HTTPException(
            status_code=400,
            detail=f"No seats available on train {booking_data.train_number}"
        )
    
    # Create booking
    booking = db.create_booking(
        train_number=booking_data.train_number,
        passenger_name=booking_data.passenger_name,
        email=booking_data.email,
        journey_date=booking_data.journey_date
    )
    
    if not booking:
        raise HTTPException(
            status_code=500,
            detail="Failed to create booking"
        )
    
    return {
        "booking": booking,
        "message": f"Booking confirmed for {booking_data.passenger_name} on train {booking_data.train_number}"
    }


@router.get("/{booking_id}", response_model=Booking)
async def get_booking_status(
    booking_id: str = Path(..., description="Booking ID to retrieve")
):
    """
    Retrieve booking status by booking ID.
    
    Args:
        booking_id: Unique booking identifier
        
    Returns:
        Booking details and current status
    """
    booking = db.get_booking(booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Booking {booking_id} not found"
        )
    
    return booking


@router.delete("/{booking_id}", response_model=CancelBookingResponse)
async def cancel_booking(
    booking_id: str = Path(..., description="Booking ID to cancel")
):
    """
    Cancel an existing booking.
    
    Args:
        booking_id: Unique booking identifier
        
    Returns:
        Cancellation confirmation
    """
    booking = db.cancel_booking(booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=404,
            detail=f"Booking {booking_id} not found"
        )
    
    return {
        "booking_id": booking_id,
        "status": "cancelled",
        "message": f"Booking {booking_id} has been successfully cancelled"
    }

