#!/usr/bin/env python3
"""
Test script for template upload and usage functionality
Run this to verify the template system is working correctly
"""

import os
import sys
from pathlib import Path
import tempfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.storage import StorageManager
from utils.pdf_generator import PDFGenerator
from config import config

def test_storage_manager():
    """Test the storage manager functionality"""
    logger.info("Testing Storage Manager...")
    
    storage = StorageManager()
    logger.info(f"Storage mode: {'Local' if storage.use_local else 'Google Cloud Storage'}")
    
    # Test listing templates
    try:
        templates = storage.list_templates()
        logger.info(f"Found {len(templates)} existing templates")
        for template in templates:
            logger.info(f"  - {template.get('name')} ({template.get('size', 0) / 1024:.1f} KB)")
    except Exception as e:
        logger.error(f"Failed to list templates: {e}")
        return False
    
    # Test saving a dummy template
    try:
        test_content = b"Mock PDF content for testing"
        test_name = "test_template_delete_me"
        metadata = {
            "display_name": "Test Template",
            "description": "This is a test template",
            "test": True
        }
        
        success = storage.save_template(test_content, test_name, metadata)
        if success:
            logger.info(f"Successfully saved test template: {test_name}")
        else:
            logger.error("Failed to save test template")
            return False
            
        # Test retrieving the template
        retrieved = storage.get_template(test_name)
        if retrieved == test_content:
            logger.info("Successfully retrieved test template")
        else:
            logger.error("Retrieved template content doesn't match")
            return False
            
        # Test getting template path
        template_path = storage.get_template_path(test_name)
        if template_path and os.path.exists(template_path):
            logger.info(f"Template path exists: {template_path}")
        else:
            logger.error("Template path not found")
            return False
            
        # Test deleting the template
        if storage.delete_template(test_name):
            logger.info("Successfully deleted test template")
        else:
            logger.error("Failed to delete test template")
            return False
            
    except Exception as e:
        logger.error(f"Storage test failed: {e}")
        return False
    
    logger.info("✅ Storage Manager tests passed!")
    return True


def test_pdf_generator():
    """Test PDF generator with a sample template"""
    logger.info("\nTesting PDF Generator...")
    
    # Check if any templates exist
    storage = StorageManager()
    templates = storage.list_templates()
    
    if not templates:
        logger.warning("No templates found to test PDF generation")
        logger.info("Please upload a template through the admin interface first")
        return True  # Don't fail the test, just skip
    
    # Use the first available template
    template = templates[0]
    template_name = template.get('name')
    logger.info(f"Using template: {template_name}")
    
    try:
        # Get template path
        template_path = storage.get_template_path(template_name)
        if not template_path:
            logger.error("Failed to get template path")
            return False
            
        # Initialize PDF generator
        generator = PDFGenerator(template_path)
        
        # Validate template
        validation_info = generator.validate_template()
        logger.info(f"Template validation: {'Valid' if validation_info['valid'] else 'Invalid'}")
        logger.info(f"  - Fields found: {validation_info['fields_found']}")
        logger.info(f"  - Page count: {validation_info['page_count']}")
        
        if not validation_info['valid']:
            logger.error(f"  - Errors: {validation_info['errors']}")
            return False
            
        # Generate a test certificate
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test_certificate.pdf")
            
            cert_path = generator.generate_certificate(
                first_name="Test",
                last_name="User",
                output_path=output_path
            )
            
            if os.path.exists(cert_path) and os.path.getsize(cert_path) > 0:
                logger.info(f"Successfully generated test certificate: {os.path.getsize(cert_path)} bytes")
            else:
                logger.error("Failed to generate test certificate")
                return False
                
        logger.info("✅ PDF Generator tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"PDF generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_template_workflow():
    """Test the complete template workflow"""
    logger.info("\nTesting Complete Template Workflow...")
    
    storage = StorageManager()
    
    # Create a minimal valid PDF for testing
    try:
        import fitz  # PyMuPDF
        
        # Create a test PDF with form fields
        doc = fitz.open()
        page = doc.new_page()
        
        # Add form fields
        # First name field
        first_name_rect = fitz.Rect(100, 100, 300, 130)
        first_name_widget = fitz.Widget()
        first_name_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        first_name_widget.field_name = "FirstName"
        first_name_widget.rect = first_name_rect
        first_name_widget.field_value = ""
        page.add_widget(first_name_widget)
        
        # Last name field  
        last_name_rect = fitz.Rect(100, 150, 300, 180)
        last_name_widget = fitz.Widget()
        last_name_widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
        last_name_widget.field_name = "LastName"
        last_name_widget.rect = last_name_rect
        last_name_widget.field_value = ""
        page.add_widget(last_name_widget)
        
        # Save to bytes
        pdf_bytes = doc.tobytes()
        doc.close()
        
        logger.info("Created test PDF with form fields")
        
        # Test the complete workflow
        # 1. Save template
        template_name = "workflow_test_template"
        metadata = {
            "display_name": "Workflow Test Template",
            "description": "Template for testing the workflow"
        }
        
        if storage.save_template(pdf_bytes, template_name, metadata):
            logger.info("✅ Step 1: Template saved successfully")
        else:
            logger.error("❌ Step 1: Failed to save template")
            return False
            
        # 2. List templates and verify it's there
        templates = storage.list_templates()
        found = any(t['name'] == f"{template_name}.pdf" for t in templates)
        if found:
            logger.info("✅ Step 2: Template found in listing")
        else:
            logger.error("❌ Step 2: Template not found in listing")
            return False
            
        # 3. Get template path
        template_path = storage.get_template_path(template_name)
        if template_path and os.path.exists(template_path):
            logger.info(f"✅ Step 3: Template path retrieved: {template_path}")
        else:
            logger.error("❌ Step 3: Failed to get template path")
            return False
            
        # 4. Use template to generate certificate
        generator = PDFGenerator(template_path)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "workflow_test.pdf")
            cert_path = generator.generate_certificate(
                first_name="Workflow",
                last_name="Test",
                output_path=output_path
            )
            
            if os.path.exists(cert_path):
                logger.info("✅ Step 4: Certificate generated successfully")
            else:
                logger.error("❌ Step 4: Failed to generate certificate")
                return False
                
        # 5. Clean up - delete test template
        if storage.delete_template(template_name):
            logger.info("✅ Step 5: Test template cleaned up")
        else:
            logger.error("❌ Step 5: Failed to clean up test template")
            
        logger.info("✅ Complete workflow test passed!")
        return True
        
    except ImportError:
        logger.warning("PyMuPDF not available - skipping workflow test")
        return True
    except Exception as e:
        logger.error(f"Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    logger.info("=== SafeSteps Template System Test Suite ===\n")
    
    # Check configuration
    logger.info(f"App Name: {config.app.app_name}")
    logger.info(f"Storage mode: {'Local' if config.storage.use_local_storage else 'GCS'}")
    logger.info(f"Local storage path: {config.storage.local_storage_path}\n")
    
    # Run tests
    all_passed = True
    
    if not test_storage_manager():
        all_passed = False
        
    if not test_pdf_generator():
        all_passed = False
        
    if not test_template_workflow():
        all_passed = False
    
    # Summary
    logger.info("\n=== Test Summary ===")
    if all_passed:
        logger.info("✅ All tests passed! The template system is working correctly.")
    else:
        logger.error("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()