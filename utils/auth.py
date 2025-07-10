"""
Authentication utilities for Certificate Generator.
Handles password validation, session management, decorators, and rate limiting.
"""
import bcrypt
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Optional, Tuple, Any, Callable
import streamlit as st
import structlog
from collections import defaultdict, deque
from jose import jwt

from config import config

logger = structlog.get_logger()

# JWT secret for CSRF tokens
JWT_SECRET = secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"


class RateLimiter:
    """Rate limiter implementation for API endpoints"""
    
    def __init__(self, max_requests: int = 40, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, key: str) -> Tuple[bool, Optional[int]]:
        """
        Check if request is allowed under rate limit.
        Returns (allowed, seconds_until_reset)
        """
        now = time.time()
        request_times = self.requests[key]
        
        # Remove old requests outside the window
        while request_times and request_times[0] < now - self.window_seconds:
            request_times.popleft()
        
        if len(request_times) >= self.max_requests:
            # Calculate when the oldest request will expire
            oldest_request = request_times[0]
            reset_time = oldest_request + self.window_seconds
            seconds_until_reset = int(reset_time - now) + 1
            return False, seconds_until_reset
        
        # Add current request
        request_times.append(now)
        return True, None
    
    def reset(self, key: str):
        """Reset rate limit for a specific key"""
        self.requests[key] = deque()


# Global rate limiter instance
rate_limiter = RateLimiter(
    max_requests=config.rate_limit.requests_limit,
    window_seconds=config.rate_limit.window_seconds
)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def validate_password(password: str, role: str = "user") -> bool:
    """
    Validate password for given role.
    Returns True if password is correct for the role.
    """
    stored_passwords = get_stored_passwords()
    
    if role not in stored_passwords:
        logger.warning(f"Invalid role attempted: {role}")
        return False
    
    # Use bcrypt to check the password
    stored_hash = stored_passwords[role]
    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    
    if is_valid:
        logger.info(f"Successful login for role: {role}")
    else:
        logger.warning(f"Failed login attempt for role: {role}")
    
    return is_valid


def get_stored_passwords() -> Dict[str, str]:
    """
    Get stored password hashes for all roles.
    Uses bcrypt hashes stored in session state or creates them from config.
    """
    # Check if hashed passwords are already in session state
    if "password_hashes" in st.session_state:
        return st.session_state.password_hashes
    
    # Initialize password hashes from config
    # In a real production system, these would be pre-hashed and stored in a database
    password_hashes = {}
    
    # Get passwords from config (these should be set via environment variables)
    user_password = config.auth.user_password
    admin_password = config.auth.admin_password
    
    # For initial setup, we need to hash the plain passwords
    # In production, passwords should already be hashed in the database
    if "initial_setup_done" not in st.session_state:
        password_hashes["user"] = hash_password(user_password)
        password_hashes["admin"] = hash_password(admin_password)
        st.session_state.password_hashes = password_hashes
        st.session_state.initial_setup_done = True
    
    return st.session_state.password_hashes


def update_passwords(user_password: Optional[str] = None, 
                    admin_password: Optional[str] = None) -> bool:
    """
    Update user and/or admin passwords.
    Only accessible to admin users.
    """
    try:
        # Ensure password hashes are initialized
        if "password_hashes" not in st.session_state:
            st.session_state.password_hashes = get_stored_passwords()
        
        if user_password:
            # Validate password strength before updating
            is_strong, msg = validate_password_strength(user_password)
            if not is_strong:
                logger.warning(f"User password update rejected: {msg}")
                return False
            st.session_state.password_hashes["user"] = hash_password(user_password)
            logger.info("User password updated")
        
        if admin_password:
            # Validate password strength before updating
            is_strong, msg = validate_password_strength(admin_password)
            if not is_strong:
                logger.warning(f"Admin password update rejected: {msg}")
                return False
            st.session_state.password_hashes["admin"] = hash_password(admin_password)
            logger.info("Admin password updated")
        
        return True
    except Exception as e:
        logger.error(f"Error updating passwords: {e}")
        return False


def create_session(username: str, role: str) -> str:
    """Create a new user session and return session ID"""
    session_id = secrets.token_urlsafe(32)
    
    st.session_state.authenticated = True
    st.session_state.username = username
    st.session_state.role = role
    st.session_state.session_id = session_id
    st.session_state.login_time = datetime.now()
    st.session_state.last_activity = datetime.now()
    
    logger.info(f"Session created for {username} with role {role}")
    return session_id


