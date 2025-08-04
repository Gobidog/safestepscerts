"""
Flexible Workflow Engine Demo Page
Demonstrates the new workflow engine capabilities
"""
import streamlit as st
import time
from datetime import datetime
from utils.workflow_engine import (
    workflow_engine, create_workflow, get_workflow_state, 
    advance_workflow_step, jump_to_workflow_step, save_workflow_state,
    get_workflow_progress, get_user_suggestions, get_user_dashboard_widgets,
    list_user_workflows, resume_latest_workflow, WorkflowMode
)
from utils.ui_components import (
    apply_custom_css, create_flexible_workflow_selector,
    create_workflow_progress_bar, create_workflow_step_card,
    create_save_resume_panel, create_user_dashboard_widgets,
    create_keyboard_shortcuts_panel, create_workflow_analytics_panel
)
from utils.auth import get_current_user
import json

def render_workflow_engine_demo():
    """Main demo page for the flexible workflow engine"""
    
    # Apply custom CSS
    apply_custom_css()
    
    # Get current user
    current_user = get_current_user()
    user_id = current_user.get('username', 'demo_user')
    
    # Page header
    st.title("🚀 Flexible Workflow Engine Demo")
    st.markdown("Experience the new adaptive workflow system with multiple paths and smart features")
    
    # Initialize session state
    if 'current_workflow_id' not in st.session_state:
        st.session_state.current_workflow_id = None
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = 'selector'
    
    # Check for workflow resume request
    if 'resume_workflow' in st.session_state:
        st.session_state.current_workflow_id = st.session_state.resume_workflow
        st.session_state.demo_mode = 'workflow'
        del st.session_state.resume_workflow
        st.rerun()
    
    # Main content based on mode
    if st.session_state.demo_mode == 'selector':
        render_workflow_selector(user_id)
    elif st.session_state.demo_mode == 'workflow':
        render_active_workflow(user_id)
    elif st.session_state.demo_mode == 'analytics':
        render_analytics_dashboard(user_id)

def render_workflow_selector(user_id: str):
    """Render the workflow selection interface"""
    
    # Get user suggestions and dashboard widgets
    suggestions = get_user_suggestions(user_id)
    widgets = get_user_dashboard_widgets(user_id)
    recent_workflows = list_user_workflows(user_id)
    
    # Show personalized dashboard widgets
    if widgets:
        create_user_dashboard_widgets(widgets)
        st.divider()
    
    # Check for latest workflow resume
    if recent_workflows:
        latest = recent_workflows[0]
        if not latest['completed'] and latest['progress'] > 0:
            st.info(f"💡 You have an incomplete workflow ({latest['progress']:.0f}% complete)")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📂 Resume Latest Workflow", type="primary", use_container_width=True):
                    st.session_state.current_workflow_id = latest['workflow_id']
                    st.session_state.demo_mode = 'workflow'
                    st.rerun()
            with col2:
                if st.button("🆕 Start New Workflow", use_container_width=True):
                    pass  # Continue to selector below
            st.divider()
    
    # Workflow mode selector
    selected_mode = create_flexible_workflow_selector(user_id, suggestions)
    
    if selected_mode:
        # Create new workflow
        workflow_id = create_workflow(user_id, selected_mode)
        st.session_state.current_workflow_id = workflow_id
        st.session_state.demo_mode = 'workflow'
        st.success(f"✅ Created new {selected_mode.replace('_', ' ').title()} workflow!")
        time.sleep(1)
        st.rerun()
    
    # Show recent workflows if any
    if recent_workflows:
        st.subheader("📋 Recent Workflows")
        
        for workflow in recent_workflows[:5]:  # Show top 5
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                mode_name = workflow['mode'].replace('_', ' ').title()
                status = "✅ Completed" if workflow['completed'] else f"🔄 {workflow['progress']:.0f}%"
                st.write(f"**{mode_name}** - {status}")
                st.caption(f"Updated: {workflow['updated_at'].split('T')[0]}")
            
            with col2:
                st.metric("Progress", f"{workflow['progress']:.0f}%")
            
            with col3:
                if not workflow['completed']:
                    if st.button("📂", key=f"resume_{workflow['workflow_id']}", help="Resume"):
                        st.session_state.current_workflow_id = workflow['workflow_id']
                        st.session_state.demo_mode = 'workflow'
                        st.rerun()
                else:
                    st.success("✅")
            
            with col4:
                if st.button("🗑️", key=f"delete_{workflow['workflow_id']}", help="Delete"):
                    workflow_engine.delete_workflow(workflow['workflow_id'])
                    st.success("Deleted!")
                    st.rerun()
    
    # Navigation to analytics
    st.divider()
    if st.button("📊 View Analytics Dashboard", use_container_width=True):
        st.session_state.demo_mode = 'analytics'
        st.rerun()

