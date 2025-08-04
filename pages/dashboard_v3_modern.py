"""
SafeSteps V3 - Modern Dashboard
Card-based modular interface with visual appeal and mobile-first design
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import random
from typing import Dict, List, Any
import time

from utils.auth import requires_admin, get_current_user
from utils.ui_components import (
    create_card, create_metric_card, create_empty_state,
    create_animated_transition, COLORS
)
from utils.mobile_optimization import (
    apply_global_mobile_optimizations, create_mobile_button,
    get_device_info, create_responsive_columns, MobileOptimizer
)
from utils.ui_helpers import (
    manage_navigation_state, update_navigation,
    get_user_preference, update_user_preference
)
from utils.theme_system import ThemeSystem
from utils.chart_components import (
    create_activity_chart, create_distribution_chart,
    create_sparkline, create_gauge_chart, create_comparison_chart,
    create_stats_grid, create_funnel_chart, create_kpi_dashboard
)
from utils.storage import StorageManager
from utils.course_manager import CourseManager

# Initialize managers
storage = StorageManager()
course_manager = CourseManager(storage.local_path / "metadata")
theme_system = ThemeSystem()

def get_greeting():
    """Get time-appropriate greeting"""
    current_hour = datetime.now().hour
    if current_hour < 12:
        return "Good morning"
    elif current_hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def safe_columns(responsive_cols, expected_count=2):
    """Safely create columns handling responsive layouts"""
    if len(responsive_cols) == expected_count:
        return st.columns(responsive_cols)
    elif len(responsive_cols) == 1:
        # Mobile: return single column repeated
        if expected_count == 2:
            return st.columns(1)[0], None
        elif expected_count == 3:
            return st.columns(1)[0], None, None
        else:
            return st.columns(1)[0]
    elif len(responsive_cols) == 2 and expected_count == 3:
        # Tablet to desktop: add a third column
        cols = st.columns(responsive_cols + [1])
        return cols[0], cols[1], cols[2]
    else:
        # Fallback: return the columns as-is
        return st.columns(responsive_cols)

@requires_admin
def render_dashboard_v3():
    """Render the modern visual dashboard with mobile optimization"""
    
    # Apply mobile optimizations first
    mobile_optimizer = apply_global_mobile_optimizations()
    device_info = get_device_info()
    
    # Apply theme and mobile styles
    theme_system.apply_theme()
    theme_system.apply_mobile_styles()
    
    current_user = get_current_user()
    
    # Responsive header with theme toggle
    header_cols = create_responsive_columns([1], [2, 1], [2, 1, 1])
    
    # Handle different column layouts based on device
    if len(header_cols) == 1:
        # Mobile: single column
        col1 = st.columns(1)[0]
        col2 = col3 = None
    elif len(header_cols) == 2:
        # Tablet: two columns
        col1, col2 = st.columns(header_cols)
        col3 = None
    else:
        # Desktop: three columns
        col1, col2, col3 = st.columns(header_cols)
    
    with col1:
        st.title("🎨 SafeSteps Modern Dashboard")
        greeting = get_greeting()
        st.caption(f"{greeting}, {current_user.get('username', 'Admin')}! 🎯")
    
    if col2:
        with col2:
            # Theme selector
            theme_options = list(theme_system.themes.keys())
            current_theme = st.session_state.get('theme', 'light')
            new_theme = st.selectbox(
                "🎨 Theme",
                theme_options,
                index=theme_options.index(current_theme),
                label_visibility="collapsed"
            )
            if new_theme != current_theme:
                theme_system.set_theme(new_theme)
                st.rerun()
    
    if col3:
        with col3:
            # Refresh with animation (mobile-optimized)
            if create_mobile_button("🔄 Refresh", "dashboard_refresh", button_type="secondary", size="medium"):
                with st.spinner("Refreshing data..."):
                    st.balloons()
                    st.rerun()
    elif not col2:  # Mobile layout - add controls below title
        with col1:
            # Theme selector for mobile
            theme_options = list(theme_system.themes.keys())
            current_theme = st.session_state.get('theme', 'light')
            col_a, col_b = st.columns([2, 1])
            with col_a:
                new_theme = st.selectbox(
                    "🎨 Theme",
                    theme_options,
                    index=theme_options.index(current_theme),
                    label_visibility="collapsed"
                )
                if new_theme != current_theme:
                    theme_system.set_theme(new_theme)
                    st.rerun()
            with col_b:
                if create_mobile_button("🔄", "dashboard_refresh_mobile", button_type="secondary", size="small"):
                    with st.spinner("Refreshing..."):
                        st.balloons()
                        st.rerun()
    
    st.divider()
    
    # KPI Dashboard
    render_kpi_section()
    
    st.divider()
    
    # Main content layout
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "🏆 Certificates", 
        "📈 Analytics", 
        "⚡ Quick Actions"
    ])
    
    with tab1:
        render_overview_tab()
    
    with tab2:
        render_certificates_tab()
    
    with tab3:
        render_analytics_tab()
    
    with tab4:
        render_quick_actions_tab()
    
    # Mobile-friendly floating action button
    render_floating_action_button()

def get_greeting():
    """Get time-based greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

