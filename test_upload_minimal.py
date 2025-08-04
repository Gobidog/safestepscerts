#!/usr/bin/env python3
"""Minimal test to verify file upload functionality"""

import streamlit as st

st.title("File Upload Test")

# Test basic file uploader
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=['csv', 'xlsx', 'xls'],
    help="Test file upload"
)

if uploaded_file is not None:
    st.success(f"✅ File uploaded successfully: {uploaded_file.name}")
    st.write(f"File size: {uploaded_file.size} bytes")
    st.write(f"File type: {uploaded_file.type}")
else:
    st.info("👆 Click 'Browse files' to upload a CSV file")

# Display session state
st.subheader("Session State")
st.json(dict(st.session_state))