def render_active_workflow(user_id: str):
    """Render the active workflow interface"""
    
    workflow_id = st.session_state.current_workflow_id
    if not workflow_id:
        st.error("No active workflow found")
        if st.button("← Back to Selector"):
            st.session_state.demo_mode = 'selector'
            st.rerun()
        return
    
    # Get workflow state and progress
    workflow_state = get_workflow_state(workflow_id)
    if not workflow_state:
        st.error("Workflow not found")
        st.session_state.current_workflow_id = None
        st.session_state.demo_mode = 'selector'
        st.rerun()
        return
    
    progress = get_workflow_progress(workflow_id)
    
    # Header with back button and mode info
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if st.button("← Back", help="Return to workflow selector"):
            st.session_state.demo_mode = 'selector'
            st.rerun()
    
    with col2:
        mode_name = workflow_state['mode'].replace('_', ' ').title()
        st.title(f"{mode_name} Workflow")
        st.caption(f"Workflow ID: {workflow_id[:8]}...")
    
    with col3:
        if progress['is_completed']:
            st.success("✅ Complete!")
        else:
            st.info(f"🔄 In Progress")
    
    # Progress bar
    create_workflow_progress_bar(progress)
    st.divider()
    
    # Save/Resume panel
    create_save_resume_panel(workflow_id, workflow_state.get('auto_save_enabled', True))
    
    # Keyboard shortcuts panel
    shortcuts = {
        'Alt+1': {'description': 'Jump to Upload step'},
        'Alt+2': {'description': 'Jump to Validation step'},
        'Alt+3': {'description': 'Jump to Course Selection step'},
        'Alt+4': {'description': 'Jump to Customization step'},
        'Alt+5': {'description': 'Jump to Preview step'},
        'Ctrl+G': {'description': 'Generate certificates'},
        'Ctrl+S': {'description': 'Save workflow'}
    }
    create_keyboard_shortcuts_panel(shortcuts)
    
    st.divider()
    
    # Workflow steps based on mode
    current_step = workflow_state.get('current_step')
    step_statuses = workflow_state.get('step_statuses', {})
    
    if workflow_state['mode'] == 'quick_generate':
        render_quick_generate_mode(workflow_id, workflow_state, current_step, step_statuses)
    elif workflow_state['mode'] == 'guided_mode':
        render_guided_mode(workflow_id, workflow_state, current_step, step_statuses)
    elif workflow_state['mode'] == 'advanced_mode':
        render_advanced_mode(workflow_id, workflow_state, current_step, step_statuses)
    
    # Auto-save functionality
    if workflow_state.get('auto_save_enabled', True):
        # Simulate auto-save every 30 seconds
        if 'last_auto_save' not in st.session_state:
            st.session_state.last_auto_save = time.time()
        
        if time.time() - st.session_state.last_auto_save > 30:
            save_workflow_state(workflow_id)
            st.session_state.last_auto_save = time.time()
            st.toast("💾 Auto-saved!", icon="✅")

