"""
Admin Panel - Redirects to main app
"""
import streamlit as st

# Redirect to main app which now handles the admin dashboard
st.switch_page("app.py")