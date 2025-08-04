"""
SafeSteps V2 - User-Friendly Guidance Dashboard
Help-rich admin interface with tutorials and guidance for beginners
"""
import streamlit as st
from datetime import datetime
import json
from typing import Dict, List, Any

from utils.auth import requires_admin, get_current_user
from utils.ui_components import (
    create_tutorial_overlay, create_help_tooltip, create_card,
    create_metric_card, create_empty_state, COLORS
)
from utils.ui_helpers import (
    manage_navigation_state, manage_tutorial_state, advance_tutorial_step,
    complete_tutorial, skip_tutorial, is_tutorial_completed
)
from utils.help_system import (
    HelpSystem, create_contextual_help, show_help_modal,
    create_guided_tour
)
from utils.workflow_persistence import (
    WorkflowPersistence, save_workflow_checkpoint, load_workflow_checkpoint
)
from utils.storage import StorageManager
from utils.course_manager import CourseManager

# Initialize managers
storage = StorageManager()
course_manager = CourseManager(storage.local_path / "metadata")
help_system = HelpSystem()
workflow_persistence = WorkflowPersistence()

@requires_admin
def render_dashboard_v2():
    """Render the user-friendly guided dashboard"""
    
    current_user = get_current_user()
    
    # Check if user is new (first time using guided interface)
    is_new_user = not st.session_state.get('guided_dashboard_visited', False)
    
    # Header with welcome message
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("🎓 SafeSteps Guided Dashboard")
        if is_new_user:
            st.info("👋 Welcome! This guided interface will help you get started with SafeSteps.")
        else:
            st.caption(f"Welcome back, {current_user.get('username', 'Admin')}! Need help? Click the 🎓 icons.")
    
    with col2:
        # Tutorial toggle
        show_tutorials = st.toggle(
            "📚 Show Tutorials", 
            value=st.session_state.get('show_tutorials', True),
            help="Toggle tutorial overlays and guidance"
        )
        st.session_state['show_tutorials'] = show_tutorials
    
    with col3:
        # Help center button
        if st.button("❓ Help Center", use_container_width=True):
            st.session_state['show_help_center'] = True
    
    # Mark as visited
    st.session_state['guided_dashboard_visited'] = True
    
    # Show initial tutorial for new users
    if is_new_user and show_tutorials:
        render_welcome_tutorial()
    
    # Help center modal
    if st.session_state.get('show_help_center', False):
        render_help_center()
    
    st.divider()
    
    # Getting Started Section (for new users)
    if is_new_user or st.session_state.get('show_getting_started', False):
        render_getting_started_section()
    
    # Main dashboard content with guidance
    render_guided_main_content()
    
    # Contextual help sidebar
    render_help_sidebar()

def render_welcome_tutorial():
    """Render welcome tutorial for new users"""
    tutorial_id = "welcome_tutorial"
    tutorial_state = manage_tutorial_state(tutorial_id)
    
    if not is_tutorial_completed(tutorial_id):
        tutorial_steps = [
            {
                "title": "Welcome to SafeSteps!",
                "content": """
                This guided dashboard is designed to help you manage certificates easily.
                
                **What you can do here:**
                - Generate certificates for students
                - Manage users and permissions
                - Create and manage certificate templates
                - View analytics and reports
                
                Let's take a quick tour!
                """
            },
            {
                "title": "Dashboard Layout",
                "content": """
                The dashboard is organized into clear sections:
                
                📊 **Quick Stats** - See your key metrics at a glance
                🏆 **Certificate Management** - Your main tools for certificates
                👥 **User Management** - Manage who can access the system
                📄 **Templates** - Create and manage certificate designs
                
                Each section has helpful tooltips and guidance.
                """
            },
            {
                "title": "Getting Help",
                "content": """
                Look for these helpful features:
                
                🎓 **Tutorial icons** - Click for contextual help
                ❓ **Help Center** - Comprehensive documentation
                💡 **Tips** - Helpful hints throughout the interface
                📚 **Guided workflows** - Step-by-step processes
                
                You can always toggle tutorials on/off in the top right.
                """
            }
        ]
        
        current_step = tutorial_state['current_step']
        total_steps = len(tutorial_steps)
        
        if current_step <= total_steps:
            step_data = tutorial_steps[current_step - 1]
            
            nav_result = create_tutorial_overlay(
                step_data['title'],
                step_data['content'],
                current_step,
                total_steps
            )
            
            if nav_result['next']:
                if current_step < total_steps:
                    advance_tutorial_step(tutorial_id)
                    st.rerun()
                else:
                    complete_tutorial(tutorial_id)
                    st.success("🎉 Welcome tutorial completed! You're ready to go.")
                    st.rerun()
            
            if nav_result['prev'] and current_step > 1:
                tutorial_state['current_step'] = current_step - 1
                st.rerun()
            
            if nav_result['skip']:
                skip_tutorial(tutorial_id)
                st.info("Tutorial skipped. You can restart it anytime from the Help Center.")
                st.rerun()

