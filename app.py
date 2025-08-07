"""
SafeSteps Certificate Generator - Main Application
Implements modern UI with brand colors and 5-step workflow
"""
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import streamlit as st
from pathlib import Path
import time
from datetime import datetime
import os
import zipfile
import tempfile
import structlog

logger = structlog.get_logger()

# Validate environment before starting app
try:
    from config import validate_environment
    validate_environment()
except EnvironmentError as e:
    st.error("🚨 Configuration Error")
    st.error(str(e))
    st.stop()

# Import utilities
from utils.auth import (
    login_with_password, 
    login_with_credentials,
    is_session_valid, 
    get_current_user, 
    logout,
    log_activity,
    requires_admin,
    create_user,
    list_users,
    update_user_role,
    toggle_user_status,
    reset_user_password,
    delete_user
)
from utils.validators import SpreadsheetValidator
# PDFGenerator removed - using programmatic generation only
from utils.storage import StorageManager
from utils.deployment_info import get_deployment_info
from utils.ui_components import apply_custom_css, create_progress_steps, COLORS
from utils.course_manager import CourseManager
from utils.version_manager import VersionManager
import json
import pickle
import base64
from utils.mobile_optimization import apply_global_mobile_optimizations, get_device_info
from config import config
import time

# Initialize storage manager
storage = StorageManager()

# Initialize course manager
course_manager = CourseManager(storage.local_path / "metadata")

