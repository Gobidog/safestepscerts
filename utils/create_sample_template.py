#!/usr/bin/env python3
"""
Utility to create sample PDF certificate templates with form fields
This helps users create compatible templates for the SafeSteps system
"""

import fitz  # PyMuPDF
import argparse
from pathlib import Path
from typing import List, Tuple

def create_basic_certificate_template(output_path: str = "sample_certificate_template.pdf"):
    """Create a basic certificate template with standard form fields"""
    
    # Create new PDF document
    doc = fitz.open()
    
    # Add a page (Letter size)
    page = doc.new_page(width=612, height=792)  # 8.5 x 11 inches in points
    
    # Add background color
    page.draw_rect(page.rect, color=(0.95, 0.95, 0.95), fill=(0.95, 0.95, 0.95))
    
    # Add border
    border_rect = fitz.Rect(50, 50, 562, 742)
    page.draw_rect(border_rect, color=(0.2, 0.2, 0.2), width=2)
    
    # Add title
    title_point = fitz.Point(306, 150)  # Center X
    page.insert_text(
        title_point,
        "Certificate of Completion",
        fontsize=32,
        fontname="helvetica-bold",
        color=(0.012, 0.165, 0.318)  # SafeSteps primary color
    )
    
    # Add subtitle
    subtitle_point = fitz.Point(306, 200)
    page.insert_text(
        subtitle_point,
        "This is to certify that",
        fontsize=18,
        fontname="helvetica",
        color=(0.3, 0.3, 0.3)
    )
    
    # Add form fields
    # First Name field
    first_name_rect = fitz.Rect(200, 250, 412, 290)
    first_name_widget = fitz.Widget()
    first_name_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    first_name_widget.field_name = "FirstName"
    first_name_widget.rect = first_name_rect
    first_name_widget.field_value = ""
    first_name_widget.text_fontsize = 24
    first_name_widget.text_align = fitz.TEXT_ALIGN_CENTER
    first_name_widget.border_width = 0
    first_name_widget.fill_color = []  # Transparent
    page.add_widget(first_name_widget)
    
    # Last Name field
    last_name_rect = fitz.Rect(200, 300, 412, 340)
    last_name_widget = fitz.Widget()
    last_name_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    last_name_widget.field_name = "LastName"
    last_name_widget.rect = last_name_rect
    last_name_widget.field_value = ""
    last_name_widget.text_fontsize = 24
    last_name_widget.text_align = fitz.TEXT_ALIGN_CENTER
    last_name_widget.border_width = 0
    last_name_widget.fill_color = []  # Transparent
    page.add_widget(last_name_widget)
    
    # Add line under name fields
    page.draw_line(fitz.Point(150, 350), fitz.Point(462, 350), color=(0.6, 0.6, 0.6), width=1)
    
    # Add completion text
    completion_point = fitz.Point(306, 400)
    page.insert_text(
        completion_point,
        "has successfully completed the",
        fontsize=16,
        fontname="helvetica",
        color=(0.3, 0.3, 0.3)
    )
    
    # Add course name placeholder
    course_point = fitz.Point(306, 450)
    page.insert_text(
        course_point,
        "SafeSteps Training Program",
        fontsize=22,
        fontname="helvetica-bold",
        color=(0.012, 0.165, 0.318)
    )
    
    # Add date field
    date_rect = fitz.Rect(250, 550, 362, 580)
    date_widget = fitz.Widget()
    date_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    date_widget.field_name = "Date"
    date_widget.rect = date_rect
    date_widget.field_value = ""
    date_widget.text_fontsize = 14
    date_widget.text_align = fitz.TEXT_ALIGN_CENTER
    date_widget.border_width = 0
    date_widget.fill_color = []  # Transparent
    page.add_widget(date_widget)
    
    # Add line under date
    page.draw_line(fitz.Point(200, 590), fitz.Point(412, 590), color=(0.6, 0.6, 0.6), width=1)
    
    # Add "Date" label
    date_label_point = fitz.Point(306, 605)
    page.insert_text(
        date_label_point,
        "Date",
        fontsize=12,
        fontname="helvetica",
        color=(0.5, 0.5, 0.5)
    )
    
    # Add organization name at bottom
    org_point = fitz.Point(306, 680)
    page.insert_text(
        org_point,
        "SafeSteps Organization",
        fontsize=16,
        fontname="helvetica-bold",
        color=(0.012, 0.165, 0.318)
    )
    
    # Save the document
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created basic certificate template: {output_path}")
    print("   Form fields: FirstName, LastName, Date")


