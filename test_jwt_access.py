#!/usr/bin/env python3
"""
Test JWT_SECRET access methods
"""
import os
import sys

print("Testing JWT_SECRET access methods...")

# Test 1: Environment variable
env_jwt = os.getenv("JWT_SECRET")
print(f"1. Environment variable JWT_SECRET: {'Found' if env_jwt else 'Not found'}")

# Test 2: Streamlit secrets (if available)
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'JWT_SECRET' in st.secrets:
        st_jwt = st.secrets["JWT_SECRET"]
        print(f"2. Streamlit secrets JWT_SECRET: {'Found' if st_jwt else 'Empty'}")
    else:
        print("2. Streamlit secrets JWT_SECRET: Not found")
except Exception as e:
    print(f"2. Streamlit secrets: Error - {e}")

# Test 3: Path detection
is_streamlit_cloud = os.path.exists("/mount/src") or os.getcwd().startswith("/mount/src")
print(f"3. Running on Streamlit Cloud: {is_streamlit_cloud}")
print(f"   Current directory: {os.getcwd()}")
print(f"   /mount/src exists: {os.path.exists('/mount/src')}")

# Test 4: Try our function
try:
    from utils.auth import get_jwt_secret_with_fallback
    jwt = get_jwt_secret_with_fallback()
    print(f"4. get_jwt_secret_with_fallback(): {'Success' if jwt else 'Failed'}")
except Exception as e:
    print(f"4. get_jwt_secret_with_fallback(): Error - {e}")