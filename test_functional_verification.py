#!/usr/bin/env python3
"""
Functional verification test for the progress bar fix.
Tests that the function works correctly after the HTML rendering fix.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import Mock, patch, MagicMock
from utils.ui_components import create_progress_steps


def test_function_executes_without_errors():
    """Test that the function runs without throwing errors"""
    print("🧪 Testing function execution...")
    
    test_steps = [
        ("Upload", "📤", 1),
        ("Validate", "✅", 2),
        ("Template", "📄", 3),
        ("Generate", "🏆", 4),
        ("Complete", "🎉", 5)
    ]
    
    try:
        with patch('utils.ui_components.st') as mock_st:
            # Set up proper mocks
            mock_columns = []
            for i in range(5):
                col = MagicMock()
                mock_columns.append(col)
            
            mock_st.columns.return_value = mock_columns
            
            # Mock inner columns for centering
            inner_mock_columns = [MagicMock(), MagicMock(), MagicMock()]
            mock_st.columns.side_effect = [mock_columns, inner_mock_columns, inner_mock_columns, inner_mock_columns, inner_mock_columns, inner_mock_columns]
            
            # Mock container
            mock_container = MagicMock()
            mock_st.container.return_value = mock_container
            
            # Test different current steps
            for current_step in [1, 3, 5]:
                print(f"  Testing current_step = {current_step}...")
                create_progress_steps(test_steps, current_step)
                print(f"  ✅ current_step = {current_step} executed successfully")
        
        print("✅ Function executes without errors")
        return True
        
    except Exception as e:
        print(f"❌ Function execution failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases to ensure robustness"""
    print("\n🔍 Testing edge cases...")
    
    try:
        with patch('utils.ui_components.st') as mock_st:
            # Set up mocks
            mock_st.columns.return_value = []
            mock_st.container.return_value = MagicMock()
            
            # Test empty steps
            create_progress_steps([], 1)
            print("  ✅ Empty steps handled correctly")
            
            # Test single step
            mock_st.columns.return_value = [MagicMock()]
            create_progress_steps([("Single", "⭐", 1)], 1)
            print("  ✅ Single step handled correctly")
            
            # Test special characters in labels
            special_steps = [
                ("Test & Verify", "🧪", 1),
                ("Save <Data>", "💾", 2),
                ("Process 'Quotes'", "⚙️", 3)
            ]
            mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
            create_progress_steps(special_steps, 2)
            print("  ✅ Special characters handled correctly")
        
        print("✅ All edge cases handled correctly")
        return True
        
    except Exception as e:
        print(f"❌ Edge case testing failed: {e}")
        return False


def test_no_html_output():
    """Verify that no HTML content is generated"""
    print("\n🔒 Testing for HTML output...")
    
    try:
        with patch('utils.ui_components.st') as mock_st:
            # Capture all calls to potentially HTML-rendering methods
            html_calls = []
            
            def capture_call(method_name):
                def wrapper(*args, **kwargs):
                    html_calls.append((method_name, args, kwargs))
                    return MagicMock()
                return wrapper
            
            # Mock columns to return proper context managers
            mock_columns = []
            for i in range(5):
                col = MagicMock()
                mock_columns.append(col)
            
            mock_st.columns.return_value = mock_columns
            
            # Set up inner columns
            inner_cols = [MagicMock(), MagicMock(), MagicMock()]
            for col in mock_columns:
                col.columns.return_value = inner_cols
            
            # Capture HTML-related calls
            mock_st.markdown.side_effect = capture_call('markdown')
            mock_st.write.side_effect = capture_call('write')
            
            test_steps = [
                ("Upload", "📤", 1),
                ("Process", "⚙️", 2),
                ("Complete", "✅", 3)
            ]
            
            create_progress_steps(test_steps, 2)
            
            # Check for HTML in captured calls
            html_found = False
            for method, args, kwargs in html_calls:
                # Check for unsafe_allow_html parameter
                if 'unsafe_allow_html' in kwargs:
                    html_found = True
                    print(f"❌ Found unsafe_allow_html in {method}")
                
                # Check for HTML tags in arguments
                for arg in args:
                    if isinstance(arg, str) and ('<' in arg and '>' in arg):
                        html_found = True
                        print(f"❌ Found HTML-like content in {method}: {arg}")
            
            if not html_found:
                print("✅ No HTML content detected in output")
                return True
            else:
                print("❌ HTML content detected in output")
                return False
        
    except Exception as e:
        print(f"❌ HTML testing failed: {e}")
        return False


def main():
    """Run all functional verification tests"""
    print("⚙️ SafeSteps Progress Bar Functional Verification")
    print("=" * 55)
    
    tests = [
        ("Function Execution", test_function_executes_without_errors),
        ("Edge Cases", test_edge_cases),
        ("HTML Output Check", test_no_html_output),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 55)
    print("📊 FUNCTIONAL VERIFICATION RESULTS")
    print("=" * 55)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nSUMMARY: {passed}/{total} functional tests passed")
    
    if passed == total:
        print("\n🎉 ALL FUNCTIONAL TESTS PASSED!")
        print("✅ Progress bars are fully functional")
        print("✅ No errors in execution")
        print("✅ Edge cases handled properly")
        return True
    else:
        print("\n❌ FUNCTIONAL VERIFICATION FAILED")
        print(f"❌ {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)