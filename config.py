"""
Configuration management for Certificate Generator application.
Handles environment variables, default values, and settings validation.
"""
import os
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field
from dotenv import load_dotenv
import structlog

# Load environment variables from .env file
load_dotenv()

# Configure structured logging
logger = structlog.get_logger()


@dataclass
class AppConfig:
    """Main application configuration"""
    app_name: str = os.getenv("APP_NAME", "Certificate Generator")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


@dataclass
class AuthConfig:
    """Authentication configuration"""
    user_password: str = os.getenv("USER_PASSWORD", "")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "")
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    max_session_count: int = int(os.getenv("MAX_SESSION_COUNT", "100"))
    enable_csrf_protection: bool = os.getenv("ENABLE_CSRF_PROTECTION", "true").lower() == "true"
    
    def __post_init__(self):
        if not self.user_password:
            logger.error("No user password set. USER_PASSWORD environment variable is required.")
            raise ValueError("USER_PASSWORD environment variable must be set")
        if not self.admin_password:
            logger.error("No admin password set. ADMIN_PASSWORD environment variable is required.")
            raise ValueError("ADMIN_PASSWORD environment variable must be set")


@dataclass
class StorageConfig:
    """Storage configuration for templates and generated files"""
    # Auto-detect storage mode: use local storage if GCS is not configured
    use_local_storage: bool = field(init=False)
    local_storage_path: Path = Path(os.getenv("LOCAL_STORAGE_PATH", "./local_storage"))
    
    # GCS Configuration
    gcs_bucket_name: Optional[str] = os.getenv("GCS_BUCKET_NAME")
    gcs_project_id: Optional[str] = os.getenv("GCS_PROJECT_ID")
    gcs_credentials_path: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    def __post_init__(self):
        # Auto-enable local storage if GCS is not configured
        explicit_local = os.getenv("USE_LOCAL_STORAGE", "").lower() == "true"
        has_gcs = bool(self.gcs_bucket_name)
        
        # Use local storage if explicitly set OR if GCS is not configured
        self.use_local_storage = explicit_local or not has_gcs
        
        # Log storage mode
        if self.use_local_storage:
            logger.info(f"Using local storage at: {self.local_storage_path}")
            # Create local storage directories
            self.local_storage_path.mkdir(parents=True, exist_ok=True)
            (self.local_storage_path / "templates").mkdir(exist_ok=True)
            (self.local_storage_path / "generated").mkdir(exist_ok=True)
        else:
            logger.info(f"Using Google Cloud Storage bucket: {self.gcs_bucket_name}")


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    requests_limit: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "3600"))


@dataclass
class FileConfig:
    """File upload and processing configuration"""
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "5"))
    allowed_extensions: List[str] = field(default_factory=lambda: 
        os.getenv("ALLOWED_EXTENSIONS", "xlsx,xls,csv").split(","))
    
    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@dataclass
class PDFConfig:
    """PDF generation configuration"""
    generation_timeout_seconds: int = int(os.getenv("PDF_GENERATION_TIMEOUT_SECONDS", "300"))
    max_concurrent_generations: int = int(os.getenv("MAX_CONCURRENT_GENERATIONS", "5"))
    compression_level: int = int(os.getenv("PDF_COMPRESSION_LEVEL", "9"))
    
    # Font settings
    default_font_family: str = "Helvetica"
    min_font_size: int = 8
    max_font_size: int = 72
    
    # Output settings
    output_dpi: int = 300
    jpeg_quality: int = 95


@dataclass
class TempFileConfig:
    """Temporary file management configuration"""
    cleanup_interval_minutes: int = int(os.getenv("TEMP_FILE_CLEANUP_INTERVAL_MINUTES", "60"))
    max_age_minutes: int = int(os.getenv("TEMP_FILE_MAX_AGE_MINUTES", "120"))
    temp_dir: Path = Path("/tmp/cert_gen")
    
    def __post_init__(self):
        self.temp_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class MonitoringConfig:
    """Monitoring and analytics configuration"""
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")
    google_analytics_id: Optional[str] = os.getenv("GOOGLE_ANALYTICS_ID")
    enable_metrics: bool = bool(os.getenv("ENABLE_METRICS", "false").lower() == "true")


@dataclass
class Config:
    """Main configuration container"""
    app: AppConfig = field(default_factory=AppConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)
    file: FileConfig = field(default_factory=FileConfig)
    pdf: PDFConfig = field(default_factory=PDFConfig)
    temp_file: TempFileConfig = field(default_factory=TempFileConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        try:
            # Check critical settings
            if not self.auth.admin_password:
                raise ValueError("Admin password not set")
            
            if not self.storage.use_local_storage and not self.storage.gcs_bucket_name:
                raise ValueError("GCS bucket required when not using local storage")
            
            # Validate numeric ranges
            if self.file.max_upload_size_mb <= 0:
                raise ValueError("Invalid max upload size")
            
            if self.rate_limit.requests_limit <= 0:
                raise ValueError("Invalid rate limit")
            
            logger.info("Configuration validated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary (for logging/debugging)"""
        return {
            "app": {
                "name": self.app.app_name,
                "version": self.app.app_version,
                "debug": self.app.debug,
                "log_level": self.app.log_level
            },
            "auth": {
                "session_timeout_minutes": self.auth.session_timeout_minutes,
                "max_sessions": self.auth.max_session_count
            },
            "storage": {
                "use_local": self.storage.use_local_storage,
                "gcs_bucket": self.storage.gcs_bucket_name
            },
            "limits": {
                "max_upload_mb": self.file.max_upload_size_mb,
                "rate_limit_requests": self.rate_limit.requests_limit
            }
        }


# Create global configuration instance
config = Config()

# Validate on import
if not config.validate():
    logger.warning("Configuration validation failed - using defaults")


# Utility functions
def get_temp_path(filename: str) -> Path:
    """Get a path for a temporary file"""
    return config.temp_file.temp_dir / filename


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in config.file.allowed_extensions


def get_storage_path(category: str, filename: str) -> Path:
    """Get storage path for a file"""
    if config.storage.use_local_storage:
        return config.storage.local_storage_path / category / filename
    else:
        # For GCS, return a string path
        return Path(f"{category}/{filename}")


# Export configuration
__all__ = [
    'config',
    'Config',
    'AppConfig', 
    'AuthConfig',
    'StorageConfig',
    'RateLimitConfig',
    'FileConfig',
    'PDFConfig',
    'TempFileConfig',
    'MonitoringConfig',
    'get_temp_path',
    'is_allowed_file',
    'get_storage_path'
]