"""
UI Components and Design System for SafeSteps
Centralized UI components for consistent design and better user experience
"""
import streamlit as st
from typing import Optional, List, Dict, Tuple
import json

# SafeSteps Brand Colors
COLORS = {
    'primary': '#032A51',      # Navy Blue
    'accent': '#9ACA3C',       # Green
    'success': '#52C41A',      # Success Green
    'warning': '#FAAD14',      # Warning Orange
    'error': '#F5222D',        # Error Red
    'info': '#1890FF',         # Info Blue
    'background': '#F5F7FA',   # Light Gray
    'border': '#E1E8ED',       # Border Gray
    'text_primary': '#2D3748', # Dark Text
    'text_secondary': '#718096' # Secondary Text
}

# Typography Scale
TYPOGRAPHY = {
    'h1': {'size': '32px', 'weight': '700', 'line_height': '1.2'},
    'h2': {'size': '24px', 'weight': '600', 'line_height': '1.3'},
    'h3': {'size': '20px', 'weight': '600', 'line_height': '1.4'},
    'body': {'size': '16px', 'weight': '400', 'line_height': '1.6'},
    'caption': {'size': '14px', 'weight': '400', 'line_height': '1.5'},
    'small': {'size': '12px', 'weight': '400', 'line_height': '1.5'}
}

def apply_custom_css():
    """Apply basic Streamlit theming without HTML injection"""
    # PHASE 1 EMERGENCY TRIAGE: COMPLETE
    # All theming is now handled by native Streamlit components
    # No HTML injection, no CSS injection, fully secure
    # Using native Streamlit theming through config.toml only
    pass

