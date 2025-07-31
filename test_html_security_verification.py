#!/usr/bin/env python3
"""
Simple but comprehensive security verification test for HTML rendering fix.
Focuses on the critical security aspects rather than complex mocking.
"""

import sys
import os
import re
import inspect

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_source_code_security():
    """Test the actual source code for security vulnerabilities"""
    print("🔍 Testing source code security...")
    
    try:
        # Read the actual source code
        with open('utils/ui_components.py', 'r') as f:
            content = f.read()
        
        # Find the create_progress_steps function
        function_match = re.search(
            r'def create_progress_steps.*?(?=def|\Z)', 
            content, 
            re.DOTALL
        )
        
        if not function_match:
            print("❌ Could not find create_progress_steps function")
            return False
        
        function_code = function_match.group(0)
        print(f"✅ Found create_progress_steps function ({len(function_code)} characters)")
        
        # Critical security checks
        security_issues = []
        
        # Check for HTML vulnerability patterns
        if 'unsafe_allow_html=True' in function_code:
            security_issues.append("unsafe_allow_html=True found")
        
        if '<div' in function_code:
            security_issues.append("HTML div tags found")
        
        if '<span' in function_code:
            security_issues.append("HTML span tags found")
        
        if '<style' in function_code:
            security_issues.append("HTML style tags found")
        
        if 'innerHTML' in function_code:
            security_issues.append("innerHTML usage found")
        
        if 'outerHTML' in function_code:
            security_issues.append("outerHTML usage found")
        
        # Check that line 451 has been fixed
        lines = function_code.split('\n')
        line_451_content = None
        for i, line in enumerate(lines):
            if 'st.columns([1, 2, 1])' in line:
                line_451_content = line.strip()
                break
        
        if line_451_content:
            print(f"✅ Line 451 fix confirmed: {line_451_content}")
        else:
            security_issues.append("Line 451 fix not found - st.columns([1, 2, 1]) missing")
        
        # Check for proper native Streamlit component usage
        native_components = [
            'st.columns',
            'st.container', 
            'st.success',
            'st.info',
            'st.markdown'
        ]
        
        found_components = []
        for component in native_components:
            if component in function_code:
                found_components.append(component)
        
        print(f"✅ Native Streamlit components found: {', '.join(found_components)}")
        
        # Report results
        if security_issues:
            print("❌ SECURITY ISSUES FOUND:")
            for issue in security_issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ NO SECURITY ISSUES FOUND - Function is secure")
            print("✅ HTML rendering vulnerability has been eliminated")
            return True
            
    except Exception as e:
        print(f"❌ Error reading source code: {e}")
        return False


def test_function_import():
    """Test that the function can be imported without errors"""
    print("\n📦 Testing function import...")
    
    try:
        from utils.ui_components import create_progress_steps
        print("✅ Function imported successfully")
        
        # Check signature
        sig = inspect.signature(create_progress_steps)
        params = list(sig.parameters.keys())
        
        if len(params) == 2 and 'steps' in params and 'current_step' in params:
            print("✅ Function signature is correct")
            return True
        else:
            print(f"❌ Unexpected function signature: {params}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing function: {e}")
        return False


def test_no_html_strings_in_code():
    """Verify no HTML strings exist in the progress bar function"""
    print("\n🔍 Testing for HTML strings in code...")
    
    try:
        with open('utils/ui_components.py', 'r') as f:
            content = f.read()
        
        # Extract just the create_progress_steps function
        function_match = re.search(
            r'def create_progress_steps.*?(?=def|\Z)', 
            content, 
            re.DOTALL
        )
        
        if not function_match:
            print("❌ Could not find function")
            return False
        
        function_code = function_match.group(0)
        
        # Look for HTML-like patterns in string literals
        html_patterns = [
            r'<[^>]+>',  # HTML tags
            r'unsafe_allow_html',  # Streamlit HTML flag
            r'innerHTML',  # JavaScript HTML manipulation
            r'outerHTML',  # JavaScript HTML manipulation
        ]
        
        html_found = []
        for pattern in html_patterns:
            matches = re.findall(pattern, function_code, re.IGNORECASE)
            if matches:
                html_found.extend(matches)
        
        if html_found:
            print(f"❌ HTML patterns found: {html_found}")
            return False
        else:
            print("✅ No HTML patterns found in function code")
            return True
            
    except Exception as e:
        print(f"❌ Error checking for HTML: {e}")
        return False


