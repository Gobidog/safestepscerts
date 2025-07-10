"""
PDF Certificate Generator using PyMuPDF
Handles form field detection, text auto-sizing, and batch processing
"""

import fitz  # PyMuPDF
import os
import tempfile
import zipfile
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import logging
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import multiprocessing
from contextlib import contextmanager

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CertificateField:
    """Represents a form field in the PDF template"""
    name: str
    rect: fitz.Rect
    page_num: int
    max_font_size: float = 48.0  # Increased from 36.0 for even larger text
    min_font_size: float = 24.0  # Increased from 18.0 for better readability

@dataclass
class GenerationResult:
    """Result of certificate generation"""
    success: bool
    filename: str
    error: Optional[str] = None
    processing_time: float = 0.0


@contextmanager
def open_pdf_document(path: str, mode: str = 'rb'):
    """Context manager for safely opening and closing PDF documents"""
    doc = None
    try:
        doc = fitz.open(path)
        yield doc
    except Exception as e:
        logger.error(f"Error opening PDF document {path}: {e}")
        raise
    finally:
        if doc:
            try:
                doc.close()
            except Exception as e:
                logger.warning(f"Error closing PDF document: {e}")


@contextmanager
def temp_pdf_file(prefix: str = "cert_", suffix: str = ".pdf"):
    """Context manager for temporary PDF files"""
    temp_file = None
    temp_path = None
    try:
        temp_file = tempfile.NamedTemporaryFile(
            prefix=prefix,
            suffix=suffix,
            delete=False
        )
        temp_path = temp_file.name
        temp_file.close()
        yield temp_path
    finally:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                logger.warning(f"Error deleting temporary file {temp_path}: {e}")