def render_getting_started_section():
    """Render getting started section with quick actions"""
    with st.container(border=True):
        st.subheader("🚀 Getting Started")
        
        # Progress checklist
        checklist_items = [
            {"key": "tutorial_completed", "label": "Complete welcome tutorial", "completed": is_tutorial_completed("welcome_tutorial")},
            {"key": "first_certificate", "label": "Generate your first certificate", "completed": st.session_state.get('first_certificate_generated', False)},
            {"key": "user_added", "label": "Add a team member", "completed": st.session_state.get('first_user_added', False)},
            {"key": "template_customized", "label": "Customize a template", "completed": st.session_state.get('first_template_customized', False)}
        ]
        
        completed_count = sum(1 for item in checklist_items if item['completed'])
        progress_percent = (completed_count / len(checklist_items)) * 100
        
        st.progress(progress_percent / 100, text=f"Setup Progress: {completed_count}/{len(checklist_items)} tasks completed")
        
        # Checklist
        col1, col2 = st.columns(2)
        
        with col1:
            for item in checklist_items[:2]:
                icon = "✅" if item['completed'] else "⭕"
                st.markdown(f"{icon} {item['label']}")
        
        with col2:
            for item in checklist_items[2:]:
                icon = "✅" if item['completed'] else "⭕"
                st.markdown(f"{icon} {item['label']}")
        
        # Quick start buttons
        st.markdown("**Quick Actions:**")
        action_cols = st.columns(4)
        
        with action_cols[0]:
            if st.button("🏆 Generate Certificate", use_container_width=True, type="primary"):
                st.session_state['navigate_to'] = 'certificate_wizard'
        
        with action_cols[1]:
            if st.button("👤 Add User", use_container_width=True):
                st.session_state['show_add_user_wizard'] = True
        
        with action_cols[2]:
            if st.button("📄 Browse Templates", use_container_width=True):
                st.session_state['navigate_to'] = 'template_gallery'
        
        with action_cols[3]:
            if st.button("📚 View Guide", use_container_width=True):
                st.session_state['show_complete_guide'] = True
        
        # Hide getting started option
        if completed_count >= 2:  # If user has made some progress
            if st.button("✖️ Hide Getting Started", key="hide_getting_started"):
                st.session_state['show_getting_started'] = False
                st.rerun()

def render_guided_main_content():
    """Render main dashboard content with contextual help"""
    
    # Key metrics with explanations
    st.subheader("📊 Your Dashboard Overview")
    create_help_tooltip(
        "These metrics show your current SafeSteps activity. Numbers update in real-time as you use the system.",
        "🎓 About Dashboard Metrics"
    )
    
    metrics_cols = st.columns(4)
    
    with metrics_cols[0]:
        create_metric_card(
            "Certificates This Month",
            "247",
            "🏆",
            "success"
        )
        create_help_tooltip("Total certificates generated this month. Includes all templates and courses.")
    
    with metrics_cols[1]:
        create_metric_card(
            "Active Users",
            "23",
            "👥",
            "info"
        )
        create_help_tooltip("Users who have logged in within the last 30 days.")
    
    with metrics_cols[2]:
        create_metric_card(
            "Templates Available",
            "8",
            "📄",
            "warning"
        )
        create_help_tooltip("Number of certificate templates ready to use. You can create custom templates too!")
    
    with metrics_cols[3]:
        create_metric_card(
            "System Health",
            "98%",
            "💚",
            "success"
        )
        create_help_tooltip("Overall system performance and availability.")
    
    st.divider()
    
    # Main action areas with guidance
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        render_certificate_management_guided()
        st.divider()
        render_user_management_guided()
    
    with col_right:
        render_quick_actions_panel()
        st.divider()
        render_recent_activity_guided()