def create_advanced_certificate_template(output_path: str = "advanced_certificate_template.pdf"):
    """Create an advanced certificate template with multiple form fields"""
    
    # Create new PDF document
    doc = fitz.open()
    
    # Add a page (Letter size, landscape)
    page = doc.new_page(width=792, height=612)  # 11 x 8.5 inches in points
    
    # Add decorative border
    page.draw_rect(page.rect, color=(0.98, 0.98, 0.98), fill=(0.98, 0.98, 0.98))
    outer_border = fitz.Rect(30, 30, 762, 582)
    page.draw_rect(outer_border, color=(0.604, 0.792, 0.235), width=3)  # SafeSteps accent color
    inner_border = fitz.Rect(40, 40, 752, 572)
    page.draw_rect(inner_border, color=(0.012, 0.165, 0.318), width=2)  # SafeSteps primary color
    
    # Add logo placeholder
    logo_rect = fitz.Rect(80, 80, 180, 140)
    page.draw_rect(logo_rect, color=(0.012, 0.165, 0.318), fill=(0.95, 0.95, 0.95))
    logo_point = fitz.Point(130, 115)
    page.insert_text(logo_point, "LOGO", fontsize=20, color=(0.5, 0.5, 0.5))
    
    # Add title
    title_point = fitz.Point(396, 120)
    page.insert_text(
        title_point,
        "Certificate of Achievement",
        fontsize=36,
        fontname="helvetica-bold",
        color=(0.012, 0.165, 0.318)
    )
    
    # Add decorative line
    page.draw_line(fitz.Point(250, 140), fitz.Point(542, 140), color=(0.604, 0.792, 0.235), width=2)
    
    # Add "This certifies that"
    certify_point = fitz.Point(396, 180)
    page.insert_text(
        certify_point,
        "This certifies that",
        fontsize=16,
        fontname="helvetica-oblique",
        color=(0.4, 0.4, 0.4)
    )
    
    # Add name fields side by side
    # First Name
    first_name_rect = fitz.Rect(200, 210, 390, 250)
    first_name_widget = fitz.Widget()
    first_name_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    first_name_widget.field_name = "FirstName"
    first_name_widget.rect = first_name_rect
    first_name_widget.field_value = ""
    first_name_widget.text_fontsize = 28
    first_name_widget.text_align = fitz.TEXT_ALIGN_RIGHT
    first_name_widget.border_width = 0
    first_name_widget.fill_color = []
    first_name_widget.text_color = (0.012, 0.165, 0.318)
    page.add_widget(first_name_widget)
    
    # Last Name
    last_name_rect = fitz.Rect(402, 210, 592, 250)
    last_name_widget = fitz.Widget()
    last_name_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    last_name_widget.field_name = "LastName"
    last_name_widget.rect = last_name_rect
    last_name_widget.field_value = ""
    last_name_widget.text_fontsize = 28
    last_name_widget.text_align = fitz.TEXT_ALIGN_LEFT
    last_name_widget.border_width = 0
    last_name_widget.fill_color = []
    last_name_widget.text_color = (0.012, 0.165, 0.318)
    page.add_widget(last_name_widget)
    
    # Add line under name
    page.draw_line(fitz.Point(180, 260), fitz.Point(612, 260), color=(0.8, 0.8, 0.8), width=1)
    
    # Add achievement text
    achieve_point = fitz.Point(396, 300)
    page.insert_text(
        achieve_point,
        "has successfully completed all requirements for",
        fontsize=14,
        fontname="helvetica",
        color=(0.3, 0.3, 0.3)
    )
    
    # Add course/program field
    course_rect = fitz.Rect(150, 330, 642, 370)
    course_widget = fitz.Widget()
    course_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    course_widget.field_name = "CourseName"
    course_widget.rect = course_rect
    course_widget.field_value = "SafeSteps Professional Certification"
    course_widget.text_fontsize = 22
    course_widget.text_align = fitz.TEXT_ALIGN_CENTER
    course_widget.border_width = 0
    course_widget.fill_color = []
    course_widget.text_color = (0.604, 0.792, 0.235)
    page.add_widget(course_widget)
    
    # Add completion details
    details_point = fitz.Point(396, 410)
    page.insert_text(
        details_point,
        "Demonstrating proficiency in safety protocols and best practices",
        fontsize=12,
        fontname="helvetica-oblique",
        color=(0.5, 0.5, 0.5)
    )
    
    # Add signature section
    # Instructor signature line
    page.draw_line(fitz.Point(150, 480), fitz.Point(350, 480), color=(0.6, 0.6, 0.6), width=1)
    inst_label = fitz.Point(250, 495)
    page.insert_text(inst_label, "Instructor", fontsize=10, color=(0.5, 0.5, 0.5))
    
    # Date line
    page.draw_line(fitz.Point(442, 480), fitz.Point(642, 480), color=(0.6, 0.6, 0.6), width=1)
    
    # Date field
    date_rect = fitz.Rect(442, 460, 642, 480)
    date_widget = fitz.Widget()
    date_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    date_widget.field_name = "Date"
    date_widget.rect = date_rect
    date_widget.field_value = ""
    date_widget.text_fontsize = 12
    date_widget.text_align = fitz.TEXT_ALIGN_CENTER
    date_widget.border_width = 0
    date_widget.fill_color = []
    page.add_widget(date_widget)
    
    date_label = fitz.Point(542, 495)
    page.insert_text(date_label, "Date", fontsize=10, color=(0.5, 0.5, 0.5))
    
    # Add certificate ID field
    cert_id_rect = fitz.Rect(600, 540, 740, 560)
    cert_id_widget = fitz.Widget()
    cert_id_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    cert_id_widget.field_name = "CertificateID"
    cert_id_widget.rect = cert_id_rect
    cert_id_widget.field_value = ""
    cert_id_widget.text_fontsize = 10
    cert_id_widget.text_align = fitz.TEXT_ALIGN_RIGHT
    cert_id_widget.border_width = 0
    cert_id_widget.fill_color = []
    cert_id_widget.text_color = (0.7, 0.7, 0.7)
    page.add_widget(cert_id_widget)
    
    # Add certificate ID label
    cert_label = fitz.Point(590, 555)
    page.insert_text(cert_label, "Certificate #", fontsize=8, color=(0.7, 0.7, 0.7))
    
    # Save the document
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created advanced certificate template: {output_path}")
    print("   Form fields: FirstName, LastName, Date, CourseName, CertificateID")