# Enhanced Guided Mode: Save/Resume Functions
def save_workflow_state():
    """Save current workflow state for resume functionality"""
    try:
        current_user = get_current_user()
        user_id = current_user.get('username', 'anonymous') if current_user else 'anonymous'
        
        workflow_state = {
            'workflow_step': st.session_state.get('workflow_step', 1),
            'selected_template': st.session_state.get('selected_template'),
            'selected_template_info': st.session_state.get('selected_template_info'),
            'selected_course_info': st.session_state.get('selected_course_info'),
            'file_upload_state': st.session_state.get('file_upload_state', 'ready'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Handle uploaded file data
        if st.session_state.get('uploaded_file'):
            try:
                file_data = st.session_state.uploaded_file.getvalue()
                workflow_state['uploaded_file_data'] = base64.b64encode(file_data).decode('utf-8')
                workflow_state['uploaded_file_name'] = st.session_state.uploaded_file.name
            except Exception as e:
                logger.warning(f"Could not save uploaded file: {e}")
        
        # Handle validated data
        if st.session_state.get('validated_data') is not None:
            try:
                workflow_state['validated_data_json'] = st.session_state.validated_data.to_json(orient='records')
            except Exception as e:
                logger.warning(f"Could not save validated data: {e}")
        
        st.session_state[f'saved_workflow_{user_id}'] = workflow_state
        return True
        
    except Exception as e:
        logger.error(f"Error saving workflow state: {e}")
        return False

def load_workflow_state():
    """Load saved workflow state for resume functionality"""
    try:
        current_user = get_current_user()
        user_id = current_user.get('username', 'anonymous') if current_user else 'anonymous'
        
        saved_state = st.session_state.get(f'saved_workflow_{user_id}')
        
        if saved_state:
            st.session_state.workflow_step = saved_state.get('workflow_step', 1)
            st.session_state.selected_template = saved_state.get('selected_template')
            st.session_state.selected_template_info = saved_state.get('selected_template_info')
            st.session_state.selected_course_info = saved_state.get('selected_course_info')
            st.session_state.file_upload_state = saved_state.get('file_upload_state', 'ready')
            
            # Restore uploaded file data
            if saved_state.get('uploaded_file_data'):
                try:
                    import io
                    file_data = base64.b64decode(saved_state['uploaded_file_data'])
                    uploaded_file = io.BytesIO(file_data)
                    uploaded_file.name = saved_state.get('uploaded_file_name', 'uploaded_file')
                    st.session_state.uploaded_file_restored = True
                    st.session_state.uploaded_file_name = saved_state.get('uploaded_file_name')
                    st.session_state.uploaded_file_data = file_data
                except Exception as e:
                    logger.warning(f"Could not restore uploaded file: {e}")
            
            # Restore validated data
            if saved_state.get('validated_data_json'):
                try:
                    import pandas as pd
                    st.session_state.validated_data = pd.read_json(saved_state['validated_data_json'], orient='records')
                except Exception as e:
                    logger.warning(f"Could not restore validated data: {e}")
            
            return True
            
    except Exception as e:
        logger.error(f"Error loading workflow state: {e}")
    
    return False

def clear_workflow_state():
    """Clear saved workflow state"""
    try:
        current_user = get_current_user()
        user_id = current_user.get('username', 'anonymous') if current_user else 'anonymous'
        
        user_key = f'saved_workflow_{user_id}'
        if user_key in st.session_state:
            del st.session_state[user_key]
            
        return True
        
    except Exception as e:
        logger.error(f"Error clearing workflow state: {e}")
        return False

def check_for_saved_workflow():
    """Check if user has a saved workflow and offer to resume"""
    try:
        current_user = get_current_user()
        if not current_user:
            return False
            
        user_id = current_user.get('username', 'anonymous')
        saved_state = st.session_state.get(f'saved_workflow_{user_id}')
        
        if saved_state:
            saved_time = saved_state.get('timestamp')
            if saved_time:
                try:
                    saved_datetime = datetime.fromisoformat(saved_time)
                    time_diff = datetime.now() - saved_datetime
                    
                    # Only offer to resume if saved within last 24 hours
                    if time_diff.total_seconds() < 86400:  # 24 hours
                        with st.container(border=True):
                            st.info("📋 **Resume Previous Session**")
                            st.write(f"Found saved progress from {saved_datetime.strftime('%B %d, %Y at %I:%M %p')}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("📂 Resume Where I Left Off", type="primary", use_container_width=True):
                                    if load_workflow_state():
                                        st.success("Previous session restored!")
                                        st.rerun()
                                    else:
                                        st.error("Could not restore previous session")
                            
                            with col2:
                                if st.button("🆕 Start Fresh", use_container_width=True):
                                    clear_workflow_state()
                                    st.success("Starting fresh session!")
                                    st.rerun()
                            
                            return True
                except ValueError:
                    clear_workflow_state()
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking for saved workflow: {e}")
        return False

# Page configuration
st.set_page_config(
    page_title="SafeSteps Certificate Generator",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="auto",  # Mobile-friendly: auto-collapse on mobile
    menu_items={
        'Get Help': 'https://safesteps.help',
        'Report a bug': 'https://safesteps.support',
        'About': '# SafeSteps Mobile-Optimized Certificate Generator\nDesigned for excellent mobile user experience with 44px+ touch targets.'
    }
)

# Deployment version indicator
DEPLOYMENT_VERSION = "v2.1 - HTML Fix 09dde6d"

# Remove unsafe HTML/CSS injection - use native Streamlit theming


def render_progress_bar(current_step: int):
    """Render horizontal progress bar for workflow using Streamlit native components"""
    steps = [
        ("Upload", "📤", 1),
        ("Validate", "✅", 2),
        ("Template", "📄", 3),
        ("Generate", "🏆", 4),
        ("Complete", "🎉", 5)
    ]
    
    # Use the ui_components function to create progress steps
    from utils.ui_components import create_progress_steps
    create_progress_steps(steps, current_step)


def login_page():
    """Render login page with brand styling and environment validation"""
    # First, check environment health and show warnings if needed
    from config import get_environment_health
    
    env_health = get_environment_health()
    if env_health["status"] != "healthy":
        if env_health["status"] == "critical":
            st.error("🚨 **System Configuration Error**")
            for issue in env_health["issues"]:
                st.error(f"• {issue}")
            st.info("🔧 **Admin Action Required**: Please check the system configuration and restart the application.")
            st.stop()
        elif env_health["status"] == "warning":
            with st.expander("⚠️ Configuration Warnings", expanded=False):
                for warning in env_health["warnings"]:
                    st.warning(f"• {warning}")
    
    # Ensure default users are initialized on first run
    from utils.user_store import user_store
    try:
        # Check if any users exist
        existing_users = user_store.list_users(include_inactive=True)
        logger.info(f"Found {len(existing_users)} existing users")
        
        if not existing_users:
            # Initialize default users
            admin_password = config.auth.admin_password
            user_password = config.auth.user_password
            
            logger.info(f"Creating default users: admin password={admin_password}, user password={user_password}")
            
            # Create admin user first
            admin_user = user_store.create_user("admin", "admin@safesteps.local", admin_password, "admin")
            if admin_user:
                logger.info("Admin user created successfully")
            else:
                logger.error("Failed to create admin user")
            
            # Create test user
            test_user = user_store.create_user("testuser", "testuser@safesteps.local", user_password, "user")
            if test_user:
                logger.info("Test user created successfully")
            else:
                logger.error("Failed to create test user")
            
            # Verify users were created
            final_users = user_store.list_users(include_inactive=True)
            logger.info(f"After initialization: {len(final_users)} users exist")
            for user in final_users:
                logger.info(f"User: {user.username} ({user.role}) - Active: {user.is_active}")
        else:
            logger.info("Users already exist, skipping initialization")
            for user in existing_users:
                logger.info(f"Existing user: {user.username} ({user.role}) - Active: {user.is_active}")
    except Exception as e:
        logger.error(f"Error during user initialization: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Welcome header using native Streamlit components
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🏆", help="SafeSteps Certificate Generator")
        st.title("SafeSteps")
        st.markdown("**Certificate Generator**")
    
    # Login form with enhanced styling
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Login card using native container
        with st.container(border=True):
            with st.form("login_form", clear_on_submit=False):
                username_or_email = st.text_input(
                    "Username or Email",
                    placeholder="Enter your username or email",
                    help="Use your assigned username or email address"
                )
                
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    help="Contact administrator if you forgot your password"
                )
                
                col_a, col_b = st.columns(2)
                with col_a:
                    submit = st.form_submit_button("Login", use_container_width=True)
                with col_b:
                    show_help = st.form_submit_button("Help", use_container_width=True)
                
                if show_help:
                    st.info("""
                **Need Help?**
                
                📧 **Contact Information:**
                • Email your administrator for login credentials
                • Include your name and department for faster assistance
                
                🔑 **Default Credentials**:
                • Admin: admin (or admin@safesteps.local) / Admin@SafeSteps2024
                • For test user credentials, contact your administrator
                
                💡 **Login Tip**: Use either username OR email address
                
                ⚠️ **Troubleshooting:**
                • Clear your browser cache if login issues persist
                • Ensure JavaScript is enabled in your browser
                • Try using an incognito/private browsing window
                """)
                
                if submit:
                    if not username_or_email:
                        st.error("📝 Please enter your username or email address")
                    elif not password:
                        st.error("🔐 Please enter your password")
                    else:
                        with st.spinner("Authenticating..."):
                            try:
                                success, role, error = login_with_credentials(username_or_email, password)
                                if success:
                                    user = get_current_user()
                                    st.success(f"✅ Welcome {user['username']}! Logged in as {role}")
                                    # Activity logging removed - function not defined
                                    time.sleep(1)  # Brief pause for success message
                                    st.rerun()
                                else:
                                    # Enhanced error messages
                                    if "Too many login attempts" in (error or ""):
                                        st.error("🚫 **Rate Limited**: " + error)
                                        st.info("💡 **Tip**: Wait a few minutes before trying again")
                                    elif "Account is disabled" in (error or ""):
                                        st.error("🚫 **Account Disabled**: " + error)
                                        st.info("📞 **Next Step**: Contact your administrator to reactivate your account")
                                    else:
                                        st.error("❌ **Login Failed**: Invalid username/email or password")
                                        st.info("💡 **Tips**: \n• Double-check your credentials\n• Try copy-pasting to avoid typos\n• Contact admin if you need help")
                            except Exception as e:
                                st.error(f"⚠️ **System Error**: Unable to process login request")
                                st.error(f"Technical details: {str(e)}")
                                st.info("🔧 **Next Step**: Please try again in a few moments or contact your administrator")
    
    # EMERGENCY AUTHENTICATION RESET (TEMPORARY FIX)
    st.markdown("---")
    with st.expander("🚨 EMERGENCY: Authentication Reset", expanded=False):
        st.warning("**For System Administrators Only - This will reset all user passwords**")
        
        # Show expected passwords
        admin_password = config.auth.admin_password
        user_password = config.auth.user_password
        
        st.info(f"**Expected Admin Password:** {admin_password}")
        st.info(f"**Expected User Password:** {user_password}")
        
        # Show current user count
        try:
            from utils.user_store import user_store
            current_users = user_store.list_users(include_inactive=True)
            st.write(f"Current users in storage: {len(current_users)}")
            for user in current_users:
                st.write(f"- {user.username} ({user.role}) - Active: {user.is_active}")
        except Exception as e:
            st.error(f"Error reading users: {e}")
        
        if st.button("🔥 EMERGENCY RESET ALL USERS", type="primary"):
            try:
                # Force recreate users with correct passwords
                from utils.environment import get_user_storage_path
                storage_path = Path(get_user_storage_path())
                
                # Create fresh users with expected passwords
                import bcrypt, uuid, json
                fresh_users = {}
                
                # Admin user
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
                
                # Test user
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
                
                # Write to storage
                storage_path.parent.mkdir(parents=True, exist_ok=True)
                with open(storage_path, 'w') as f:
                    json.dump(fresh_users, f, indent=2)
                
                st.success("✅ **EMERGENCY RESET COMPLETE!**")
                st.success("**Working Credentials:**")
                st.code(f"""
Admin Login:
  Username: admin
  Password: {admin_password}

Test User Login:  
  Username: testuser
  Password: {user_password}
                """)
                st.info("**Try logging in now with the credentials above!**")
                
            except Exception as e:
                st.error(f"Emergency reset failed: {e}")
                import traceback
                st.code(traceback.format_exc())


def user_workflow():
    """Main user workflow with enhanced UI"""
    from utils.ui_components import create_header, create_card
    
    # Initialize workflow state
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 1
        st.session_state.uploaded_file = None
        st.session_state.validated_data = None
        st.session_state.selected_template = None
        st.session_state.file_upload_state = 'ready'
        st.session_state.upload_key = 0
        st.session_state.show_uploader = False
        st.session_state.generated_files = []
    
    # Get current user
    user = get_current_user()
    
    # Enhanced header
    col1, col2 = st.columns([5, 1])
    with col1:
        # Enhanced header with mode indication
        create_header(
            "Enhanced Guided Certificate Generator", 
            "Generate professional certificates with step-by-step guidance and save/resume functionality",
            user
        )
        
        # Show workflow resume option if not already shown
        workflow_resumed = st.session_state.get('workflow_resumed', False)
        if not workflow_resumed and st.session_state.get('workflow_step', 1) == 1:
            check_for_saved_workflow()
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()
    
    # Progress bar
    render_progress_bar(st.session_state.workflow_step)
    
    # Step content
    if st.session_state.workflow_step == 1:
        step1_upload()
    elif st.session_state.workflow_step == 2:
        step2_validate()
    elif st.session_state.workflow_step == 3:
        step3_template()
    elif st.session_state.workflow_step == 4:
        step4_generate()
    elif st.session_state.workflow_step == 5:
        step5_complete()


def step1_upload():
    """Step 1: File Upload with Enhanced Guided Mode"""
    from utils.ui_components import create_card, COLORS
    
    # Enhanced guided mode header with contextual help
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("📁 Upload Your Student List")
            st.markdown("Upload a file with your student names to create certificates")
        with col2:
            if st.button("❓ Need Help?", type="secondary"):
                st.session_state.show_step1_help = not st.session_state.get('show_step1_help', False)
    
    # Contextual help section
    if st.session_state.get('show_step1_help', False):
        with st.expander("💡 How to Upload Your File", expanded=True):
            st.markdown("""
            **What files work?**
            - Excel files (.xlsx, .xls)
            - CSV files (.csv)
            
            **What should be in your file?**
            - Column with first names
            - Column with last names
            - Any other student information
            
            **Tips:**
            - Make sure names are spelled correctly
            - Remove empty rows at the bottom
            - First row should have column headers
            """)
    
    # Enhanced upload zone using native components
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("# 📁")
            st.markdown("### Drop your file here")
            st.markdown("or click to browse")
            st.info("**Supported:** CSV, Excel (.xlsx, .xls)")
    
    # Initialize file upload state if not exists
    if 'file_upload_state' not in st.session_state:
        st.session_state.file_upload_state = 'ready'
    if 'show_uploader' not in st.session_state:
        st.session_state.show_uploader = False
    
    # Check if we already have an uploaded file
    if 'uploaded_file' in st.session_state and st.session_state.uploaded_file is not None:
        # Show uploaded file status and continue button
        st.success(f"✅ File uploaded: {st.session_state.uploaded_file.name}")
        
        # Navigation buttons with save functionality
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("💾 Save Progress", use_container_width=True):
                save_workflow_state()
                st.success("Progress saved!")
        with col2:
            st.button("← Back", disabled=True, use_container_width=True)
        with col3:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.workflow_step = 2
                save_workflow_state()  # Auto-save on navigation
                st.rerun()
        
        # Option to upload different file
        st.markdown("---")
        if st.button("📁 Upload Different File"):
            st.session_state.uploaded_file = None
            st.session_state.file_upload_state = 'ready'
            st.session_state.show_uploader = False
            st.rerun()
    else:
        # Show button to reveal file uploader
        if not st.session_state.show_uploader:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("📁 Choose File to Upload", type="primary", use_container_width=True):
                    st.session_state.show_uploader = True
                    st.rerun()
        else:
            # Show the actual file uploader
            st.info("📎 Click 'Browse files' below to select your CSV/Excel file")
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['csv', 'xlsx', 'xls'],
                label_visibility="collapsed",
                key=f"main_file_uploader_{st.session_state.get('upload_key', 0)}"
            )
            
            # Cancel button to hide uploader
            if st.button("Cancel"):
                st.session_state.show_uploader = False
                st.rerun()
            
            if uploaded_file:
                st.session_state.uploaded_file = uploaded_file
                st.session_state.file_upload_state = 'uploaded'
                st.session_state.show_uploader = False
                # Increment key to force re-render without modal
                st.session_state.upload_key = st.session_state.get('upload_key', 0) + 1
                st.rerun()


def step2_validate():
    """Step 2: Data Validation with Enhanced Guided Mode"""
    from utils.ui_components import create_card, create_loading_animation, COLORS
    
    # Enhanced guided mode header with contextual help
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("✅ Check Your Data")
            st.caption("We're making sure your file has everything needed")
        with col2:
            if st.button("❓ What's Being Checked?", type="secondary"):
                st.session_state.show_step2_help = not st.session_state.get('show_step2_help', False)
    
    # Contextual help section
    if st.session_state.get('show_step2_help', False):
        with st.expander("🔍 What We're Looking For", expanded=True):
            st.markdown("""
            **Required Information:**
            - Student first names
            - Student last names
            - Clean, readable data
            
            **Common Issues We Fix:**
            - Extra spaces around names
            - Empty rows
            - Mixed up column names
            - Special characters that might cause problems
            
            **Don't Worry!**
            - We'll show you exactly what we find
            - You can fix any issues and try again
            - Your original file is never changed
            """)
    
    if not st.session_state.uploaded_file:
        st.error("📁 **No file uploaded**: Please go back to Step 1 to upload your data file.")
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("💾 Save Progress", use_container_width=True):
                save_workflow_state()
                st.success("Progress saved!")
        with col2:
            if st.button("← Back to Upload", use_container_width=True):
                st.session_state.workflow_step = 1
                save_workflow_state()
                st.rerun()
        with col3:
            st.button("Next →", disabled=True, use_container_width=True)
        return
    
    # Show file information
    st.info(f"📊 **Processing**: {st.session_state.uploaded_file.name} ({st.session_state.uploaded_file.size:,} bytes)")
    
    # Process file with detailed progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Initialize validator
        status_text.text("🔧 Initializing validator...")
        progress_bar.progress(0.2)
        time.sleep(0.5)
        
        validator = SpreadsheetValidator()
        
        # Step 2: Reading file
        status_text.text("📖 Reading file content...")
        progress_bar.progress(0.4)
        time.sleep(0.5)
        
        # Step 3: Validating data
        status_text.text("✅ Validating data structure...")
        progress_bar.progress(0.7)
        
        validation_result = validator.validate_file(st.session_state.uploaded_file)
        
        # Step 4: Complete
        status_text.text("🎉 Validation complete!")
        progress_bar.progress(1.0)
        time.sleep(0.5)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        if validation_result.valid:
            st.session_state.validated_data = validation_result.cleaned_data
            st.success(f"✅ **Validation Successful**: Found {validation_result.row_count} recipients ready for certificates!")
            
            # Show detailed statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Recipients", validation_result.row_count)
            with col2:
                column_count = len(validation_result.cleaned_data.columns) if hasattr(validation_result.cleaned_data, 'columns') else 0
                st.metric("Data Columns", column_count)
            with col3:
                st.metric("Data Quality", "✅ Passed")
            
            # Show any warnings
            if validation_result.warnings:
                with st.expander("⚠️ Data Warnings (Review Recommended)"):
                    for warning in validation_result.warnings:
                        st.warning(f"• {warning}")
            
            # Show preview with better formatting
            st.subheader("📋 Data Preview")
            st.caption("First 10 rows of your validated data:")
            st.dataframe(
                validation_result.cleaned_data.head(10), 
                use_container_width=True,
                hide_index=True
            )
            
            # Navigation buttons - remove auto-advance
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("💾 Save Progress", use_container_width=True):
                    save_workflow_state()
                    st.success("Progress saved!")
            with col2:
                if st.button("← Back to Upload", use_container_width=True):
                    st.session_state.workflow_step = 1
                    save_workflow_state()
                    st.rerun()
            with col3:
                if st.button("Next: Choose Template →", type="primary", use_container_width=True):
                    st.session_state.workflow_step = 3
                    save_workflow_state()
                    st.rerun()
        else:
            st.error("❌ **Validation Failed**: Your data file has issues that need to be resolved")
            
            with st.expander("🔍 Error Details", expanded=True):
                for i, error in enumerate(validation_result.errors, 1):
                    st.error(f"**{i}.** {error}")
            
            st.info("""
            💡 **Common Solutions**:
            • Ensure your file has 'First Name' and 'Last Name' columns
            • Check for special characters or formatting issues
            • Save Excel files as CSV if having trouble
            • Remove empty rows at the end of your data
            """)
                
            # Navigation buttons for error state
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("← Back to Upload", use_container_width=True):
                    st.session_state.workflow_step = 1
                    save_workflow_state()
                    st.rerun()
            with col2:
                if st.button("📁 Try Another File", use_container_width=True):
                    st.session_state.workflow_step = 1
                    st.session_state.uploaded_file = None
                    st.session_state.file_upload_state = 'ready'
                    st.session_state.upload_key = st.session_state.get('upload_key', 0) + 1
                    st.session_state.show_uploader = False
                    save_workflow_state()
                    st.rerun()
            with col3:
                if st.button("🔄 Retry Validation", use_container_width=True):
                    st.rerun()
                
    except Exception as e:
        import traceback
        progress_bar.empty()
        status_text.empty()
        
        st.error("⚠️ **Processing Error**: Unable to validate your file")
        
        with st.expander("🔧 Technical Details"):
            st.code(str(e))
            st.text("Full traceback:")
            st.code(traceback.format_exc())
        
        st.info("""
        🛠️ **Troubleshooting Steps**:
        1. Try saving your file in a different format (CSV recommended)
        2. Check if the file is corrupted or contains unusual characters
        3. Ensure the file is not password-protected
        4. Contact support if the problem persists
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📁 Try Different File", use_container_width=True):
                st.session_state.workflow_step = 1
                st.session_state.uploaded_file = None
                st.session_state.file_upload_state = 'ready'
                st.session_state.upload_key = st.session_state.get('upload_key', 0) + 1
                st.session_state.show_uploader = False
                st.rerun()
        with col2:
            if st.button("🔄 Try Again", use_container_width=True):
                st.rerun()


def step3_template():
    """Step 3: Template Selection with enhanced UI"""
    from utils.ui_components import create_card, create_empty_state, COLORS
    
    # Use native Streamlit components instead of HTML
    with st.container(border=True):
        st.header("Step 3: Choose a Template")
        st.caption("Select a certificate design for your participants")
    
    # Get available templates - Use programmatic certificate
    try:
        # We no longer need PDF templates since we use programmatic generation
        available_templates = [{"name": "Programmatic Certificate", "filename": "programmatic", "path": "programmatic"}]
        
        if not available_templates:
            st.error("⚠️ **No Templates Available**: No certificate templates were found in the system.")
            st.info("""
            🛠️ **Administrator Action Needed**:
            • Upload certificate templates to the templates directory
            • Ensure templates are in PDF format
            • Restart the application if templates were recently added
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Data", use_container_width=True):
                    st.session_state.workflow_step = 2
                    st.rerun()
            with col2:
                if st.button("🔄 Refresh Templates", use_container_width=True):
                    st.rerun()
            
            return
        
        # Show template statistics
        st.info(f"📚 **Available Templates**: {len(available_templates)} certificate designs ready to use")
        
        # Template validation results
        validated_templates = []
        validation_warnings = []
        
        for template in available_templates:
            # For programmatic templates, skip file validation
            if template['name'] == 'Programmatic Certificate':
                validated_templates.append({
                    **template,
                    "path": "programmatic",
                    "status": "available",
                    "display_name": "Programmatic Certificate",
                    "description": "Modern certificate design generated programmatically"
                })
            else:
                # Validate template accessibility for PDF templates (if any)
                template_path = storage.get_template_path(template['name'])
                if template_path and os.path.exists(template_path):
                    validated_templates.append({
                        **template,
                        "path": template_path,
                        "status": "available"
                    })
                else:
                    validation_warnings.append(f"Template '{template['name']}' file not accessible")
        
        # Show warnings if any
        if validation_warnings:
            with st.expander("⚠️ Template Validation Warnings"):
                for warning in validation_warnings:
                    st.warning(f"• {warning}")
        
        if not validated_templates:
            st.error("❌ **No Valid Templates**: All templates failed validation")
            st.info("Contact your administrator to fix template issues.")
            return
        
        # Auto-select if only one template
        if len(validated_templates) == 1:
            template = validated_templates[0]
            st.session_state.selected_template = template.get('name', 'template_0')
            st.session_state.selected_template_info = template
            st.success(f"✅ **Template Auto-Selected**: {template.get('display_name', template.get('name'))}")
            # Skip template selection UI entirely
        else:
            # Display templates in improved grid only if multiple
            st.subheader("📋 Available Templates")
            
            # Create responsive columns based on number of templates
            display_cols = st.columns(min(3, len(validated_templates)))
            
            for idx, template in enumerate(validated_templates):
                with display_cols[idx % len(display_cols)]:
                    # Template card with enhanced information
                    template_name = template.get('display_name', template.get('name', 'Unknown'))
                    template_id = template.get('name', f'template_{idx}')
                    
                    selected = st.session_state.selected_template == template_id
                    
                    # Template selection button
                    button_style = "🟢" if selected else "⚪"
                    button_text = f"{button_style} {template_name}"
                    
                    if st.button(
                        button_text,
                        key=f"template_select_{template_id}",
                        use_container_width=True,
                        type="primary" if selected else "secondary"
                    ):
                        st.session_state.selected_template = template_id
                        st.session_state.selected_template_info = template
                        st.rerun()
                    
                    # Template details
                    with st.container():
                        st.caption(template.get('description', 'Certificate template'))
                        
                        # Show file size and creation date
                        if template.get('size'):
                            size_kb = template['size'] / 1024
                            st.caption(f"📁 Size: {size_kb:.1f} KB")
                    
                    if template.get('created'):
                        try:
                            created_date = datetime.fromisoformat(template['created'].replace('Z', '+00:00'))
                            st.caption(f"📅 Added: {created_date.strftime('%Y-%m-%d')}")
                        except:
                            pass
                    
                    # Template status indicator
                    st.caption("✅ Ready to use")
        
        # Selection confirmation and next steps
        if st.session_state.selected_template:
            selected_info = st.session_state.get('selected_template_info', {})
            selected_name = selected_info.get('display_name', st.session_state.selected_template)
            
            st.success(f"✅ **Template Selected**: {selected_name}")
            
            # Course Selection Section using native components
            with st.container(border=True):
                st.subheader("📚 Course Selection")
                st.caption("Choose the course for this certificate")
            
            # Get available courses
            courses = storage.list_course_templates()
            
            if courses:
                # Create course options for selectbox
                course_options = {f"{course['name']}": course for course in courses}
                
                # Course selection
                selected_course_name = st.selectbox(
                    "Select a course:",
                    options=list(course_options.keys()),
                    key="selected_course",
                    help="Choose the course that participants completed"
                )
                
                if selected_course_name:
                    selected_course = course_options[selected_course_name]
                    st.session_state.selected_course_info = selected_course
                    
                    # Show course details
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if selected_course.get('description'):
                            st.info(f"📝 **Description**: {selected_course['description']}")
                    with col2:
                        if selected_course.get('usage_count', 0) > 0:
                            st.metric("Usage Count", selected_course['usage_count'])
            else:
                st.warning("No courses available. Please contact an administrator to create courses.")
                # Provide default course for backward compatibility
                st.session_state.selected_course_info = {
                    'name': 'Vapes and Vaping',
                    'id': 'default_course',
                    'description': 'Default course'
                }
            
            # Show selection details
            with st.expander("📋 Selection Details", expanded=False):
                st.write(f"**Template**: {selected_name}")
                st.write(f"**File**: {selected_info.get('filename', 'N/A')}")
                if selected_info.get('description'):
                    st.write(f"**Description**: {selected_info['description']}")
                if st.session_state.get('selected_course_info'):
                    st.write(f"**Course**: {st.session_state.selected_course_info['name']}")
                
                # Template validation status
                template_path = selected_info.get('path')
                if template_path == 'programmatic' or (template_path and os.path.exists(template_path)):
                    st.success("🟢 Template verified and accessible")
                else:
                    st.error("🔴 Template validation failed")
            
            # Navigation buttons
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                if st.button("← Back to Data", use_container_width=True):
                    st.session_state.workflow_step = 2
                    st.rerun()
            with col3:
                # Validate template and course selection before proceeding
                template_path = selected_info.get('path')
                has_course = st.session_state.get('selected_course_info') is not None
                
                if template_path and (template_path == 'programmatic' or os.path.exists(template_path)) and has_course:
                    # Navigation buttons with save functionality
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("💾 Save Progress", use_container_width=True):
                            save_workflow_state()
                            st.success("Progress saved!")
                    with col2:
                        if st.button("← Back to Data Check", use_container_width=True):
                            st.session_state.workflow_step = 2
                            save_workflow_state()
                            st.rerun()
                    with col3:
                        if st.button("Next: Create Certificates →", type="primary", use_container_width=True):
                            st.session_state.workflow_step = 4
                            save_workflow_state()
                            st.rerun()
                else:
                    if not has_course:
                        st.error("Please select a course")
                    else:
                        st.error("Cannot proceed: Selected template is not accessible")
                    if st.button("🔄 Refresh", use_container_width=True):
                        st.rerun()
        else:
            st.info("👆 **Please select a template above to continue**")
            
            # Back button when no template selected
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                if st.button("← Back to Data", use_container_width=True):
                    st.session_state.workflow_step = 2
                    st.rerun()
    
    except Exception as e:
        st.error("⚠️ **Template System Error**: Unable to load templates")
        
        with st.expander("🔧 Technical Details"):
            st.code(str(e))
        
        st.info("""
        🛠️ **Troubleshooting**:
        • Check if templates directory exists and contains PDF files
        • Verify file permissions on templates directory
        • Contact administrator if problem persists
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Data", use_container_width=True):
                st.session_state.workflow_step = 2
                st.rerun()
        with col2:
            if st.button("🔄 Retry", use_container_width=True):
                st.rerun()


def step4_generate():
    """Step 4: Generate Certificates with Enhanced Guided Mode"""
    from utils.ui_components import create_card, COLORS
    
    # Enhanced guided mode header with contextual help
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("🏆 Create Your Certificates")
            st.caption("Ready to generate certificates for your students")
        with col2:
            if st.button("❓ What Happens Next?", type="secondary"):
                st.session_state.show_step4_help = not st.session_state.get('show_step4_help', False)
    
    # Contextual help section
    if st.session_state.get('show_step4_help', False):
        with st.expander("⚙️ How Certificate Creation Works", expanded=True):
            st.markdown("""
            **What we'll do:**
            - Create one certificate for each student
            - Use the template style you picked
            - Add each student's name automatically
            - Package everything in a zip file
            
            **This might take a moment:**
            - We'll show progress as we work
            - You can't stop the process once started
            - All certificates will be ready to download
            
            **What you get:**
            - Professional PDF certificates
            - One file for each student
            - Everything packaged for easy download
            """)
    
    if not st.session_state.validated_data.empty and st.session_state.selected_template:
        # Get template info for display
        template_info = st.session_state.get('selected_template_info', {})
        template_display_name = template_info.get('display_name', st.session_state.selected_template)
        
        # Get course info
        course_info = st.session_state.get('selected_course_info', {})
        course_name = course_info.get('name', 'Vapes and Vaping')  # Default for backward compatibility
        
        st.info(f"""
        **Ready to generate certificates:**
        - Recipients: {len(st.session_state.validated_data)}
        - Template: {template_display_name}
        - Course: {course_name}
        """)
        
        # Navigation buttons with save functionality
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("💾 Save Progress", use_container_width=True):
                save_workflow_state()
                st.success("Progress saved!")
        with col2:
            if st.button("← Back to Templates", use_container_width=True):
                st.session_state.workflow_step = 3
                save_workflow_state()
                st.rerun()
        with col3:
            if st.button("🏆 Create Certificates", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                generated_files = []
                total = len(st.session_state.validated_data)
                
                # Use programmatic certificate generator only
                from certificate_generator_production import generate_certificate_for_app
                
                # Create temp directory if it doesn't exist
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                
                # Generate certificates
                for idx, row in st.session_state.validated_data.iterrows():
                    progress = (idx + 1) / total
                    progress_bar.progress(progress)
                    status_text.text(f"Generating certificate {idx + 1} of {total}...")
                    
                    # Generate certificate
                    try:
                        # Extract name fields - handle various column name formats
                        first_name = row.get('first_name', row.get('First Name', row.get('first name', row.get('FirstName', ''))))
                        last_name = row.get('last_name', row.get('Last Name', row.get('last name', row.get('LastName', ''))))
                        
                        # Skip if no names
                        if not first_name and not last_name:
                            st.warning(f"Skipping row {idx + 1}: No name data found")
                            continue
                        
                        # Generate unique filename
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        safe_name = f"{first_name}_{last_name}".replace(' ', '_').replace('/', '_')
                        output_path = str(temp_dir / f"{safe_name}_{timestamp}.pdf")
                        
                        # Get course info
                        course_info = st.session_state.get('selected_course_info', {})
                        course_name = course_info.get('name', 'Vapes and Vaping')
                        course_id = course_info.get('id')
                        
                        # Generate the certificate using programmatic generation
                        pdf_bytes = generate_certificate_for_app(
                            student_name=f"{first_name} {last_name}".strip(),
                            course_name=course_name,
                            score="Pass",
                            completion_date=datetime.now().strftime("%B %d, %Y")
                        )
                        # Save to file
                        with open(output_path, 'wb') as f:
                            f.write(pdf_bytes)
                        pdf_path = output_path
                        generated_files.append(pdf_path)
                        
                        # Log certificate generation
                        storage.log_certificate_generation(
                            user=get_current_user()['username'],
                            template=template_display_name,
                            count=1
                        )
                        
                        # Update course usage count if we have a valid course ID
                        if course_id and course_id != 'default_course':
                            storage.increment_course_usage(course_id)
                        
                    except Exception as e:
                        st.error(f"Error generating certificate for {first_name} {last_name}: {str(e)}")
                        logger.error(f"Certificate generation error: {e}")
                
                st.session_state.generated_files = generated_files
                progress_bar.progress(1.0)
                status_text.text("All certificates generated!")
                
                # Show summary
                st.success(f"✅ Generated {len(generated_files)} certificates successfully!")
                
                time.sleep(1)
                st.session_state.workflow_step = 5
                st.rerun()
    else:
        st.error("Missing data or template selection")
        # Navigation buttons for error state
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("💾 Save Progress", use_container_width=True):
                save_workflow_state()
                st.success("Progress saved!")
        with col2:
            if st.button("← Back to Templates", use_container_width=True):
                st.session_state.workflow_step = 3
                save_workflow_state()
                st.rerun()
        with col3:
            st.button("Create Certificates →", disabled=True, use_container_width=True)


def step5_complete():
    """Step 5: Download Complete with Enhanced Guided Mode"""
    from utils.ui_components import COLORS
    
    # Enhanced guided mode header with celebration
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("# 🎉")
            st.title("All Done!")
            st.caption("Your certificates are ready to download")
    
    # Contextual help section
    with st.expander("💾 What's in Your Download?", expanded=False):
        st.markdown("""
        **Your certificate package includes:**
        - One PDF certificate for each student
        - Professional quality, ready to print
        - All files in one convenient zip folder
        
        **What to do next:**
        - Click the download button below
        - Unzip the folder on your computer
        - Print or email individual certificates
        
        **Need to make more?**
        - Use the "Create More Certificates" button
        - You can upload a new file anytime
        """)
    
    if st.session_state.generated_files:
        # Create zip file
        with st.spinner("Preparing download..."):
            zip_filename = f"temp/certificates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            with zipfile.ZipFile(zip_filename, 'w') as zipf:
                for pdf_path in st.session_state.generated_files:
                    if os.path.exists(pdf_path):
                        # Add file to zip with just the filename (not full path)
                        arcname = os.path.basename(pdf_path)
                        zipf.write(pdf_path, arcname)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with open(zip_filename, 'rb') as f:
                st.download_button(
                    label="📥 Download All Certificates",
                    data=f,
                    file_name=f"certificates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    help="Click to download a zip file containing all your certificates"
                )
            
            st.info(f"✅ Ready: {len(st.session_state.generated_files)} certificates in your download")
            
            # Navigation buttons for completion
            col_start, col_save = st.columns(2)
            with col_start:
                if st.button("🎆 Create More Certificates", use_container_width=True):
                    # Clear workflow state
                    clear_workflow_state()
                    # Reset workflow
                    st.session_state.workflow_step = 1
                    st.session_state.uploaded_file = None
                    st.session_state.validated_data = None
                    st.session_state.selected_template = None
                    st.session_state.file_upload_state = 'ready'
                    st.session_state.upload_key = st.session_state.get('upload_key', 0) + 1
                    st.session_state.show_uploader = False
                    st.session_state.generated_files = []
                    st.rerun()
            with col_save:
                if st.button("💾 Save This Session", use_container_width=True):
                    save_workflow_state()
                    st.success("Session saved!")


def logout_action():
    """Logout action page"""
    st.title("Logout")
    st.write("Are you sure you want to logout?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Logout", type="primary", use_container_width=True):
            logout()
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.info("Logout cancelled")


def render_dashboard():
    """Render main dashboard"""
    st.title("Dashboard")
    st.markdown("Welcome to the SafeSteps Admin Dashboard")
    
    # Stats cards using native Streamlit components
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.container(border=True):
            st.metric(
                label="Total Certificates",
                value="0",
                help="No certificates generated yet"
            )
    
    with col2:
        # Get actual user count
        active_users = len([u for u in list_users(include_inactive=False) if u.is_active])
        with st.container(border=True):
            st.metric(
                label="Active Users",
                value=str(active_users)
            )
    
    with col3:
        with st.container(border=True):
            st.metric(
                label="Templates",
                value="1",
                help="Programmatic Certificate"
            )
    
    with col4:
        with st.container(border=True):
            st.metric(
                label="This Month",
                value="0",
                help="No certificates this month"
            )
    
    # Action cards
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 📄 Manage Templates")
            st.markdown("Upload, edit, or remove certificate templates")
            if st.button("Go to Templates", key="quick_templates", use_container_width=True):
                # Use st.session_state to trigger navigation
                st.session_state.navigate_to = "Templates"
                st.rerun()
    
    with col2:
        with st.container(border=True):
            st.markdown("### 📚 Manage Courses")
            st.markdown("Create and manage course templates")
            if st.button("Go to Courses", key="quick_courses", use_container_width=True):
                # Use st.session_state to trigger navigation
                st.session_state.navigate_to = "Courses"
                st.rerun()
    
    with col3:
        with st.container(border=True):
            st.markdown("### 👥 Manage Users")
            st.markdown("View and manage user accounts and permissions")
            if st.button("Go to Users", key="quick_users", use_container_width=True):
                # Use st.session_state to trigger navigation
                st.session_state.navigate_to = "Users"
                st.rerun()
    
    # Recent activity
    st.subheader("Recent Activity")
    with st.container(border=True):
        st.info("📋 No recent activity - start generating certificates to see activity here!")


def render_templates_page():
    """Render templates management page with enhanced UI/UX"""
    from utils.ui_components import (
        create_header, create_card, create_empty_state,
        create_status_badge, create_action_menu, COLORS
    )
    
    create_header(
        "Template Management",
        "Upload and manage certificate templates",
        get_current_user()
    )
    
    # Quick actions bar - simplified for programmatic only
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("🎨 SafeSteps now uses programmatic certificate generation only")
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    # Upload feature removed - programmatic generation only
    
    # Template validation feature removed - programmatic generation only
    
    # Existing templates section
    # Use native header instead of HTML
    st.subheader("📄 Template Library")
    
    try:
        # Get templates - Use programmatic certificate
        templates = [{"name": "Programmatic Certificate", "filename": "programmatic", "path": "programmatic", "created": "2025-07-30", "size": 0}]
        
        # No search filtering needed for single programmatic template
        
        if not templates:
            st.info("🎨 SafeSteps uses programmatic certificate generation - no templates needed!")
        else:
            # Template grid view
            cols_per_row = 3
            for i in range(0, len(templates), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, template in enumerate(templates[i:i+cols_per_row]):
                    with cols[j]:
                        # Template card
                        display_name = template.get('display_name', template.get('name', 'Unknown'))
                        description = template.get('description', 'No description available')
                        size_kb = template.get('size', 0) / 1024 if template.get('size') else 0
                        
                        # Use native container and components instead of HTML
                        with st.container(border=True):
                            st.subheader(display_name)
                            st.caption(description)
                            
                            # Template metadata
                            col_meta1, col_meta2 = st.columns(2)
                            with col_meta1:
                                st.caption(f"📁 {template.get('filename', 'Unknown file')}")
                            with col_meta2:
                                st.caption(f"💾 {size_kb:.1f} KB")
                            
                            # Status badge using native component
                            st.success("✅ Active")
                        
                        # Action buttons
                        col_preview, col_delete = st.columns(2)
                        
                        with col_preview:
                            if st.button(
                                "👁️ Preview",
                                key=f"preview_{template['name']}",
                                use_container_width=True
                            ):
                                # PDF template preview removed - programmatic generation only
                                st.info("Preview not available - using programmatic generation")
                        
                        with col_delete:
                            st.caption("🔒 Protected")  # Programmatic template cannot be deleted
            
            # Summary stats
            st.divider()  # Use native divider instead of HTML
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Templates", len(templates))
            with col2:
                total_size = sum(t.get('size', 0) for t in templates) / (1024 * 1024)
                st.metric("Total Size", f"{total_size:.1f} MB")
            with col3:
                st.metric("Available Slots", "Unlimited" if len(templates) < 50 else f"{50 - len(templates)}")
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                    
                    with col1:
                        display_name = template.get('display_name', template.get('name', 'Unknown'))
                        st.markdown(f"**{display_name}**")
                        if template.get('description'):
                            st.caption(template['description'])
                    
                    with col2:
                        st.caption(f"📁 {template.get('filename', 'Unknown file')}")
                        if template.get('size'):
                            st.caption(f"Size: {template['size'] / 1024:.1f} KB")
                    
                    with col3:
                        if template.get('created'):
                            try:
                                created_date = datetime.fromisoformat(template['created'].replace('Z', '+00:00'))
                                st.caption(f"📅 {created_date.strftime('%Y-%m-%d')}")
                            except:
                                pass
                    
                    with col4:
                        # Action buttons in a vertical layout
                        if st.button("👁️ Preview", key=f"preview_{template['name']}"):
                            # PDF template preview removed - programmatic generation only
                            st.info("Preview not available - using programmatic generation")
                        
                        if st.button("🗑️ Delete", key=f"delete_{template['name']}"):
                            if storage.delete_template(template['name']):
                                st.success(f"Template '{display_name}' deleted")
                                st.rerun()
                            else:
                                st.error("Failed to delete template")
                    
                    st.divider()
                    
    except Exception as e:
        st.error(f"Error loading templates: {str(e)}")
        logger.error(f"Template listing error: {e}")


def render_courses_page():
    """Render course management page with enhanced UI/UX"""
    from utils.ui_components import (
        create_header, create_card, create_empty_state,
        create_status_badge, create_action_menu, COLORS
    )
    
    # Migrate default courses if needed
    if not course_manager.courses:
        migrated = course_manager.migrate_default_courses()
        if migrated > 0:
            st.info(f"Initialized {migrated} default courses")
    
    create_header(
        "Course Management",
        "Create and manage course templates for certificate generation",
        get_current_user()
    )
    
    # Quick actions bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input(
            "Search courses",
            placeholder="🔍 Search by name or description...",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("➕ Add Course", type="primary", use_container_width=True):
            st.session_state.show_add_course_form = True
    with col3:
        # Statistics button
        if st.button("📊 Statistics", use_container_width=True):
            st.session_state.show_course_stats = not st.session_state.get('show_course_stats', False)
    
    # Show statistics if toggled
    if st.session_state.get('show_course_stats', False):
        stats = course_manager.get_statistics()
        # Use native container instead of HTML
        with st.container(border=True):
            st.subheader("📊 Course Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Courses", stats.get('total_courses', 0))
            with col2:
                st.metric("Total Usage", stats.get('total_usage', 0))
            with col3:
                st.metric("Courses Used", stats.get('courses_with_usage', 0))
            with col4:
                st.metric("Unused Courses", stats.get('courses_without_usage', 0))
            
            if stats.get('most_used_course'):
                st.markdown(f"**Most Used:** {stats['most_used_course']['name']} ({stats['most_used_course']['usage_count']} uses)")
            
            pass  # Container automatically closes
    
    # Add new course modal
    if st.session_state.get('show_add_course_form', False):
        # Use native container instead of HTML
        with st.container(border=True):
            st.subheader("➕ Add New Course")
            st.caption("Create a new course template for certificate generation")
            
            with st.form("add_course_form"):
                course_name = st.text_input(
                    "Course Name",
                    placeholder="e.g., Digital Citizenship",
                    help="Enter a descriptive name for the course"
                )
                
                course_description = st.text_area(
                    "Course Description",
                    placeholder="Describe what this course covers and when it should be used...",
                    help="Provide a clear description to help users understand the course content"
                )
                
                col_submit, col_cancel = st.columns(2)
                with col_submit:
                    submit_button = st.form_submit_button("💾 Save Course", type="primary", use_container_width=True)
                with col_cancel:
                    cancel_button = st.form_submit_button("Cancel", use_container_width=True)
                
                if cancel_button:
                    st.session_state.show_add_course_form = False
                    st.rerun()
                
                if submit_button:
                    if not course_name:
                        st.error("Please provide a course name")
                    elif not course_description:
                        st.error("Please provide a course description")
                    else:
                        # Create the course
                        new_course = course_manager.create_course(
                            name=course_name,
                            description=course_description,
                            created_by=get_current_user()['username']
                        )
                        
                        if new_course:
                            st.success(f"Course '{course_name}' created successfully!")
                            # Activity logging removed - function not defined
                            st.session_state.show_add_course_form = False
                            st.rerun()
                        else:
                            st.error("Failed to create course. It may already exist.")
            
            pass  # Container automatically closes
    
    # Course list
    st.subheader("Course Library")
    
    # Get courses based on search
    if search_query:
        courses = course_manager.search_courses(search_query)
    else:
        courses = course_manager.list_courses(sort_by='name', reverse=False)
    
    if not courses:
        create_empty_state(
            "No courses found",
            "Get started by adding your first course template",
            "➕ Add Course"
        )
    else:
        # Create course cards
        for i in range(0, len(courses), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(courses):
                    course = courses[i + j]
                    with cols[j]:
                        # Use native container instead of HTML
                        with st.container(border=True):
                            # Course card
                            st.subheader(course['name'])
                            st.caption(course['description'])
                            
                            # Course metadata
                            col_usage, col_created = st.columns(2)
                            with col_usage:
                                st.caption(f"📊 {course.get('usage_count', 0)} uses")
                            with col_created:
                                created_date = datetime.fromisoformat(course['created_at']).strftime("%b %d, %Y")
                                st.caption(f"📅 {created_date}")
                            
                            # Last used info
                            if course.get('last_used'):
                                last_used = datetime.fromisoformat(course['last_used']).strftime("%b %d, %Y")
                                st.caption(f"Last used: {last_used}")
                            else:
                                st.caption("Never used")
                            
                            # Action buttons
                            col_edit, col_delete = st.columns(2)
                            with col_edit:
                                if st.button("✏️ Edit", key=f"edit_{course['id']}", use_container_width=True):
                                    st.session_state.edit_course_id = course['id']
                                    st.session_state.show_edit_course_form = True
                            
                            with col_delete:
                                # Only allow deletion of unused courses
                                if course.get('usage_count', 0) == 0:
                                    if st.button("🗑️ Delete", key=f"delete_{course['id']}", use_container_width=True):
                                        st.session_state.delete_course_id = course['id']
                                        st.session_state.show_delete_confirm = True
                                else:
                                    st.button("🔒 In Use", key=f"locked_{course['id']}", disabled=True, use_container_width=True)
                            
                            pass  # Container automatically closes
    
    # Edit course modal
    if st.session_state.get('show_edit_course_form', False) and st.session_state.get('edit_course_id'):
        course_id = st.session_state.edit_course_id
        course = course_manager.get_course(course_id)
        
        if course:
            # Use native container instead of HTML
            with st.container(border=True):
                st.subheader("✏️ Edit Course")
                
                with st.form("edit_course_form"):
                    course_name = st.text_input(
                        "Course Name",
                        value=course['name'],
                        help="Enter a descriptive name for the course"
                    )
                    
                    course_description = st.text_area(
                        "Course Description",
                        value=course['description'],
                        help="Provide a clear description to help users understand the course content"
                    )
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submit_button = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
                    with col_cancel:
                        cancel_button = st.form_submit_button("Cancel", use_container_width=True)
                    
                    if cancel_button:
                        st.session_state.show_edit_course_form = False
                        st.session_state.edit_course_id = None
                        st.rerun()
                    
                    if submit_button:
                        if not course_name:
                            st.error("Course name cannot be empty")
                        elif not course_description:
                            st.error("Course description cannot be empty")
                        else:
                            # Update the course
                            updated_course = course_manager.update_course(
                                course_id=course_id,
                                name=course_name,
                                description=course_description
                            )
                            
                            if updated_course:
                                st.success(f"Course '{course_name}' updated successfully!")
                                # Activity logging removed - function not defined
                                st.session_state.show_edit_course_form = False
                                st.session_state.edit_course_id = None
                                st.rerun()
                            else:
                                st.error("Failed to update course. The name may already be in use.")
                
                pass  # Container automatically closes
    
    # Delete confirmation modal
    if st.session_state.get('show_delete_confirm', False) and st.session_state.get('delete_course_id'):
        course_id = st.session_state.delete_course_id
        course = course_manager.get_course(course_id)
        
        if course:
            # Use native container with warning styling
            with st.container(border=True):
                st.subheader("🗑️ Delete Course?")
                st.warning(f"Are you sure you want to delete the course **{course['name']}**? This action cannot be undone.")
                
                col_confirm, col_cancel = st.columns(2)
                with col_confirm:
                    if st.button("🗑️ Delete", type="primary", use_container_width=True):
                        if course_manager.delete_course(course_id):
                            st.success(f"Course '{course['name']}' deleted successfully!")
                            # Activity logging removed - function not defined
                            st.session_state.show_delete_confirm = False
                            st.session_state.delete_course_id = None
                            st.rerun()
                        else:
                            st.error("Failed to delete course")
                
                with col_cancel:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.show_delete_confirm = False
                        st.session_state.delete_course_id = None
                        st.rerun()
                
                pass  # Container automatically closes


def render_users_page():
    """Render users management page"""
    st.title("User Management")
    
    # Tabs for different user management functions
    tab1, tab2 = st.tabs(["User List", "Add New User"])
    
    with tab1:
        # Display all users
        st.subheader("All Users")
        
        # Get users list
        users = list_users(include_inactive=True)
        
        if not users:
            st.info("No users found. Create the first user using the 'Add New User' tab.")
        else:
            # Create a table of users
            for user in users:
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 2])
                    
                    with col1:
                        st.text(user.username)
                    
                    with col2:
                        st.text(user.email)
                    
                    with col3:
                        st.text(user.role.upper())
                    
                    with col4:
                        status_text = "Active" if user.is_active else "Inactive"
                        if user.is_active:
                            st.success(status_text)
                        else:
                            st.error(status_text)
                    
                    with col5:
                        # Last login
                        if user.last_login:
                            try:
                                last_login = datetime.fromisoformat(user.last_login)
                                st.text(last_login.strftime("%Y-%m-%d"))
                            except:
                                st.text("Never")
                        else:
                            st.text("Never")
                    
                    with col6:
                        # Action buttons
                        button_col1, button_col2, button_col3 = st.columns(3)
                        
                        with button_col1:
                            if st.button("Edit", key=f"edit_{user.user_id}"):
                                st.session_state.editing_user = user.user_id
                        
                        with button_col2:
                            if user.is_active:
                                if st.button("Deactivate", key=f"deactivate_{user.user_id}"):
                                    toggle_user_status(user.user_id)
                                    st.rerun()
                            else:
                                if st.button("Activate", key=f"activate_{user.user_id}"):
                                    toggle_user_status(user.user_id)
                                    st.rerun()
                        
                        with button_col3:
                            # Check if this is the last admin
                            admin_count = sum(1 for u in users if u.role == 'admin' and u.is_active)
                            if not (user.role == 'admin' and admin_count <= 1):
                                if st.button("Delete", key=f"delete_{user.user_id}"):
                                    if delete_user(user.user_id):
                                        st.success(f"User {user.username} deleted successfully")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete user")
                    
                    # Edit user form (if editing)
                    if st.session_state.get('editing_user') == user.user_id:
                        with st.expander("Edit User", expanded=True):
                            with st.form(f"edit_form_{user.user_id}"):
                                new_role = st.selectbox(
                                    "Role",
                                    options=["user", "admin"],
                                    index=0 if user.role == "user" else 1
                                )
                                
                                new_password = st.text_input(
                                    "New Password (leave empty to keep current)",
                                    type="password"
                                )
                                
                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    if st.form_submit_button("Save Changes"):
                                        # Update role if changed
                                        if new_role != user.role:
                                            update_user_role(user.user_id, new_role)
                                        
                                        # Update password if provided
                                        if new_password:
                                            try:
                                                reset_user_password(user.user_id, new_password)
                                                st.success("User updated successfully")
                                            except ValueError as e:
                                                st.error(str(e))
                                        
                                        del st.session_state.editing_user
                                        st.rerun()
                                
                                with col_cancel:
                                    if st.form_submit_button("Cancel"):
                                        del st.session_state.editing_user
                                        st.rerun()
                    
                    st.divider()
    
    with tab2:
        # Add new user form
        st.subheader("Add New User")
        
        with st.form("add_user_form"):
            new_username = st.text_input("Username", placeholder="johndoe")
            new_email = st.text_input("Email", placeholder="john.doe@example.com")
            new_password = st.text_input("Password", type="password", placeholder="Enter a strong password")
            new_role = st.selectbox("Role", options=["user", "admin"])
            
            if st.form_submit_button("Create User"):
                if not new_username:
                    st.error("Username is required")
                elif not new_email:
                    st.error("Email is required")
                elif not new_password:
                    st.error("Password is required")
                else:
                    try:
                        user = create_user(new_username, new_email, new_password, new_role)
                        if user:
                            st.success(f"User {new_username} created successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to create user. Username or email may already exist.")
                    except ValueError as e:
                        st.error(str(e))


def render_analytics_page():
    """Render analytics page"""
    st.title("Analytics")
    st.info("Analytics dashboard coming soon!")


def render_settings_page():
    """Render settings page"""
    st.title("System Settings")
    
    with st.form("settings_form"):
        st.subheader("Application Settings")
        
        app_name = st.text_input("Application Name", value=config.app.app_name)
        session_timeout = st.number_input(
            "Session Timeout (minutes)",
            value=config.auth.session_timeout_minutes,
            min_value=5,
            max_value=120
        )
        
        st.subheader("Security Settings")
        enable_csrf = st.checkbox(
            "Enable CSRF Protection",
            value=config.auth.enable_csrf_protection
        )
        
        rate_limit = st.number_input(
            "Rate Limit (requests per minute)",
            value=config.rate_limit.requests_limit,
            min_value=10,
            max_value=100
        )
        
        if st.form_submit_button("Save Settings"):
            st.success("Settings saved successfully!")


def render_admin_certificate_generation():
    """Render certificate generation interface for admins"""
    st.title("🏆 Generate Certificates")
    st.markdown("As an admin, you can access the certificate generation workflow to help users or generate certificates directly.")
    
    # Add admin note
    st.info("💡 **Admin Access**: You are accessing the certificate generation workflow with administrative privileges.")
    
    # Initialize workflow state if not exists
    if 'admin_workflow_step' not in st.session_state:
        st.session_state.admin_workflow_step = 1
        st.session_state.admin_uploaded_file = None
        st.session_state.admin_validated_data = None
        st.session_state.admin_selected_template = None
        st.session_state.admin_generated_files = []
        st.session_state.admin_show_uploader = False
        st.session_state.admin_upload_key = 0
    
    # Get current user
    user = get_current_user()
    
    # Header with admin context
    # Use native container instead of HTML card
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("### Certificate Generation Workflow")
    with col2:
        st.markdown(f"**Admin:** {user['username']}")
    with col3:
        if st.button("Reset Workflow", type="secondary"):
            # Reset admin workflow state
            for key in ['admin_workflow_step', 'admin_uploaded_file', 'admin_validated_data', 'admin_selected_template', 'admin_generated_files']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.admin_workflow_step = 1
            st.rerun()
    # Container automatically closes
    
    # Progress bar for admin workflow
    render_admin_progress_bar(st.session_state.admin_workflow_step)
    
    # Step content - using the same workflow but with admin prefix
    if st.session_state.admin_workflow_step == 1:
        admin_step1_upload()
    elif st.session_state.admin_workflow_step == 2:
        admin_step2_validate()
    elif st.session_state.admin_workflow_step == 3:
        admin_step3_template()
    elif st.session_state.admin_workflow_step == 4:
        admin_step4_generate()
    elif st.session_state.admin_workflow_step == 5:
        admin_step5_complete()


def render_admin_progress_bar(current_step):
    """Render progress bar for admin workflow"""
    steps = [
        ("Upload Data", "📤", 1),
        ("Validate", "✅", 2),
        ("Template", "📄", 3),
        ("Generate", "🏆", 4),
        ("Complete", "🎉", 5)
    ]
    
    create_progress_steps(steps, current_step)


def admin_step1_upload():
    """Admin Step 1: File Upload"""
    # Use native container instead of HTML card
    st.header("Step 1: Upload Data File")
    
    # Use native components instead of HTML
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("# 📁")
            st.markdown("### Drop your file here")
            st.markdown("or click to browse")
            st.info("**Supported:** CSV, Excel (.xlsx, .xls)")
    
    # Initialize admin upload state
    if 'admin_show_uploader' not in st.session_state:
        st.session_state.admin_show_uploader = False
    
    # Check if we already have an uploaded file
    if 'admin_uploaded_file' in st.session_state and st.session_state.admin_uploaded_file is not None:
        # Show uploaded file status and continue button
        st.success(f"✅ File uploaded: {st.session_state.admin_uploaded_file.name}")
        st.info(f"📊 File size: {st.session_state.admin_uploaded_file.size:,} bytes")
        
        if st.button("Continue to Validation", type="primary", use_container_width=True):
            st.session_state.admin_workflow_step = 2
            st.rerun()
        
        # Option to upload different file
        st.markdown("---")
        if st.button("📁 Upload Different File"):
            st.session_state.admin_uploaded_file = None
            st.session_state.admin_show_uploader = False
            st.rerun()
    else:
        # Show button to reveal file uploader
        if not st.session_state.admin_show_uploader:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col2:
                if st.button("📁 Choose File to Upload", type="primary", use_container_width=True):
                    st.session_state.admin_show_uploader = True
                    st.rerun()
        else:
            # Show the actual file uploader
            st.info("📎 Click 'Browse files' below to select your CSV/Excel file")
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['csv', 'xlsx', 'xls'],
                help="Upload a CSV or Excel file with participant data",
                key=f"admin_file_upload_{st.session_state.get('admin_upload_key', 0)}"
            )
            
            # Cancel button to hide uploader
            if st.button("Cancel"):
                st.session_state.admin_show_uploader = False
                st.rerun()
            
            if uploaded_file is not None:
                st.session_state.admin_uploaded_file = uploaded_file
                st.session_state.admin_show_uploader = False
                st.session_state.admin_upload_key = st.session_state.get('admin_upload_key', 0) + 1
                st.rerun()


def admin_step2_validate():
    """Admin Step 2: Data Validation"""
    # Use native container instead of HTML card
    st.header("Step 2: Validate Data")
    
    if st.session_state.admin_uploaded_file is None:
        st.error("No file uploaded. Please go back to Step 1.")
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state.admin_workflow_step = 1
            st.rerun()
        # Container automatically closes
        return
    
    # Validate the uploaded file
    try:
        validator = SpreadsheetValidator()
        validation_result = validator.validate_file(st.session_state.admin_uploaded_file)
        
        if validation_result.valid:
            st.session_state.admin_validated_data = validation_result.cleaned_data
            st.success("✅ Data validation successful!")
            
            # Show preview of data
            st.subheader("📋 Data Preview")
            st.dataframe(validation_result.cleaned_data.head(10), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Upload", use_container_width=True):
                    st.session_state.admin_workflow_step = 1
                    st.rerun()
            with col2:
                if st.button("Continue to Template →", type="primary", use_container_width=True):
                    st.session_state.admin_workflow_step = 3
                    st.rerun()
        else:
            st.error("❌ Data validation failed!")
            for error in validation_result.errors:
                st.error(f"• {error}")
            
            if st.button("← Back to Upload", use_container_width=True):
                st.session_state.admin_workflow_step = 1
                st.rerun()
                
    except Exception as e:
        import traceback
        st.error(f"Error during validation: {str(e)}")
        
        # Show detailed traceback for debugging
        with st.expander("🔍 Debug Information"):
            st.code(traceback.format_exc())
            
        if st.button("← Back to Upload", use_container_width=True):
            st.session_state.admin_workflow_step = 1
            st.rerun()


def admin_step3_template():
    """Admin Step 3: Template Selection"""
    # Use native container instead of HTML card
    st.header("Step 3: Choose Template")
    
    if st.session_state.admin_validated_data is None:
        st.error("No validated data. Please complete previous steps.")
        if st.button("← Back to Validation", use_container_width=True):
            st.session_state.admin_workflow_step = 2
            st.rerun()
        # Container automatically closes
        return
    
    # Template auto-selected - Use programmatic certificate
    # Since we only have one template, auto-select it
    template = {
        "name": "Programmatic Certificate", 
        "filename": "programmatic", 
        "path": "programmatic", 
        "display_name": "Programmatic Certificate"
    }
    st.session_state.admin_selected_template = template
    
    # Show template status
    st.subheader("📋 Template Ready")
    st.success("✅ **Template Selected**: Programmatic Certificate")
    st.info("📋 Modern certificate design generated programmatically with your organization branding.")
    
    # Show template info card
    with st.container(border=True):
        col1, col2 = st.columns([1, 9])
        with col1:
            st.markdown("📄")
        with col2:
            st.markdown("**Programmatic Certificate**")
            st.caption("Modern, professional certificate design")
            st.caption("✅ Ready to use")
            
    # Course Selection
    st.subheader("📚 Course Selection")
    
    # Get available courses
    courses = storage.list_course_templates()
    
    if courses:
        # Create course options for selectbox
        course_options = {f"{course['name']}": course for course in courses}
        
        # Course selection
        selected_course_name = st.selectbox(
            "Select a course:",
            options=list(course_options.keys()),
            key="admin_selected_course",
            help="Choose the course that participants completed"
        )
        
        if selected_course_name:
            selected_course = course_options[selected_course_name]
            st.session_state.admin_selected_course_info = selected_course
            
            # Show course details
            col1, col2 = st.columns([3, 1])
            with col1:
                if selected_course.get('description'):
                    st.info(f"📝 **Description**: {selected_course['description']}")
            with col2:
                if selected_course.get('usage_count', 0) > 0:
                    st.metric("Usage Count", selected_course['usage_count'])
        else:
            st.warning("No courses available. Using default course.")
            # Provide default course for backward compatibility
            st.session_state.admin_selected_course_info = {
                'name': 'Vapes and Vaping',
                'id': 'default_course',
                'description': 'Default course'
            }
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Validation", use_container_width=True):
                    st.session_state.admin_workflow_step = 2
                    st.rerun()
            with col2:
                # Check if both template and course are selected
                has_course = st.session_state.get('admin_selected_course_info') is not None
                if has_course:
                    if st.button("Continue to Generate →", type="primary", use_container_width=True):
                        st.session_state.admin_workflow_step = 4
                        st.rerun()
                else:
                    st.error("Please select a course to continue")


def admin_step4_generate():
    """Admin Step 4: Generate Certificates"""
    # Use native container instead of HTML card
    st.header("Step 4: Generate Certificates")
    
    # Initialize session state if needed
    if 'admin_validated_data' not in st.session_state:
        st.session_state.admin_validated_data = None
    if 'admin_selected_template' not in st.session_state:
        st.session_state.admin_selected_template = None
    if 'admin_generated_files' not in st.session_state:
        st.session_state.admin_generated_files = []
    
    if st.session_state.admin_selected_template is None:
        st.error("No template selected. Please complete previous steps.")
        if st.button("← Back to Template", use_container_width=True):
            st.session_state.admin_workflow_step = 3
            st.rerun()
        # Container automatically closes
        return
    
    # Show generation summary
    st.subheader("📋 Generation Summary")
    
    # Get course info
    course_info = st.session_state.get('admin_selected_course_info', {})
    course_name = course_info.get('name', 'Vapes and Vaping')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Participants:** {len(st.session_state.admin_validated_data)}")
    with col2:
        # Use display_name if available, otherwise fallback to name
        template_display_name = st.session_state.admin_selected_template.get('display_name', 
                                                                           st.session_state.admin_selected_template.get('name', 'Unknown Template'))
        st.info(f"**Template:** {template_display_name}")
    with col3:
        st.info(f"**Course:** {course_name}")
    
    # Generate button
    if 'admin_generated_files' not in st.session_state:
        st.session_state.admin_generated_files = []
    
    if len(st.session_state.admin_generated_files) == 0:
        if st.button("🏆 Generate Certificates", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Get template path using storage manager
                template_name = st.session_state.admin_selected_template.get('name')
                if not template_name:
                    st.error("Template name not found. Please select a valid template.")
                    return
                
                # Use programmatic generation only
                from certificate_generator_production import generate_certificate_for_app
                
                # Prepare recipients data
                recipients = []
                for idx, row in st.session_state.admin_validated_data.iterrows():
                    # Handle various column name formats
                    first_name = row.get('first_name', row.get('First Name', row.get('first name', row.get('FirstName', ''))))
                    last_name = row.get('last_name', row.get('Last Name', row.get('last name', row.get('LastName', ''))))
                    
                    if first_name or last_name:
                        recipients.append({
                            'first_name': str(first_name).strip(),
                            'last_name': str(last_name).strip()
                        })
                
                if not recipients:
                    st.error("No valid recipients found in the data.")
                    return
                
                # Generate certificates using simple iteration (matching user workflow)
                generated_files = []
                total = len(recipients)
                
                for i, recipient in enumerate(recipients):
                    try:
                        progress = (i + 1) / total
                        progress_bar.progress(progress)
                        status_text.text(f"Generating certificate {i + 1} of {total} for {recipient['first_name']} {recipient['last_name']}")
                        
                        # Get course info
                        course_info = st.session_state.get('admin_selected_course_info', {})
                        course_name = course_info.get('name', 'Vapes and Vaping')
                        
                        # Generate certificate using programmatic generation
                        pdf_bytes = generate_certificate_for_app(
                            student_name=f"{recipient['first_name']} {recipient['last_name']}".strip(),
                            course_name=course_name,
                            score="Pass",
                            completion_date=datetime.now().strftime("%B %d, %Y")
                        )
                        
                        filename = f"{recipient['first_name']}_{recipient['last_name']}_certificate.pdf"
                        generated_files.append({
                            'name': filename,
                            'content': pdf_bytes
                        })
                        
                    except Exception as e:
                        st.error(f"Error generating certificate for {recipient['first_name']} {recipient['last_name']}: {str(e)}")
                
                st.session_state.admin_generated_files = generated_files
                
                # Log certificate generation
                storage.log_certificate_generation(
                    user=get_current_user()['username'],
                    template=template_display_name,
                    count=len(generated_files)
                )
                
                # Update course usage count
                course_info = st.session_state.get('admin_selected_course_info', {})
                course_id = course_info.get('id')
                if course_id and course_id != 'default_course':
                    # Increment usage by the number of certificates generated
                    for _ in range(len(generated_files)):
                        storage.increment_course_usage(course_id)
                
                progress_bar.progress(1.0)
                status_text.text("Complete!")
                st.success(f"✅ Successfully generated {len(generated_files)} certificates!")
                
                time.sleep(1)
                st.session_state.admin_workflow_step = 5
                st.rerun()
                
            except Exception as e:
                st.error(f"Error generating certificates: {str(e)}")
                logger.error(f"Admin certificate generation error: {e}")
    else:
        st.success("✅ Certificates have been generated!")
        if st.button("View Results →", type="primary", use_container_width=True):
            st.session_state.admin_workflow_step = 5
            st.rerun()
    
    # Back button
    if st.button("← Back to Template", use_container_width=True):
        st.session_state.admin_workflow_step = 3
        st.rerun()
    
    # Container automatically closes


def admin_step5_complete():
    """Admin Step 5: Completion"""
    # Use native container instead of HTML card
    st.header("🎉 Certificates Generated Successfully!")
    
    # Initialize session state if needed
    if 'admin_generated_files' not in st.session_state:
        st.session_state.admin_generated_files = []
    
    if st.session_state.admin_generated_files:
        st.success(f"Generated {len(st.session_state.admin_generated_files)} certificates")
        
        # Download options
        st.subheader("📥 Download Options")
        
        # Individual downloads
        with st.expander("Individual Certificate Downloads"):
            for i, cert_file in enumerate(st.session_state.admin_generated_files):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text(f"Certificate {i+1}: {cert_file['name']}")
                with col2:
                    st.download_button(
                        "Download",
                        data=cert_file['content'],
                        file_name=cert_file['name'],
                        mime="application/pdf",
                        key=f"admin_download_{i}"
                    )
        
        # Batch download as ZIP
        zip_data = create_zip_archive(st.session_state.admin_generated_files)
        st.download_button(
            "📦 Download All Certificates as ZIP",
            data=zip_data,
            file_name=f"certificates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
    
    # Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Generate New Batch", use_container_width=True):
            # Reset workflow
            for key in ['admin_workflow_step', 'admin_uploaded_file', 'admin_validated_data', 'admin_selected_template', 'admin_generated_files']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.admin_workflow_step = 1
            st.rerun()
    
    with col2:
        if st.button("📊 Back to Dashboard", use_container_width=True):
            # Go back to dashboard
            st.session_state.admin_workflow_step = 1
            st.rerun()


def create_zip_archive(files):
    """Create a ZIP archive from a list of files"""
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_data in files:
            zip_file.writestr(file_data['name'], file_data['content'])
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def main():
    """Main application entry point with modern navigation"""
    # Apply global mobile optimizations first
    apply_custom_css()
    mobile_optimizer = apply_global_mobile_optimizations()
    
    # Initialize session state for navigation
    if 'current_page' not in st.session_state:
        st.session_state.current_page = None
    
    # Display deployment info in sidebar
    with st.sidebar:
        deployment_info = get_deployment_info()
        st.caption(f"{DEPLOYMENT_VERSION}")
        st.caption(f"Commit: {deployment_info['commit'][:7]} | Env: {deployment_info['environment']}")
    
    # Check authentication and determine available pages
    if not is_session_valid():
        # User not authenticated - show only login
        login_page_func = st.Page(login_page, title="Login", icon="🔐")
        pg = st.navigation([login_page_func])
    else:
        user = get_current_user()
        
        # Version selector removed - only use working version
        
        if user and user.get("role") == "admin":
            # Admin user - show admin navigation
            # Always use the working dashboard - other versions were removed
            dashboard_page = st.Page(render_dashboard, title="Dashboard", icon="📊", default=True)
            
            # Import certificate generation with help system
            from pages.certificate_generation_with_help import render_certificate_generation
            cert_gen_with_help = st.Page(render_certificate_generation, title="🏆 Certificate Generator", icon="🏆")
            
            # Import Express Mode
            from pages.express_mode import render_express_mode
            express_page = st.Page(render_express_mode, title="⚡ Express Mode", icon="⚡")
            
            generate_page = st.Page(render_admin_certificate_generation, title="Legacy Generate", icon="📋")
            templates_page = st.Page(render_templates_page, title="Templates", icon="📄")
            courses_page = st.Page(render_courses_page, title="Courses", icon="📚")
            users_page = st.Page(render_users_page, title="Users", icon="👥")
            analytics_page = st.Page(render_analytics_page, title="Analytics", icon="📈")
            settings_page = st.Page(render_settings_page, title="Settings", icon="⚙️")
            
            # Workflow engine demo removed
            
            logout_page = st.Page(logout_action, title="Logout", icon="🚪")
            
            pg = st.navigation({
                "Certificate Generation": [cert_gen_with_help, express_page, generate_page],
                "Admin": [dashboard_page, templates_page, courses_page, users_page],
                "System": [analytics_page, settings_page, logout_page]
            })
        else:
            # Regular user - ONE SIMPLE workflow only
            generate_page = st.Page(user_workflow, title="🏆 Generate Certificates", icon="🏆", default=True)
                
            logout_page = st.Page(logout_action, title="Logout", icon="🚪")
            
            pg = st.navigation({
                "Certificate Generator": [generate_page],
                "Account": [logout_page]
            })
    
    # Handle navigation from dashboard quick actions
    if hasattr(st.session_state, 'navigate_to'):
        target_page = st.session_state.navigate_to
        del st.session_state.navigate_to
        
        # Switch to the requested page if it exists in navigation
        user = get_current_user()
        if user and user.get("role") == "admin":
            if target_page == "Templates":
                st.switch_page(templates_page)
            elif target_page == "Courses":
                st.switch_page(courses_page)
            elif target_page == "Users":
                st.switch_page(users_page)
    
    # Run the selected page
    pg.run()


if __name__ == "__main__":
    main()