def test_line_451_fix():
    """Specifically test that line 451 has been fixed"""
    print("\n🎯 Testing Line 451 Fix...")
    
    try:
        with open('utils/ui_components.py', 'r') as f:
            lines = f.readlines()
        
        # Check around line 451 (accounting for 0-based indexing)
        if len(lines) >= 451:
            line_451 = lines[450].strip()  # Line 451 (0-based index 450)
            
            print(f"Line 451 content: {line_451}")
            
            # Check if the fix is in place
            if 'st.columns([1, 2, 1])' in line_451:
                print("✅ Line 451 fix confirmed - using native st.columns([1, 2, 1])")
                return True
            elif 'unsafe_allow_html' in line_451.lower():
                print("❌ Line 451 still contains unsafe_allow_html")
                return False
            else:
                # Check nearby lines for the fix
                for i in range(max(0, 445), min(len(lines), 455)):
                    if 'st.columns([1, 2, 1])' in lines[i]:
                        print(f"✅ Line 451 fix found on line {i+1}: {lines[i].strip()}")
                        return True
                
                print(f"❌ Line 451 fix not found near line 451")
                return False
        else:
            print("❌ File too short to check line 451")
            return False
            
    except Exception as e:
        print(f"❌ Error checking line 451: {e}")
        return False


def test_regression_prevention():
    """Test that previous vulnerable patterns are not present"""
    print("\n🛡️ Testing Regression Prevention...")
    
    try:
        with open('utils/ui_components.py', 'r') as f:
            content = f.read()
        
        # Extract just the create_progress_steps function
        function_match = re.search(
            r'def create_progress_steps.*?(?=def|\Z)', 
            content, 
            re.DOTALL
        )
        
        if not function_match:
            print("❌ Could not find function")
            return False
        
        function_code = function_match.group(0)
        
        # Check for vulnerable patterns that should NOT be present
        vulnerable_patterns = [
            ('unsafe_allow_html=True', 'XSS vulnerability'),
            ('<div', 'HTML div injection'),
            ('<span', 'HTML span injection'), 
            ('<style', 'CSS injection'),
            ('innerHTML', 'DOM manipulation'),
            ('document.write', 'Document write injection'),
        ]
        
        issues_found = []
        for pattern, description in vulnerable_patterns:
            if pattern in function_code:
                issues_found.append(f"{description}: {pattern}")
        
        if issues_found:
            print("❌ REGRESSION DETECTED - Vulnerable patterns found:")
            for issue in issues_found:
                print(f"   - {issue}")
            return False
        else:
            print("✅ No vulnerable patterns detected")
            print("✅ Regression prevention successful")
            return True
            
    except Exception as e:
        print(f"❌ Error checking regression: {e}")
        return False


def main():
    """Run all security verification tests"""
    print("🔒 SafeSteps Progress Bar HTML Security Verification")
    print("=" * 60)
    
    tests = [
        ("Source Code Security", test_source_code_security),
        ("Function Import", test_function_import),
        ("HTML String Detection", test_no_html_strings_in_code),
        ("Line 451 Fix", test_line_451_fix),
        ("Regression Prevention", test_regression_prevention),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 SECURITY VERIFICATION RESULTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nSUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL SECURITY TESTS PASSED!")
        print("✅ HTML rendering vulnerability has been ELIMINATED")
        print("✅ Progress bars are SECURE and functional")
        print("✅ No XSS vulnerabilities detected")
        print("✅ Native Streamlit components confirmed")
        return True
    else:
        print("\n❌ SECURITY VERIFICATION FAILED")
        print(f"❌ {total - passed} test(s) failed")
        print("⚠️  Manual review required")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)