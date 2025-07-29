#!/usr/bin/env python3
"""
CRITICAL FIX: Authentication system diagnostic and repair tool
Addresses authentication failures on Streamlit Cloud deployment
"""

import json
import os
import sys
from pathlib import Path
import bcrypt
from datetime import datetime
import uuid

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.environment import is_streamlit_cloud, get_user_storage_path, get_environment_info
from utils.user_store import UserStore, User
from config import config

def diagnose_authentication_issue():
    """Comprehensive diagnosis of the authentication system"""
    print("🔍 DIAGNOSING AUTHENTICATION SYSTEM")
    print("=" * 50)
    
    # Get environment info
    env_info = get_environment_info()
    print(f"Environment: {'Streamlit Cloud' if env_info['is_streamlit_cloud'] else 'Local Development'}")
    print(f"User storage path: {env_info['user_storage_path']}")
    print(f"Working directory: {env_info['current_working_directory']}")
    
    # Check if storage file exists
    storage_path = Path(env_info['user_storage_path'])
    print(f"\nStorage file exists: {storage_path.exists()}")
    
    if storage_path.exists():
        print(f"Storage file size: {storage_path.stat().st_size} bytes")
        
        # Try to read the current users
        try:
            with open(storage_path, 'r') as f:
                users_data = json.load(f)
            
            print(f"Number of users in storage: {len(users_data)}")
            
            if users_data:
                print("\n📋 CURRENT USERS:")
                for user_id, user_data in users_data.items():
                    print(f"  - ID: {user_id}")
                    print(f"    Username: {user_data.get('username', 'N/A')}")
                    print(f"    Email: {user_data.get('email', 'N/A')}")
                    print(f"    Role: {user_data.get('role', 'N/A')}")
                    print(f"    Active: {user_data.get('is_active', 'N/A')}")
                    print(f"    Created: {user_data.get('created_at', 'N/A')}")
                    print(f"    Last Login: {user_data.get('last_login', 'Never')}")
                    print()
            else:
                print("❌ No users found in storage file!")
                
        except Exception as e:
            print(f"❌ Error reading users file: {e}")
    else:
        print("❌ Storage file does not exist!")
    
    # Check expected passwords from config
    print(f"\n🔐 EXPECTED PASSWORDS FROM CONFIG:")
    print(f"Admin password: {config.auth.admin_password}")
    print(f"User password: {config.auth.user_password}")
    
    return users_data if storage_path.exists() else {}

def create_working_users():
    """Create properly functioning user accounts"""
    print("\n🔧 CREATING WORKING USER ACCOUNTS")
    print("=" * 50)
    
    # Initialize user store
    user_store = UserStore()
    
    # Get expected passwords from config
    admin_password = config.auth.admin_password  # Admin@SafeSteps2024
    user_password = config.auth.user_password    # SafeSteps2024!
    
    print(f"Creating admin with password: {admin_password}")
    print(f"Creating testuser with password: {user_password}")
    
    # Clear existing users and create fresh ones
    storage_path = Path(get_user_storage_path())
    
    # Backup existing users if any
    if storage_path.exists():
        backup_path = storage_path.with_suffix('.backup')
        print(f"Backing up existing users to: {backup_path}")
        try:
            import shutil
            shutil.copy2(storage_path, backup_path)
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
    
    # Create fresh user storage with the correct users
    fresh_users = {}
    
    # Create admin user
    admin_id = str(uuid.uuid4())
    admin_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    fresh_users[admin_id] = {
        "user_id": admin_id,
        "username": "admin",
        "email": "admin@safesteps.local", 
        "password_hash": admin_hash,
        "role": "admin",
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True
    }
    
    # Create test user
    user_id = str(uuid.uuid4())
    user_hash = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    fresh_users[user_id] = {
        "user_id": user_id,
        "username": "testuser",
        "email": "testuser@safesteps.local",
        "password_hash": user_hash,
        "role": "user", 
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True
    }
    
    # Write fresh users to storage
    try:
        # Ensure parent directory exists
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(storage_path, 'w') as f:
            json.dump(fresh_users, f, indent=2)
        
        print("✅ Successfully created fresh user accounts!")
        print(f"✅ Storage written to: {storage_path}")
        
        # Verify the creation worked
        with open(storage_path, 'r') as f:
            verification_data = json.load(f)
        
        print(f"✅ Verification: {len(verification_data)} users created")
        
        for user_data in verification_data.values():
            print(f"  - {user_data['username']} ({user_data['role']})")
            
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        return False
    
    return True

