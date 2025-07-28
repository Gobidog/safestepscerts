"""
Login page - Properly redirects to main app using st.switch_page
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import auth utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import is_session_valid

# Check if user is already authenticated
if is_session_valid():
    st.info("You are already logged in. Redirecting to main page...")
    st.switch_page("app.py")
else:
    # Redirect to main app for login
    st.switch_page("app.py")