import streamlit as st

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
