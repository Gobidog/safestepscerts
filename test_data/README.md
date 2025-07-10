# Test Data for Certificate Generator

This directory contains various test files for testing the certificate generator application.

## CSV Files

### Basic Test Files
- **small_10_rows.csv** - Simple file with 10 recipients
- **medium_100_rows.csv** - Medium-sized file with 100 recipients  
- **large_500_rows.csv** - Large file with 500 recipients for performance testing

### Special Test Cases
- **unicode_names.csv** - International names with various character sets
- **edge_cases.csv** - Special characters, long names, security tests
- **missing_values.csv** - Files with empty cells to test validation
- **duplicates.csv** - Duplicate entries to test handling

### Invalid Files (Should Be Rejected)
- **invalid_no_names.csv** - Missing required first_name/last_name columns
- **empty_data.csv** - Only headers, no data rows
- **not_spreadsheet.txt** - Wrong file format

## Excel Files

- **simple.xlsx** - Basic Excel file with 5 rows
- **multi_sheet.xlsx** - Excel with multiple sheets (only first should be used)
- **formatted_columns.xlsx** - Excel with column names containing spaces
- **large_excel_200.xlsx** - Large Excel file with 200 rows

## Helper Files

- **courses_to_templates.csv** - Maps course names to certificate templates

## Usage

1. Use these files to test the upload functionality
2. Test both successful and error cases
3. Verify Unicode support with international names
4. Check performance with large files
5. Ensure invalid files are properly rejected

## Expected Behavior

- Valid files should process successfully
- Files with missing names should show validation errors
- Unicode names should display correctly on certificates
- Large files should show progress indicators
- Invalid file formats should be rejected at upload
