"""
Deployment information utilities for SafeSteps application.
Provides git commit hash, timestamp, and environment detection.
"""

import os
import subprocess
from datetime import datetime


def get_deployment_info():
    """
    Get deployment information including git commit, timestamp, and environment.
    
    Returns:
        dict: Dictionary with deployment information
    """
    # Get git commit hash
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], 
            stderr=subprocess.DEVNULL
        ).decode().strip()[:8]
    except (subprocess.CalledProcessError, FileNotFoundError):
        commit = "unknown"
    
    # Detect environment
    # Streamlit Cloud sets multiple environment variables
    if any(env in os.environ for env in ['STREAMLIT_CLOUD', 'STREAMLIT_SHARING_MODE']):
        environment = "cloud"
    elif 'GOOGLE_CLOUD_PROJECT' in os.environ:
        environment = "gcp"
    elif 'DOCKER_CONTAINER' in os.environ:
        environment = "docker"
    else:
        environment = "local"
    
    return {
        "commit": commit,
        "timestamp": datetime.now().isoformat(),
        "environment": environment,
        "version": get_app_version()
    }


def get_app_version():
    """
    Get application version from git tags or default.
    
    Returns:
        str: Version string
    """
    try:
        # Try to get the latest git tag
        version = subprocess.check_output(
            ['git', 'describe', '--tags', '--abbrev=0'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        version = "1.0.0"
    
    return version


def get_git_revision():
    """
    Get git revision hash (short form).
    Legacy function for backward compatibility.
    
    Returns:
        str: Git commit hash (8 chars) or "unknown"
    """
    try:
        return subprocess.check_output(
            ['git', 'rev-parse', 'HEAD']
        ).decode('ascii').strip()[:8]
    except:
        return "unknown"