def render_quick_generate_mode(workflow_id: str, workflow_state: dict, current_step: str, step_statuses: dict):
    """Render Quick Generate mode interface"""
    
    st.subheader("⚡ Quick Generate Mode")
    st.info("Streamlined interface for fast certificate generation")
    
    # All steps visible in columns (express style)
    step_cols = st.columns(4)  # Skip customization and preview in quick mode
    
    steps_info = {
        'upload': {'name': 'Upload', 'description': 'Upload student data'},
        'validate': {'name': 'Validate', 'description': 'Validate data format'},
        'course_select': {'name': 'Course', 'description': 'Select course template'},
        'generate': {'name': 'Generate', 'description': 'Create certificates'}
    }
    
    with step_cols[0]:
        action = create_workflow_step_card('upload', steps_info['upload'], workflow_state, current_step == 'upload')
        if action:
            handle_step_action(workflow_id, action)
    
    with step_cols[1]:
        action = create_workflow_step_card('validate', steps_info['validate'], workflow_state, current_step == 'validate')
        if action:
            handle_step_action(workflow_id, action)
    
    with step_cols[2]:
        action = create_workflow_step_card('course_select', steps_info['course_select'], workflow_state, current_step == 'course_select')
        if action:
            handle_step_action(workflow_id, action)
    
    with step_cols[3]:
        action = create_workflow_step_card('generate', steps_info['generate'], workflow_state, current_step == 'generate')
        if action:
            handle_step_action(workflow_id, action)
    
    # Quick actions bar
    st.divider()
    st.subheader("⚡ Quick Actions")
    
    action_cols = st.columns(4)
    
    with action_cols[0]:
        if st.button("📤 Upload & Validate", use_container_width=True, type="primary"):
            simulate_quick_action(workflow_id, "upload_and_validate")
    
    with action_cols[1]:
        if st.button("🎯 Smart Select", use_container_width=True):
            simulate_quick_action(workflow_id, "smart_course_select")
    
    with action_cols[2]:
        if st.button("🚀 Generate All", use_container_width=True):
            simulate_quick_action(workflow_id, "generate_all")
    
    with action_cols[3]:
        if st.button("📦 Bulk Download", use_container_width=True):
            simulate_quick_action(workflow_id, "bulk_download")

def render_guided_mode(workflow_id: str, workflow_state: dict, current_step: str, step_statuses: dict):
    """Render Guided mode interface"""
    
    st.subheader("🧭 Guided Mode") 
    st.info("Step-by-step guidance with help and validation")
    
    # Current step focus
    if current_step:
        st.subheader(f"Current Step: {current_step.replace('_', ' ').title()}")
        
        steps_info = {
            'upload': {
                'name': 'Upload Student Data',
                'description': 'Upload your CSV or Excel file with student information',
                'help_text': 'Make sure your file includes columns: name, email, and any additional fields needed'
            },
            'validate': {
                'name': 'Validate Data',
                'description': 'We\'ll check your data for completeness and format',
                'help_text': 'This automatic step ensures your data meets requirements'
            },
            'course_select': {
                'name': 'Select Course Template',  
                'description': 'Choose the appropriate course for your certificates',
                'help_text': 'Browse available courses or search for specific topics'
            },
            'customize': {
                'name': 'Customize Template',
                'description': 'Personalize your certificate design and content',
                'help_text': 'Add logos, adjust colors, and customize the certificate message'
            },
            'preview': {
                'name': 'Preview Certificates',
                'description': 'Review how your certificates will look',
                'help_text': 'Check a sample certificate before generating the full batch'
            },
            'generate': {
                'name': 'Generate Certificates',
                'description': 'Create and download your certificate files',
                'help_text': 'This will create a ZIP file with all certificates'
            }
        }
        
        step_info = steps_info.get(current_step, {})
        action = create_workflow_step_card(current_step, step_info, workflow_state, True)
        if action:
            handle_step_action(workflow_id, action)
        
        # Step-specific content
        render_step_content(workflow_id, current_step, workflow_state)
    
    # Progress overview
    st.divider()
    st.subheader("📋 All Steps Overview")
    
    for step_id in ['upload', 'validate', 'course_select', 'customize', 'preview', 'generate']:
        if step_id in step_statuses:
            step_info = {
                'name': step_id.replace('_', ' ').title(),
                'description': f"Step: {step_id}"
            }
            
            with st.expander(f"{step_info['name']} - {step_statuses[step_id].title()}", 
                           expanded=(step_id == current_step)):
                action = create_workflow_step_card(step_id, step_info, workflow_state, step_id == current_step)
                if action:
                    handle_step_action(workflow_id, action)

