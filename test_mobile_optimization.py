#!/usr/bin/env python3
"""
Test Mobile Optimization Implementation
Comprehensive testing of mobile features and touch targets
"""

import sys
import streamlit as st
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_mobile_imports():
    """Test that mobile optimization modules can be imported"""
    print("Testing mobile optimization imports...")
    try:
        from utils.mobile_optimization import (
            MobileDetector, ResponsiveLayout, TouchTargetOptimizer,
            MobileNavigation, MobileGestures, MobileOptimizer,
            apply_global_mobile_optimizations, create_mobile_button,
            get_device_info, is_mobile, create_responsive_columns
        )
        print("✅ All mobile optimization classes imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_mobile_detector():
    """Test mobile device detection functionality"""
    print("\nTesting mobile device detection...")
    try:
        from utils.mobile_optimization import MobileDetector
        
        detector = MobileDetector()
        device_info = detector.get_device_info()
        
        print(f"Device info: {device_info}")
        print(f"Is mobile: {device_info.get('is_mobile', 'Unknown')}")
        print(f"Is tablet: {device_info.get('is_tablet', 'Unknown')}")
        print(f"Is desktop: {device_info.get('is_desktop', 'Unknown')}")
        
        print("✅ Mobile detection working")
        return True
    except Exception as e:
        print(f"❌ Mobile detection error: {e}")
        return False

def test_touch_targets():
    """Test touch target optimization"""
    print("\nTesting touch target optimization...")
    try:
        from utils.mobile_optimization import TouchTargetOptimizer
        
        optimizer = TouchTargetOptimizer()
        
        # Test minimum sizes
        assert optimizer.MIN_TOUCH_TARGET == 44, f"Expected 44px minimum, got {optimizer.MIN_TOUCH_TARGET}"
        assert optimizer.RECOMMENDED_TARGET == 48, f"Expected 48px recommended, got {optimizer.RECOMMENDED_TARGET}"
        assert optimizer.LARGE_TARGET == 56, f"Expected 56px large, got {optimizer.LARGE_TARGET}"
        
        print(f"✅ Touch target sizes correct:")
        print(f"  - Minimum: {optimizer.MIN_TOUCH_TARGET}px")
        print(f"  - Recommended: {optimizer.RECOMMENDED_TARGET}px")
        print(f"  - Large: {optimizer.LARGE_TARGET}px")
        
        return True
    except Exception as e:
        print(f"❌ Touch target error: {e}")
        return False

def test_responsive_layout():
    """Test responsive layout functionality"""
    print("\nTesting responsive layout...")
    try:
        from utils.mobile_optimization import ResponsiveLayout
        
        layout = ResponsiveLayout()
        
        # Test responsive columns
        mobile_cols = [1]
        tablet_cols = [1, 1] 
        desktop_cols = [1, 1, 1]
        
        result_cols = layout.get_responsive_columns(mobile_cols, tablet_cols, desktop_cols)
        print(f"Responsive columns result: {result_cols}")
        
        # Should return one of the input configurations
        assert result_cols in [mobile_cols, tablet_cols, desktop_cols], "Invalid column configuration returned"
        
        print("✅ Responsive layout working")
        return True
    except Exception as e:
        print(f"❌ Responsive layout error: {e}")
        return False

def test_mobile_navigation():
    """Test mobile navigation components"""
    print("\nTesting mobile navigation...")
    try:
        from utils.mobile_optimization import MobileNavigation
        
        nav = MobileNavigation()
        
        # Test bottom navigation
        nav_items = [
            {'key': 'home', 'label': 'Home', 'icon': '🏠', 'active': True},
            {'key': 'generate', 'label': 'Generate', 'icon': '🏆'},
            {'key': 'account', 'label': 'Account', 'icon': '👤'}
        ]
        
        bottom_nav_html = nav.create_bottom_nav(nav_items)
        assert 'bottom-nav' in bottom_nav_html, "Bottom nav HTML should contain bottom-nav class"
        assert 'nav-item' in bottom_nav_html, "Bottom nav HTML should contain nav-item elements"
        
        # Test floating action button
        fab_html = nav.create_floating_action_button()
        assert 'floating-action-button' in fab_html, "FAB HTML should contain floating-action-button class"
        
        # Test hamburger menu
        menu_items = [
            {'action': 'settings', 'label': 'Settings', 'icon': '⚙️'},
            {'action': 'help', 'label': 'Help', 'icon': '❓'}
        ]
        
        hamburger_html = nav.create_hamburger_menu(menu_items)
        assert 'hamburger-menu' in hamburger_html, "Hamburger HTML should contain hamburger-menu class"
        
        print("✅ Mobile navigation components working")
        return True
    except Exception as e:
        print(f"❌ Mobile navigation error: {e}")
        return False

def test_mobile_gestures():
    """Test mobile gesture functionality"""
    print("\nTesting mobile gestures...")
    try:
        from utils.mobile_optimization import MobileGestures
        
        gestures = MobileGestures()
        
        # Test swipe navigation
        pages = ['home', 'generate', 'account']
        swipe_script = gestures.enable_swipe_navigation(pages)
        assert 'touchstart' in swipe_script, "Swipe script should handle touchstart"
        assert 'touchend' in swipe_script, "Swipe script should handle touchend"
        
        # Test pull to refresh
        refresh_script = gestures.enable_pull_to_refresh()
        assert 'touchstart' in refresh_script, "Refresh script should handle touchstart"
        assert 'touchmove' in refresh_script, "Refresh script should handle touchmove"
        
        print("✅ Mobile gestures working")
        return True
    except Exception as e:
        print(f"❌ Mobile gestures error: {e}")
        return False

def test_mobile_optimizer():
    """Test main mobile optimizer"""
    print("\nTesting mobile optimizer...")
    try:
        from utils.mobile_optimization import MobileOptimizer
        
        optimizer = MobileOptimizer()
        
        # Test layout configurations
        dashboard_layout = optimizer.get_responsive_layout('dashboard')
        form_layout = optimizer.get_responsive_layout('form')
        workflow_layout = optimizer.get_responsive_layout('workflow')
        
        assert 'columns' in dashboard_layout, "Layout should contain columns config"
        assert 'sidebar' in dashboard_layout, "Layout should contain sidebar config"
        
        print(f"Dashboard layout: {dashboard_layout}")
        print(f"Form layout: {form_layout}")
        print(f"Workflow layout: {workflow_layout}")
        
        print("✅ Mobile optimizer working")
        return True
    except Exception as e:
        print(f"❌ Mobile optimizer error: {e}")
        return False

def test_convenience_functions():
    """Test convenience functions"""
    print("\nTesting convenience functions...")
    try:
        from utils.mobile_optimization import (
            get_device_info, is_mobile, create_responsive_columns
        )
        
        # Test device info
        device_info = get_device_info()
        assert isinstance(device_info, dict), "Device info should be a dictionary"
        
        # Test mobile check
        mobile_status = is_mobile()
        assert isinstance(mobile_status, bool), "Mobile status should be boolean"
        
        # Test responsive columns
        cols = create_responsive_columns([1], [1, 1], [1, 1, 1])
        assert isinstance(cols, list), "Responsive columns should return a list"
        
        print(f"Device info keys: {list(device_info.keys())}")
        print(f"Is mobile: {mobile_status}")
        print(f"Responsive columns: {cols}")
        
        print("✅ Convenience functions working")
        return True
    except Exception as e:
        print(f"❌ Convenience functions error: {e}")
        return False

def test_ui_components_integration():
    """Test integration with existing UI components"""
    print("\nTesting UI components integration...")
    try:
        from utils.ui_components import COLORS, TYPOGRAPHY, SPACING, BREAKPOINTS
        from utils.mobile_optimization import TouchTargetOptimizer
        
        # Verify that mobile optimization can access UI constants
        optimizer = TouchTargetOptimizer()
        
        # Test that colors are available for mobile styles
        assert 'primary' in COLORS, "Primary color should be available"
        assert 'touch_target_min' in COLORS, "Touch target minimum should be defined"
        
        # Test breakpoints
        assert 'mobile' in BREAKPOINTS, "Mobile breakpoint should be defined"
        assert 'tablet' in BREAKPOINTS, "Tablet breakpoint should be defined"
        assert 'desktop' in BREAKPOINTS, "Desktop breakpoint should be defined"
        
        print("✅ UI components integration working")
        return True
    except Exception as e:
        print(f"❌ UI integration error: {e}")
        return False

def run_mobile_optimization_tests():
    """Run all mobile optimization tests"""
    print("🧪 Starting Mobile Optimization Tests")
    print("=" * 50)
    
    tests = [
        test_mobile_imports,
        test_mobile_detector,
        test_touch_targets,
        test_responsive_layout,
        test_mobile_navigation,
        test_mobile_gestures,
        test_mobile_optimizer,
        test_convenience_functions,
        test_ui_components_integration
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 Mobile Optimization Test Results")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All mobile optimization tests passed!")
        print("Mobile features are ready for production use.")
        return True
    else:
        print("\n⚠️  Some mobile optimization tests failed.")
        print("Please review the errors above before deployment.")
        return False

if __name__ == "__main__":
    success = run_mobile_optimization_tests()
    sys.exit(0 if success else 1)