def render_certificate_management_guided():
    """Render certificate management with guidance"""
    col_header, col_help = st.columns([3, 1])
    
    with col_header:
        st.subheader("🏆 Certificate Management")
    
    with col_help:
        if st.button("🎓 Certificate Help", key="cert_help"):
            st.session_state['show_certificate_help'] = True
    
    # Certificate help modal
    if st.session_state.get('show_certificate_help', False):
        with st.container(border=True):
            st.markdown("### 🏆 Certificate Management Help")
            st.markdown("""
            **What are certificates?**
            Digital certificates are awarded to students who complete courses or training.
            
            **How to generate certificates:**
            1. **Upload student data** - CSV or Excel file with student names and emails
            2. **Choose a template** - Select from existing templates or create custom ones
            3. **Review and generate** - Check everything looks correct
            4. **Download or email** - Get your certificates as PDF files
            
            **Tips for success:**
            - Make sure your data file has 'name' and 'email' columns
            - Preview templates before generating large batches
            - Test with a small group first
            """)
            
            if st.button("Close Help", type="primary"):
                st.session_state['show_certificate_help'] = False
                st.rerun()
    
    # Certificate actions with guidance
    cert_tabs = st.tabs(["🚀 Quick Generate", "📋 Manage Batches", "📄 Templates"])
    
    with cert_tabs[0]:
        st.markdown("**Generate certificates in 3 easy steps:**")
        
        # Step-by-step guidance
        step_cols = st.columns(3)
        
        with step_cols[0]:
            with st.container(border=True):
                st.markdown("**Step 1: Upload Data**")
                st.markdown("📤 Upload your student list")
                
                if st.button("📁 Choose File", use_container_width=True, type="primary"):
                    st.session_state['show_upload_wizard'] = True
                
                create_help_tooltip(
                    "Upload a CSV or Excel file with student information. Required columns: 'name' and 'email'."
                )
        
        with step_cols[1]:
            with st.container(border=True):
                st.markdown("**Step 2: Pick Template**")
                st.markdown("🎨 Choose certificate design")
                
                template_options = ["Digital Citizenship", "Safety Training", "Compliance Course"]
                selected_template = st.selectbox(
                    "Template",
                    template_options,
                    key="guided_template_select",
                    help="Select the certificate template to use"
                )
                
                create_help_tooltip(
                    "Templates define how your certificates look. You can preview them before generating."
                )
        
        with step_cols[2]:
            with st.container(border=True):
                st.markdown("**Step 3: Generate**")
                st.markdown("🏆 Create certificates")
                
                if st.button("✨ Generate Now", use_container_width=True, type="primary"):
                    st.success("🎉 Certificate generation started!")
                    st.session_state['first_certificate_generated'] = True
                    # In real app, this would start the generation process
                
                create_help_tooltip(
                    "Click to start generating certificates. You'll get a ZIP file with all certificates as PDFs."
                )
    
    with cert_tabs[1]:
        st.markdown("**Your Certificate Batches**")
        
        # Show recent batches with status
        batch_data = [
            {"name": "January Safety Training", "status": "Completed", "count": 45, "date": "2024-01-15"},
            {"name": "Q4 Compliance Certificates", "status": "Processing", "count": 23, "date": "2024-01-14"},
            {"name": "Digital Citizenship Batch 3", "status": "Ready", "count": 67, "date": "2024-01-13"}
        ]
        
        for batch in batch_data:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{batch['name']}**")
                    st.caption(f"Created: {batch['date']}")
                
                with col2:
                    status_colors = {"Completed": "success", "Processing": "info", "Ready": "warning"}
                    status_color = status_colors.get(batch['status'], 'secondary')
                    if status_color == "success":
                        st.success(f"✅ {batch['status']}")
                    elif status_color == "info":
                        st.info(f"🔄 {batch['status']}")
                    else:
                        st.warning(f"⏳ {batch['status']}")
                
                with col3:
                    st.metric("Certificates", batch['count'])
                
                with col4:
                    if batch['status'] == 'Completed':
                        if st.button("📥 Download", key=f"download_{batch['name']}"):
                            st.success("Download started!")
                    elif batch['status'] == 'Ready':
                        if st.button("🚀 Generate", key=f"generate_{batch['name']}"):
                            st.success("Generation started!")
                    else:
                        st.button("⏳ Processing", disabled=True)
    
    with cert_tabs[2]:
        st.markdown("**Available Templates**")
        create_help_tooltip(
            "Templates determine how your certificates look. You can use built-in templates or create custom ones."
        )
        
        # Template gallery with previews
        template_cols = st.columns(2)
        
        templates = [
            {"name": "Digital Citizenship", "description": "Modern design for digital literacy courses", "uses": 156},
            {"name": "Safety Training", "description": "Professional template for safety certifications", "uses": 89},
            {"name": "Compliance Course", "description": "Formal design for compliance training", "uses": 234},
            {"name": "General Achievement", "description": "Versatile template for any course", "uses": 45}
        ]
        
        for idx, template in enumerate(templates):
            col_idx = idx % 2
            with template_cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**📄 {template['name']}**")
                    st.caption(template['description'])
                    st.text(f"Used {template['uses']} times")
                    
                    template_action_cols = st.columns(2)
                    with template_action_cols[0]:
                        if st.button("👁️ Preview", key=f"preview_{template['name']}", use_container_width=True):
                            st.session_state[f'show_preview_{template["name"]}'] = True
                    
                    with template_action_cols[1]:
                        if st.button("🚀 Use", key=f"use_{template['name']}", use_container_width=True):
                            st.success(f"Using {template['name']} template!")

