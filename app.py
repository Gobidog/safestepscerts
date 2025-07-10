"""
Certificate Generator - Main Application Entry Point
Handles initialization, routing, and global configuration
"""
import streamlit as st
import structlog
import asyncio
import signal
import sys
import os
from pathlib import Path
from datetime import datetime
import threading
import time

from config import config
from utils.storage import cleanup_old_files
from utils.auth import is_session_valid, get_current_user

# Configure structured logging
logger = structlog.get_logger()

# Page configuration must be called before any other st commands
st.set_page_config(
    page_title="SafeSteps Certificate Generator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "SafeSteps Certificate Generator v1.0.0"
    }
)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        'authenticated': False,
        'user_role': None,
        'username': None,
        'login_time': None,
        'last_activity': datetime.now(),
        'current_template': None,
        'upload_data': None,
        'generated_files': [],
        'generation_progress': 0,
        'generation_status': None,
        'rate_limit_remaining': config.rate_limit.requests_limit,
        'rate_limit_reset': time.time() + config.rate_limit.window_seconds
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Custom CSS for new branding
def inject_custom_css():
    """Inject custom CSS for SafeSteps branding"""
    # Hide sidebar if not authenticated
    hide_sidebar = """
        section[data-testid="stSidebar"] {
            display: none !important;
        }
    """ if not st.session_state.get('authenticated', False) else ""
    
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Brand colors */
        :root {{
            --primary-color: #032A51;
            --accent-color: #9ACA3C;
            --background: #F8F9FA;
            --card-background: #FFFFFF;
            --text-primary: #212529;
            --text-secondary: #6C757D;
            --border-color: #DEE2E6;
            --success-color: #28A745;
            --warning-color: #FFC107;
            --error-color: #DC3545;
        }}
        
        /* Global styles */
        * {{
            font-family: 'Inter', sans-serif !important;
        }}
        
        .main {{
            background-color: var(--background);
        }}
        
        {hide_sidebar}
        
        /* Sidebar styling when visible */
        section[data-testid="stSidebar"] {{
            background-color: var(--primary-color);
            width: 280px !important;
        }}
        
        section[data-testid="stSidebar"] .block-container {{
            padding-top: 2rem;
        }}
        
        section[data-testid="stSidebar"] * {{
            color: white !important;
        }}
        
        /* Logo container */
        .logo-container {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 0 20px 20px 20px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .logo-text {{
            font-size: 36px;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
        }}
        
        /* User info card */
        .user-info-card {{
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 16px;
            margin: 0 20px 20px 20px;
            text-align: center;
        }}
        
        /* Navigation items */
        .nav-item {{
            padding: 12px 20px;
            margin: 4px 20px;
            border-radius: 8px;
            transition: all 0.2s;
            cursor: pointer;
        }}
        
        .nav-item:hover {{
            background: rgba(255,255,255,0.1);
        }}
        
        .nav-item.active {{
            background: rgba(154,202,60,0.2);
            border-left: 4px solid var(--accent-color);
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            background-color: var(--primary-color) !important;
            filter: brightness(1.1);
        }}
        
        /* Primary button */
        button[kind="primary"] {{
            background-color: var(--primary-color) !important;
            color: white !important;
        }}
        
        /* Accent button */
        .accent-button > button {{
            background-color: var(--accent-color) !important;
            color: var(--primary-color) !important;
        }}
        
        /* Secondary button */
        button[kind="secondary"] {{
            background-color: white !important;
            color: var(--primary-color) !important;
            border: 2px solid var(--primary-color) !important;
        }}
        
        /* Cards */
        .action-card {{
            background: var(--card-background);
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border: 1px solid var(--border-color);
            transition: all 0.3s;
            height: 100%;
        }}
        
        .action-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}
        
        /* Progress indicators */
        .workflow-step {{
            display: inline-block;
            padding: 8px 16px;
            margin: 0 8px;
            border-radius: 20px;
            background: #E9ECEF;
            color: var(--text-secondary);
            font-weight: 500;
            transition: all 0.3s;
        }}
        
        .workflow-step.active {{
            background: var(--accent-color);
            color: var(--primary-color);
        }}
        
        .workflow-step.completed {{
            background: var(--success-color);
            color: white;
        }}
        
        /* File upload zone */
        .file-upload-zone {{
            border: 2px dashed var(--border-color);
            background: var(--background);
            min-height: 200px;
            border-radius: 8px;
            text-align: center;
            padding: 40px;
            transition: all 0.3s;
        }}
        
        .file-upload-zone:hover {{
            border-color: var(--accent-color);
            background: #E8F5E9;
        }}
        
        /* Typography */
        h1 {{
            color: var(--primary-color);
            font-size: 32px;
            font-weight: 700;
        }}
        
        h2 {{
            color: var(--primary-color);
            font-size: 24px;
            font-weight: 600;
        }}
        
        h3 {{
            color: var(--primary-color);
            font-size: 20px;
            font-weight: 600;
        }}
        
        /* Forms */
        .stTextInput input, .stSelectbox select {{
            background: white;
            border: 2px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 16px;
            font-size: 16px;
        }}
        
        .stTextInput input:focus, .stSelectbox select:focus {{
            border-color: var(--accent-color);
            outline: none;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Dashboard grid */
        .dashboard-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        /* Quick stats */
        .quick-stats {{
            background: rgba(255,255,255,0.1);
            padding: 16px;
            border-radius: 8px;
            margin: 0 20px;
        }}
        
        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            color: white;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: rgba(255,255,255,0.8);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        </style>
    """, unsafe_allow_html=True)

# Background cleanup scheduler
cleanup_thread = None
cleanup_stop_event = threading.Event()

def cleanup_scheduler():
    """Background thread for periodic cleanup"""
    while not cleanup_stop_event.is_set():
        try:
            # Wait for the cleanup interval
            cleanup_stop_event.wait(config.temp_file.cleanup_interval_minutes * 60)
            
            if not cleanup_stop_event.is_set():
                # Perform cleanup
                count = cleanup_old_files(age_hours=config.temp_file.max_age_minutes / 60)
                if count > 0:
                    logger.info(f"Cleanup scheduler removed {count} old files")
        except Exception as e:
            logger.error(f"Error in cleanup scheduler: {e}")

def start_cleanup_scheduler():
    """Start the background cleanup scheduler"""
    global cleanup_thread
    if cleanup_thread is None or not cleanup_thread.is_alive():
        cleanup_thread = threading.Thread(target=cleanup_scheduler, daemon=True)
        cleanup_thread.start()
        logger.info("Started cleanup scheduler")

def stop_cleanup_scheduler():
    """Stop the background cleanup scheduler"""
    cleanup_stop_event.set()
    if cleanup_thread and cleanup_thread.is_alive():
        cleanup_thread.join(timeout=5)
        logger.info("Stopped cleanup scheduler")

# Signal handlers for graceful shutdown
def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    stop_cleanup_scheduler()
    sys.exit(0)

# Register signal handlers (only in main thread)
try:
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
except ValueError:
    # Not in main thread, skip signal handling
    pass

# Error boundary decorator
def error_boundary(func):
    """Decorator to catch and display errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            st.error(f"An error occurred: {str(e)}")
            st.stop()
    return wrapper

# Health check endpoint (for Cloud Run)
def health_check():
    """Simple health check for monitoring"""
    return {
        'status': 'healthy',
        'version': config.app.app_version,
        'timestamp': datetime.now().isoformat(),
        'storage': 'local' if config.storage.use_local_storage else 'gcs'
    }

# Main application
@error_boundary
def main():
    """Main application entry point with smart routing"""
    
    # Initialize session state
    init_session_state()
    
    # Inject custom CSS
    inject_custom_css()
    
    # Start cleanup scheduler
    start_cleanup_scheduler()
    
    # Check for session timeout
    if st.session_state.authenticated:
        last_activity = st.session_state.last_activity
        timeout_minutes = config.auth.session_timeout_minutes
        
        if (datetime.now() - last_activity).total_seconds() > timeout_minutes * 60:
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.warning("Your session has expired. Please login again.")
            st.rerun()
        else:
            # Update last activity
            st.session_state.last_activity = datetime.now()
    
    # Smart routing based on authentication status
    if not st.session_state.authenticated:
        # Show login page
        show_login_page()
    else:
        # Route to appropriate dashboard based on role
        if st.session_state.user_role == "admin":
            show_admin_dashboard()
        else:
            show_user_dashboard()


def show_login_page():
    """Display the branded login page"""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo/Brand
        st.markdown("""
            <div style="text-align: center; margin-bottom: 2rem;">
                <div class="logo-container">
                    <h1 class="logo-text">SS</h1>
                </div>
                <h1 style="margin-top: 1rem;">SafeSteps Certificate Generator</h1>
                <p style="color: #6C757D; font-size: 18px;">Professional Certificates Made Simple</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=True):
            password = st.text_input(
                "Enter Password",
                type="password",
                placeholder="Enter your password"
            )
            
            # Centered sign in button
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                submit = st.form_submit_button(
                    "Sign In",
                    type="primary",
                    use_container_width=True
                )
            
            if submit:
                if not password:
                    st.error("Please enter a password")
                else:
                    # Import here to avoid circular dependency
                    from utils.auth import login_with_password
                    success, role, error_message = login_with_password(password)
                    
                    if success:
                        st.session_state.user_role = role
                        st.session_state.username = role
                        st.success(f"Welcome! Redirecting to your dashboard...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(error_message or "Invalid password")
        
        # Footer
        st.markdown(
            "<p style='text-align: center; color: #6C757D; margin-top: 2rem;'>"
            "Forgot password? Contact admin</p>",
            unsafe_allow_html=True
        )


def show_user_dashboard():
    """Display the user dashboard with workflow"""
    # Sidebar - Only basic user info
    with st.sidebar:
        # Logo
        st.markdown("""
            <div class="logo-container">
                <h2 class="logo-text">SS</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # User info
        st.markdown(f"""
            <div class="user-info-card">
                <div>👤 <strong>User</strong></div>
                <div style="font-size: 14px; margin-top: 4px;">
                    Session: {int((datetime.now() - st.session_state.login_time).total_seconds() / 60)} mins
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Simple info
        st.markdown("### Certificate Generator")
        st.markdown("Follow the workflow to generate your certificates.")
        
        # Logout at bottom
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.rerun()
    
    # Main content
    st.title("Certificate Generation Workflow")
    
    # Initialize workflow state
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 1
    
    # Progress bar using columns
    steps = ["Upload", "Validate", "Select Template", "Generate"]
    cols = st.columns(len(steps) * 2 - 1)
    
    for i, step in enumerate(steps, 1):
        col_index = (i - 1) * 2
        
        if i < st.session_state.workflow_step:
            status = "completed"
            icon = "✓"
            color = "#28A745"
        elif i == st.session_state.workflow_step:
            status = "active"
            icon = "●"
            color = "#9ACA3C"
        else:
            status = "pending"
            icon = "○"
            color = "#E9ECEF"
        
        with cols[col_index]:
            st.markdown(
                f"""
                <div style="text-align: center;">
                    <div class="workflow-step {status}" style="background: {color};">
                        {icon} {i}. {step}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        # Add arrow between steps
        if i < len(steps):
            with cols[col_index + 1]:
                st.markdown(
                    '<div style="text-align: center; padding-top: 8px;">→</div>',
                    unsafe_allow_html=True
                )
    
    # Show appropriate step content
    if st.session_state.workflow_step == 1:
        show_upload_step()
    elif st.session_state.workflow_step == 2:
        show_validate_step()
    elif st.session_state.workflow_step == 3:
        show_template_step()
    elif st.session_state.workflow_step == 4:
        show_generate_step()


def show_upload_step():
    """Step 1: Upload spreadsheet"""
    st.markdown("""
        <div class="file-upload-zone">
            <div style="font-size: 48px; margin-bottom: 1rem;">📁</div>
            <h3>Drop your spreadsheet here</h3>
            <p>or click to browse</p>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose file",
        type=['csv', 'xlsx', 'xls'],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        st.success(f"File uploaded: {uploaded_file.name}")
        # Auto-advance to validation
        st.session_state.workflow_step = 2
        st.session_state.uploaded_file = uploaded_file
        time.sleep(1)
        st.rerun()
    
    st.caption("Supported: CSV, XLSX (max 5MB)")


def show_validate_step():
    """Step 2: Validate data"""
    import tempfile
    import os
    from utils.validators import SpreadsheetValidator
    
    if 'validation_complete' not in st.session_state:
        st.session_state.validation_complete = False
    
    if not st.session_state.validation_complete:
        with st.spinner("🔄 Validating your spreadsheet..."):
            # Save uploaded file temporarily
            uploaded_file = st.session_state.uploaded_file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getbuffer())
                temp_path = tmp_file.name
            
            try:
                # Validate spreadsheet
                validator = SpreadsheetValidator()
                validation_result = validator.validate_spreadsheet(temp_path)
                
                if validation_result.valid:
                    st.session_state.validated_data = validation_result.cleaned_data
                    st.session_state.validation_complete = True
                    st.session_state.row_count = validation_result.row_count
                    st.success(f"✅ Validation complete! Found {validation_result.row_count} valid recipients.")
                    
                    # Store warnings if any
                    if validation_result.warnings:
                        st.session_state.validation_warnings = validation_result.warnings
                else:
                    st.error("❌ Validation failed!")
                    for error in validation_result.errors:
                        st.error(f"• {error}")
                    
                    # Reset workflow
                    st.session_state.workflow_step = 1
                    del st.session_state.uploaded_file
                    if st.button("Try Again", type="primary"):
                        st.rerun()
                    st.stop()
            finally:
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    # Show validated data
    if st.session_state.validation_complete:
        st.success(f"✅ Validation complete! Found {st.session_state.row_count} valid recipients.")
        
        # Show data preview
        st.subheader("Data Preview")
        st.dataframe(
            st.session_state.validated_data.head(10),
            use_container_width=True
        )
        if st.session_state.row_count > 10:
            st.caption(f"Showing first 10 of {st.session_state.row_count} rows")
        
        # Show warnings if any
        if hasattr(st.session_state, 'validation_warnings'):
            with st.expander("⚠️ Warnings"):
                for warning in st.session_state.validation_warnings:
                    st.warning(warning)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Continue", type="primary", use_container_width=True):
                st.session_state.workflow_step = 3
                st.rerun()


def show_template_step():
    """Step 3: Select template"""
    from utils.storage import list_templates, get_template_path
    
    st.subheader("Select Certificate Template")
    
    # Get available templates from storage
    templates = list_templates()
    
    if not templates:
        st.error("No templates available. Please contact an administrator.")
        st.stop()
    
    # Display templates in a grid
    cols = st.columns(2)
    for i, template in enumerate(templates):
        with cols[i % 2]:
            # Create a card-like button for each template
            template_name = template.get('name', 'Unknown')
            template_desc = template.get('description', 'Certificate template')
            
            # Card container
            st.markdown(f"""
                <div class="action-card" style="cursor: pointer; margin-bottom: 1rem;">
                    <h3>📄 {template_name}</h3>
                    <p style="color: #6C757D; margin-bottom: 1rem;">{template_desc}</p>
                    <p style="font-size: 14px; color: #6C757D;">
                        Created: {template.get('created', 'Unknown')[:10]}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(
                f"Select {template_name}",
                use_container_width=True,
                key=f"template_{i}"
            ):
                # Get the actual template path
                template_path = get_template_path(template.get('filename', template_name))
                if template_path and os.path.exists(template_path):
                    st.session_state.selected_template = template_name
                    st.session_state.selected_template_path = template_path
                    st.session_state.workflow_step = 4
                    st.rerun()
                else:
                    st.error(f"Failed to load template: {template_name}")
                    if template_path:
                        st.error(f"Template file not found at: {template_path}")


def show_generate_step():
    """Step 4: Generate certificates"""
    from utils.pdf_generator import PDFGenerator
    from utils.storage import log_certificate_generation
    from utils.auth import log_activity
    
    st.subheader("Ready to Generate")
    
    # Summary card
    recipients_count = len(st.session_state.validated_data)
    template_name = st.session_state.selected_template
    estimated_time = recipients_count * 0.1  # With parallel processing
    
    st.markdown(f"""
        <div class="action-card">
            <h3>Generation Summary</h3>
            <p><strong>Recipients:</strong> {recipients_count}</p>
            <p><strong>Template:</strong> {template_name}</p>
            <p><strong>Estimated time:</strong> ~{estimated_time:.1f} seconds</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Generate button with accent color
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Generate All Certificates", type="primary", use_container_width=True):
            try:
                # Convert dataframe to list of dicts
                recipients = st.session_state.validated_data.to_dict('records')
                
                # Debug: Check data format
                logger.info(f"Recipients count: {len(recipients)}")
                if recipients:
                    logger.info(f"First recipient keys: {list(recipients[0].keys())}")
                    logger.info(f"First recipient data: {recipients[0]}")
                
                # Create PDF generator
                generator = PDFGenerator(st.session_state.selected_template_path)
                logger.info(f"PDF Generator field mapping: {generator.field_mapping}")
                
                # Show spinner during parallel generation
                with st.spinner(f"🚀 Generating {len(recipients)} certificates in parallel..."):
                    # Generate certificates with parallel processing
                    start_time = time.time()
                    results, zip_path = generator.generate_batch(
                        recipients=recipients,
                        progress_callback=None,  # No progress callback for parallel processing
                        parallel=True  # Enable parallel processing
                    )
                    generation_time = time.time() - start_time
                
                # Count successes
                successful = sum(1 for r in results if r.success)
                failed = sum(1 for r in results if not r.success)
                
                if successful > 0:
                    st.success(f"""
                    ✅ Generation complete!
                    - Certificates generated: {successful}
                    - Time taken: {generation_time:.1f} seconds
                    - Average: {generation_time/len(recipients):.2f} seconds per certificate
                    """)
                    
                    # Celebration
                    st.balloons()
                    
                    # Read ZIP file for download
                    with open(zip_path, 'rb') as f:
                        zip_data = f.read()
                    
                    # Download button
                    st.download_button(
                        "📥 Download All Certificates (ZIP)",
                        data=zip_data,
                        file_name=f"certificates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
                    
                    # Log activity
                    log_certificate_generation(
                        user=st.session_state.username,
                        template=template_name,
                        count=successful
                    )
                    
                    log_activity("certificates_generated", {
                        "count": successful,
                        "template": template_name,
                        "generation_time": generation_time
                    })
                    
                    # Store in session for history
                    st.session_state.generated_files = results
                    
                    # Cleanup
                    if os.path.exists(zip_path):
                        try:
                            os.remove(zip_path)
                        except:
                            pass
                
                if failed > 0:
                    st.warning(f"⚠️ {failed} certificates failed to generate")
                    with st.expander("View Failed Certificates"):
                        failed_results = [r for r in results if not r.success]
                        for i, result in enumerate(failed_results[:10]):
                            st.error(f"Row {i+1}: {result.error}")
                        if len(failed_results) > 10:
                            st.caption(f"...and {len(failed_results) - 10} more")
                
                # Option to start over
                if st.button("Generate More Certificates", use_container_width=True):
                    # Reset workflow
                    st.session_state.workflow_step = 1
                    for key in ['uploaded_file', 'validated_data', 'validation_complete', 
                               'selected_template', 'selected_template_path']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
                    
            except Exception as e:
                error_msg = str(e)
                st.error(f"Error generating certificates: {error_msg}")
                logger.error(f"Generation error: {e}", exc_info=True)
                
                # Show more details in expander
                with st.expander("Error Details"):
                    st.code(error_msg)
                    if hasattr(e, '__traceback__'):
                        import traceback
                        st.code(traceback.format_exc())


def show_admin_dashboard():
    """Display the admin dashboard"""
    from utils.storage import list_templates, get_usage_statistics, get_activity_logs
    
    # Initialize admin page state
    if 'admin_page' not in st.session_state:
        st.session_state.admin_page = 'dashboard'
    
    # Sidebar
    with st.sidebar:
        # Logo
        st.markdown("""
            <div class="logo-container">
                <h2 class="logo-text">SS</h2>
            </div>
        """, unsafe_allow_html=True)
        
        # Admin info
        st.markdown(f"""
            <div class="user-info-card">
                <div>👤 <strong>Admin</strong></div>
                <div style="font-size: 14px; margin-top: 4px;">
                    ⚡ Session: {int((datetime.now() - st.session_state.login_time).total_seconds() / 60)} mins
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Quick stats
        templates_count = len(list_templates())
        stats = get_usage_statistics()
        
        st.markdown(f"""
            <div class="quick-stats">
                <div style="margin-bottom: 12px;">
                    <div class="stat-label">Templates</div>
                    <div class="stat-value">{templates_count}</div>
                </div>
                <div>
                    <div class="stat-label">Total Certs</div>
                    <div class="stat-value">{stats.get('total_certificates', 0)}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Menu
        st.markdown("### Menu")
        menu_items = [
            ("Dashboard", "dashboard"),
            ("Generate", "generate"),
            ("Templates", "templates"),
            ("Users", "users"),
            ("Analytics", "analytics"),
            ("Settings", "settings")
        ]
        
        for label, page in menu_items:
            is_active = st.session_state.admin_page == page
            if st.button(
                f"{'●' if is_active else '○'} {label}",
                use_container_width=True,
                key=f"admin_menu_{page}"
            ):
                st.session_state.admin_page = page
                st.rerun()
        
        # Logout
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = None
            st.rerun()
    
    # Main content based on selected page
    if st.session_state.admin_page == 'dashboard':
        show_admin_dashboard_main()
    elif st.session_state.admin_page == 'generate':
        # Show the certificate generation workflow without changing the sidebar
        st.title("Certificate Generation Workflow")
        
        # Initialize workflow state
        if 'workflow_step' not in st.session_state:
            st.session_state.workflow_step = 1
        
        # Progress bar using columns (same as user workflow)
        steps = ["Upload", "Validate", "Select Template", "Generate"]
        cols = st.columns(len(steps) * 2 - 1)
        
        for i, step in enumerate(steps, 1):
            col_index = (i - 1) * 2
            
            if i < st.session_state.workflow_step:
                status = "completed"
                icon = "✓"
                color = "#28A745"
            elif i == st.session_state.workflow_step:
                status = "active"
                icon = "●"
                color = "#9ACA3C"
            else:
                status = "pending"
                icon = "○"
                color = "#E9ECEF"
            
            with cols[col_index]:
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <div class="workflow-step {status}" style="background: {color};">
                            {icon} {i}. {step}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            # Add arrow between steps
            if i < len(steps):
                with cols[col_index + 1]:
                    st.markdown(
                        '<div style="text-align: center; padding-top: 8px;">→</div>',
                        unsafe_allow_html=True
                    )
        
        # Show appropriate step content
        if st.session_state.workflow_step == 1:
            show_upload_step()
        elif st.session_state.workflow_step == 2:
            show_validate_step()
        elif st.session_state.workflow_step == 3:
            show_template_step()
        elif st.session_state.workflow_step == 4:
            show_generate_step()
    elif st.session_state.admin_page == 'templates':
        show_template_management()
    elif st.session_state.admin_page == 'users':
        show_user_management()
    elif st.session_state.admin_page == 'analytics':
        show_analytics()
    elif st.session_state.admin_page == 'settings':
        show_settings()


def show_admin_dashboard_main():
    """Main admin dashboard with action cards"""
    st.title("Admin Dashboard")
    
    # Get real stats
    templates_count = len(list_templates())
    stats = get_usage_statistics()
    
    # Dashboard grid
    col1, col2 = st.columns(2)
    
    with col1:
        # Templates card
        if st.button("templates_card", key="dash_templates", label_visibility="hidden"):
            st.session_state.admin_page = 'templates'
            st.rerun()
        
        st.markdown(f"""
            <div class="action-card">
                <h2>📄 Templates</h2>
                <p style="color: #6C757D;">Manage PDFs</p>
                <h3>{templates_count} Active</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Analytics card
        if st.button("analytics_card", key="dash_analytics", label_visibility="hidden"):
            st.session_state.admin_page = 'analytics'
            st.rerun()
            
        st.markdown(f"""
            <div class="action-card">
                <h2>📊 Analytics</h2>
                <p style="color: #6C757D;">View Stats</p>
                <h3>{stats.get('total_certificates', 0)} Total</h3>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Users card
        if st.button("users_card", key="dash_users", label_visibility="hidden"):
            st.session_state.admin_page = 'users'
            st.rerun()
            
        st.markdown("""
            <div class="action-card">
                <h2>👥 Users</h2>
                <p style="color: #6C757D;">Passwords</p>
                <h3>2 Roles</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Settings card
        if st.button("settings_card", key="dash_settings", label_visibility="hidden"):
            st.session_state.admin_page = 'settings'
            st.rerun()
            
        st.markdown("""
            <div class="action-card">
                <h2>⚙️ Settings</h2>
                <p style="color: #6C757D;">System Config</p>
                <h3>System OK</h3>
            </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    st.markdown("### Recent Activity")
    
    # Get actual recent activity
    recent_logs = get_activity_logs(limit=10)
    
    if recent_logs:
        activity_html = '<div class="action-card"><ul style="list-style: none; padding: 0;">'
        for log in recent_logs[:5]:
            timestamp = log.get('timestamp', '')[:19]
            user = log.get('user', 'Unknown')
            if log.get('type') == 'certificate_generation':
                count = log.get('count', 0)
                template = log.get('template', 'Unknown')
                activity_html += f'<li style="margin-bottom: 8px;">• {user} generated {count} certificates using {template}</li>'
        activity_html += '</ul></div>'
        st.markdown(activity_html, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="action-card">
                <p style="color: #6C757D;">No recent activity</p>
            </div>
        """, unsafe_allow_html=True)

# Application metadata for deployment
def get_app_info():
    """Return application metadata"""
    return {
        'name': config.app.app_name,
        'version': config.app.app_version,
        'description': 'Professional PDF Certificate Generator',
        'author': 'Certificate Generator Team',
        'python_version': '3.11',
        'streamlit_version': '1.31.0',
        'deployment': 'Google Cloud Run',
        'health_check': '/health',
        'port': 8080
    }

def show_template_management():
    """Template management interface"""
    from utils.storage import list_templates, save_template, delete_template, get_template
    import tempfile
    import fitz  # PyMuPDF
    
    st.title("Template Management")
    
    # Three column layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Column 1: Template list
    with col1:
        st.subheader("Templates")
        
        # Search box
        search = st.text_input("Search", placeholder="Search templates...")
        
        # Template list
        templates = list_templates()
        filtered_templates = [t for t in templates if search.lower() in t.get('name', '').lower()] if search else templates
        
        for i, template in enumerate(filtered_templates):
            if st.button(
                f"📄 {template.get('name', 'Unknown')}",
                key=f"select_template_{i}",
                use_container_width=True
            ):
                st.session_state.selected_template_admin = template
    
    # Column 2: Preview
    with col2:
        st.subheader("Preview")
        
        if 'selected_template_admin' in st.session_state:
            template = st.session_state.selected_template_admin
            st.markdown(f"""
                <div class="action-card">
                    <h3>{template.get('name', 'Unknown')}</h3>
                    <p>Created: {template.get('created', 'Unknown')[:10]}</p>
                    <p>Size: {template.get('size', 0) / 1024:.1f} KB</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Show detected fields
            template_content = get_template(template.get('filename'))
            if template_content:
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                    tmp.write(template_content)
                    tmp_path = tmp.name
                
                try:
                    doc = fitz.open(tmp_path)
                    fields = []
                    for page in doc:
                        for widget in page.widgets():
                            if widget.field_type == fitz.PDF_WIDGET_TYPE_TEXT:
                                fields.append(widget.field_name)
                    doc.close()
                    
                    if fields:
                        st.info(f"Fields detected: {len(fields)}")
                        for field in fields:
                            st.caption(f"• {field}")
                finally:
                    os.unlink(tmp_path)
        else:
            st.info("Select a template to preview")
    
    # Column 3: Actions
    with col3:
        st.subheader("Actions")
        
        # Upload new template
        with st.expander("📤 Upload Template", expanded=True):
            uploaded_file = st.file_uploader("Choose PDF", type=['pdf'])
            template_name = st.text_input("Template Name")
            
            if uploaded_file and template_name:
                if st.button("Upload", type="primary", use_container_width=True):
                    with st.spinner("Uploading..."):
                        success = save_template(
                            uploaded_file.getbuffer(),
                            template_name,
                            {"description": "Uploaded via admin panel"}
                        )
                        if success:
                            st.success("Template uploaded!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Upload failed")
        
        # Test template
        if 'selected_template_admin' in st.session_state:
            if st.button("🧪 Test Template", use_container_width=True):
                st.info("Test generation would happen here")
            
            # Delete template
            if st.button("🗑️ Delete Template", use_container_width=True, type="secondary"):
                if st.checkbox("Confirm deletion"):
                    template = st.session_state.selected_template_admin
                    if delete_template(template.get('filename')):
                        st.success("Template deleted")
                        del st.session_state.selected_template_admin
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Failed to delete template")


def show_user_management():
    """User management interface"""
    from utils.auth import update_passwords, validate_password_strength
    
    st.title("User Management")
    
    st.info("Manage user and admin passwords")
    
    # Password change form
    with st.form("password_form"):
        st.subheader("Change Passwords")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### User Password")
            new_user_password = st.text_input(
                "New User Password",
                type="password",
                help="Leave blank to keep current password"
            )
            
            if new_user_password:
                is_strong, msg = validate_password_strength(new_user_password)
                if is_strong:
                    st.success(msg)
                else:
                    st.error(msg)
        
        with col2:
            st.markdown("### Admin Password")
            new_admin_password = st.text_input(
                "New Admin Password",
                type="password",
                help="Leave blank to keep current password"
            )
            
            if new_admin_password:
                is_strong, msg = validate_password_strength(new_admin_password)
                if is_strong:
                    st.success(msg)
                else:
                    st.error(msg)
        
        submitted = st.form_submit_button("Update Passwords", type="primary")
        
        if submitted:
            if update_passwords(new_user_password, new_admin_password):
                st.success("Passwords updated successfully!")
                from utils.auth import log_activity
                log_activity("passwords_updated", {
                    "user_changed": bool(new_user_password),
                    "admin_changed": bool(new_admin_password)
                })
            else:
                st.error("Failed to update passwords")


def show_analytics():
    """Analytics dashboard"""
    from utils.storage import get_usage_statistics
    
    st.title("Analytics")
    
    stats = get_usage_statistics()
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Certificates", stats.get('total_certificates', 0))
    
    with col2:
        st.metric("Total Generations", stats.get('total_generations', 0))
    
    with col3:
        st.metric("Unique Users", stats.get('unique_users', 0))
    
    with col4:
        st.metric("Templates Used", len(stats.get('template_usage', {})))
    
    # Template usage
    st.subheader("Template Usage")
    template_usage = stats.get('template_usage', {})
    if template_usage:
        for template, count in sorted(template_usage.items(), key=lambda x: x[1], reverse=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(template)
            with col2:
                st.text(f"{count} uses")
            st.progress(count / max(template_usage.values()))
    else:
        st.info("No usage data available yet")
    
    # Daily usage chart
    st.subheader("Daily Usage")
    daily_usage = stats.get('daily_usage', {})
    if daily_usage:
        import pandas as pd
        df = pd.DataFrame(list(daily_usage.items()), columns=['Date', 'Count'])
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')
        st.line_chart(df.set_index('Date'))
    else:
        st.info("No daily usage data available yet")


def show_settings():
    """System settings"""
    st.title("System Settings")
    
    # System info
    st.subheader("System Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
            <div class="action-card">
                <h4>Application</h4>
                <p>Version: 1.0.0</p>
                <p>Framework: Streamlit</p>
                <p>Storage: Local/GCS</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="action-card">
                <h4>Configuration</h4>
                <p>Session Timeout: 30 min</p>
                <p>Rate Limit: 40 req/min</p>
                <p>Max Upload: 5 MB</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Environment info
    st.subheader("Environment")
    
    storage_mode = "Local Storage" if config.storage.use_local_storage else "Google Cloud Storage"
    st.info(f"Storage Mode: {storage_mode}")
    
    if st.button("🔄 Clear Temporary Files"):
        from utils.storage import cleanup_old_files
        count = cleanup_old_files(age_hours=0)
        st.success(f"Cleared {count} temporary files")
    
    # Export config
    st.subheader("Configuration Export")
    if st.button("📥 Export Configuration"):
        config_data = {
            "app_name": config.app.app_name,
            "version": config.app.app_version,
            "storage_mode": storage_mode,
            "session_timeout": config.auth.session_timeout_minutes,
            "rate_limit": config.rate_limit.requests_limit
        }
        st.json(config_data)


if __name__ == "__main__":
    # Log startup
    logger.info(
        "Starting Certificate Generator",
        version=config.app.app_version,
        debug=config.app.debug,
        storage="local" if config.storage.use_local_storage else "gcs"
    )
    
    # Validate configuration
    if config.validate():
        main()
    else:
        st.error("Configuration validation failed. Check logs for details.")
        st.stop()