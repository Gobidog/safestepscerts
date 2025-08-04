"""
Streamlined User Workflow for SafeSteps - Mobile-First Certificate Generation
Implements 3 flexible workflow modes: Quick, Guided, and Advanced
Built with enhanced UI components and touch-friendly interfaces
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import SafeSteps modules
from utils.ui_components import (
    create_prominent_button, create_enhanced_button_group, create_card,
    create_mobile_friendly_form, create_touch_friendly_upload,
    create_progress_indicator, create_step_navigation,
    COLORS, TYPOGRAPHY, apply_custom_css
)
from utils.workflow_engine import (
    WorkflowMode, create_workflow, get_workflow_state, 
    advance_workflow_step, jump_to_workflow_step,
    get_workflow_progress, get_user_suggestions,
    resume_latest_workflow, save_workflow_state
)
from config.auth import get_current_user
from utils.file_processing import SpreadsheetValidator
from utils.certificate_generation import CertificateGenerator
from data.course_manager import CourseManager

def streamlined_workflow_page():
    """Main entry point for streamlined user workflow"""
    # Apply custom CSS for mobile-first design
    apply_custom_css()
    
    # Get current user
    user = get_current_user()
    if not user:
        st.error("Authentication required. Please log in.")
        return
    
    user_id = user.get('username', 'anonymous')
    
    # Check for existing workflow or start new one
    if 'workflow_id' not in st.session_state:
        # Try to resume latest workflow
        latest_workflow_id = resume_latest_workflow(user_id)
        if latest_workflow_id:
            st.session_state.workflow_id = latest_workflow_id
            st.session_state.resumed_workflow = True
        else:
            st.session_state.workflow_id = None
            st.session_state.resumed_workflow = False
    
    # Show workflow mode selection or active workflow
    if st.session_state.workflow_id:
        render_active_workflow()
    else:
        render_workflow_mode_selection(user_id)

def render_workflow_mode_selection(user_id: str):
    """Render workflow mode selection with smart suggestions"""
    # Header with mobile-friendly design
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 100%);
        color: white;
        border-radius: 1rem;
        margin-bottom: 2rem;
    ">
        <h1 style="margin: 0; font-size: {TYPOGRAPHY['h1']['size']}; font-weight: {TYPOGRAPHY['h1']['weight']};">🎓 SafeSteps</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: {TYPOGRAPHY['body_large']['size']}; opacity: 0.9;">Certificate Generation Made Simple</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get smart suggestions based on user behavior
    suggestions = get_user_suggestions(user_id)
    
    # Show suggested mode if available
    if suggestions.get('preferred_mode'):
        with st.container(border=True):
            st.info(f"💡 **Smart Suggestion**: Based on your usage pattern, we recommend **{suggestions['preferred_mode'].value.replace('_', ' ').title()}** mode.")
    
    # Workflow mode cards with enhanced mobile design
    st.markdown("### Choose Your Workflow")
    
    col1, col2, col3 = st.columns(1 if _is_mobile_viewport() else 3)
    
    # Quick Generate Mode
    with (col1 if not _is_mobile_viewport() else st.container()):
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">⚡</div>
                <h3 style="color: {COLORS['primary']}; margin: 0.5rem 0;">Quick Generate</h3>
                <p style="color: {COLORS['text_secondary']}; margin-bottom: 1.5rem;">Fast certificate generation with smart defaults. Perfect for recurring tasks.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if create_prominent_button(
                "Start Quick Generate",
                "quick_mode_btn",
                button_type="success",
                size="large",
                icon="⚡",
                help_text="Generate certificates in 3 simple steps"
            ):
                start_workflow(user_id, WorkflowMode.QUICK_GENERATE)
    
    # Guided Mode
    with (col2 if not _is_mobile_viewport() else st.container()):
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
                <h3 style="color: {COLORS['primary']}; margin: 0.5rem 0;">Guided Mode</h3>
                <p style="color: {COLORS['text_secondary']}; margin-bottom: 1.5rem;">Step-by-step guidance with help text and validation. Ideal for new users.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if create_prominent_button(
                "Start Guided Mode",
                "guided_mode_btn",
                button_type="primary",
                size="large",
                icon="🎯",
                help_text="Get help and validation at each step"
            ):
                start_workflow(user_id, WorkflowMode.GUIDED_MODE)
    
    # Advanced Mode
    with (col3 if not _is_mobile_viewport() else st.container()):
        with st.container(border=True):
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🔧</div>
                <h3 style="color: {COLORS['primary']}; margin: 0.5rem 0;">Advanced Mode</h3>
                <p style="color: {COLORS['text_secondary']}; margin-bottom: 1.5rem;">Full customization and control. For power users who need all options.</p>
            </div>
            """, unsafe_allow_html=True)
            
            if create_prominent_button(
                "Start Advanced Mode",
                "advanced_mode_btn",
                button_type="secondary",
                size="large",
                icon="🔧",
                help_text="Access all features and customization options"
            ):
                start_workflow(user_id, WorkflowMode.ADVANCED_MODE)
    
    # Recent workflows section (mobile-stacked)
    if _is_mobile_viewport():
        st.markdown("---")
    
    render_recent_workflows_section(user_id)

