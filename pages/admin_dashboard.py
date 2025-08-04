"""
SafeSteps Admin Dashboard - Consolidated Experience
Implements WORK | MANAGE | MONITOR task-oriented architecture with enhanced UX

Features:
- Task-oriented navigation replacing 8-page admin structure
- Prominent action buttons with 44px+ touch targets
- Bulk operations with selection interfaces
- Admin shortcuts and power user features
- Mobile-first responsive design
- WCAG 2.2 AA compliance
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
import json
from datetime import datetime, timedelta
import pandas as pd

# Enhanced UI Components
from utils.ui_components import (
    apply_custom_css, create_prominent_button, create_enhanced_button_group,
    create_card_grid, create_bulk_action_toolbar, create_quick_search,
    create_real_time_metric, create_sortable_table, create_mobile_nav,
    create_empty_state, show_toast, create_action_menu, create_theme_toggle,
    create_collapsible_section, create_progress_ring, create_status_badge
)

# Navigation System
from navigation_system import (
    NavigationManager, render_task_oriented_navigation, 
    get_current_navigation
)

# Business Logic (mock implementations for demo)
def mock_certificate_data():
    """Mock certificate data for demonstration"""
    return [
        {
            'id': 'cert_001', 
            'student_name': 'Alice Johnson',
            'course': 'Digital Citizenship',
            'date_issued': '2025-01-15',
            'status': 'completed',
            'score': 85
        },
        {
            'id': 'cert_002',
            'student_name': 'Bob Smith', 
            'course': 'Cyber Safety',
            'date_issued': '2025-01-14',
            'status': 'completed',
            'score': 92
        },
        {
            'id': 'cert_003',
            'student_name': 'Carol Davis',
            'course': 'Online Ethics',
            'date_issued': '2025-01-13', 
            'status': 'pending',
            'score': None
        }
    ]

def mock_analytics_data():
    """Mock analytics data"""
    return {
        'total_certificates': 1247,
        'certificates_this_month': 89,
        'active_courses': 12,
        'registered_users': 156,
        'completion_rate': 87.5,
        'avg_score': 84.2,
        'system_uptime': 99.8,
        'storage_used': 2.4  # GB
    }

def mock_system_health():
    """Mock system health data"""
    return {
        'status': 'healthy',
        'cpu_usage': 34,
        'memory_usage': 58,
        'disk_usage': 23,
        'response_time': 142,  # ms
        'last_backup': '2025-01-15 03:00:00',
        'ssl_expires': '2025-06-15'
    }

class AdminDashboard:
    """Main Admin Dashboard Controller"""
    
    def __init__(self):
        self.nav_manager = NavigationManager()
        
        # Initialize session state for admin features
        if 'admin_selections' not in st.session_state:
            st.session_state.admin_selections = {}
        if 'admin_search' not in st.session_state:
            st.session_state.admin_search = {}
        if 'admin_settings' not in st.session_state:
            st.session_state.admin_settings = {
                'shortcuts_enabled': True,
                'notifications_enabled': True,
                'auto_refresh': False
            }
    
    def render_keyboard_shortcuts_panel(self):
        """Render admin keyboard shortcuts panel"""
        with st.sidebar:
            with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
                st.markdown("""
                ### Navigation
                - **Ctrl + 1** → WORK area
                - **Ctrl + 2** → MANAGE area  
                - **Ctrl + 3** → MONITOR area
                - **Ctrl + Tab** → Next tab
                
                ### Quick Actions
                - **Ctrl + G** → Generate Certificate
                - **Ctrl + B** → Batch Operations
                - **Ctrl + K** → Global Search  
                - **Ctrl + S** → Save/Export
                
                ### Bulk Operations
                - **Ctrl + A** → Select All
                - **Shift + Click** → Range Select
                - **Ctrl + D** → Bulk Delete
                - **Ctrl + E** → Bulk Edit
                """)
    
    def render_admin_command_palette(self):
        """Render admin command palette for power users"""
        if st.session_state.get('show_command_palette', False):
            with st.container():
                st.markdown("### 🎯 Admin Command Palette")
                
                command = st.text_input(
                    "Type command...",
                    placeholder="generate, search, export, users, analytics...",
                    key="admin_command",
                    help="Type commands for instant access to admin functions"
                )
                
                if command:
                    # Simple command routing
                    if 'generate' in command.lower():
                        st.success("🚀 Navigate to Certificate Generation")
                        if st.button("Go to Generate", type="primary"):
                            self.nav_manager.navigate_to('work', 'generate')
                            st.rerun()
                    
                    elif 'search' in command.lower():
                        st.success("🔍 Global Search Mode Activated")
                    
                    elif 'export' in command.lower():
                        st.success("📊 Export Data Options")
                    
                    elif 'users' in command.lower():
                        st.success("👤 Navigate to User Management") 
                        if st.button("Go to Users", type="primary"):
                            self.nav_manager.navigate_to('manage', 'users')
                            st.rerun()

    def render_work_area_content(self, tab: str):
        """Render WORK area content with all certificate generation & management"""
        
        if tab == 'generate':
            self.render_certificate_generation()
        elif tab == 'batch':
            self.render_batch_operations()
        elif tab == 'manage':
            self.render_certificate_management()
        elif tab == 'results':
            self.render_student_results()
    
    def render_certificate_generation(self):
        """Enhanced certificate generation interface"""
        st.markdown("## 🚀 Certificate Generation")
        
        # Quick generation section with prominent buttons
        st.markdown("### Express Generation")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if create_prominent_button(
                "🚀 Generate Single Certificate",
                "generate_single",
                button_type="primary",
                size="large",
                help_text="Generate a single certificate quickly"
            ):
                st.success("🎉 Single certificate generation started!")
                show_toast("Certificate generation in progress...", "info")
        
        with col2:
            if create_prominent_button(
                "⚡ Quick Batch (CSV)",
                "quick_batch",
                button_type="secondary", 
                size="large",
                help_text="Upload CSV for bulk generation"
            ):
                st.info("📤 Upload your CSV file for batch processing")
        
        with col3:
            if create_prominent_button(
                "🎨 Template Preview",
                "preview_template",
                button_type="secondary",
                size="medium",
                help_text="Preview certificate templates"
            ):
                st.info("🔍 Template preview coming soon")
        
        st.divider()
        
        # Detailed generation form
        st.markdown("### Certificate Details")
        
        with st.form("certificate_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                student_name = st.text_input(
                    "Student Name *",
                    placeholder="Enter student full name",
                    help="Student name as it should appear on certificate"
                )
                
                course_name = st.selectbox(
                    "Course *",
                    ["Digital Citizenship", "Cyber Safety", "Online Ethics", "Data Privacy"],
                    help="Select the course for this certificate"
                )
                
                completion_date = st.date_input(
                    "Completion Date",
                    value=datetime.now().date(),
                    help="Date when student completed the course"
                )
            
            with col2:
                score = st.number_input(
                    "Score",
                    min_value=0,
                    max_value=100,
                    value=85,
                    help="Student's score (0-100)"
                )
                
                template = st.selectbox(
                    "Certificate Template",
                    ["Standard Template", "Premium Template", "Custom Template"],
                    help="Choose certificate design template"
                )
                
                instructor = st.text_input(
                    "Instructor",
                    placeholder="Instructor name (optional)",
                    help="Name of course instructor"
                )
            
            # Form submission buttons
            st.markdown("### Actions")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.form_submit_button("🎯 Generate & Download", type="primary", use_container_width=True):
                    if student_name and course_name:
                        st.success(f"✅ Certificate generated for {student_name}!")
                        st.balloons()
                    else:
                        st.error("❌ Please fill in required fields")
            
            with col2:
                if st.form_submit_button("👁️ Preview First", use_container_width=True):
                    st.info("🔍 Generating preview...")
            
            with col3:
                if st.form_submit_button("💾 Save Draft", use_container_width=True):
                    st.success("💾 Draft saved!")
            
            with col4:
                if st.form_submit_button("🔄 Reset Form", use_container_width=True):
                    st.info("🔄 Form reset!")
    
    def render_batch_operations(self):
        """Enhanced batch operations with progress tracking"""
        st.markdown("## 📚 Batch Certificate Operations")
        
        # Bulk action buttons
        bulk_actions = [
            {'key': 'upload', 'text': 'Upload CSV', 'type': 'primary', 'icon': '📤'},
            {'key': 'template', 'text': 'Download Template', 'type': 'secondary', 'icon': '📋'},
            {'key': 'validate', 'text': 'Validate Data', 'type': 'secondary', 'icon': '✅'},
            {'key': 'process', 'text': 'Process Batch', 'type': 'success', 'icon': '⚡'}
        ]
        
        results = create_enhanced_button_group(bulk_actions, "batch", "horizontal")
        
        # Handle button clicks
        if results.get('batch_upload'):
            st.success("📤 CSV Upload Ready")
            
            uploaded_file = st.file_uploader(
                "Choose CSV file",
                type=['csv'],
                help="Upload CSV with student data for bulk certificate generation"
            )
            
            if uploaded_file:
                # Mock file processing
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ File uploaded: {len(df)} records found")
                st.dataframe(df.head(), use_container_width=True)
        
        if results.get('batch_template'):
            st.info("📋 CSV Template Download")
            
            # Create sample CSV template
            template_data = {
                'student_name': ['John Doe', 'Jane Smith'],
                'course': ['Digital Citizenship', 'Cyber Safety'],
                'completion_date': ['2025-01-15', '2025-01-14'],
                'score': [85, 92],
                'instructor': ['Ms. Johnson', 'Mr. Wilson']
            }
            
            template_df = pd.DataFrame(template_data)
            
            st.download_button(
                "⬇️ Download CSV Template",
                template_df.to_csv(index=False),
                file_name="certificate_batch_template.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.divider()
        
        # Batch processing status
        st.markdown("### 📊 Batch Processing Status")
        
        # Mock batch jobs
        batch_jobs = [
            {'id': 'batch_001', 'name': 'January Graduates', 'status': 'completed', 'progress': 100, 'count': 45},
            {'id': 'batch_002', 'name': 'Makeup Certificates', 'status': 'processing', 'progress': 67, 'count': 12},
            {'id': 'batch_003', 'name': 'New Student Batch', 'status': 'pending', 'progress': 0, 'count': 28}
        ]
        
        for job in batch_jobs:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.markdown(f"**{job['name']}**")
                    st.caption(f"ID: {job['id']} • {job['count']} certificates")
                
                with col2:
                    create_status_badge(job['status'].title(), 
                                      'success' if job['status'] == 'completed' 
                                      else 'warning' if job['status'] == 'processing' 
                                      else 'info')
                
                with col3:
                    if job['progress'] > 0:
                        st.progress(job['progress'] / 100, f"{job['progress']}%")
                    else:
                        st.text("Not started")
                
                with col4:
                    if st.button("📋", key=f"details_{job['id']}", help="View details"):
                        st.info(f"Details for {job['name']}")
    
    def render_certificate_management(self):
        """Certificate search, edit, and management interface"""
        st.markdown("## 📋 Certificate Management")
        
        # Search and filter interface
        search_term, category = create_quick_search(
            "Search certificates...",
            ["All Courses", "Digital Citizenship", "Cyber Safety", "Online Ethics"]
        )
        
        # Action buttons for selected certificates
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if create_prominent_button("🔍 Advanced Search", "advanced_search", size="medium"):
                st.session_state['show_advanced_search'] = True
        
        with col2:
            if create_prominent_button("📊 Export Selected", "export_certs", size="medium"):
                st.success("📊 Export functionality ready")
        
        with col3:
            if create_prominent_button("✏️ Bulk Edit", "bulk_edit", size="medium"):
                st.info("✏️ Bulk edit mode activated")
        
        with col4:
            if create_prominent_button("🗑️ Bulk Delete", "bulk_delete", button_type="danger", size="medium"):
                st.warning("🗑️ Bulk delete requires confirmation")
        
        # Advanced search panel
        if st.session_state.get('show_advanced_search', False):
            with st.expander("🔍 Advanced Search Options", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    date_range = st.date_input(
                        "Date Range",
                        value=(datetime.now().date() - timedelta(days=30), datetime.now().date()),
                        help="Filter by certificate issue date"
                    )
                
                with col2:
                    score_range = st.slider(
                        "Score Range",
                        min_value=0,
                        max_value=100,
                        value=(70, 100),
                        help="Filter by student scores"
                    )
                
                with col3:
                    status_filter = st.multiselect(
                        "Status",
                        ["completed", "pending", "draft", "expired"],
                        default=["completed", "pending"]
                    )
        
        st.divider()
        
        # Certificates table with selection
        st.markdown("### Certificate Records")
        
        certificates = mock_certificate_data()
        
        # Bulk selection interface
        select_all = st.checkbox("Select All", key="select_all_certs")
        
        selected_certs = []
        
        for idx, cert in enumerate(certificates):
            with st.container(border=True):
                col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 2, 1.5, 1, 1.5])
                
                with col1:
                    is_selected = st.checkbox("", key=f"cert_select_{idx}", value=select_all)
                    if is_selected:
                        selected_certs.append(cert['id'])
                
                with col2:
                    st.markdown(f"**{cert['student_name']}**")
                    st.caption(f"ID: {cert['id']}")
                
                with col3:
                    st.text(cert['course'])
                    st.caption(cert['date_issued'])
                
                with col4:
                    create_status_badge(cert['status'].title(), 
                                      'success' if cert['status'] == 'completed' else 'warning')
                
                with col5:
                    if cert['score']:
                        st.metric("Score", f"{cert['score']}%")
                    else:
                        st.text("Pending")
                
                with col6:
                    cert_actions = [
                        {'key': 'view', 'label': '👁️ View', 'type': 'secondary'},
                        {'key': 'edit', 'label': '✏️ Edit', 'type': 'secondary'},
                        {'key': 'download', 'label': '⬇️ Download', 'type': 'secondary'}
                    ]
                    
                    action_col1, action_col2, action_col3 = st.columns(3)
                    with action_col1:
                        if st.button("👁️", key=f"view_{idx}", help="View certificate"):
                            st.info(f"Viewing certificate for {cert['student_name']}")
                    with action_col2:
                        if st.button("✏️", key=f"edit_{idx}", help="Edit certificate"):
                            st.info(f"Editing certificate for {cert['student_name']}")
                    with action_col3:
                        if st.button("⬇️", key=f"download_{idx}", help="Download certificate"):
                            st.success(f"Downloading certificate for {cert['student_name']}")
        
        # Bulk actions toolbar
        if selected_certs:
            create_bulk_action_toolbar([
                {'key': 'export', 'label': 'Export Selected', 'type': 'primary', 'icon': '📊'},
                {'key': 'edit', 'label': 'Bulk Edit', 'type': 'secondary', 'icon': '✏️'},
                {'key': 'delete', 'label': 'Delete Selected', 'type': 'danger', 'icon': '🗑️'}
            ], len(selected_certs))
    
    def render_student_results(self):
        """Student records and results management"""
        st.markdown("## 👥 Student Results Management")
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_real_time_metric("Total Students", "1,247", "up", "👥")
        with col2:
            create_real_time_metric("Avg Score", "84.2%", "up", "📊")
        with col3:
            create_real_time_metric("Completion Rate", "87.5%", "up", "✅")
        with col4:
            create_real_time_metric("This Month", "+89", "up", "📈")
        
        st.divider()
        
        # Student management actions
        actions = [
            {'key': 'add', 'text': 'Add Student', 'type': 'primary', 'icon': '👤'},
            {'key': 'import', 'text': 'Import Students', 'type': 'secondary', 'icon': '📤'},
            {'key': 'export', 'text': 'Export Results', 'type': 'secondary', 'icon': '📊'},
            {'key': 'reports', 'text': 'Generate Reports', 'type': 'secondary', 'icon': '📋'}
        ]
        
        results = create_enhanced_button_group(actions, "student", "horizontal")
        
        if results.get('student_add'):
            st.success("👤 Add Student Form")
            with st.form("add_student"):
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Student Name", placeholder="Full name")
                    st.text_input("Email", placeholder="student@example.com")
                with col2:
                    st.selectbox("Course", ["Digital Citizenship", "Cyber Safety"])
                    st.date_input("Enrollment Date")
                
                if st.form_submit_button("Add Student", type="primary"):
                    st.success("✅ Student added successfully!")
    
    def render_manage_area_content(self, tab: str):
        """Render MANAGE area content for system configuration"""
        
        if tab == 'templates':
            self.render_template_management()
        elif tab == 'courses':
            self.render_course_management()
        elif tab == 'users':
            self.render_user_management()
        elif tab == 'content':
            self.render_content_management()
    
    def render_template_management(self):
        """Certificate template design and management"""
        st.markdown("## 🎨 Template Management")
        
        # Template actions
        actions = [
            {'key': 'create', 'text': 'Create Template', 'type': 'primary', 'icon': '🎨'},
            {'key': 'upload', 'text': 'Upload Template', 'type': 'secondary', 'icon': '📤'},
            {'key': 'gallery', 'text': 'Template Gallery', 'type': 'secondary', 'icon': '🖼️'},
            {'key': 'preview', 'text': 'Preview All', 'type': 'secondary', 'icon': '👁️'}
        ]
        
        results = create_enhanced_button_group(actions, "template", "horizontal")
        
        # Template gallery
        templates = [
            {
                'icon': '📜',
                'title': 'Standard Certificate',
                'content': 'Clean, professional design suitable for all courses',
                'action': {'label': 'Use Template', 'type': 'primary'}
            },
            {
                'icon': '🏆',
                'title': 'Premium Certificate', 
                'content': 'Enhanced design with gold accents and borders',
                'action': {'label': 'Use Template', 'type': 'primary'}
            },
            {
                'icon': '🎯',
                'title': 'Custom Certificate',
                'content': 'Fully customizable template with brand elements',
                'action': {'label': 'Customize', 'type': 'secondary'}
            }
        ]
        
        create_card_grid(templates, columns=3)
        
        if results.get('template_create'):
            st.success("🎨 Template Creation Wizard")
            # Template creation interface would go here
    
    def render_course_management(self):
        """Course configuration and content management"""
        st.markdown("## 📖 Course Management")
        
        # Course stats and actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_real_time_metric("Active Courses", "12", "up", "📚")
        with col2:
            create_real_time_metric("Total Enrollments", "1,247", "up", "👥")
        with col3:
            create_real_time_metric("Avg Completion", "87.5%", "up", "✅")
        with col4:
            create_real_time_metric("New This Month", "3", "up", "📈")
        
        # Course management actions
        st.divider()
        
        actions = [
            {'key': 'create', 'text': 'Create Course', 'type': 'primary', 'icon': '📖'},
            {'key': 'import', 'text': 'Import Content', 'type': 'secondary', 'icon': '📤'},
            {'key': 'analytics', 'text': 'Course Analytics', 'type': 'secondary', 'icon': '📊'},
            {'key': 'settings', 'text': 'Course Settings', 'type': 'secondary', 'icon': '⚙️'}
        ]
        
        results = create_enhanced_button_group(actions, "course", "horizontal")
        
        if results.get('course_create'):
            st.success("📖 Course Creation Form")
            # Course creation form would go here
    
    def render_user_management(self):
        """User accounts and permissions management"""
        st.markdown("## 👤 User Management")
        
        # User stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_real_time_metric("Total Users", "156", "up", "👥")
        with col2:
            create_real_time_metric("Active This Month", "89", "up", "🟢")
        with col3:
            create_real_time_metric("Administrators", "5", "normal", "👑")
        with col4:
            create_real_time_metric("New Registrations", "12", "up", "🆕")
        
        # User management actions
        st.divider()
        
        actions = [
            {'key': 'add', 'text': 'Add User', 'type': 'primary', 'icon': '👤'},
            {'key': 'import', 'text': 'Bulk Import', 'type': 'secondary', 'icon': '📤'},
            {'key': 'permissions', 'text': 'Manage Permissions', 'type': 'secondary', 'icon': '🔒'},
            {'key': 'export', 'text': 'Export Users', 'type': 'secondary', 'icon': '📊'}
        ]
        
        results = create_enhanced_button_group(actions, "user", "horizontal")
        
        if results.get('user_add'):
            st.success("👤 Add User Form")
            # User creation form would go here
    
    def render_content_management(self):
        """Media files and educational resources"""
        st.markdown("## 📁 Content Management")
        
        # Content stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_real_time_metric("Total Files", "2,456", "up", "📁")
        with col2:
            create_real_time_metric("Storage Used", "2.4 GB", "up", "💾")
        with col3:
            create_real_time_metric("Videos", "89", "up", "🎥")
        with col4:
            create_real_time_metric("Documents", "145", "up", "📄")
        
        # Content management actions
        st.divider()
        
        actions = [
            {'key': 'upload', 'text': 'Upload Files', 'type': 'primary', 'icon': '📤'},
            {'key': 'organize', 'text': 'Organize Library', 'type': 'secondary', 'icon': '📂'},
            {'key': 'compress', 'text': 'Optimize Storage', 'type': 'secondary', 'icon': '⚡'},
            {'key': 'backup', 'text': 'Backup Content', 'type': 'secondary', 'icon': '💾'}
        ]
        
        results = create_enhanced_button_group(actions, "content", "horizontal")
        
        if results.get('content_upload'):
            st.success("📤 File Upload Interface")
            # File upload interface would go here
    
    def render_monitor_area_content(self, tab: str):
        """Render MONITOR area content for analytics and system health"""
        
        if tab == 'analytics':
            self.render_analytics_dashboard()
        elif tab == 'settings':
            self.render_system_settings()
        elif tab == 'health':
            self.render_system_health()
        elif tab == 'security':
            self.render_security_compliance()
    
    def render_analytics_dashboard(self):
        """Usage metrics and performance analytics"""
        st.markdown("## 📈 Analytics Dashboard")
        
        analytics = mock_analytics_data()
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_real_time_metric("Total Certificates", f"{analytics['total_certificates']:,}", "up", "📋")
        with col2:
            create_real_time_metric("This Month", f"+{analytics['certificates_this_month']}", "up", "📈")
        with col3:
            create_real_time_metric("Completion Rate", f"{analytics['completion_rate']}%", "up", "✅")
        with col4:
            create_real_time_metric("Avg Score", f"{analytics['avg_score']}%", "up", "🎯")
        
        st.divider()
        
        # Analytics actions
        actions = [
            {'key': 'export', 'text': 'Export Report', 'type': 'primary', 'icon': '📊'},
            {'key': 'schedule', 'text': 'Schedule Reports', 'type': 'secondary', 'icon': '📅'},
            {'key': 'custom', 'text': 'Custom Analytics', 'type': 'secondary', 'icon': '🎛️'},
            {'key': 'insights', 'text': 'AI Insights', 'type': 'secondary', 'icon': '🤖'}
        ]
        
        results = create_enhanced_button_group(actions, "analytics", "horizontal")
        
        # Charts and visualizations (mock)
        st.markdown("### 📊 Usage Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Certificate Generation")
            # Mock chart data
            chart_data = pd.DataFrame({
                'Date': pd.date_range('2025-01-01', periods=30),
                'Certificates': [15, 23, 18, 31, 29, 42, 35, 28, 33, 41, 
                               38, 45, 42, 39, 44, 48, 51, 46, 52, 55,
                               49, 58, 61, 54, 63, 59, 66, 62, 69, 71]
            })
            st.line_chart(chart_data.set_index('Date'))
        
        with col2:
            st.markdown("#### Course Popularity")
            course_data = pd.DataFrame({
                'Course': ['Digital Citizenship', 'Cyber Safety', 'Online Ethics', 'Data Privacy'],
                'Certificates': [342, 298, 267, 340]
            })
            st.bar_chart(course_data.set_index('Course'))
    
    def render_system_settings(self):
        """System configuration and preferences"""
        st.markdown("## ⚙️ System Settings")
        
        # Settings sections
        tabs = st.tabs(["🔧 General", "🎨 Appearance", "📧 Notifications", "🔌 Integrations"])
        
        with tabs[0]:  # General
            st.markdown("### General Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                site_name = st.text_input("Site Name", value="SafeSteps")
                admin_email = st.text_input("Admin Email", value="admin@safesteps.com")
                max_file_size = st.number_input("Max File Size (MB)", value=10)
            
            with col2:
                backup_frequency = st.selectbox("Backup Frequency", ["Daily", "Weekly", "Monthly"])
                auto_cleanup = st.checkbox("Auto Cleanup Old Files", value=True)
                maintenance_mode = st.checkbox("Maintenance Mode", value=False)
        
        with tabs[1]:  # Appearance
            st.markdown("### Appearance Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                theme = st.selectbox("Default Theme", ["Light", "Dark", "Auto"])
                primary_color = st.color_picker("Primary Color", value="#032A51")
                logo_upload = st.file_uploader("Upload Logo", type=['png', 'jpg', 'svg'])
            
            with col2:
                font_size = st.slider("Base Font Size", 12, 20, 16)
                show_animations = st.checkbox("Enable Animations", value=True)
                compact_mode = st.checkbox("Compact Mode", value=False)
        
        with tabs[2]:  # Notifications
            st.markdown("### Notification Settings")
            
            email_notifications = st.checkbox("Email Notifications", value=True)
            if email_notifications:
                st.multiselect("Email Events", [
                    "New User Registration",
                    "Certificate Generated", 
                    "System Errors",
                    "Daily Reports"
                ], default=["System Errors"])
        
        with tabs[3]:  # Integrations
            st.markdown("### Integration Settings")
            
            st.info("🔌 Configure external service integrations")
            
            # Mock integration settings
            integrations = [
                {"name": "Google Workspace", "status": "connected", "icon": "🔗"},
                {"name": "Microsoft Teams", "status": "disconnected", "icon": "❌"},
                {"name": "Slack Notifications", "status": "connected", "icon": "🔗"},
                {"name": "Zoom Integration", "status": "pending", "icon": "⏳"}
            ]
            
            for integration in integrations:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.text(f"{integration['icon']} {integration['name']}")
                with col2:
                    create_status_badge(integration['status'].title(), 
                                      'success' if integration['status'] == 'connected' 
                                      else 'warning' if integration['status'] == 'pending'
                                      else 'error')
                with col3:
                    st.button("Configure", key=f"config_{integration['name']}")
        
        # Save settings
        st.divider()
        if create_prominent_button("💾 Save All Settings", "save_settings", button_type="primary"):
            st.success("✅ Settings saved successfully!")
    
    def render_system_health(self):
        """System performance and diagnostics"""
        st.markdown("## ❤️ System Health Monitor")
        
        health = mock_system_health()
        
        # Overall system status
        status_color = "success" if health['status'] == 'healthy' else "error"
        create_status_badge(f"System Status: {health['status'].title()}", status_color)
        
        st.divider()
        
        # Health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_progress_ring(health['cpu_usage'], "CPU Usage", "primary")
        with col2:
            create_progress_ring(health['memory_usage'], "Memory Usage", "warning")
        with col3:
            create_progress_ring(health['disk_usage'], "Disk Usage", "success")
        with col4:
            create_real_time_metric("Response Time", f"{health['response_time']}ms", "normal", "⚡")
        
        st.divider()
        
        # System actions
        actions = [
            {'key': 'refresh', 'text': 'Refresh Status', 'type': 'primary', 'icon': '🔄'},
            {'key': 'diagnostics', 'text': 'Run Diagnostics', 'type': 'secondary', 'icon': '🔍'},
            {'key': 'cleanup', 'text': 'System Cleanup', 'type': 'secondary', 'icon': '🧹'},
            {'key': 'backup', 'text': 'Backup Now', 'type': 'secondary', 'icon': '💾'}
        ]
        
        results = create_enhanced_button_group(actions, "health", "horizontal")
        
        if results.get('health_diagnostics'):
            st.success("🔍 Running system diagnostics...")
            # Diagnostic results would appear here
        
        # Recent events
        st.markdown("### 📋 Recent System Events")
        
        events = [
            {"time": "2025-01-15 14:30", "event": "Automatic backup completed", "type": "success"},
            {"time": "2025-01-15 12:15", "event": "SSL certificate renewed", "type": "info"},
            {"time": "2025-01-15 09:00", "event": "System restart completed", "type": "warning"},
            {"time": "2025-01-14 23:45", "event": "Scheduled maintenance completed", "type": "success"}
        ]
        
        for event in events:
            col1, col2, col3 = st.columns([1, 3, 1])
            with col1:
                st.caption(event["time"])
            with col2:
                st.text(event["event"])
            with col3:
                create_status_badge("", event["type"])
    
    def render_security_compliance(self):
        """Security logs and compliance monitoring"""
        st.markdown("## 🔒 Security & Compliance")
        
        # Security overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_real_time_metric("Security Score", "98%", "up", "🛡️")
        with col2:
            create_real_time_metric("Failed Logins", "3", "down", "🚫")
        with col3:
            create_real_time_metric("Active Sessions", "42", "normal", "👥")
        with col4:
            create_real_time_metric("SSL Status", "Valid", "up", "🔐")
        
        st.divider()
        
        # Security actions
        actions = [
            {'key': 'scan', 'text': 'Security Scan', 'type': 'primary', 'icon': '🔍'},
            {'key': 'logs', 'text': 'View Logs', 'type': 'secondary', 'icon': '📋'},
            {'key': 'backup', 'text': 'Emergency Backup', 'type': 'secondary', 'icon': '💾'},
            {'key': 'lockdown', 'text': 'Lockdown Mode', 'type': 'danger', 'icon': '🔒'}
        ]
        
        results = create_enhanced_button_group(actions, "security", "horizontal")
        
        if results.get('security_scan'):
            st.success("🔍 Security scan initiated...")
        
        # Compliance checklist
        st.markdown("### ✅ Compliance Checklist")
        
        compliance_items = [
            {"item": "Data encryption at rest", "status": "compliant", "priority": "high"},
            {"item": "Regular security audits", "status": "compliant", "priority": "high"},
            {"item": "User access controls", "status": "compliant", "priority": "medium"},
            {"item": "Backup procedures", "status": "warning", "priority": "high"},
            {"item": "Privacy policy updated", "status": "compliant", "priority": "low"}
        ]
        
        for item in compliance_items:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(item["item"])
            with col2:
                status_type = "success" if item["status"] == "compliant" else "warning"
                create_status_badge(item["status"].title(), status_type)
            with col3:
                priority_color = "error" if item["priority"] == "high" else "warning" if item["priority"] == "medium" else "info"
                create_status_badge(item["priority"].title(), priority_color)
    
    def render_main_dashboard(self):
        """Main dashboard rendering method"""
        
        # Apply enhanced CSS
        apply_custom_css()
        
        # Page configuration
        st.set_page_config(
            page_title="SafeSteps Admin Dashboard",
            page_icon="🛡️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Header with admin context
        st.markdown("# 🛡️ SafeSteps Admin Dashboard")
        st.markdown("**Consolidated Admin Experience** • Task-Oriented Design • Mobile-First")
        
        # Render navigation and get current location
        current_area, current_tab = render_task_oriented_navigation()
        
        # Admin-specific sidebar features
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👑 Admin Tools")
            
            # Quick stats
            if st.button("📊 Quick Stats", use_container_width=True):
                st.session_state['show_quick_stats'] = not st.session_state.get('show_quick_stats', False)
            
            if st.session_state.get('show_quick_stats', False):
                analytics = mock_analytics_data()
                st.metric("Certificates", f"{analytics['total_certificates']:,}")
                st.metric("Users", f"{analytics['registered_users']}")
                st.metric("Uptime", f"{analytics['system_uptime']}%")
            
            # Command palette toggle
            if st.button("🎯 Command Palette", use_container_width=True):
                st.session_state['show_command_palette'] = not st.session_state.get('show_command_palette', False)
            
            # Theme toggle
            create_theme_toggle()
        
        # Render keyboard shortcuts panel
        self.render_keyboard_shortcuts_panel()
        
        # Render command palette if enabled
        if st.session_state.get('show_command_palette', False):
            self.render_admin_command_palette()
        
        # Route content based on navigation
        st.markdown("---")
        
        if current_area == 'work':
            self.render_work_area_content(current_tab)
        elif current_area == 'manage':
            self.render_manage_area_content(current_tab)
        elif current_area == 'monitor':
            self.render_monitor_area_content(current_tab)
        
        # Footer with admin info
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.caption("🛡️ SafeSteps Admin Dashboard v2.0 • Task-Oriented Design")
        with col2:
            st.caption(f"Current: {current_area.upper()} → {current_tab.title()}")
        with col3:
            st.caption(f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

def main():
    """Main application entry point"""
    admin_dashboard = AdminDashboard()
    admin_dashboard.render_main_dashboard()

if __name__ == "__main__":
    main()