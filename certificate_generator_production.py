#!/usr/bin/env python3
"""
Production Certificate Generator for SafeSteps Learning
Replaces template-based PDF generation with programmatic generation
Matches the exact design of the original certificates
"""

import io
import math
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Design constants
COLORS = {
    'gold': HexColor('#D4AF37'),
    'dark_gold': HexColor('#B8941F'),
    'navy': HexColor('#1E3A5F'),
    'light_gold': HexColor('#F4E4BC'),
    'black': HexColor('#000000'),
    'gray': HexColor('#666666'),
    'white': HexColor('#FFFFFF')
}

class CertificateGenerator:
    def __init__(self):
        self.width, self.height = landscape(letter)
        
    def _draw_decorative_curves(self, c):
        """Draw decorative curve elements on the sides"""
        c.saveState()
        c.setStrokeColor(COLORS['gold'])
        c.setLineWidth(2)
        
        # Left side curves
        for i in range(5):
            offset = i * 3
            c.bezier(0, self.height * 0.3 + offset, 
                    self.width * 0.1, self.height * 0.5 + offset,
                    self.width * 0.05, self.height * 0.7 + offset,
                    0, self.height * 0.9 + offset)
        
        # Right side curves (mirror)
        for i in range(5):
            offset = i * 3
            c.bezier(self.width, self.height * 0.3 + offset,
                    self.width * 0.9, self.height * 0.5 + offset,
                    self.width * 0.95, self.height * 0.7 + offset,
                    self.width, self.height * 0.9 + offset)
        
        c.restoreState()
    
    def _draw_corner_triangles(self, c):
        """Draw decorative triangular elements in corners"""
        c.saveState()
        
        # Bottom left triangles
        self._draw_triangle(c, 0, 0, self.width * 0.2, self.height * 0.25, COLORS['gold'])
        self._draw_triangle(c, 0, 0, self.width * 0.15, self.height * 0.18, COLORS['navy'])
        
        # Bottom right triangles
        self._draw_triangle(c, self.width, 0, self.width * 0.8, self.height * 0.25, COLORS['gold'], flip=True)
        self._draw_triangle(c, self.width, 0, self.width * 0.85, self.height * 0.18, COLORS['navy'], flip=True)
        
        c.restoreState()
    
    def _draw_triangle(self, c, x1, y1, x2, y2, color, flip=False):
        """Helper to draw a triangle"""
        c.setFillColor(color)
        p = c.beginPath()
        if flip:
            p.moveTo(x1, y1)
            p.lineTo(x2, y1)
            p.lineTo(x1, y2)
        else:
            p.moveTo(x1, y1)
            p.lineTo(x2, y1)
            p.lineTo(x1, y2)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    
    def _draw_logo_or_badge(self, c, x, y, size=80):
        """Draw the SafeSteps logo if available, otherwise draw badge"""
        import os
        # First try the logo in the project root, then in data/templates
        logo_path = "safesteps_logo.png"
        if not os.path.exists(logo_path):
            logo_path = "data/templates/safesteps_logo.png"
        
        c.saveState()
        
        # Try to draw logo image if it exists
        if os.path.exists(logo_path):
            try:
                # Draw the logo centered at the given position
                # Assuming logo should be about 120 pixels wide
                logo_width = 120
                logo_height = 120  # Adjust based on actual aspect ratio
                c.drawImage(logo_path, 
                          x - logo_width/2, 
                          y - logo_height/2, 
                          width=logo_width, 
                          height=logo_height,
                          preserveAspectRatio=True,
                          mask='auto')
            except Exception as e:
                # If logo fails, fall back to badge
                self._draw_badge_fallback(c, x, y, size)
        else:
            # No logo file, use fallback badge
            self._draw_badge_fallback(c, x, y, size)
            
        c.restoreState()
    
    def _draw_badge_fallback(self, c, x, y, size=80):
        """Fallback badge design when logo is not available - enhanced with footprint theme"""
        # Outer gold scalloped edge
        c.setFillColor(COLORS['gold'])
        points = 16
        outer_radius = size / 2
        inner_radius = outer_radius * 0.85
        
        p = c.beginPath()
        for i in range(points * 2):
            angle = i * math.pi / points
            radius = outer_radius if i % 2 == 0 else inner_radius
            px = x + radius * math.cos(angle)
            py = y + radius * math.sin(angle)
            if i == 0:
                p.moveTo(px, py)
            else:
                p.lineTo(px, py)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
        
        # Inner navy circle
        c.setFillColor(COLORS['navy'])
        c.circle(x, y, size * 0.35, fill=1, stroke=0)
        
        # Draw footprint pattern with green dots
        # Main foot shape
        c.setFillColor(HexColor('#4CAF50'))  # Green color for SafeSteps theme
        
        # Heel
        c.circle(x, y + size * 0.12, size * 0.08, fill=1, stroke=0)
        
        # Arch
        c.ellipse(x - size * 0.06, y + size * 0.02, 
                  x + size * 0.06, y + size * 0.08, fill=1, stroke=0)
        
        # Ball of foot
        c.ellipse(x - size * 0.08, y - size * 0.05, 
                  x + size * 0.08, y + size * 0.02, fill=1, stroke=0)
        
        # Switch to navy for toes
        c.setFillColor(COLORS['navy'])  # Dark blue for toes
        
        # Toes (5 small circles)
        toe_positions = [
            (-0.08, -0.10),  # Big toe
            (-0.04, -0.12),  # Second toe
            (0, -0.13),      # Middle toe
            (0.04, -0.12),   # Fourth toe
            (0.08, -0.10)    # Little toe
        ]
        
        for tx, ty in toe_positions:
            c.circle(x + size * tx, y + size * ty, size * 0.025, fill=1, stroke=0)
        
        # SafeSteps branding
        c.setFillColor(COLORS['white'])
        c.setFont("Helvetica-Bold", size * 0.08)
        c.drawCentredString(x, y - size * 0.22, "SAFE STEPS")
        c.setFont("Helvetica", size * 0.06)
        c.drawCentredString(x, y - size * 0.30, "LEARNING")
    
    def generate(self, student_name, course_name, score, completion_date, output_buffer=None):
        """
        Generate a certificate
        
        Args:
            student_name: Name of the student
            course_name: Name of the course
            score: Score achieved (e.g., "Passed", "95%")
            completion_date: Date of completion
            output_buffer: Optional BytesIO buffer. If None, returns bytes
            
        Returns:
            bytes or None (if output_buffer provided)
        """
        # Create buffer if not provided
        if output_buffer is None:
            output_buffer = io.BytesIO()
            return_bytes = True
        else:
            return_bytes = False
        
        # Create canvas
        c = canvas.Canvas(output_buffer, pagesize=landscape(letter))
        
        # Draw background elements
        self._draw_decorative_curves(c)
        self._draw_corner_triangles(c)
        
        # Main title
        c.setFont("Helvetica-Bold", 60)
        c.setFillColor(COLORS['black'])
        c.drawCentredString(self.width/2, self.height - 120, "CERTIFICATE")
        
        c.setFont("Helvetica", 24)
        c.drawCentredString(self.width/2, self.height - 160, "OF ACHIEVEMENT")
        
        # Gold line under title
        c.setStrokeColor(COLORS['gold'])
        c.setLineWidth(2)
        c.line(self.width/2 - 150, self.height - 175, self.width/2 + 150, self.height - 175)
        
        # Presentation text
        c.setFont("Helvetica", 16)
        c.setFillColor(COLORS['black'])
        c.drawCentredString(self.width/2, self.height - 220, "THIS CERTIFICATE IS PROUDLY PRESENTED TO")
        
        # Student name with underline
        c.setStrokeColor(COLORS['black'])
        c.setLineWidth(1)
        c.line(self.width/2 - 200, self.height - 280, self.width/2 + 200, self.height - 280)
        
        # Draw student name (auto-size for long names)
        name_font_size = 28
        if len(student_name) > 30:
            name_font_size = 24
        elif len(student_name) > 40:
            name_font_size = 20
            
        c.setFont("Helvetica-Bold", name_font_size)
        c.drawCentredString(self.width/2, self.height - 270, student_name)
        
        # "For completing"
        c.setFont("Helvetica", 16)
        c.drawCentredString(self.width/2, self.height - 330, "FOR COMPLETING")
        
        # Course name (auto-size for long names)
        course_font_size = 48
        if len(course_name) > 20:
            course_font_size = 40
        elif len(course_name) > 30:
            course_font_size = 32
            
        c.setFont("Helvetica-Bold", course_font_size)
        c.drawCentredString(self.width/2, self.height - 380, course_name)
        
        # Description text
        c.setFont("Helvetica", 14)
        text_lines = [
            "THIS FORMS PART OF A SOCIAL CONTRACT BETWEEN YOURSELF AND",
            "YOUR SCHOOL, DEMONSTRATING A CLEAR UNDERSTANDING OF THE",
            "TOPIC AND EXPECTATIONS."
        ]
        y_pos = self.height - 440
        for line in text_lines:
            c.drawCentredString(self.width/2, y_pos, line)
            y_pos -= 20
        
        # SafeSteps logo/badge
        self._draw_logo_or_badge(c, self.width/2, self.height - 550)
        
        # Score section - aligned above the line
        c.setFont("Helvetica-Bold", 24)
        c.drawString(self.width * 0.2, self.height - 565, str(score))  # Fixed Y position - 5px above line
        c.setFont("Helvetica", 14)
        c.drawString(self.width * 0.2, self.height - 600, "SCORE")
        c.setStrokeColor(COLORS['black'])
        c.line(self.width * 0.15, self.height - 570, self.width * 0.35, self.height - 570)
        
        # Date section - aligned above the line
        c.setFont("Helvetica-Bold", 24)
        c.drawString(self.width * 0.65, self.height - 565, str(completion_date))  # Fixed Y position - 5px above line
        c.setFont("Helvetica", 14)
        c.drawString(self.width * 0.65, self.height - 600, "DATE")
        c.line(self.width * 0.65, self.height - 570, self.width * 0.85, self.height - 570)
        
        # Save the PDF
        c.save()
        
        # Return bytes if needed
        if return_bytes:
            output_buffer.seek(0)
            return output_buffer.read()
        
    def generate_to_file(self, student_name, course_name, score, completion_date, filename):
        """Generate certificate directly to a file"""
        with open(filename, 'wb') as f:
            pdf_bytes = self.generate(student_name, course_name, score, completion_date)
            f.write(pdf_bytes)
        return filename


