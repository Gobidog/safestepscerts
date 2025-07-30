#!/usr/bin/env python3
"""
Test integration of programmatic certificate generation with SafeSteps app
"""

import streamlit as st
from datetime import datetime
from certificate_generator_production import generate_certificate_for_app

# Simulate Streamlit app behavior
def test_integration():
    print("Testing programmatic certificate generation integration...")
    
    # Test cases
    test_cases = [
        {
            "name": "Basic Test",
            "student": "Test Student",
            "course": "Vapes and Vaping",
            "score": "Passed"
        },
        {
            "name": "Long Names",
            "student": "Alexander Christopher Wellington-Smythe III",
            "course": "Understanding the Dangers of Substance Abuse and Making Healthy Choices",
            "score": "95%"
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        print(f"  Student: {test['student']}")
        print(f"  Course: {test['course']}")
        
        # Generate certificate using the new function
        pdf_bytes = generate_certificate_for_app(
            student_name=test['student'],
            course_name=test['course'],
            score=test['score'],
            completion_date=datetime.now().strftime("%B %d, %Y")
        )
        
        # Verify PDF was generated
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')  # PDF header
        
        print(f"  ✅ Generated PDF: {len(pdf_bytes)} bytes")
        
        # Save for manual inspection
        filename = f"test_integration_{test['name'].replace(' ', '_').lower()}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_bytes)
        print(f"  📄 Saved to: {filename}")
    
    print("\n✅ All integration tests passed!")
    print("\nTo integrate with app.py, replace the existing certificate generation with:")
    print("""
    # Instead of:
    # pdf_path = generator.generate_certificate(first_name, last_name)
    
    # Use:
    from certificate_generator_production import generate_certificate_for_app
    
    pdf_bytes = generate_certificate_for_app(
        student_name=f"{first_name} {last_name}",
        course_name=template_name,
        score="Passed",
        completion_date=datetime.now().strftime("%B %d, %Y")
    )
    
    # Then use st.download_button directly with bytes:
    st.download_button(
        label="Download Certificate",
        data=pdf_bytes,
        file_name=f"certificate_{first_name}_{last_name}.pdf",
        mime="application/pdf"
    )
    """)

if __name__ == "__main__":
    test_integration()