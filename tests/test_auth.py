"""
Unit tests for authentication module
"""
import pytest
import streamlit as st
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import bcrypt
from jose import jwt

from utils.auth import (
    hash_password,
    validate_password,
    validate_password_strength,
    create_session,
    is_session_valid,
    get_current_user,
    logout,
    update_passwords,
    RateLimiter,
    generate_csrf_token,
    validate_csrf_token,
    login_with_password
)


class TestPasswordHashing:
    """Test password hashing functionality"""
    
    def test_hash_password_creates_valid_bcrypt_hash(self):
        """Test that password hashing creates valid bcrypt hash"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        # Verify it's a valid bcrypt hash
        assert hashed.startswith('$2b$')
        assert len(hashed) == 60
        
        # Verify the hash works with bcrypt
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def test_hash_password_different_salts(self):
        """Test that same password creates different hashes"""
        password = "TestPassword123!"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Hashes should be different due to different salts
        assert hash1 != hash2
        
        # But both should validate the same password
        assert bcrypt.checkpw(password.encode('utf-8'), hash1.encode('utf-8'))
        assert bcrypt.checkpw(password.encode('utf-8'), hash2.encode('utf-8'))
    
    def test_hash_password_unicode(self):
        """Test hashing works with unicode passwords"""
        password = "Test密码123!🔒"
        hashed = hash_password(password)
        
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


class TestPasswordValidation:
    """Test password validation functionality"""
    
    @patch('utils.auth.get_stored_passwords')
    def test_validate_password_correct(self, mock_get_passwords):
        """Test validation with correct password"""
        password = "TestPassword123!"
        hashed = hash_password(password)
        mock_get_passwords.return_value = {"user": hashed}
        
        assert validate_password(password, "user") is True
    
    @patch('utils.auth.get_stored_passwords')
    def test_validate_password_incorrect(self, mock_get_passwords):
        """Test validation with incorrect password"""
        correct_password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = hash_password(correct_password)
        mock_get_passwords.return_value = {"user": hashed}
        
        assert validate_password(wrong_password, "user") is False
    
    @patch('utils.auth.get_stored_passwords')
    def test_validate_password_invalid_role(self, mock_get_passwords):
        """Test validation with invalid role"""
        mock_get_passwords.return_value = {"user": "hash", "admin": "hash"}
        
        assert validate_password("any_password", "invalid_role") is False
    
    def test_validate_password_strength_valid(self):
        """Test password strength validation with valid password"""
        is_valid, msg = validate_password_strength("ValidPass123!")
        assert is_valid is True
        assert "acceptable" in msg
    
    def test_validate_password_strength_too_short(self):
        """Test password strength validation with short password"""
        is_valid, msg = validate_password_strength("Pass1!")
        assert is_valid is False
        assert "at least 8 characters" in msg
    
    def test_validate_password_strength_missing_requirements(self):
        """Test password strength validation with missing requirements"""
        # Missing uppercase
        is_valid, msg = validate_password_strength("password123")
        assert is_valid is False
        assert "uppercase" in msg
        
        # Missing lowercase
        is_valid, msg = validate_password_strength("PASSWORD123")
        assert is_valid is False
        assert "lowercase" in msg
        
        # Missing digit
        is_valid, msg = validate_password_strength("PasswordOnly")
        assert is_valid is False
        assert "numbers" in msg


class TestSessionManagement:
    """Test session management functionality"""
    
    def setup_method(self):
        """Reset session state before each test"""
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    def test_create_session(self):
        """Test session creation"""
        session_id = create_session("testuser", "user")
        
        assert st.session_state.authenticated is True
        assert st.session_state.username == "testuser"
        assert st.session_state.role == "user"
        assert st.session_state.session_id == session_id
        assert isinstance(st.session_state.login_time, datetime)
        assert isinstance(st.session_state.last_activity, datetime)
    
    def test_is_session_valid_authenticated(self):
        """Test session validation for authenticated session"""
        create_session("testuser", "user")
        assert is_session_valid() is True
    
    def test_is_session_valid_not_authenticated(self):
        """Test session validation for non-authenticated session"""
        assert is_session_valid() is False
    
    @patch('utils.auth.config')
    def test_is_session_valid_expired(self, mock_config):
        """Test session validation for expired session"""
        # Set short timeout
        mock_config.auth.session_timeout_minutes = 1
        
        # Create session
        create_session("testuser", "user")
        
        # Simulate expired session
        st.session_state.last_activity = datetime.now() - timedelta(minutes=2)
        
        assert is_session_valid() is False
        assert st.session_state.get("authenticated") is None
    
    def test_get_current_user_authenticated(self):
        """Test getting current user when authenticated"""
        create_session("testuser", "admin")
        
        user = get_current_user()
        assert user is not None
        assert user["username"] == "testuser"
        assert user["role"] == "admin"
        assert "session_id" in user
        assert "login_time" in user
    
    def test_get_current_user_not_authenticated(self):
        """Test getting current user when not authenticated"""
        user = get_current_user()
        assert user is None
    
    def test_logout(self):
        """Test logout functionality"""
        # Create session
        create_session("testuser", "user")
        assert st.session_state.authenticated is True
        
        # Logout
        logout()
        
        # Verify session cleared
        assert st.session_state.get("authenticated") is None
        assert st.session_state.get("username") is None
        assert st.session_state.get("role") is None
        assert st.session_state.get("session_id") is None


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_allows_under_limit(self):
        """Test rate limiter allows requests under limit"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        # First 3 requests should be allowed
        for i in range(3):
            allowed, retry_after = limiter.is_allowed("test_key")
            assert allowed is True
            assert retry_after is None
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit"""
        limiter = RateLimiter(max_requests=3, window_seconds=60)
        
        # Use up the limit
        for i in range(3):
            limiter.is_allowed("test_key")
        
        # Next request should be blocked
        allowed, retry_after = limiter.is_allowed("test_key")
        assert allowed is False
        assert retry_after is not None
        assert retry_after > 0
    
    def test_rate_limiter_different_keys(self):
        """Test rate limiter tracks different keys separately"""
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        
        # Use up limit for key1
        allowed, _ = limiter.is_allowed("key1")
        assert allowed is True
        
        allowed, _ = limiter.is_allowed("key1")
        assert allowed is False
        
        # key2 should still be allowed
        allowed, _ = limiter.is_allowed("key2")
        assert allowed is True
    
    def test_rate_limiter_reset(self):
        """Test rate limiter reset functionality"""
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        
        # Use up limit
        limiter.is_allowed("test_key")
        allowed, _ = limiter.is_allowed("test_key")
        assert allowed is False
        
        # Reset
        limiter.reset("test_key")
        
        # Should be allowed again
        allowed, _ = limiter.is_allowed("test_key")
        assert allowed is True


class TestCSRFProtection:
    """Test CSRF protection functionality"""
    
    def setup_method(self):
        """Reset session state before each test"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    @patch('utils.auth.config')
    def test_generate_csrf_token_enabled(self, mock_config):
        """Test CSRF token generation when enabled"""
        mock_config.auth.enable_csrf_protection = True
        
        # Create session
        create_session("testuser", "user")
        
        # Generate token
        token = generate_csrf_token()
        
        assert token != ""
        assert st.session_state.csrf_token == token
        
        # Verify token structure
        from utils.auth import JWT_SECRET, JWT_ALGORITHM
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["username"] == "testuser"
        assert "session_id" in payload
        assert "exp" in payload
    
    @patch('utils.auth.config')
    def test_generate_csrf_token_disabled(self, mock_config):
        """Test CSRF token generation when disabled"""
        mock_config.auth.enable_csrf_protection = False
        
        token = generate_csrf_token()
        assert token == ""
    
    @patch('utils.auth.config')
    def test_validate_csrf_token_valid(self, mock_config):
        """Test CSRF token validation with valid token"""
        mock_config.auth.enable_csrf_protection = True
        
        # Create session and token
        create_session("testuser", "user")
        token = generate_csrf_token()
        
        # Validate
        assert validate_csrf_token(token) is True
    
    @patch('utils.auth.config')
    def test_validate_csrf_token_invalid_session(self, mock_config):
        """Test CSRF token validation with mismatched session"""
        mock_config.auth.enable_csrf_protection = True
        
        # Create session and token
        create_session("testuser", "user")
        token = generate_csrf_token()
        
        # Change session
        st.session_state.session_id = "different_session"
        
        # Validate should fail
        assert validate_csrf_token(token) is False
    
    @patch('utils.auth.config')
    def test_validate_csrf_token_expired(self, mock_config):
        """Test CSRF token validation with expired token"""
        mock_config.auth.enable_csrf_protection = True
        
        # Create expired token
        from utils.auth import JWT_SECRET, JWT_ALGORITHM
        payload = {
            "session_id": "test",
            "username": "test",
            "exp": datetime.utcnow() - timedelta(hours=1),
            "iat": datetime.utcnow() - timedelta(hours=2)
        }
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        
        assert validate_csrf_token(expired_token) is False


