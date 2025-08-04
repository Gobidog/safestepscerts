"""
UI Components and Design System for SafeSteps
Centralized UI components for consistent design and better user experience
"""
import streamlit as st
from typing import Optional, List, Dict, Tuple, Any
import json

# SafeSteps Enhanced Brand Colors - WCAG 2.2 AA Compliant
COLORS = {
    # Primary Brand Colors
    'primary': '#032A51',      # Navy Blue (21:1 contrast on white)
    'primary_light': '#1E4A72', # Lighter Navy (7:1 contrast)
    'primary_dark': '#021D37',  # Darker Navy (for hover states)
    
    # Secondary Colors
    'accent': '#7BA428',       # Accessible Green (4.5:1 contrast)
    'accent_light': '#9ACA3C', # Original Green (for backgrounds)
    'accent_dark': '#5D7A1E',  # Dark Green (for active states)
    
    # Semantic Colors - All WCAG 2.2 AA Compliant
    'success': '#16A34A',      # Success Green (4.5:1 contrast)
    'success_bg': '#DCFCE7',   # Success Background
    'warning': '#CA8A04',      # Warning Orange (4.5:1 contrast) 
    'warning_bg': '#FEF3C7',   # Warning Background
    'error': '#DC2626',        # Error Red (4.8:1 contrast)
    'error_bg': '#FEE2E2',     # Error Background
    'info': '#2563EB',         # Info Blue (4.5:1 contrast)
    'info_bg': '#DBEAFE',      # Info Background
    
    # Neutral Colors
    'background': '#FFFFFF',   # Pure White
    'surface': '#F8FAFC',      # Light Surface
    'border': '#CBD5E1',       # Border Gray (3:1 contrast)
    'border_focus': '#3B82F6', # Focus Border Blue
    
    # Text Colors - High contrast for accessibility
    'text_primary': '#0F172A',   # Near Black (16:1 contrast)
    'text_secondary': '#475569', # Dark Gray (7.5:1 contrast)
    'text_muted': '#64748B',     # Medium Gray (4.8:1 contrast)
    'text_inverse': '#FFFFFF',   # White text for dark backgrounds
    
    # Interactive States
    'hover_overlay': 'rgba(0, 0, 0, 0.05)',
    'active_overlay': 'rgba(0, 0, 0, 0.1)',
    'disabled_bg': '#F1F5F9',
    'disabled_text': '#94A3B8',
    
    # Mobile Touch Targets
    'touch_target_min': '44px',  # WCAG 2.2 minimum touch target
    'button_primary_min': '48px', # Large primary buttons
    'button_secondary_min': '44px' # Standard secondary buttons
}

# Enhanced Typography Scale - Mobile-First Design
TYPOGRAPHY = {
    # Mobile-first sizes (base)
    'display': {'size': '2.5rem', 'weight': '800', 'line_height': '1.1'},  # 40px
    'h1': {'size': '2rem', 'weight': '700', 'line_height': '1.2'},        # 32px
    'h2': {'size': '1.5rem', 'weight': '600', 'line_height': '1.3'},      # 24px 
    'h3': {'size': '1.25rem', 'weight': '600', 'line_height': '1.4'},     # 20px
    'h4': {'size': '1.125rem', 'weight': '600', 'line_height': '1.4'},    # 18px
    'body_large': {'size': '1.125rem', 'weight': '400', 'line_height': '1.6'}, # 18px
    'body': {'size': '1rem', 'weight': '400', 'line_height': '1.6'},       # 16px
    'body_small': {'size': '0.875rem', 'weight': '400', 'line_height': '1.5'}, # 14px
    'caption': {'size': '0.75rem', 'weight': '400', 'line_height': '1.5'}, # 12px
    
    # Button Typography
    'button_large': {'size': '1.125rem', 'weight': '600', 'line_height': '1.2'}, # 18px
    'button_medium': {'size': '1rem', 'weight': '600', 'line_height': '1.2'},    # 16px  
    'button_small': {'size': '0.875rem', 'weight': '500', 'line_height': '1.2'}, # 14px
    
    # Responsive breakpoints for larger screens
    'desktop_scale': 1.125,  # 12.5% larger on desktop
    'tablet_scale': 1.0625   # 6.25% larger on tablet
}

# Spacing System - 8px grid for consistent spacing
SPACING = {
    'xs': '0.25rem',   # 4px
    'sm': '0.5rem',    # 8px  
    'md': '1rem',      # 16px
    'lg': '1.5rem',    # 24px
    'xl': '2rem',      # 32px
    '2xl': '3rem',     # 48px
    '3xl': '4rem',     # 64px
    '4xl': '6rem',     # 96px
}

# Responsive Breakpoints
BREAKPOINTS = {
    'mobile': '320px',   # Small mobile
    'mobile_lg': '480px', # Large mobile
    'tablet': '768px',   # Tablet
    'desktop': '1024px', # Desktop
    'desktop_lg': '1280px' # Large desktop
}

