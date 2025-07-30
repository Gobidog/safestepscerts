#!/usr/bin/env python3
"""
Analyze the feasibility of reproducing the vapes certificate PDF programmatically
This will help determine if we can replace the template-based system
"""

import os
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Group, Circle, Polygon
from reportlab.graphics.charts.textlabels import Label
from PIL import Image as PILImage
import io
import tempfile
from datetime import datetime
import json

def analyze_certificate_reproduction():
    """
    Analyze if we can reproduce the certificate programmatically
    """
    
    print("=== PDF Certificate Reproduction Analysis ===\n")
    
    # 1. Check if we have ReportLab available
    print("1. ReportLab Availability:")
    try:
        import reportlab
        print(f"   ✓ ReportLab version: {reportlab.Version}")
    except ImportError:
        print("   ✗ ReportLab not installed")
        print("   → Run: pip install reportlab")
        return False
    
    # 2. Analyze the design elements from the vapes certificate
    print("\n2. Certificate Design Elements (from visual analysis):")
    design_elements = {
        "Page Setup": {
            "Size": "A4 Landscape (841.92 x 595.44 pts)",
            "Background": "White with decorative corner elements",
            "Colors": ["Gold/Yellow gradients", "Blue accents", "Black text"]
        },
        "Typography": {
            "Main Title": "CERTIFICATE - Large, bold, centered",
            "Subtitle": "OF ACHIEVEMENT - Medium, centered",
            "Body Text": "Variable sizes for different sections",
            "Fields": ["Name field", "Score field", "Date field"]
        },
        "Decorative Elements": {
            "Corners": "Curved gold/yellow decorative swooshes",
            "Logo": "Safe Steps Learning badge with footprint icon",
            "Lines": "Gold horizontal line under subtitle"
        },
        "Layout": {
            "Structure": "Centered vertical layout",
            "Spacing": "Generous white space",
            "Alignment": "Center-aligned main content"
        }
    }
    
    for category, items in design_elements.items():
        print(f"\n   {category}:")
        if isinstance(items, dict):
            for key, value in items.items():
                print(f"      - {key}: {value}")
        else:
            for item in items:
                print(f"      - {item}")
    
    # 3. Create a sample programmatic certificate
    print("\n3. Creating Sample Programmatic Certificate...")
    
    try:
        output_path = "programmatic_certificate_sample.pdf"
        create_sample_certificate(output_path)
        print(f"   ✓ Sample certificate created: {output_path}")
        
        # Compare file sizes
        original_size = os.path.getsize("vapes_certificate_with_fields.pdf")
        new_size = os.path.getsize(output_path)
        print(f"\n   File size comparison:")
        print(f"   - Original template: {original_size:,} bytes")
        print(f"   - Programmatic: {new_size:,} bytes")
        print(f"   - Difference: {abs(original_size - new_size):,} bytes")
        
    except Exception as e:
        print(f"   ✗ Error creating sample: {e}")
        return False
    
    # 4. Advantages of programmatic generation
    print("\n4. Advantages of Programmatic Generation:")
    advantages = [
        "No template file management needed",
        "Dynamic design adjustments possible",
        "Easier to maintain and version control",
        "Can generate different designs based on course/topic",
        "No form field compatibility issues",
        "Smaller file sizes possible",
        "Better text fitting and layout control",
        "Can add dynamic elements (QR codes, verification IDs, etc.)",
        "Easier to implement accessibility features"
    ]
    
    for adv in advantages:
        print(f"   + {adv}")
    
    # 5. Implementation considerations
    print("\n5. Implementation Considerations:")
    considerations = [
        "Need to recreate decorative elements (can use SVG or vector graphics)",
        "Font selection and embedding",
        "Color matching with original design",
        "Testing across different names/text lengths",
        "Performance for batch generation",
        "Preview generation capability"
    ]
    
    for con in considerations:
        print(f"   • {con}")
    
    # 6. Recommendation
    print("\n6. RECOMMENDATION:")
    print("   ✓ YES - Programmatic generation is feasible and advantageous")
    print("\n   The certificate can be reproduced programmatically with the following approach:")
    print("   1. Use ReportLab for PDF generation")
    print("   2. Create reusable certificate class with customizable parameters")
    print("   3. Store design elements as code (colors, fonts, layout)")
    print("   4. Generate decorative elements using vector graphics")
    print("   5. Implement dynamic text sizing and positioning")
    
    return True