def test_password_verification():
    """Test that password verification works correctly"""
    print("\n🧪 TESTING PASSWORD VERIFICATION")
    print("=" * 50)
    
    try:
        user_store = UserStore()
        
        # Test admin login
        admin_user = user_store.get_user_by_username("admin")
        if admin_user:
            admin_password = config.auth.admin_password
            admin_valid = user_store.verify_password(admin_user, admin_password)
            print(f"Admin login test: {'✅ PASS' if admin_valid else '❌ FAIL'}")
            print(f"  Username: admin")
            print(f"  Password: {admin_password}")
            print(f"  Email: {admin_user.email}")
        else:
            print("❌ Admin user not found!")
        
        # Test regular user login  
        test_user = user_store.get_user_by_username("testuser")
        if test_user:
            user_password = config.auth.user_password
            user_valid = user_store.verify_password(test_user, user_password)
            print(f"Test user login test: {'✅ PASS' if user_valid else '❌ FAIL'}")
            print(f"  Username: testuser")
            print(f"  Password: {user_password}")
            print(f"  Email: {test_user.email}")
        else:
            print("❌ Test user not found!")
            
        # Test email-based login
        admin_by_email = user_store.get_user_by_email("admin@safesteps.local")
        if admin_by_email:
            email_valid = user_store.verify_password(admin_by_email, config.auth.admin_password)
            print(f"Admin email login test: {'✅ PASS' if email_valid else '❌ FAIL'}")
            print(f"  Email: admin@safesteps.local")
            print(f"  Password: {config.auth.admin_password}")
        else:
            print("❌ Admin user not found by email!")
            
    except Exception as e:
        print(f"❌ Error during password verification test: {e}")
        import traceback
        traceback.print_exc()

def print_working_credentials():
    """Print the working credentials for the user"""
    print("\n🎯 WORKING CREDENTIALS")
    print("=" * 50)
    print("🔑 Use these credentials to login to the app:")
    print()
    print("👨‍💼 ADMIN LOGIN:")
    print(f"   Username: admin")
    print(f"   Password: {config.auth.admin_password}")
    print(f"   OR")
    print(f"   Email: admin@safesteps.local")
    print(f"   Password: {config.auth.admin_password}")
    print()
    print("👤 TEST USER LOGIN:")
    print(f"   Username: testuser") 
    print(f"   Password: {config.auth.user_password}")
    print(f"   OR")
    print(f"   Email: testuser@safesteps.local")
    print(f"   Password: {config.auth.user_password}")
    print()
    print("🌐 LIVE APP URL: https://safestepscerts.streamlit.app/")

def main():
    """Main function to diagnose and fix authentication"""
    print("🚨 SAFESTEPS AUTHENTICATION DIAGNOSTIC & REPAIR TOOL")
    print("=" * 60)
    print("This tool will diagnose and fix authentication issues")
    print("on the SafeSteps Certificate Generator app.")
    print()
    
    # Step 1: Diagnose the current state
    current_users = diagnose_authentication_issue()
    
    # Step 2: Create working users
    success = create_working_users()
    
    if not success:
        print("\n❌ FAILED TO CREATE USERS - MANUAL INTERVENTION REQUIRED")
        return 1
    
    # Step 3: Test password verification
    test_password_verification()
    
    # Step 4: Print working credentials
    print_working_credentials()
    
    print("\n✅ AUTHENTICATION SYSTEM REPAIR COMPLETE!")
    print("\nNext steps:")
    print("1. Restart the Streamlit Cloud app (if needed)")
    print("2. Try logging in with the credentials above")
    print("3. If issues persist, check the app logs")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())