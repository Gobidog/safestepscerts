#!/usr/bin/env python3
"""
Patch to ensure progress bar renders correctly
This adds a safeguard to prevent raw HTML from being displayed
"""

def apply_progress_bar_patch():
    """Apply patch to ensure progress bar HTML renders correctly"""
    
    # Read the current app.py
    with open('app.py', 'r') as f:
        content = f.read()
    
    # Add a safeguard function after the imports
    safeguard_code = '''
# Progress bar rendering safeguard
def safe_progress_bar(current_step: int):
    """Safely render progress bar with fallback"""
    try:
        render_progress_bar(current_step)
    except Exception as e:
        # Fallback to simple progress indicator if HTML rendering fails
        st.warning("Progress bar rendering issue detected. Using simple indicator.")
        progress_text = f"Step {current_step} of 5"
        st.progress(current_step / 5)
        st.text(progress_text)
'''
    
    # Check if safeguard already exists
    if 'safe_progress_bar' not in content:
        # Find where to insert (after render_progress_bar function)
        insert_pos = content.find('def login_page():')
        if insert_pos > 0:
            content = content[:insert_pos] + safeguard_code + '\n\n' + content[insert_pos:]
            
            # Replace render_progress_bar calls with safe_progress_bar
            content = content.replace('render_progress_bar(st.session_state.workflow_step)', 
                                    'safe_progress_bar(st.session_state.workflow_step)')
            
            # Write the patched content
            with open('app_patched.py', 'w') as f:
                f.write(content)
            
            print("✅ Created app_patched.py with progress bar safeguard")
            print("To use: mv app.py app_backup.py && mv app_patched.py app.py")
        else:
            print("❌ Could not find insertion point for safeguard")
    else:
        print("ℹ️ Safeguard already exists in app.py")

def create_minimal_test():
    """Create a minimal test to isolate the issue"""
    
    test_code = '''import streamlit as st

st.title("HTML Rendering Test")

# Test 1: Basic HTML rendering
st.subheader("Test 1: Basic HTML")
st.markdown("""
<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
    <p>This should be a styled div with gray background</p>
</div>
""", unsafe_allow_html=True)

# Test 2: Progress-like HTML
st.subheader("Test 2: Progress HTML")
html_content = """
<div class="progress-container">
    <div class="progress-step active">
        <div class="progress-circle">1</div>
        <div class="progress-label">Test</div>
    </div>
</div>
"""

col1, col2 = st.columns(2)
with col1:
    st.write("With unsafe_allow_html=True:")
    st.markdown(html_content, unsafe_allow_html=True)

with col2:
    st.write("Without unsafe_allow_html:")
    st.markdown(html_content)

# Test 3: Check if HTML is being printed
st.subheader("Test 3: Output Check")
import sys
from io import StringIO

# Capture stdout
old_stdout = sys.stdout
sys.stdout = StringIO()

# Simulate some output
print("Normal output")
print("<div>This is HTML in print</div>")

# Get captured output
output = sys.stdout.getvalue()
sys.stdout = old_stdout

if output:
    st.warning("Found output in stdout:")
    st.code(output)
'''
    
    with open('test_html_rendering.py', 'w') as f:
        f.write(test_code)
    
    print("✅ Created test_html_rendering.py")
    print("Run with: streamlit run test_html_rendering.py")

if __name__ == "__main__":
    print("=== Progress Bar Rendering Patch ===\n")
    
    print("1. Creating patched version...")
    apply_progress_bar_patch()
    
    print("\n2. Creating HTML rendering test...")
    create_minimal_test()
    
    print("\n=== Next Steps ===")
    print("1. Test HTML rendering: streamlit run test_html_rendering.py")
    print("2. If test works, apply patch: mv app.py app_backup.py && mv app_patched.py app.py")
    print("3. Clear cache and restart: bash clear_cache_and_restart.sh")