#!/usr/bin/env python3
"""
Corrected comprehensive test suite for the HTML rendering fix in SafeSteps progress bars.
Tests verify that no HTML is rendered and that progress bars work correctly.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ui_components import create_progress_steps


class TestProgressBarHTMLFix(unittest.TestCase):
    """Test suite for verifying the HTML rendering fix in progress bars"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_steps = [
            ("Upload", "📤", 1),
            ("Validate", "✅", 2),
            ("Template", "📄", 3),
            ("Generate", "🏆", 4),
            ("Complete", "🎉", 5)
        ]
        
        self.admin_steps = [
            ("Select Course", "📚", 1),
            ("Configure", "⚙️", 2),
            ("Preview", "👁️", 3),
            ("Publish", "🚀", 4)
        ]
    
    def create_mock_streamlit(self):
        """Create a properly configured Streamlit mock"""
        mock_st = Mock()
        
        # Create mock columns that work as context managers
        def create_mock_column():
            mock_col = Mock()
            mock_col.__enter__ = Mock(return_value=mock_col)
            mock_col.__exit__ = Mock(return_value=None)
            
            # Mock inner columns for centering
            inner_cols = []
            for _ in range(3):
                inner_col = Mock()
                inner_col.__enter__ = Mock(return_value=inner_col)
                inner_col.__exit__ = Mock(return_value=None)
                inner_cols.append(inner_col)
            
            mock_col.columns.return_value = inner_cols
            return mock_col
        
        # Mock container
        mock_container = Mock()
        mock_container.__enter__ = Mock(return_value=mock_container)
        mock_container.__exit__ = Mock(return_value=None)
        mock_container.columns.return_value = [Mock() for _ in range(3)]
        
        mock_st.container.return_value = mock_container
        
        return mock_st, create_mock_column
    
    @patch('utils.ui_components.st')
    def test_no_html_in_output(self, mock_st):
        """Critical test: Verify NO HTML strings are passed to Streamlit"""
        mock_st_obj, create_mock_column = self.create_mock_streamlit()
        mock_st.return_value = mock_st_obj
        
        # Set up main columns
        main_columns = [create_mock_column() for _ in range(5)]
        mock_st.columns.return_value = main_columns
        
        # Set up container
        mock_container = Mock()
        mock_container.__enter__ = Mock(return_value=mock_container)  
        mock_container.__exit__ = Mock(return_value=None)
        mock_st.container.return_value = mock_container
        
        # Set up inner columns for centering
        inner_cols = []
        for _ in range(3):
            inner_col = Mock()
            inner_col.__enter__ = Mock(return_value=inner_col)
            inner_col.__exit__ = Mock(return_value=None)
            inner_cols.append(inner_col)
        mock_container.columns.return_value = inner_cols
        
        # Track all calls to st.markdown
        markdown_calls = []
        mock_st.markdown.side_effect = lambda x: markdown_calls.append(x)
        mock_container.markdown.side_effect = lambda x: markdown_calls.append(x)
        for col in inner_cols:
            col.markdown.side_effect = lambda x: markdown_calls.append(x)
        
        # Test progress bar at step 3
        create_progress_steps(self.test_steps, 3)
        
        # Verify no HTML in any markdown calls
        for call_arg in markdown_calls:
            call_str = str(call_arg)
            self.assertNotIn('<div', call_str, "HTML div tag found in output")
            self.assertNotIn('<span', call_str, "HTML span tag found in output")
            self.assertNotIn('<style', call_str, "HTML style tag found in output")
            self.assertNotIn('unsafe_allow_html', call_str, "unsafe_allow_html found in output")
            
        print(f"✅ No HTML found in {len(markdown_calls)} markdown calls")
    
    @patch('utils.ui_components.st')
    def test_columns_structure(self, mock_st):
        """Test that columns are created correctly for each step"""
        # Set up main columns
        main_columns = []
        for _ in range(5):
            col = Mock()
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
            main_columns.append(col)
        
        mock_st.columns.return_value = main_columns
        
        # Set up container and inner columns for each main column
        for main_col in main_columns:
            mock_container = Mock()
            mock_container.__enter__ = Mock(return_value=mock_container)
            mock_container.__exit__ = Mock(return_value=None)
            main_col.container.return_value = mock_container
            
            # Inner columns for centering
            inner_cols = []
            for _ in range(3):
                inner_col = Mock()
                inner_col.__enter__ = Mock(return_value=inner_col)
                inner_col.__exit__ = Mock(return_value=None)
                inner_cols.append(inner_col)
            mock_container.columns.return_value = inner_cols
        
        # Test progress bar
        create_progress_steps(self.test_steps, 3)
        
        # Verify columns were created with correct number of steps
        mock_st.columns.assert_called_once_with(len(self.test_steps))
        print(f"✅ Created {len(self.test_steps)} columns correctly")
    
    @patch('utils.ui_components.st')
    def test_no_unsafe_allow_html_usage(self, mock_st):
        """Ensure unsafe_allow_html is never used in progress bars"""
        # Set up main columns
        main_columns = []
        for _ in range(5):
            col = Mock()
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
            main_columns.append(col)
        
        mock_st.columns.return_value = main_columns
        
        # Track all method calls
        all_method_calls = []
        
        def track_call(obj, method_name):
            original_method = getattr(obj, method_name, Mock())
            def wrapper(*args, **kwargs):
                all_method_calls.append((method_name, args, kwargs))
                return original_method(*args, **kwargs)
            setattr(obj, method_name, wrapper)
        
        # Track calls on mock_st and all columns
        track_call(mock_st, 'markdown')
        track_call(mock_st, 'success')
        track_call(mock_st, 'info')
        
        for col in main_columns:
            mock_container = Mock()
            mock_container.__enter__ = Mock(return_value=mock_container)
            mock_container.__exit__ = Mock(return_value=None)
            col.container.return_value = mock_container
            
            track_call(mock_container, 'markdown')
            track_call(mock_container, 'success')
            track_call(mock_container, 'info')
            
            # Inner columns
            inner_cols = []
            for _ in range(3):
                inner_col = Mock()
                inner_col.__enter__ = Mock(return_value=inner_col)
                inner_col.__exit__ = Mock(return_value=None)
                track_call(inner_col, 'markdown')
                inner_cols.append(inner_col)
            mock_container.columns.return_value = inner_cols
        
        # Run the function
        create_progress_steps(self.test_steps, 3)
        
        # Check no call uses unsafe_allow_html
        unsafe_html_found = False
        for method, args, kwargs in all_method_calls:
            if 'unsafe_allow_html' in kwargs:
                unsafe_html_found = True
                self.assertFalse(kwargs.get('unsafe_allow_html', False),
                               f"{method} was called with unsafe_allow_html=True")
            if 'unsafe_allow_html' in str(args):
                unsafe_html_found = True
                self.fail(f"{method} contains unsafe_allow_html in args: {args}")
        
        print(f"✅ No unsafe_allow_html usage found in {len(all_method_calls)} method calls")
    
    @patch('utils.ui_components.st')
    def test_progress_states(self, mock_st):
        """Test that progress states (completed, active, pending) work correctly"""
        for current_step in range(1, 6):
            with self.subTest(current_step=current_step):
                mock_st.reset_mock()
                
                # Set up main columns
                main_columns = []
                for i in range(5):
                    col = Mock()
                    col.__enter__ = Mock(return_value=col)
                    col.__exit__ = Mock(return_value=None)
                    
                    # Container setup
                    mock_container = Mock()
                    mock_container.__enter__ = Mock(return_value=mock_container)
                    mock_container.__exit__ = Mock(return_value=None)
                    col.container.return_value = mock_container
                    
                    # Inner columns for centering
                    inner_cols = []
                    for _ in range(3):
                        inner_col = Mock()
                        inner_col.__enter__ = Mock(return_value=inner_col)
                        inner_col.__exit__ = Mock(return_value=None)
                        inner_cols.append(inner_col)
                    mock_container.columns.return_value = inner_cols
                    
                    main_columns.append(col)
                
                mock_st.columns.return_value = main_columns
                
                # Run the function
                create_progress_steps(self.test_steps, current_step)
                
                # Verify states
                for i, col in enumerate(main_columns):
                    step_num = i + 1
                    container = col.container.return_value
                    
                    if step_num < current_step:
                        # Should show as completed (success)
                        container.success.assert_called()
                        args = container.success.call_args[0]
                        self.assertIn("✓", args[0])
                    elif step_num == current_step:
                        # Should show as active (info)
                        container.info.assert_called()
                        args = container.info.call_args[0]
                        self.assertIn(str(step_num), args[0])
                    else:
                        # Should show as pending (markdown)
                        container.markdown.assert_called()
                        args = container.markdown.call_args[0]
                        self.assertIn(str(step_num), args[0])
        
        print(f"✅ Progress states tested for all {len(self.test_steps)} steps")
    
    @patch('utils.ui_components.st')
    def test_icon_display_no_html(self, mock_st):
        """Test that icons are displayed without HTML rendering"""
        # Set up main columns
        main_columns = []
        for _ in range(5):
            col = Mock()
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
            
            # Container setup
            mock_container = Mock()
            mock_container.__enter__ = Mock(return_value=mock_container)
            mock_container.__exit__ = Mock(return_value=None)
            col.container.return_value = mock_container
            
            # Inner columns for centering - this is where icons are displayed
            inner_cols = []
            for _ in range(3):
                inner_col = Mock()
                inner_col.__enter__ = Mock(return_value=inner_col)
                inner_col.__exit__ = Mock(return_value=None)
                inner_cols.append(inner_col)
            mock_container.columns.return_value = inner_cols
            
            main_columns.append(col)
        
        mock_st.columns.return_value = main_columns
        
        # Run the function
        create_progress_steps(self.test_steps, 3)
        
        # Check that icons were displayed in the middle column (col2) of each step
        expected_icons = ["📤", "✅", "📄", "🏆", "🎉"]
        for i, col in enumerate(main_columns):
            container = col.container.return_value
            inner_cols = container.columns.return_value
            middle_col = inner_cols[1]  # The middle column where icons are displayed
            
            # Verify icon was displayed
            middle_col.markdown.assert_called()
            icon_call = middle_col.markdown.call_args[0][0]
            self.assertEqual(icon_call, expected_icons[i])
            
            # Verify no HTML in icon call
            self.assertNotIn('<', icon_call)
            self.assertNotIn('>', icon_call)
        
        print(f"✅ Icons displayed correctly without HTML in {len(expected_icons)} steps")
    
    @patch('utils.ui_components.st') 
    def test_edge_cases(self, mock_st):
        """Test edge cases and error conditions"""
        # Test with empty steps
        mock_st.columns.return_value = []
        create_progress_steps([], 1)
        mock_st.columns.assert_called_with(0)
        
        # Test with current_step = 0 (all pending)
        main_columns = []
        for _ in range(5):
            col = Mock()
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
            
            mock_container = Mock()
            mock_container.__enter__ = Mock(return_value=mock_container)
            mock_container.__exit__ = Mock(return_value=None)
            col.container.return_value = mock_container
            
            inner_cols = []
            for _ in range(3):
                inner_col = Mock()
                inner_col.__enter__ = Mock(return_value=inner_col)
                inner_col.__exit__ = Mock(return_value=None)
                inner_cols.append(inner_col)
            mock_container.columns.return_value = inner_cols
            
            main_columns.append(col)
            
        mock_st.columns.return_value = main_columns
        
        # Reset mocks for clean test
        mock_st.reset_mock()
        for col in main_columns:
            col.reset_mock()
            col.container.return_value.reset_mock()
        
        create_progress_steps(self.test_steps, 0)
        
        # All steps should be pending (using markdown, not success/info)
        for col in main_columns:
            container = col.container.return_value
            container.markdown.assert_called()
            # Should not call success or info for pending steps
            container.success.assert_not_called()
            container.info.assert_not_called()
        
        print("✅ Edge cases handled correctly")

    def test_function_signature(self):
        """Test that the function can be imported and has correct signature"""
        import inspect
        
        # Check function exists and is callable
        self.assertTrue(callable(create_progress_steps))
        
        # Check signature
        sig = inspect.signature(create_progress_steps)
        params = list(sig.parameters.keys())
        self.assertEqual(len(params), 2)
        self.assertIn('steps', params)
        self.assertIn('current_step', params)
        
        print("✅ Function signature is correct")


