"""
Pytest configuration and fixtures for Certificate Generator tests
"""
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables before any imports
os.environ["JWT_SECRET"] = "test_jwt_secret_key_for_testing_only_32_chars_min"
os.environ["USER_PASSWORD"] = "TestUser123!"
os.environ["ADMIN_PASSWORD"] = "TestAdmin123!"
os.environ["USE_LOCAL_STORAGE"] = "true"
os.environ["LOCAL_STORAGE_PATH"] = "./test_storage"
os.environ["LOG_LEVEL"] = "ERROR"  # Reduce noise during tests

# Mock streamlit before any modules import it
from unittest.mock import MagicMock

# Pre-emptively create mock streamlit module
_mock_streamlit = MagicMock()
_mock_streamlit.session_state = {}
sys.modules['streamlit'] = _mock_streamlit


class MockSessionState:
    """Mock Streamlit session state for testing"""
    def __init__(self):
        self._state = {}
    
    def __getattr__(self, key):
        # For attribute access like st.session_state.authenticated
        return self._state.get(key)
    
    def __setattr__(self, key, value):
        if key == "_state":
            super().__setattr__(key, value)
        else:
            # Store in state dictionary
            if not hasattr(self, '_state'):
                super().__setattr__('_state', {})
            self._state[key] = value
    
    def __contains__(self, key):
        return key in self._state
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def clear(self):
        if hasattr(self, '_state'):
            self._state.clear()
    
    def __delitem__(self, key):
        if key in self._state:
            del self._state[key]
    
    def keys(self):
        return self._state.keys() if hasattr(self, '_state') else []


@pytest.fixture(autouse=True)
def mock_streamlit():
    """Auto-use fixture to mock Streamlit for all tests"""
    # Get the pre-mocked streamlit
    st_mock = sys.modules['streamlit']
    
    # Create new session state for each test
    mock_state = MockSessionState()
    st_mock.session_state = mock_state
    
    # Set up mock methods
    st_mock.error = MagicMock()
    st_mock.warning = MagicMock()
    st_mock.info = MagicMock()
    st_mock.success = MagicMock()
    st_mock.stop = MagicMock(side_effect=Exception("st.stop() called"))
    
    # Mock other streamlit components that might be used
    st_mock.columns = MagicMock(return_value=[MagicMock(), MagicMock()])
    st_mock.container = MagicMock()
    st_mock.empty = MagicMock()
    st_mock.spinner = MagicMock()
    st_mock.progress = MagicMock()
    st_mock.file_uploader = MagicMock()
    st_mock.selectbox = MagicMock()
    st_mock.multiselect = MagicMock()
    st_mock.checkbox = MagicMock()
    st_mock.button = MagicMock(return_value=False)
    st_mock.form = MagicMock()
    st_mock.form_submit_button = MagicMock(return_value=False)
    st_mock.expander = MagicMock()
    st_mock.markdown = MagicMock()
    st_mock.write = MagicMock()
    st_mock.text_input = MagicMock()
    st_mock.text_area = MagicMock()
    st_mock.number_input = MagicMock()
    st_mock.slider = MagicMock()
    st_mock.download_button = MagicMock()
    
    yield st_mock


@pytest.fixture
def temp_storage_dir():
    """Create a temporary directory for test storage"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    from unittest.mock import MagicMock
    config = MagicMock()
    config.auth.user_password = "TestUser123!"
    config.auth.admin_password = "TestAdmin123!"
    config.auth.session_timeout_minutes = 30
    config.auth.enable_csrf_protection = True
    config.rate_limit.requests_limit = 40
    config.rate_limit.window_seconds = 60
    config.storage.local_path = "./test_storage"
    config.storage.use_local = True
    return config


@pytest.fixture
def authenticated_session(mock_streamlit):
    """Create an authenticated session for testing"""
    mock_streamlit.session_state.authenticated = True
    mock_streamlit.session_state.username = "testuser"
    mock_streamlit.session_state.role = "user"
    mock_streamlit.session_state.session_id = "test_session_123"
    mock_streamlit.session_state.login_time = datetime.now()
    mock_streamlit.session_state.last_activity = datetime.now()
    return mock_streamlit.session_state


@pytest.fixture
def admin_session(mock_streamlit):
    """Create an admin session for testing"""
    mock_streamlit.session_state.authenticated = True
    mock_streamlit.session_state.username = "admin"
    mock_streamlit.session_state.role = "admin"
    mock_streamlit.session_state.session_id = "admin_session_123"
    mock_streamlit.session_state.login_time = datetime.now()
    mock_streamlit.session_state.last_activity = datetime.now()
    return mock_streamlit.session_state


@pytest.fixture
def sample_csv_data():
    """Provide sample CSV data for testing"""
    return """Name,Email,Course,Date
John Doe,john@example.com,Python Basics,2024-01-15
Jane Smith,jane@example.com,Data Science,2024-01-16
Bob Johnson,bob@example.com,Web Development,2024-01-17"""


@pytest.fixture
def sample_template_data():
    """Provide sample template data for testing"""
    return {
        "template_name": "Basic Certificate",
        "template_type": "completion",
        "fields": {
            "title": "Certificate of Completion",
            "subtitle": "This certifies that",
            "name_field": "{{name}}",
            "course_field": "{{course}}",
            "date_field": "{{date}}",
            "signature": "Authorized Signature"
        },
        "style": {
            "background_color": "#ffffff",
            "text_color": "#000000",
            "font_family": "Arial"
        }
    }


# Ensure test directories exist
os.makedirs("./test_storage", exist_ok=True)
os.makedirs("./test_data", exist_ok=True)