def apply_custom_css():
    """Apply enhanced UI theming using safe CSS injection"""
    # Enhanced theming for better button visibility and accessibility
    # All CSS is safe and doesn't use HTML injection for interactive elements
    st.markdown("""
    <style>
    /* Enhanced Button System - WCAG 2.2 Compliant */
    .stButton > button {
        min-height: 48px !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: 2px solid transparent !important;
        transition: all 0.2s ease !important;
        font-size: 16px !important;
    }
    
    /* Primary Button - Large and Prominent */
    .stButton > button[kind="primary"] {
        background-color: #032A51 !important;
        color: white !important;
        min-height: 52px !important;
        font-size: 18px !important;
        box-shadow: 0 4px 6px rgba(3, 42, 81, 0.25) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #021D37 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(3, 42, 81, 0.35) !important;
    }
    
    .stButton > button[kind="primary"]:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 4px rgba(3, 42, 81, 0.25) !important;
    }
    
    /* Secondary Button - Accessible and Clear */
    .stButton > button[kind="secondary"] {
        background-color: white !important;
        color: #032A51 !important;
        border: 2px solid #032A51 !important;
        min-height: 48px !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #F8FAFC !important;
        border-color: #021D37 !important;
        color: #021D37 !important;
    }
    
    /* Success Button */
    .stButton.success > button {
        background-color: #16A34A !important;
        color: white !important;
        border-color: #16A34A !important;
    }
    
    .stButton.success > button:hover {
        background-color: #15803D !important;
    }
    
    /* Warning Button */
    .stButton.warning > button {
        background-color: #CA8A04 !important;
        color: white !important;
        border-color: #CA8A04 !important;
    }
    
    .stButton.warning > button:hover {
        background-color: #A16207 !important;
    }
    
    /* Error/Danger Button */
    .stButton.danger > button {
        background-color: #DC2626 !important;
        color: white !important;
        border-color: #DC2626 !important;
    }
    
    .stButton.danger > button:hover {
        background-color: #B91C1C !important;
    }
    
    /* Large Button Variant */
    .stButton.large > button {
        min-height: 56px !important;
        font-size: 20px !important;
        padding: 16px 32px !important;
    }
    
    /* Small Button Variant (still meets 44px minimum) */
    .stButton.small > button {
        min-height: 44px !important;
        font-size: 14px !important;
        padding: 12px 20px !important;
    }
    
    /* Focus States for Accessibility */
    .stButton > button:focus {
        outline: 3px solid #3B82F6 !important;
        outline-offset: 2px !important;
    }
    
    /* Disabled State */
    .stButton > button:disabled {
        background-color: #F1F5F9 !important;
        color: #94A3B8 !important;
        border-color: #E2E8F0 !important;
        cursor: not-allowed !important;
        box-shadow: none !important;
    }
    
    /* Mobile Optimizations - Enhanced for 44px+ Touch Targets */
    @media (max-width: 768px) {
        .stButton > button {
            min-height: 52px !important;
            font-size: 18px !important;
            padding: 16px 24px !important;
            margin-bottom: 8px !important;
            border-radius: 12px !important;
        }
        
        .stButton.large > button {
            min-height: 60px !important;
            font-size: 22px !important;
        }
        
        /* Ensure proper spacing between interactive elements */
        .element-container {
            margin-bottom: 20px !important;
        }
        
        /* Enhanced touch target compliance */
        .stSelectbox > div > div {
            min-height: 52px !important;
        }
        
        .stTextInput > div > div > input {
            min-height: 52px !important;
            font-size: 18px !important;
        }
        
        /* Card spacing for mobile */
        .stContainer {
            margin-bottom: 16px !important;
        }
        
        /* Mobile-friendly metric cards */
        [data-testid="metric-container"] {
            padding: 12px !important;
            margin-bottom: 12px !important;
        }
    }
    
    /* Tablet optimizations */
    @media (min-width: 769px) and (max-width: 1024px) {
        .stButton > button {
            min-height: 50px !important;
            font-size: 17px !important;
        }
        
        /* Ensure touch targets remain compliant on tablets */
        .stSelectbox > div > div,
        .stTextInput > div > div > input {
            min-height: 48px !important;
        }
    }
    
    /* Enhanced Form Elements */
    .stTextInput > div > div > input {
        min-height: 48px !important;
        font-size: 16px !important;
        border-radius: 8px !important;
    }
    
    .stSelectbox > div > div > div {
        min-height: 48px !important;
        font-size: 16px !important;
    }
    
    /* Container Improvements */
    .element-container {
        margin-bottom: 16px !important;
    }
    
    /* Loading Spinner Enhancement */
    .stSpinner > div {
        border-color: #032A51 !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

# Enhanced Components for V1 - Streamlined Efficiency

def create_collapsible_section(title: str, content_func: callable, expanded: bool = False, key: str = None):
    """Create a collapsible section using native expander"""
    with st.expander(title, expanded=expanded):
        content_func()

def create_bulk_action_toolbar(actions: List[Dict[str, any]], selected_count: int = 0):
    """Create a toolbar for bulk operations"""
    if selected_count > 0:
        st.info(f"📋 {selected_count} items selected")
        cols = st.columns(len(actions))
        for idx, action in enumerate(actions):
            with cols[idx]:
                if st.button(
                    f"{action.get('icon', '')} {action['label']}",
                    key=f"bulk_{action['key']}",
                    type=action.get('type', 'secondary'),
                    use_container_width=True
                ):
                    if 'callback' in action:
                        action['callback']()

def create_quick_search(placeholder: str = "Quick search...", categories: List[str] = None):
    """Create an enhanced search with category filters"""
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input(
            "🔍", 
            placeholder=placeholder,
            label_visibility="collapsed"
        )
    with col2:
        if categories:
            category = st.selectbox(
                "Category",
                ["All"] + categories,
                label_visibility="collapsed"
            )
        else:
            category = "All"
    return search_term, category

def create_real_time_metric(label: str, value: any, trend: str = None, icon: str = "📊"):
    """Create a real-time updating metric card"""
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"## {icon}")
        with col2:
            if trend:
                delta_color = "normal" if trend == "up" else "inverse" if trend == "down" else "off"
                st.metric(label, value, delta=trend, delta_color=delta_color)
            else:
                st.metric(label, value)

# Enhanced Components for V2 - User-Friendly Guidance

def create_tutorial_overlay(step_title: str, step_content: str, step_number: int, total_steps: int):
    """Create a tutorial overlay using native modal dialog"""
    with st.container(border=True):
        st.info(f"📚 Tutorial - Step {step_number} of {total_steps}")
        st.subheader(step_title)
        st.markdown(step_content)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            prev_disabled = step_number <= 1
            prev_button = st.button("⬅️ Previous", disabled=prev_disabled)
        with col2:
            skip_button = st.button("⏭️ Skip Tutorial")
        with col3:
            next_disabled = step_number >= total_steps
            next_label = "✅ Finish" if step_number == total_steps else "➡️ Next"
            next_button = st.button(next_label, disabled=next_disabled)
        
        return {"prev": prev_button, "skip": skip_button, "next": next_button}

def create_help_tooltip(content: str, trigger_text: str = "❓"):
    """Create a help tooltip using expander"""
    with st.expander(trigger_text, expanded=False):
        st.markdown(content)

def create_validation_preview(data: Dict[str, any], validation_rules: List[str]):
    """Create a preview of validation results"""
    with st.container(border=True):
        st.subheader("🔍 Validation Preview")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**Data Summary:**")
            for key, value in data.items():
                st.text(f"{key}: {value}")
        
        with col2:
            st.markdown("**Validation Rules:**")
            for rule in validation_rules:
                st.success(f"✅ {rule}")

def create_save_resume_widget(workflow_state: Dict[str, any]):
    """Create save/resume functionality widget"""
    with st.sidebar:
        st.divider()
        st.subheader("💾 Save Progress")
        
        if st.button("💾 Save Current Progress", use_container_width=True):
            st.session_state['saved_workflow'] = workflow_state.copy()
            st.success("Progress saved!")
        
        if 'saved_workflow' in st.session_state:
            if st.button("📂 Resume Saved Progress", use_container_width=True):
                for key, value in st.session_state['saved_workflow'].items():
                    st.session_state[key] = value
                st.success("Progress resumed!")

# Enhanced Components for V3 - Modern Dashboard

def create_flexible_workflow_selector(user_id: str, user_suggestions: Dict = None):
    """
    Create workflow mode selector with smart suggestions
    """
    st.subheader("🚀 Choose Your Workflow")
    
    # Mode descriptions
    modes = {
        'quick_generate': {
            'name': '⚡ Quick Generate',
            'description': 'One-click certificate generation with smart defaults',
            'features': ['Single page interface', 'Keyboard shortcuts (Ctrl+G)', 'Bulk operations', 'Auto-save every 30s'],
            'best_for': 'Power users who generate certificates regularly',
            'estimated_time': '2-3 minutes'
        },
        'guided_mode': {
            'name': '🧭 Guided Mode', 
            'description': 'Step-by-step guidance with help and validation',
            'features': ['Interactive tutorials', 'Save/resume anywhere', 'Contextual help', 'Preview certificates'],
            'best_for': 'New users or complex certificate setups',
            'estimated_time': '5-8 minutes'
        },
        'advanced_mode': {
            'name': '🎛️ Advanced Mode',
            'description': 'Full control with all customization options',
            'features': ['Complete customization', 'Template editor', 'Bulk operations', 'Advanced settings'],
            'best_for': 'Experienced users needing full control',
            'estimated_time': '8-15 minutes'
        }
    }
    
    # Show smart suggestion if available
    if user_suggestions and 'preferred_mode' in user_suggestions:
        preferred = user_suggestions['preferred_mode'].value
        st.info(f"💡 **Smart Suggestion:** Based on your usage, we recommend **{modes[preferred]['name']}**")
    
    # Create mode selection cards
    cols = st.columns(3)
    selected_mode = None
    
    for idx, (mode_key, mode_info) in enumerate(modes.items()):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"### {mode_info['name']}")
                st.write(mode_info['description'])
                
                st.markdown("**Features:**")
                for feature in mode_info['features']:
                    st.markdown(f"• {feature}")
                
                st.markdown(f"**Best for:** {mode_info['best_for']}")
                st.markdown(f"**Time:** {mode_info['estimated_time']}")
                
                # Highlight suggested mode
                button_type = "primary" if (user_suggestions and 
                                          user_suggestions.get('preferred_mode', {}).value == mode_key) else "secondary"
                
                if st.button(f"Start {mode_info['name']}", 
                           key=f"select_{mode_key}",
                           use_container_width=True,
                           type=button_type):
                    selected_mode = mode_key
    
    return selected_mode

def create_workflow_progress_bar(workflow_progress: Dict):
    """
    Create enhanced workflow progress visualization
    """
    progress = workflow_progress.get('progress_percentage', 0) / 100
    current_step = workflow_progress.get('current_step', 'None')
    completed_steps = workflow_progress.get('completed_steps', 0)
    total_steps = workflow_progress.get('total_steps', 1)
    time_remaining = workflow_progress.get('estimated_time_remaining', 0)
    
    # Progress header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Current Step:** {current_step.replace('_', ' ').title() if current_step else 'Getting Started'}")
    
    with col2:
        st.metric("Progress", f"{completed_steps}/{total_steps}", f"{progress*100:.0f}%")
    
    with col3:
        if time_remaining > 0:
            mins = time_remaining // 60
            secs = time_remaining % 60
            st.metric("Est. Time", f"{mins}m {secs}s")
    
    # Enhanced progress bar
    st.progress(progress, text=f"Progress: {progress*100:.0f}% ({completed_steps}/{total_steps} steps)")
    
    return progress

def create_workflow_step_card(step_id: str, step_info: Dict, workflow_state: Dict, is_current: bool = False):
    """
    Create individual workflow step card with status and actions
    """
    status = workflow_state.get('step_statuses', {}).get(step_id, 'pending')
    
    # Status styling
    status_colors = {
        'pending': ('⏳', '#6B7280', 'Pending'),
        'active': ('🔄', '#3B82F6', 'In Progress'),
        'completed': ('✅', '#10B981', 'Completed'),
        'skipped': ('⏭️', '#8B5CF6', 'Skipped'),
        'error': ('❌', '#EF4444', 'Error')
    }
    
    icon, color, status_text = status_colors.get(status, status_colors['pending'])
    
    # Card styling based on status
    border_style = "border-left: 4px solid " + color + ";"
    if is_current:
        border_style += " box-shadow: 0 4px 8px rgba(59, 130, 246, 0.25);"
    
    with st.container(border=True):
        # Custom CSS for this card
        st.markdown(f"""
        <div style="{border_style} padding: 8px; border-radius: 4px;">
            <h4>{icon} {step_info.get('name', step_id.title())}</h4>
            <p style="color: {color}; font-weight: 600;">{status_text}</p>
            <p style="color: #6B7280;">{step_info.get('description', '')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons based on status
        if status == 'active' and is_current:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"Continue {step_id}", key=f"continue_{step_id}", use_container_width=True, type="primary"):
                    return f"continue_{step_id}"
            
            if not step_info.get('required', True):
                with col2:
                    if st.button(f"Skip {step_id}", key=f"skip_{step_id}", use_container_width=True):
                        return f"skip_{step_id}"
        
        elif status == 'pending' and not is_current:
            # Check if dependencies are met
            if st.button(f"Jump to {step_id}", key=f"jump_{step_id}", use_container_width=True):
                return f"jump_{step_id}"
        
        elif status == 'completed':
            col1, col2 = st.columns(2)
            with col1:
                st.success("Completed ✓")
            with col2:
                if st.button(f"Edit {step_id}", key=f"edit_{step_id}", use_container_width=True):
                    return f"edit_{step_id}"
        
        # Show keyboard shortcut if available
        if step_info.get('keyboard_shortcut'):
            st.caption(f"💡 Shortcut: {step_info['keyboard_shortcut']}")
        
        # Show help text if available
        if step_info.get('help_text'):
            with st.expander("ℹ️ Help", expanded=False):
                st.info(step_info['help_text'])
    
    return None

def create_save_resume_panel(workflow_id: str, auto_save_enabled: bool = True):
    """
    Create save/resume panel with auto-save functionality
    """
    st.subheader("💾 Save & Resume")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save Now", use_container_width=True, type="primary"):
            from utils.workflow_engine import save_workflow_state
            if save_workflow_state(workflow_id):
                st.success("✅ Saved!")
                st.balloons()
            else:
                st.error("❌ Save failed")
    
    with col2:
        auto_save = st.toggle("🔄 Auto-save", value=auto_save_enabled, help="Save progress every 30 seconds")
        if auto_save != auto_save_enabled:
            st.session_state[f'workflow_{workflow_id}_auto_save'] = auto_save
    
    with col3:
        if st.button("📋 Export Progress", use_container_width=True):
            # Export workflow state as JSON
            from utils.workflow_engine import get_workflow_state
            state = get_workflow_state(workflow_id)
            if state:
                st.download_button(
                    "⬇️ Download",
                    data=json.dumps(state, indent=2),
                    file_name=f"workflow_{workflow_id[:8]}.json",
                    mime="application/json",
                    use_container_width=True
                )
    
    # Auto-save indicator
    if auto_save:
        st.caption("🟢 Auto-save enabled - Progress saved automatically")
    else:
        st.caption("🟡 Auto-save disabled - Remember to save manually")

def create_user_dashboard_widgets(widgets: List[Dict]):
    """
    Create personalized dashboard widgets based on user behavior
    """
    if not widgets:
        return
    
    st.subheader("📊 Your Dashboard")
    
    # Organize widgets by type
    widget_cols = st.columns(len(widgets))
    
    for idx, widget in enumerate(widgets):
        with widget_cols[idx]:
            widget_type = widget.get('type')
            title = widget.get('title', 'Widget')
            data = widget.get('data', {})
            
            with st.container(border=True):
                st.subheader(title)
                
                if widget_type == 'recent_workflows':
                    for workflow in data[:3]:  # Show top 3
                        progress = workflow.get('progress', 0)
                        mode = workflow.get('mode', '').replace('_', ' ').title()
                        updated = workflow.get('updated_at', '').split('T')[0]  # Just date
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{mode}**")
                            st.caption(f"Updated: {updated}")
                            st.progress(progress / 100, text=f"{progress:.0f}%")
                        with col2:
                            if st.button("📂", key=f"resume_{workflow['workflow_id']}", help="Resume"):
                                st.session_state[f"resume_workflow"] = workflow['workflow_id']
                
                elif widget_type == 'quick_actions':
                    for action, count in data:
                        action_name = action.replace('_', ' ').title()
                        if st.button(f"⚡ {action_name}", key=f"quick_{action}", use_container_width=True):
                            st.session_state[f"quick_action"] = action
                
                elif widget_type == 'performance_stats':
                    st.metric("Efficiency Score", f"{data.get('efficiency_score', 0):.0f}%")
                    st.metric("Completions", data.get('successful_completions', 0))
                    avg_time = data.get('avg_completion_time', 0)
                    st.metric("Avg Time", f"{avg_time//60:.0f}m {avg_time%60:.0f}s")

def create_keyboard_shortcuts_panel(shortcuts: Dict):
    """
    Create keyboard shortcuts help panel
    """
    if not shortcuts:
        return
    
    with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
        st.markdown("**Available Shortcuts:**")
        
        shortcut_cols = st.columns(2)
        
        for idx, (key, info) in enumerate(shortcuts.items()):
            col_idx = idx % 2
            with shortcut_cols[col_idx]:
                st.code(f"{key}: {info.get('description', 'Action')}")
        
        st.info("💡 **Tip:** Use shortcuts to navigate quickly through your workflow!")

def create_workflow_analytics_panel(user_id: str, workflow_engine):
    """
    Create workflow analytics and insights panel
    """
    st.subheader("📈 Workflow Analytics")
    
    # Get user behavior data
    behavior = workflow_engine.user_behaviors.get(user_id)
    if not behavior:
        st.info("Complete a few workflows to see your analytics!")
        return
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Completions", behavior.successful_completions)
    
    with col2:
        if behavior.average_step_time:
            avg_time = sum(behavior.average_step_time.values()) / len(behavior.average_step_time)
            st.metric("Avg Step Time", f"{avg_time:.0f}s")
        else:
            st.metric("Avg Step Time", "N/A")
    
    with col3:
        total_actions = sum(behavior.feature_usage.values())
        st.metric("Total Actions", total_actions)
    
    with col4:
        # Calculate efficiency score
        if behavior.average_step_time:
            benchmark_time = 300  # 5 minutes
            avg_time = sum(behavior.average_step_time.values()) / len(behavior.average_step_time)
            efficiency = max(0, min(100, 100 - (avg_time / benchmark_time) * 100))
            st.metric("Efficiency", f"{efficiency:.0f}%")
        else:
            st.metric("Efficiency", "N/A")
    
    # Most used features
    if behavior.feature_usage:
        st.subheader("🔥 Most Used Features")
        top_features = sorted(behavior.feature_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for feature, count in top_features:
            feature_name = feature.replace('_', ' ').title()
            st.write(f"**{feature_name}:** {count} times")

def create_card_grid(cards: List[Dict[str, any]], columns: int = 3):
    """Create a responsive card grid layout"""
    cols = st.columns(columns)
    
    for idx, card in enumerate(cards):
        col_idx = idx % columns
        with cols[col_idx]:
            with st.container(border=True):
                if card.get('icon'):
                    st.markdown(f"## {card['icon']}")
                if card.get('title'):
                    st.subheader(card['title'])
                if card.get('content'):
                    st.markdown(card['content'])
                if card.get('action'):
                    if st.button(
                        card['action']['label'],
                        key=f"card_action_{idx}",
                        use_container_width=True,
                        type=card['action'].get('type', 'secondary')
                    ):
                        if 'callback' in card['action']:
                            card['action']['callback']()

def create_mobile_nav(items: List[Dict[str, str]], current_page: str):
    """Create mobile-friendly navigation with bottom nav for primary actions"""
    # Check if we're in mobile mode
    is_mobile = st.session_state.get('layout_info', {}).get('is_mobile', False)
    
    if is_mobile:
        # Bottom navigation for mobile - primary actions only
        primary_items = [item for item in items if item.get('primary', False)][:4]  # Max 4 for mobile
        
        if primary_items:
            st.markdown("""
            <style>
            .mobile-bottom-nav {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                border-top: 1px solid #e0e0e0;
                padding: 8px;
                z-index: 1000;
                display: flex;
                justify-content: space-around;
                box-shadow: 0 -2px 8px rgba(0,0,0,0.1);
            }
            
            .mobile-nav-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 8px;
                min-width: 44px;
                min-height: 44px;
                text-decoration: none;
                color: #666;
                border-radius: 8px;
                transition: all 0.2s ease;
            }
            
            .mobile-nav-item.active {
                background-color: #032A51;
                color: white;
            }
            
            .mobile-nav-item:hover {
                background-color: #f0f0f0;
            }
            
            .mobile-nav-icon {
                font-size: 20px;
                margin-bottom: 2px;
            }
            
            .mobile-nav-label {
                font-size: 10px;
                font-weight: 500;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create bottom navigation
            nav_html = '<div class="mobile-bottom-nav">'
            for item in primary_items:
                active_class = 'active' if item['key'] == current_page else ''
                nav_html += f"""
                <div class="mobile-nav-item {active_class}" onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: '{item['key']}'}}, '*')">
                    <div class="mobile-nav-icon">{item.get('icon', '📄')}</div>
                    <div class="mobile-nav-label">{item['label'][:6]}</div>
                </div>
                """
            nav_html += '</div>'
            
            st.markdown(nav_html, unsafe_allow_html=True)
            
            # Add bottom padding to prevent content from being hidden
            st.markdown('<div style="height: 80px;"></div>', unsafe_allow_html=True)
        
        # Hamburger menu for secondary items
        with st.sidebar:
            st.markdown("### 📱 Navigation")
            for item in items:
                if not item.get('primary', False):
                    if st.button(f"{item.get('icon', '📄')} {item['label']}", 
                               key=f"nav_{item['key']}", 
                               use_container_width=True):
                        return item['key']
    else:
        # Standard navigation for desktop/tablet
        page_options = [item['label'] for item in items]
        current_index = next((i for i, item in enumerate(items) if item['key'] == current_page), 0)
        
        selected_page = st.selectbox(
            "📱 Navigate",
            page_options,
            index=current_index,
            label_visibility="collapsed"
        )
        
        # Return the key of selected page
        selected_item = next((item for item in items if item['label'] == selected_page), items[0])
        return selected_item['key']
    
    return current_page

def create_theme_toggle():
    """Create a theme toggle widget (simulated with session state)"""
    with st.sidebar:
        st.divider()
        current_theme = st.session_state.get('theme', 'light')
        theme_icon = "🌙" if current_theme == 'light' else "☀️"
        theme_label = "Dark Mode" if current_theme == 'light' else "Light Mode"
        
        if st.button(f"{theme_icon} {theme_label}", use_container_width=True):
            new_theme = 'dark' if current_theme == 'light' else 'light'
            st.session_state['theme'] = new_theme
            st.rerun()
        
        return st.session_state.get('theme', 'light')

def create_progress_ring(percentage: int, label: str, color: str = 'primary'):
    """Create a circular progress indicator using text representation"""
    with st.container(border=True):
        # Text-based progress ring
        filled_segments = int(percentage / 10)
        empty_segments = 10 - filled_segments
        
        progress_ring = "●" * filled_segments + "○" * empty_segments
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### {percentage}%")
        with col2:
            st.markdown(f"**{label}**")
            st.markdown(progress_ring)

def create_data_visualization(data: Dict[str, any], chart_type: str = 'bar'):
    """Create data visualizations using Streamlit native charts"""
    if chart_type == 'bar':
        st.bar_chart(data)
    elif chart_type == 'line':
        st.line_chart(data)
    elif chart_type == 'area':
        st.area_chart(data)
    else:
        st.bar_chart(data)

# Multi-step Wizard Components

def create_wizard_navigation(steps: List[str], current_step: int):
    """Create wizard-style navigation"""
    cols = st.columns(len(steps))
    
    for idx, step in enumerate(steps):
        with cols[idx]:
            step_num = idx + 1
            if step_num < current_step:
                st.success(f"✅ {step_num}. {step}")
            elif step_num == current_step:
                st.info(f"👉 {step_num}. {step}")
            else:
                st.text(f"⭕ {step_num}. {step}")

def create_step_validator(validation_rules: List[Dict[str, any]], data: Dict[str, any]):
    """Create step-by-step validation display"""
    all_valid = True
    
    for rule in validation_rules:
        rule_key = rule['key']
        rule_label = rule['label']
        rule_validator = rule['validator']
        
        is_valid = rule_validator(data.get(rule_key))
        
        if is_valid:
            st.success(f"✅ {rule_label}")
        else:
            st.error(f"❌ {rule_label}")
            all_valid = False
    
    return all_valid

# Enhanced Table Components

def create_sortable_table(data: List[Dict[str, any]], columns: List[Dict[str, str]], key: str = "table"):
    """Create a sortable table using native components"""
    if not data:
        create_empty_state("📋", "No Data", "No items to display")
        return
    
    # Sort controls
    col1, col2 = st.columns([1, 1])
    with col1:
        sort_column = st.selectbox("Sort by", [col['key'] for col in columns], key=f"{key}_sort")
    with col2:
        sort_order = st.selectbox("Order", ["Ascending", "Descending"], key=f"{key}_order")
    
    # Sort data
    reverse_sort = sort_order == "Descending"
    sorted_data = sorted(data, key=lambda x: x.get(sort_column, ''), reverse=reverse_sort)
    
    # Display table
    for idx, row in enumerate(sorted_data):
        with st.container(border=True):
            cols = st.columns([col.get('width', 1) for col in columns])
            for col_idx, col in enumerate(columns):
                with cols[col_idx]:
                    value = row.get(col['key'], '')
                    if col.get('type') == 'action':
                        if st.button(col['label'], key=f"{key}_{idx}_{col['key']}"):
                            if 'callback' in col:
                                col['callback'](row)
                    else:
                        st.text(str(value))

# Advanced Form Components

def create_multi_step_form(steps: List[Dict[str, any]], current_step: int, form_data: Dict[str, any]):
    """Create a multi-step form with navigation"""
    # Show progress
    create_wizard_navigation([step['title'] for step in steps], current_step)
    
    st.divider()
    
    # Show current step
    if 0 <= current_step - 1 < len(steps):
        current_step_config = steps[current_step - 1]
        
        st.subheader(current_step_config['title'])
        if current_step_config.get('description'):
            st.markdown(current_step_config['description'])
        
        # Render step content
        if 'render_func' in current_step_config:
            current_step_config['render_func'](form_data)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_step > 1:
                prev_button = st.button("⬅️ Previous", key="form_prev")
            else:
                prev_button = False
        
        with col2:
            # Validate current step
            is_valid = True
            if 'validator' in current_step_config:
                is_valid = current_step_config['validator'](form_data)
        
        with col3:
            if current_step < len(steps):
                next_button = st.button("➡️ Next", key="form_next", disabled=not is_valid)
            else:
                next_button = st.button("✅ Complete", key="form_complete", disabled=not is_valid, type="primary")
        
        return {"prev": prev_button, "next": next_button, "valid": is_valid}
    
    return {"prev": False, "next": False, "valid": False}

def create_animated_transition(duration=0.3):
    """Create smooth page transitions"""
    st.markdown(f"""
        <style>
        * {{
            transition: all {duration}s ease;
        }}
        
        .stApp > div {{
            animation: fadeIn {duration}s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        </style>
    """, unsafe_allow_html=True)

# ================================
# ENHANCED BUTTON SYSTEM - WCAG 2.2 COMPLIANT
# ================================

def create_prominent_button(
    text: str, 
    key: str,
    button_type: str = "primary",
    size: str = "medium",
    icon: Optional[str] = None,
    disabled: bool = False,
    use_container_width: bool = True,
    help_text: Optional[str] = None
) -> bool:
    """Create prominent, accessible buttons with proper sizing and visual hierarchy
    
    Args:
        text: Button text
        key: Unique key for the button
        button_type: 'primary', 'secondary', 'success', 'warning', 'danger'
        size: 'small' (44px), 'medium' (48px), 'large' (56px)
        icon: Optional emoji/icon to prefix the text
        disabled: Whether button is disabled
        use_container_width: Whether to use full container width
        help_text: Tooltip/help text
        
    Returns:
        bool: True if button was clicked
    """
    # Add CSS classes based on button type and size
    css_classes = []
    if button_type in ['success', 'warning', 'danger']:
        css_classes.append(button_type)
    if size != 'medium':
        css_classes.append(size)
    
    # Apply CSS classes if any
    if css_classes:
        # Create a container with CSS classes
        container_class = ' '.join(css_classes)
        st.markdown(f'<div class="stButton {container_class}">', unsafe_allow_html=True)
    
    # Create button text with optional icon
    button_text = f"{icon} {text}" if icon else text
    
    # Determine Streamlit button type
    if button_type == 'primary':
        st_type = 'primary'
    elif button_type == 'secondary':
        st_type = 'secondary'
    else:
        st_type = 'secondary'  # Custom styled via CSS
    
    # Create the button
    clicked = st.button(
        button_text,
        key=key,
        type=st_type,
        disabled=disabled,
        use_container_width=use_container_width,
        help=help_text
    )
    
    # Close CSS container if opened
    if css_classes:
        st.markdown('</div>', unsafe_allow_html=True)
    
    return clicked

def create_enhanced_button_group(
    buttons: List[Dict[str, any]], 
    key_prefix: str,
    layout: str = "horizontal"
) -> Dict[str, bool]:
    """Create a group of related buttons with consistent styling
    
    Args:
        buttons: List of button configurations
        key_prefix: Prefix for button keys
        layout: 'horizontal' or 'vertical'
        
    Returns:
        Dict mapping button keys to clicked status
    """
    results = {}
    
    if layout == "horizontal":
        cols = st.columns(len(buttons))
        for idx, button_config in enumerate(buttons):
            with cols[idx]:
                button_key = f"{key_prefix}_{button_config['key']}"
                clicked = create_prominent_button(
                    text=button_config['text'],
                    key=button_key,
                    button_type=button_config.get('type', 'secondary'),
                    size=button_config.get('size', 'medium'),
                    icon=button_config.get('icon'),
                    disabled=button_config.get('disabled', False),
                    help_text=button_config.get('help')
                )
                results[button_config['key']] = clicked
    else:
        for button_config in buttons:
            button_key = f"{key_prefix}_{button_config['key']}"
            clicked = create_prominent_button(
                text=button_config['text'],
                key=button_key,
                button_type=button_config.get('type', 'secondary'),
                size=button_config.get('size', 'medium'),
                icon=button_config.get('icon'),
                disabled=button_config.get('disabled', False),
                help_text=button_config.get('help')
            )
            results[button_config['key']] = clicked
    
    return results

# ================================
# MOBILE-SPECIFIC COMPONENTS AND UTILITIES
# ================================

def detect_mobile_device():
    """Detect if user is on mobile device (simulated for now)"""
    # In production, this would use JavaScript to detect screen size
    # For now, use session state toggle or CSS media queries
    return st.session_state.get('layout_info', {}).get('is_mobile', False)

def create_mobile_friendly_form(form_fields: List[Dict[str, Any]], form_key: str = "mobile_form"):
    """Create a mobile-optimized form with proper spacing and touch targets"""
    is_mobile = detect_mobile_device()
    
    with st.form(form_key):
        for field in form_fields:
            field_type = field.get('type', 'text')
            field_label = field.get('label', 'Field')
            field_key = field.get('key', 'field')
            field_required = field.get('required', False)
            field_help = field.get('help', None)
            
            # Add spacing for mobile
            if is_mobile:
                st.markdown('<div style="margin-bottom: 16px;"></div>', unsafe_allow_html=True)
            
            # Create field based on type
            if field_type == 'text':
                st.text_input(
                    field_label,
                    key=f"{form_key}_{field_key}",
                    help=field_help,
                    placeholder=field.get('placeholder', '')
                )
            elif field_type == 'email':
                st.text_input(
                    field_label,
                    key=f"{form_key}_{field_key}",
                    help=field_help,
                    placeholder=field.get('placeholder', 'email@example.com')
                )
            elif field_type == 'select':
                st.selectbox(
                    field_label,
                    field.get('options', []),
                    key=f"{form_key}_{field_key}",
                    help=field_help
                )
            elif field_type == 'textarea':
                st.text_area(
                    field_label,
                    key=f"{form_key}_{field_key}",
                    help=field_help,
                    height=150 if is_mobile else 100
                )
            elif field_type == 'file':
                st.file_uploader(
                    field_label,
                    key=f"{form_key}_{field_key}",
                    help=field_help,
                    type=field.get('accepted_types', None)
                )
        
        # Submit button with proper mobile sizing
        submit_col1, submit_col2 = st.columns([3, 1] if not is_mobile else [1])
        with submit_col1 if not is_mobile else st.container():
            submitted = st.form_submit_button(
                "Submit",
                type="primary",
                use_container_width=True
            )
    
    return submitted

def create_mobile_card_grid(cards: List[Dict[str, Any]], mobile_columns: int = 1, desktop_columns: int = 3):
    """Create a responsive card grid that adapts to mobile"""
    is_mobile = detect_mobile_device()
    columns = mobile_columns if is_mobile else desktop_columns
    
    cols = st.columns(columns)
    
    for idx, card in enumerate(cards):
        col_idx = idx % columns
        with cols[col_idx]:
            with st.container(border=True):
                # Add mobile-specific styling
                if is_mobile:
                    st.markdown('<div style="padding: 8px;">', unsafe_allow_html=True)
                
                if card.get('icon'):
                    st.markdown(f"## {card['icon']}")
                if card.get('title'):
                    st.subheader(card['title'])
                if card.get('content'):
                    st.markdown(card['content'])
                if card.get('metric'):
                    st.metric(card['metric']['label'], card['metric']['value'])
                
                # Mobile-friendly action button
                if card.get('action'):
                    button_key = f"card_action_{idx}_{card.get('key', 'action')}"
                    if st.button(
                        card['action']['label'],
                        key=button_key,
                        use_container_width=True,
                        type=card['action'].get('type', 'secondary')
                    ):
                        if 'callback' in card['action']:
                            card['action']['callback']()
                
                if is_mobile:
                    st.markdown('</div>', unsafe_allow_html=True)

def create_mobile_data_table(data: List[Dict[str, Any]], columns: List[str], mobile_view: str = "cards"):
    """Create a mobile-friendly data display"""
    is_mobile = detect_mobile_device()
    
    if is_mobile and mobile_view == "cards":
        # Show data as cards on mobile
        for idx, row in enumerate(data):
            with st.container(border=True):
                for col in columns:
                    if col in row:
                        st.markdown(f"**{col.title()}:** {row[col]}")
                
                # Add action buttons if present
                if 'actions' in row:
                    action_cols = st.columns(len(row['actions']))
                    for act_idx, action in enumerate(row['actions']):
                        with action_cols[act_idx]:
                            if st.button(
                                action['label'],
                                key=f"row_{idx}_action_{act_idx}",
                                use_container_width=True
                            ):
                                if 'callback' in action:
                                    action['callback'](row)
    else:
        # Standard table for desktop
        import pandas as pd
        df = pd.DataFrame(data)
        if columns:
            df = df[columns]
        st.dataframe(df, use_container_width=True)

def create_mobile_workflow_stepper(steps: List[Dict[str, Any]], current_step: int):
    """Create a mobile-optimized workflow stepper"""
    is_mobile = detect_mobile_device()
    
    if is_mobile:
        # Compact vertical stepper for mobile
        st.markdown("### Progress")
        progress_percentage = (current_step - 1) / len(steps) if len(steps) > 0 else 0
        st.progress(progress_percentage, text=f"Step {current_step} of {len(steps)}")
        
        # Current step card
        if 0 < current_step <= len(steps):
            current_step_info = steps[current_step - 1]
            with st.container(border=True):
                st.markdown(f"### {current_step_info.get('icon', '📄')} {current_step_info.get('title', f'Step {current_step}')}")
                if current_step_info.get('description'):
                    st.markdown(current_step_info['description'])
        
        # Step navigation
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if current_step > 1:
                if st.button("⬅️", key="prev_step", help="Previous Step"):
                    return "prev"
        with col2:
            st.markdown(f"**Step {current_step} of {len(steps)}**")
        with col3:
            if current_step < len(steps):
                if st.button("➡️", key="next_step", help="Next Step"):
                    return "next"
    else:
        # Horizontal stepper for desktop
        cols = st.columns(len(steps))
        for idx, step in enumerate(steps):
            step_num = idx + 1
            with cols[idx]:
                if step_num < current_step:
                    st.success(f"✅ {step_num}. {step.get('title', f'Step {step_num}')}")
                elif step_num == current_step:
                    st.info(f"👉 {step_num}. {step.get('title', f'Step {step_num}')}")
                else:
                    st.text(f"⭕ {step_num}. {step.get('title', f'Step {step_num}')}")
    
    return None

def create_floating_action_button(actions: List[Dict[str, Any]], position: str = "bottom-right"):
    """Create a floating action button for mobile quick actions"""
    is_mobile = detect_mobile_device()
    
    if not is_mobile or not actions:
        return
    
    # Position mapping
    position_styles = {
        "bottom-right": "bottom: 20px; right: 20px;",
        "bottom-left": "bottom: 20px; left: 20px;",
        "bottom-center": "bottom: 20px; left: 50%; transform: translateX(-50%);"
    }
    
    position_style = position_styles.get(position, position_styles["bottom-right"])
    
    # Single FAB or multiple actions
    if len(actions) == 1:
        action = actions[0]
        fab_html = f"""
        <style>
        .fab {{
            position: fixed;
            {position_style}
            width: 56px;
            height: 56px;
            background-color: #032A51;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(3, 42, 81, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 1000;
            transition: all 0.3s ease;
            border: none;
        }}
        
        .fab:hover {{
            transform: scale(1.1) translateY(-2px);
            box-shadow: 0 6px 16px rgba(3, 42, 81, 0.4);
        }}
        
        .fab-icon {{
            color: white;
            font-size: 24px;
        }}
        </style>
        
        <button class="fab" onclick="alert('{action.get('label', 'Action')} clicked!')">
            <span class="fab-icon">{action.get('icon', '+')}</span>
        </button>
        """
        st.markdown(fab_html, unsafe_allow_html=True)
    else:
        # Multi-action FAB menu
        st.markdown("""
        <style>
        .fab-menu {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }
        
        .fab-actions {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .fab-action {
            width: 48px;
            height: 48px;
            background-color: #032A51;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 18px;
            box-shadow: 0 2px 8px rgba(3, 42, 81, 0.3);
            cursor: pointer;
            transition: all 0.2s ease;
            border: none;
        }
        
        .fab-action:hover {
            transform: scale(1.1);
        }
        
        .fab-main {
            width: 56px;
            height: 56px;
            background-color: #032A51;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(3, 42, 81, 0.3);
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
        }
        </style>
        
        <div class="fab-menu">
            <div class="fab-actions">
        """, unsafe_allow_html=True)
        
        for idx, action in enumerate(actions[:-1]):  # All except last
            st.markdown(f"""
                <button class="fab-action" onclick="alert('{action.get('label', 'Action')} clicked!')">
                    {action.get('icon', '•')}
                </button>
            """, unsafe_allow_html=True)
        
        # Main FAB (last action or toggle)
        main_action = actions[-1] if actions else {'icon': '+', 'label': 'Menu'}
        st.markdown(f"""
            </div>
            <button class="fab-main" onclick="alert('{main_action.get('label', 'Menu')} clicked!')">
                {main_action.get('icon', '+')}
            </button>
        </div>
        """, unsafe_allow_html=True)

def create_touch_friendly_inputs(input_config: Dict[str, Any]):
    """Create touch-friendly input components with proper sizing"""
    is_mobile = detect_mobile_device()
    
    # Apply mobile-specific CSS for inputs
    if is_mobile:
        st.markdown("""
        <style>
        /* Touch-friendly inputs */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {
            min-height: 52px !important;
            font-size: 18px !important;
            padding: 12px 16px !important;
            border-radius: 12px !important;
        }
        
        /* File uploader touch targets */
        .stFileUploader > div > div {
            min-height: 52px !important;
            padding: 12px !important;
        }
        
        /* Checkbox and radio touch targets */
        .stCheckbox > label,
        .stRadio > label {
            min-height: 44px !important;
            padding: 10px !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    return input_config

def audit_touch_targets():
    """Audit and report touch target compliance"""
    report = {
        "compliant_elements": [],
        "non_compliant_elements": [],
        "recommendations": []
    }
    
    # This would be implemented with JavaScript in production
    # For now, return a mock report
    report["compliant_elements"] = [
        "Primary buttons (52px+ on mobile)",
        "Text inputs (52px+ height)",
        "Select boxes (52px+ height)",
        "Navigation buttons (48px+ minimum)"
    ]
    
    report["non_compliant_elements"] = [
        # Would be populated by actual measurement
    ]
    
    report["recommendations"] = [
        "Ensure 8px minimum spacing between interactive elements",
        "Use border-radius of 8px+ for better thumb-friendly interaction",
        "Consider thumb zones - place primary actions in easy-reach areas",
        "Test on actual devices, not just browser dev tools"
    ]
    
    return report