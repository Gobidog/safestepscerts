"""
Admin Panel - Ensures admin authentication and redirects appropriately
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path to import auth utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import is_session_valid, get_current_user

# Check authentication and admin role
if not is_session_valid():
    st.error("Please login to access the admin panel.")
    st.switch_page("app.py")
else:
    user = get_current_user()
    if user.get("role") != "admin":
        st.error("You do not have permission to access the admin panel.")
        st.warning("Redirecting to main page...")
        st.switch_page("app.py")
    else:
        # Admin is authenticated, redirect to main app which handles the admin dashboard
        st.info(f"Welcome Admin {user['username']}! Redirecting to admin dashboard...")
        st.switch_page("app.py")