class TestPasswordUpdate:
    """Test password update functionality"""
    
    def setup_method(self):
        """Reset session state before each test"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    @patch('utils.auth.config')
    def test_update_passwords_valid(self, mock_config):
        """Test updating passwords with valid new passwords"""
        # Initialize with mock config
        mock_config.auth.user_password = "OldUser123!"
        mock_config.auth.admin_password = "OldAdmin123!"
        
        # Update passwords
        result = update_passwords(
            user_password="NewUser123!",
            admin_password="NewAdmin123!"
        )
        
        assert result is True
        assert "password_hashes" in st.session_state
        
        # Verify new passwords work
        user_hash = st.session_state.password_hashes["user"]
        admin_hash = st.session_state.password_hashes["admin"]
        
        assert bcrypt.checkpw("NewUser123!".encode('utf-8'), user_hash.encode('utf-8'))
        assert bcrypt.checkpw("NewAdmin123!".encode('utf-8'), admin_hash.encode('utf-8'))
    
    def test_update_passwords_weak_password(self):
        """Test updating passwords with weak password"""
        result = update_passwords(user_password="weak")
        assert result is False
    
    def test_update_passwords_partial_update(self):
        """Test updating only one password"""
        result = update_passwords(user_password="NewUser123!")
        assert result is True
        
        # Only user password should be updated
        assert "user" in st.session_state.password_hashes


class TestLoginFunction:
    """Test login functionality"""
    
    def setup_method(self):
        """Reset session state before each test"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    @patch('utils.auth.validate_password')
    @patch('utils.auth.rate_limiter')
    def test_login_with_password_admin(self, mock_limiter, mock_validate):
        """Test login with admin password"""
        mock_limiter.is_allowed.return_value = (True, None)
        mock_validate.side_effect = lambda pwd, role: role == "admin"
        
        success, role, error = login_with_password("admin_password")
        
        assert success is True
        assert role == "admin"
        assert error is None
        assert st.session_state.authenticated is True
    
    @patch('utils.auth.validate_password')
    @patch('utils.auth.rate_limiter')
    def test_login_with_password_user(self, mock_limiter, mock_validate):
        """Test login with user password"""
        mock_limiter.is_allowed.return_value = (True, None)
        mock_validate.side_effect = lambda pwd, role: role == "user" and pwd == "user_password"
        
        success, role, error = login_with_password("user_password")
        
        assert success is True
        assert role == "user"
        assert error is None
    
    @patch('utils.auth.rate_limiter')
    def test_login_with_password_rate_limited(self, mock_limiter):
        """Test login when rate limited"""
        mock_limiter.is_allowed.return_value = (False, 30)
        
        success, role, error = login_with_password("any_password")
        
        assert success is False
        assert role is None
        assert "Too many login attempts" in error
        assert "30 seconds" in error
    
    @patch('utils.auth.validate_password')
    @patch('utils.auth.rate_limiter')
    def test_login_with_password_invalid(self, mock_limiter, mock_validate):
        """Test login with invalid password"""
        mock_limiter.is_allowed.return_value = (True, None)
        mock_validate.return_value = False
        
        success, role, error = login_with_password("wrong_password")
        
        assert success is False
        assert role is None
        assert error == "Invalid password"


if __name__ == "__main__":
    pytest.main([__file__])