def render_advanced_mode(workflow_id: str, workflow_state: dict, current_step: str, step_statuses: dict):
    """Render Advanced mode interface"""
    
    st.subheader("🎛️ Advanced Mode")
    st.info("Full control with all customization options available")
    
    # Tabbed interface for advanced features
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Workflow", "🎨 Customization", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        # Standard workflow steps
        for step_id in ['upload', 'validate', 'course_select', 'customize', 'preview', 'generate']:
            if step_id in step_statuses:
                step_info = {
                    'name': step_id.replace('_', ' ').title(),
                    'description': f"Advanced {step_id} with full control"
                }
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    action = create_workflow_step_card(step_id, step_info, workflow_state, step_id == current_step)
                    if action:
                        handle_step_action(workflow_id, action)
                
                with col2:
                    # Advanced options for each step
                    if st.button(f"⚙️ Advanced", key=f"adv_{step_id}", use_container_width=True):
                        st.session_state[f"show_advanced_{step_id}"] = True
                
                # Show advanced options if requested
                if st.session_state.get(f"show_advanced_{step_id}", False):
                    with st.container(border=True):
                        st.subheader(f"Advanced {step_id.title()} Options")
                        render_advanced_step_options(step_id)
                        
                        if st.button("Close Advanced Options", key=f"close_adv_{step_id}"):
                            st.session_state[f"show_advanced_{step_id}"] = False
                            st.rerun()
    
    with tab2:
        st.subheader("🎨 Template Customization")
        render_template_customization()
    
    with tab3:
        st.subheader("📊 Real-time Analytics")
        render_workflow_analytics_panel(workflow_state['user_id'], workflow_engine)
    
    with tab4:
        st.subheader("⚙️ Advanced Settings")
        render_advanced_settings(workflow_id, workflow_state)

def render_step_content(workflow_id: str, step_id: str, workflow_state: dict):
    """Render step-specific content"""
    
    if step_id == 'upload':
        st.subheader("📤 Upload Your Data")
        uploaded_file = st.file_uploader(
            "Choose CSV or Excel file",
            type=['csv', 'xlsx'],
            help="Upload file with student information"
        )
        
        if uploaded_file:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info("Click 'Continue' to proceed to validation")
            
            # Simulate file processing
            if st.button("📊 Preview File Content", use_container_width=True):
                st.write("**File Preview:**")
                st.text("name,email,department\nJohn Doe,john@example.com,IT\nJane Smith,jane@example.com,HR")
    
    elif step_id == 'validate':
        st.subheader("✅ Data Validation")
        with st.spinner("Validating your data..."):
            time.sleep(1)  # Simulate validation
        
        st.success("✅ Data validation passed!")
        st.write("**Validation Results:**")
        st.write("• ✅ Required columns found: name, email")
        st.write("• ✅ 25 valid records found")
        st.write("• ✅ No data errors detected")
    
    elif step_id == 'course_select':
        st.subheader("🎯 Select Course Template")
        
        course_options = [
            "Digital Citizenship & Safety",
            "Cybersecurity Basics",
            "Data Privacy Fundamentals", 
            "Online Safety for Kids"
        ]
        
        selected_course = st.selectbox(
            "Choose course template:",
            course_options,
            help="Select the course that matches your training content"
        )
        
        if selected_course:
            st.success(f"✅ Selected: {selected_course}")
            
            # Show course preview
            with st.expander("🔍 Course Preview", expanded=True):
                st.write(f"**Course:** {selected_course}")
                st.write("**Description:** Comprehensive training on digital safety and best practices")
                st.write("**Certificate Style:** Professional with company branding")

