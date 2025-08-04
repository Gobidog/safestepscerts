"""
Certificate Generation Utilities for SafeSteps
Enhanced certificate generation with modern UI integration
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from datetime import datetime
import io
import json
from pathlib import Path

# Import existing SafeSteps modules
try:
    from utils.pdf_generator import PDFGenerator
    from utils.storage import StorageManager
    from utils.course_manager import CourseManager
    from utils.validators import validate_certificate_data
except ImportError as e:
    st.error(f"Import error in certificate_generation: {e}")

class CertificateGenerator:
    """Enhanced certificate generator with UI integration"""
    
    def __init__(self):
        self.pdf_generator = PDFGenerator()
        self.storage = StorageManager()
        self.course_manager = CourseManager()
        
    def generate_single_certificate(self, student_data: Dict[str, Any]) -> Tuple[bool, str, Optional[bytes]]:
        """
        Generate a single certificate
        
        Args:
            student_data: Dictionary containing student information
                Required keys: name, course
                Optional keys: date, instructor, grade
        
        Returns:
            Tuple of (success, message, pdf_bytes)
        """
        try:
            # Validate input data
            validation_result = validate_certificate_data(student_data)
            if not validation_result['valid']:
                return False, f"Validation error: {validation_result['message']}", None
            
            # Add default values
            certificate_data = self._prepare_certificate_data(student_data)
            
            # Generate PDF
            pdf_bytes = self.pdf_generator.create_certificate(certificate_data)
            
            if pdf_bytes:
                # Store certificate record
                self._store_certificate_record(certificate_data)
                return True, "Certificate generated successfully", pdf_bytes
            else:
                return False, "Failed to generate PDF", None
                
        except Exception as e:
            return False, f"Error generating certificate: {str(e)}", None
    
    def generate_batch_certificates(self, students_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate certificates for multiple students
        
        Args:
            students_df: DataFrame with student data
        
        Returns:
            Dictionary with generation results
        """
        results = {
            'total': len(students_df),
            'successful': 0,
            'failed': 0,
            'certificates': [],
            'errors': []
        }
        
        try:
            for index, row in students_df.iterrows():
                student_data = row.to_dict()
                success, message, pdf_bytes = self.generate_single_certificate(student_data)
                
                if success:
                    results['successful'] += 1
                    results['certificates'].append({
                        'name': student_data.get('name', ''),
                        'course': student_data.get('course', ''),
                        'pdf_bytes': pdf_bytes,
                        'filename': self._generate_filename(student_data)
                    })
                else:
                    results['failed'] += 1
                    results['errors'].append({
                        'row': index + 1,
                        'name': student_data.get('name', 'Unknown'),
                        'error': message
                    })
            
            return results
            
        except Exception as e:
            results['errors'].append({
                'general_error': f"Batch processing error: {str(e)}"
            })
            return results
    
    def _prepare_certificate_data(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare certificate data with defaults"""
        prepared_data = student_data.copy()
        
        # Add defaults
        if 'date' not in prepared_data or not prepared_data['date']:
            prepared_data['date'] = datetime.now().strftime('%B %d, %Y')
        
        if 'instructor' not in prepared_data or not prepared_data['instructor']:
            prepared_data['instructor'] = 'SafeSteps Administrator'
        
        if 'grade' not in prepared_data or not prepared_data['grade']:
            prepared_data['grade'] = 'Pass'
        
        return prepared_data
    
    def _generate_filename(self, student_data: Dict[str, Any]) -> str:
        """Generate filename for certificate"""
        name = student_data.get('name', 'Unknown').replace(' ', '_')
        course = student_data.get('course', 'Course').replace(' ', '_')
        timestamp = datetime.now().strftime('%Y%m%d')
        
        return f"Certificate_{name}_{course}_{timestamp}.pdf"
    
    def _store_certificate_record(self, certificate_data: Dict[str, Any]) -> None:
        """Store certificate generation record"""
        try:
            record = {
                'name': certificate_data.get('name'),
                'course': certificate_data.get('course'),
                'date_generated': datetime.now().isoformat(),
                'instructor': certificate_data.get('instructor'),
                'grade': certificate_data.get('grade')
            }
            
            # Store using existing storage system
            self.storage.store_certificate_record(record)
            
        except Exception as e:
            st.warning(f"Could not store certificate record: {e}")
    
    def get_available_courses(self) -> List[str]:
        """Get list of available courses"""
        try:
            return self.course_manager.get_course_list()
        except Exception:
            # Fallback to default courses
            return [
                "Safety Training 101",
                "Advanced Safety Procedures",
                "Emergency Response Training",
                "Workplace Safety Fundamentals",
                "Risk Assessment and Management"
            ]
    
    def get_certificate_templates(self) -> List[str]:
        """Get available certificate templates"""
        try:
            # This would interface with template management
            return [
                "Standard Certificate",
                "Professional Certificate", 
                "Achievement Certificate",
                "Completion Certificate"
            ]
        except Exception:
            return ["Standard Certificate"]

class CertificateUI:
    """UI components for certificate generation"""
    
    def __init__(self, generator: CertificateGenerator):
        self.generator = generator
    
    def render_single_certificate_form(self) -> Optional[Dict[str, Any]]:
        """Render form for single certificate generation"""
        st.subheader("🎓 Generate Single Certificate")
        
        with st.form("single_certificate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Student Name*", placeholder="Enter full name")
                course = st.selectbox("Course*", options=self.generator.get_available_courses())
                
            with col2:
                date = st.date_input("Completion Date", value=datetime.now())
                instructor = st.text_input("Instructor", placeholder="Optional")
                
            grade = st.selectbox("Grade", options=["Pass", "Distinction", "Merit", "Credit"])
            
            submitted = st.form_submit_button("🚀 Generate Certificate", use_container_width=True)
            
            if submitted:
                if not name or not course:
                    st.error("Please fill in all required fields (marked with *)")
                    return None
                
                return {
                    'name': name,
                    'course': course,
                    'date': date.strftime('%B %d, %Y'),
                    'instructor': instructor,
                    'grade': grade
                }
        
        return None
    
    def render_batch_certificate_form(self) -> Optional[pd.DataFrame]:
        """Render form for batch certificate generation"""
        st.subheader("📚 Batch Certificate Generation")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="File should contain columns: name, course (required), date, instructor, grade (optional)"
        )
        
        if uploaded_file:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                # Display preview
                st.write("📋 **File Preview:**")
                st.dataframe(df.head(), use_container_width=True)
                
                # Validate columns
                required_columns = ['name', 'course']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                    return None
                
                st.success(f"✅ File validated. Found {len(df)} records.")
                
                if st.button("🚀 Generate All Certificates", use_container_width=True):
                    return df
                    
            except Exception as e:
                st.error(f"Error reading file: {e}")
        
        return None
    
    def display_generation_results(self, results: Dict[str, Any]) -> None:
        """Display batch generation results"""
        st.subheader("📊 Generation Results")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Processed", results['total'])
        
        with col2:
            st.metric("Successful", results['successful'], 
                     delta=f"{(results['successful']/results['total']*100):.1f}%" if results['total'] > 0 else "0%")
        
        with col3:
            st.metric("Failed", results['failed'])
        
        # Download successful certificates
        if results['certificates']:
            st.success(f"✅ {results['successful']} certificates generated successfully!")
            
            # Create download links for each certificate
            st.write("📥 **Download Certificates:**")
            for cert in results['certificates']:
                st.download_button(
                    label=f"Download - {cert['name']}",
                    data=cert['pdf_bytes'],
                    file_name=cert['filename'],
                    mime="application/pdf"
                )
        
        # Show errors if any
        if results['errors']:
            st.error(f"❌ {results['failed']} certificates failed to generate:")
            for error in results['errors']:
                if 'general_error' in error:
                    st.write(f"• {error['general_error']}")
                else:
                    st.write(f"• Row {error['row']} - {error['name']}: {error['error']}")

# Convenience functions for easy integration
def create_certificate_generator() -> CertificateGenerator:
    """Create certificate generator instance"""
    return CertificateGenerator()

def create_certificate_ui(generator: CertificateGenerator = None) -> CertificateUI:
    """Create certificate UI instance"""
    if generator is None:
        generator = create_certificate_generator()
    return CertificateUI(generator)