# Integration with existing SafeSteps app
def generate_certificate_for_app(student_name, course_name, score=None, completion_date=None):
    """
    Drop-in replacement for existing certificate generation
    Compatible with Streamlit's st.download_button
    """
    # Always use "Pass" for score (hardcoded as requested)
    score = "Pass"
    
    if completion_date is None:
        completion_date = datetime.now().strftime("%B %d, %Y")
    
    # Generate certificate
    generator = CertificateGenerator()
    pdf_bytes = generator.generate(student_name, course_name, score, completion_date)
    
    return pdf_bytes


# Example usage and testing
if __name__ == "__main__":
    # Test generation
    generator = CertificateGenerator()
    
    # Test 1: Marshall Newton certificate
    generator.generate_to_file(
        "Marshall Newton",
        "Vapes and Vaping",
        "Pass",
        datetime.now().strftime("%B %d, %Y"),
        "marshall_newton_certificate.pdf"
    )
    
    # Test 2: Using the app function
    pdf_bytes = generate_certificate_for_app(
        "Marshall Newton",
        "Vapes and Vaping"
    )
    with open("marshall_newton_app_certificate.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print("Test certificates generated!")
    print("- marshall_newton_certificate.pdf (direct generation)")
    print("- marshall_newton_app_certificate.pdf (via app function with hardcoded Pass)")
    
    # Show how to integrate with Streamlit
    print("\nStreamlit integration example:")
    print("""
    # In your Streamlit app:
    from certificate_generator_production import generate_certificate_for_app
    
    # Generate certificate
    pdf_bytes = generate_certificate_for_app(
        student_name=st.session_state['student_name'],
        course_name=st.session_state['course_name'],
        score="Passed",
        completion_date=datetime.now().strftime("%B %d, %Y")
    )
    
    # Offer download
    st.download_button(
        label="Download Certificate",
        data=pdf_bytes,
        file_name=f"certificate_{student_name}_{course_name}.pdf",
        mime="application/pdf"
    )
    """)