def render_template_customization():
    """Render template customization interface"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎨 Design Options")
        
        # Color scheme
        color_scheme = st.selectbox(
            "Color Scheme",
            ["Professional Blue", "Elegant Gold", "Modern Green", "Classic Red"]
        )
        
        # Logo upload
        logo_file = st.file_uploader("Upload Logo", type=['png', 'jpg', 'jpeg'])
        
        # Font selection
        font_style = st.selectbox(
            "Font Style", 
            ["Arial", "Times New Roman", "Helvetica", "Georgia"]
        )
        
        # Certificate size
        cert_size = st.selectbox(
            "Certificate Size",
            ["A4 Landscape", "A4 Portrait", "Letter Landscape", "Custom"]
        )
    
    with col2:
        st.subheader("📝 Content Options")
        
        # Custom message
        custom_message = st.text_area(
            "Custom Message",
            value="This certifies that",
            help="Customize the certificate message"
        )
        
        # Date format
        date_format = st.selectbox(
            "Date Format",
            ["MM/DD/YYYY", "DD/MM/YYYY", "Month DD, YYYY", "DD Month YYYY"]
        )
        
        # Signature options
        signature_style = st.selectbox(
            "Signature Style",
            ["Digital Signature", "Scanned Signature", "Text Only", "None"]
        )
        
        # Additional fields
        include_fields = st.multiselect(
            "Additional Fields",
            ["Course Duration", "Credits Earned", "Instructor Name", "Certificate ID"]
        )

def render_advanced_step_options(step_id: str):
    """Render advanced options for specific steps"""
    
    if step_id == 'upload':
        st.write("**Advanced Upload Options:**")
        
        # File validation rules
        st.checkbox("Strict column validation", value=True)
        st.checkbox("Allow missing optional fields", value=True)
        st.number_input("Max file size (MB)", min_value=1, max_value=100, value=10)
        
        # Data transformation
        st.selectbox("Text encoding", ["UTF-8", "Latin-1", "Windows-1252"])
        st.checkbox("Auto-trim whitespace", value=True)
        st.checkbox("Convert names to title case", value=True)
    
    elif step_id == 'generate':
        st.write("**Advanced Generation Options:**")
        
        # Batch processing
        st.number_input("Batch size", min_value=1, max_value=1000, value=100)
        st.checkbox("Generate in background", value=False)
        st.checkbox("Email certificates automatically", value=False)
        
        # Quality settings
        st.selectbox("PDF Quality", ["High", "Medium", "Low"])
        st.checkbox("Include watermark", value=False)
        st.checkbox("Enable digital signatures", value=False)

def render_advanced_settings(workflow_id: str, workflow_state: dict):
    """Render advanced workflow settings"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Workflow Settings")
        
        # Auto-save settings
        auto_save = st.checkbox("Enable auto-save", value=workflow_state.get('auto_save_enabled', True))
        if auto_save:
            auto_save_interval = st.slider("Auto-save interval (seconds)", 15, 300, 30)
        
        # Keyboard shortcuts
        shortcuts_enabled = st.checkbox("Enable keyboard shortcuts", value=workflow_state.get('shortcuts_enabled', True))
        
        # Workflow timeout
        timeout_minutes = st.number_input("Workflow timeout (minutes)", min_value=30, max_value=480, value=120)
    
    with col2:
        st.subheader("📊 Behavior Tracking")
        
        # Privacy settings
        st.checkbox("Track usage analytics", value=True)
        st.checkbox("Save performance metrics", value=True)
        st.checkbox("Enable smart suggestions", value=True)
        
        # Data retention
        retention_days = st.number_input("Keep workflow data (days)", min_value=7, max_value=365, value=90)
    
    # Apply settings
    if st.button("💾 Save Settings", use_container_width=True, type="primary"):
        # Update workflow settings
        workflow = workflow_engine.get_workflow(workflow_id)
        if workflow:
            workflow.auto_save_enabled = auto_save
            workflow.shortcuts_enabled = shortcuts_enabled
            workflow_engine.save_workflow(workflow_id)
            st.success("✅ Settings saved!")