def create_sample_certificate(output_path):
    """
    Create a sample certificate using ReportLab to demonstrate feasibility
    """
    # Create canvas
    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    width, height = landscape(A4)
    
    # Background
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1)
    
    # Decorative corners (simplified version)
    # Top-left corner
    c.setStrokeColor(colors.Color(1, 0.84, 0, alpha=0.3))  # Light gold
    c.setLineWidth(3)
    for i in range(3):
        c.arc(0 - i*20, height - 100 - i*20, 100 + i*20, height + i*20, 
              startAng=180, extent=90)
    
    # Top-right corner
    for i in range(3):
        c.arc(width - 100 - i*20, height - 100 - i*20, width + i*20, height + i*20, 
              startAng=270, extent=90)
    
    # Bottom-left corner (blue)
    c.setStrokeColor(colors.Color(0, 0.2, 0.6, alpha=0.8))  # Navy blue
    c.setFillColor(colors.Color(0, 0.2, 0.6, alpha=0.8))
    # Draw triangle using path
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(150, 0)
    p.lineTo(0, 150)
    p.close()
    c.drawPath(p, fill=1)
    
    # Bottom-left gold accent
    c.setFillColor(colors.Color(1, 0.84, 0, alpha=0.8))  # Gold
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(100, 0)
    p.lineTo(0, 100)
    p.close()
    c.drawPath(p, fill=1)
    
    # Main title
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 48)
    c.drawCentredString(width/2, height - 150, "CERTIFICATE")
    
    # Subtitle
    c.setFont("Helvetica", 24)
    c.drawCentredString(width/2, height - 190, "OF ACHIEVEMENT")
    
    # Gold line under subtitle
    c.setStrokeColor(colors.Color(1, 0.84, 0))
    c.setLineWidth(2)
    c.line(width/2 - 150, height - 210, width/2 + 150, height - 210)
    
    # "This certificate is proudly presented to"
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height - 270, "THIS CERTIFICATE IS PROUDLY PRESENTED TO")
    
    # Placeholder for name (would be dynamic)
    c.setFont("Helvetica-Bold", 32)
    c.drawCentredString(width/2, height - 320, "[Recipient Name]")
    
    # "For completing"
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 380, "FOR COMPLETING")
    
    # Course title
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width/2, height - 430, "Vapes and Vaping")
    
    # Description text
    c.setFont("Helvetica", 12)
    text_lines = [
        "THIS FORMS PART OF A SOCIAL CONTRACT BETWEEN YOURSELF AND",
        "YOUR SCHOOL, DEMONSTRATING A CLEAR UNDERSTANDING OF THE",
        "TOPIC AND EXPECTATIONS."
    ]
    y_pos = height - 480
    for line in text_lines:
        c.drawCentredString(width/2, y_pos, line)
        y_pos -= 18
    
    # Score and Date placeholders
    c.setFont("Helvetica-Bold", 24)
    c.drawString(150, 120, "Passed")
    c.drawRightString(width - 150, 120, "2025")
    
    c.setFont("Helvetica", 12)
    c.drawString(150, 100, "SCORE")
    c.drawRightString(width - 150, 100, "DATE")
    
    # Logo placeholder (center bottom)
    # Draw a simple circle with text as placeholder
    c.setFillColor(colors.Color(0, 0.2, 0.6))  # Navy blue
    c.circle(width/2, 80, 40, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(width/2, 85, "SAFE STEPS")
    c.drawCentredString(width/2, 73, "LEARNING")
    
    # Save the PDF
    c.save()


def create_production_certificate_generator():
    """
    Create a production-ready certificate generator class
    """
    
    code = '''"""
Production-ready certificate generator to replace template-based system
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import tempfile
import os
from typing import Dict, Optional, Tuple
import io


class CertificateGenerator:
    """
    Programmatic certificate generator for SafeSteps Learning
    Replaces the template-based system with dynamic PDF generation
    """
    
    # Design constants
    COLORS = {
        'gold': colors.Color(1, 0.84, 0),
        'light_gold': colors.Color(1, 0.84, 0, alpha=0.3),
        'navy': colors.Color(0, 0.2, 0.6),
        'navy_alpha': colors.Color(0, 0.2, 0.6, alpha=0.8),
        'black': colors.black,
        'white': colors.white
    }
    
    FONTS = {
        'title': ('Helvetica-Bold', 48),
        'subtitle': ('Helvetica', 24),
        'body': ('Helvetica', 16),
        'name': ('Helvetica-Bold', 32),
        'course': ('Helvetica-Bold', 36),
        'small': ('Helvetica', 12),
        'score': ('Helvetica-Bold', 24),
        'logo': ('Helvetica-Bold', 10)
    }
    
    def __init__(self):
        """Initialize the certificate generator"""
        self.page_size = landscape(A4)
        self.width, self.height = self.page_size
        
    def generate_certificate(
        self,
        first_name: str,
        last_name: str,
        course_name: str,
        score: str = "Passed",
        date: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a certificate for a single recipient
        
        Args:
            first_name: Recipient's first name
            last_name: Recipient's last name
            course_name: Name of the completed course
            score: Score or status (default: "Passed")
            date: Completion date (default: current date)
            output_path: Where to save the PDF (default: temp file)
            
        Returns:
            Path to the generated certificate
        """
        if not date:
            date = datetime.now().strftime("%B %d, %Y")
            
        if not output_path:
            output_path = tempfile.mktemp(suffix='.pdf')
            
        # Create canvas
        c = canvas.Canvas(output_path, pagesize=self.page_size)
        
        # Draw all elements
        self._draw_background(c)
        self._draw_decorative_elements(c)
        self._draw_header(c)
        self._draw_recipient_section(c, first_name, last_name)
        self._draw_course_section(c, course_name)
        self._draw_footer(c, score, date)
        self._draw_logo(c)
        
        # Save the PDF
        c.save()
        
        return output_path
        
    def _draw_background(self, c: canvas.Canvas):
        """Draw white background"""
        c.setFillColor(self.COLORS['white'])
        c.rect(0, 0, self.width, self.height, fill=1)
        
    def _draw_decorative_elements(self, c: canvas.Canvas):
        """Draw decorative corner elements"""
        # Top corners - gold arcs
        c.setStrokeColor(self.COLORS['light_gold'])
        c.setLineWidth(3)
        
        # Top-left corner arcs
        for i in range(3):
            c.arc(0 - i*20, self.height - 100 - i*20, 
                  100 + i*20, self.height + i*20, 
                  startAng=180, extent=90)
        
        # Top-right corner arcs
        for i in range(3):
            c.arc(self.width - 100 - i*20, self.height - 100 - i*20, 
                  self.width + i*20, self.height + i*20, 
                  startAng=270, extent=90)
        
        # Bottom-left corner - blue triangle
        c.setFillColor(self.COLORS['navy_alpha'])
        points = [0, 0, 150, 0, 0, 150]
        c.drawPolygon(points, fill=1)
        
        # Bottom-left corner - gold triangle overlay
        c.setFillColor(self.COLORS['gold'])
        points = [0, 0, 100, 0, 0, 100]
        c.drawPolygon(points, fill=1)
        
        # Bottom-right corner - mirrored triangles
        c.setFillColor(self.COLORS['navy_alpha'])
        points = [self.width, 0, self.width - 150, 0, self.width, 150]
        c.drawPolygon(points, fill=1)
        
        c.setFillColor(self.COLORS['gold'])
        points = [self.width, 0, self.width - 100, 0, self.width, 100]
        c.drawPolygon(points, fill=1)
        
    def _draw_header(self, c: canvas.Canvas):
        """Draw certificate header"""
        # Main title
        c.setFillColor(self.COLORS['black'])
        c.setFont(*self.FONTS['title'])
        c.drawCentredString(self.width/2, self.height - 150, "CERTIFICATE")
        
        # Subtitle
        c.setFont(*self.FONTS['subtitle'])
        c.drawCentredString(self.width/2, self.height - 190, "OF ACHIEVEMENT")
        
        # Decorative line
        c.setStrokeColor(self.COLORS['gold'])
        c.setLineWidth(2)
        c.line(self.width/2 - 150, self.height - 210, 
               self.width/2 + 150, self.height - 210)
        
    def _draw_recipient_section(self, c: canvas.Canvas, first_name: str, last_name: str):
        """Draw recipient information"""
        # "Presented to" text
        c.setFont(*self.FONTS['body'])
        c.setFillColor(self.COLORS['black'])
        c.drawCentredString(self.width/2, self.height - 270, 
                           "THIS CERTIFICATE IS PROUDLY PRESENTED TO")
        
        # Recipient name
        full_name = f"{first_name} {last_name}"
        c.setFont(*self.FONTS['name'])
        
        # Auto-size name if too long
        font_size = self.FONTS['name'][1]
        while c.stringWidth(full_name, self.FONTS['name'][0], font_size) > self.width - 200:
            font_size -= 2
            
        c.setFont(self.FONTS['name'][0], font_size)
        c.drawCentredString(self.width/2, self.height - 320, full_name)
        
    def _draw_course_section(self, c: canvas.Canvas, course_name: str):
        """Draw course information"""
        # "For completing" text
        c.setFont(*self.FONTS['body'])
        c.drawCentredString(self.width/2, self.height - 380, "FOR COMPLETING")
        
        # Course name
        c.setFont(*self.FONTS['course'])
        
        # Auto-size course name if too long
        font_size = self.FONTS['course'][1]
        while c.stringWidth(course_name, self.FONTS['course'][0], font_size) > self.width - 200:
            font_size -= 2
            
        c.setFont(self.FONTS['course'][0], font_size)
        c.drawCentredString(self.width/2, self.height - 430, course_name)
        
        # Description text
        c.setFont(*self.FONTS['small'])
        text_lines = [
            "THIS FORMS PART OF A SOCIAL CONTRACT BETWEEN YOURSELF AND",
            "YOUR SCHOOL, DEMONSTRATING A CLEAR UNDERSTANDING OF THE",
            "TOPIC AND EXPECTATIONS."
        ]
        y_pos = self.height - 480
        for line in text_lines:
            c.drawCentredString(self.width/2, y_pos, line)
            y_pos -= 18
            
    def _draw_footer(self, c: canvas.Canvas, score: str, date: str):
        """Draw footer with score and date"""
        # Score
        c.setFont(*self.FONTS['score'])
        c.drawString(150, 120, score)
        
        c.setFont(*self.FONTS['small'])
        c.drawString(150, 100, "SCORE")
        
        # Date
        c.setFont(*self.FONTS['score'])
        c.drawRightString(self.width - 150, 120, date)
        
        c.setFont(*self.FONTS['small'])
        c.drawRightString(self.width - 150, 100, "DATE")
        
    def _draw_logo(self, c: canvas.Canvas):
        """Draw SafeSteps Learning logo"""
        # Logo background circle
        c.setFillColor(self.COLORS['navy'])
        c.circle(self.width/2, 80, 40, fill=1)
        
        # Gold ring
        c.setStrokeColor(self.COLORS['gold'])
        c.setLineWidth(3)
        c.circle(self.width/2, 80, 43, fill=0)
        
        # Logo text
        c.setFillColor(self.COLORS['white'])
        c.setFont(*self.FONTS['logo'])
        c.drawCentredString(self.width/2, 85, "SAFE STEPS")
        c.drawCentredString(self.width/2, 73, "LEARNING")
        
        # Footprint icon (simplified)
        c.setFillColor(self.COLORS['white'])
        # Left footprint dot
        c.circle(self.width/2 - 8, 95, 3, fill=1)
        # Right footprint dot
        c.circle(self.width/2 + 8, 95, 3, fill=1)
        
    def generate_batch(
        self,
        recipients: list,
        course_name: str,
        output_dir: Optional[str] = None
    ) -> list:
        """
        Generate certificates for multiple recipients
        
        Args:
            recipients: List of dicts with 'first_name' and 'last_name'
            course_name: Name of the course
            output_dir: Directory to save certificates (default: temp)
            
        Returns:
            List of generated file paths
        """
        if not output_dir:
            output_dir = tempfile.mkdtemp()
            
        generated_files = []
        
        for recipient in recipients:
            first_name = recipient.get('first_name', '')
            last_name = recipient.get('last_name', '')
            
            if not first_name or not last_name:
                continue
                
            # Generate safe filename
            safe_name = f"{first_name}_{last_name}".replace(" ", "_")
            output_path = os.path.join(output_dir, f"{safe_name}_certificate.pdf")
            
            # Generate certificate
            self.generate_certificate(
                first_name=first_name,
                last_name=last_name,
                course_name=course_name,
                output_path=output_path
            )
            
            generated_files.append(output_path)
            
        return generated_files
        
    def generate_preview(self, course_name: str = "Sample Course") -> bytes:
        """
        Generate a preview certificate as bytes
        
        Args:
            course_name: Course name for preview
            
        Returns:
            PDF content as bytes
        """
        # Create in-memory file
        buffer = io.BytesIO()
        
        # Generate to temp file first (ReportLab limitation)
        temp_path = self.generate_certificate(
            first_name="John",
            last_name="Doe",
            course_name=course_name,
            date="January 1, 2025"
        )
        
        # Read and return bytes
        with open(temp_path, 'rb') as f:
            buffer.write(f.read())
            
        # Clean up temp file
        os.unlink(temp_path)
        
        return buffer.getvalue()


# Integration function for SafeSteps
def create_programmatic_generator():
    """Factory function to create certificate generator"""
    return CertificateGenerator()
'''
    
    # Save the production code
    with open("certificate_generator_production.py", "w") as f:
        f.write(code)
    
    print("\n7. Production Code Generated:")
    print("   ✓ Created: certificate_generator_production.py")
    print("   This code can replace the current template-based system")


if __name__ == "__main__":
    # Check if reportlab is installed
    try:
        import reportlab
    except ImportError:
        print("Installing reportlab...")
        os.system("pip install reportlab pillow")
    
    # Run analysis
    success = analyze_certificate_reproduction()
    
    if success:
        # Generate production code
        create_production_certificate_generator()
        
        print("\n" + "="*50)
        print("CONCLUSION: Programmatic PDF generation is fully feasible!")
        print("="*50)
        
        print("\nNext Steps:")
        print("1. Install reportlab: pip install reportlab")
        print("2. Review the generated certificate_generator_production.py")
        print("3. Test with your specific requirements")
        print("4. Integrate with SafeSteps to replace template system")
        
        print("\nBenefits over template system:")
        print("- No PyMuPDF compatibility issues")
        print("- No form field management")
        print("- Dynamic designs possible")
        print("- Better text fitting")
        print("- Easier maintenance")