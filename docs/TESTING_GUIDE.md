# Testing Guide

## Overview
This guide covers how to test the Certificate Generator application, including unit tests, integration tests, and security verification.

## Test Suite Structure

```
tests/
├── test_security_fixes.py    # Security-specific tests
├── test_auth.py             # Authentication tests
├── test_pdf_generator.py    # PDF generation tests
├── test_validators.py       # Input validation tests
└── test_storage.py          # Storage integration tests
```

## Running Tests

### Prerequisites

1. Install test dependencies:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

2. Set up test environment:
```bash
# Copy test environment file
cp .env.test.example .env.test

# Set test environment variables
export JWT_SECRET="test_jwt_secret_32_chars_minimum!"
export USER_PASSWORD="TestUser123"
export ADMIN_PASSWORD="TestAdmin456"
```

### Running All Tests

```bash
# Run all tests with verbose output
python -m pytest -v

# Run with coverage report
python -m pytest --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_security_fixes.py -v
```

### Running Security Tests

The security test suite verifies critical security fixes:

```bash
# Run only security tests
python -m pytest tests/test_security_fixes.py -v

# Run specific security test
python -m pytest tests/test_security_fixes.py::TestSecurityFixes::test_jwt_secret_from_environment -v
```

## Test Categories

### 1. Unit Tests

#### Authentication Tests (`test_auth.py`)
- Password hashing and validation
- Session creation and management
- Rate limiting functionality
- CSRF token generation/validation

```python
def test_password_validation():
    """Test password validation with bcrypt"""
    # Test implementation
```

#### Security Tests (`test_security_fixes.py`)
- JWT_SECRET environment loading
- Password requirement enforcement
- Session persistence verification
- CSRF protection validation

```python
def test_jwt_secret_from_environment():
    """Test that JWT_SECRET is loaded from environment variable"""
    # Test implementation
```

### 2. Integration Tests

#### Storage Tests (`test_storage.py`)
- Local storage functionality
- GCS integration (with mocks)
- Fallback behavior
- File operations

```python
def test_gcs_fallback_to_local():
    """Test fallback to local storage when GCS unavailable"""
    # Test implementation
```

#### PDF Generation Tests (`test_pdf_generator.py`)
- Template loading
- Field mapping
- Bulk generation
- Error handling

### 3. End-to-End Tests

#### Manual Testing Checklist

1. **Authentication Flow**
   - [ ] Login with user credentials
   - [ ] Login with admin credentials
   - [ ] Verify session persistence after restart
   - [ ] Test logout functionality
   - [ ] Verify rate limiting on failed logins

2. **Certificate Generation**
   - [ ] Upload CSV file
   - [ ] Upload XLSX file
   - [ ] Select template
   - [ ] Preview certificate
   - [ ] Generate bulk certificates
   - [ ] Download ZIP file

3. **Admin Functions**
   - [ ] Upload new template
   - [ ] Map template to course
   - [ ] Delete template
   - [ ] Change passwords
   - [ ] View activity logs

## Security Testing

### Environment Variable Validation

Test that the application properly validates required environment variables:

```bash
# Test missing JWT_SECRET
unset JWT_SECRET
python -m pytest tests/test_security_fixes.py::test_jwt_secret_warning_when_not_set

# Test missing passwords
unset USER_PASSWORD
python app.py  # Should fail with ValueError
```

### Session Persistence Testing

1. Start the application:
```bash
streamlit run app.py
```

2. Login and create a session

3. Stop the application (Ctrl+C)

4. Start the application again

5. Verify you're still logged in

### CSRF Protection Testing

```python
# Test CSRF token generation
def test_csrf_token_generation():
    token = generate_csrf_token()
    assert token != ""
    assert validate_csrf_token(token) == True

# Test invalid token
def test_invalid_csrf_token():
    assert validate_csrf_token("invalid") == False
```

## Performance Testing

### Load Testing

Use locust for load testing:

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8501
```

### Rate Limit Testing

```python
# Test rate limiter
def test_rate_limiting():
    for i in range(101):  # Exceed limit
        allowed, retry_after = rate_limiter.is_allowed("test_key")
        if i < 100:
            assert allowed == True
        else:
            assert allowed == False
            assert retry_after > 0
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          JWT_SECRET: "test_secret_for_ci_32_chars_min!"
          USER_PASSWORD: "TestUser123"
          ADMIN_PASSWORD: "TestAdmin456"
        run: |
          python -m pytest -v --cov=.
```

## Test Data

### Sample Test Files

Location: `tests/fixtures/`

- `test_data.csv` - Sample CSV with certificate data
- `test_template.pdf` - Sample PDF template
- `invalid_data.csv` - CSV with invalid data for error testing

### Mock Data Generation

```python
def generate_test_data(num_records=10):
    """Generate test certificate data"""
    return pd.DataFrame({
        'Name': [f'Test User {i}' for i in range(num_records)],
        'Course': ['Test Course'] * num_records,
        'Date': [datetime.now().strftime('%Y-%m-%d')] * num_records,
        'Certificate_Number': [f'TEST-{i:04d}' for i in range(num_records)]
    })
```

## Debugging Tests

### Verbose Output

```bash
# Maximum verbosity
python -m pytest -vvv

# Show print statements
python -m pytest -s

# Stop on first failure
python -m pytest -x
```

### Debug Specific Test

```bash
# Run with pdb debugger
python -m pytest --pdb tests/test_auth.py::test_password_validation
```

### Check Test Coverage

```bash
# Generate coverage report
python -m pytest --cov=. --cov-report=term-missing

# HTML coverage report
python -m pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

## Common Test Issues

### Issue: Import Errors

```python
# Add parent directory to path in test files
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

### Issue: Environment Variables Not Set

```python
# Use fixtures to set environment variables
@pytest.fixture
def env_setup():
    os.environ['JWT_SECRET'] = 'test_secret'
    yield
    del os.environ['JWT_SECRET']
```

### Issue: Streamlit Session State

```python
# Mock streamlit session state
from unittest.mock import MagicMock
st.session_state = MagicMock()
st.session_state.get.return_value = "test_value"
```

## Best Practices

1. **Test Isolation**
   - Each test should be independent
   - Clean up after tests (files, env vars)
   - Use fixtures for common setup

2. **Test Coverage**
   - Aim for >80% code coverage
   - Focus on critical paths
   - Test error conditions

3. **Security Testing**
   - Always test with different permission levels
   - Verify authentication boundaries
   - Test input validation thoroughly

4. **Performance Considerations**
   - Mock external services (GCS, etc.)
   - Use small test datasets
   - Parallelize tests when possible

## Adding New Tests

Template for new test file:

```python
"""
Test module for [component name]
"""
import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestComponentName:
    """Test suite for ComponentName"""
    
    def setup_method(self):
        """Setup before each test"""
        pass
    
    def teardown_method(self):
        """Cleanup after each test"""
        pass
    
    def test_basic_functionality(self):
        """Test basic component functionality"""
        # Arrange
        # Act
        # Assert
        assert True
    
    def test_error_handling(self):
        """Test error conditions"""
        with pytest.raises(ValueError):
            # Code that should raise error
            pass
```

## Reporting Issues

When reporting test failures:

1. Include full error output
2. Specify Python version and OS
3. List environment variables set
4. Provide minimal reproduction case
5. Include relevant log output