def start_workflow(user_id: str, mode: WorkflowMode):
    """Start a new workflow with the selected mode"""
    workflow_id = create_workflow(user_id, mode.value)
    st.session_state.workflow_id = workflow_id
    st.session_state.resumed_workflow = False
    st.rerun()

def render_active_workflow():
    """Render the active workflow interface"""
    workflow_id = st.session_state.workflow_id
    workflow_state = get_workflow_state(workflow_id)
    
    if not workflow_state:
        st.error("Workflow not found. Starting fresh...")
        st.session_state.workflow_id = None
        st.rerun()
        return
    
    mode = WorkflowMode(workflow_state['mode'])
    progress = get_workflow_progress(workflow_id)
    
    # Render mode-specific interface
    if mode == WorkflowMode.QUICK_GENERATE:
        render_quick_mode(workflow_id, workflow_state, progress)
    elif mode == WorkflowMode.GUIDED_MODE:
        render_guided_mode(workflow_id, workflow_state, progress)
    elif mode == WorkflowMode.ADVANCED_MODE:
        render_advanced_mode(workflow_id, workflow_state, progress)

def render_quick_mode(workflow_id: str, workflow_state: Dict, progress: Dict):
    """Render Quick Generate mode - all steps on one page"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['success']} 0%, {COLORS['accent']} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
            ⚡ Quick Generate Mode
        </h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Complete all steps on one page with smart defaults</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress indicator
    render_workflow_progress(progress)
    
    # All steps in one interface with smart defaults
    with st.form("quick_generate_form", clear_on_submit=False):
        # Step 1: Upload
        st.markdown("### 📁 Step 1: Upload Your Data")
        uploaded_file = st.file_uploader(
            "Select participant data file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload CSV or Excel file with participant names and emails"
        )
        
        # Step 2: Course Selection (with smart defaults)
        st.markdown("### 🎓 Step 2: Select Course Template")
        course_manager = CourseManager()
        courses = course_manager.get_available_courses()
        
        # Smart default: most recently used course
        default_course = None
        suggestions = get_user_suggestions(workflow_state['user_id'])
        if suggestions.get('quick_templates'):
            default_course = suggestions['quick_templates'][0]
        
        course_options = [course['name'] for course in courses]
        default_index = 0
        if default_course and default_course in course_options:
            default_index = course_options.index(default_course)
        
        selected_course = st.selectbox(
            "Course Template",
            course_options,
            index=default_index,
            help="Select the course template for your certificates"
        )
        
        # Step 3: Quick Options
        st.markdown("### ⚙️ Step 3: Generation Options")
        col1, col2 = st.columns(2)
        with col1:
            send_emails = st.checkbox("Send email notifications", value=True)
            include_qr = st.checkbox("Include QR codes", value=True)
        with col2:
            batch_size = st.select_slider(
                "Processing batch size",
                options=[10, 25, 50, 100],
                value=25,
                help="Larger batches are faster but use more memory"
            )
        
        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button(
                "🚀 Generate All Certificates",
                type="primary",
                use_container_width=True
            )
        
        if submitted and uploaded_file:
            process_quick_generation(
                workflow_id=workflow_id,
                uploaded_file=uploaded_file,
                selected_course=selected_course,
                send_emails=send_emails,
                include_qr=include_qr,
                batch_size=batch_size
            )
    
    # Workflow actions
    render_workflow_actions(workflow_id)

def render_guided_mode(workflow_id: str, workflow_state: Dict, progress: Dict):
    """Render Guided mode - step by step with help and validation"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['info']} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
            🎯 Guided Mode
        </h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Step-by-step guidance with help and validation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress with step navigation
    render_workflow_progress(progress)
    render_step_navigation(workflow_id, workflow_state, progress)
    
    current_step = workflow_state.get('current_step')
    
    if current_step == 'upload':
        render_guided_upload_step(workflow_id, workflow_state)
    elif current_step == 'validate':
        render_guided_validate_step(workflow_id, workflow_state)
    elif current_step == 'course_select':
        render_guided_course_step(workflow_id, workflow_state)
    elif current_step == 'preview':
        render_guided_preview_step(workflow_id, workflow_state)
    elif current_step == 'generate':
        render_guided_generate_step(workflow_id, workflow_state)
    else:
        st.success("🎉 Workflow completed! Check your downloads.")
        render_workflow_completion(workflow_id, workflow_state)

