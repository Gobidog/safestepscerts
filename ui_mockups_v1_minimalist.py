"""
UI Mockup Implementation - Version 1: Minimalist Professional
Clean, efficient implementation focused on usability and professional appearance
"""

import streamlit as st
from typing import Dict, List, Optional, Callable
import pandas as pd

# Color constants for V1 - Minimalist Professional
MINIMALIST_COLORS = {
    'primary_navy': '#1A365D',
    'primary_blue': '#3182CE', 
    'accent_green': '#38A169',
    'gray_50': '#F7FAFC',
    'gray_100': '#EDF2F7',
    'gray_200': '#E2E8F0',
    'gray_300': '#CBD5E0',
    'gray_500': '#718096',
    'gray_700': '#2D3748',
    'gray_900': '#1A202C',
    'success': '#38A169',
    'warning': '#D69E2E',
    'error': '#E53E3E',
    'info': '#3182CE'
}

def apply_minimalist_theme():
    """Apply minimalist professional theme"""
    st.markdown("""
    <style>
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #F7FAFC;
    }
    
    /* Header styling */
    .minimalist-header {
        background: white;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        color: #1A365D;
        font-size: 1.875rem;
        font-weight: 700;
        margin: 0;
        line-height: 1.2;
    }
    
    .header-subtitle {
        color: #718096;
        font-size: 0.875rem;
        margin: 0.25rem 0 0 0;
        font-weight: 400;
    }
    
    .user-info {
        text-align: right;
    }
    
    .user-name {
        color: #2D3748;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .user-role {
        color: #718096;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Progress indicator */
    .progress-stepper {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: white;
        padding: 2rem;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
        position: relative;
    }
    
    .step-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
    }
    
    .step.completed .step-icon {
        background: #38A169;
        color: white;
    }
    
    .step.active .step-icon {
        background: #3182CE;
        color: white;
        box-shadow: 0 0 0 4px rgba(49, 130, 206, 0.2);
    }
    
    .step.pending .step-icon {
        background: #E2E8F0;
        color: #718096;
    }
    
    .step-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #2D3748;
        text-align: center;
    }
    
    .step-connector {
        height: 2px;
        flex: 1;
        background: #E2E8F0;
        margin: 0 1rem;
        position: relative;
        top: -20px;
    }
    
    .step-connector.completed {
        background: #38A169;
    }
    
    /* Card styling */
    .content-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        margin-bottom: 2rem;
    }
    
    .card-header {
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #E2E8F0;
        background: #F7FAFC;
    }
    
    .card-title {
        color: #1A365D;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
    }
    
    .card-description {
        color: #718096;
        font-size: 0.875rem;
        margin: 0;
    }
    
    .card-body {
        padding: 2rem;
    }
    
    /* Button styling */
    .btn-primary {
        background: #3182CE;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }
    
    .btn-primary:hover {
        background: #2C5AA0;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(49, 130, 206, 0.3);
    }
    
    .btn-secondary {
        background: #EDF2F7;
        color: #2D3748;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-size: 0.875rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .btn-secondary:hover {
        background: #E2E8F0;
        border-color: #CBD5E0;
    }
    
    /* Table styling */
    .data-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .data-table th {
        background: #F7FAFC;
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.875rem;
        color: #2D3748;
        border-bottom: 1px solid #E2E8F0;
    }
    
    .data-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid #F1F5F9;
        font-size: 0.875rem;
        color: #2D3748;
    }
    
    .data-table tr:hover {
        background: #F7FAFC;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-badge.success {
        background: #C6F6D5;
        color: #276749;
    }
    
    .status-badge.warning {
        background: #FAF089;
        color: #744210;
    }
    
    .status-badge.error {
        background: #FED7D7;
        color: #C53030;
    }
    
    /* Sidebar styling */
    .sidebar {
        background: white;
        border-right: 1px solid #E2E8F0;
        padding: 1.5rem 0;
    }
    
    .nav-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 1.5rem;
        color: #718096;
        text-decoration: none;
        transition: all 0.2s ease;
        border-left: 3px solid transparent;
    }
    
    .nav-item:hover {
        background: #F7FAFC;
        color: #2D3748;
    }
    
    .nav-item.active {
        background: #EBF8FF;
        color: #3182CE;
        border-left-color: #3182CE;
    }
    
    .nav-icon {
        margin-right: 0.75rem;
        font-size: 1.125rem;
    }
    
    .nav-label {
        font-weight: 500;
        font-size: 0.875rem;
    }
    </style>
    """, unsafe_allow_html=True)

