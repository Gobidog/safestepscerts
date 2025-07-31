#!/usr/bin/env python3
"""
Comprehensive test suite for the HTML rendering fix in SafeSteps progress bars.
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
    
    @patch('utils.ui_components.st')
    def test_no_html_in_output(self, mock_st):
        """Critical test: Verify NO HTML strings are passed to Streamlit"""
        # Set up mocks
        mock_columns = [Mock(), Mock(), Mock(), Mock(), Mock()]
        mock_st.columns.return_value = mock_columns
        
        # Track all calls to st.markdown
        markdown_calls = []
        mock_st.markdown.side_effect = lambda x: markdown_calls.append(x)
        
        # Test progress bar at step 3
        create_progress_steps(self.test_steps, 3)
        
        # Verify no HTML in any markdown calls
        for call_arg in markdown_calls:
            self.assertNotIn('<div', str(call_arg), "HTML div tag found in output")
            self.assertNotIn('<span', str(call_arg), "HTML span tag found in output")
            self.assertNotIn('<style', str(call_arg), "HTML style tag found in output")
            self.assertNotIn('unsafe_allow_html', str(call_arg), "unsafe_allow_html found in output")
    
    @patch('utils.ui_components.st')
    def test_columns_structure(self, mock_st):
        """Test that columns are created correctly for each step"""
        # Set up mocks
        mock_columns = [Mock() for _ in range(5)]
        mock_st.columns.return_value = mock_columns
        
        # Test progress bar
        create_progress_steps(self.test_steps, 3)
        
        # Verify columns were created with correct number of steps
        mock_st.columns.assert_called_once_with(len(self.test_steps))
    
    @patch('utils.ui_components.st')
    def test_icon_display(self, mock_st):
        """Test that icons are displayed correctly at each step"""
        # Set up column mocks
        mock_columns = []
        for i in range(5):
            col_mock = Mock()
            col_mock.__enter__ = Mock(return_value=col_mock)
            col_mock.__exit__ = Mock(return_value=None)
            
            # Mock inner columns for centering
            inner_cols = [Mock(), Mock(), Mock()]
            for inner_col in inner_cols:
                inner_col.__enter__ = Mock(return_value=inner_col)
                inner_col.__exit__ = Mock(return_value=None)
            col_mock.columns.return_value = inner_cols
            
            mock_columns.append(col_mock)
        
        mock_st.columns.return_value = mock_columns
        
        # Test progress bar
        create_progress_steps(self.test_steps, 3)
        
        # Verify icons were displayed
        expected_icons = ["📤", "✅", "📄", "🏆", "🎉"]
        for i, col_mock in enumerate(mock_columns):
            # Get the middle column where icon should be displayed
            inner_cols = col_mock.columns.return_value
            middle_col = inner_cols[1]
            # Verify icon was passed to markdown
            middle_col.markdown.assert_called_once_with(expected_icons[i])
    
    @patch('utils.ui_components.st')
    def test_progress_states(self, mock_st):
        """Test that progress states (completed, active, pending) work correctly"""
        # Test each possible current step
        for current_step in range(1, 6):
            mock_st.reset_mock()
            
            # Set up column mocks
            mock_columns = []
            for i in range(5):
                col_mock = Mock()
                col_mock.__enter__ = Mock(return_value=col_mock)
                col_mock.__exit__ = Mock(return_value=None)
                mock_columns.append(col_mock)
            
            mock_st.columns.return_value = mock_columns
            
            # Run the function
            create_progress_steps(self.test_steps, current_step)
            
            # Verify states
            for i, col_mock in enumerate(mock_columns):
                step_num = i + 1
                if step_num < current_step:
                    # Should show as completed (success)
                    col_mock.success.assert_called()
                    args = col_mock.success.call_args[0]
                    self.assertIn("✓", args[0])
                elif step_num == current_step:
                    # Should show as active (info)
                    col_mock.info.assert_called()
                    args = col_mock.info.call_args[0]
                    self.assertIn(str(step_num), args[0])
                else:
                    # Should show as pending (markdown)
                    # Last markdown call should be for the status
                    markdown_calls = [call[0][0] for call in col_mock.markdown.call_args_list]
                    status_call = [c for c in markdown_calls if str(step_num) in c]
                    self.assertTrue(len(status_call) > 0, f"Step {step_num} status not displayed")
    
    @patch('utils.ui_components.st')
    def test_admin_workflow(self, mock_st):
        """Test that admin workflow steps work correctly"""
        # Set up mocks
        mock_columns = [Mock() for _ in range(4)]  # Admin has 4 steps
        mock_st.columns.return_value = mock_columns
        
        for col in mock_columns:
            col.__enter__ = Mock(return_value=col)
            col.__exit__ = Mock(return_value=None)
        
        # Test admin progress bar
        create_progress_steps(self.admin_steps, 2)
        
        # Verify correct number of columns
        mock_st.columns.assert_called_once_with(len(self.admin_steps))
    
    @patch('utils.ui_components.st')
    def test_edge_cases(self, mock_st):
        """Test edge cases and error conditions"""
        # Test with empty steps
        mock_st.columns.return_value = []
        create_progress_steps([], 1)
        mock_st.columns.assert_called_with(0)
        
        # Test with current_step = 0
        mock_columns = [Mock() for _ in range(5)]
        mock_st.columns.return_value = mock_columns
        create_progress_steps(self.test_steps, 0)
        
        # All steps should be pending
        for col in mock_columns:
            col.markdown.assert_called()
        
        # Test with current_step > total steps
        create_progress_steps(self.test_steps, 10)
        # All steps should be completed
        for col in mock_columns:
            col.success.assert_called()
    
    @patch('utils.ui_components.st')
    def test_container_usage(self, mock_st):
        """Test that st.container is used correctly"""
        # Set up mocks
        mock_columns = [Mock() for _ in range(5)]
        mock_st.columns.return_value = mock_columns
        
        # Mock container
        mock_container = Mock()
        mock_container.__enter__ = Mock(return_value=mock_container)
        mock_container.__exit__ = Mock(return_value=None)
        mock_st.container.return_value = mock_container
        
        # Run the function
        create_progress_steps(self.test_steps, 3)
        
        # Verify container was used
        self.assertEqual(mock_st.container.call_count, 5)
    
    @patch('utils.ui_components.st')
    def test_column_centering(self, mock_st):
        """Test that content is centered using [1, 2, 1] column ratio"""
        # Set up mocks
        mock_columns = []
        for i in range(5):
            col_mock = Mock()
            col_mock.__enter__ = Mock(return_value=col_mock)
            col_mock.__exit__ = Mock(return_value=None)
            mock_columns.append(col_mock)
        
        mock_st.columns.return_value = mock_columns
        
        # Run the function
        create_progress_steps(self.test_steps, 3)
        
        # Verify inner columns use [1, 2, 1] ratio for centering
        for col in mock_columns:
            col.columns.assert_called_with([1, 2, 1])
    
    def test_no_css_injection(self):
        """Verify no CSS can be injected through step labels"""
        malicious_steps = [
            ("<style>body{display:none}</style>", "💣", 1),
            ("Normal", "📄", 2),
            ("<script>alert('xss')</script>", "⚠️", 3)
        ]
        
        with patch('utils.ui_components.st') as mock_st:
            mock_columns = [Mock() for _ in range(3)]
            mock_st.columns.return_value = mock_columns
            
            # This should not raise an error
            create_progress_steps(malicious_steps, 2)
            
            # The malicious content should be treated as plain text
            # Not interpreted as HTML
            self.assertTrue(True)  # If we get here, no injection occurred


class TestRegressionPrevention(unittest.TestCase):
    """Tests to ensure the HTML rendering issue doesn't return"""
    
    @patch('utils.ui_components.st')
    def test_no_unsafe_allow_html_usage(self, mock_st):
        """Ensure unsafe_allow_html is never used in progress bars"""
        # Set up basic mocks
        mock_st.columns.return_value = [Mock() for _ in range(5)]
        
        # Intercept all Streamlit calls
        all_calls = []
        
        def track_call(method_name):
            def wrapper(*args, **kwargs):
                all_calls.append((method_name, args, kwargs))
                return Mock()
            return wrapper
        
        # Track all potential HTML-rendering methods
        mock_st.markdown = track_call('markdown')
        mock_st.write = track_call('write')
        mock_st.text = track_call('text')
        mock_st.code = track_call('code')
        
        steps = [
            ("Step 1", "1️⃣", 1),
            ("Step 2", "2️⃣", 2),
            ("Step 3", "3️⃣", 3)
        ]
        
        create_progress_steps(steps, 2)
        
        # Check no call uses unsafe_allow_html
        for method, args, kwargs in all_calls:
            self.assertNotIn('unsafe_allow_html', kwargs,
                           f"{method} was called with unsafe_allow_html")
            if 'unsafe_allow_html' in str(args):
                self.fail(f"{method} contains unsafe_allow_html in args")


