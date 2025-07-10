"""
Login page - Redirects to main app
"""
import streamlit as st

# Redirect to main app which now handles login
st.switch_page("app.py")