class PDFGenerator:
    """Handles PDF certificate generation with form fields"""
    
    # Default form field names (can be overridden)
    FIRST_NAME_FIELD = "FirstName"
    LAST_NAME_FIELD = "LastName"
    DATE_FIELD = "Date"
    
    def __init__(self, template_path: str, field_mapping: Optional[Dict[str, str]] = None):
        """
        Initialize PDF generator with a template
        
        Args:
            template_path: Path to PDF template with form fields
            field_mapping: Optional custom field mapping {logical_name: pdf_field_name}
                          e.g. {"first_name": "FullName", "last_name": "text_5plme", "date": "Date_dm"}
        """
        self.template_path = template_path
        self.field_mapping = field_mapping or {}
        self.fields = self._detect_form_fields()
        self._analyze_field_mapping()
        
    def _detect_form_fields(self) -> Dict[str, CertificateField]:
        """Detect and catalog form fields in the template"""
        fields = {}
        
        try:
            with open_pdf_document(self.template_path) as doc:
                for page_num, page in enumerate(doc):
                    for widget in page.widgets():
                        if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                            field_name = widget.field_name
                            # Add ALL text fields, not just specific ones
                            fields[field_name] = CertificateField(
                                name=field_name,
                                rect=widget.rect,
                                page_num=page_num
                            )
                            logger.debug(f"Found field '{field_name}' on page {page_num}")
            
        except Exception as e:
            logger.error(f"Error detecting form fields: {e}")
            raise ValueError(f"Invalid template or error reading PDF: {e}")
        
        # Validate required fields are present
        # Don't enforce required fields here, let the mapping handle it
        if not fields:
            logger.warning("No form fields detected in template")
        
        return fields
    
    def _analyze_field_mapping(self):
        """Analyze and set up field mapping based on detected fields and custom mapping"""
        detected_fields = list(self.fields.keys())
        logger.info(f"Detected PDF form fields: {detected_fields}")
        
        # If no custom mapping provided, try to auto-detect common patterns
        if not self.field_mapping:
            self.field_mapping = {}
            
            # Auto-detect first name fields
            for field in detected_fields:
                field_lower = field.lower()
                if any(x in field_lower for x in ['first', 'fname', 'given', 'fullname', 'name']):
                    if 'first_name' not in self.field_mapping:
                        self.field_mapping['first_name'] = field
                        logger.info(f"Auto-mapped 'first_name' to field '{field}'")
            
            # Auto-detect last name fields
            for field in detected_fields:
                field_lower = field.lower()
                if any(x in field_lower for x in ['last', 'lname', 'surname', 'family']):
                    if 'last_name' not in self.field_mapping:
                        self.field_mapping['last_name'] = field
                        logger.info(f"Auto-mapped 'last_name' to field '{field}'")
                elif field.startswith('text_') and 'last_name' not in self.field_mapping:
                    # Handle generic field names like text_5plme
                    self.field_mapping['last_name'] = field
                    logger.info(f"Auto-mapped 'last_name' to generic field '{field}'")
            
            # Auto-detect date fields
            for field in detected_fields:
                field_lower = field.lower()
                if any(x in field_lower for x in ['date', 'day', 'time']):
                    if 'date' not in self.field_mapping:
                        self.field_mapping['date'] = field
                        logger.info(f"Auto-mapped 'date' to field '{field}'")
        
        # Validate mapping
        if 'first_name' not in self.field_mapping and 'last_name' not in self.field_mapping:
            logger.warning("No name fields mapped. Certificate generation may fail.")
        
        logger.info(f"Final field mapping: {self.field_mapping}")
    
    def _calculate_text_width(self, text: str, font_size: float, font_name: str = "Helvetica") -> float:
        """
        Calculate the width of text at given font size
        
        Args:
            text: Text to measure
            font_size: Font size in points
            font_name: Font family name
            
        Returns:
            Width in points
        """
        # PyMuPDF font width calculation
        # This is an approximation - actual width depends on the specific font
        char_width = font_size * 0.6  # Average character width ratio
        return len(text) * char_width
    
    def _adjust_font_size(self, text: str, field: CertificateField) -> float:
        """
        Calculate optimal font size for text to fit in field
        
        Args:
            text: Text to fit
            field: Field containing bounding box info
            
        Returns:
            Optimal font size
        """
        field_width = field.rect.width
        font_size = field.max_font_size
        
        # Iterate to find best fit
        while font_size >= field.min_font_size:
            text_width = self._calculate_text_width(text, font_size)
            if text_width <= field_width * 0.9:  # 90% to leave some margin
                break
            font_size -= 0.5
        
        return max(font_size, field.min_font_size)
    
    def generate_certificate(self, first_name: str, last_name: str, output_path: Optional[str] = None, additional_fields: Optional[Dict[str, str]] = None, flatten_fields: bool = True) -> str:
        """
        Generate a single certificate
        
        Args:
            first_name: Recipient's first name
            last_name: Recipient's last name
            output_path: Optional output path, generates temp file if not provided
            additional_fields: Optional additional fields to populate
            flatten_fields: Whether to flatten form fields after filling (removes blue backgrounds)
            
        Returns:
            Path to generated certificate
        """
        start_time = time.time()
        
        # Generate output filename if not provided
        if not output_path:
            safe_name = f"{first_name}_{last_name}".replace(" ", "_").replace("/", "_")
            output_path = os.path.join(tempfile.gettempdir(), f"cert_{safe_name}.pdf")
        
        try:
            doc = fitz.open(self.template_path)
            
            # Prepare field values
            field_values = {}
            
            # Map logical names to actual PDF field names
            if 'first_name' in self.field_mapping:
                field_values[self.field_mapping['first_name']] = first_name
            if 'last_name' in self.field_mapping:
                field_values[self.field_mapping['last_name']] = last_name
            
            # Add date if mapped
            if 'date' in self.field_mapping:
                today = datetime.now().strftime("%B %d, %Y")  # e.g., "July 09, 2024"
                field_values[self.field_mapping['date']] = today
            
            # Add any additional fields
            if additional_fields:
                for logical_name, value in additional_fields.items():
                    if logical_name in self.field_mapping:
                        field_values[self.field_mapping[logical_name]] = value
                    else:
                        # Try direct field name if not in mapping
                        field_values[logical_name] = value
            
            # Fill form fields and update appearance for ALL fields
            for page_num in range(len(doc)):
                page = doc[page_num]
                for widget in page.widgets():
                    if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                        field_name = widget.field_name
                        
                        # Make fields completely transparent - use empty list for no fill
                        widget.fill_color = []  # Empty list removes fill color
                        widget.border_color = []  # Empty list removes border color
                        widget.text_color = (0, 0, 0)  # Black text
                        widget.border_width = 0  # No border width
                        
                        # Check if we have a value for this field
                        text_value = field_values.get(field_name, "")
                        
                        if text_value and field_name in self.fields:
                            field_info = self.fields[field_name]
                            # Calculate optimal font size
                            font_size = self._adjust_font_size(text_value, field_info)
                            
                            # Update field value
                            widget.field_value = text_value
                            widget.text_fontsize = font_size
                            
                            # Set text alignment based on field
                            # Check if this is a first name field - right align
                            if 'first_name' in self.field_mapping and field_name == self.field_mapping['first_name']:
                                widget.text_align = fitz.TEXT_ALIGN_RIGHT
                            # Check if this is a last name field - left align (default)
                            elif 'last_name' in self.field_mapping and field_name == self.field_mapping['last_name']:
                                widget.text_align = fitz.TEXT_ALIGN_LEFT
                            
                            logger.debug(f"Updated {field_name} with '{text_value}' at size {font_size}")
                        
                        widget.update()
            
            # Flatten form fields to remove blue backgrounds completely
            if flatten_fields:
                # Convert to PDF to flatten all widgets and annotations
                pdfbytes = doc.convert_to_pdf()
                doc.close()
                
                # Open the flattened version and save it
                flattened_doc = fitz.open("pdf", pdfbytes)
                flattened_doc.save(output_path)
                flattened_doc.close()
            else:
                # Save the certificate without flattening
                doc.save(output_path)
                doc.close()
            
            processing_time = time.time() - start_time
            logger.info(f"Generated certificate for {first_name} {last_name} in {processing_time:.2f}s")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating certificate: {e}")
            raise
    
    def generate_preview(self, first_name: str = "John", last_name: str = "Doe") -> bytes:
        """
        Generate a preview certificate in memory
        
        Args:
            first_name: Sample first name
            last_name: Sample last name
            
        Returns:
            PDF content as bytes
        """
        with temp_pdf_file(prefix="preview_") as temp_path:
            self.generate_certificate(first_name, last_name, temp_path)
            with open(temp_path, 'rb') as f:
                return f.read()
    
    def generate_batch(self, recipients: List[Dict[str, str]], 
                      output_dir: str = None,
                      progress_callback: Optional[Callable] = None,
                      parallel: bool = True,
                      max_workers: Optional[int] = None) -> Tuple[List[GenerationResult], str]:
        """
        Generate certificates for multiple recipients with optional parallel processing
        
        Args:
            recipients: List of dicts with 'first_name' and 'last_name' keys
            output_dir: Directory to save certificates (temp if not provided)
            progress_callback: Optional callback function(current, total, message)
            parallel: Whether to use parallel processing (default: True)
            max_workers: Maximum number of worker threads (default: CPU count)
            
        Returns:
            Tuple of (results list, zip file path)
        """
        if not output_dir:
            output_dir = tempfile.mkdtemp()
        
        results = []
        generated_files = []
        total = len(recipients)
        
        # Thread-safe counter for progress tracking
        progress_lock = Lock()
        completed_count = 0
        
        def process_recipient(index: int, recipient: Dict[str, str]) -> Tuple[int, GenerationResult, Optional[str]]:
            """Process a single recipient and return result"""
            nonlocal completed_count
            
            try:
                first_name = recipient.get('first_name', '').strip()
                last_name = recipient.get('last_name', '').strip()
                
                if not first_name or not last_name:
                    return index, GenerationResult(
                        success=False,
                        filename="",
                        error="Missing first or last name"
                    ), None
                
                # Generate safe filename
                safe_name = f"{first_name}_{last_name}".replace(" ", "_").replace("/", "_")
                
                # Handle duplicates (thread-safe)
                with progress_lock:
                    base_path = os.path.join(output_dir, f"{safe_name}.pdf")
                    output_path = base_path
                    counter = 1
                    while os.path.exists(output_path):
                        output_path = os.path.join(output_dir, f"{safe_name}_{counter}.pdf")
                        counter += 1
                
                # Generate certificate
                start_time = time.time()
                self.generate_certificate(first_name, last_name, output_path)
                processing_time = time.time() - start_time
                
                # Update progress
                with progress_lock:
                    completed_count += 1
                    if progress_callback:
                        try:
                            progress_callback(
                                completed_count, 
                                total, 
                                f"Processed {first_name} {last_name} ({completed_count}/{total})"
                            )
                        except Exception as e:
                            # Ignore progress callback errors in threads (e.g., Streamlit NoSessionContext)
                            logger.debug(f"Progress callback error (non-critical): {e}")
                
                return index, GenerationResult(
                    success=True,
                    filename=os.path.basename(output_path),
                    processing_time=processing_time
                ), output_path
                
            except Exception as e:
                logger.error(f"Error generating certificate for {recipient}: {e}")
                
                with progress_lock:
                    completed_count += 1
                    if progress_callback:
                        try:
                            progress_callback(completed_count, total, f"Error processing certificate ({completed_count}/{total})")
                        except Exception as e:
                            # Ignore progress callback errors in threads
                            logger.debug(f"Progress callback error (non-critical): {e}")
                
                return index, GenerationResult(
                    success=False,
                    filename="",
                    error=str(e)
                ), None
        
        if parallel and len(recipients) > 1:
            # Use parallel processing for multiple recipients
            if max_workers is None:
                # Default to CPU count but cap at 8 for PDF generation
                max_workers = min(multiprocessing.cpu_count(), 8)
            
            # Create a list to store results in order
            results_dict = {}
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_index = {
                    executor.submit(process_recipient, i, recipient): i
                    for i, recipient in enumerate(recipients)
                }
                
                # Process completed tasks
                for future in as_completed(future_to_index):
                    index, result, file_path = future.result()
                    results_dict[index] = result
                    if file_path:
                        generated_files.append(file_path)
            
            # Sort results by original order
            results = [results_dict[i] for i in sorted(results_dict.keys())]
        
        else:
            # Sequential processing
            for i, recipient in enumerate(recipients):
                if progress_callback:
                    progress_callback(i, total, f"Processing {recipient.get('first_name', '')} {recipient.get('last_name', '')}...")
                
                _, result, file_path = process_recipient(i, recipient)
                results.append(result)
                if file_path:
                    generated_files.append(file_path)
        
        # Create ZIP file
        zip_path = os.path.join(output_dir, "certificates.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in generated_files:
                zipf.write(file_path, os.path.basename(file_path))
        
        if progress_callback:
            progress_callback(total, total, "Complete!")
        
        return results, zip_path
    
    def validate_template(self) -> Dict[str, any]:
        """
        Validate the template and return information about it
        
        Returns:
            Dictionary with template information
        """
        info = {
            'valid': True,
            'fields_found': list(self.fields.keys()),
            'missing_fields': [],
            'page_count': 0,
            'file_size': os.path.getsize(self.template_path),
            'errors': []
        }
        
        try:
            with open_pdf_document(self.template_path) as doc:
                info['page_count'] = len(doc)
            
            # Check for required fields using mapping
            # We need at least one name field mapped
            has_name_field = ('first_name' in self.field_mapping or 
                            'last_name' in self.field_mapping)
            
            if not has_name_field:
                info['missing_fields'].append('Name fields (first_name or last_name)')
                info['valid'] = False
                info['errors'].append('No name fields could be mapped in the template')
            
            # If we have fields but no mapping was possible
            if self.fields and not self.field_mapping:
                info['valid'] = False
                info['errors'].append('Template has fields but none could be mapped to name fields')
            
        except Exception as e:
            info['valid'] = False
            info['errors'].append(str(e))
        
        return info


def test_generator():
    """Test function for the PDF generator"""
    # This would be used with a test template
    print("PDF Generator module loaded successfully")
    print("Available classes: PDFGenerator")
    print("Required form fields: FirstName, LastName")


if __name__ == "__main__":
    test_generator()