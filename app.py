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
from utils.pdf_generator import PDFGenerator
from utils.storage import StorageManager
from utils.deployment_info import get_deployment_info
from utils.ui_components import apply_custom_css, create_progress_steps, COLORS
from utils.course_manager import CourseManager
from config import config
import time

# Initialize storage manager
storage = StorageManager()

# Initialize course manager
course_manager = CourseManager(storage.local_path / "metadata")

# Page configuration
st.set_page_config(
    page_title="SafeSteps Certificate Generator",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
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
                                    log_activity("login", {"username": user['username'], "role": role})
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
        st.session_state.generated_files = []
    
    # Get current user
    user = get_current_user()
    
    # Enhanced header
    col1, col2 = st.columns([5, 1])
    with col1:
        create_header(
            "Certificate Generator",
            "Follow the steps below to generate your certificates",
            user
        )
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
    """Step 1: File Upload with enhanced UI"""
    from utils.ui_components import create_card, COLORS
    
    # Step header using native components
    with st.container(border=True):
        st.subheader("Step 1: Upload Your Data")
        st.markdown("Upload a spreadsheet containing participant names")
    
    # Enhanced upload zone using native components
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("# 📁")
            st.markdown("### Drop your file here")
            st.markdown("or click to browse")
            st.info("**Supported:** CSV, Excel (.xlsx, .xls)")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✓ File uploaded: {uploaded_file.name}")
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Continue", type="primary", use_container_width=True):
                st.session_state.workflow_step = 2
                st.rerun()


def step2_validate():
    """Step 2: Data Validation with enhanced feedback"""
    from utils.ui_components import create_card, create_loading_animation, COLORS
    
    # Use native Streamlit components instead of HTML
    with st.container(border=True):
        st.header("Step 2: Validate Your Data")
        st.caption("Checking your file for required information")
    
    if not st.session_state.uploaded_file:
        st.error("📁 **No file uploaded**: Please go back to Step 1 to upload your data file.")
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("← Back to Upload", use_container_width=True):
                st.session_state.workflow_step = 1
                st.rerun()
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
            
            # Auto-advance with countdown
            countdown_placeholder = st.empty()
            for i in range(3, 0, -1):
                countdown_placeholder.info(f"🚀 **Auto-advancing to template selection in {i} seconds...** (Click below to continue immediately)")
                time.sleep(1)
            countdown_placeholder.empty()
            
            st.session_state.workflow_step = 3
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
                
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📁 Try Another File", use_container_width=True):
                    st.session_state.workflow_step = 1
                    st.session_state.uploaded_file = None
                    st.rerun()
            with col2:
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
            # Validate template accessibility
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
        
        # Display templates in improved grid
        st.subheader("📋 Available Templates")
        
        # Create responsive columns based on number of templates
        if len(validated_templates) == 1:
            cols = st.columns([1, 2, 1])
            display_cols = [cols[1]]  # Center single template
        elif len(validated_templates) == 2:
            display_cols = st.columns(2)
        else:
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
                if template_path and os.path.exists(template_path):
                    st.success("🟢 Template file verified and accessible")
                else:
                    st.error("🔴 Template file validation failed")
            
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
                
                if template_path and os.path.exists(template_path) and has_course:
                    if st.button("Continue to Generate →", type="primary", use_container_width=True):
                        st.session_state.workflow_step = 4
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
    """Step 4: Generate Certificates with enhanced UI"""
    from utils.ui_components import create_card, COLORS
    
    # Use native Streamlit components instead of HTML
    with st.container(border=True):
        st.header("Step 4: Generate Certificates")
        st.caption("Ready to create your certificates")
    
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
        
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button("Generate Certificates", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                generated_files = []
                total = len(st.session_state.validated_data)
                
                # Use programmatic certificate generator
                try:
                    # Check if using programmatic certificate
                    if st.session_state.selected_template == "Programmatic Certificate":
                        # Use programmatic generation - no template file needed
                        from certificate_generator_production import generate_certificate_for_app
                        use_programmatic = True
                    else:
                        # Legacy PDF template support
                        template_path = storage.get_template_path(st.session_state.selected_template)
                        if not template_path:
                            st.error("Template file not found. Please select a different template.")
                            return
                        generator = PDFGenerator(template_path)
                        use_programmatic = False
                    
                    # Validate template (skip for programmatic)
                    if not use_programmatic:
                        validation_info = generator.validate_template()
                        if not validation_info['valid']:
                            st.error("Template validation failed:")
                            for error in validation_info['errors']:
                                st.error(f"• {error}")
                            return
                        
                except Exception as e:
                    st.error(f"Error loading template: {str(e)}")
                    return
                
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
                        first_name = row.get('First Name', row.get('first name', row.get('FirstName', '')))
                        last_name = row.get('Last Name', row.get('last name', row.get('LastName', '')))
                        
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
                        
                        # Generate the certificate
                        if use_programmatic:
                            # Use programmatic generation
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
                        else:
                            # Use PDF template
                            pdf_path = generator.generate_certificate(
                                first_name=str(first_name).strip(),
                                last_name=str(last_name).strip(),
                                output_path=output_path,
                                additional_fields={'course': course_name}
                            )
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
        if st.button("Go Back"):
            st.session_state.workflow_step = 3
            st.rerun()


def step5_complete():
    """Step 5: Download Complete with enhanced celebration"""
    from utils.ui_components import COLORS
    
    # Use native Streamlit components instead of HTML
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("# 🎉")
            st.title("Certificates Generated Successfully!")
            st.caption("All certificates have been generated and are ready for download.")
    
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
                    use_container_width=True
                )
            
            if st.button("Generate More Certificates", use_container_width=True):
                # Reset workflow
                st.session_state.workflow_step = 1
                st.session_state.uploaded_file = None
                st.session_state.validated_data = None
                st.session_state.selected_template = None
                st.session_state.generated_files = []
                st.rerun()


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
                value="1,234"
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
                value="4"
            )
    
    with col4:
        with st.container(border=True):
            st.metric(
                label="This Month",
                value="89"
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
        activities = [
            ("User generated 25 certificates", "2 hours ago"),
            ("New template uploaded: Summer Workshop", "5 hours ago"),
            ("Admin updated system settings", "1 day ago"),
            ("Batch generation completed: 150 certificates", "2 days ago")
        ]
        
        for activity, time in activities:
            st.markdown(f"• {activity} - *{time}*")


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
    
    # Quick actions bar
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input(
            "Search templates",
            placeholder="🔍 Search by name or description...",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("📤 Upload Template", type="primary", use_container_width=True):
            st.session_state.show_upload_form = True
    with col3:
        if st.button("🔍 Validate PDF", use_container_width=True):
            st.session_state.show_validate_form = True
    
    # Upload new template modal
    if st.session_state.get('show_upload_form', False):
        # Use native container instead of HTML
        with st.container(border=True):
            st.subheader("📤 Upload New Template")
            st.caption("Add a new certificate template to your library")
        with st.form("upload_template_form"):
            uploaded_template = st.file_uploader(
                "Choose a PDF template",
                type=['pdf'],
                help="Select a PDF file with form fields for FirstName and LastName"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                template_name = st.text_input(
                    "Template Name",
                    placeholder="e.g., Professional Certificate",
                    help="A friendly name for this template"
                )
            with col2:
                template_filename = st.text_input(
                    "Filename (optional)",
                    placeholder="e.g., professional_cert",
                    help="Leave blank to auto-generate from template name"
                )
            
            template_description = st.text_area(
                "Template Description",
                placeholder="Describe when to use this template...",
                help="Optional description to help users choose the right template"
            )
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submit_button = st.form_submit_button("💾 Save Template", type="primary", use_container_width=True)
            with col_cancel:
                cancel_button = st.form_submit_button("Cancel", use_container_width=True)
            
            if cancel_button:
                st.session_state.show_upload_form = False
                st.rerun()
            
            if submit_button and uploaded_template:
                if not template_name:
                    st.error("Please provide a template name")
                else:
                    try:
                        # Generate filename if not provided
                        if not template_filename:
                            template_filename = template_name.lower().replace(" ", "_")
                        
                        # Ensure filename ends with .pdf
                        if not template_filename.endswith('.pdf'):
                            template_filename += '.pdf'
                        
                        # Prepare metadata
                        metadata = {
                            'display_name': template_name,
                            'description': template_description,
                            'uploaded_by': get_current_user()['username'],
                            'uploaded_at': datetime.now().isoformat()
                        }
                        
                        # Save template using storage manager
                        with st.spinner("Uploading template..."):
                            if storage.save_template(uploaded_template, template_filename, metadata):
                                st.success(f"✅ Template '{template_name}' uploaded successfully!")
                                st.session_state.show_upload_form = False
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Failed to save template. Please try again.")
                            
                    except Exception as e:
                        st.error(f"Error uploading template: {str(e)}")
                        logger.error(f"Template upload error: {e}")
    
            pass  # Container automatically closes
    
    # Template validation modal
    if st.session_state.get('show_validate_form', False):
        # Use native container instead of HTML
        with st.container(border=True):
            st.subheader("🔍 Validate PDF Template")
        st.info("Upload a PDF to check if it has the required form fields")
        test_template = st.file_uploader(
            "Choose a PDF to validate",
            type=['pdf'],
            key="validate_template"
        )
        
        if test_template:
            try:
                # Save temporarily to validate
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(test_template.read())
                    tmp_path = tmp.name
                
                # Validate using PDF generator
                generator = PDFGenerator(tmp_path)
                validation_info = generator.validate_template()
                
                # Clean up temp file
                os.unlink(tmp_path)
                
                # Show validation results
                if validation_info['valid']:
                    st.success("✅ Template is valid!")
                else:
                    st.error("❌ Template validation failed")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Form Fields Found", len(validation_info['fields_found']))
                    if validation_info['fields_found']:
                        st.write("**Detected fields:**")
                        for field in validation_info['fields_found']:
                            st.write(f"• {field}")
                
                with col2:
                    st.metric("Page Count", validation_info['page_count'])
                    st.metric("File Size", f"{validation_info['file_size'] / 1024:.1f} KB")
                
                if validation_info['errors']:
                    st.error("**Errors:**")
                    for error in validation_info['errors']:
                        st.error(f"• {error}")
                        
            except Exception as e:
                st.error(f"Error validating template: {str(e)}")
            
            if st.button("Close", use_container_width=True):
                st.session_state.show_validate_form = False
                st.rerun()
            
            pass  # Container automatically closes
    
    # Existing templates section
    # Use native header instead of HTML
    st.subheader("📄 Template Library")
    
    try:
        # Get templates - Use programmatic certificate
        templates = [{"name": "Programmatic Certificate", "filename": "programmatic", "path": "programmatic", "created": "2025-07-30", "size": 0}]
        
        # Filter templates based on search
        if search_query:
            templates = [
                t for t in templates 
                if search_query.lower() in t.get('display_name', t.get('name', '')).lower() 
                or search_query.lower() in t.get('description', '').lower()
            ]
        
        if not templates:
            create_empty_state(
                "📄",
                "No templates found" if search_query else "No templates uploaded yet",
                "Upload your first certificate template to get started" if not search_query else "Try a different search term",
                "Upload Template" if not search_query else None,
                lambda: st.session_state.update({'show_upload_form': True}) if not search_query else None
            )
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
                                try:
                                    template_path = storage.get_template_path(template['name'])
                                    if template_path:
                                        generator = PDFGenerator(template_path)
                                        preview_bytes = generator.generate_preview("John", "Doe")
                                        
                                        st.download_button(
                                            label="📥 Download Preview",
                                            data=preview_bytes,
                                            file_name=f"preview_{template['name']}",
                                            mime="application/pdf",
                                            key=f"download_preview_{template['name']}",
                                            use_container_width=True
                                        )
                                    else:
                                        st.error("Template file not found")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                        
                        with col_delete:
                            if st.button(
                                "🗑️ Delete",
                                key=f"delete_{template['name']}",
                                use_container_width=True,
                                type="secondary"
                            ):
                                if st.session_state.get(f"confirm_delete_{template['name']}"):
                                    if storage.delete_template(template['name']):
                                        st.success(f"Template '{display_name}' deleted")
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete template")
                                else:
                                    st.session_state[f"confirm_delete_{template['name']}"] = True
                                    st.warning("Click again to confirm deletion")
            
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
                            try:
                                # Generate preview using the template
                                template_path = storage.get_template_path(template['name'])
                                if template_path:
                                    generator = PDFGenerator(template_path)
                                    preview_bytes = generator.generate_preview("John", "Doe")
                                    
                                    st.download_button(
                                        label="📥 Download Preview",
                                        data=preview_bytes,
                                        file_name=f"preview_{template['name']}",
                                        mime="application/pdf",
                                        key=f"download_preview_{template['name']}"
                                    )
                                else:
                                    st.error("Template file not found")
                            except Exception as e:
                                st.error(f"Error generating preview: {str(e)}")
                        
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
                            log_activity(
                                get_current_user()['username'],
                                "create_course",
                                {"course_name": course_name}
                            )
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
                                log_activity(
                                    get_current_user()['username'],
                                    "update_course",
                                    {"course_id": course_id, "course_name": course_name}
                                )
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
                            log_activity(
                                get_current_user()['username'],
                                "delete_course",
                                {"course_id": course_id, "course_name": course['name']}
                            )
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
        st.subheader("📤 Upload Your Spreadsheet")
        st.caption("Supported formats: CSV, Excel (.xlsx, .xls)")
        st.caption("Your file should contain participant names and any additional certificate data.")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file with participant data",
        key="admin_file_upload"
    )
    
    if uploaded_file is not None:
        st.session_state.admin_uploaded_file = uploaded_file
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show file info
        st.info(f"📊 File size: {uploaded_file.size:,} bytes")
        
        if st.button("Continue to Validation", type="primary", use_container_width=True):
            st.session_state.admin_workflow_step = 2
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
    
    # Template selection - Use programmatic certificate
    # We no longer need PDF templates since we use programmatic generation
    templates = [{"name": "Programmatic Certificate", "filename": "programmatic", "path": "programmatic"}]
    
    # Always have at least one template available
    if not templates:
        st.warning("⚠️ No templates available. Please contact administrator to upload templates.")
    else:
        st.subheader("🎨 Available Templates")
        
        template_options = {}
        for template in templates:
            # Use display_name if available, otherwise fallback to name
            display_name = template.get('display_name', template.get('name', 'Unknown Template'))
            template_options[display_name] = template
        
        selected_template_name = st.selectbox(
            "Choose a certificate template:",
            options=list(template_options.keys()),
            help="Select the template design for your certificates"
        )
        
        if selected_template_name:
            selected_template = template_options[selected_template_name]
            st.session_state.admin_selected_template = selected_template
            
            # Show template preview if available
            if 'preview' in selected_template:
                st.image(selected_template['preview'], caption=f"Preview: {selected_template_name}")
            
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
                
                # Check if using programmatic certificate
                if template_name == "Programmatic Certificate":
                    # Use programmatic generation
                    from certificate_generator_production import generate_certificate_for_app
                    use_programmatic = True
                else:
                    # Legacy PDF template
                    template_path = storage.get_template_path(template_name)
                    if not template_path:
                        st.error("Template file not found. The template may have been deleted.")
                        return
                    pdf_generator = PDFGenerator(template_path)
                    use_programmatic = False
                
                # Validate template (skip for programmatic)
                if not use_programmatic:
                    validation_info = pdf_generator.validate_template()
                    if not validation_info['valid']:
                        st.error("Template validation failed:")
                        for error in validation_info['errors']:
                            st.error(f"• {error}")
                        return
                
                # Prepare recipients data
                recipients = []
                for idx, row in st.session_state.admin_validated_data.iterrows():
                    # Handle various column name formats
                    first_name = row.get('First Name', row.get('first name', row.get('FirstName', '')))
                    last_name = row.get('Last Name', row.get('last name', row.get('LastName', '')))
                    
                    if first_name or last_name:
                        recipients.append({
                            'first_name': str(first_name).strip(),
                            'last_name': str(last_name).strip()
                        })
                
                if not recipients:
                    st.error("No valid recipients found in the data.")
                    return
                
                # Generate certificates with progress callback
                def update_progress(current, total, message):
                    progress = current / total if total > 0 else 0
                    progress_bar.progress(progress)
                    status_text.text(message)
                
                if use_programmatic:
                    # Use programmatic generation for batch
                    results = []
                    generated_files = []
                    
                    for i, recipient in enumerate(recipients):
                        try:
                            update_progress(i, f"Generating certificate for {recipient['first_name']} {recipient['last_name']}")
                            
                            # Get course info
                            course_info = st.session_state.get('admin_selected_course_info', {})
                            course_name = course_info.get('name', 'Vapes and Vaping')
                            
                            # Generate certificate
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
                    
                    # Skip the zip_path and results conversion
                    st.session_state.admin_generated_files = generated_files
                    
                else:
                    # Use PDF template batch generation
                    results, zip_path = pdf_generator.generate_batch(
                        recipients=recipients,
                        progress_callback=update_progress,
                        parallel=True
                    )
                
                # Convert results to the format expected by admin workflow (only for PDF templates)
                if not use_programmatic:
                    generated_files = []
                    for i, result in enumerate(results):
                        if result.success:
                            # Read the generated file
                            output_dir = os.path.dirname(zip_path)
                            file_path = os.path.join(output_dir, result.filename)
                            
                            if os.path.exists(file_path):
                                with open(file_path, 'rb') as f:
                                    generated_files.append({
                                        'name': result.filename,
                                        'content': f.read()
                                    })
                    
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
        if st.button("📦 Download All as ZIP", type="primary", use_container_width=True):
            zip_data = create_zip_archive(st.session_state.admin_generated_files)
            st.download_button(
                "Download ZIP Archive",
                data=zip_data,
                file_name=f"certificates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip"
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
        if user and user.get("role") == "admin":
            # Admin user - show admin navigation
            dashboard_page = st.Page(render_dashboard, title="Dashboard", icon="📊", default=True)
            generate_page = st.Page(render_admin_certificate_generation, title="Generate Certificates", icon="🏆")
            templates_page = st.Page(render_templates_page, title="Templates", icon="📄")
            courses_page = st.Page(render_courses_page, title="Courses", icon="📚")
            users_page = st.Page(render_users_page, title="Users", icon="👥")
            analytics_page = st.Page(render_analytics_page, title="Analytics", icon="📈")
            settings_page = st.Page(render_settings_page, title="Settings", icon="⚙️")
            logout_page = st.Page(logout_action, title="Logout", icon="🚪")
            
            pg = st.navigation({
                "Admin": [dashboard_page, generate_page, templates_page, courses_page, users_page],
                "System": [analytics_page, settings_page, logout_page]
            })
        else:
            # Regular user - show user workflow
            generate_page = st.Page(user_workflow, title="Generate Certificates", icon="🏆", default=True)
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