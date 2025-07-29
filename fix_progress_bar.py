#!/usr/bin/env python3
"""
Fix for progress bar HTML rendering issue in SafeSteps

This script checks and fixes any issues with HTML rendering in the progress bar
"""

import re

def check_html_rendering():
    """Check app.py for potential HTML rendering issues"""
    
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Check for any print statements that might output HTML
    print_matches = re.findall(r'print.*progress.*', content, re.IGNORECASE)
    if print_matches:
        print(f"Found {len(print_matches)} print statements with 'progress'")
        for match in print_matches:
            print(f"  - {match}")
    
    # Check for st.write or st.text that might output HTML
    write_matches = re.findall(r'st\.(write|text).*<div', content)
    if write_matches:
        print(f"Found {len(write_matches)} st.write/text statements with HTML")
        for match in write_matches:
            print(f"  - {match}")
    
    # Check if CSS block is properly closed
    css_blocks = re.findall(r'st\.markdown\(""".*?</style>.*?""", unsafe_allow_html=True\)', content, re.DOTALL)
    print(f"Found {len(css_blocks)} CSS blocks with proper markdown rendering")
    
    # Check for any HTML strings that might be output incorrectly
    html_strings = re.findall(r'["\'].*?<div class="progress-step.*?["\']', content)
    if html_strings:
        print(f"Found {len(html_strings)} HTML strings with progress-step")
        for match in html_strings[:3]:  # Show first 3
            print(f"  - {match[:50]}...")

def create_test_app():
    """Create a minimal test app to verify progress bar rendering"""
    
    test_code = '''import streamlit as st
from utils.ui_components import create_progress_steps

st.set_page_config(page_title="Progress Bar Test", layout="wide")

st.title("Progress Bar Rendering Test")

# Test the progress bar at different steps
for step in range(1, 6):
    st.subheader(f"Step {step}")
    steps = [
        ("Upload", "📤", 1),
        ("Validate", "✅", 2),
        ("Template", "📄", 3),
        ("Generate", "🏆", 4),
        ("Complete", "🎉", 5)
    ]
    create_progress_steps(steps, step)
    st.markdown("---")

st.info("If you see raw HTML above instead of styled progress bars, there's a rendering issue.")
'''
    
    with open('test_progress_bar.py', 'w') as f:
        f.write(test_code)
    
    print("Created test_progress_bar.py - run with: streamlit run test_progress_bar.py")

def add_debug_logging():
    """Add debug logging to track where HTML might be output"""
    
    debug_code = '''
# Add this at the top of app.py after imports
import sys
from io import StringIO

# Capture any print statements
old_stdout = sys.stdout
sys.stdout = StringIO()

# Add this function to check for HTML in output
def check_stdout_for_html():
    output = sys.stdout.getvalue()
    if '<div class="progress-step' in output:
        st.error("⚠️ Found HTML in stdout - this might be causing the rendering issue")
        st.code(output[:500])  # Show first 500 chars
        sys.stdout = StringIO()  # Reset buffer
'''
    
    print("Debug code to add to app.py:")
    print(debug_code)

if __name__ == "__main__":
    print("=== SafeSteps Progress Bar HTML Rendering Fix ===\n")
    
    print("1. Checking for potential HTML rendering issues...")
    check_html_rendering()
    
    print("\n2. Creating test app...")
    create_test_app()
    
    print("\n3. Debug logging suggestions...")
    add_debug_logging()
    
    print("\n=== Recommendations ===")
    print("1. Run the test app to verify progress bar rendering:")
    print("   streamlit run test_progress_bar.py")
    print("\n2. Clear browser cache and restart Streamlit:")
    print("   - Clear browser cache (Ctrl+Shift+Delete)")
    print("   - Stop Streamlit (Ctrl+C)")
    print("   - Run: streamlit run app.py --server.runOnSave false")
    print("\n3. Check for any custom CSS or JavaScript that might interfere")
    print("\n4. Ensure all HTML is rendered with st.markdown(..., unsafe_allow_html=True)")