def render_user_management_guided():
    """Render user management with guidance"""
    col_header, col_help = st.columns([3, 1])
    
    with col_header:
        st.subheader("👥 User Management")
    
    with col_help:
        if st.button("🎓 User Help", key="user_help"):
            st.session_state['show_user_help'] = True
    
    # User help modal
    if st.session_state.get('show_user_help', False):
        with st.container(border=True):
            st.markdown("### 👥 User Management Help")
            st.markdown("""
            **User Roles Explained:**
            - **Admin**: Full access to all features, can manage other users
            - **User**: Can generate certificates and view their own data
            - **Guest**: Read-only access for viewing certificates
            
            **Adding Users:**
            1. Click "Add New User"
            2. Enter their name and email
            3. Choose their role
            4. They'll receive login instructions by email
            
            **Security Tips:**
            - Only give admin access to trusted team members
            - Regularly review user list and remove inactive accounts
            - Use strong passwords and consider enabling 2FA
            """)
            
            if st.button("Close Help", type="primary"):
                st.session_state['show_user_help'] = False
                st.rerun()
    
    # User management interface
    user_tabs = st.tabs(["👤 Add User", "📋 Manage Users", "🔐 Permissions"])
    
    with user_tabs[0]:
        st.markdown("**Add a new team member:**")
        
        with st.form("add_user_guided"):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input(
                    "Username",
                    placeholder="john.doe",
                    help="Choose a unique username (letters, numbers, dots, underscores)"
                )
                
                new_email = st.text_input(
                    "Email Address",
                    placeholder="john.doe@company.com",
                    help="User's email address for login and notifications"
                )
            
            with col2:
                new_role = st.selectbox(
                    "Role",
                    ["user", "admin"],
                    help="Choose user's permission level"
                )
                
                send_welcome = st.checkbox(
                    "Send Welcome Email",
                    value=True,
                    help="Automatically send login instructions"
                )
            
            # Role explanation
            if new_role == "admin":
                st.info("👑 **Admin users** can manage all aspects of SafeSteps including other users.")
            else:
                st.info("👤 **Regular users** can generate certificates and manage their own data.")
            
            col_submit, col_cancel = st.columns(2)
            
            with col_submit:
                if st.form_submit_button("➕ Add User", type="primary", use_container_width=True):
                    if new_username and new_email:
                        st.success(f"✅ User {new_username} added successfully!")
                        st.session_state['first_user_added'] = True
                        if send_welcome:
                            st.info("📧 Welcome email sent!")
                    else:
                        st.error("Please fill in all required fields.")
            
            with col_cancel:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.info("User creation cancelled.")
    
    with user_tabs[1]:
        st.markdown("**Current Users**")
        
        # User list with actions
        users_data = [
            {"username": "admin", "email": "admin@safesteps.local", "role": "admin", "status": "active", "last_login": "Today"},
            {"username": "john.doe", "email": "john@company.com", "role": "user", "status": "active", "last_login": "Yesterday"},
            {"username": "jane.smith", "email": "jane@company.com", "role": "user", "status": "inactive", "last_login": "1 week ago"}
        ]
        
        for user in users_data:
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 2])
                
                with col1:
                    role_icon = "👑" if user['role'] == 'admin' else "👤"
                    st.markdown(f"**{role_icon} {user['username']}**")
                    st.caption(user['email'])
                
                with col2:
                    st.text(f"Role: {user['role'].title()}")
                    st.caption(f"Last login: {user['last_login']}")
                
                with col3:
                    if user['status'] == 'active':
                        st.success("🟢 Active")
                    else:
                        st.error("🔴 Inactive")
                
                with col4:
                    if user['username'] != 'admin':  # Don't allow editing admin user
                        if st.button("✏️ Edit", key=f"edit_user_{user['username']}"):
                            st.session_state[f'edit_user_{user["username"]}'] = True
                
                with col5:
                    if user['username'] != 'admin':  # Don't allow deleting admin user
                        action_label = "🔓 Activate" if user['status'] == 'inactive' else "🔒 Deactivate"
                        if st.button(action_label, key=f"toggle_user_{user['username']}"):
                            new_status = "active" if user['status'] == 'inactive' else "inactive"
                            st.success(f"User {user['username']} {new_status}!")
    
    with user_tabs[2]:
        st.markdown("**Permission Settings**")
        
        # Permission explanations
        with st.container(border=True):
            st.markdown("**👑 Admin Permissions:**")
            permissions = [
                "✅ Generate certificates",
                "✅ Manage all users",
                "✅ Create and edit templates",
                "✅ View all analytics",
                "✅ System administration",
                "✅ Export all data"
            ]
            
            for perm in permissions:
                st.markdown(perm)
        
        with st.container(border=True):
            st.markdown("**👤 User Permissions:**")
            permissions = [
                "✅ Generate certificates",
                "❌ Manage other users",
                "❌ Create templates (can use existing)",
                "✅ View own analytics",
                "❌ System administration",
                "✅ Export own data"
            ]
            
            for perm in permissions:
                if "❌" in perm:
                    st.markdown(f":gray[{perm}]")
                else:
                    st.markdown(perm)

