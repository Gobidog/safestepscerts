"""
Unit tests for PDF generator module
"""
import pytest
import os
import tempfile
import fitz
from pathlib import Path
from unittest.mock import patch, MagicMock
import zipfile

from utils.pdf_generator import (
    PDFGenerator,
    CertificateField,
    GenerationResult
)


class TestPDFGenerator:
    """Test PDF generator functionality"""
    
    @pytest.fixture
    def mock_template_path(self):
        """Create a mock PDF template for testing"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Create a simple PDF with form fields
            doc = fitz.open()
            page = doc.new_page()
            
            # Add text fields
            widget1 = fitz.Widget()
            widget1.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget1.field_name = "FirstName"
            widget1.rect = fitz.Rect(100, 100, 300, 130)
            page.add_widget(widget1)
            
            widget2 = fitz.Widget()
            widget2.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget2.field_name = "LastName"
            widget2.rect = fitz.Rect(100, 150, 300, 180)
            page.add_widget(widget2)
            
            widget3 = fitz.Widget()
            widget3.field_type = fitz.PDF_WIDGET_TYPE_TEXT
            widget3.field_name = "Date"
            widget3.rect = fitz.Rect(100, 200, 300, 230)
            page.add_widget(widget3)
            
            doc.save(tmp.name)
            doc.close()
            
            yield tmp.name
            
            # Cleanup
            os.unlink(tmp.name)
    
    def test_init_detects_form_fields(self, mock_template_path):
        """Test that initialization detects form fields"""
        generator = PDFGenerator(mock_template_path)
        
        assert len(generator.fields) == 3
        assert "FirstName" in generator.fields
        assert "LastName" in generator.fields
        assert "Date" in generator.fields
        
        # Check field properties
        first_name_field = generator.fields["FirstName"]
        assert isinstance(first_name_field, CertificateField)
        assert first_name_field.name == "FirstName"
        assert first_name_field.page_num == 0
    
    def test_init_with_custom_field_mapping(self, mock_template_path):
        """Test initialization with custom field mapping"""
        custom_mapping = {
            "first_name": "FirstName",
            "last_name": "LastName",
            "date": "Date"
        }
        
        generator = PDFGenerator(mock_template_path, field_mapping=custom_mapping)
        
        assert generator.field_mapping == custom_mapping
    
    def test_init_with_invalid_template(self):
        """Test initialization with invalid template path"""
        with pytest.raises(ValueError) as excinfo:
            PDFGenerator("/nonexistent/template.pdf")
        
        assert "Invalid template" in str(excinfo.value)
    
    def test_calculate_text_width(self, mock_template_path):
        """Test text width calculation"""
        generator = PDFGenerator(mock_template_path)
        
        # Test normal text
        width = generator._calculate_text_width("Hello", 12)
        assert width == 5 * 12 * 0.6  # 5 chars * font_size * ratio
        
        # Test empty text
        width = generator._calculate_text_width("", 12)
        assert width == 0
    
    def test_adjust_font_size(self, mock_template_path):
        """Test font size adjustment"""
        generator = PDFGenerator(mock_template_path)
        
        # Create a field with specific dimensions
        field = CertificateField(
            name="test",
            rect=fitz.Rect(0, 0, 100, 30),
            page_num=0,
            max_font_size=24,
            min_font_size=10
        )
        
        # Test short text (should use max font size)
        font_size = generator._adjust_font_size("Hi", field)
        assert font_size == 24
        
        # Test long text (should reduce font size)
        long_text = "This is a very long name that needs to fit"
        font_size = generator._adjust_font_size(long_text, field)
        assert font_size < 24
        assert font_size >= 10
    
    def test_generate_certificate_basic(self, mock_template_path):
        """Test basic certificate generation"""
        generator = PDFGenerator(mock_template_path)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "test_cert.pdf")
            
            # Generate certificate
            result_path = generator.generate_certificate(
                "John",
                "Doe",
                output_path
            )
            
            assert result_path == output_path
            assert os.path.exists(output_path)
            
            # Verify the PDF has the filled fields
            doc = fitz.open(output_path)
            page = doc[0]
            
            # Check if fields were filled
            fields_found = False
            for widget in page.widgets():
                if widget.field_name == "FirstName":
                    assert widget.field_value == "John"
                    fields_found = True
                elif widget.field_name == "LastName":
                    assert widget.field_value == "Doe"
                    fields_found = True
            
            doc.close()
    
    def test_generate_certificate_with_unicode(self, mock_template_path):
        """Test certificate generation with unicode names"""
        generator = PDFGenerator(mock_template_path)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "unicode_cert.pdf")
            
            # Generate with unicode names
            result_path = generator.generate_certificate(
                "José",
                "García-López",
                output_path
            )
            
            assert os.path.exists(result_path)
    
    def test_generate_certificate_auto_filename(self, mock_template_path):
        """Test certificate generation with automatic filename"""
        generator = PDFGenerator(mock_template_path)
        
        # Generate without specifying output path
        result_path = generator.generate_certificate("Jane", "Smith")
        
        assert os.path.exists(result_path)
        assert "Jane_Smith" in result_path
        assert result_path.endswith(".pdf")
        
        # Cleanup
        os.unlink(result_path)
    
    def test_generate_preview(self, mock_template_path):
        """Test preview generation"""
        generator = PDFGenerator(mock_template_path)
        
        # Generate preview
        preview_bytes = generator.generate_preview()
        
        assert isinstance(preview_bytes, bytes)
        assert len(preview_bytes) > 0
        
        # Verify it's a valid PDF
        # PDF files start with %PDF
        assert preview_bytes.startswith(b'%PDF')
    
    def test_generate_batch_success(self, mock_template_path):
        """Test batch certificate generation"""
        generator = PDFGenerator(mock_template_path)
        
        recipients = [
            {"first_name": "Alice", "last_name": "Anderson"},
            {"first_name": "Bob", "last_name": "Brown"},
            {"first_name": "Charlie", "last_name": "Chen"}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            results, zip_path = generator.generate_batch(recipients, tmpdir)
            
            # Check results
            assert len(results) == 3
            assert all(r.success for r in results)
            assert all(isinstance(r, GenerationResult) for r in results)
            
            # Check ZIP file
            assert os.path.exists(zip_path)
            assert zip_path.endswith("certificates.zip")
            
            # Verify ZIP contents
            with zipfile.ZipFile(zip_path, 'r') as zf:
                files = zf.namelist()
                assert len(files) == 3
                assert any("Alice_Anderson" in f for f in files)
                assert any("Bob_Brown" in f for f in files)
                assert any("Charlie_Chen" in f for f in files)
    
    def test_generate_batch_with_errors(self, mock_template_path):
        """Test batch generation with some invalid recipients"""
        generator = PDFGenerator(mock_template_path)
        
        recipients = [
            {"first_name": "Valid", "last_name": "Name"},
            {"first_name": "", "last_name": "NoFirstName"},
            {"first_name": "NoLastName", "last_name": ""},
            {"first_name": "Another", "last_name": "Valid"}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            results, zip_path = generator.generate_batch(recipients, tmpdir)
            
            # Check results
            assert len(results) == 4
            assert results[0].success is True
            assert results[1].success is False
            assert results[2].success is False
            assert results[3].success is True
            
            # Check error messages
            assert "Missing first or last name" in results[1].error
            assert "Missing first or last name" in results[2].error
            
            # ZIP should only contain successful certificates
            with zipfile.ZipFile(zip_path, 'r') as zf:
                files = zf.namelist()
                assert len(files) == 2
    
    def test_generate_batch_with_duplicates(self, mock_template_path):
        """Test batch generation handles duplicate names"""
        generator = PDFGenerator(mock_template_path)
        
        recipients = [
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "John", "last_name": "Doe"},
            {"first_name": "John", "last_name": "Doe"}
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Generate with sequential processing to ensure consistent ordering
            results, zip_path = generator.generate_batch(recipients, tmpdir, parallel=False)
            
            # All should succeed
            assert all(r.success for r in results)
            
            # Check filenames are unique
            filenames = [r.filename for r in results]
            assert len(set(filenames)) == 3, f"Expected 3 unique filenames, got: {filenames}"
            assert "John_Doe.pdf" in filenames
            assert "John_Doe_1.pdf" in filenames
            assert "John_Doe_2.pdf" in filenames
    
    def test_generate_batch_with_progress_callback(self, mock_template_path):
        """Test batch generation with progress callback"""
        generator = PDFGenerator(mock_template_path)
        
        recipients = [
            {"first_name": f"User{i}", "last_name": f"Test{i}"}
            for i in range(5)
        ]
        
        progress_calls = []
        
        def progress_callback(current, total, message):
            progress_calls.append((current, total, message))
        
        with tempfile.TemporaryDirectory() as tmpdir:
            results, zip_path = generator.generate_batch(
                recipients, 
                tmpdir,
                progress_callback=progress_callback
            )
            
            # Check progress was reported
            assert len(progress_calls) == 6  # 5 processing + 1 complete
            assert progress_calls[-1][0] == 5
            assert progress_calls[-1][1] == 5
            assert "Complete" in progress_calls[-1][2]
    
    def test_validate_template(self, mock_template_path):
        """Test template validation"""
        generator = PDFGenerator(mock_template_path)
        
        info = generator.validate_template()
        
        assert info['valid'] is True
        assert len(info['fields_found']) == 3
        assert info['page_count'] == 1
        assert info['file_size'] > 0
        assert len(info['errors']) == 0
        assert "FirstName" in info['fields_found']
        assert "LastName" in info['fields_found']
    
    @patch('fitz.open')
    def test_generate_certificate_error_handling(self, mock_fitz_open, mock_template_path):
        """Test error handling during certificate generation"""
        generator = PDFGenerator(mock_template_path)
        
        # Simulate error during generation
        mock_fitz_open.side_effect = Exception("PDF generation error")
        
        with pytest.raises(Exception) as excinfo:
            generator.generate_certificate("Test", "User")
        
        assert "PDF generation error" in str(excinfo.value)
    
    def test_field_mapping_auto_detection(self):
        """Test automatic field mapping detection"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            # Create PDF with different field names
            doc = fitz.open()
            page = doc.new_page()
            
            # Add fields with various names
            fields = [
                ("FullName", fitz.Rect(100, 100, 300, 130)),
                ("text_5plme", fitz.Rect(100, 150, 300, 180)),
                ("DateField", fitz.Rect(100, 200, 300, 230))
            ]
            
            for field_name, rect in fields:
                widget = fitz.Widget()
                widget.field_type = fitz.PDF_WIDGET_TYPE_TEXT
                widget.field_name = field_name
                widget.rect = rect
                page.add_widget(widget)
            
            doc.save(tmp.name)
            doc.close()
            
            # Test auto-detection
            generator = PDFGenerator(tmp.name)
            
            # Should auto-map FullName to both first_name and last_name 
            # (since it's the only name-related field)
            assert generator.field_mapping.get('first_name') == 'FullName'
            assert generator.field_mapping.get('last_name') == 'FullName'
            # Should auto-map DateField to date
            assert generator.field_mapping.get('date') == 'DateField'
            
            # Cleanup
            os.unlink(tmp.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])