def is_session_valid() -> bool:
    """Check if current session is valid and not expired"""
    if not st.session_state.get("authenticated", False):
        return False
    
    # Check session timeout
    last_activity = st.session_state.get("last_activity")
    if last_activity:
        timeout_minutes = config.auth.session_timeout_minutes
        if datetime.now() - last_activity > timedelta(minutes=timeout_minutes):
            logger.info("Session expired due to inactivity")
            logout()
            return False
    
    # Update last activity
    st.session_state.last_activity = datetime.now()
    return True


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get current authenticated user information"""
    if not is_session_valid():
        return None
    
    return {
        "username": st.session_state.get("username"),
        "role": st.session_state.get("role"),
        "session_id": st.session_state.get("session_id"),
        "login_time": st.session_state.get("login_time")
    }


def logout():
    """Clear session and logout user"""
    logger.info(f"User {st.session_state.get('username')} logged out")
    
    # Clear session state
    for key in ["authenticated", "username", "role", "session_id", 
                "login_time", "last_activity"]:
        if key in st.session_state:
            del st.session_state[key]


def requires_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for a function/page.
    Redirects to login page if not authenticated.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_session_valid():
            st.error("Please login to access this page")
            st.stop()
        return func(*args, **kwargs)
    return wrapper


def requires_admin(func: Callable) -> Callable:
    """
    Decorator to require admin role for a function/page.
    Shows error if user doesn't have admin privileges.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not is_session_valid():
            st.error("Please login to access this page")
            st.stop()
        
        user = get_current_user()
        if user and user.get("role") != "admin":
            st.error("This page requires admin privileges")
            st.stop()
        
        return func(*args, **kwargs)
    return wrapper


def rate_limit(key_func: Optional[Callable] = None):
    """
    Decorator to apply rate limiting to a function.
    
    Args:
        key_func: Optional function to generate rate limit key from args
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate rate limit key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default to session ID or IP
                user = get_current_user()
                key = user.get("session_id") if user else "anonymous"
            
            # Check rate limit
            allowed, retry_after = rate_limiter.is_allowed(key)
            
            if not allowed:
                st.error(f"Rate limit exceeded. Please try again in {retry_after} seconds.")
                st.stop()
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    return True, "Password strength is acceptable"


def login_with_password(password: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Attempt to login with a password.
    Returns (success, role, error_message)
    """
    # Check rate limit for login attempts
    ip_key = "login_attempt"  # In production, use actual IP
    allowed, retry_after = rate_limiter.is_allowed(ip_key)
    
    if not allowed:
        return False, None, f"Too many login attempts. Try again in {retry_after} seconds."
    
    # Try admin password first
    if validate_password(password, "admin"):
        session_id = create_session("admin", "admin")
        return True, "admin", None
    
    # Try user password
    if validate_password(password, "user"):
        session_id = create_session("user", "user")
        return True, "user", None
    
    return False, None, "Invalid password"


def check_session_hijacking() -> bool:
    """
    Basic session hijacking prevention.
    In production, would check IP, user agent, etc.
    """
    # For now, just ensure session hasn't been tampered with
    if st.session_state.get("authenticated") and not st.session_state.get("session_id"):
        logger.warning("Potential session hijacking detected")
        logout()
        return False
    return True


# Activity logging functions
def log_activity(action: str, details: Optional[Dict] = None):
    """Log user activity for audit trail"""
    user = get_current_user()
    logger.info(
        "user_activity",
        action=action,
        username=user.get("username") if user else "anonymous",
        role=user.get("role") if user else None,
        details=details or {}
    )


def get_session_info() -> Dict[str, Any]:
    """Get detailed session information for display"""
    user = get_current_user()
    if not user:
        return {}
    
    login_time = user.get("login_time")
    if login_time:
        duration = datetime.now() - login_time
        duration_str = f"{duration.seconds // 60} minutes"
    else:
        duration_str = "Unknown"
    
    return {
        "Username": user.get("username"),
        "Role": user.get("role"),
        "Login Time": login_time.strftime("%Y-%m-%d %H:%M:%S") if login_time else "Unknown",
        "Session Duration": duration_str,
        "Session ID": user.get("session_id")[:8] + "..." if user.get("session_id") else "Unknown"
    }


# CSRF Protection Functions
def generate_csrf_token() -> str:
    """Generate a CSRF token for the current session"""
    if not config.auth.enable_csrf_protection:
        return ""
    
    # Get current session
    user = get_current_user()
    if not user:
        return ""
    
    # Create token payload
    payload = {
        "session_id": user.get("session_id"),
        "username": user.get("username"),
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    
    # Generate token
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    # Store in session
    st.session_state.csrf_token = token
    
    return token


def validate_csrf_token(token: str) -> bool:
    """Validate a CSRF token"""
    if not config.auth.enable_csrf_protection:
        return True
    
    try:
        # Decode token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Verify session matches
        user = get_current_user()
        if not user:
            return False
        
        if payload.get("session_id") != user.get("session_id"):
            logger.warning("CSRF token session mismatch")
            return False
        
        if payload.get("username") != user.get("username"):
            logger.warning("CSRF token username mismatch")
            return False
        
        return True
        
    except jwt.ExpiredSignatureError:
        logger.warning("CSRF token expired")
        return False
    except jwt.JWTError as e:
        logger.warning(f"CSRF token validation error: {e}")
        return False


def csrf_protected(func: Callable) -> Callable:
    """Decorator to require CSRF token validation for a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not config.auth.enable_csrf_protection:
            return func(*args, **kwargs)
        
        # Get token from session state
        token = st.session_state.get("current_csrf_token")
        
        if not token or not validate_csrf_token(token):
            st.error("Invalid or missing CSRF token. Please refresh the page.")
            st.stop()
        
        return func(*args, **kwargs)
    return wrapper