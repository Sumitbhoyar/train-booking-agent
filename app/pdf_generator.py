"""PDF Generation Utility for Booking Confirmations"""
from io import BytesIO
from datetime import datetime
from typing import Dict
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class BookingPDFGenerator:
    """Generate PDF documents for train booking confirmations"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=6
        ))
        
        # Footer style
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
            alignment=TA_CENTER
        ))
    
    def generate_booking_pdf(self, booking: Dict, train: Dict) -> BytesIO:
        """
        Generate a PDF for a booking confirmation.
        
        Args:
            booking: Booking dictionary with booking details
            train: Train dictionary with train information
            
        Returns:
            BytesIO: PDF file as bytes buffer
        """
        buffer = BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add title
        title = Paragraph("🚂 Train Booking Confirmation", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Status indicator
        status = booking.get('status', 'unknown').upper()
        status_color = colors.green if status == 'CONFIRMED' else colors.red
        status_style = ParagraphStyle(
            name='Status',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=status_color,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        status_text = Paragraph(f"Status: {status}", status_style)
        elements.append(status_text)
        elements.append(Spacer(1, 0.4*inch))
        
        # Booking Information Section
        elements.append(Paragraph("Booking Information", self.styles['CustomHeader']))
        
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
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7'))
        ]))
        
        elements.append(booking_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Train Information Section
        elements.append(Paragraph("Train Information", self.styles['CustomHeader']))
        
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
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7'))
        ]))
        
        elements.append(train_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # Important Notice
        notice_style = ParagraphStyle(
            name='Notice',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#e74c3c'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=12,
            borderWidth=1,
            borderColor=colors.HexColor('#e74c3c'),
            borderPadding=10
        )
        notice_text = Paragraph(
            "<b>Important:</b> Please arrive at the station at least 30 minutes before departure. "
            "Carry a valid ID proof along with this booking confirmation.",
            notice_style
        )
        elements.append(notice_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # Terms and Conditions
        elements.append(Paragraph("Terms & Conditions", self.styles['CustomHeader']))
        terms = [
            "1. This ticket is non-transferable and valid only for the mentioned passenger.",
            "2. Please arrive at the station at least 30 minutes before departure.",
            "3. Cancellation is allowed up to 4 hours before departure.",
            "4. Refund will be processed within 7 business days after cancellation.",
            "5. In case of train delays or cancellations, full refund will be provided."
        ]
        
        for term in terms:
            elements.append(Paragraph(term, self.styles['InfoText']))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>" \
                     "Train Booking API - Powered by AWS | For support: support@trainbooking.com"
        footer = Paragraph(footer_text, self.styles['Footer'])
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Reset buffer position to beginning
        buffer.seek(0)
        
        return buffer
    
    def generate_cancellation_pdf(self, booking: Dict, train: Dict) -> BytesIO:
        """
        Generate a PDF for a cancelled booking.
        
        Args:
            booking: Cancelled booking dictionary
            train: Train dictionary
            
        Returns:
            BytesIO: PDF file as bytes buffer
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        elements = []
        
        # Title
        title = Paragraph("🚫 Booking Cancellation Receipt", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        # Cancellation notice
        cancel_style = ParagraphStyle(
            name='CancelNotice',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.red,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        cancel_text = Paragraph("This booking has been CANCELLED", cancel_style)
        elements.append(cancel_text)
        elements.append(Spacer(1, 0.4*inch))
        
        # Booking details
        elements.append(Paragraph("Cancelled Booking Details", self.styles['CustomHeader']))
        
        booking_data = [
            ['Booking ID:', booking.get('booking_id', 'N/A')],
            ['Passenger Name:', booking.get('passenger_name', 'N/A')],
            ['Email:', booking.get('email', 'N/A')],
            ['Original Journey Date:', booking.get('journey_date', 'N/A')],
            ['Cancelled On:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        booking_table = Table(booking_data, colWidths=[2.5*inch, 3.5*inch])
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
        elements.append(Spacer(1, 0.4*inch))
        
        # Refund information
        refund_text = Paragraph(
            "<b>Refund Information:</b> Your refund will be processed within 7 business days "
            "to the original payment method. You will receive a confirmation email once processed.",
            self.styles['InfoText']
        )
        elements.append(refund_text)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>" \
                     "Train Booking API | For support: support@trainbooking.com"
        footer = Paragraph(footer_text, self.styles['Footer'])
        elements.append(footer)
        
        doc.build(elements)
        buffer.seek(0)
        
        return buffer


# Global PDF generator instance
pdf_generator = BookingPDFGenerator()