def render_quick_actions_panel():
    """Render quick actions panel with helpful shortcuts"""
    st.subheader("⚡ Quick Actions")
    create_help_tooltip(
        "These shortcuts help you perform common tasks quickly. Click any action to get started."
    )
    
    # Quick action buttons with descriptions
    actions = [
        {"label": "🏆 Generate Certificates", "desc": "Start the certificate creation process", "key": "quick_generate"},
        {"label": "👤 Add User", "desc": "Invite a new team member", "key": "quick_add_user"},
        {"label": "📄 Upload Template", "desc": "Add a new certificate design", "key": "quick_template"},
        {"label": "📊 View Reports", "desc": "See usage and analytics", "key": "quick_reports"},
        {"label": "💾 Backup Data", "desc": "Create a system backup", "key": "quick_backup"},
        {"label": "⚙️ System Settings", "desc": "Configure SafeSteps", "key": "quick_settings"}
    ]
    
    for action in actions:
        with st.container(border=True):
            if st.button(action["label"], key=action["key"], use_container_width=True):
                st.success(f"Starting: {action['desc']}")
            st.caption(action["desc"])

def render_recent_activity_guided():
    """Render recent activity with explanations"""
    st.subheader("📝 Recent Activity")
    create_help_tooltip(
        "This shows the latest actions in your SafeSteps system. Helps you track what's happening."
    )
    
    activities = [
        {"time": "5 minutes ago", "user": "john.doe", "action": "generated 25 certificates", "icon": "🏆", "type": "success"},
        {"time": "15 minutes ago", "user": "You", "action": "added new user jane.smith", "icon": "👤", "type": "info"},
        {"time": "1 hour ago", "user": "jane.smith", "action": "logged in for the first time", "icon": "🔐", "type": "info"},
        {"time": "2 hours ago", "user": "System", "action": "completed automatic backup", "icon": "💾", "type": "success"},
        {"time": "3 hours ago", "user": "john.doe", "action": "uploaded new template", "icon": "📄", "type": "info"}
    ]
    
    for activity in activities:
        with st.container():
            col1, col2, col3 = st.columns([0.5, 2.5, 1])
            
            with col1:
                st.markdown(activity["icon"])
            
            with col2:
                user_display = "**You**" if activity['user'] == 'You' else f"**{activity['user']}**"
                st.markdown(f"{user_display} {activity['action']}")
            
            with col3:
                st.caption(activity["time"])
            
            st.divider()

