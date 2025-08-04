#!/usr/bin/env python3
"""Test the template name fix directly"""

print("Testing template name comparison fix...")

# Test the exact strings used in the fix
template_stored = "Programmatic Certificate"
template_check_old = "programmatic"  # OLD BROKEN CODE
template_check_new = "Programmatic Certificate"  # NEW FIXED CODE

print(f"\nTemplate stored as: '{template_stored}'")
print(f"OLD code checked for: '{template_check_old}'")
print(f"NEW code checks for: '{template_check_new}'")

print("\nTesting comparisons:")
print(f"OLD: '{template_stored}' == '{template_check_old}' -> {template_stored == template_check_old} ❌")
print(f"NEW: '{template_stored}' == '{template_check_new}' -> {template_stored == template_check_new} ✅")

# Check the actual lines in app.py
print("\nVerifying the fix in app.py...")
with open("app.py", "r") as f:
    content = f.read()
    lines = content.split('\n')
    
    # Check line 815
    if len(lines) > 814:
        line_815 = lines[814].strip()
        if 'if st.session_state.selected_template == "Programmatic Certificate":' in line_815:
            print("✅ Line 815: Fixed correctly")
        else:
            print(f"❌ Line 815: NOT FIXED - Current: {line_815}")
    
    # Check line 2157  
    if len(lines) > 2156:
        line_2157 = lines[2156].strip()
        if 'if template_name == "Programmatic Certificate":' in line_2157:
            print("✅ Line 2157: Fixed correctly")
        else:
            print(f"❌ Line 2157: NOT FIXED - Current: {line_2157}")
            
print("\nFix verification complete!")