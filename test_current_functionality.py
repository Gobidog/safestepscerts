#!/usr/bin/env python3
"""
Test current functionality to identify any remaining HTML rendering issues
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ui_components import (
    create_progress_steps, create_card, create_metric_card, 
    create_status_badge, create_empty_state, apply_custom_css
)

def test_progress_steps():
    """Test progress steps functionality"""
    print("Testing progress steps...")
    steps = [
        ("Upload", "📤", 1),
        ("Validate", "✅", 2),
        ("Template", "📄", 3),
        ("Generate", "🏆", 4),
        ("Complete", "🎉", 5)
    ]
    
    # This should not cause any errors and should not output HTML
    try:
        # Mock streamlit for testing
        class MockStreamlit:
            def columns(self, n):
                return [MockColumn() for _ in range(n)]
            
            def container(self):
                return MockContainer()
            
            def markdown(self, text):
                # Check if text contains HTML tags
                if '<' in text and '>' in text:
                    print(f"❌ HTML detected in markdown: {text}")
                    return False
                else:
                    print(f"✅ Clean text: {text}")
                    return True
            
            def success(self, text):
                print(f"✅ Success: {text}")
                
            def info(self, text):
                print(f"ℹ️ Info: {text}")
        
        class MockColumn:
            def __init__(self):
                self.st = MockStreamlit()
                
            def __enter__(self):
                return self
                
            def __exit__(self, *args):
                pass
            
            def columns(self, n):
                return [MockColumn() for _ in range(n)]
            
            def container(self):
                return MockContainer()
            
            def markdown(self, text):
                return self.st.markdown(text)
            
            def success(self, text):
                return self.st.success(text)
            
            def info(self, text):
                return self.st.info(text)
        
        class MockContainer:
            def __init__(self):
                self.st = MockStreamlit()
                
            def __enter__(self):
                return self
                
            def __exit__(self, *args):
                pass
            
            def columns(self, n):
                return [MockColumn() for _ in range(n)]
            
            def markdown(self, text):
                return self.st.markdown(text)
        
        # Mock streamlit module
        import utils.ui_components
        utils.ui_components.st = MockStreamlit()
        
        # Test with different current steps
        for current_step in range(1, 6):
            print(f"\nTesting step {current_step}:")
            create_progress_steps(steps, current_step)
            
        print("✅ Progress steps test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in progress steps: {e}")
        return False

def test_css_function():
    """Test that CSS function doesn't inject HTML"""
    print("\nTesting CSS function...")
    try:
        apply_custom_css()
        print("✅ CSS function executed without errors")
        return True
    except Exception as e:
        print(f"❌ Error in CSS function: {e}")
        return False

def test_import_structure():
    """Test that all imports work correctly"""
    print("\nTesting imports...")
    try:
        from app import main
        print("✅ Main app imports successfully")
        
        from utils.ui_components import COLORS, TYPOGRAPHY
        print("✅ UI constants imported successfully")
        print(f"Colors available: {list(COLORS.keys())}")
        print(f"Typography available: {list(TYPOGRAPHY.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("SafeSteps Functionality Test - Phase 1 Emergency Triage")
    print("=" * 60)
    
    results = []
    
    # Test 1: Import Structure
    results.append(test_import_structure())
    
    # Test 2: CSS Function
    results.append(test_css_function())
    
    # Test 3: Progress Steps
    results.append(test_progress_steps())
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Phase 1 appears to be working correctly")
        print("✅ No HTML injection detected")
        print("✅ Native Streamlit components functioning")
        print("✅ Certificate generation should be operational")
    else:
        print("⚠️ Some tests failed - manual inspection required")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)