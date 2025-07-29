"""
Configuration settings for SafeSteps Certificate Generator
"""
import os
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Import centralized environment detection
from utils.environment import is_streamlit_cloud, get_jwt_secret, get_environment_info


def validate_environment():
    """Validate that required environment variables are present with user-friendly messages"""
    try:
        # Use centralized environment detection to validate JWT secret
        jwt_secret = get_jwt_secret()
        
        # Log environment information for debugging
        env_info = get_environment_info()
        import structlog
        logger = structlog.get_logger()
        logger.info("Environment validation successful", 
                   is_streamlit_cloud=env_info["is_streamlit_cloud"],
                   has_jwt_secret=bool(jwt_secret))
        
        return True
        
    except EnvironmentError as e:
        # Re-raise with additional context for user-friendly error messages
        env_info = get_environment_info()
        
        error_msg = f"""
🚨 Environment Configuration Error:

{str(e)}

📋 Quick Setup Guide:
1. Generate a secure JWT_SECRET:
   python -c "import secrets; print(secrets.token_urlsafe(32))"

2. Set the environment variable:
   • For development: Add JWT_SECRET=your-generated-secret to .env file
   • For production: Set JWT_SECRET environment variable in your deployment

3. Restart the application

Need help? Check the documentation or contact your administrator.
        """
        
        # Add platform-specific instructions
        if env_info["is_streamlit_cloud"]:
            error_msg += "\n\n📱 **Streamlit Cloud Instructions:**\n"
            error_msg += "1. Go to your app dashboard at share.streamlit.io\n"
            error_msg += "2. Click on your app settings (⋮ menu → Settings)\n"
            error_msg += "3. Navigate to 'Secrets' in the left sidebar\n"
            error_msg += "4. Add the following line:\n"
            error_msg += "   JWT_SECRET = \"your-generated-secret-here\"\n"
            error_msg += "5. Save and reboot the app\n\n"
            error_msg += "⚠️ Note: Environment variables do NOT work on Streamlit Cloud. You MUST use Secrets."
        else:
            error_msg += "\n\n💻 **Local Development:**\n"
            error_msg += "Set JWT_SECRET in your .env file or as an environment variable."
        
        raise EnvironmentError(error_msg.strip())


def get_environment_health() -> dict:
    """Check environment health and return status"""
    health = {
        "status": "healthy",
        "issues": [],
        "warnings": []
    }
    
    # Use centralized environment detection
    env_info = get_environment_info()
    is_cloud = env_info["is_streamlit_cloud"]
    
    # Check JWT_SECRET (from Streamlit secrets or environment)
    jwt_secret = None
    
    try:
        # Use centralized JWT secret handling
        jwt_secret = get_jwt_secret()
    except EnvironmentError:
        jwt_secret = None
    
    if not jwt_secret or not jwt_secret.strip():
        if not is_cloud:
            health["status"] = "critical"
            health["issues"].append("JWT_SECRET not set - sessions will not work")
    elif len(jwt_secret) < 32:
        health["status"] = "warning"
        health["warnings"].append("JWT_SECRET is shorter than recommended (32+ characters)")
    
    # Check optional environment variables
    if not os.getenv("USER_PASSWORD"):
        health["warnings"].append("USER_PASSWORD not set - using default (not recommended for production)")
    
    if not os.getenv("ADMIN_PASSWORD"):
        health["warnings"].append("ADMIN_PASSWORD not set - using default (not recommended for production)")
    
    # Check storage configuration
    if os.getenv("USE_LOCAL_STORAGE", "true").lower() == "false":
        if not os.getenv("GCS_PROJECT_ID") or not os.getenv("GCS_BUCKET_NAME"):
            health["status"] = "warning"
            health["warnings"].append("Cloud storage enabled but GCS configuration incomplete")
    
    return health


