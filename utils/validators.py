"""
Validators for spreadsheet and file validation
Handles CSV/XLSX validation, duplicate detection, and data cleaning
"""

import pandas as pd
import os
import re
import chardet
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import logging
from difflib import SequenceMatcher

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of file validation"""
    valid: bool
    row_count: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    cleaned_data: pd.DataFrame = None
    encoding: str = 'utf-8'
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class SpreadsheetValidator:
    """Validates and cleans spreadsheet data for certificate generation"""
    
    # Required column names (case-insensitive)
    REQUIRED_COLUMNS = ['first name', 'last name']
    
    # File constraints
    MAX_FILE_SIZE_MB = 5
    MAX_ROWS = 500
    MIN_ROWS = 1
    
    # Supported file types
    ALLOWED_EXTENSIONS = ['.csv', '.xlsx', '.xls']
    
    def __init__(self):
        """Initialize the validator"""
        self.column_mappings = {
            'first name': ['first name', 'firstname', 'first_name', 'fname', 'given name', 'given_name'],
            'last name': ['last name', 'lastname', 'last_name', 'lname', 'surname', 'family name', 'family_name']
        }
    
    def validate_file_size(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate file size
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            if size_mb > self.MAX_FILE_SIZE_MB:
                return False, f"File size ({size_mb:.1f}MB) exceeds maximum allowed size ({self.MAX_FILE_SIZE_MB}MB)"
            return True, None
        except Exception as e:
            return False, f"Error checking file size: {str(e)}"
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding for proper Unicode handling
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding string
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                confidence = result['confidence']
                
                logger.debug(f"Detected encoding: {encoding} (confidence: {confidence})")
                
                # Default to utf-8 if detection fails or confidence is low
                if not encoding or confidence < 0.7:
                    return 'utf-8'
                
                return encoding
        except Exception as e:
            logger.warning(f"Error detecting encoding: {e}. Using UTF-8.")
            return 'utf-8'
    
    def find_column(self, df: pd.DataFrame, target_column: str) -> Optional[str]:
        """
        Find a column in the dataframe using fuzzy matching
        
        Args:
            df: DataFrame to search
            target_column: Target column name (lowercase)
            
        Returns:
            Actual column name if found, None otherwise
        """
        # Get lowercase column names
        columns_lower = {col.lower().strip(): col for col in df.columns}
        
        # Check direct match first
        if target_column in columns_lower:
            return columns_lower[target_column]
        
        # Check alternative names
        if target_column in self.column_mappings:
            for alt_name in self.column_mappings[target_column]:
                if alt_name in columns_lower:
                    return columns_lower[alt_name]
        
        # Fuzzy matching for typos (e.g., "frist name" -> "first name")
        best_match = None
        best_ratio = 0.0
        threshold = 0.8  # 80% similarity threshold
        
        for col_lower, col_original in columns_lower.items():
            # Check against target
            ratio = SequenceMatcher(None, target_column, col_lower).ratio()
            if ratio > best_ratio and ratio >= threshold:
                best_ratio = ratio
                best_match = col_original
            
            # Check against known alternatives
            if target_column in self.column_mappings:
                for alt_name in self.column_mappings[target_column]:
                    ratio = SequenceMatcher(None, alt_name, col_lower).ratio()
                    if ratio > best_ratio and ratio >= threshold:
                        best_ratio = ratio
                        best_match = col_original
        
        if best_match:
            logger.info(f"Fuzzy matched '{best_match}' for '{target_column}' (similarity: {best_ratio:.2%})")
        
        return best_match
    
    def read_spreadsheet(self, file_path: str) -> Tuple[pd.DataFrame, str, List[str]]:
        """
        Read spreadsheet file with proper encoding
        
        Args:
            file_path: Path to the spreadsheet
            
        Returns:
            Tuple of (dataframe, encoding, warnings)
        """
        warnings = []
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {ext}. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}")
        
        try:
            if ext == '.csv':
                # Detect encoding for CSV files
                encoding = self.detect_encoding(file_path)
                
                # Try to read with detected encoding
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                except UnicodeDecodeError:
                    # Fallback to UTF-8 with error handling
                    warnings.append(f"Encoding issue detected. Some characters may not display correctly.")
                    df = pd.read_csv(file_path, encoding='utf-8', errors='replace')
                    encoding = 'utf-8'
            else:
                # Excel files
                df = pd.read_excel(file_path)
                encoding = 'utf-8'  # Excel handles encoding internally
            
            return df, encoding, warnings
            
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")
    
    def clean_name(self, name: any) -> str:
        """
        Clean and standardize a name value
        
        Args:
            name: Name value (could be string, float, etc.)
            
        Returns:
            Cleaned name string
        """
        if pd.isna(name):
            return ""
        
        # Convert to string and strip whitespace
        name_str = str(name).strip()
        
        # Remove multiple spaces
        name_str = re.sub(r'\s+', ' ', name_str)
        
        # Remove non-printable characters
        name_str = ''.join(char for char in name_str if char.isprintable())
        
        return name_str
    
    def handle_duplicates(self, df: pd.DataFrame, first_col: str, last_col: str) -> pd.DataFrame:
        """
        Handle duplicate names by appending numbers
        
        Args:
            df: DataFrame with names
            first_col: First name column name
            last_col: Last name column name
            
        Returns:
            DataFrame with duplicates handled
        """
        # Create a combined name column for duplicate detection
        df['_full_name'] = df[first_col].astype(str) + '_' + df[last_col].astype(str)
        
        # Find duplicates
        duplicates = df[df.duplicated('_full_name', keep=False)]
        
        if len(duplicates) > 0:
            # Group by full name and add counter
            for name, group in df.groupby('_full_name'):
                if len(group) > 1:
                    for i, idx in enumerate(group.index):
                        if i > 0:  # Keep first occurrence as-is
                            df.at[idx, last_col] = f"{df.at[idx, last_col]}_{i}"
        
        # Remove temporary column
        df.drop('_full_name', axis=1, inplace=True)
        
        return df
    
    def validate_spreadsheet(self, file_path: str) -> ValidationResult:
        """
        Validate a spreadsheet file for certificate generation
        
        Args:
            file_path: Path to the spreadsheet file
            
        Returns:
            ValidationResult with validation status and cleaned data
        """
        result = ValidationResult(valid=True)
        
        # Check file size
        size_valid, size_error = self.validate_file_size(file_path)
        if not size_valid:
            result.valid = False
            result.errors.append(size_error)
            return result
        
        try:
            # Read the file
            df, encoding, read_warnings = self.read_spreadsheet(file_path)
            result.encoding = encoding
            result.warnings.extend(read_warnings)
            
            # Check if empty
            if df.empty:
                result.valid = False
                result.errors.append("Spreadsheet is empty")
                return result
            
            # Check row count
            result.row_count = len(df)
            if result.row_count > self.MAX_ROWS:
                result.valid = False
                result.errors.append(f"Too many rows ({result.row_count}). Maximum allowed: {self.MAX_ROWS}")
                return result
            
            if result.row_count < self.MIN_ROWS:
                result.valid = False
                result.errors.append("Spreadsheet must contain at least one data row")
                return result
            
            # Find required columns
            first_name_col = self.find_column(df, 'first name')
            last_name_col = self.find_column(df, 'last name')
            
            missing_columns = []
            if not first_name_col:
                missing_columns.append('First Name')
            if not last_name_col:
                missing_columns.append('Last Name')
            
            if missing_columns:
                result.valid = False
                result.errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                result.errors.append(f"Found columns: {', '.join(df.columns)}")
                return result
            
            # Create cleaned dataframe with standardized column names
            cleaned_df = pd.DataFrame()
            cleaned_df['first_name'] = df[first_name_col].apply(self.clean_name)
            cleaned_df['last_name'] = df[last_name_col].apply(self.clean_name)
            
            # Check for empty names
            empty_first = cleaned_df['first_name'] == ''
            empty_last = cleaned_df['last_name'] == ''
            empty_rows = empty_first | empty_last
            
            if empty_rows.any():
                empty_count = empty_rows.sum()
                result.warnings.append(f"Found {empty_count} rows with missing names. These will be skipped.")
                # Remove empty rows
                cleaned_df = cleaned_df[~empty_rows].reset_index(drop=True)
                result.row_count = len(cleaned_df)
            
            # Handle duplicates
            original_count = len(cleaned_df)
            cleaned_df = self.handle_duplicates(cleaned_df, 'first_name', 'last_name')
            
            dup_count = len(cleaned_df[cleaned_df['last_name'].str.contains('_\d+$', regex=True)])
            if dup_count > 0:
                result.warnings.append(f"Found {dup_count} duplicate names. Numbers appended to last names.")
            
            # Final validation
            if len(cleaned_df) == 0:
                result.valid = False
                result.errors.append("No valid names found in spreadsheet")
                return result
            
            result.cleaned_data = cleaned_df
            result.row_count = len(cleaned_df)
            
            # Add summary info
            if result.valid:
                result.warnings.insert(0, f"Successfully validated {result.row_count} recipients")
            
        except Exception as e:
            result.valid = False
            result.errors.append(f"Error processing file: {str(e)}")
        
        return result
    
    def validate_file(self, uploaded_file) -> ValidationResult:
        """
        Validate uploaded file for certificate generation
        Wrapper method that handles Streamlit UploadedFile objects
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            ValidationResult with validation status and cleaned data
        """
        import tempfile
        
        # Create temporary directory if it doesn't exist
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # Save uploaded file temporarily
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        
        try:
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Use existing validate_spreadsheet method
            result = self.validate_spreadsheet(temp_path)
            
            return result
            
        except Exception as e:
            # Return error result if file handling fails
            result = ValidationResult(valid=False)
            result.errors.append(f"Error processing uploaded file: {str(e)}")
            return result
            
        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as cleanup_error:
                logger.warning(f"Could not clean up temp file {temp_path}: {cleanup_error}")
    
    def validate_character_encoding(self, text: str) -> bool:
        """
        Validate that text contains only valid Unicode characters
        
        Args:
            text: Text to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to encode/decode to catch any issues
            text.encode('utf-8').decode('utf-8')
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False
    
    def get_validation_summary(self, result: ValidationResult) -> str:
        """
        Get a human-readable summary of validation results
        
        Args:
            result: ValidationResult object
            
        Returns:
            Summary string
        """
        lines = []
        
        if result.valid:
            lines.append(f"✅ Validation successful!")
            lines.append(f"📊 Found {result.row_count} valid recipients")
        else:
            lines.append("❌ Validation failed!")
        
        if result.errors:
            lines.append("\n**Errors:**")
            for error in result.errors:
                lines.append(f"  • {error}")
        
        if result.warnings:
            lines.append("\n**Warnings:**")
            for warning in result.warnings:
                lines.append(f"  • {warning}")
        
        if result.valid and result.cleaned_data is not None:
            lines.append("\n**Data Preview:**")
            preview_df = result.cleaned_data.head(5)
            lines.append(preview_df.to_string(index=False))
            
            if result.row_count > 5:
                lines.append(f"  ... and {result.row_count - 5} more rows")
        
        return "\n".join(lines)


def test_validators():
    """Test function for validators module"""
    print("Validators module loaded successfully")
    print("Available classes: SpreadsheetValidator")
    print("Max file size: 5MB")
    print("Max rows: 500")
    print("Supported formats: CSV, XLSX, XLS")


if __name__ == "__main__":
    test_validators()