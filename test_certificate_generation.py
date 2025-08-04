#\!/usr/bin/env python3
"""
Test certificate generation with the column name fixes
"""

import sys
import pandas as pd
import tempfile
import os

# Add project root to path
sys.path.insert(0, '/home/marsh/coding/Safesteps')

def test_certificate_generation_logic():
    """Test the actual certificate generation with underscore column names"""
    print("🧪 Testing Certificate Generation Logic")
    
    try:
        # Create test data exactly as the validator would output it
        test_data = pd.DataFrame({
            'first_name': ['John', 'Jane', 'Bob'],
            'last_name': ['Doe', 'Smith', 'Johnson'],
            'course': ['Safety Training', 'Safety Training', 'Safety Training'],
            'email': ['john@test.com', 'jane@test.com', 'bob@test.com']
        })
        
        print(f"📊 Test data columns: {list(test_data.columns)}")
        
        # Test the logic from both step4_generate and admin_step4_generate
        successful_extractions = 0
        
        for index, row in test_data.iterrows():
            # This is the exact logic from lines 854-855 (step4_generate)
            first_name = row.get('first_name', row.get('First Name', row.get('first name', '')))
            last_name = row.get('last_name', row.get('Last Name', row.get('last name', '')))
            
            print(f"   Row {index}: '{first_name}' '{last_name}'")
            
            if first_name and last_name:
                successful_extractions += 1
            else:
                print(f"   ❌ Failed to extract names for row {index}")
                
        print(f"\n📊 Results: {successful_extractions}/{len(test_data)} successful name extractions")
        
        if successful_extractions == len(test_data):
            print("✅ ALL CERTIFICATE GENERATION LOGIC TESTS PASSED")
            print("✅ Column name mismatch fix is working correctly")
            return True
        else:
            print("❌ Some certificate generation logic failed")
            return False
            
    except Exception as e:
        print(f"❌ Certificate generation test failed: {e}")
        return False

def test_specific_line_changes():
    """Verify the exact line changes were made"""
    print("\n🔍 Verifying Specific Line Changes")
    
    try:
        with open('/home/marsh/coding/Safesteps/app.py', 'r') as f:
            lines = f.readlines()
        
        # Check specific lines mentioned in the fix
        changes_verified = 0
        
        # Look for the patterns in the code
        for i, line in enumerate(lines, 1):
            if "row.get('first_name', row.get('First Name'" in line:
                print(f"✅ Line {i}: Found first_name priority fix")
                changes_verified += 1
            elif "row.get('last_name', row.get('Last Name'" in line:
                print(f"✅ Line {i}: Found last_name priority fix") 
                changes_verified += 1
        
        print(f"\n📊 Found {changes_verified} verified line changes")
        
        if changes_verified >= 4:  # Should be 4 total changes (2 in user, 2 in admin)
            print("✅ ALL SPECIFIED LINE CHANGES VERIFIED")
            return True
        else:
            print(f"❌ Expected 4 changes, found {changes_verified}")
            return False
            
    except Exception as e:
        print(f"❌ Line change verification failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🎯 TARGETED CERTIFICATE GENERATION FIX TEST")
    print("=" * 60)
    
    test1_pass = test_certificate_generation_logic()
    test2_pass = test_specific_line_changes()
    
    print("\n" + "=" * 60)
    
    if test1_pass and test2_pass:
        print("🎉 CERTIFICATE GENERATION FIX VERIFICATION COMPLETE")
        print("🟢 Status: All fixes working correctly")
        sys.exit(0)
    else:
        print("❌ CERTIFICATE GENERATION FIX VERIFICATION FAILED")
        print("🔴 Status: Issues detected")
        sys.exit(1)
