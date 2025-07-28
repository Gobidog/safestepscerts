"""
Certificate Generation Page - Ensures authentication and shows generation workflow
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import auth utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import is_session_valid, get_current_user

# Check authentication
if not is_session_valid():
    st.error("Please login to access the certificate generation page.")
    st.switch_page("app.py")
else:
    # User is authenticated, redirect to main app which handles the workflow
    user = get_current_user()
    st.info(f"Welcome {user['username']}! Redirecting to certificate generation...")
    st.switch_page("app.py")