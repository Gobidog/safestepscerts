"""
SafeSteps V1 - Streamlined Efficiency Dashboard
Single-page admin dashboard with collapsible sections for power users
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Any
import time

from utils.auth import requires_admin, get_current_user
from utils.ui_components import (
    create_collapsible_section, create_bulk_action_toolbar, 
    create_quick_search, create_real_time_metric, create_card_grid,
    create_sortable_table, COLORS
)
from utils.ui_helpers import (
    manage_navigation_state, update_navigation, create_version_selector,
    get_user_preference, update_user_preference
)
from utils.keyboard_shortcuts import (
    create_shortcut_display, create_shortcuts_modal, handle_keyboard_input,
    keyboard_manager, register_page_shortcuts
)
from utils.storage import StorageManager
from utils.course_manager import CourseManager

# Initialize managers
storage = StorageManager()
course_manager = CourseManager(storage.local_path / "metadata")

@requires_admin
def render_efficiency_dashboard():
    """Render the streamlined efficiency dashboard for power users"""
    
    # Handle keyboard shortcuts
    handle_keyboard_input()
    
    # Register page-specific shortcuts
    page_shortcuts = {
        'ctrl+q': {
            'action': 'quick_search_focus',
            'description': 'Focus Quick Search',
            'callback': lambda: st.session_state.update({'focus_quick_search': True})
        },
        'ctrl+b': {
            'action': 'bulk_actions',
            'description': 'Toggle Bulk Actions',
            'callback': lambda: st.session_state.update({'show_bulk_actions': not st.session_state.get('show_bulk_actions', False)})
        }
    }
    register_page_shortcuts(page_shortcuts)
    
    # Header with real-time info
    current_user = get_current_user()
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("⚡ Efficiency Dashboard")
        st.caption(f"Welcome back, {current_user.get('username', 'Admin')} | Last login: {datetime.now().strftime('%H:%M:%S')}")
    
    with col2:
        # Real-time clock
        clock_placeholder = st.empty()
        clock_placeholder.metric("Current Time", datetime.now().strftime('%H:%M:%S'))
    
    with col3:
        # Quick actions
        if st.button("🔄 Refresh All", use_container_width=True):
            st.rerun()
    
    # Keyboard shortcuts display
    create_shortcuts_modal()
    
    # Quick search and filters
    st.divider()
    search_term, category = create_quick_search(
        "Search across all data...",
        ["Certificates", "Users", "Templates", "Courses"]
    )
    
    # Real-time metrics row
    st.subheader("📊 Live Dashboard Metrics")
    metrics_cols = st.columns(4)
    
    # Generate realistic metrics
    current_time = datetime.now()
    certificates_today = 47 + (current_time.minute % 10)  # Simulated real-time data
    active_users = 12 + (current_time.second % 5)
    system_load = min(95, 65 + (current_time.second % 30))
    
    with metrics_cols[0]:
        create_real_time_metric(
            "Certificates Today", 
            certificates_today,
            "up" if certificates_today > 45 else "normal",
            "🏆"
        )
    
    with metrics_cols[1]:
        create_real_time_metric(
            "Active Users", 
            active_users,
            "up" if active_users > 10 else "normal",
            "👥"
        )
    
    with metrics_cols[2]:
        create_real_time_metric(
            "System Health", 
            f"{system_load}%",
            "up" if system_load > 90 else "normal",
            "💚"
        )
    
    with metrics_cols[3]:
        storage_used = 2.3  # GB
        create_real_time_metric(
            "Storage Used", 
            f"{storage_used:.1f} GB",
            "normal",
            "💾"
        )
    
    st.divider()
    
    # Main dashboard sections (collapsible)
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        # Certificate Generation Section
        with st.expander("🏆 Certificate Generation Hub", expanded=True):
            render_certificate_hub()
        
        # User Management Section
        with st.expander("👥 User Management Console", expanded=False):
            render_user_management_console()
        
        # Template Management Section
        with st.expander("📄 Template & Course Manager", expanded=False):
            render_template_course_manager()
    
    with col_right:
        # Analytics & Reports Section
        with st.expander("📈 Analytics Dashboard", expanded=True):
            render_analytics_panel()
        
        # System Administration
        with st.expander("⚙️ System Administration", expanded=False):
            render_system_admin_panel()
        
        # Recent Activity Feed
        with st.expander("📝 Activity Feed", expanded=True):
            render_activity_feed()
    
    # Bulk actions toolbar (if items selected)
    if st.session_state.get('selected_items', []):
        st.divider()
        bulk_actions = [
            {'key': 'export', 'label': 'Export Selected', 'icon': '📤', 'type': 'secondary', 'callback': lambda: bulk_export()},
            {'key': 'delete', 'label': 'Delete Selected', 'icon': '🗑️', 'type': 'secondary', 'callback': lambda: bulk_delete()},
            {'key': 'archive', 'label': 'Archive Selected', 'icon': '📦', 'type': 'secondary', 'callback': lambda: bulk_archive()}
        ]
        create_bulk_action_toolbar(bulk_actions, len(st.session_state.get('selected_items', [])))
    
    # Footer with shortcuts hint
    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("💡 Tip: Use `Ctrl+Shift+K` to view all keyboard shortcuts")
    with col2:
        create_shortcut_display()

def render_certificate_hub():
    """Render certificate generation hub with express mode"""
    tab1, tab2, tab3 = st.tabs(["🚀 Express Mode", "📊 Batch Status", "🎯 Quick Generate"])
    
    with tab1:
        st.markdown("**Express Certificate Generation - All Steps in One View**")
        
        # Express mode: All 5 steps visible
        cols = st.columns(5)
        
        with cols[0]:
            st.markdown("**1. Upload**")
            uploaded_file = st.file_uploader(
                "Data File",
                type=['csv', 'xlsx'],
                key="express_upload",
                label_visibility="collapsed"
            )
            if uploaded_file:
                st.success("✅ File ready")
        
        with cols[1]:
            st.markdown("**2. Validate**")
            if uploaded_file:
                if st.button("🔍 Validate", key="express_validate", use_container_width=True):
                    st.success("✅ Valid data")
                    st.session_state['express_validated'] = True
            else:
                st.button("🔍 Validate", disabled=True, use_container_width=True)
        
        with cols[2]:
            st.markdown("**3. Template**")
            if st.session_state.get('express_validated'):
                template = st.selectbox(
                    "Template",
                    ["Digital Citizenship", "Safety Training", "Compliance Course"],
                    key="express_template",
                    label_visibility="collapsed"
                )
                st.success("✅ Template set")
            else:
                st.selectbox("Template", ["Select template..."], disabled=True, label_visibility="collapsed")
        
        with cols[3]:
            st.markdown("**4. Generate**")
            if st.session_state.get('express_validated') and 'express_template' in st.session_state:
                if st.button("🏆 Generate", key="express_generate", use_container_width=True, type="primary"):
                    # Simulate generation with progress
                    progress_bar = st.progress(0)
                    for i in range(100):
                        progress_bar.progress(i + 1)
                        time.sleep(0.01)
                    st.success("✅ Generated!")
                    st.session_state['express_generated'] = True
            else:
                st.button("🏆 Generate", disabled=True, use_container_width=True)
        
        with cols[4]:
            st.markdown("**5. Download**")
            if st.session_state.get('express_generated'):
                st.download_button(
                    "📥 Download",
                    data="dummy certificate data",
                    file_name="certificates.zip",
                    mime="application/zip",
                    use_container_width=True
                )
            else:
                st.button("📥 Download", disabled=True, use_container_width=True)
    
    with tab2:
        # Batch status table
        batch_data = [
            {"id": "BATCH001", "status": "Completed", "count": 25, "created": "2024-01-15 09:30"},
            {"id": "BATCH002", "status": "Processing", "count": 42, "created": "2024-01-15 10:15"},
            {"id": "BATCH003", "status": "Failed", "count": 18, "created": "2024-01-15 11:00"}
        ]
        
        create_sortable_table(
            batch_data,
            [
                {"key": "id", "label": "Batch ID", "width": 1},
                {"key": "status", "label": "Status", "width": 1},
                {"key": "count", "label": "Certificates", "width": 1},
                {"key": "created", "label": "Created", "width": 2}
            ],
            "batch_table"
        )
    
    with tab3:
        st.markdown("**Quick Generate - Templates & Courses**")
        
        # Quick generation options
        quick_col1, quick_col2 = st.columns(2)
        
        with quick_col1:
            st.markdown("**Predefined Templates**")
            templates = ["Digital Citizenship", "Safety Training", "Compliance Course"]
            for template in templates:
                if st.button(f"🚀 Generate {template}", key=f"quick_{template}", use_container_width=True):
                    st.success(f"Generating {template} certificates...")
        
        with quick_col2:
            st.markdown("**Recent Courses**")
            courses = course_manager.list_courses()[:3]  # Get first 3 courses
            for course in courses:
                if st.button(f"📚 Use {course.name}", key=f"course_{course.id}", use_container_width=True):
                    st.success(f"Loading {course.name} template...")

def render_user_management_console():
    """Render user management console with bulk operations"""
    
    # Quick user actions
    action_cols = st.columns(4)
    with action_cols[0]:
        if st.button("➕ Add User", use_container_width=True):
            st.session_state['show_add_user'] = True
    with action_cols[1]:
        if st.button("📤 Export Users", use_container_width=True):
            st.success("Exporting user list...")
    with action_cols[2]:
        if st.button("🔄 Sync LDAP", use_container_width=True):
            st.success("LDAP sync initiated...")
    with action_cols[3]:
        if st.button("📊 User Report", use_container_width=True):
            st.success("Generating user report...")
    
    # User statistics
    user_stats_cols = st.columns(3)
    with user_stats_cols[0]:
        st.metric("Total Users", "156")
    with user_stats_cols[1]:
        st.metric("Active Users", "142")
    with user_stats_cols[2]:
        st.metric("Admin Users", "8")
    
    # User management table with selection
    st.markdown("**User Management**")
    
    # Sample user data
    users_data = [
        {"username": "john.doe", "email": "john@company.com", "role": "user", "status": "active", "last_login": "2024-01-15"},
        {"username": "jane.admin", "email": "jane@company.com", "role": "admin", "status": "active", "last_login": "2024-01-15"},
        {"username": "bob.user", "email": "bob@company.com", "role": "user", "status": "inactive", "last_login": "2024-01-10"}
    ]
    
    # Selection checkboxes
    selected_users = []
    for idx, user in enumerate(users_data):
        col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 2, 1, 1, 1])
        
        with col1:
            if st.checkbox("", key=f"user_select_{idx}"):
                selected_users.append(user['username'])
        
        with col2:
            st.text(user['username'])
        with col3:
            st.text(user['email'])
        with col4:
            st.text(user['role'])
        with col5:
            status_color = "🟢" if user['status'] == 'active' else "🔴"
            st.text(f"{status_color} {user['status']}")
        with col6:
            st.text(user['last_login'])
    
    # Store selected users for bulk actions
    if selected_users:
        st.session_state['selected_items'] = selected_users

def render_template_course_manager():
    """Render template and course management"""
    
    tab1, tab2 = st.tabs(["📄 Templates", "📚 Courses"])
    
    with tab1:
        # Template management
        template_cols = st.columns(3)
        with template_cols[0]:
            if st.button("➕ Upload Template", use_container_width=True):
                st.success("Template upload initiated...")
        with template_cols[1]:
            if st.button("🎨 Template Builder", use_container_width=True):
                st.success("Opening template builder...")
        with template_cols[2]:
            if st.button("📋 Template Library", use_container_width=True):
                st.success("Opening template library...")
        
        # Template list
        templates = [
            {"name": "Digital Citizenship", "uses": 245, "created": "2024-01-10"},
            {"name": "Safety Training", "uses": 156, "created": "2024-01-12"},
            {"name": "Compliance Course", "uses": 89, "created": "2024-01-14"}
        ]
        
        for template in templates:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.markdown(f"**{template['name']}**")
                with col2:
                    st.text(f"Uses: {template['uses']}")
                with col3:
                    st.text(template['created'])
                with col4:
                    if st.button("✏️ Edit", key=f"edit_template_{template['name']}"):
                        st.success(f"Editing {template['name']}...")
    
    with tab2:
        # Course management
        course_cols = st.columns(2)
        with course_cols[0]:
            if st.button("➕ Create Course", use_container_width=True):
                st.success("Course creation initiated...")
        with course_cols[1]:
            if st.button("📊 Course Analytics", use_container_width=True):
                st.success("Loading course analytics...")
        
        # Course list
        courses = course_manager.list_courses()
        if courses:
            for course in courses[:5]:  # Show first 5 courses
                with st.container(border=True):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.markdown(f"**{course.name}**")
                        st.caption(course.description)
                    with col2:
                        st.text(f"Uses: {course.usage_count}")
                    with col3:
                        if st.button("🚀 Use", key=f"use_course_{course.id}"):
                            st.success(f"Using {course.name}...")
        else:
            st.info("No courses available. Create your first course!")

def render_analytics_panel():
    """Render analytics dashboard panel"""
    
    # Analytics tabs
    tab1, tab2, tab3 = st.tabs(["📈 Usage", "👥 Users", "🏆 Certs"])
    
    with tab1:
        # Usage analytics
        st.markdown("**System Usage Trends**")
        
        # Generate sample data for charts
        dates = pd.date_range(start='2024-01-01', periods=14, freq='D')
        usage_data = pd.DataFrame({
            'Date': dates,
            'Certificates': [23, 34, 45, 32, 56, 67, 78, 54, 43, 65, 76, 87, 65, 89],
            'Users': [12, 15, 18, 14, 22, 25, 28, 21, 19, 24, 27, 31, 26, 33]
        })
        
        st.line_chart(usage_data.set_index('Date'))
    
    with tab2:
        # User analytics
        st.markdown("**User Activity**")
        
        # User metrics
        metric_cols = st.columns(2)
        with metric_cols[0]:
            st.metric("Daily Active Users", "47", delta="+5")
        with metric_cols[1]:
            st.metric("New Users (Week)", "12", delta="+3")
        
        # User role distribution
        role_data = pd.DataFrame({
            'Role': ['Admin', 'User', 'Guest'],
            'Count': [8, 142, 6]
        })
        st.bar_chart(role_data.set_index('Role'))
    
    with tab3:
        # Certificate analytics
        st.markdown("**Certificate Generation**")
        
        # Certificate metrics
        cert_cols = st.columns(2)
        with cert_cols[0]:
            st.metric("Today", "47", delta="+12")
        with cert_cols[1]:
            st.metric("This Week", "284", delta="+45")
        
        # Most popular templates
        template_data = pd.DataFrame({
            'Template': ['Digital Citizenship', 'Safety Training', 'Compliance'],
            'Generated': [156, 89, 67]
        })
        st.bar_chart(template_data.set_index('Template'))

def render_system_admin_panel():
    """Render system administration panel"""
    
    # System status indicators
    status_cols = st.columns(3)
    with status_cols[0]:
        st.success("🟢 System Online")
    with status_cols[1]:
        st.info("🔵 Backup Running")
    with status_cols[2]:
        st.warning("🟡 Updates Available")
    
    # Quick admin actions
    admin_cols = st.columns(2)
    with admin_cols[0]:
        if st.button("🔄 Restart Services", use_container_width=True):
            st.success("Services restarting...")
        if st.button("🧹 Clear Cache", use_container_width=True):
            st.success("Cache cleared!")
    
    with admin_cols[1]:
        if st.button("💾 Backup Now", use_container_width=True):
            st.success("Backup initiated...")
        if st.button("📊 System Report", use_container_width=True):
            st.success("Generating system report...")

def render_activity_feed():
    """Render recent activity feed"""
    
    activities = [
        {"time": "2 min ago", "user": "john.doe", "action": "Generated 25 certificates", "icon": "🏆"},
        {"time": "5 min ago", "user": "jane.admin", "action": "Created new user account", "icon": "👤"},
        {"time": "8 min ago", "user": "bob.user", "action": "Uploaded new template", "icon": "📄"},
        {"time": "15 min ago", "user": "system", "action": "Automated backup completed", "icon": "💾"},
        {"time": "23 min ago", "user": "alice.admin", "action": "Updated course content", "icon": "📚"}
    ]
    
    for activity in activities:
        with st.container():
            col1, col2, col3 = st.columns([0.5, 2, 1])
            with col1:
                st.markdown(activity["icon"])
            with col2:
                st.markdown(f"**{activity['user']}** {activity['action']}")
            with col3:
                st.caption(activity["time"])
            st.divider()

# Bulk action functions
def bulk_export():
    """Handle bulk export action"""
    selected = st.session_state.get('selected_items', [])
    st.success(f"Exporting {len(selected)} items...")

def bulk_delete():
    """Handle bulk delete action"""
    selected = st.session_state.get('selected_items', [])
    st.warning(f"Deleting {len(selected)} items...")
    # Clear selection after action
    st.session_state['selected_items'] = []

def bulk_archive():
    """Handle bulk archive action"""
    selected = st.session_state.get('selected_items', [])
    st.info(f"Archiving {len(selected)} items...")
    # Clear selection after action
    st.session_state['selected_items'] = []

# Main entry point
if __name__ == "__main__":
    render_dashboard_v1()