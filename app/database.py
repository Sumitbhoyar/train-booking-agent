"""In-Memory Database for Train Booking System"""
from typing import List, Optional, Dict
from datetime import date
import uuid


class Database:
    """In-memory database for trains and bookings"""
    
    def __init__(self):
        # Sample train data
        self.trains: List[Dict] = [
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
        
        # Bookings storage
        self.bookings: List[Dict] = []
        
        # Track seat assignments per train
        self.seat_counter: Dict[str, int] = {}
    
    def search_trains(self, origin: str, destination: str, journey_date: date) -> List[Dict]:
        """Search for trains matching route"""
        results = []
        for train in self.trains:
            route = train["route"]
            if (route["from"].lower() == origin.lower() and 
                route["to"].lower() == destination.lower() and
                train["available_seats"] > 0):
                results.append(train.copy())
        return results
    
    def get_train(self, train_number: str) -> Optional[Dict]:
        """Get train by train number"""
        for train in self.trains:
            if train["train_number"] == train_number:
                return train.copy()
        return None
    
    def create_booking(self, train_number: str, passenger_name: str, 
                      email: str, journey_date: date) -> Optional[Dict]:
        """Create a new booking"""
        # Check if train exists and has available seats
        train = None
        for t in self.trains:
            if t["train_number"] == train_number:
                train = t
                break
        
        if not train:
            return None
        
        if train["available_seats"] <= 0:
            return None
        
        # Generate booking ID
        booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
        
        # Assign seat number
        if train_number not in self.seat_counter:
            self.seat_counter[train_number] = 1
        seat_number = f"A{self.seat_counter[train_number]}"
        self.seat_counter[train_number] += 1
        
        # Create booking
        booking = {
            "booking_id": booking_id,
            "train_number": train_number,
            "passenger_name": passenger_name,
            "email": email,
            "journey_date": journey_date.isoformat(),
            "seat_number": seat_number,
            "status": "confirmed"
        }
        
        self.bookings.append(booking)
        
        # Decrease available seats
        train["available_seats"] -= 1
        
        return booking.copy()
    
    def get_booking(self, booking_id: str) -> Optional[Dict]:
        """Get booking by ID"""
        for booking in self.bookings:
            if booking["booking_id"] == booking_id:
                return booking.copy()
        return None
    
    def cancel_booking(self, booking_id: str) -> Optional[Dict]:
        """Cancel a booking"""
        booking = None
        for b in self.bookings:
            if b["booking_id"] == booking_id:
                booking = b
                break
        
        if not booking:
            return None
        
        if booking["status"] == "cancelled":
            return booking.copy()
        
        # Update booking status
        booking["status"] = "cancelled"
        
        # Restore available seats
        train_number = booking["train_number"]
        for train in self.trains:
            if train["train_number"] == train_number:
                train["available_seats"] += 1
                break
        
        return booking.copy()
    
    def get_all_trains(self) -> List[Dict]:
        """Get all trains"""
        return [train.copy() for train in self.trains]


# Global database instance
db = Database()

