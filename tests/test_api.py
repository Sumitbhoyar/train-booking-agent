"""Unit Tests for Train Booking API"""
import pytest
from fastapi.testclient import TestClient
from datetime import date
from app.main import app
from app.database import db

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


class TestTrainEndpoints:
    """Test train search endpoints"""
    
    def test_get_all_trains(self):
        """Test getting all trains"""
        response = client.get("/trains/all")
        assert response.status_code == 200
        trains = response.json()
        assert len(trains) > 0
        assert "train_number" in trains[0]
    
    def test_search_trains_success(self):
        """Test searching trains with valid route"""
        response = client.get("/trains?origin=Paris&destination=Lyon&date=2025-12-27")
        assert response.status_code == 200
        trains = response.json()
        assert isinstance(trains, list)
    
    def test_search_trains_no_results(self):
        """Test searching trains with no matching route"""
        response = client.get("/trains?origin=InvalidCity&destination=AnotherCity&date=2025-12-27")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_specific_train(self):
        """Test getting a specific train"""
        response = client.get("/trains/T101")
        assert response.status_code == 200
        train = response.json()
        assert train["train_number"] == "T101"
    
    def test_get_nonexistent_train(self):
        """Test getting a non-existent train"""
        response = client.get("/trains/T999")
        assert response.status_code == 404


class TestBookingEndpoints:
    """Test booking management endpoints"""
    
    def test_create_booking_success(self):
        """Test creating a booking successfully"""
        booking_data = {
            "train_number": "T101",
            "passenger_name": "Test User",
            "email": "test@example.com",
            "journey_date": "2025-12-27"
        }
        response = client.post("/bookings", json=booking_data)
        assert response.status_code == 201
        result = response.json()
        assert "booking" in result
        assert result["booking"]["status"] == "confirmed"
        
        # Store booking ID for other tests
        return result["booking"]["booking_id"]
    
    def test_create_booking_invalid_train(self):
        """Test creating a booking with invalid train"""
        booking_data = {
            "train_number": "T999",
            "passenger_name": "Test User",
            "email": "test@example.com",
            "journey_date": "2025-12-27"
        }
        response = client.post("/bookings", json=booking_data)
        assert response.status_code == 404
    
    def test_get_booking_status(self):
        """Test getting booking status"""
        # First create a booking
        booking_data = {
            "train_number": "T102",
            "passenger_name": "Test User 2",
            "email": "test2@example.com",
            "journey_date": "2025-12-28"
        }
        create_response = client.post("/bookings", json=booking_data)
        booking_id = create_response.json()["booking"]["booking_id"]
        
        # Then get its status
        response = client.get(f"/bookings/{booking_id}")
        assert response.status_code == 200
        booking = response.json()
        assert booking["booking_id"] == booking_id
    
    def test_get_nonexistent_booking(self):
        """Test getting a non-existent booking"""
        response = client.get("/bookings/INVALID123")
        assert response.status_code == 404
    
    def test_cancel_booking(self):
        """Test cancelling a booking"""
        # First create a booking
        booking_data = {
            "train_number": "T103",
            "passenger_name": "Test User 3",
            "email": "test3@example.com",
            "journey_date": "2025-12-29"
        }
        create_response = client.post("/bookings", json=booking_data)
        booking_id = create_response.json()["booking"]["booking_id"]
        
        # Then cancel it
        response = client.delete(f"/bookings/{booking_id}")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "cancelled"
    
    def test_cancel_nonexistent_booking(self):
        """Test cancelling a non-existent booking"""
        response = client.delete("/bookings/INVALID123")
        assert response.status_code == 404


class TestDataValidation:
    """Test data validation"""
    
    def test_invalid_email(self):
        """Test booking with invalid email"""
        booking_data = {
            "train_number": "T101",
            "passenger_name": "Test User",
            "email": "invalid-email",
            "journey_date": "2025-12-27"
        }
        response = client.post("/bookings", json=booking_data)
        assert response.status_code == 422
    
    def test_missing_required_fields(self):
        """Test booking with missing fields"""
        booking_data = {
            "train_number": "T101",
            "passenger_name": "Test User"
        }
        response = client.post("/bookings", json=booking_data)
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

