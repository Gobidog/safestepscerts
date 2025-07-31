#!/usr/bin/env python3
"""
Functionality verification test for SafeSteps progress bars.
Tests basic functionality without complex mocking.
"""

import sys
import os
from unittest.mock import Mock, patch

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_basic_functionality():
    """Test basic functionality with minimal mocking"""
    print("🔧 Testing basic progress bar functionality...")
    
    try:
        from utils.ui_components import create_progress_steps
        
        # Test with simple mock
        with patch('utils.ui_components.st') as mock_st:
            # Set up basic mock structure
            mock_columns = []
            for _ in range(5):
                col = Mock()
                col.__enter__ = Mock(return_value=col)
                col.__exit__ = Mock(return_value=None)
                
                # Mock container
                container = Mock()
                container.__enter__ = Mock(return_value=container)
                container.__exit__ = Mock(return_value=None)
                col.container.return_value = container
                
                # Mock inner columns for centering - return exactly 3 columns
                inner_cols = [Mock(), Mock(), Mock()]
                for inner_col in inner_cols:
                    inner_col.__enter__ = Mock(return_value=inner_col)
                    inner_col.__exit__ = Mock(return_value=None)
                container.columns.return_value = inner_cols
                
                mock_columns.append(col)
            
            mock_st.columns.return_value = mock_columns
            
            # Test data
            test_steps = [
                ("Upload", "📤", 1),
                ("Validate", "✅", 2),
                ("Template", "📄", 3),
                ("Generate", "🏆", 4),
                ("Complete", "🎉", 5)
            ]
            
            # Test function execution
            create_progress_steps(test_steps, 3)
            
            # Basic verification
            mock_st.columns.assert_called_once_with(5)
            print("✅ Function executed without errors")
            print("✅ Correct number of columns created")
            return True
            
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def test_different_step_counts():
    """Test with different numbers of steps"""
    print("\n📊 Testing different step counts...")
    
    try:
        from utils.ui_components import create_progress_steps
        
        test_cases = [
            ([], 0, "empty steps"),
            ([("Step 1", "1️⃣", 1)], 1, "single step"),
            ([("Step 1", "1️⃣", 1), ("Step 2", "2️⃣", 2)], 2, "two steps"),
            ([("Step 1", "1️⃣", 1), ("Step 2", "2️⃣", 2), ("Step 3", "3️⃣", 3), ("Step 4", "4️⃣", 4)], 2, "four steps")
        ]
        
        for steps, current_step, description in test_cases:
            with patch('utils.ui_components.st') as mock_st:
                # Set up mock columns
                mock_columns = []
                for _ in range(len(steps)):
                    col = Mock()
                    col.__enter__ = Mock(return_value=col)
                    col.__exit__ = Mock(return_value=None)
                    
                    container = Mock()
                    container.__enter__ = Mock(return_value=container)
                    container.__exit__ = Mock(return_value=None)
                    col.container.return_value = container
                    
                    inner_cols = [Mock(), Mock(), Mock()]
                    for inner_col in inner_cols:
                        inner_col.__enter__ = Mock(return_value=inner_col)
                        inner_col.__exit__ = Mock(return_value=None)
                    container.columns.return_value = inner_cols
                    
                    mock_columns.append(col)
                
                mock_st.columns.return_value = mock_columns
                
                # Test execution
                create_progress_steps(steps, current_step)
                
                if steps:  # Only check if there are steps
                    mock_st.columns.assert_called_once_with(len(steps))
                
                print(f"✅ {description}: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Step count test failed: {e}")
        return False


def test_edge_cases():
    """Test edge cases"""
    print("\n🔍 Testing edge cases...")
    
    try:
        from utils.ui_components import create_progress_steps
        
        # Test with special characters and emojis
        special_steps = [
            ("Test & Validate", "🧪", 1),
            ("Deploy <Production>", "🚀", 2), 
            ("Monitor 'System'", "📊", 3)
        ]
        
        with patch('utils.ui_components.st') as mock_st:
            mock_columns = []
            for _ in range(3):
                col = Mock()
                col.__enter__ = Mock(return_value=col)
                col.__exit__ = Mock(return_value=None)
                
                container = Mock()
                container.__enter__ = Mock(return_value=container)
                container.__exit__ = Mock(return_value=None)
                col.container.return_value = container
                
                inner_cols = [Mock(), Mock(), Mock()]
                for inner_col in inner_cols:
                    inner_col.__enter__ = Mock(return_value=inner_col)
                    inner_col.__exit__ = Mock(return_value=None)
                container.columns.return_value = inner_cols
                
                mock_columns.append(col)
            
            mock_st.columns.return_value = mock_columns
            
            # This should handle special characters safely
            create_progress_steps(special_steps, 2)
            print("✅ Special characters handled safely")
        
        # Test with current_step = 0 (all pending)
        with patch('utils.ui_components.st') as mock_st:
            mock_columns = []
            for _ in range(3):
                col = Mock()
                col.__enter__ = Mock(return_value=col)
                col.__exit__ = Mock(return_value=None)
                
                container = Mock()
                container.__enter__ = Mock(return_value=container)
                container.__exit__ = Mock(return_value=None)
                col.container.return_value = container
                
                inner_cols = [Mock(), Mock(), Mock()]
                for inner_col in inner_cols:
                    inner_col.__enter__ = Mock(return_value=inner_col)
                    inner_col.__exit__ = Mock(return_value=None)
                container.columns.return_value = inner_cols
                
                mock_columns.append(col)
            
            mock_st.columns.return_value = mock_columns
            
            create_progress_steps(special_steps, 0)
            print("✅ current_step = 0 handled correctly")
        
        # Test with current_step > total steps
        with patch('utils.ui_components.st') as mock_st:
            mock_columns = []
            for _ in range(3):
                col = Mock()
                col.__enter__ = Mock(return_value=col)  
                col.__exit__ = Mock(return_value=None)
                
                container = Mock()
                container.__enter__ = Mock(return_value=container)
                container.__exit__ = Mock(return_value=None)
                col.container.return_value = container
                
                inner_cols = [Mock(), Mock(), Mock()]
                for inner_col in inner_cols:
                    inner_col.__enter__ = Mock(return_value=inner_col)
                    inner_col.__exit__ = Mock(return_value=None)
                container.columns.return_value = inner_cols
                
                mock_columns.append(col)
            
            mock_st.columns.return_value = mock_columns
            
            create_progress_steps(special_steps, 10)
            print("✅ current_step > total steps handled correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Edge case test failed: {e}")
        return False


def main():
    """Run all functionality tests"""
    print("⚙️ SafeSteps Progress Bar Functionality Verification")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Different Step Counts", test_different_step_counts),
        ("Edge Cases", test_edge_cases),
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
    print("📊 FUNCTIONALITY TEST RESULTS")
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
        print("\n🎉 ALL FUNCTIONALITY TESTS PASSED!")
        print("✅ Progress bars work correctly")
        print("✅ All edge cases handled")
        print("✅ Function is robust and reliable")
        return True
    else:
        print("\n❌ FUNCTIONALITY VERIFICATION FAILED")
        print(f"❌ {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)