#!/usr/bin/env python3
"""
EMERGENCY USER RESET - Force reset users to expected passwords
This script can be run directly on Streamlit Cloud to fix authentication
"""

import streamlit as st
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

def emergency_user_reset():
    """Emergency function to reset users with correct passwords"""
    st.title("🚨 EMERGENCY USER RESET")
    st.write("This will reset ALL users with the correct expected passwords")
    
    # Get environment info
    env_info = get_environment_info()
    is_cloud = env_info['is_streamlit_cloud']
    storage_path = env_info['user_storage_path']
    
    st.info(f"Environment: {'Streamlit Cloud' if is_cloud else 'Local Development'}")
    st.info(f"User storage path: {storage_path}")
    
    # Show expected passwords
    admin_password = config.auth.admin_password
    user_password = config.auth.user_password
    
    st.success(f"Admin password will be: {admin_password}")
    st.success(f"User password will be: {user_password}")
    
    # Show current users
    try:
        user_store = UserStore()
        current_users = user_store.list_users(include_inactive=True)
        
        st.write(f"Current users in storage: {len(current_users)}")
        
        for user in current_users:
            st.write(f"- {user.username} ({user.role}) - Active: {user.is_active}")
    except Exception as e:
        st.error(f"Error reading current users: {e}")
        current_users = []
    
    # Reset button
    if st.button("🔥 FORCE RESET ALL USERS", type="primary"):
        try:
            # Create completely fresh user storage
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
            
            # Write to the actual storage location
            storage_file = Path(storage_path)
            storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(storage_file, 'w') as f:
                json.dump(fresh_users, f, indent=2)
            
            st.success("✅ Users successfully reset!")
            st.success(f"✅ {len(fresh_users)} users created")
            
            # Verify by reading back
            with open(storage_file, 'r') as f:
                verification = json.load(f)
            
            st.success(f"✅ Verification: {len(verification)} users in storage")
            
            # Test password verification
            user_store_new = UserStore()
            
            admin_user = user_store_new.get_user_by_username("admin")
            if admin_user and user_store_new.verify_password(admin_user, admin_password):
                st.success("✅ Admin password verification: PASS")
            else:
                st.error("❌ Admin password verification: FAIL")
            
            test_user = user_store_new.get_user_by_username("testuser")
            if test_user and user_store_new.verify_password(test_user, user_password):
                st.success("✅ Test user password verification: PASS")
            else:
                st.error("❌ Test user password verification: FAIL")
            
            st.markdown("---")
            st.success("🎯 **WORKING CREDENTIALS:**")
            st.code(f"""
Admin Login:
  Username: admin
  Password: {admin_password}
  OR
  Email: admin@safesteps.local  
  Password: {admin_password}

Test User Login:
  Username: testuser
  Password: {user_password}
  OR
  Email: testuser@safesteps.local
  Password: {user_password}
            """)
            
        except Exception as e:
            st.error(f"❌ Error during reset: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # Show raw storage contents
    if st.checkbox("Show raw storage file contents"):
        try:
            with open(storage_path, 'r') as f:
                raw_content = f.read()
            st.code(raw_content, language="json")
        except Exception as e:
            st.error(f"Could not read storage file: {e}")

# Run the emergency reset function
if __name__ == "__main__":
    emergency_user_reset()