def create_header(title: str, subtitle: Optional[str] = None, user_info: Optional[Dict] = None):
    """Create a consistent header component using native components"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.title(title)
        if subtitle:
            st.markdown(subtitle)
    
    with col2:
        if user_info:
            st.markdown(f"**{user_info.get('username', 'User')}**")
            st.caption(user_info.get('role', 'user').upper())

def create_card(content: str, title: Optional[str] = None, icon: Optional[str] = None):
    """Create a card component using native containers"""
    with st.container(border=True):
        if title:
            title_text = f"{icon} {title}" if icon else title
            st.subheader(title_text)
        
        st.markdown(content)

def create_metric_card(label: str, value: str, icon: str, color: str = 'primary'):
    """Create an enhanced metric card using native components"""
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"# {icon}")
            st.metric(label=label, value=value)

def create_status_badge(status: str, type: str = 'default'):
    """Create a status badge using native Streamlit components"""
    # Map status types to native Streamlit status indicators
    status_icons = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
        'default': '📋'
    }
    
    icon = status_icons.get(type, status_icons['default'])
    badge_text = f"{icon} {status}"
    
    # Use native Streamlit status components
    if type == 'success':
        st.success(badge_text, icon="✅")
    elif type == 'warning':
        st.warning(badge_text, icon="⚠️")
    elif type == 'error':
        st.error(badge_text, icon="❌")
    elif type == 'info':
        st.info(badge_text, icon="ℹ️")
    else:
        st.markdown(f"**{badge_text}**")
    
    return badge_text  # Return text for compatibility

def create_progress_steps(steps: List[Tuple[str, str, int]], current_step: int):
    """Create an enhanced progress indicator using native Streamlit components"""
    cols = st.columns(len(steps))
    
    for idx, (label, icon, step_num) in enumerate(steps):
        with cols[idx]:
            # Determine status
            if step_num < current_step:
                status = 'completed'
                status_icon = '✓'
                status_text = 'Completed'
            elif step_num == current_step:
                status = 'active'
                status_icon = str(step_num)
                status_text = 'Current'
            else:
                status = 'pending'
                status_icon = str(step_num)
                status_text = 'Pending'
            
            # Create step using native Streamlit components
            with st.container():
                # Center content using columns
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(icon)  # No HTML, just the emoji/icon
                
                # Status indicator
                if status == 'completed':
                    st.success(f"{status_icon} {label}")
                elif status == 'active':
                    st.info(f"{status_icon} {label}")
                else:
                    st.markdown(f"{status_icon} {label}")

def create_loading_animation(text: str = "Loading..."):
    """Create a custom loading animation using native components"""
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Use Streamlit's built-in spinner
            with st.spinner(text):
                import time
                time.sleep(0.1)  # Brief pause to show spinner

def show_toast(message: str, type: str = 'info', duration: int = 3):
    """Show a toast notification using native components"""
    icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    
    toast_message = f"{icons.get(type, '📢')} {message}"
    
    # Use native Streamlit notification components
    if type == 'success':
        st.success(toast_message)
    elif type == 'error':
        st.error(toast_message)
    elif type == 'warning':
        st.warning(toast_message)
    else:
        st.info(toast_message)

def create_empty_state(
    icon: str, 
    title: str, 
    description: str, 
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
):
    """Create an empty state component using native components"""
    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"# {icon}")
            st.subheader(title)
            st.markdown(description)
            
            if action_label and action_callback:
                if st.button(action_label, type="primary", use_container_width=True):
                    action_callback()

def create_breadcrumb(items: List[Dict[str, str]]):
    """Create a breadcrumb navigation using native components"""
    breadcrumb_parts = []
    for idx, item in enumerate(items):
        if idx > 0:
            breadcrumb_parts.append(" › ")
        breadcrumb_parts.append(item['label'])
    
    breadcrumb_text = "".join(breadcrumb_parts)
    st.markdown(f"**Navigation:** {breadcrumb_text}")

def create_search_bar(placeholder: str = "Search...", key: str = "search"):
    """Create a styled search bar using native components"""
    return st.text_input(
        label="🔍 Search",
        placeholder=placeholder,
        key=key,
        help="Search for items..."
    )

def create_table_header(columns: List[Dict[str, str]]):
    """Create a styled table header using native components"""
    cols = st.columns([col.get('width', 1) for col in columns])
    
    for idx, col in enumerate(columns):
        with cols[idx]:
            # Use native Streamlit subheader for table headers
            st.subheader(col['label'].upper(), divider=True)

def create_action_menu(actions: List[Dict[str, any]], key_prefix: str):
    """Create an action menu with icons"""
    cols = st.columns(len(actions))
    
    for idx, action in enumerate(actions):
        with cols[idx]:
            if st.button(
                f"{action.get('icon', '')} {action['label']}",
                key=f"{key_prefix}_{action['key']}",
                use_container_width=True,
                type=action.get('type', 'secondary')
            ):
                if 'callback' in action:
                    action['callback']()

def create_course_card(course: Dict[str, any], on_edit: callable = None, on_delete: callable = None):
    """Create a course card component using native Streamlit components"""
    with st.container(border=True):
        # Course title
        st.subheader(course['name'])
        
        # Course description
        st.markdown(course['description'])
        
        # Course statistics using columns for layout
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"📊 {course.get('usage_count', 0)} uses")
        with col2:
            st.caption(f"👤 Created by {course.get('created_by', 'Unknown')}")
    
    # Action buttons
    if on_edit or on_delete:
        col1, col2 = st.columns(2)
        with col1:
            if on_edit and st.button("✏️ Edit", key=f"edit_course_{course['id']}", use_container_width=True):
                on_edit(course)
        with col2:
            if on_delete:
                # Only allow deletion of unused courses
                if course.get('usage_count', 0) == 0:
                    if st.button("🗑️ Delete", key=f"delete_course_{course['id']}", use_container_width=True):
                        on_delete(course)
                else:
                    st.button("🔒 In Use", key=f"locked_course_{course['id']}", disabled=True, use_container_width=True)

def create_course_form(course: Dict[str, any] = None, on_submit: callable = None, on_cancel: callable = None):
    """Create a course form component for add/edit"""
    is_edit = course is not None
    
    with st.form("course_form"):
        course_name = st.text_input(
            "Course Name",
            value=course['name'] if is_edit else "",
            placeholder="e.g., Digital Citizenship",
            help="Enter a descriptive name for the course"
        )
        
        course_description = st.text_area(
            "Course Description",
            value=course['description'] if is_edit else "",
            placeholder="Describe what this course covers and when it should be used...",
            help="Provide a clear description to help users understand the course content",
            height=100
        )
        
        col_submit, col_cancel = st.columns(2)
        with col_submit:
            submit_label = "💾 Save Changes" if is_edit else "💾 Create Course"
            if st.form_submit_button(submit_label, type="primary", use_container_width=True):
                if on_submit:
                    on_submit(course_name, course_description)
        
        with col_cancel:
            if st.form_submit_button("Cancel", use_container_width=True):
                if on_cancel:
                    on_cancel()

def create_course_stats_card(stats: Dict[str, any]):
    """Create a statistics card for courses using native components"""
    with st.container(border=True):
        st.subheader("📊 Course Statistics")
        
        # Create metrics using native Streamlit columns and metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Courses", stats.get('total_courses', 0))
            st.metric("Active Courses", stats.get('courses_with_usage', 0))
        
        with col2:
            st.metric("Total Usage", stats.get('total_usage', 0))
            st.metric("Unused Courses", stats.get('courses_without_usage', 0))
        
        # Show most used course if available
        if stats.get('most_used_course'):
            st.divider()
            st.markdown(f"**Most Used:** {stats['most_used_course']['name']} ({stats['most_used_course']['usage_count']} uses)")