def create_minimal_template(output_path: str = "minimal_certificate_template.pdf"):
    """Create a minimal certificate template with just name fields"""
    
    # Create new PDF document
    doc = fitz.open()
    
    # Add a page
    page = doc.new_page(width=612, height=792)
    
    # Add title
    title_point = fitz.Point(306, 200)
    page.insert_text(
        title_point,
        "Certificate",
        fontsize=48,
        fontname="helvetica-bold"
    )
    
    # Add full name field (single field for both names)
    name_rect = fitz.Rect(106, 350, 506, 400)
    name_widget = fitz.Widget()
    name_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
    name_widget.field_name = "FullName"
    name_widget.rect = name_rect
    name_widget.field_value = ""
    name_widget.text_fontsize = 32
    name_widget.text_align = fitz.TEXT_ALIGN_CENTER
    name_widget.border_width = 0
    name_widget.fill_color = []
    page.add_widget(name_widget)
    
    # Add line under name
    page.draw_line(fitz.Point(100, 410), fitz.Point(512, 410), width=2)
    
    # Save the document
    doc.save(output_path)
    doc.close()
    
    print(f"✅ Created minimal certificate template: {output_path}")
    print("   Form fields: FullName")


def main():
    """Main function to create sample templates"""
    parser = argparse.ArgumentParser(description="Create sample PDF certificate templates")
    parser.add_argument(
        "--type",
        choices=["basic", "advanced", "minimal", "all"],
        default="basic",
        help="Type of template to create"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output filename (default: auto-generated based on type)"
    )
    
    args = parser.parse_args()
    
    print("SafeSteps Certificate Template Generator")
    print("=" * 40)
    
    try:
        if args.type == "basic" or args.type == "all":
            output = args.output if args.output and args.type == "basic" else "sample_certificate_template.pdf"
            create_basic_certificate_template(output)
            
        if args.type == "advanced" or args.type == "all":
            output = args.output if args.output and args.type == "advanced" else "advanced_certificate_template.pdf"
            create_advanced_certificate_template(output)
            
        if args.type == "minimal" or args.type == "all":
            output = args.output if args.output and args.type == "minimal" else "minimal_certificate_template.pdf"
            create_minimal_template(output)
            
        print("\n✅ Template creation complete!")
        print("\nThese templates can be uploaded through the SafeSteps admin interface.")
        print("The PDF generator will automatically detect and use the form fields.")
        
    except Exception as e:
        print(f"\n❌ Error creating template: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())