"""Pydantic Models for Request/Response Validation"""
from pydantic import BaseModel, Field, EmailStr
from typing import Literal
from datetime import date


class Route(BaseModel):
    """Train route information"""
    from_station: str = Field(..., alias="from", description="Origin station")
    to_station: str = Field(..., alias="to", description="Destination station")

    class Config:
        populate_by_name = True


class Train(BaseModel):
    """Train information model"""
    train_number: str = Field(..., description="Unique train identifier")
    name: str = Field(..., description="Train name")
    route: Route = Field(..., description="Train route")
    departure_time: str = Field(..., description="Departure time (HH:MM format)")
    available_seats: int = Field(..., ge=0, description="Number of available seats")


class TrainSearchParams(BaseModel):
    """Parameters for searching trains"""
    origin: str = Field(..., description="Origin station")
    destination: str = Field(..., description="Destination station")
    date: date = Field(..., description="Journey date")


class BookingCreate(BaseModel):
    """Request model for creating a booking"""
    train_number: str = Field(..., description="Train number to book")
    passenger_name: str = Field(..., min_length=1, description="Passenger name")
    email: EmailStr = Field(..., description="Passenger email")
    journey_date: date = Field(..., description="Journey date")


class Booking(BaseModel):
    """Booking information model"""
    booking_id: str = Field(..., description="Unique booking identifier")
    train_number: str = Field(..., description="Train number")
    passenger_name: str = Field(..., description="Passenger name")
    email: EmailStr = Field(..., description="Passenger email")
    journey_date: date = Field(..., description="Journey date")
    seat_number: str = Field(..., description="Assigned seat number")
    status: Literal["confirmed", "cancelled"] = Field(..., description="Booking status")


class BookingResponse(BaseModel):
    """Response model for booking operations"""
    booking: Booking
    message: str = Field(..., description="Operation message")


class CancelBookingResponse(BaseModel):
    """Response model for booking cancellation"""
    booking_id: str = Field(..., description="Cancelled booking ID")
    status: str = Field(..., description="New status")
    message: str = Field(..., description="Cancellation message")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: str = Field(None, description="Additional error details")

