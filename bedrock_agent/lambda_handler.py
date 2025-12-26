"""AWS Bedrock Agent Action Group Lambda Handler"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import BedrockAgentResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
app = BedrockAgentResolver()

# In-memory data store (same as FastAPI app)
trains_data = [
    {
        "train_number": "T101",
        "name": "Express 2025",
        "route": {"from": "Paris", "to": "Lyon"},
        "departure_time": "08:00",
        "available_seats": 50
    },
    {
        "train_number": "T102",
        "name": "Rapid Express",
        "route": {"from": "Paris", "to": "Marseille"},
        "departure_time": "09:30",
        "available_seats": 45
    },
    {
        "train_number": "T103",
        "name": "Night Express",
        "route": {"from": "Lyon", "to": "Paris"},
        "departure_time": "22:00",
        "available_seats": 60
    },
    {
        "train_number": "T104",
        "name": "Morning Special",
        "route": {"from": "Marseille", "to": "Paris"},
        "departure_time": "06:00",
        "available_seats": 40
    },
    {
        "train_number": "T105",
        "name": "City Connect",
        "route": {"from": "Paris", "to": "Nice"},
        "departure_time": "14:00",
        "available_seats": 55
    }
]

bookings_data = []
seat_counter = {}


@app.get("/searchTrains")
def search_trains(origin: str, destination: str, date: str) -> Dict[str, Any]:
    """
    Search for available trains by route and date.
    
    Args:
        origin: Origin station
        destination: Destination station
        date: Journey date (YYYY-MM-DD)
        
    Returns:
        Dictionary with list of matching trains
    """
    logger.info(f"Searching trains from {origin} to {destination} on {date}")
    
    results = []
    for train in trains_data:
        route = train["route"]
        if (route["from"].lower() == origin.lower() and 
            route["to"].lower() == destination.lower() and
            train["available_seats"] > 0):
            results.append(train)
    
    if not results:
        return {
            "trains": [],
            "message": f"No trains found from {origin} to {destination}"
        }
    
    return {
        "trains": results,
        "count": len(results)
    }


@app.post("/createBooking")
def create_booking(train_number: str, passenger_name: str, 
                  email: str, journey_date: str) -> Dict[str, Any]:
    """
    Create a new train booking.
    
    Args:
        train_number: Train number to book
        passenger_name: Passenger name
        email: Passenger email
        journey_date: Journey date (YYYY-MM-DD)
        
    Returns:
        Booking confirmation details
    """
    logger.info(f"Creating booking for {passenger_name} on train {train_number}")
    
    # Find train
    train = None
    for t in trains_data:
        if t["train_number"] == train_number:
            train = t
            break
    
    if not train:
        return {
            "error": f"Train {train_number} not found"
        }
    
    if train["available_seats"] <= 0:
        return {
            "error": f"No seats available on train {train_number}"
        }
    
    # Generate booking ID
    import uuid
    booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
    
    # Assign seat
    if train_number not in seat_counter:
        seat_counter[train_number] = 1
    seat_number = f"A{seat_counter[train_number]}"
    seat_counter[train_number] += 1
    
    # Create booking
    booking = {
        "booking_id": booking_id,
        "train_number": train_number,
        "passenger_name": passenger_name,
        "email": email,
        "journey_date": journey_date,
        "seat_number": seat_number,
        "status": "confirmed"
    }
    
    bookings_data.append(booking)
    train["available_seats"] -= 1
    
    return {
        "booking": booking,
        "message": f"Booking confirmed! Your booking ID is {booking_id}. Seat number: {seat_number}"
    }


@app.get("/getBookingStatus")
def get_booking_status(booking_id: str) -> Dict[str, Any]:
    """
    Get booking status by booking ID.
    
    Args:
        booking_id: Booking ID to retrieve
        
    Returns:
        Booking details and status
    """
    logger.info(f"Retrieving booking status for {booking_id}")
    
    for booking in bookings_data:
        if booking["booking_id"] == booking_id:
            return {
                "booking": booking,
                "message": f"Booking {booking_id} is {booking['status']}"
            }
    
    return {
        "error": f"Booking {booking_id} not found"
    }


@app.delete("/cancelBooking")
def cancel_booking(booking_id: str) -> Dict[str, Any]:
    """
    Cancel an existing booking.
    
    Args:
        booking_id: Booking ID to cancel
        
    Returns:
        Cancellation confirmation
    """
    logger.info(f"Cancelling booking {booking_id}")
    
    booking = None
    for b in bookings_data:
        if b["booking_id"] == booking_id:
            booking = b
            break
    
    if not booking:
        return {
            "error": f"Booking {booking_id} not found"
        }
    
    if booking["status"] == "cancelled":
        return {
            "booking_id": booking_id,
            "status": "cancelled",
            "message": f"Booking {booking_id} is already cancelled"
        }
    
    # Update status
    booking["status"] = "cancelled"
    
    # Restore seat
    train_number = booking["train_number"]
    for train in trains_data:
        if train["train_number"] == train_number:
            train["available_seats"] += 1
            break
    
    return {
        "booking_id": booking_id,
        "status": "cancelled",
        "message": f"Booking {booking_id} has been successfully cancelled"
    }


@logger.inject_lambda_context
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> Dict[str, Any]:
    """
    Lambda handler for Bedrock Agent action group.
    
    Args:
        event: Lambda event from Bedrock Agent
        context: Lambda context
        
    Returns:
        Response for Bedrock Agent
    """
    logger.info("Received event", extra={"event": event})
    
    return app.resolve(event, context)

