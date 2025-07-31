import streamlit as st
import subprocess
import os
import hashlib

st.title("SafeSteps Deployment Diagnostics")

# Show current git commit
try:
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    st.info(f"Current Git Commit: {commit}")
except:
    st.error("Could not get git commit")

# Show file hashes to verify content
files_to_check = ['app.py', 'utils/ui_components.py']
for file in files_to_check:
    if os.path.exists(file):
        with open(file, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        st.write(f"**{file}** MD5: {file_hash}")

# Check for unsafe HTML
st.header("Checking for unsafe_allow_html")
for file in files_to_check:
    if os.path.exists(file):
        with open(file, 'r') as f:
            content = f.read()
            if 'unsafe_allow_html=True' in content:
                st.error(f"❌ Found unsafe_allow_html in {file}")
            else:
                st.success(f"✅ No unsafe_allow_html in {file}")

# Show environment
st.header("Environment Info")
st.write(f"Working Directory: {os.getcwd()}")
st.write(f"Streamlit Cloud: {'Yes' if os.path.exists('/mount/src') else 'No'}")

# Check actual progress function
st.header("Progress Function Check")
try:
    from utils.ui_components import create_progress_steps
    import inspect
    source = inspect.getsource(create_progress_steps)
    st.code(source[:500] + "..." if len(source) > 500 else source, language='python')
except Exception as e:
    st.error(f"Could not load progress function: {e}")

# Show deployment version
if 'DEPLOYMENT_VERSION' in globals():
    st.info(f"Deployment Version: {DEPLOYMENT_VERSION}")
else:
    # Try to get it from app.py
    try:
        with open('app.py', 'r') as f:
            for line in f:
                if 'DEPLOYMENT_VERSION' in line and '=' in line:
                    st.info(f"Found: {line.strip()}")
                    break
    except:
        pass