"""
Centralized environment detection for SafeSteps Certificate Generator.
Provides consistent environment detection and storage path resolution across all modules.
"""
import os
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()


def is_streamlit_cloud() -> bool:
    """
    Detect if the application is running on Streamlit Cloud.
    Uses multiple detection methods for robust identification.
    
    Returns:
        bool: True if running on Streamlit Cloud, False otherwise
    """
    # Method 1: Check for Streamlit Cloud mount path
    if os.path.exists("/mount/src"):
        logger.debug("Streamlit Cloud detected via /mount/src path")
        return True
    
    # Method 2: Check if current working directory starts with mount path
    if os.getcwd().startswith("/mount/src"):
        logger.debug("Streamlit Cloud detected via working directory path")
        return True
    
    # Method 3: Check Streamlit-specific environment variables
    if os.getenv("STREAMLIT_RUNTIME_ENV") == "cloud":
        logger.debug("Streamlit Cloud detected via STREAMLIT_RUNTIME_ENV")
        return True
    
    # Method 4: Check server address for streamlit.io domain
    server_address = os.getenv("STREAMLIT_SERVER_ADDRESS", "")
    if "streamlit.io" in server_address or "streamlitapp.com" in server_address:
        logger.debug("Streamlit Cloud detected via server address")
        return True
    
    # Method 5: Check for Streamlit Cloud-specific environment markers
    streamlit_cloud_markers = [
        "STREAMLIT_SHARING_MODE",
        "STREAMLIT_CLOUD_MODE", 
        "STREAMLIT_DEPLOYMENT_ID"
    ]
    
    for marker in streamlit_cloud_markers:
        if os.getenv(marker):
            logger.debug(f"Streamlit Cloud detected via {marker} environment variable")
            return True
    
    logger.debug("Local development environment detected")
    return False


def get_user_storage_path() -> str:
    """
    Get the appropriate user storage path based on the current environment.
    
    Returns:
        str: Path to the user storage file
    """
    if is_streamlit_cloud():
        # On Streamlit Cloud, use /tmp directory for user storage
        storage_path = "/tmp/safesteps_users.json"
        logger.info(f"Using Streamlit Cloud user storage path: {storage_path}")
    else:
        # On local development, use local data directory
        storage_path = "./data/storage/users.json"
        logger.info(f"Using local development user storage path: {storage_path}")
    
    return storage_path


def get_jwt_secret() -> str:
    """
    Get JWT secret with environment-appropriate handling.
    
    Returns:
        str: JWT secret for token signing
        
    Raises:
        EnvironmentError: If JWT_SECRET is not properly configured
    """
    if is_streamlit_cloud():
        # On Streamlit Cloud, ONLY use st.secrets or generate deterministic secret
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'JWT_SECRET' in st.secrets:
                jwt_secret = st.secrets["JWT_SECRET"]
                if jwt_secret and jwt_secret.strip():
                    logger.info("JWT secret loaded from Streamlit Cloud secrets")
                    return jwt_secret
        except Exception as e:
            logger.debug(f"Could not read JWT_SECRET from Streamlit secrets: {e}")
        
        # Generate deterministic JWT_SECRET for Streamlit Cloud as fallback
        stable_seed = "SafeSteps-Certificate-Generator-2024-Streamlit-Cloud"
        jwt_secret = hashlib.sha256(stable_seed.encode()).hexdigest()
        logger.info("Using generated deterministic JWT secret for Streamlit Cloud")
        return jwt_secret
    else:
        # For local development, try st.secrets first, then environment
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'JWT_SECRET' in st.secrets:
                jwt_secret = st.secrets["JWT_SECRET"]
                if jwt_secret and jwt_secret.strip():
                    logger.info("JWT secret loaded from local Streamlit secrets")
                    return jwt_secret
        except Exception as e:
            logger.debug(f"Could not read JWT_SECRET from Streamlit secrets: {e}")
        
        # Fall back to environment variable for local dev
        jwt_secret = os.getenv("JWT_SECRET")
        if jwt_secret and jwt_secret.strip():
            logger.info("JWT secret loaded from environment variable")
            return jwt_secret
        
        # If no JWT secret found, raise error
        raise EnvironmentError(
            "JWT_SECRET is required for local development. "
            "Please set it in your .env file or as an environment variable."
        )


def get_environment_info() -> Dict[str, Any]:
    """
    Get comprehensive environment information for debugging.
    
    Returns:
        Dict[str, Any]: Environment information dictionary
    """
    info = {
        "is_streamlit_cloud": is_streamlit_cloud(),
        "user_storage_path": get_user_storage_path(),
        "current_working_directory": os.getcwd(),
        "environment_variables": {
            "STREAMLIT_RUNTIME_ENV": os.getenv("STREAMLIT_RUNTIME_ENV"),
            "STREAMLIT_SERVER_ADDRESS": os.getenv("STREAMLIT_SERVER_ADDRESS"),
            "STREAMLIT_SHARING_MODE": os.getenv("STREAMLIT_SHARING_MODE"),
            "STREAMLIT_CLOUD_MODE": os.getenv("STREAMLIT_CLOUD_MODE"),
            "STREAMLIT_DEPLOYMENT_ID": os.getenv("STREAMLIT_DEPLOYMENT_ID"),
        },
        "file_system_checks": {
            "/mount/src_exists": os.path.exists("/mount/src"),
            "cwd_starts_with_mount_src": os.getcwd().startswith("/mount/src"),
        }
    }
    
    # Filter out None values from environment variables
    info["environment_variables"] = {
        k: v for k, v in info["environment_variables"].items() if v is not None
    }
    
    return info


def log_environment_info():
    """Log comprehensive environment information for debugging."""
    env_info = get_environment_info()
    
    logger.info("Environment Detection Results", **env_info)
    
    # Log specific findings
    if env_info["is_streamlit_cloud"]:
        logger.info("Running on Streamlit Cloud - using cloud-specific configurations")
    else:
        logger.info("Running in local development - using local configurations")


def validate_storage_path(storage_path: str) -> bool:
    """
    Validate that the storage path is accessible and writable.
    
    Args:
        storage_path: Path to validate
        
    Returns:
        bool: True if path is valid and writable
    """
    try:
        # Create parent directories if they don't exist
        Path(storage_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Test write access by creating a temporary file
        test_file = Path(storage_path).with_suffix('.test')
        test_file.write_text('test')
        test_file.unlink()  # Remove test file
        
        logger.debug(f"Storage path validation successful: {storage_path}")
        return True
    except Exception as e:
        logger.error(f"Storage path validation failed for {storage_path}: {e}")
        return False


def ensure_storage_directory():
    """Ensure the storage directory exists and is writable."""
    storage_path = get_user_storage_path()
    
    if not validate_storage_path(storage_path):
        raise EnvironmentError(f"Cannot access user storage path: {storage_path}")
    
    logger.info(f"User storage directory verified: {Path(storage_path).parent}")


# Initialize logging when module is imported
log_environment_info()