def render_kpi_section():
    """Render key performance indicators"""
    st.markdown("### 🎯 Key Performance Indicators")
    
    # Generate dynamic KPIs
    kpis = [
        {
            "title": "Total Certificates",
            "value": "1,247",
            "delta": "+156",
            "delta_color": "normal"
        },
        {
            "title": "Active Users",
            "value": "89",
            "delta": "+12",
            "delta_color": "normal"
        },
        {
            "title": "Completion Rate",
            "value": "94.5%",
            "delta": "+2.3%",
            "delta_color": "normal"
        },
        {
            "title": "Avg. Processing Time",
            "value": "1.2s",
            "delta": "-0.3s",
            "delta_color": "normal"
        }
    ]
    
    create_kpi_dashboard(kpis)

def render_overview_tab():
    """Render overview tab with visual elements"""
    # Responsive layout: mobile (1 col), tablet/desktop (2 cols)
    overview_cols = create_responsive_columns([1], [2, 1], [2, 1])
    col1, col2 = safe_columns(overview_cols, 2)
    
    with col1:
        # Activity chart
        st.markdown("### 📈 Certificate Generation Trend")
        create_activity_chart()
        
        st.divider()
        
        # Recent activity with animations
        st.markdown("### 🔥 Recent Activity")
        activities = [
            {"time": "2 min ago", "user": "john.doe", "action": "Generated 15 certificates", "type": "success"},
            {"time": "5 min ago", "user": "admin", "action": "Updated Digital Citizenship template", "type": "info"},
            {"time": "10 min ago", "user": "jane.smith", "action": "Added 3 new users", "type": "info"},
            {"time": "15 min ago", "user": "system", "action": "Completed automatic backup", "type": "success"}
        ]
        
        for activity in activities:
            with st.container(border=True):
                activity_type_icon = "✅" if activity["type"] == "success" else "ℹ️"
                st.markdown(f"{activity_type_icon} **{activity['user']}** {activity['action']}")
                st.caption(f"🕒 {activity['time']}")
    
    if col2:
        with col2:
            # Visual stats
            st.markdown("### 📊 Quick Stats")
            
            # Certificate distribution
            cert_data = {
                "Digital Citizenship": 456,
                "Safety Training": 389,
                "Compliance": 402
            }
            create_distribution_chart(cert_data)
            
            st.divider()
            
            # System health gauge
            st.markdown("### 💚 System Health")
            create_gauge_chart(98, 100, "Overall Health")
            
            # Storage usage
            create_gauge_chart(23, 100, "Storage Used (GB)")

