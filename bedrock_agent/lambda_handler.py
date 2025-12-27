"""AWS Bedrock Agent Action Group Lambda Handler with PDF Generation"""
import json
import os
import base64
from datetime import datetime
from typing import Dict, Any, List
from io import BytesIO
import uuid

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import BedrockAgentResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

# PDF generation imports
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER

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


def generate_booking_pdf(booking: Dict, train: Dict) -> BytesIO:
    """Generate a PDF for booking confirmation"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    status_style = ParagraphStyle(
        name='Status',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.green if booking['status'] == 'confirmed' else colors.red,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("🚂 Train Booking Confirmation", title_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Status
    status_text = booking.get('status', 'unknown').upper()
    elements.append(Paragraph(f"Status: {status_text}", status_style))
    elements.append(Spacer(1, 0.4*inch))
    
    # Booking Information
    elements.append(Paragraph("Booking Information", styles['Heading2']))
    booking_data = [
        ['Booking ID:', booking.get('booking_id', 'N/A')],
        ['Passenger Name:', booking.get('passenger_name', 'N/A')],
        ['Email:', booking.get('email', 'N/A')],
        ['Journey Date:', booking.get('journey_date', 'N/A')],
        ['Seat Number:', booking.get('seat_number', 'N/A')]
    ]
    
    booking_table = Table(booking_data, colWidths=[2*inch, 4*inch])
    booking_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7'))
    ]))
    elements.append(booking_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Train Information
    elements.append(Paragraph("Train Information", styles['Heading2']))
    train_data = [
        ['Train Number:', train.get('train_number', 'N/A')],
        ['Train Name:', train.get('name', 'N/A')],
        ['From:', train.get('route', {}).get('from', 'N/A')],
        ['To:', train.get('route', {}).get('to', 'N/A')],
        ['Departure Time:', train.get('departure_time', 'N/A')]
    ]
    
    train_table = Table(train_data, colWidths=[2*inch, 4*inch])
    train_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7'))
    ]))
    elements.append(train_table)
    elements.append(Spacer(1, 0.4*inch))
    
    # Footer
    footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>" \
                 "Train Booking API - Powered by AWS"
    footer_style = ParagraphStyle(name='Footer', parent=styles['Normal'], fontSize=9, 
                                 textColor=colors.HexColor('#7f8c8d'), alignment=TA_CENTER)
    elements.append(Paragraph(footer_text, footer_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


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


@app.post("/exportBookingPDF")
def export_booking_pdf(booking_id: str) -> Dict[str, Any]:
    """
    Export booking confirmation as PDF (Tool Use - generates and returns PDF).
    
    Args:
        booking_id: Booking ID to export
        
    Returns:
        Dictionary with base64-encoded PDF content
    """
    logger.info(f"Generating PDF for booking {booking_id}")
    
    # Check if booking exists
    booking = None
    for b in bookings_data:
        if b["booking_id"] == booking_id:
            booking = b
            break
    
    if not booking:
        return {
            "error": f"Booking {booking_id} not found"
        }
    
    # Get train details
    train = None
    for t in trains_data:
        if t["train_number"] == booking["train_number"]:
            train = t
            break
    
    if not train:
        return {
            "error": f"Train information not found for booking {booking_id}"
        }
    
    try:
        # Generate PDF
        pdf_buffer = generate_booking_pdf(booking, train)
        pdf_bytes = pdf_buffer.getvalue()
        
        # Encode to base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Calculate file size
        file_size_kb = len(pdf_bytes) / 1024
        
        return {
            "booking_id": booking_id,
            "pdf_generated": True,
            "pdf_content": pdf_base64,
            "file_size_kb": round(file_size_kb, 2),
            "filename": f"booking_{booking_id}.pdf",
            "message": f"PDF generated successfully for {booking['passenger_name']}'s booking on train {booking['train_number']}. "
                      f"The PDF is {file_size_kb:.1f}KB and contains complete booking details including seat {booking['seat_number']}.",
            "instructions": "The PDF content is base64-encoded. You can save it or provide it to the user. "
                          "To save: decode the base64 string and write to a .pdf file."
        }
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return {
            "error": f"Failed to generate PDF: {str(e)}",
            "booking_id": booking_id
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
