"""
User storage and management system for SafeSteps Certificate Generator.
Provides JSON-based user storage with file locking for concurrent access.
"""
import json
import os
import fcntl
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import bcrypt
import structlog

logger = structlog.get_logger()


@dataclass
class User:
    """User data model"""
    user_id: str
    username: str
    email: str
    password_hash: str
    role: str  # 'user' or 'admin'
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary"""
        return cls(**data)


class UserStore:
    """
    User storage management with JSON file backend.
    Provides thread-safe operations with file locking.
    """
    
    def __init__(self, storage_path: str = "./data/storage/users.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage file if it doesn't exist
        if not self.storage_path.exists():
            self._write_users({})
            logger.info(f"Initialized user storage at {self.storage_path}")
    
    def _read_users(self) -> Dict[str, Dict[str, Any]]:
        """Read users from storage with file locking"""
        try:
            with open(self.storage_path, 'r') as f:
                # Acquire shared lock for reading
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                    return data
                finally:
                    # Release lock
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Could not read users file, returning empty dict")
            return {}
    
    def _write_users(self, users: Dict[str, Dict[str, Any]]) -> None:
        """Write users to storage with file locking"""
        with open(self.storage_path, 'w') as f:
            # Acquire exclusive lock for writing
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(users, f, indent=2)
            finally:
                # Release lock
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    def create_user(self, username: str, email: str, password: str, role: str = "user") -> Optional[User]:
        """
        Create a new user.
        Returns the created user or None if username/email already exists.
        """
        # Validate inputs
        if not username or not email or not password:
            logger.error("Cannot create user with empty username, email, or password")
            return None
        
        if role not in ["user", "admin"]:
            logger.error(f"Invalid role: {role}")
            return None
        
        # Check if username or email already exists
        users = self._read_users()
        
        for user_data in users.values():
            if user_data['username'].lower() == username.lower():
                logger.warning(f"Username already exists: {username}")
                return None
            if user_data['email'].lower() == email.lower():
                logger.warning(f"Email already exists: {email}")
                return None
        
        # Hash the password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create new user
        user = User(
            user_id=str(uuid.uuid4()),
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            created_at=datetime.now().isoformat(),
            last_login=None,
            is_active=True
        )
        
        # Save to storage
        users[user.user_id] = user.to_dict()
        self._write_users(users)
        
        logger.info(f"Created new user: {username} with role: {role}")
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        users = self._read_users()
        user_data = users.get(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username (case-insensitive)"""
        users = self._read_users()
        for user_data in users.values():
            if user_data['username'].lower() == username.lower():
                return User.from_dict(user_data)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email (case-insensitive)"""
        users = self._read_users()
        for user_data in users.values():
            if user_data['email'].lower() == email.lower():
                return User.from_dict(user_data)
        return None
    
    def get_user_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """Get user by username or email (case-insensitive)"""
        # First try username
        user = self.get_user_by_username(username_or_email)
        if user:
            return user
        
        # Then try email
        return self.get_user_by_email(username_or_email)
    
    def list_users(self, include_inactive: bool = False) -> List[User]:
        """List all users"""
        users = self._read_users()
        user_list = []
        
        for user_data in users.values():
            user = User.from_dict(user_data)
            if include_inactive or user.is_active:
                user_list.append(user)
        
        # Sort by created_at
        user_list.sort(key=lambda u: u.created_at)
        return user_list
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """
        Update user fields.
        Allowed fields: email, role, is_active, last_login
        """
        users = self._read_users()
        
        if user_id not in users:
            logger.error(f"User not found: {user_id}")
            return None
        
        user_data = users[user_id]
        
        # Update allowed fields
        allowed_fields = ['email', 'role', 'is_active', 'last_login']
        for field, value in kwargs.items():
            if field in allowed_fields:
                user_data[field] = value
                logger.info(f"Updated user {user_id} field {field}")
        
        # Save changes
        users[user_id] = user_data
        self._write_users(users)
        
        return User.from_dict(user_data)
    
    def update_password(self, user_id: str, new_password: str) -> bool:
        """Update user password"""
        users = self._read_users()
        
        if user_id not in users:
            logger.error(f"User not found: {user_id}")
            return False
        
        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        users[user_id]['password_hash'] = password_hash
        self._write_users(users)
        
        logger.info(f"Updated password for user: {user_id}")
        return True
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        Cannot delete the last admin user.
        """
        users = self._read_users()
        
        if user_id not in users:
            logger.error(f"User not found: {user_id}")
            return False
        
        user_data = users[user_id]
        
        # Check if this is the last admin
        if user_data['role'] == 'admin':
            admin_count = sum(1 for u in users.values() if u['role'] == 'admin' and u['is_active'])
            if admin_count <= 1:
                logger.error("Cannot delete the last admin user")
                return False
        
        # Delete user
        del users[user_id]
        self._write_users(users)
        
        logger.info(f"Deleted user: {user_id}")
        return True
    
    def verify_password(self, user: User, password: str) -> bool:
        """Verify user password"""
        return bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
    
    def get_admin_count(self) -> int:
        """Get count of active admin users"""
        users = self._read_users()
        return sum(1 for u in users.values() if u['role'] == 'admin' and u['is_active'])
    
    def initialize_default_admin(self, admin_password: str) -> Optional[User]:
        """
        Initialize default admin user if no users exist.
        Only called on first run.
        """
        users = self._read_users()
        
        if users:
            logger.info("Users already exist, skipping default admin creation")
            return None
        
        # Create default admin
        admin = self.create_user(
            username="admin",
            email="admin@safesteps.local",
            password=admin_password,
            role="admin"
        )
        
        if admin:
            logger.info("Created default admin user")
        else:
            logger.error("Failed to create default admin user")
        
        return admin


# Global user store instance
user_store = UserStore()