def render_help_sidebar():
    """Render contextual help in sidebar"""
    with st.sidebar:
        st.subheader("🎓 Need Help?")
        
        # Context-sensitive help
        current_section = st.session_state.get('current_help_context', 'dashboard')
        
        help_content = {
            'dashboard': {
                'title': '📊 Dashboard Help',
                'content': '''
                **Dashboard Overview:**
                Your main control center for SafeSteps.
                
                **Key Sections:**
                - Metrics: See your current stats
                - Certificate Management: Create certificates
                - User Management: Manage team access
                - Quick Actions: Common shortcuts
                '''
            },
            'certificates': {
                'title': '🏆 Certificate Help',
                'content': '''
                **Certificate Generation:**
                
                1. Upload student data (CSV/Excel)
                2. Choose a template design
                3. Review and generate
                4. Download or email results
                
                **File Requirements:**
                - Must have 'name' column
                - Must have 'email' column
                - CSV or Excel format only
                '''
            }
        }
        
        current_help = help_content.get(current_section, help_content['dashboard'])
        
        with st.container(border=True):
            st.markdown(f"**{current_help['title']}**")
            st.markdown(current_help['content'])
        
        st.divider()
        
        # Help actions
        if st.button("📚 Complete Guide", use_container_width=True):
            st.session_state['show_complete_guide'] = True
        
        if st.button("💬 Contact Support", use_container_width=True):
            st.session_state['show_contact_support'] = True
        
        if st.button("🔄 Restart Tutorial", use_container_width=True):
            # Reset welcome tutorial
            st.session_state['tutorial_welcome_tutorial'] = {
                'current_step': 1,
                'completed_steps': [],
                'skipped': False,
                'started_at': datetime.now().isoformat(),
                'completed_at': None
            }
            st.success("Tutorial restarted!")
            st.rerun()

def render_help_center():
    """Render comprehensive help center modal"""
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.subheader("❓ SafeSteps Help Center")
            
            help_tabs = st.tabs(["📚 Guides", "❓ FAQ", "🎥 Tutorials", "📞 Support"])
            
            with help_tabs[0]:
                st.markdown("**Step-by-Step Guides:**")
                
                guides = [
                    "🏆 How to Generate Your First Certificate",
                    "👥 Managing Users and Permissions",
                    "📄 Creating Custom Templates",
                    "📊 Understanding Analytics",
                    "💾 Backing Up Your Data",
                    "⚙️ System Configuration"
                ]
                
                for guide in guides:
                    if st.button(guide, use_container_width=True):
                        st.info(f"Opening: {guide}")
            
            with help_tabs[1]:
                st.markdown("**Frequently Asked Questions:**")
                
                faqs = [
                    {"q": "What file formats can I upload?", "a": "SafeSteps accepts CSV and Excel (.xlsx) files with student data."},
                    {"q": "How many certificates can I generate at once?", "a": "There's no limit! You can generate certificates for thousands of students in one batch."},
                    {"q": "Can I customize the certificate design?", "a": "Yes! You can upload custom templates or modify existing ones."},
                    {"q": "Are certificates secure?", "a": "Yes, all certificates include unique verification codes and digital signatures."}
                ]
                
                for faq in faqs:
                    with st.expander(faq["q"]):
                        st.markdown(faq["a"])
            
            with help_tabs[2]:
                st.markdown("**Video Tutorials:**")
                
                tutorials = [
                    "🎬 SafeSteps Overview (5 min)",
                    "🎬 Generating Your First Certificate (3 min)",
                    "🎬 Managing Users (4 min)",
                    "🎬 Custom Templates (6 min)",
                    "🎬 Advanced Features (8 min)"
                ]
                
                for tutorial in tutorials:
                    if st.button(tutorial, use_container_width=True):
                        st.info(f"Playing: {tutorial}")
            
            with help_tabs[3]:
                st.markdown("**Get Support:**")
                
                with st.form("support_request"):
                    support_type = st.selectbox(
                        "Type of Issue",
                        ["General Question", "Technical Problem", "Feature Request", "Bug Report"]
                    )
                    
                    support_message = st.text_area(
                        "Describe your issue",
                        placeholder="Please provide as much detail as possible..."
                    )
                    
                    support_email = st.text_input(
                        "Your Email",
                        placeholder="your.email@company.com"
                    )
                    
                    if st.form_submit_button("📧 Send Support Request", type="primary"):
                        if support_message and support_email:
                            st.success("✅ Support request sent! We'll respond within 24 hours.")
                        else:
                            st.error("Please fill in all fields.")
            
            if st.button("Close Help Center", type="primary", use_container_width=True):
                st.session_state['show_help_center'] = False
                st.rerun()

# Main entry point
if __name__ == "__main__":
    render_dashboard_v2()