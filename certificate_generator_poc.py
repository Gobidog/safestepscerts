#!/usr/bin/env python3
"""
Proof of Concept: Programmatic Certificate Generation
Reproduces the exact design of vapes_certificate_with_fields.pdf
"""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Define colors from the original design
GOLD = HexColor('#D4AF37')
DARK_GOLD = HexColor('#B8941F')
NAVY = HexColor('#1E3A5F')
LIGHT_GOLD = HexColor('#F4E4BC')
BLACK = HexColor('#000000')
GRAY = HexColor('#666666')

def draw_decorative_curves(c, width, height):
    """Draw the decorative curve elements on the sides"""
    c.saveState()
    
    # Left side curves
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    
    # Draw multiple curved lines on the left
    for i in range(5):
        offset = i * 3
        c.bezier(0, height * 0.3 + offset, 
                width * 0.1, height * 0.5 + offset,
                width * 0.05, height * 0.7 + offset,
                0, height * 0.9 + offset)
    
    # Right side curves (mirror of left)
    for i in range(5):
        offset = i * 3
        c.bezier(width, height * 0.3 + offset,
                width * 0.9, height * 0.5 + offset,
                width * 0.95, height * 0.7 + offset,
                width, height * 0.9 + offset)
    
    c.restoreState()

def draw_corner_triangles(c, width, height):
    """Draw the decorative triangular elements in corners"""
    c.saveState()
    
    # Bottom left triangle - gold
    c.setFillColor(GOLD)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(width * 0.2, 0)
    p.lineTo(0, height * 0.25)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # Bottom left inner triangle - navy
    c.setFillColor(NAVY)
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(width * 0.15, 0)
    p.lineTo(0, height * 0.18)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # Bottom right triangle - gold
    c.setFillColor(GOLD)
    p = c.beginPath()
    p.moveTo(width, 0)
    p.lineTo(width * 0.8, 0)
    p.lineTo(width, height * 0.25)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # Bottom right inner triangle - navy
    c.setFillColor(NAVY)
    p = c.beginPath()
    p.moveTo(width, 0)
    p.lineTo(width * 0.85, 0)
    p.lineTo(width, height * 0.18)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    c.restoreState()

def draw_badge(c, x, y, size=80):
    """Draw the SafeSteps badge/seal"""
    c.saveState()
    
    # Outer gold scalloped edge
    c.setFillColor(GOLD)
    # Draw a star-like scalloped edge
    import math
    points = 16
    outer_radius = size / 2
    inner_radius = outer_radius * 0.85
    
    p = c.beginPath()
    for i in range(points * 2):
        angle = i * math.pi / points
        if i % 2 == 0:
            radius = outer_radius
        else:
            radius = inner_radius
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        if i == 0:
            p.moveTo(px, py)
        else:
            p.lineTo(px, py)
    p.close()
    c.drawPath(p, fill=1, stroke=0)
    
    # Inner navy circle
    c.setFillColor(NAVY)
    c.circle(x, y, size * 0.35, fill=1, stroke=0)
    
    # Draw footprint icon
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", size * 0.15)
    c.drawCentredString(x, y + size * 0.1, "ⵏ")  # Footprint symbol
    
    # SafeSteps text
    c.setFont("Helvetica-Bold", size * 0.08)
    c.drawCentredString(x, y - size * 0.05, "SAFE STEPS")
    c.setFont("Helvetica", size * 0.06)
    c.drawCentredString(x, y - size * 0.15, "LEARNING")
    
    c.restoreState()

def generate_certificate(student_name, course_name, score, completion_date, output_filename):
    """Generate a certificate matching the original design"""
    
    # Create canvas in landscape orientation
    width, height = landscape(letter)
    c = canvas.Canvas(output_filename, pagesize=landscape(letter))
    
    # Draw background decorative elements
    draw_decorative_curves(c, width, height)
    draw_corner_triangles(c, width, height)
    
    # Draw title
    c.setFont("Helvetica-Bold", 60)
    c.setFillColor(BLACK)
    c.drawCentredString(width/2, height - 120, "CERTIFICATE")
    
    c.setFont("Helvetica", 24)
    c.drawCentredString(width/2, height - 160, "OF ACHIEVEMENT")
    
    # Draw gold line under title
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.line(width/2 - 150, height - 175, width/2 + 150, height - 175)
    
    # "This certificate is proudly presented to"
    c.setFont("Helvetica", 16)
    c.setFillColor(BLACK)
    c.drawCentredString(width/2, height - 220, "THIS CERTIFICATE IS PROUDLY PRESENTED TO")
    
    # Student name (placeholder line for form field)
    c.setStrokeColor(BLACK)
    c.setLineWidth(1)
    c.line(width/2 - 200, height - 280, width/2 + 200, height - 280)
    
    # Draw the actual name if provided
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(BLACK)
    c.drawCentredString(width/2, height - 270, student_name)
    
    # "For completing"
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 330, "FOR COMPLETING")
    
    # Course name
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(width/2, height - 380, course_name)
    
    # Description text
    c.setFont("Helvetica", 14)
    text_lines = [
        "THIS FORMS PART OF A SOCIAL CONTRACT BETWEEN YOURSELF AND",
        "YOUR SCHOOL, DEMONSTRATING A CLEAR UNDERSTANDING OF THE",
        "TOPIC AND EXPECTATIONS."
    ]
    y_pos = height - 440
    for line in text_lines:
        c.drawCentredString(width/2, y_pos, line)
        y_pos -= 20
    
    # Draw the badge
    draw_badge(c, width/2, height - 550)
    
    # Score section
    c.setFont("Helvetica-Bold", 24)
    c.drawString(width * 0.2, height - 580, score)
    c.setFont("Helvetica", 14)
    c.drawString(width * 0.2, height - 600, "SCORE")
    c.setStrokeColor(BLACK)
    c.line(width * 0.15, height - 570, width * 0.35, height - 570)
    
    # Date section
    c.setFont("Helvetica-Bold", 24)
    c.drawString(width * 0.65, height - 580, completion_date)
    c.setFont("Helvetica", 14)
    c.drawString(width * 0.65, height - 600, "DATE")
    c.line(width * 0.65, height - 570, width * 0.85, height - 570)
    
    # Save the PDF
    c.save()
    return output_filename

# Test the generator
if __name__ == "__main__":
    output_file = generate_certificate(
        student_name="Test Certificate",
        course_name="Vapes and Vaping",
        score="Passed",
        completion_date="July 10, 2025",
        output_filename="programmatic_certificate.pdf"
    )
    print(f"Certificate generated: {output_file}")
    
    # Check file size
    original_size = os.path.getsize("vapes_certificate_with_fields.pdf") / 1024
    new_size = os.path.getsize(output_file) / 1024
    print(f"Original PDF: {original_size:.1f} KB")
    print(f"Programmatic PDF: {new_size:.1f} KB")
    print(f"Size reduction: {(1 - new_size/original_size) * 100:.1f}%")