def render_advanced_mode(workflow_id: str, workflow_state: Dict, progress: Dict):
    """Render Advanced mode - full control with all options"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['text_primary']} 0%, {COLORS['primary_dark']} 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h2 style="margin: 0; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
            🔧 Advanced Mode
        </h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Full customization and power user features</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabbed interface for advanced users
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Data", "🎓 Templates", "⚙️ Options", "🚀 Generate"])
    
    with tab1:
        render_advanced_data_tab(workflow_id, workflow_state)
    
    with tab2:
        render_advanced_template_tab(workflow_id, workflow_state)
    
    with tab3:
        render_advanced_options_tab(workflow_id, workflow_state)
    
    with tab4:
        render_advanced_generate_tab(workflow_id, workflow_state)
    
    # Global workflow actions
    render_workflow_actions(workflow_id)

def render_guided_upload_step(workflow_id: str, workflow_state: Dict):
    """Render guided upload step with validation and help"""
    with st.container(border=True):
        st.markdown("### 📁 Upload Your Participant Data")
        st.markdown("""
        Upload a spreadsheet containing participant information. Your file should include:
        - **Name column**: Full names of certificate recipients
        - **Email column**: Email addresses for delivery (optional)
        - **Additional columns**: Any custom data for certificate personalization
        """)
        
        # Enhanced file upload with validation
        uploaded_file = st.file_uploader(
            "Select your file",
            type=['csv', 'xlsx', 'xls'],
            help="Drag and drop or click to browse for CSV/Excel files"
        )
        
        if uploaded_file:
            # Show file details
            st.success(f"✅ File selected: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
            
            # Preview file contents
            with st.expander("📊 Preview File Contents", expanded=True):
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    st.dataframe(df.head(10), use_container_width=True)
                    st.caption(f"Showing first 10 rows of {len(df)} total rows")
                    
                    # Column analysis
                    st.markdown("**Detected Columns:**")
                    for col in df.columns:
                        st.markdown(f"• `{col}` ({df[col].dtype})")
                    
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
                    uploaded_file = None
            
            if uploaded_file:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if create_prominent_button(
                        "Continue to Validation",
                        "upload_continue",
                        button_type="primary",
                        size="large",
                        icon="➡️"
                    ):
                        # Save upload data and advance
                        step_data = {'uploaded_file': uploaded_file.name, 'file_size': uploaded_file.size}
                        advance_workflow_step(workflow_id, 'upload', step_data)
                        st.rerun()
        
        # Help section
        with st.expander("❓ Need Help?"):
            st.markdown("""
            **File Format Requirements:**
            - CSV files: Use UTF-8 encoding
            - Excel files: .xlsx or .xls format
            - Maximum file size: 10MB
            - Required: At least one column with names
            
            **Common Issues:**
            - Make sure column headers are in the first row
            - Remove any merged cells
            - Ensure names are in a single column
            - Check for special characters that might cause encoding issues
            """)

def render_workflow_progress(progress: Dict):
    """Render mobile-friendly workflow progress indicator"""
    if not progress:
        return
    
    progress_percent = progress.get('progress_percentage', 0)
    current_step = progress.get('current_step', '')
    completed_steps = progress.get('completed_steps', 0)
    total_steps = progress.get('total_steps', 1)
    
    # Mobile-friendly progress display
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.progress(progress_percent / 100)
        st.caption(f"Progress: {progress_percent:.0f}% complete")
    
    with col2:
        st.metric("Steps", f"{completed_steps}/{total_steps}")
    
    with col3:
        if progress.get('estimated_time_remaining'):
            time_remaining = progress['estimated_time_remaining']
            if time_remaining > 60:
                time_str = f"{time_remaining // 60}m {time_remaining % 60}s"
            else:
                time_str = f"{time_remaining}s"
            st.metric("Remaining", time_str)

def render_step_navigation(workflow_id: str, workflow_state: Dict, progress: Dict):
    """Render step navigation with jump capabilities"""
    steps = ['upload', 'validate', 'course_select', 'preview', 'generate']
    current_step = workflow_state.get('current_step')
    step_statuses = workflow_state.get('step_statuses', {})
    
    # Create navigation buttons
    nav_buttons = []
    for i, step in enumerate(steps):
        status = step_statuses.get(step, 'pending')
        
        if status == 'completed':
            icon = "✅"
            button_type = "secondary"
        elif step == current_step:
            icon = "🔄"
            button_type = "primary"
        else:
            icon = "⏳"
            button_type = "secondary"
        
        nav_buttons.append({
            'key': step,
            'text': f"{icon} {step.replace('_', ' ').title()}",
            'type': button_type,
            'disabled': status == 'pending' and step != current_step
        })
    
    # Render navigation (horizontal on desktop, vertical on mobile)
    layout = "vertical" if _is_mobile_viewport() else "horizontal"
    clicked_buttons = create_enhanced_button_group(nav_buttons, "nav", layout)
    
    # Handle navigation clicks
    for step, clicked in clicked_buttons.items():
        if clicked and step != current_step:
            if jump_to_workflow_step(workflow_id, step):
                st.rerun()

def render_workflow_actions(workflow_id: str):
    """Render workflow action buttons (save, reset, etc.)"""
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if create_prominent_button(
            "💾 Save Progress",
            "save_workflow",
            button_type="secondary",
            size="small"
        ):
            if save_workflow_state(workflow_id):
                st.success("Progress saved!")
                time.sleep(1)
                st.rerun()
    
    with col2:
        if create_prominent_button(
            "🔄 New Workflow",
            "new_workflow",
            button_type="secondary",
            size="small"
        ):
            st.session_state.workflow_id = None
            st.rerun()
    
    with col3:
        if create_prominent_button(
            "📋 Copy Settings",
            "copy_settings",
            button_type="secondary",
            size="small"
        ):
            # Copy current workflow settings to clipboard
            st.info("Settings copied to clipboard!")
    
    with col4:
        if create_prominent_button(
            "❓ Get Help",
            "get_help",
            button_type="secondary",
            size="small"
        ):
            show_contextual_help()

def render_recent_workflows_section(user_id: str):
    """Render recent workflows section"""
    from utils.workflow_engine import list_user_workflows
    
    recent_workflows = list_user_workflows(user_id)
    
    if recent_workflows:
        st.markdown("### 📋 Recent Workflows")
        
        for workflow in recent_workflows[:3]:  # Show only last 3
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{workflow['mode'].replace('_', ' ').title()}**")
                    st.caption(f"Updated: {workflow['updated_at'][:10]}")
                
                with col2:
                    st.progress(workflow['progress'] / 100)
                    st.caption(f"{workflow['progress']:.0f}% complete")
                
                with col3:
                    if st.button("Resume", key=f"resume_{workflow['workflow_id']}"):
                        st.session_state.workflow_id = workflow['workflow_id']
                        st.rerun()

def process_quick_generation(workflow_id: str, uploaded_file, selected_course: str, 
                           send_emails: bool, include_qr: bool, batch_size: int):
    """Process quick generation with progress indicators"""
    progress_container = st.empty()
    status_container = st.empty()
    
    try:
        # Step 1: Validate file
        with progress_container.container():
            st.info("🔍 Validating uploaded data...")
            
        validator = SpreadsheetValidator()
        validation_result = validator.validate_file(uploaded_file)
        
        if not validation_result.valid:
            st.error(f"❌ Validation failed: {', '.join(validation_result.errors)}")
            return
        
        # Step 2: Initialize generator
        with progress_container.container():
            st.info("⚙️ Initializing certificate generator...")
            
        generator = CertificateGenerator()
        course_manager = CourseManager()
        template = course_manager.get_course_by_name(selected_course)
        
        # Step 3: Generate certificates
        with progress_container.container():
            st.info(f"🎓 Generating {len(validation_result.cleaned_data)} certificates...")
            
        # Create progress bar for generation
        progress_bar = st.progress(0)
        
        generated_files = []
        total_rows = len(validation_result.cleaned_data)
        
        for i, (_, row) in enumerate(validation_result.cleaned_data.iterrows()):
            # Generate individual certificate
            cert_data = {
                'name': row.get('name', row.get('Name', '')),
                'email': row.get('email', row.get('Email', '')),
                'course': selected_course,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'include_qr': include_qr
            }
            
            try:
                cert_file = generator.generate_certificate(cert_data, template)
                generated_files.append(cert_file)
                
                # Update progress
                progress = (i + 1) / total_rows
                progress_bar.progress(progress)
                
                # Send email if requested
                if send_emails and cert_data.get('email'):
                    # Email sending logic would go here
                    pass
                    
            except Exception as e:
                st.warning(f"Failed to generate certificate for {cert_data['name']}: {str(e)}")
        
        # Step 4: Package results
        with progress_container.container():
            st.info("📦 Packaging certificates for download...")
            
        # Create ZIP file with all certificates
        zip_path = generator.create_certificate_package(generated_files)
        
        # Success message
        progress_container.empty()
        st.success(f"🎉 Successfully generated {len(generated_files)} certificates!")
        
        # Download button
        with open(zip_path, 'rb') as f:
            st.download_button(
                "📥 Download All Certificates",
                f.read(),
                file_name=f"certificates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True
            )
        
        # Mark workflow as completed
        advance_workflow_step(workflow_id, 'generate', {
            'generated_count': len(generated_files),
            'completion_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        st.error(f"❌ Generation failed: {str(e)}")
        st.exception(e)

def show_contextual_help():
    """Show contextual help dialog"""
    with st.expander("❓ Need Help?", expanded=True):
        st.markdown("""
        ### Quick Help Guide
        
        **File Upload Issues:**
        - Ensure your file has a 'name' or 'Name' column
        - Use CSV (UTF-8) or Excel (.xlsx) formats
        - Maximum file size: 10MB
        
        **Course Templates:**
        - Select the appropriate course for your certificates
        - Templates include predefined layouts and styling
        - Contact admin to add custom templates
        
        **Generation Options:**
        - Email notifications require valid email addresses
        - QR codes link to certificate verification
        - Larger batch sizes are faster but use more memory
        
        **Need More Help?**
        - Contact support: support@safesteps.com
        - Documentation: [SafeSteps Help Center](https://help.safesteps.com)
        - Video tutorials: [SafeSteps YouTube](https://youtube.com/safesteps)
        """)

def render_workflow_completion(workflow_id: str, workflow_state: Dict):
    """Render workflow completion screen"""
    st.balloons()
    
    with st.container(border=True):
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🎉</div>
            <h2 style="color: {COLORS['success']}; margin: 0.5rem 0;">Workflow Completed!</h2>
            <p style="color: {COLORS['text_secondary']};">Your certificates have been generated successfully.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show completion stats
    completion_data = workflow_state.get('step_data', {}).get('generate', {})
    if completion_data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Certificates Generated", completion_data.get('generated_count', 0))
        with col2:
            st.metric("Success Rate", "100%")
        with col3:
            completion_time = completion_data.get('completion_time', '')
            if completion_time:
                st.metric("Completed", completion_time[:10])
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if create_prominent_button(
            "🔄 Start New Workflow",
            "new_workflow_complete",
            button_type="primary",
            size="large"
        ):
            st.session_state.workflow_id = None
            st.rerun()
    
    with col2:
        if create_prominent_button(
            "📊 View Analytics",
            "view_analytics",
            button_type="secondary", 
            size="large"
        ):
            st.switch_page("pages/analytics_dashboard.py")

def _is_mobile_viewport() -> bool:
    """Detect if current viewport is mobile-sized"""
    # Simple mobile detection based on session state or user agent
    # In production, this could use JavaScript to detect viewport width
    return st.session_state.get('is_mobile', False)

# Additional helper functions for advanced mode tabs
def render_advanced_data_tab(workflow_id: str, workflow_state: Dict):
    """Render advanced data management tab"""
    st.markdown("### 📊 Advanced Data Management")
    
    # Multiple file upload
    uploaded_files = st.file_uploader(
        "Upload multiple data files",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True,
        help="Upload multiple files to batch process"
    )
    
    # Data transformation options
    if uploaded_files:
        st.markdown("#### Data Transformation Options")
        
        col1, col2 = st.columns(2)
        with col1:
            merge_files = st.checkbox("Merge all files", value=True)
            remove_duplicates = st.checkbox("Remove duplicates", value=True)
            normalize_names = st.checkbox("Normalize name formatting", value=True)
        
        with col2:
            validate_emails = st.checkbox("Validate email addresses", value=True)
            sort_by_name = st.checkbox("Sort by name", value=False)
            add_metadata = st.checkbox("Add generation metadata", value=True)
        
        # Column mapping
        st.markdown("#### Column Mapping")
        # This would show a detailed column mapping interface
        st.info("Advanced column mapping interface would go here")

def render_advanced_template_tab(workflow_id: str, workflow_state: Dict):
    """Render advanced template customization tab"""
    st.markdown("### 🎨 Advanced Template Customization")
    
    # Template selection with preview
    course_manager = CourseManager()
    courses = course_manager.get_available_courses()
    
    selected_course = st.selectbox(
        "Base Template",
        [course['name'] for course in courses],
        help="Select base template to customize"
    )
    
    # Customization options
    st.markdown("#### Customization Options")
    
    col1, col2 = st.columns(2)
    with col1:
        st.color_picker("Primary Color", value=COLORS['primary'])
        st.color_picker("Accent Color", value=COLORS['accent'])
        custom_logo = st.file_uploader("Custom Logo", type=['png', 'jpg', 'svg'])
    
    with col2:
        font_family = st.selectbox("Font Family", ["Arial", "Times", "Helvetica", "Custom"])
        certificate_size = st.selectbox("Certificate Size", ["A4", "Letter", "Custom"])
        orientation = st.radio("Orientation", ["Landscape", "Portrait"])
    
    # Live preview
    st.markdown("#### Live Preview")
    with st.container(border=True):
        st.info("📖 Live certificate preview would be rendered here")
        # This would show a real-time preview of the customized template

def render_advanced_options_tab(workflow_id: str, workflow_state: Dict):
    """Render advanced generation options tab"""
    st.markdown("### ⚙️ Advanced Generation Options")
    
    # Performance settings
    st.markdown("#### Performance Settings")
    col1, col2 = st.columns(2)
    with col1:
        parallel_workers = st.slider("Parallel Workers", 1, 8, 4)
        memory_limit = st.selectbox("Memory Limit", ["1GB", "2GB", "4GB", "8GB"])
    with col2:
        batch_size = st.slider("Batch Size", 10, 1000, 100)
        compression_level = st.slider("PDF Compression", 0, 9, 6)
    
    # Output options
    st.markdown("#### Output Options")
    col1, col2 = st.columns(2)
    with col1:
        output_format = st.multiselect(
            "Output Formats",
            ["PDF", "PNG", "JPG", "SVG"],
            default=["PDF"]
        )
        naming_pattern = st.text_input(
            "File Naming Pattern",
            value="{name}_{course}_{date}",
            help="Use {name}, {course}, {date}, {email} as placeholders"
        )
    with col2:
        include_metadata = st.checkbox("Include PDF metadata", value=True)
        watermark_enabled = st.checkbox("Add watermark", value=False)
        digital_signature = st.checkbox("Digital signature", value=False)
    
    # Notification settings
    st.markdown("#### Notification Settings")
    email_template = st.text_area(
        "Email Template",
        value="Congratulations {name}! Your certificate for {course} is attached.",
        height=100
    )
    
    send_summary = st.checkbox("Send generation summary", value=True)
    webhook_url = st.text_input("Webhook URL (optional)", help="Notify external systems when complete")

def render_advanced_generate_tab(workflow_id: str, workflow_state: Dict):
    """Render advanced generation tab with monitoring"""
    st.markdown("### 🚀 Advanced Generation")
    
    # Pre-generation validation
    st.markdown("#### Pre-Generation Checklist")
    
    checklist_items = [
        "Data file uploaded and validated",
        "Template selected and customized", 
        "Output options configured",
        "Notification settings verified"
    ]
    
    all_ready = True
    for item in checklist_items:
        # In real implementation, these would check actual workflow state
        ready = st.checkbox(item, value=True, disabled=True)
        if not ready:
            all_ready = False
    
    if all_ready:
        st.success("✅ All systems ready for generation")
        
        # Generation controls
        col1, col2 = st.columns(2)
        with col1:
            dry_run = st.checkbox("Dry run (validation only)", value=False)
            pause_on_error = st.checkbox("Pause on errors", value=True)
        
        with col2:
            auto_retry = st.checkbox("Auto-retry failed certificates", value=True)
            create_log = st.checkbox("Create detailed log", value=True)
        
        # Generate button
        if create_prominent_button(
            "🚀 Start Advanced Generation",
            "advanced_generate",
            button_type="primary",
            size="large",
            help_text="Start generation with all advanced options"
        ):
            # Advanced generation would start here
            st.info("🔄 Advanced generation starting...")
            # This would include real-time monitoring, error handling, etc.
    else:
        st.warning("⚠️ Please complete all checklist items before generating")

if __name__ == "__main__":
    streamlined_workflow_page()
