#!/usr/bin/env python3
"""
EMERGENCY SMOKE TEST for SafeSteps App
Tests if the app starts and basic functionality works
"""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def test_basic_imports():
    """Test that all critical modules can be imported"""
    print("🧪 Testing basic imports...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, str(Path.cwd()))
        
        # Test core imports
        import app
        from pages.dashboard_v3_modern import render_dashboard_v3
        from utils.auth import requires_admin, get_current_user
        from utils.ui_components import create_card, create_metric_card
        from utils.mobile_optimization import apply_global_mobile_optimizations
        
        print("✅ All critical imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_streamlit_startup():
    """Test if Streamlit app can start without errors"""
    print("🚀 Testing Streamlit startup...")
    
    try:
        # Start Streamlit in background
        process = subprocess.Popen([
            'streamlit', 'run', 'app.py', 
            '--server.headless', 'true',
            '--server.port', '8502',
            '--logger.level', 'error'
        ], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
        )
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running (not crashed)
        if process.poll() is None:
            print("✅ Streamlit app started successfully")
            
            # Try to hit the health endpoint
            try:
                response = requests.get('http://localhost:8502/_stcore/health', timeout=5)
                if response.status_code == 200:
                    print("✅ Streamlit health check passed")
                else:
                    print(f"⚠️  Health check returned {response.status_code}")
            except:
                print("⚠️  Could not reach health endpoint (might be normal)")
            
            # Clean up
            process.terminate()
            process.wait(timeout=10)
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Streamlit crashed on startup")
            print(f"STDOUT: {stdout[-500:]}")  # Last 500 chars
            print(f"STDERR: {stderr[-500:]}")  # Last 500 chars
            return False
            
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        return False

def test_dashboard_rendering():
    """Test if dashboard functions can be called without errors"""
    print("📊 Testing dashboard rendering...")
    
    try:
        # This tests the function signature and basic setup
        from pages.dashboard_v3_modern import get_greeting, safe_columns
        
        # Test helper functions
        greeting = get_greeting()
        print(f"   Greeting function works: '{greeting}'")
        
        # Test safe columns function
        cols = safe_columns([2, 1], 2)
        print(f"   Safe columns function works")
        
        print("✅ Dashboard functions are callable")
        return True
        
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all smoke tests"""
    print("🚨 EMERGENCY SMOKE TEST for SafeSteps App")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Dashboard Functions", test_dashboard_rendering),
        ("Streamlit Startup", test_streamlit_startup),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        result = test_func()
        results.append((test_name, result))
        print(f"{'✅ PASSED' if result else '❌ FAILED'}: {test_name}")
    
    print("\n" + "=" * 50)
    print("📊 SMOKE TEST RESULTS:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / len(results)) * 100
    print(f"\n🎯 Success Rate: {success_rate:.0f}% ({passed}/{len(results)} tests passed)")
    
    if success_rate >= 75:
        print("🎉 SMOKE TEST PASSED - App appears to be working!")
        return True
    else:
        print("💥 SMOKE TEST FAILED - Critical issues detected!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)