@dataclass
class AuthConfig:
    """Authentication configuration"""
    # Try Streamlit secrets first, then environment variables, then defaults
    user_password: str = None
    admin_password: str = None
    session_timeout_minutes: int = 30
    enable_csrf_protection: bool = True
    jwt_secret: str = None
    jwt_algorithm: str = "HS256"
    
    def __post_init__(self):
        """Initialize passwords from Streamlit secrets or environment variables"""
        # Use centralized environment detection
        env_info = get_environment_info()
        is_cloud = env_info["is_streamlit_cloud"]
        
        if is_cloud:
            # On Streamlit Cloud, use secrets and generate deterministic JWT_SECRET if not provided
            try:
                import streamlit as st
                
                if hasattr(st, 'secrets'):
                    self.user_password = st.secrets.get("USER_PASSWORD", "SafeSteps2024!")
                    self.admin_password = st.secrets.get("ADMIN_PASSWORD", "Admin@SafeSteps2024")
                    
                    # Use centralized JWT secret handling
                    try:
                        self.jwt_secret = get_jwt_secret()
                    except EnvironmentError:
                        # Fallback to deterministic secret generation
                        stable_seed = "SafeSteps-Certificate-Generator-2024-Streamlit-Cloud"
                        self.jwt_secret = hashlib.sha256(stable_seed.encode()).hexdigest()
                else:
                    # Use defaults if secrets not available
                    self.user_password = "SafeSteps2024!"
                    self.admin_password = "Admin@SafeSteps2024"
                    # Use centralized JWT secret handling
                    try:
                        self.jwt_secret = get_jwt_secret()
                    except EnvironmentError:
                        stable_seed = "SafeSteps-Certificate-Generator-2024-Streamlit-Cloud"
                        self.jwt_secret = hashlib.sha256(stable_seed.encode()).hexdigest()
            except Exception as e:
                # Use defaults on error
                import structlog
                logger = structlog.get_logger()
                logger.warning(f"Error loading Streamlit Cloud configuration: {e}")
                
                self.user_password = "SafeSteps2024!"
                self.admin_password = "Admin@SafeSteps2024"
                # Use centralized JWT secret handling
                try:
                    self.jwt_secret = get_jwt_secret()
                except EnvironmentError:
                    stable_seed = "SafeSteps-Certificate-Generator-2024-Streamlit-Cloud"
                    self.jwt_secret = hashlib.sha256(stable_seed.encode()).hexdigest()
        else:
            # For local development, try st.secrets first, then environment
            try:
                import streamlit as st
                # Try Streamlit secrets first
                if hasattr(st, 'secrets'):
                    self.user_password = st.secrets.get("USER_PASSWORD", "") or os.getenv("USER_PASSWORD", "SafeSteps2024!")
                    self.admin_password = st.secrets.get("ADMIN_PASSWORD", "") or os.getenv("ADMIN_PASSWORD", "Admin@SafeSteps2024")
                    
                    # Use centralized JWT secret handling
                    try:
                        self.jwt_secret = get_jwt_secret()
                    except EnvironmentError:
                        self.jwt_secret = ""
                else:
                    # Fallback to environment variables only
                    self.user_password = os.getenv("USER_PASSWORD", "SafeSteps2024!")
                    self.admin_password = os.getenv("ADMIN_PASSWORD", "Admin@SafeSteps2024")
                    
                    # Use centralized JWT secret handling
                    try:
                        self.jwt_secret = get_jwt_secret()
                    except EnvironmentError:
                        self.jwt_secret = ""
            except Exception as e:
                # Fallback to environment variables only
                import structlog
                logger = structlog.get_logger()
                logger.warning(f"Error loading local development configuration: {e}")
                
                self.user_password = os.getenv("USER_PASSWORD", "SafeSteps2024!")
                self.admin_password = os.getenv("ADMIN_PASSWORD", "Admin@SafeSteps2024")
                
                # Use centralized JWT secret handling
                try:
                    self.jwt_secret = get_jwt_secret()
                except EnvironmentError:
                    self.jwt_secret = ""


@dataclass
class StorageConfig:
    """Storage configuration"""
    use_local_storage: bool = os.getenv("USE_LOCAL_STORAGE", "true").lower() == "true"
    local_storage_path: Path = Path("./data/storage")
    gcs_project_id: Optional[str] = os.getenv("GCS_PROJECT_ID")
    gcs_bucket_name: Optional[str] = os.getenv("GCS_BUCKET_NAME")
    max_file_size_mb: int = 10


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_limit: int = 40
    window_seconds: int = 60
    login_attempts_limit: int = 5
    login_window_seconds: int = 300  # 5 minutes


@dataclass
class TempFileConfig:
    """Temporary file configuration"""
    temp_dir: Path = Path("./temp")
    cleanup_interval_seconds: int = 300
    max_age_seconds: int = 3600


@dataclass
class AppConfig:
    """Main application configuration"""
    app_name: str = "SafeSteps Certificate Generator"
    app_version: str = "1.0.0"
    debug_mode: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Brand colors
    primary_color: str = "#032A51"
    accent_color: str = "#9ACA3C"
    
    # UI Configuration
    sidebar_width: int = 280
    max_upload_size_mb: int = 10
    
    # Certificate settings
    default_template: str = "professional_certificate"
    available_templates: list = None
    
    def __post_init__(self):
        if self.available_templates is None:
            self.available_templates = [
                "professional_certificate",
                "basic_certificate",
                "workshop_certificate",
                "multilingual_certificate"
            ]


@dataclass
class Config:
    """Main configuration container"""
    auth: AuthConfig = None
    storage: StorageConfig = None
    rate_limit: RateLimitConfig = None
    temp_file: TempFileConfig = None
    app: AppConfig = None
    
    def __post_init__(self):
        self.auth = self.auth or AuthConfig()
        self.storage = self.storage or StorageConfig()
        self.rate_limit = self.rate_limit or RateLimitConfig()
        self.temp_file = self.temp_file or TempFileConfig()
        self.app = self.app or AppConfig()
        
        # Create necessary directories
        self.storage.local_storage_path.mkdir(parents=True, exist_ok=True)
        self.temp_file.temp_dir.mkdir(parents=True, exist_ok=True)


# Global config instance
config = Config()