def render_analytics_dashboard(user_id: str):
    """Render the analytics dashboard"""
    
    st.title("📊 Workflow Analytics Dashboard")
    
    # Back button
    if st.button("← Back to Workflows"):
        st.session_state.demo_mode = 'selector'
        st.rerun()
    
    # Analytics content
    create_workflow_analytics_panel(user_id, workflow_engine)
    
    # Additional analytics
    workflows = list_user_workflows(user_id)
    if workflows:
        st.divider()
        st.subheader("📈 Workflow History")
        
        # Create a simple chart of workflow completion over time
        import pandas as pd
        
        df_data = []
        for wf in workflows:
            df_data.append({
                'Date': wf['created_at'].split('T')[0],
                'Mode': wf['mode'].replace('_', ' ').title(),
                'Progress': wf['progress'],
                'Completed': wf['completed']
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            
            # Mode usage chart
            st.subheader("📊 Mode Usage")
            mode_counts = df['Mode'].value_counts()
            st.bar_chart(mode_counts)
            
            # Completion rate
            completion_rate = (df['Completed'].sum() / len(df)) * 100
            st.metric("Completion Rate", f"{completion_rate:.0f}%")

def handle_step_action(workflow_id: str, action: str):
    """Handle workflow step actions"""
    
    if action.startswith('continue_'):
        step_id = action.replace('continue_', '')
        # Simulate step completion
        advance_workflow_step(workflow_id, step_id, {'completed_at': datetime.now().isoformat()})
        st.success(f"✅ Completed {step_id}!")
        st.rerun()
    
    elif action.startswith('jump_'):
        step_id = action.replace('jump_', '')
        if jump_to_workflow_step(workflow_id, step_id):
            st.success(f"🚀 Jumped to {step_id}!")
            st.rerun()
        else:
            st.error("Cannot jump to this step - dependencies not met")
    
    elif action.startswith('skip_'):
        step_id = action.replace('skip_', '')
        if workflow_engine.skip_step(workflow_id, step_id):
            st.info(f"⏭️ Skipped {step_id}")
            st.rerun()
        else:
            st.error("Cannot skip required step")
    
    elif action.startswith('edit_'):
        step_id = action.replace('edit_', '')
        if jump_to_workflow_step(workflow_id, step_id):
            st.info(f"✏️ Editing {step_id}...")
            st.rerun()

def simulate_quick_action(workflow_id: str, action: str):
    """Simulate quick actions for demo purposes"""
    
    if action == "upload_and_validate":
        advance_workflow_step(workflow_id, 'upload', {'file': 'demo_students.csv'})
        advance_workflow_step(workflow_id, 'validate', {'valid': True, 'records': 25})
        st.success("✅ Upload and validation completed!")
        st.rerun()
    
    elif action == "smart_course_select":
        advance_workflow_step(workflow_id, 'course_select', {'course': 'Digital Citizenship & Safety'})
        st.success("✅ Smart course selection completed!")
        st.rerun()
    
    elif action == "generate_all":
        advance_workflow_step(workflow_id, 'generate', {'certificates': 25, 'file_size': '2.3MB'})
        st.success("✅ All certificates generated!")
        st.balloons()
        st.rerun()
    
    elif action == "bulk_download":
        st.download_button(
            "📦 Download All Certificates",
            data=b"Demo certificate data",
            file_name="certificates_demo.zip",
            mime="application/zip",
            use_container_width=True
        )

if __name__ == "__main__":
    render_workflow_engine_demo()