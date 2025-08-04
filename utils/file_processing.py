"""
File Processing Utilities for SafeSteps
Handles CSV validation, file uploads, and data processing
"""

import pandas as pd
import io
import csv
from typing import Dict, List, Optional, Tuple, Any
import re
from pathlib import Path

class SpreadsheetValidator:
    """Validates uploaded spreadsheet files for certificate generation"""
    
    def __init__(self):
        self.required_columns = ['name', 'course']  # Minimum required columns
        self.optional_columns = ['email', 'date', 'grade', 'instructor']
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        
    def validate_file(self, uploaded_file) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Validate uploaded file and return validation result
        
        Returns:
            Tuple of (is_valid, message, dataframe)
        """
        try:
            # Check file size
            if uploaded_file.size > self.max_file_size:
                return False, "File size exceeds 10MB limit", None
            
            # Check file extension
            if not uploaded_file.name.lower().endswith(('.csv', '.xlsx', '.xls')):
                return False, "File must be CSV or Excel format", None
            
            # Read file into DataFrame
            try:
                if uploaded_file.name.lower().endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
            except Exception as e:
                return False, f"Error reading file: {str(e)}", None
            
            # Check if DataFrame is empty
            if df.empty:
                return False, "File appears to be empty", None
            
            # Validate required columns
            df_columns = [col.lower().strip() for col in df.columns]
            missing_columns = []
            
            for req_col in self.required_columns:
                if req_col not in df_columns:
                    missing_columns.append(req_col)
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None
            
            # Validate data quality
            validation_issues = self._validate_data_quality(df)
            if validation_issues:
                return False, f"Data quality issues: {'; '.join(validation_issues)}", None
            
            # Clean and standardize the data
            cleaned_df = self._clean_dataframe(df)
            
            return True, f"File validated successfully. Found {len(cleaned_df)} records.", cleaned_df
            
        except Exception as e:
            return False, f"Unexpected error during validation: {str(e)}", None
    
    def _validate_data_quality(self, df: pd.DataFrame) -> List[str]:
        """Validate data quality and return list of issues"""
        issues = []
        
        # Check for empty names
        name_col = self._find_column(df, 'name')
        if name_col and df[name_col].isna().sum() > 0:
            issues.append(f"{df[name_col].isna().sum()} records have missing names")
        
        # Check for empty courses
        course_col = self._find_column(df, 'course')
        if course_col and df[course_col].isna().sum() > 0:
            issues.append(f"{df[course_col].isna().sum()} records have missing courses")
        
        # Check for invalid email formats (if email column exists)
        email_col = self._find_column(df, 'email')
        if email_col:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            invalid_emails = df[email_col].notna() & ~df[email_col].str.match(email_pattern, na=False)
            if invalid_emails.sum() > 0:
                issues.append(f"{invalid_emails.sum()} records have invalid email formats")
        
        return issues
    
    def _find_column(self, df: pd.DataFrame, target_col: str) -> Optional[str]:
        """Find column name that matches target (case-insensitive)"""
        for col in df.columns:
            if col.lower().strip() == target_col.lower():
                return col
        return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the dataframe"""
        # Create a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Standardize column names
        cleaned_df.columns = [col.lower().strip() for col in cleaned_df.columns]
        
        # Remove completely empty rows
        cleaned_df = cleaned_df.dropna(how='all')
        
        # Clean string columns
        string_columns = cleaned_df.select_dtypes(include=['object']).columns
        for col in string_columns:
            cleaned_df[col] = cleaned_df[col].astype(str).str.strip()
            # Replace 'nan' strings with actual NaN
            cleaned_df[col] = cleaned_df[col].replace('nan', pd.NA)
        
        return cleaned_df
    
    def generate_template(self) -> pd.DataFrame:
        """Generate a template DataFrame for download"""
        template_data = {
            'name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
            'course': ['Safety Training 101', 'Advanced Safety', 'Emergency Response'],
            'email': ['john@example.com', 'jane@example.com', 'bob@example.com'],
            'date': ['2024-01-15', '2024-01-16', '2024-01-17'],
            'grade': ['Pass', 'Pass', 'Distinction'],
            'instructor': ['Sarah Wilson', 'Mike Brown', 'Lisa Davis']
        }
        
        return pd.DataFrame(template_data)

class FileProcessor:
    """General file processing utilities"""
    
    @staticmethod
    def convert_to_csv_string(df: pd.DataFrame) -> str:
        """Convert DataFrame to CSV string"""
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        # Remove special characters and spaces
        sanitized = re.sub(r'[^\w\-_\.]', '_', filename)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Limit length
        if len(sanitized) > 100:
            name, ext = Path(sanitized).stem, Path(sanitized).suffix
            sanitized = name[:95-len(ext)] + ext
        
        return sanitized
    
    @staticmethod
    def get_file_info(uploaded_file) -> Dict[str, Any]:
        """Get detailed information about uploaded file"""
        return {
            'name': uploaded_file.name,
            'size_bytes': uploaded_file.size,
            'size_mb': round(uploaded_file.size / (1024 * 1024), 2),
            'type': uploaded_file.type if hasattr(uploaded_file, 'type') else 'unknown'
        }

# Convenience functions for common use cases
def validate_certificate_csv(uploaded_file) -> Tuple[bool, str, Optional[pd.DataFrame]]:
    """Quick validation function for certificate CSV files"""
    validator = SpreadsheetValidator()
    return validator.validate_file(uploaded_file)

def create_template_csv() -> str:
    """Create a template CSV string for download"""
    validator = SpreadsheetValidator()
    template_df = validator.generate_template()
    return FileProcessor.convert_to_csv_string(template_df)