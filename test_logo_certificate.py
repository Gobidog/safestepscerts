#!/usr/bin/env python3
"""Test certificate generation with logo"""

from certificate_generator_production import generate_certificate_for_app

# Generate a test certificate
print("Generating test certificate...")
pdf_bytes = generate_certificate_for_app(
    student_name="Marshall Newton",
    course_name="Vapes and Vaping",
    score="Pass",
    completion_date="Jul 30, 2025"
)

# Save to file
with open("test_certificate_with_logo.pdf", "wb") as f:
    f.write(pdf_bytes)

print(f"Certificate generated! Size: {len(pdf_bytes)} bytes")
print("Saved as: test_certificate_with_logo.pdf")
print("\nNote: The logo file 'safesteps_logo.png' appears to be only 42 bytes.")
print("Please ensure you've saved the actual logo image to this file.")