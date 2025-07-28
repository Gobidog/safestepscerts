#!/usr/bin/env python3
"""
Password Reset Utility for SafeSteps Certificate Generator
Resets user passwords to match documented values
"""
import json
import bcrypt
import shutil
from datetime import datetime
from pathlib import Path
import sys
import os

# Add parent directory to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.user_store import user_store

def reset_passwords():
    """Reset passwords for all users to match documentation"""
    print("=== SafeSteps Password Reset Utility ===")
    print(f"Start time: {datetime.now().isoformat()}")
    
    # Define new passwords matching documentation
    password_updates = {
        "admin": "Admin@SafeSteps2024",
        "testuser": "UserPass123"
    }
    
    # Backup current users.json
    users_path = Path("data/storage/users.json")
    if not users_path.exists():
        print("ERROR: users.json not found at data/storage/users.json")
        return False
        
    backup_path = users_path.parent / f"users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    print(f"\nCreating backup: {backup_path}")
    shutil.copy2(users_path, backup_path)
    
    # Load current users
    print("\nLoading current users...")
    with open(users_path, 'r') as f:
        users_data = json.load(f)
    
    # Track updates
    updated_users = []
    failed_users = []
    
    # Update passwords
    print("\nUpdating passwords...")
    for user_id, user_data in users_data.items():
        username = user_data.get('username')
        if username in password_updates:
            new_password = password_updates[username]
            try:
                # Generate new bcrypt hash
                password_bytes = new_password.encode('utf-8')
                new_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt(12))
                
                # Update the user data
                old_hash = user_data['password_hash']
                user_data['password_hash'] = new_hash.decode('utf-8')
                
                print(f"  ✓ {username}: Password hash updated")
                print(f"    Old hash: {old_hash[:20]}...")
                print(f"    New hash: {user_data['password_hash'][:20]}...")
                
                updated_users.append(username)
            except Exception as e:
                print(f"  ✗ {username}: Failed to update - {str(e)}")
                failed_users.append(username)
    
    # Save updated users
    if updated_users and not failed_users:
        print("\nSaving updated users.json...")
        with open(users_path, 'w') as f:
            json.dump(users_data, f, indent=2)
        print("✓ File saved successfully")
        
        # Verify changes
        print("\nVerifying password updates...")
        verification_success = True
        
        for username, new_password in password_updates.items():
            user = user_store.get_user_by_username(username)
            if user:
                try:
                    # Test password verification
                    password_bytes = new_password.encode('utf-8')
                    if bcrypt.checkpw(password_bytes, user.password_hash.encode('utf-8')):
                        print(f"  ✓ {username}: Password verification successful")
                    else:
                        print(f"  ✗ {username}: Password verification failed")
                        verification_success = False
                except Exception as e:
                    print(f"  ✗ {username}: Verification error - {str(e)}")
                    verification_success = False
            else:
                print(f"  ✗ {username}: User not found in UserStore")
                verification_success = False
        
        # Summary
        print("\n=== Summary ===")
        print(f"Users updated: {len(updated_users)} - {', '.join(updated_users)}")
        print(f"Users failed: {len(failed_users)}")
        print(f"Backup created: {backup_path}")
        print(f"Verification: {'PASSED' if verification_success else 'FAILED'}")
        print(f"End time: {datetime.now().isoformat()}")
        
        if verification_success:
            print("\n✅ Password reset completed successfully!")
            print("\nNew credentials:")
            for username, password in password_updates.items():
                print(f"  - {username}: {password}")
            return True
        else:
            print("\n❌ Password reset completed but verification failed!")
            print("Consider restoring from backup")
            return False
    else:
        print("\n❌ Password reset failed - no changes saved")
        if failed_users:
            print(f"Failed users: {', '.join(failed_users)}")
        return False

if __name__ == "__main__":
    # Change to project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    success = reset_passwords()
    sys.exit(0 if success else 1)