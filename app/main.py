"""FastAPI Application Entry Point with Mangum Adapter"""
from fastapi import FastAPI
from mangum import Mangum
from app.routers import trains, bookings

app = FastAPI(
    title="Train Booking API",
    description="Serverless train booking system with AWS Bedrock Agent integration",
    version="1.0.0"
)

# Include routers
app.include_router(trains.router, prefix="/trains", tags=["trains"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "train-booking-api",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Train Booking API",
        "docs": "/docs",
        "health": "/health"
    }


# Mangum handler for AWS Lambda
handler = Mangum(app, lifespan="off")

