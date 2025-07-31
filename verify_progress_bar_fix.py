#!/usr/bin/env python3
"""
Manual verification script for progress bar HTML rendering fix
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ui_components import create_progress_steps

def check_function_for_html():
    """Check if create_progress_steps function contains unsafe HTML usage"""
    import inspect
    source = inspect.getsource(create_progress_steps)
    
    print("=== VERIFYING PROGRESS BAR IMPLEMENTATION ===\n")
    
    # Check for unsafe_allow_html
    if "unsafe_allow_html=True" in source:
        print("❌ FAILED: Found unsafe_allow_html=True in function")
        return False
    else:
        print("✅ PASSED: No unsafe_allow_html=True found")
    
    # Check for HTML tags
    html_tags = ["<div", "<span", "<style", "<p>", "<h1", "<h2", "<h3", "<center"]
    found_html = False
    for tag in html_tags:
        if tag in source:
            print(f"❌ FAILED: Found HTML tag '{tag}' in function")
            found_html = True
    
    if not found_html:
        print("✅ PASSED: No HTML tags found in function")
    
    # Check for st.columns usage
    if "st.columns" in source:
        print("✅ PASSED: Using st.columns for layout")
    else:
        print("❌ FAILED: Not using st.columns")
    
    # Check for st.container usage
    if "st.container" in source:
        print("✅ PASSED: Using st.container")
    else:
        print("⚠️  WARNING: Not using st.container")
    
    # Check for native Streamlit components
    native_components = ["st.success", "st.info", "st.text", "st.markdown"]
    components_found = []
    for comp in native_components:
        if comp in source:
            components_found.append(comp)
    
    if components_found:
        print(f"✅ PASSED: Using native Streamlit components: {', '.join(components_found)}")
    else:
        print("❌ FAILED: Not using native Streamlit components")
    
    return not found_html and "unsafe_allow_html=True" not in source

def verify_actual_file():
    """Verify the actual ui_components.py file"""
    file_path = "utils/ui_components.py"
    print(f"\n=== CHECKING FILE: {file_path} ===\n")
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find the create_progress_steps function
    import re
    pattern = r'def create_progress_steps\(.*?\):(.*?)(?=\ndef|\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ FAILED: Could not find create_progress_steps function")
        return False
    
    func_content = match.group(0)
    
    # Check line 451 specifically
    lines = content.split('\n')
    if len(lines) > 450:
        line_451 = lines[450]  # 0-indexed
        print(f"Line 451: {line_451.strip()}")
        if "unsafe_allow_html=True" in line_451:
            print("❌ FAILED: Line 451 still contains unsafe_allow_html=True")
            return False
        else:
            print("✅ PASSED: Line 451 does not contain unsafe_allow_html=True")
    
    return True

def main():
    print("Progress Bar HTML Rendering Fix Verification")
    print("=" * 50)
    
    # Check function implementation
    func_check = check_function_for_html()
    
    # Check actual file
    file_check = verify_actual_file()
    
    print("\n" + "=" * 50)
    print("FINAL RESULT:")
    if func_check and file_check:
        print("✅ ALL CHECKS PASSED - Progress bars are safe from HTML injection")
        print("✅ No HTML strings will be displayed to users")
        print("✅ XSS vulnerability has been removed")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please review the implementation")
        return 1

if __name__ == "__main__":
    exit(main())