def render_certificates_tab():
    """Render certificates tab with visual workflow"""
    st.markdown("### 🏆 Certificate Management")
    
    # Responsive workflow steps
    workflow_cols = create_responsive_columns([1], [1, 1], [1, 1, 1, 1])
    
    if len(workflow_cols) == 4:
        col1, col2, col3, col4 = st.columns(workflow_cols)
    elif len(workflow_cols) == 2:
        col1, col2 = st.columns(workflow_cols)
        col3, col4 = st.columns(workflow_cols)
    else:
        # Mobile: single column, stack vertically
        col1 = col2 = col3 = col4 = st.container()
    
    with col1:
        with st.container(border=True):
            st.markdown("#### 1️⃣ Upload")
            st.markdown("📤 Drop your CSV/Excel file")
            uploaded = st.file_uploader("Choose file", type=['csv', 'xlsx'], label_visibility="collapsed")
            if uploaded:
                st.success("✅ File uploaded!")
    
    with col2:
        with st.container(border=True):
            st.markdown("#### 2️⃣ Template")
            st.markdown("🎨 Choose design")
            template = st.selectbox(
                "Template",
                ["Digital Citizenship", "Safety Training", "Compliance"],
                label_visibility="collapsed"
            )
    
    with col3:
        with st.container(border=True):
            st.markdown("#### 3️⃣ Preview")
            st.markdown("👁️ Check sample")
            if create_mobile_button("Preview", "preview_btn", button_type="secondary", size="medium"):
                st.info("🖼️ Preview generated!")
    
    with col4:
        with st.container(border=True):
            st.markdown("#### 4️⃣ Generate")
            st.markdown("🚀 Create certificates")
            if create_mobile_button("Generate All", "generate_all_btn", button_type="primary", size="large"):
                with st.spinner("Generating certificates..."):
                    progress = st.progress(0)
                    for i in range(100):
                        progress.progress(i + 1)
                    st.success("🎉 Certificates ready!")
    
    st.divider()
    
    # Batch management with visual cards
    st.markdown("### 📦 Recent Batches")
    
    batches = [
        {"name": "January Training", "count": 125, "status": "completed", "date": "2024-01-15"},
        {"name": "Q1 Compliance", "count": 89, "status": "processing", "date": "2024-01-14"},
        {"name": "New Employee Onboarding", "count": 34, "status": "ready", "date": "2024-01-13"}
    ]
    
    cols = st.columns(3)
    for idx, batch in enumerate(batches):
        with cols[idx % 3]:
            with st.container(border=True):
                status_emoji = {"completed": "✅", "processing": "🔄", "ready": "📋"}
                st.markdown(f"### {status_emoji[batch['status']]} {batch['name']}")
                st.metric("Certificates", batch['count'])
                st.caption(f"📅 {batch['date']}")
                
                if batch['status'] == 'completed':
                    create_mobile_button("📥 Download", f"dl_{idx}", button_type="success", size="medium")
                elif batch['status'] == 'processing':
                    st.progress(0.7)
                else:
                    create_mobile_button("🚀 Process", f"proc_{idx}", button_type="primary", size="medium")