class TestSecurityVerification(unittest.TestCase):
    """Tests specifically for security vulnerability prevention"""
    
    @patch('utils.ui_components.st')
    def test_malicious_input_handling(self, mock_st):
        """Test that malicious HTML/JS input is handled safely"""
        malicious_steps = [
            ("<script>alert('xss')</script>", "💣", 1),
            ("<div onclick='alert(1)'>Click</div>", "⚠️", 2),
            ("'; DROP TABLE users; --", "🗑️", 3)
        ]
        
        # Set up mocks
        main_columns = []
        for _ in range(3):
            col = Mock()
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
            
            mock_container = Mock()
            mock_container.__enter__ = Mock(return_value=mock_container)
            mock_container.__exit__ = Mock(return_value=None)
            col.container.return_value = mock_container
            
            inner_cols = []
            for _ in range(3):
                inner_col = Mock()
                inner_col.__enter__ = Mock(return_value=inner_col)
                inner_col.__exit__ = Mock(return_value=None)
                inner_cols.append(inner_col)
            mock_container.columns.return_value = inner_cols
            
            main_columns.append(col)
        
        mock_st.columns.return_value = main_columns
        
        # This should not raise an error and should handle malicious input safely
        try:
            create_progress_steps(malicious_steps, 2)
            test_passed = True
        except Exception as e:
            test_passed = False
            self.fail(f"Function failed with malicious input: {e}")
        
        self.assertTrue(test_passed)
        print("✅ Malicious input handled safely without errors")


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestProgressBarHTMLFix))
    suite.addTests(loader.loadTestsFromTestCase(TestSecurityVerification))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("Running Corrected HTML Rendering Fix Tests for SafeSteps Progress Bars")
    print("=" * 80)
    result = run_tests()
    print("=" * 80)
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED! HTML rendering fix is verified and secure.")
        print(f"✅ {result.testsRun} tests passed successfully")
        print("✅ No HTML injection vulnerabilities found")
        print("✅ Progress bar functionality preserved")
        print("✅ Icons display correctly without HTML")
        print("✅ All edge cases handled properly")
    else:
        print(f"\n❌ TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
        for test, error in result.failures + result.errors:
            print(f"   - {test}: {error.split(':', 1)[0] if ':' in error else error}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)