# API Reference - SafeSteps Certificate Generator

## Overview

This document provides a comprehensive API reference for all utility modules in the SafeSteps Certificate Generator application.

---

## Table of Contents

1. [Authentication Module (`utils/auth.py`)](#authentication-module)
2. [PDF Generator Module (`utils/pdf_generator.py`)](#pdf-generator-module)
3. [Validators Module (`utils/validators.py`)](#validators-module)
4. [Storage Module (`utils/storage.py`)](#storage-module)

---

## Authentication Module

**Module**: `utils.auth`  
**Description**: Handles authentication, session management, CSRF protection, and rate limiting.

### Classes

#### `RateLimiter`
Rate limiter implementation for API endpoints.

**Constructor Parameters:**
- `max_requests` (int, default=40): Maximum requests allowed in window
- `window_seconds` (int, default=60): Time window in seconds

**Methods:**

##### `is_allowed(key: str) -> Tuple[bool, Optional[int]]`
Check if request is allowed under rate limit.

**Parameters:**
- `key` (str): Unique identifier for rate limiting (e.g., session ID)

**Returns:**
- `Tuple[bool, Optional[int]]`: (allowed, seconds_until_reset)

##### `reset(key: str) -> None`
Reset rate limit for a specific key.

### Functions

#### `hash_password(password: str) -> str`
Hash a password using bcrypt.

**Parameters:**
- `password` (str): Plain text password

**Returns:**
- `str`: Bcrypt hashed password

#### `validate_password(password: str, role: str = "user") -> bool`
Validate password for given role.

**Parameters:**
- `password` (str): Plain text password to validate
- `role` (str): Role to validate against ("user" or "admin")

**Returns:**
- `bool`: True if password is valid

#### `check_password_strength(password: str) -> Tuple[bool, str]`
Check if password meets strength requirements.

**Parameters:**
- `password` (str): Password to check

**Returns:**
- `Tuple[bool, str]`: (is_strong, error_message)

**Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

#### `generate_csrf_token() -> str`
Generate a CSRF token using JWT.

**Returns:**
- `str`: JWT-encoded CSRF token

#### `validate_csrf_token(token: str) -> bool`
Validate a CSRF token.

**Parameters:**
- `token` (str): CSRF token to validate

**Returns:**
- `bool`: True if token is valid and not expired

#### `csrf_protected(func: Callable) -> Callable`
Decorator to protect forms with CSRF validation.

**Usage:**
```python
@csrf_protected
def handle_form_submission():
    # Form handling code
```

#### `require_auth(role: str = "user") -> Callable`
Decorator to require authentication for a function.

**Parameters:**
- `role` (str): Required role ("user" or "admin")

**Usage:**
```python
@require_auth(role="admin")
def admin_function():
    # Admin-only code
```

#### `check_session_timeout() -> bool`
Check if current session has timed out.

**Returns:**
- `bool`: True if session is still valid

#### `update_session_activity() -> None`
Update the last activity time for the current session.

---

## PDF Generator Module

**Module**: `utils.pdf_generator`  
**Description**: Handles PDF certificate generation with parallel processing support.

### Classes

#### `PDFGenerator`
Main class for generating PDF certificates.

**Constructor Parameters:**
- `template_path` (str): Path to PDF template file
- `field_mapping` (Optional[Dict[str, str]]): Custom field mappings

**Methods:**

##### `validate_template() -> bool`
Validate that the PDF template has required form fields.

**Returns:**
- `bool`: True if template is valid

##### `get_form_fields() -> List[str]`
Get list of all form fields in the PDF template.

**Returns:**
- `List[str]`: List of field names

##### `fill_certificate(data: Dict[str, Any], output_path: str) -> bool`
Fill a single certificate with data.

**Parameters:**
- `data` (Dict[str, Any]): Data to fill in certificate
- `output_path` (str): Path to save filled certificate

**Returns:**
- `bool`: True if successful

##### `generate_bulk_certificates(df: pd.DataFrame, output_dir: str, max_workers: Optional[int] = None, progress_callback: Optional[Callable] = None) -> Tuple[List[str], List[str]]`
Generate multiple certificates in parallel.

**Parameters:**
- `df` (pd.DataFrame): DataFrame with certificate data
- `output_dir` (str): Directory to save certificates
- `max_workers` (Optional[int]): Number of parallel workers
- `progress_callback` (Optional[Callable]): Progress update callback

**Returns:**
- `Tuple[List[str], List[str]]`: (successful_paths, failed_names)

### Context Managers

#### `open_pdf_document(path: str, mode: str = 'rb')`
Context manager for safely opening PDF documents.

**Parameters:**
- `path` (str): Path to PDF file
- `mode` (str): File open mode

#### `temp_pdf_file(prefix: str = "cert_", suffix: str = ".pdf")`
Context manager for temporary PDF files.

**Parameters:**
- `prefix` (str): Prefix for temp file name
- `suffix` (str): Suffix for temp file name

### Utility Functions

#### `create_zip_archive(file_paths: List[str], zip_path: str) -> bool`
Create a ZIP archive from list of files.

**Parameters:**
- `file_paths` (List[str]): List of file paths to archive
- `zip_path` (str): Output ZIP file path

**Returns:**
- `bool`: True if successful

---

## Validators Module

**Module**: `utils.validators`  
**Description**: Handles input validation and data processing.

### Functions

#### `validate_spreadsheet(file) -> Tuple[bool, str, Optional[pd.DataFrame]]`
Validate uploaded spreadsheet file.

**Parameters:**
- `file`: Streamlit UploadedFile object

**Returns:**
- `Tuple[bool, str, Optional[pd.DataFrame]]`: (is_valid, message, dataframe)

**Validation Checks:**
- File size (max 5MB)
- File extension (xlsx, xls, csv)
- Content validation
- Required columns presence

#### `validate_data_columns(df: pd.DataFrame) -> Tuple[bool, str, Dict[str, str]]`
Validate DataFrame columns with fuzzy matching.

**Parameters:**
- `df` (pd.DataFrame): DataFrame to validate

**Returns:**
- `Tuple[bool, str, Dict[str, str]]`: (is_valid, message, column_mapping)

**Features:**
- Fuzzy matching with 80% similarity threshold
- Handles common typos (e.g., "Frist Name" → "First Name")
- Case-insensitive matching

#### `get_unique_filename(directory: str, base_name: str, extension: str) -> str`
Generate unique filename to avoid overwrites.

**Parameters:**
- `directory` (str): Target directory
- `base_name` (str): Base filename
- `extension` (str): File extension

**Returns:**
- `str`: Unique filename

#### `detect_encoding(file_bytes: bytes, sample_size: int = 10240) -> str`
Detect file encoding using chardet.

**Parameters:**
- `file_bytes` (bytes): File content
- `sample_size` (int): Bytes to sample for detection

**Returns:**
- `str`: Detected encoding (defaults to 'utf-8')

#### `sanitize_dataframe(df: pd.DataFrame) -> pd.DataFrame`
Clean and sanitize DataFrame values.

**Parameters:**
- `df` (pd.DataFrame): DataFrame to sanitize

**Returns:**
- `pd.DataFrame`: Sanitized DataFrame

**Operations:**
- Strips whitespace
- Removes special characters
- Handles Unicode normalization

---

## Storage Module

**Module**: `utils.storage`  
**Description**: Handles file storage with Google Cloud Storage and local fallback.

### Classes

#### `Storage`
Unified storage interface with GCS and local file system support.

**Methods:**

##### `upload_template(file_path: str, template_name: str) -> bool`
Upload a template file to storage.

**Parameters:**
- `file_path` (str): Local path to template file
- `template_name` (str): Name for stored template

**Returns:**
- `bool`: True if successful

##### `download_template(template_name: str, local_path: str) -> bool`
Download a template from storage.

**Parameters:**
- `template_name` (str): Name of template to download
- `local_path` (str): Local path to save template

**Returns:**
- `bool`: True if successful

##### `delete_template(template_name: str) -> bool`
Delete a template from storage.

**Parameters:**
- `template_name` (str): Name of template to delete

**Returns:**
- `bool`: True if successful

##### `list_templates() -> List[str]`
List all available templates.

**Returns:**
- `List[str]`: List of template names

##### `template_exists(template_name: str) -> bool`
Check if a template exists.

**Parameters:**
- `template_name` (str): Name of template to check

**Returns:**
- `bool`: True if template exists

##### `get_template_path(template_name: str) -> Optional[str]`
Get local path to template (downloads from GCS if needed).

**Parameters:**
- `template_name` (str): Name of template

**Returns:**
- `Optional[str]`: Local file path or None if not found

##### `log_activity(activity: str, details: Dict[str, Any]) -> None`
Log an activity to storage.

**Parameters:**
- `activity` (str): Activity type
- `details` (Dict[str, Any]): Activity details

##### `get_usage_stats() -> Dict[str, Any]`
Get usage statistics from logs.

**Returns:**
- `Dict[str, Any]`: Usage statistics

### Utility Functions

#### `sanitize_filename(filename: str) -> str`
Sanitize filename for safe storage.

**Parameters:**
- `filename` (str): Original filename

**Returns:**
- `str`: Sanitized filename

#### `cleanup_old_files(directory: str, max_age_hours: int = 2) -> int`
Remove old temporary files.

**Parameters:**
- `directory` (str): Directory to clean
- `max_age_hours` (int): Maximum file age in hours

**Returns:**
- `int`: Number of files removed

#### `ensure_directory_exists(directory: str) -> None`
Ensure a directory exists, create if not.

**Parameters:**
- `directory` (str): Directory path

---

## Configuration

All modules use configuration from `config.py`:

```python
from config import config

# Access configuration
max_upload_size = config.max_upload_size_mb
session_timeout = config.session.timeout_minutes
```

## Error Handling

All modules use structured logging with `structlog`:

```python
import structlog
logger = structlog.get_logger()

try:
    # Operation
except Exception as e:
    logger.error("operation_failed", error=str(e))
```

## Security Considerations

1. **Authentication**: All sensitive operations require authentication
2. **CSRF Protection**: Forms protected with JWT tokens
3. **Rate Limiting**: Prevents abuse and DoS attacks
4. **Input Validation**: All user inputs validated and sanitized
5. **File Security**: Path traversal prevention and content validation

## Performance Considerations

1. **Parallel Processing**: PDF generation uses ThreadPoolExecutor
2. **Caching**: Templates cached for 5 minutes (GCS)
3. **Resource Management**: Context managers ensure cleanup
4. **Memory Efficiency**: Streaming for large files

## Threading Safety

Thread-safe components:
- Rate limiter (uses locks)
- PDF generation progress tracking
- Session management

## Best Practices

1. Always use context managers for file operations
2. Validate all user inputs before processing
3. Log security-relevant events
4. Handle errors gracefully with user-friendly messages
5. Clean up temporary files promptly