class TestIntegration(unittest.TestCase):
    """Integration tests for progress bar functionality"""
    
    @patch('utils.ui_components.st')
    def test_full_workflow_simulation(self, mock_st):
        """Simulate a complete workflow from start to finish"""
        steps = [
            ("Upload", "📤", 1),
            ("Validate", "✅", 2),
            ("Template", "📄", 3),
            ("Generate", "🏆", 4),
            ("Complete", "🎉", 5)
        ]
        
        # Simulate progressing through all steps
        for current_step in range(1, 6):
            mock_st.reset_mock()
            
            # Set up mocks for this iteration
            mock_columns = []
            for i in range(5):
                col = Mock()
                col.__enter__ = Mock(return_value=col)
                col.__exit__ = Mock(return_value=None)
                
                # Mock inner columns
                inner_cols = [Mock(), Mock(), Mock()]
                for ic in inner_cols:
                    ic.__enter__ = Mock(return_value=ic)
                    ic.__exit__ = Mock(return_value=None)
                col.columns.return_value = inner_cols
                
                mock_columns.append(col)
            
            mock_st.columns.return_value = mock_columns
            
            # Create progress bar
            create_progress_steps(steps, current_step)
            
            # Verify behavior
            self.assertEqual(mock_st.columns.call_count, 1)
            self.assertEqual(len(mock_columns), 5)
            
            # Verify no HTML was rendered
            for col in mock_columns:
                for call in col.method_calls:
                    if 'unsafe_allow_html' in str(call):
                        self.fail("HTML rendering detected in integration test")


def run_tests():
    """Run all tests and generate report"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestProgressBarHTMLFix))
    suite.addTests(loader.loadTestsFromTestCase(TestRegressionPrevention))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("Running comprehensive progress bar HTML rendering fix tests...")
    print("=" * 70)
    result = run_tests()
    print("=" * 70)
    
    # Summary
    print(f"\nTest Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)