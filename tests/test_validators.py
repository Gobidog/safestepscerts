"""
Unit tests for validators module
"""
import pytest
import pandas as pd
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import csv

from utils.validators import (
    SpreadsheetValidator,
    ValidationResult
)


class TestSpreadsheetValidator:
    """Test spreadsheet validation functionality"""
    
    @pytest.fixture
    def validator(self):
        """Create a validator instance"""
        return SpreadsheetValidator()
    
    @pytest.fixture
    def valid_csv_file(self):
        """Create a valid CSV file for testing"""
        # Create file with delete=False so we can close it properly
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8')
        try:
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Last Name', 'Email'])
            writer.writerow(['John', 'Doe', 'john@example.com'])
            writer.writerow(['Jane', 'Smith', 'jane@example.com'])
            writer.writerow(['Bob', 'Johnson', 'bob@example.com'])
            f.close()  # Close the file before yielding
            
            yield f.name
        finally:
            # Cleanup
            if os.path.exists(f.name):
                os.unlink(f.name)
    
    @pytest.fixture
    def valid_excel_file(self):
        """Create a valid Excel file for testing"""
        # Create file with delete=False so we can close it properly
        f = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        try:
            df = pd.DataFrame({
                'First Name': ['Alice', 'Bob', 'Charlie'],
                'Last Name': ['Anderson', 'Brown', 'Chen'],
                'Department': ['HR', 'IT', 'Sales']
            })
            f.close()  # Close the file handle before writing with pandas
            df.to_excel(f.name, index=False)
            
            yield f.name
        finally:
            # Cleanup
            if os.path.exists(f.name):
                os.unlink(f.name)
    
    def test_validate_file_size_valid(self, validator):
        """Test file size validation with valid size"""
        with tempfile.NamedTemporaryFile() as f:
            # Write 1MB of data
            f.write(b'x' * 1024 * 1024)
            f.flush()
            
            is_valid, error = validator.validate_file_size(f.name)
            assert is_valid is True
            assert error is None
    
    def test_validate_file_size_too_large(self, validator):
        """Test file size validation with oversized file"""
        with tempfile.NamedTemporaryFile() as f:
            # Write 6MB of data (exceeds 5MB limit)
            f.write(b'x' * 6 * 1024 * 1024)
            f.flush()
            
            is_valid, error = validator.validate_file_size(f.name)
            assert is_valid is False
            assert "exceeds maximum allowed size" in error
    
    def test_detect_encoding_utf8(self, validator):
        """Test encoding detection for UTF-8 file"""
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("Hello, 世界! Testing UTF-8 encoding.")
            f.flush()
            
            encoding = validator.detect_encoding(f.name)
            assert encoding.lower() in ['utf-8', 'ascii']  # ASCII is subset of UTF-8
            
            os.unlink(f.name)
    
    def test_find_column_exact_match(self, validator, valid_csv_file):
        """Test finding column with exact match"""
        df = pd.read_csv(valid_csv_file)
        
        # Test exact match (case-insensitive)
        assert validator.find_column(df, 'first name') == 'First Name'
        assert validator.find_column(df, 'last name') == 'Last Name'
        assert validator.find_column(df, 'email') == 'Email'
    
    def test_find_column_alternative_names(self, validator):
        """Test finding column with alternative names"""
        df = pd.DataFrame({
            'FirstName': ['John'],
            'LastName': ['Doe'],
            'Given Name': ['Jane']
        })
        
        # Should find FirstName for 'first name'
        assert validator.find_column(df, 'first name') == 'FirstName'
        
        # Should find LastName for 'last name'
        assert validator.find_column(df, 'last name') == 'LastName'
    
    def test_find_column_fuzzy_match(self, validator):
        """Test finding column with fuzzy matching (typos)"""
        df = pd.DataFrame({
            'Frist Name': ['John'],  # Typo: "Frist" instead of "First"
            'Last Nmae': ['Doe'],    # Typo: "Nmae" instead of "Name"
            'Emial': ['john@example.com']  # Typo: "Emial" instead of "Email"
        })
        
        # Should find typo columns with fuzzy matching
        assert validator.find_column(df, 'first name') == 'Frist Name'
        assert validator.find_column(df, 'last name') == 'Last Nmae'
    
    def test_find_column_no_match(self, validator):
        """Test finding column with no match"""
        df = pd.DataFrame({
            'Product': ['A'],
            'Price': [100],
            'Quantity': [5]
        })
        
        assert validator.find_column(df, 'first name') is None
        assert validator.find_column(df, 'last name') is None
    
    def test_read_spreadsheet_csv(self, validator, valid_csv_file):
        """Test reading CSV spreadsheet"""
        df, encoding, warnings = validator.read_spreadsheet(valid_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert list(df.columns) == ['First Name', 'Last Name', 'Email']
        assert len(warnings) == 0
    
    def test_read_spreadsheet_excel(self, validator, valid_excel_file):
        """Test reading Excel spreadsheet"""
        df, encoding, warnings = validator.read_spreadsheet(valid_excel_file)
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'First Name' in df.columns
        assert 'Last Name' in df.columns
        assert encoding == 'utf-8'
    
    def test_read_spreadsheet_invalid_extension(self, validator):
        """Test reading file with invalid extension"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            with pytest.raises(ValueError) as excinfo:
                validator.read_spreadsheet(f.name)
            
            assert "Unsupported file type" in str(excinfo.value)
    
    def test_clean_name_valid(self, validator):
        """Test name cleaning with valid input"""
        assert validator.clean_name("John") == "John"
        assert validator.clean_name("  Jane  ") == "Jane"
        assert validator.clean_name("Mary Ann") == "Mary Ann"
    
    def test_clean_name_multiple_spaces(self, validator):
        """Test name cleaning with multiple spaces"""
        assert validator.clean_name("John    Doe") == "John Doe"
        assert validator.clean_name("  Mary   Ann   ") == "Mary Ann"
    
    def test_clean_name_special_cases(self, validator):
        """Test name cleaning with special cases"""
        assert validator.clean_name(None) == ""
        assert validator.clean_name(pd.NA) == ""
        assert validator.clean_name(123) == "123"
        assert validator.clean_name(45.67) == "45.67"
    
    def test_handle_duplicates(self, validator):
        """Test duplicate name handling"""
        df = pd.DataFrame({
            'first_name': ['John', 'Jane', 'John', 'John'],
            'last_name': ['Doe', 'Smith', 'Doe', 'Doe']
        })
        
        result = validator.handle_duplicates(df, 'first_name', 'last_name')
        
        # First John Doe should remain unchanged
        assert result.iloc[0]['last_name'] == 'Doe'
        
        # Subsequent John Does should have numbers appended
        assert result.iloc[2]['last_name'] == 'Doe_1'
        assert result.iloc[3]['last_name'] == 'Doe_2'
        
        # Jane Smith should remain unchanged
        assert result.iloc[1]['last_name'] == 'Smith'
    
    def test_validate_spreadsheet_valid_file(self, validator, valid_csv_file):
        """Test validating a valid spreadsheet"""
        result = validator.validate_spreadsheet(valid_csv_file)
        
        assert result.valid is True
        assert result.row_count == 3
        assert len(result.errors) == 0
        assert isinstance(result.cleaned_data, pd.DataFrame)
        assert list(result.cleaned_data.columns) == ['first_name', 'last_name']
    
    def test_validate_spreadsheet_empty_file(self, validator):
        """Test validating an empty spreadsheet"""
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        try:
            # Write headers only - no data rows
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Last Name', 'Email'])
            f.close()
            
            result = validator.validate_spreadsheet(f.name)
            
            assert result.valid is False
            assert "Spreadsheet is empty" in result.errors
        finally:
            os.unlink(f.name)
    
    def test_validate_spreadsheet_missing_columns(self, validator):
        """Test validating spreadsheet with missing required columns"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['Product', 'Price', 'Quantity'])
            writer.writerow(['Widget', '10.99', '5'])
            
            f.flush()
            result = validator.validate_spreadsheet(f.name)
            
            assert result.valid is False
            assert any("Missing required columns" in error for error in result.errors)
            
            os.unlink(f.name)
    
    def test_validate_spreadsheet_too_many_rows(self, validator):
        """Test validating spreadsheet with too many rows"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Last Name'])
            
            # Write 501 rows (exceeds 500 limit)
            for i in range(501):
                writer.writerow([f'User{i}', f'Test{i}'])
            
            f.flush()
            result = validator.validate_spreadsheet(f.name)
            
            assert result.valid is False
            assert any("Too many rows" in error for error in result.errors)
            
            os.unlink(f.name)
    
    def test_validate_spreadsheet_with_empty_names(self, validator):
        """Test validating spreadsheet with empty names"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Last Name'])
            writer.writerow(['John', 'Doe'])
            writer.writerow(['', 'Smith'])  # Empty first name
            writer.writerow(['Bob', ''])     # Empty last name
            writer.writerow(['Alice', 'Anderson'])
            
            f.flush()
            result = validator.validate_spreadsheet(f.name)
            
            assert result.valid is True
            assert result.row_count == 2  # Only valid rows
            assert any("2 rows with missing names" in warning for warning in result.warnings)
            
            os.unlink(f.name)
    
    def test_validate_spreadsheet_unicode_names(self, validator):
        """Test validating spreadsheet with unicode names"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['First Name', 'Last Name'])
            writer.writerow(['José', 'García'])
            writer.writerow(['李', '明'])
            writer.writerow(['Müller', 'François'])
            
            f.flush()
            result = validator.validate_spreadsheet(f.name)
            
            assert result.valid is True
            assert result.row_count == 3
            assert result.cleaned_data.iloc[0]['first_name'] == 'José'
            assert result.cleaned_data.iloc[1]['first_name'] == '李'
            
            os.unlink(f.name)
    
    def test_validate_character_encoding(self, validator):
        """Test character encoding validation"""
        assert validator.validate_character_encoding("Hello World") is True
        assert validator.validate_character_encoding("José García") is True
        assert validator.validate_character_encoding("你好世界") is True
        assert validator.validate_character_encoding("🎉 Emoji") is True
    
    def test_get_validation_summary_success(self, validator):
        """Test getting validation summary for successful validation"""
        result = ValidationResult(
            valid=True,
            row_count=10,
            cleaned_data=pd.DataFrame({
                'first_name': ['John', 'Jane'],
                'last_name': ['Doe', 'Smith']
            })
        )
        
        summary = validator.get_validation_summary(result)
        
        assert "✅ Validation successful!" in summary
        assert "Found 10 valid recipients" in summary
        assert "Data Preview:" in summary
    
    def test_get_validation_summary_failure(self, validator):
        """Test getting validation summary for failed validation"""
        result = ValidationResult(
            valid=False,
            errors=["Missing required columns", "File too large"],
            warnings=["Some rows have missing data"]
        )
        
        summary = validator.get_validation_summary(result)
        
        assert "❌ Validation failed!" in summary
        assert "Missing required columns" in summary
        assert "File too large" in summary
        assert "Some rows have missing data" in summary
    
    def test_column_mappings(self, validator):
        """Test column mapping configurations"""
        # Check that common variations are mapped
        assert 'firstname' in validator.column_mappings['first name']
        assert 'first_name' in validator.column_mappings['first name']
        assert 'given name' in validator.column_mappings['first name']
        
        assert 'lastname' in validator.column_mappings['last name']
        assert 'surname' in validator.column_mappings['last name']
        assert 'family name' in validator.column_mappings['last name']
    
    def test_validation_result_defaults(self):
        """Test ValidationResult dataclass defaults"""
        result = ValidationResult(valid=True)
        
        assert result.valid is True
        assert result.row_count == 0
        assert result.errors == []
        assert result.warnings == []
        assert result.cleaned_data is None
        assert result.encoding == 'utf-8'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])