def create_minimalist_header(user_name: str, user_role: str):
    """Create clean, professional header"""
    st.markdown(f"""
    <div class="minimalist-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 class="header-title">SafeSteps Certificate Generator</h1>
                <p class="header-subtitle">Professional Certificate Management System v2.1</p>
            </div>
            <div class="user-info">
                <div class="user-name">{user_name}</div>
                <div class="user-role">{user_role}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_minimalist_progress(current_step: int):
    """Create clean progress indicator"""
    steps = [
        ("1", "Upload", 1),
        ("2", "Validate", 2), 
        ("3", "Template", 3),
        ("4", "Generate", 4),
        ("✓", "Complete", 5)
    ]
    
    progress_html = '<div class="progress-stepper">'
    
    for i, (icon, label, step_num) in enumerate(steps):
        # Determine step state
        if step_num < current_step:
            step_class = "completed"
            step_icon = "✓"
        elif step_num == current_step:
            step_class = "active"  
            step_icon = str(step_num)
        else:
            step_class = "pending"
            step_icon = str(step_num)
        
        progress_html += f"""
        <div class="step {step_class}">
            <div class="step-icon">{step_icon}</div>
            <div class="step-label">{label}</div>
        </div>
        """
        
        # Add connector except for last step
        if i < len(steps) - 1:
            connector_class = "completed" if step_num < current_step else ""
            progress_html += f'<div class="step-connector {connector_class}"></div>'
    
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)

def create_minimalist_card(title: str, description: str, content_func: Callable):
    """Create clean content card"""
    st.markdown(f"""
    <div class="content-card">
        <div class="card-header">
            <h2 class="card-title">{title}</h2>
            <p class="card-description">{description}</p>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    # Execute content function
    content_func()
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def create_minimalist_data_table(df: pd.DataFrame, title: str = "Data Overview"):
    """Create clean, scannable data table"""
    st.markdown(f"""
    <div class="content-card">
        <div class="card-header">
            <h3 class="card-title">{title}</h3>
            <p class="card-description">{len(df)} records total</p>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    # Search functionality
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("Search students", key="min_search", label_visibility="collapsed", placeholder="🔍 Search by name or email...")
    with col2:
        status_filter = st.selectbox("Filter status", ["All", "Valid", "Warning", "Error"], key="min_filter")
    
    # Apply filters
    filtered_df = df.copy()
    if search:
        filtered_df = filtered_df[
            (filtered_df['name'].str.contains(search, case=False, na=False)) |
            (filtered_df['email'].str.contains(search, case=False, na=False))
        ]
    
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'].str.title() == status_filter]
    
    # Display table with clean styling
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Student Name", width="medium"),
            "email": st.column_config.TextColumn("Email Address", width="large"), 
            "course": st.column_config.TextColumn("Course", width="medium"),
            "status": st.column_config.SelectboxColumn(
                "Status",
                options=["Valid", "Warning", "Error"],
                required=True,
                width="small"
            )
        }
    )
    
    # Summary info
    st.caption(f"Showing {len(filtered_df)} of {len(df)} records")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def create_minimalist_metrics(metrics: Dict):
    """Create clean metrics display"""
    st.markdown("""
    <div class="content-card">
        <div class="card-header">
            <h3 class="card-title">Data Summary</h3>
            <p class="card-description">Overview of uploaded data</p>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 Total Records",
            value=metrics.get('total', 0),
            delta=metrics.get('total_delta')
        )
    
    with col2:
        st.metric(
            label="✅ Valid",
            value=metrics.get('valid', 0),
            delta=metrics.get('valid_delta')
        )
    
    with col3:
        st.metric(
            label="⚠️ Warnings", 
            value=metrics.get('warnings', 0),
            delta=metrics.get('warnings_delta')
        )
    
    with col4:
        st.metric(
            label="❌ Errors",
            value=metrics.get('errors', 0),
            delta=metrics.get('errors_delta'),
            delta_color="inverse"
        )
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def create_minimalist_action_bar(actions: List[Dict]):
    """Create clean action button bar"""
    if not actions:
        return
        
    cols = st.columns(len(actions))
    
    for i, action in enumerate(actions):
        with cols[i]:
            button_type = "primary" if action.get('primary') else "secondary"
            
            if st.button(
                action['label'],
                key=action.get('key', f'action_{i}'),
                type=button_type,
                use_container_width=True,
                help=action.get('help')
            ):
                if action.get('callback'):
                    action['callback']()

def create_minimalist_status_summary(status_counts: Dict):
    """Create clean status summary"""
    st.markdown("""
    <div class="content-card">
        <div class="card-header">
            <h3 class="card-title">Validation Status</h3>
            <p class="card-description">Summary of data validation results</p>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem; color: #38A169; margin-bottom: 0.5rem;">✅</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #2D3748;">{status_counts.get('valid', 0)}</div>
            <div style="font-size: 0.875rem; color: #718096;">Valid Records</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem; color: #D69E2E; margin-bottom: 0.5rem;">⚠️</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #2D3748;">{status_counts.get('warnings', 0)}</div>
            <div style="font-size: 0.875rem; color: #718096;">Warnings</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 2rem; color: #E53E3E; margin-bottom: 0.5rem;">❌</div>
            <div style="font-size: 1.5rem; font-weight: 600; color: #2D3748;">{status_counts.get('errors', 0)}</div>
            <div style="font-size: 0.875rem; color: #718096;">Errors</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div></div>", unsafe_allow_html=True)

def demo_minimalist_ui():
    """Demo of the minimalist professional UI"""
    # Apply theme
    apply_minimalist_theme()
    
    # Header
    create_minimalist_header("Dr. Sarah Johnson", "Administrator")
    
    # Progress indicator
    create_minimalist_progress(2)  # Currently on step 2 (Validate)
    
    # Sample data
    sample_data = pd.DataFrame([
        {"name": "John Smith", "email": "john.smith@school.edu", "course": "Digital Safety", "status": "Valid"},
        {"name": "Jane Doe", "email": "jane.doe@school.edu", "course": "Internet Ethics", "status": "Valid"},
        {"name": "Bob Wilson", "email": "bob.wilson@school.edu", "course": "Digital Safety", "status": "Warning"},
        {"name": "Alice Brown", "email": "alice.brown@", "course": "Cybersecurity", "status": "Error"},
        {"name": "Charlie Davis", "email": "charlie.davis@school.edu", "course": "Digital Safety", "status": "Valid"},
    ])
    
    # Metrics
    metrics = {
        'total': 125,
        'valid': 118,
        'warnings': 5,
        'errors': 2,
        'total_delta': 25,
        'valid_delta': 20
    }
    
    create_minimalist_metrics(metrics)
    
    # Status summary
    status_counts = {'valid': 118, 'warnings': 5, 'errors': 2}
    create_minimalist_status_summary(status_counts)
    
    # Data table
    create_minimalist_data_table(sample_data, "Validation Results")
    
    # Action buttons
    actions = [
        {
            'label': '⬅️ Back to Upload',
            'key': 'back_upload',
            'help': 'Return to upload step'
        },
        {
            'label': '🔧 Fix Errors',
            'key': 'fix_errors',
            'help': 'Address validation errors'
        },
        {
            'label': 'Continue to Template ➡️',
            'key': 'continue_template',
            'primary': True,
            'help': 'Proceed to template selection'
        }
    ]
    
    create_minimalist_action_bar(actions)
    
    # Footer info
    st.markdown("---")
    st.caption("SafeSteps Certificate Generator v2.1 | Minimalist Professional Theme")

if __name__ == "__main__":
    st.set_page_config(
        page_title="SafeSteps - Minimalist UI Demo",
        page_icon="🏆",
        layout="wide"
    )
    
    demo_minimalist_ui()