def render_analytics_tab():
    """Render analytics tab with data visualizations"""
    st.markdown("### 📊 Analytics Dashboard")
    
    # Time period selector
    period = st.select_slider(
        "Time Period",
        options=["Today", "This Week", "This Month", "This Quarter", "This Year"],
        value="This Month"
    )
    
    # Responsive metrics row
    metrics_cols = create_responsive_columns([1], [1, 1], [1, 1, 1, 1])
    
    if len(metrics_cols) == 4:
        col1, col2, col3, col4 = st.columns(metrics_cols)
    elif len(metrics_cols) == 2:
        col1, col2 = st.columns(metrics_cols)
        col3, col4 = st.columns(metrics_cols)
    else:
        # Mobile: show metrics vertically
        col1 = col2 = col3 = col4 = st.container()
    
    with col1:
        create_metric_card("Total Generated", "3,456", "+234", "normal")
    with col2:
        create_metric_card("Unique Recipients", "2,891", "+156", "normal")
    with col3:
        create_metric_card("Templates Used", "12", "+2", "normal")
    with col4:
        create_metric_card("Avg. Time", "1.8s", "-0.2s", "normal")
    
    st.divider()
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Funnel chart
        stages = ["Uploaded", "Validated", "Generated", "Downloaded"]
        values = [1000, 950, 920, 890]
        create_funnel_chart(stages, values, "Certificate Pipeline")
    
    with col2:
        # Comparison chart
        st.markdown("### 📊 Month-over-Month")
        last_month = [234, 156, 89, 45]
        this_month = [345, 189, 102, 67]
        labels = ["Digital", "Safety", "Compliance", "Custom"]
        create_comparison_chart(last_month, this_month, labels)
    
    st.divider()
    
    # Detailed analytics
    st.markdown("### 🔍 Detailed Analysis")
    
    tab1, tab2, tab3 = st.tabs(["By Template", "By User", "By Time"])
    
    with tab1:
        # Template performance
        template_data = pd.DataFrame({
            'Template': ['Digital Citizenship', 'Safety Training', 'Compliance', 'Custom'],
            'Usage': [456, 389, 234, 167],
            'Success Rate': [98.5, 97.2, 99.1, 95.4]
        })
        st.bar_chart(template_data.set_index('Template'))
    
    with tab2:
        # User activity
        user_data = pd.DataFrame({
            'User': ['john.doe', 'jane.smith', 'admin', 'bob.wilson'],
            'Certificates': [234, 189, 156, 98]
        })
        st.bar_chart(user_data.set_index('User'))
    
    with tab3:
        # Time-based analysis
        time_data = pd.DataFrame({
            'Hour': list(range(24)),
            'Activity': [random.randint(10, 100) for _ in range(24)]
        })
        st.line_chart(time_data.set_index('Hour'))

def render_quick_actions_tab():
    """Render quick actions tab with visual buttons"""
    st.markdown("### ⚡ Quick Actions")
    
    # Action categories
    categories = {
        "Certificate Operations": [
            {"icon": "🏆", "label": "Bulk Generate", "desc": "Generate multiple certificates at once"},
            {"icon": "📋", "label": "Template Builder", "desc": "Create custom certificate templates"},
            {"icon": "🔍", "label": "Verify Certificate", "desc": "Check certificate authenticity"},
            {"icon": "📊", "label": "Export Report", "desc": "Generate detailed reports"}
        ],
        "User Management": [
            {"icon": "👤", "label": "Add User", "desc": "Create new user account"},
            {"icon": "👥", "label": "Bulk Import", "desc": "Import users from CSV"},
            {"icon": "🔐", "label": "Reset Password", "desc": "Help user reset credentials"},
            {"icon": "📧", "label": "Send Invites", "desc": "Invite new team members"}
        ],
        "System Operations": [
            {"icon": "💾", "label": "Backup Now", "desc": "Create system backup"},
            {"icon": "🔄", "label": "Sync Data", "desc": "Synchronize with external systems"},
            {"icon": "🧹", "label": "Clean Storage", "desc": "Remove old temporary files"},
            {"icon": "⚙️", "label": "Settings", "desc": "Configure system settings"}
        ]
    }
    
    for category, actions in categories.items():
        st.markdown(f"#### {category}")
        cols = st.columns(4)
        
        for idx, action in enumerate(actions):
            with cols[idx % 4]:
                with st.container(border=True):
                    if st.button(
                        f"{action['icon']} {action['label']}", 
                        key=f"action_{category}_{idx}",
                        use_container_width=True
                    ):
                        st.success(f"Starting: {action['desc']}")
                    st.caption(action['desc'])
        
        st.divider()

def render_floating_action_button():
    """Render a floating action button for mobile"""
    fab_html = """
    <style>
    .fab {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 56px;
        height: 56px;
        background-color: var(--primary-color);
        border-radius: 50%;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 1000;
        transition: all 0.3s ease;
    }
    
    .fab:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
    }
    
    .fab-icon {
        color: white;
        font-size: 24px;
    }
    
    @media (min-width: 769px) {
        .fab {
            display: none;
        }
    }
    </style>
    
    <div class="fab" onclick="alert('Quick action menu would open here')">
        <span class="fab-icon">+</span>
    </div>
    """
    st.markdown(fab_html, unsafe_allow_html=True)

# Main entry point
if __name__ == "__main__":
    render_dashboard_v3()