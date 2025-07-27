"""
Test to verify JWT_SECRET persistence fix
"""
import os
import sys
import pytest
from unittest.mock import patch

# Ensure we're testing from the right directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_jwt_secret_required():
    """Test that JWT_SECRET is required and not auto-generated"""
    # Clear JWT_SECRET from environment
    env_copy = os.environ.copy()
    if 'JWT_SECRET' in env_copy:
        del env_copy['JWT_SECRET']
    
    # Mock other required env vars
    env_copy['USER_PASSWORD'] = 'test123'
    env_copy['ADMIN_PASSWORD'] = 'admin123'
    
    with patch.dict('os.environ', env_copy, clear=True):
        # Should raise RuntimeError when JWT_SECRET is missing
        with pytest.raises(RuntimeError) as exc_info:
            # Force reload to pick up environment changes
            import importlib
            if 'utils.auth' in sys.modules:
                del sys.modules['utils.auth']
            if 'config' in sys.modules:
                del sys.modules['config']
            import utils.auth
        
        assert "JWT_SECRET environment variable is required" in str(exc_info.value)


def test_jwt_secret_used_when_set():
    """Test that provided JWT_SECRET is used"""
    test_secret = "test_jwt_secret_key_that_is_at_least_32_chars_long"
    
    env_copy = os.environ.copy()
    env_copy['JWT_SECRET'] = test_secret
    env_copy['USER_PASSWORD'] = 'test123'
    env_copy['ADMIN_PASSWORD'] = 'admin123'
    
    with patch.dict('os.environ', env_copy, clear=True):
        # Force reload
        import importlib
        if 'utils.auth' in sys.modules:
            del sys.modules['utils.auth']
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # This should work without raising an error
        import utils.auth
        assert utils.auth.JWT_SECRET == test_secret