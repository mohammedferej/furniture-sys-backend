from django.core.files import File  # Add this import
from django.conf import settings
from io import BytesIO
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile


def generate_order_pdf(order):

    try:
        # Create buffer for PDF
        buffer = BytesIO()
        
        # Create document template
        doc = SimpleDocTemplate(buffer, pagesize=letter,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Prepare styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading2']
        body_style = styles['BodyText']
        footer_style = ParagraphStyle(
            'footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1
        )
        
        story = []
        
        # Add header
        # story.append(Paragraph(f"<b>Order #{order.order_code}</b>", title_style))
        # story.append(Spacer(1, 0.25*inch))
        
        # Customer information
        customer = order.customer
        customer_info = [
            ["Customer:", customer.name],
            ["Phone:", customer.phone],
            ["Address:", customer.address]
        ]
        story.append(Paragraph("Customer Information", heading_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Table(customer_info, colWidths=[1.5*inch, 4*inch]))
        story.append(Spacer(1, 0.3*inch))
        
        # Order details
        order_info = [
            ["Order Date:", order.receive_order_at.strftime("%B %d, %Y")],
            ["Completion Date:", order.completed_order_at.strftime("%B %d, %Y")],
            ["Total Price:", f"${order.total_price}"],
            ["Remaining Payment:", f"${order.remaining_payment}"]
        ]
        story.append(Paragraph("Order Details", heading_style))
        story.append(Spacer(1, 0.1*inch))
        story.append(Table(order_info, colWidths=[1.5*inch, 4*inch]))
        story.append(Spacer(1, 0.3*inch))
        
        # Material details (if exists)
        material = order.mejlis_materials.first()
        if material:
            material_info = [
                ["Type:", material.material_type],
                ["Material Made from:", material.material_made_from],
                ["Design:", material.design_type],
                ["Room Size:", f"{material.room_size} sqm"],
                ["Shape:", material.room_shape.upper()],
                ["Price/Meter:", f"${material.price_per_meter}"]
            ]
            story.append(Paragraph("Material Specifications", heading_style))
            story.append(Spacer(1, 0.1*inch))
            story.append(Table(material_info, colWidths=[1.5*inch, 4*inch]))
            story.append(Spacer(1, 0.3*inch))
            
            # Segments information
            segments_info = []
            for segment in material.segments.all():
                segments_info.append([f"Side {segment.side_name}:", ", ".join(map(str, segment.values))])
            
            story.append(Paragraph("Segment Measurements", heading_style))
            story.append(Spacer(1, 0.1*inch))
            story.append(Table(segments_info, colWidths=[1.5*inch, 4*inch]))
            story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Thank you for your business! | © 2025 Your Company", footer_style))
        
        # Build PDF
        doc.build(story)
        
        # Save to model
        buffer.seek(0)
        filename = f"order_{order.order_code}.pdf"
        
        # Remove old file if exists
        if order.document_path and os.path.exists(order.document_path.path):
            os.remove(order.document_path.path)
        
        # Save new file
        order.document_path.save(filename, File(buffer))
        return order.document_path.url
        
    except Exception as e:
        print(f"PDF generation error: {str(e)}")
        raise e