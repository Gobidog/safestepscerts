#!/usr/bin/env python3
"""Test the certificate generation fix directly"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from certificate_generator_production import generate_certificate_for_app
from datetime import datetime

print("Testing programmatic certificate generation...")

try:
    # Test parameters
    student_name = "John Doe"
    course_name = "Vapes and Vaping"
    score = 85
    completion_date = datetime.now()
    
    print(f"Generating certificate for: {student_name}")
    print(f"Course: {course_name}")
    print(f"Score: {score}%")
    print(f"Date: {completion_date.strftime('%B %d, %Y')}")
    
    # Generate certificate
    pdf_bytes = generate_certificate_for_app(student_name, course_name, score, completion_date)
    
    if pdf_bytes:
        # Save to file to verify
        output_file = "test_certificate_output.pdf"
        with open(output_file, "wb") as f:
            f.write(pdf_bytes)
        print(f"\n✅ SUCCESS: Certificate generated successfully!")
        print(f"PDF saved to: {output_file}")
        print(f"File size: {len(pdf_bytes)} bytes")
    else:
        print("\n❌ FAILED: No PDF bytes returned")
        
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()