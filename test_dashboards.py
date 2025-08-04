#!/usr/bin/env python3
"""Test importing all dashboard versions"""
import sys

try:
    print("Testing dashboard imports...")
    
    # Test Version 1
    print("Testing Version 1 (Efficiency)...")
    from pages.dashboard_v1_efficiency import render_efficiency_dashboard
    print("✅ Version 1 imported successfully")
    
    # Test Version 2
    print("\nTesting Version 2 (Guided)...")
    from pages.dashboard_v2_guided import render_dashboard_v2
    print("✅ Version 2 imported successfully")
    
    # Test Version 3
    print("\nTesting Version 3 (Modern)...")
    from pages.dashboard_v3_modern import render_dashboard_v3
    print("✅ Version 3 imported successfully")
    
    print("\n🎉 All dashboards imported successfully!")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"\n❌ Syntax Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected Error: {e}")
    sys.exit(1)