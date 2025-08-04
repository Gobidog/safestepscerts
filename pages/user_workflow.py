"""
SafeSteps User Experience Redesign - Complete User Workflow
Implements streamlined certificate generation with multiple workflow paths:
- Quick Mode: Single page with smart defaults
- Guided Mode: Step-by-step with help text  
- Advanced Mode: All options visible
Built with mobile-first design and accessibility standards
"""

import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import uuid

# Import SafeSteps modules
from utils.ui_components import (
    apply_custom_css, create_prominent_button, create_enhanced_button_group,
    create_card, create_mobile_friendly_form, create_progress_steps,
    create_loading_animation, create_empty_state, create_touch_friendly_inputs,
    COLORS, TYPOGRAPHY, SPACING, BREAKPOINTS
)
from utils.workflow_engine import (
    FlexibleWorkflowEngine, WorkflowMode, StepStatus, WorkflowStep, 
    WorkflowState
)
from utils.auth import get_current_user
from utils.file_processing import SpreadsheetValidator
from utils.certificate_generation import CertificateGenerator
from data.course_manager import CourseManager

# Initialize workflow engine
workflow_engine = FlexibleWorkflowEngine()

def user_workflow_page():
    """
    Main entry point for the redesigned user workflow interface
    Implements task-oriented design with mobile-first approach
    """
    # Apply custom CSS for mobile-first design
    apply_custom_css()
    
    # Initialize session state
    _initialize_session_state()
    
    # Get current user with error handling
    user = get_current_user()
    if not user:
        _render_authentication_required()
        return
    
    user_id = user.get('username', 'anonymous')
    
    # Check for auto-resume workflow
    _check_auto_resume(user_id)
    
    # Render main interface based on current state
    if st.session_state.get('active_workflow_id'):
        _render_active_workflow(user_id)
    else:
        _render_workflow_launcher(user_id)

def _initialize_session_state():
    """Initialize all session state variables with safe defaults"""
    defaults = {
        'active_workflow_id': None,
        'workflow_mode': None,
        'workflow_step': 0,
        'workflow_data': {},
        'resumed_workflow': False,
        'error_state': None,
        'undo_stack': [],
        'mobile_nav_expanded': False,
        'help_visible': False,
        'debug_mode': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def _check_auto_resume(user_id: str):
    """Check for and offer to resume interrupted workflows"""
    if st.session_state.resumed_workflow:
        return
        
    # Try to find interrupted workflows
    saved_workflows = workflow_engine.get_user_saved_workflows(user_id)
    
    if saved_workflows:
        latest_workflow = max(saved_workflows, key=lambda w: w.get('last_modified', 0))
        time_since_last = datetime.now() - datetime.fromisoformat(
            latest_workflow.get('last_modified', datetime.now().isoformat())
        )
        
        # Offer resume if less than 24 hours old
        if time_since_last < timedelta(hours=24):
            _show_resume_workflow_banner(latest_workflow)

def _show_resume_workflow_banner(workflow_data: Dict):
    """Show banner offering to resume interrupted workflow"""
    with st.container():
        st.info("🔄 **Resume Workflow**: You have an interrupted workflow from earlier. Would you like to continue where you left off?")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col2:
            if create_prominent_button(
                "Resume",
                button_type="secondary",
                size="medium",
                key="resume_workflow"
            ):
                st.session_state.active_workflow_id = workflow_data['id']
                st.session_state.workflow_mode = WorkflowMode(workflow_data['mode'])
                st.session_state.workflow_data = workflow_data.get('data', {})
                st.session_state.workflow_step = workflow_data.get('current_step', 0)
                st.session_state.resumed_workflow = True
                st.rerun()
        
        with col3:
            if create_prominent_button(
                "Start Fresh",
                button_type="tertiary", 
                size="medium",
                key="start_fresh"
            ):
                st.session_state.resumed_workflow = True
                st.rerun()

def _render_authentication_required():
    """Render authentication required message with helpful guidance"""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 3rem 1rem;
        background: {COLORS['error_bg']};
        border: 2px solid {COLORS['error']};
        border-radius: 1rem;
        margin: 2rem 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">🔒</div>
        <h2 style="color: {COLORS['error']}; margin-bottom: 1rem;">Authentication Required</h2>
        <p style="color: {COLORS['text_secondary']}; font-size: {TYPOGRAPHY['body_large']['size']};">
            Please log in to access the certificate generation system.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if create_prominent_button(
        "Go to Login",
        button_type="primary",
        size="large",
        key="go_to_login"
    ):
        st.switch_page("Login")

def _render_workflow_launcher(user_id: str):
    """Render the main workflow mode selection interface"""
    # Hero section with clear value proposition
    _render_hero_section()
    
    # Smart suggestions based on user history
    _render_smart_suggestions(user_id)
    
    # Workflow mode selection cards
    _render_workflow_mode_cards(user_id)
    
    # Quick actions for power users
    _render_quick_actions()
    
    # Help and support section
    _render_help_section()

def _render_hero_section():
    """Render hero section with clear value proposition"""
    # Detect mobile viewport for responsive design
    is_mobile = _is_mobile_viewport()
    
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: {SPACING['3xl'] if not is_mobile else SPACING['xl']};
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['primary_light']} 50%, {COLORS['accent']} 100%);
        color: {COLORS['text_inverse']};
        border-radius: 1rem;
        margin-bottom: {SPACING['xl']};
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -50px;
            right: -50px;
            width: 100px;
            height: 100px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        "></div>
        <div style="
            position: absolute;
            bottom: -30px;
            left: -30px;
            width: 60px;
            height: 60px;
            background: rgba(255,255,255,0.1);
            border-radius: 50%;
        "></div>
        <div style="position: relative; z-index: 1;">
            <h1 style="
                margin: 0;
                font-size: {TYPOGRAPHY['display']['size'] if not is_mobile else TYPOGRAPHY['h1']['size']};
                font-weight: {TYPOGRAPHY['display']['weight']};
                line-height: {TYPOGRAPHY['display']['line_height']};
                margin-bottom: {SPACING['md']};
            ">🎓 SafeSteps Certificate Generator</h1>
            <p style="
                margin: 0;
                font-size: {TYPOGRAPHY['body_large']['size']};
                opacity: 0.9;
                max-width: 600px;
                margin: 0 auto;
                line-height: 1.6;
            ">Generate professional certificates for your courses with our streamlined, mobile-friendly interface. Choose your preferred workflow style.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_smart_suggestions(user_id: str):
    """Render AI-powered workflow suggestions based on user behavior"""
    # Get user behavior data
    user_stats = workflow_engine.get_user_statistics(user_id)
    
    if not user_stats:
        return
    
    # Determine preferred mode based on usage patterns
    preferred_mode = _analyze_user_preferences(user_stats)
    
    if preferred_mode:
        with st.container():
            st.markdown(f"""
            <div style="
                background: {COLORS['info_bg']};
                border-left: 4px solid {COLORS['info']};
                padding: {SPACING['lg']};
                border-radius: 0.5rem;
                margin-bottom: {SPACING['lg']};
            ">
                <div style="display: flex; align-items: center; gap: {SPACING['md']};">
                    <div style="font-size: 1.5rem;">💡</div>
                    <div>
                        <strong style="color: {COLORS['info']};">Smart Suggestion</strong>
                        <p style="margin: 0.5rem 0 0 0; color: {COLORS['text_secondary']};">
                            Based on your usage pattern, we recommend <strong>{preferred_mode['name']}</strong> mode. 
                            {preferred_mode['reason']}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def _analyze_user_preferences(user_stats: Dict) -> Optional[Dict]:
    """Analyze user statistics to suggest optimal workflow mode"""
    total_workflows = user_stats.get('total_workflows', 0)
    if total_workflows < 3:
        return None
    
    quick_usage = user_stats.get('quick_mode_usage', 0)
    guided_usage = user_stats.get('guided_mode_usage', 0)
    advanced_usage = user_stats.get('advanced_mode_usage', 0)
    
    # Calculate percentages
    quick_pct = (quick_usage / total_workflows) * 100
    guided_pct = (guided_usage / total_workflows) * 100
    advanced_pct = (advanced_usage / total_workflows) * 100
    
    if quick_pct > 60:
        return {
            'name': 'Quick Generate',
            'mode': WorkflowMode.QUICK_GENERATE,
            'reason': 'You typically use smart defaults and complete workflows quickly.'
        }
    elif guided_pct > 50:
        return {
            'name': 'Guided Mode',
            'mode': WorkflowMode.GUIDED_MODE,
            'reason': 'You prefer step-by-step guidance and detailed explanations.'
        }
    elif advanced_pct > 40:
        return {
            'name': 'Advanced Mode',
            'mode': WorkflowMode.ADVANCED_MODE,
            'reason': 'You frequently customize options and prefer full control.'
        }
    
    return None

def _render_workflow_mode_cards(user_id: str):
    """Render workflow mode selection cards with mobile-responsive layout"""
    st.markdown(f"""
    <h2 style="
        color: {COLORS['text_primary']};
        margin-bottom: {SPACING['lg']};
        text-align: center;
    ">Choose Your Workflow Style</h2>
    """, unsafe_allow_html=True)
    
    is_mobile = _is_mobile_viewport()
    
    if is_mobile:
        # Stack cards vertically on mobile
        _render_quick_mode_card(user_id)
        _render_guided_mode_card(user_id)
        _render_advanced_mode_card(user_id)
    else:
        # Horizontal layout on desktop/tablet
        col1, col2, col3 = st.columns(3)
        
        with col1:
            _render_quick_mode_card(user_id)
        
        with col2:
            _render_guided_mode_card(user_id)
        
        with col3:
            _render_advanced_mode_card(user_id)

def _render_quick_mode_card(user_id: str):
    """Render Quick Generate mode card"""
    with st.container():
        st.markdown(f"""
        <div style="
            background: {COLORS['surface']};
            border: 2px solid {COLORS['border']};
            border-radius: 1rem;
            padding: {SPACING['xl']};
            text-align: center;
            height: 100%;
            transition: all 0.3s ease;
            margin-bottom: {SPACING['lg']};
        ">
            <div style="font-size: 4rem; margin-bottom: {SPACING['lg']};">⚡</div>
            <h3 style="
                color: {COLORS['primary']};
                margin-bottom: {SPACING['md']};
                font-size: {TYPOGRAPHY['h3']['size']};
                font-weight: {TYPOGRAPHY['h3']['weight']};
            ">Quick Generate</h3>
            <p style="
                color: {COLORS['text_secondary']};
                margin-bottom: {SPACING['lg']};
                line-height: 1.6;
            ">Perfect for repeat tasks. Smart defaults and one-click generation with minimal input required.</p>
            
            <div style="
                background: {COLORS['success_bg']};
                padding: {SPACING['sm']};
                border-radius: 0.5rem;
                margin-bottom: {SPACING['lg']};
            ">
                <small style="color: {COLORS['success']}; font-weight: 600;">⏱️ ~2 minutes</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if create_prominent_button(
            "Start Quick Generate",
            button_type="primary",
            size="large",
            key="start_quick_mode",
            help_text="Generate certificates quickly with smart defaults"
        ):
            _start_workflow(user_id, WorkflowMode.QUICK_GENERATE)

def _render_guided_mode_card(user_id: str):
    """Render Guided Mode card"""
    with st.container():
        st.markdown(f"""
        <div style="
            background: {COLORS['surface']};
            border: 2px solid {COLORS['border']};
            border-radius: 1rem;
            padding: {SPACING['xl']};
            text-align: center;
            height: 100%;
            transition: all 0.3s ease;
            margin-bottom: {SPACING['lg']};
        ">
            <div style="font-size: 4rem; margin-bottom: {SPACING['lg']};">🎯</div>
            <h3 style="
                color: {COLORS['primary']};
                margin-bottom: {SPACING['md']};
                font-size: {TYPOGRAPHY['h3']['size']};
                font-weight: {TYPOGRAPHY['h3']['weight']};
            ">Guided Mode</h3>
            <p style="
                color: {COLORS['text_secondary']};
                margin-bottom: {SPACING['lg']};
                line-height: 1.6;
            ">Step-by-step guidance with help text, validation, and preview options. Great for new users.</p>
            
            <div style="
                background: {COLORS['info_bg']};
                padding: {SPACING['sm']};
                border-radius: 0.5rem;
                margin-bottom: {SPACING['lg']};
            ">
                <small style="color: {COLORS['info']}; font-weight: 600;">⏱️ ~5 minutes</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if create_prominent_button(
            "Start Guided Mode",
            button_type="secondary",
            size="large",
            key="start_guided_mode",
            help_text="Get step-by-step guidance through the process"
        ):
            _start_workflow(user_id, WorkflowMode.GUIDED_MODE)

def _render_advanced_mode_card(user_id: str):
    """Render Advanced Mode card"""
    with st.container():
        st.markdown(f"""
        <div style="
            background: {COLORS['surface']};
            border: 2px solid {COLORS['border']};
            border-radius: 1rem;
            padding: {SPACING['xl']};
            text-align: center;
            height: 100%;
            transition: all 0.3s ease;
            margin-bottom: {SPACING['lg']};
        ">
            <div style="font-size: 4rem; margin-bottom: {SPACING['lg']};">🔧</div>
            <h3 style="
                color: {COLORS['primary']};
                margin-bottom: {SPACING['md']};
                font-size: {TYPOGRAPHY['h3']['size']};
                font-weight: {TYPOGRAPHY['h3']['weight']};
            ">Advanced Mode</h3>
            <p style="
                color: {COLORS['text_secondary']};
                margin-bottom: {SPACING['lg']};
                line-height: 1.6;
            ">Full control with all options visible. Bulk operations, custom templates, and power user features.</p>
            
            <div style="
                background: {COLORS['warning_bg']};
                padding: {SPACING['sm']};
                border-radius: 0.5rem;
                margin-bottom: {SPACING['lg']};
            ">
                <small style="color: {COLORS['warning']}; font-weight: 600;">⏱️ ~10 minutes</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if create_prominent_button(
            "Start Advanced Mode",
            button_type="tertiary",
            size="large",
            key="start_advanced_mode",
            help_text="Access all features and customization options"
        ):
            _start_workflow(user_id, WorkflowMode.ADVANCED_MODE)

def _render_quick_actions():
    """Render quick action buttons for power users"""
    st.markdown(f"""
    <div style="
        background: {COLORS['background']};
        border: 1px solid {COLORS['border']};
        border-radius: 0.5rem;
        padding: {SPACING['lg']};
        margin: {SPACING['xl']} 0;
    ">
        <h3 style="
            color: {COLORS['text_primary']};
            margin-bottom: {SPACING['md']};
            font-size: {TYPOGRAPHY['h4']['size']};
        ">⚡ Quick Actions</h3>
        <p style="
            color: {COLORS['text_secondary']};
            margin-bottom: {SPACING['lg']};
        ">Jump directly to common tasks without going through the full workflow.</p>
    """, unsafe_allow_html=True)
    
    # Quick action buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if create_prominent_button(
            "📁 Upload File",
            button_type="tertiary",
            size="medium",
            key="quick_upload"
        ):
            _quick_action_upload_file()
    
    with col2:
        if create_prominent_button(
            "📋 Use Template",
            button_type="tertiary", 
            size="medium",
            key="quick_template"
        ):
            _quick_action_use_template()
    
    with col3:
        if create_prominent_button(
            "🔄 Repeat Last",
            button_type="tertiary",
            size="medium", 
            key="quick_repeat"
        ):
            _quick_action_repeat_last()
    
    with col4:
        if create_prominent_button(
            "📊 View History",
            button_type="tertiary",
            size="medium",
            key="quick_history"
        ):
            _quick_action_view_history()
    
    st.markdown("</div>", unsafe_allow_html=True)

def _render_help_section():
    """Render help and support section"""
    with st.expander("🆘 Need Help? Click here for guides and support"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **📖 Getting Started**
            - [Quick Start Guide](#)
            - [File Format Requirements](#)
            - [Template Options](#)
            - [Common Issues & Solutions](#)
            """)
        
        with col2:
            st.markdown(f"""
            **🎥 Video Tutorials**
            - [How to Upload Student Data](#)
            - [Customizing Certificates](#)
            - [Bulk Generation Tips](#)
            - [Mobile App Usage](#)
            """)
        
        st.markdown(f"""
        <div style="
            background: {COLORS['info_bg']};
            padding: {SPACING['lg']};
            border-radius: 0.5rem;
            margin-top: {SPACING['lg']};
        ">
            <p style="margin: 0; color: {COLORS['info']};">
                <strong>💬 Need personal help?</strong> Contact our support team at 
                <a href="mailto:support@safesteps.com" style="color: {COLORS['info']};">support@safesteps.com</a> 
                or use the chat widget in the bottom right corner.
            </p>
        </div>
        """, unsafe_allow_html=True)

def _start_workflow(user_id: str, mode: WorkflowMode):
    """Initialize and start a new workflow"""
    # Create new workflow ID
    workflow_id = f"workflow_{user_id}_{int(time.time())}"
    
    # Initialize workflow engine
    workflow_engine.create_workflow(
        workflow_id=workflow_id,
        user_id=user_id,
        mode=mode,
        initial_data={}
    )
    
    # Update session state
    st.session_state.active_workflow_id = workflow_id
    st.session_state.workflow_mode = mode
    st.session_state.workflow_step = 0
    st.session_state.workflow_data = {}
    st.session_state.undo_stack = []
    
    # Save workflow state
    workflow_engine.save_workflow_state(workflow_id, {
        'user_id': user_id,
        'mode': mode.value,
        'current_step': 0,
        'data': {},
        'created_at': datetime.now().isoformat(),
        'last_modified': datetime.now().isoformat()
    })
    
    st.rerun()

def _render_active_workflow(user_id: str):
    """Render the active workflow interface"""
    workflow_id = st.session_state.active_workflow_id
    mode = st.session_state.workflow_mode
    current_step = st.session_state.workflow_step
    
    # Get workflow state
    workflow_state = workflow_engine.get_workflow_state(workflow_id)
    
    if not workflow_state:
        st.error("Workflow not found. Starting fresh.")
        st.session_state.active_workflow_id = None
        st.rerun()
        return
    
    # Render workflow header with progress
    _render_workflow_header(workflow_state, mode)
    
    # Render mobile navigation if needed
    if _is_mobile_viewport():
        _render_mobile_navigation(workflow_state)
    
    # Render workflow content based on mode and step
    if mode == WorkflowMode.QUICK_GENERATE:
        _render_quick_generate_workflow(workflow_state)
    elif mode == WorkflowMode.GUIDED_MODE:
        _render_guided_mode_workflow(workflow_state)
    elif mode == WorkflowMode.ADVANCED_MODE:
        _render_advanced_mode_workflow(workflow_state)
    
    # Render workflow footer with actions
    _render_workflow_footer(workflow_state)

def _render_workflow_header(workflow_state: Dict, mode: WorkflowMode):
    """Render workflow header with progress indicator"""
    # Calculate progress
    total_steps = len(workflow_state.get('steps', []))
    current_step = workflow_state.get('current_step', 0)
    progress = (current_step / max(total_steps, 1)) * 100
    
    st.markdown(f"""
    <div style="
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 1rem;
        padding: {SPACING['lg']};
        margin-bottom: {SPACING['lg']};
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: {SPACING['md']};">
            <h2 style="
                margin: 0;
                color: {COLORS['primary']};
                font-size: {TYPOGRAPHY['h2']['size']};
            ">{mode.value.replace('_', ' ').title()}</h2>
            
            <div style="display: flex; gap: {SPACING['sm']};">
                {_render_workflow_action_buttons()}
            </div>
        </div>
        
        <div style="
            background: {COLORS['background']};
            border-radius: 0.5rem;
            height: 8px;
            overflow: hidden;
            margin-bottom: {SPACING['sm']};
        ">
            <div style="
                background: linear-gradient(90deg, {COLORS['accent']} 0%, {COLORS['accent_light']} 100%);
                height: 100%;
                width: {progress}%;
                transition: width 0.3s ease;
            "></div>
        </div>
        
        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: {TYPOGRAPHY['body_small']['size']};
            color: {COLORS['text_secondary']};
        ">
            <span>Step {current_step + 1} of {total_steps}</span>
            <span>{progress:.0f}% Complete</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_workflow_action_buttons() -> str:
    """Generate HTML for workflow action buttons"""
    return f"""
    <div style="display: flex; gap: {SPACING['xs']};">
        <button onclick="showHelp()" style="
            background: {COLORS['info']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 0.25rem;
            padding: {SPACING['xs']} {SPACING['sm']};
            font-size: {TYPOGRAPHY['body_small']['size']};
            cursor: pointer;
        ">❓</button>
        
        <button onclick="saveProgress()" style="
            background: {COLORS['success']};
            color: {COLORS['text_inverse']};
            border: none;
            border-radius: 0.25rem;
            padding: {SPACING['xs']} {SPACING['sm']};
            font-size: {TYPOGRAPHY['body_small']['size']};
            cursor: pointer;
        ">💾</button>
    </div>
    """

def _render_mobile_navigation(workflow_state: Dict):
    """Render mobile-friendly navigation"""
    if not _is_mobile_viewport():
        return
    
    # Mobile nav toggle
    nav_expanded = st.session_state.get('mobile_nav_expanded', False)
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        if create_prominent_button(
            "☰" if not nav_expanded else "✕",
            button_type="tertiary",
            size="medium",
            key="mobile_nav_toggle"
        ):
            st.session_state.mobile_nav_expanded = not nav_expanded
            st.rerun()
    
    if nav_expanded:
        with st.container():
            st.markdown("**Quick Navigation**")
            
            steps = workflow_state.get('steps', [])
            for i, step in enumerate(steps):
                if st.button(f"{i+1}. {step.get('name', 'Step')}", key=f"nav_step_{i}"):
                    st.session_state.workflow_step = i
                    st.session_state.mobile_nav_expanded = False
                    st.rerun()

def _render_quick_generate_workflow(workflow_state: Dict):
    """Render Quick Generate workflow - single page with smart defaults"""
    st.markdown(f"""
    <div style="
        background: {COLORS['success_bg']};
        border-left: 4px solid {COLORS['success']};
        padding: {SPACING['lg']};
        border-radius: 0.5rem;
        margin-bottom: {SPACING['lg']};
    ">
        <h3 style="color: {COLORS['success']}; margin-bottom: {SPACING['sm']};">⚡ Quick Generate Mode</h3>
        <p style="margin: 0; color: {COLORS['text_secondary']};">
            Upload your student data and we'll handle the rest with smart defaults. Perfect for recurring certificate generation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Single form with all essential fields
    with st.form("quick_generate_form", clear_on_submit=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # File upload with drag & drop
            st.markdown("**📁 Upload Student Data**")
            uploaded_file = st.file_uploader(
                "Choose CSV or Excel file",
                type=['csv', 'xlsx'],
                help="Upload a file with student names and scores",
                label_visibility="collapsed"
            )
            
            if uploaded_file:
                # Quick preview
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    st.success(f"✅ File loaded: {len(df)} students found")
                    
                    # Smart column detection
                    detected_columns = _detect_columns(df)
                    if detected_columns:
                        st.info(f"🎯 Detected columns: {', '.join(detected_columns.keys())}")
                    
                    # Quick preview
                    with st.expander("📋 Preview data (first 5 rows)"):
                        st.dataframe(df.head(), use_container_width=True)
                        
                except Exception as e:
                    st.error(f"❌ Error reading file: {str(e)}")
        
        with col2:
            # Smart defaults with minimal options
            st.markdown("**🎯 Quick Options**")
            
            # Course selection with smart suggestion
            course_manager = CourseManager()
            courses = course_manager.get_all_courses()
            
            if courses:
                # Suggest most recently used course
                suggested_course = _get_suggested_course(st.session_state.get('user_id'))
                default_index = 0
                if suggested_course:
                    try:
                        default_index = courses.index(suggested_course)
                    except ValueError:
                        pass
                
                selected_course = st.selectbox(
                    "Course",
                    courses,
                    index=default_index,
                    help="Select the course for certificates"
                )
            else:
                selected_course = st.text_input(
                    "Course Name",
                    value="Vapes and Vaping",
                    help="Enter the course name"
                )
            
            # Auto-pass option
            auto_pass = st.checkbox(
                "Auto-pass all students",
                value=True,
                help="Mark all students as passed automatically"
            )
            
            # Generate button
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button(
                "🚀 Generate Certificates",
                use_container_width=True,
                type="primary"
            )
            
            if submitted and uploaded_file:
                _process_quick_generate(uploaded_file, selected_course, auto_pass)

def _render_guided_mode_workflow(workflow_state: Dict):
    """Render Guided Mode workflow - step by step with help"""
    current_step = workflow_state.get('current_step', 0)
    steps = workflow_state.get('steps', [])
    
    if not steps:
        # Initialize guided mode steps
        steps = [
            {'name': 'Upload Data', 'description': 'Upload your student data file'},
            {'name': 'Verify Data', 'description': 'Review and validate the data'},
            {'name': 'Configure Options', 'description': 'Set certificate options'},
            {'name': 'Preview', 'description': 'Preview sample certificates'},
            {'name': 'Generate', 'description': 'Generate all certificates'}
        ]
        workflow_state['steps'] = steps
    
    # Step indicator
    _render_step_indicator(steps, current_step)
    
    # Current step content
    if current_step == 0:
        _render_guided_upload_step()
    elif current_step == 1:
        _render_guided_verify_step()
    elif current_step == 2:
        _render_guided_configure_step()
    elif current_step == 3:
        _render_guided_preview_step()
    elif current_step == 4:
        _render_guided_generate_step()
    
    # Navigation buttons
    _render_guided_navigation(current_step, len(steps))

def _render_advanced_mode_workflow(workflow_state: Dict):
    """Render Advanced Mode workflow - all options visible"""
    st.markdown(f"""
    <div style="
        background: {COLORS['warning_bg']};
        border-left: 4px solid {COLORS['warning']};
        padding: {SPACING['lg']};
        border-radius: 0.5rem;
        margin-bottom: {SPACING['lg']};
    ">
        <h3 style="color: {COLORS['warning']}; margin-bottom: {SPACING['sm']};">🔧 Advanced Mode</h3>
        <p style="margin: 0; color: {COLORS['text_secondary']};">
            Full control over all certificate generation options. Bulk operations and custom templates available.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabbed interface for organization
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Data", "🎨 Design", "⚙️ Options", "🚀 Generate"])
    
    with tab1:
        _render_advanced_data_tab()
    
    with tab2:
        _render_advanced_design_tab()
    
    with tab3:
        _render_advanced_options_tab()
    
    with tab4:
        _render_advanced_generate_tab()

def _render_workflow_footer(workflow_state: Dict):
    """Render workflow footer with save/exit actions"""
    st.markdown(f"""
    <div style="
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: 0.5rem;
        padding: {SPACING['lg']};
        margin-top: {SPACING['xl']};
    ">
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        if create_prominent_button(
            "💾 Save Progress",
            button_type="tertiary",
            size="medium",
            key="save_progress"
        ):
            _save_workflow_progress()
    
    with col2:
        if create_prominent_button(
            "↶ Undo",
            button_type="tertiary",
            size="medium",
            key="undo_action",
            disabled=len(st.session_state.get('undo_stack', [])) == 0
        ):
            _undo_last_action()
    
    with col3:
        if create_prominent_button(
            "🆘 Help",
            button_type="tertiary",
            size="medium",
            key="show_help"
        ):
            st.session_state.help_visible = not st.session_state.get('help_visible', False)
            st.rerun()
    
    with col4:
        if create_prominent_button(
            "❌ Exit",
            button_type="secondary",
            size="medium",
            key="exit_workflow"
        ):
            _exit_workflow_with_confirmation()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Show help panel if toggled
    if st.session_state.get('help_visible', False):
        _render_contextual_help(workflow_state)

# Helper functions for workflow operations

def _detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Detect likely column mappings in uploaded data"""
    columns = df.columns.str.lower()
    detected = {}
    
    # Common patterns for different column types
    name_patterns = ['name', 'student', 'full_name', 'firstname', 'last_name']
    score_patterns = ['score', 'grade', 'result', 'mark', 'percentage']
    email_patterns = ['email', 'mail', 'address']
    
    for col in columns:
        original_col = df.columns[columns.get_loc(col)]
        
        if any(pattern in col for pattern in name_patterns):
            detected['name'] = original_col
        elif any(pattern in col for pattern in score_patterns):
            detected['score'] = original_col
        elif any(pattern in col for pattern in email_patterns):
            detected['email'] = original_col
    
    return detected

def _get_suggested_course(user_id: str) -> Optional[str]:
    """Get most recently used course for user"""
    user_stats = workflow_engine.get_user_statistics(user_id)
    if user_stats and 'recent_courses' in user_stats:
        return user_stats['recent_courses'][0] if user_stats['recent_courses'] else None
    return None

def _is_mobile_viewport() -> bool:
    """Detect if current viewport is mobile-sized"""
    # This would typically use JavaScript in a real app
    # For Streamlit, we can use container width detection or user agent
    return st.session_state.get('is_mobile', False)

def _process_quick_generate(uploaded_file, course: str, auto_pass: bool):
    """Process quick generate certificate creation"""
    try:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validate data
        validator = SpreadsheetValidator()
        validation_result = validator.validate_spreadsheet(df)
        
        if not validation_result.is_valid:
            st.error(f"❌ Data validation failed: {validation_result.errors}")
            return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Generate certificates
        generator = CertificateGenerator()
        results = []
        
        for i, row in df.iterrows():
            progress = (i + 1) / len(df)
            progress_bar.progress(progress)
            status_text.text(f"Generating certificate {i+1} of {len(df)}...")
            
            # Use auto-pass or actual score
            score = "Pass" if auto_pass else row.get('score', 'Pass')
            
            try:
                cert_path = generator.generate_certificate_for_app(
                    student_name=row.get('name', row.get('student', 'Student')),
                    course_name=course,
                    score=score,
                    date=datetime.now().strftime("%Y-%m-%d")
                )
                results.append({'student': row.get('name'), 'status': 'Success', 'path': cert_path})
            except Exception as e:
                results.append({'student': row.get('name'), 'status': 'Error', 'error': str(e)})
        
        # Show results
        success_count = len([r for r in results if r['status'] == 'Success'])
        error_count = len(results) - success_count
        
        if error_count == 0:
            st.success(f"🎉 Successfully generated {success_count} certificates!")
        else:
            st.warning(f"⚠️ Generated {success_count} certificates with {error_count} errors")
        
        # Provide download options
        _render_certificate_results(results)
        
    except Exception as e:
        st.error(f"❌ Error processing certificates: {str(e)}")

def _render_certificate_results(results: List[Dict]):
    """Render certificate generation results with download options"""
    st.markdown("### 📋 Generation Results")
    
    # Results summary
    col1, col2, col3 = st.columns(3)
    
    success_count = len([r for r in results if r['status'] == 'Success'])
    error_count = len([r for r in results if r['status'] == 'Error'])
    total_count = len(results)
    
    with col1:
        st.metric("✅ Successful", success_count)
    
    with col2:
        st.metric("❌ Errors", error_count)
    
    with col3:
        st.metric("📊 Total", total_count)
    
    # Detailed results
    if results:
        results_df = pd.DataFrame(results)
        st.dataframe(results_df, use_container_width=True)
        
        # Download options
        if success_count > 0:
            st.markdown("### 📥 Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if create_prominent_button(
                    "📦 Download All (ZIP)",
                    button_type="primary",
                    size="medium",
                    key="download_zip"
                ):
                    _create_download_zip(results)
            
            with col2:
                if create_prominent_button(
                    "📧 Email Results",
                    button_type="secondary",
                    size="medium",
                    key="email_results"
                ):
                    _email_certificates(results)

# Additional helper functions for workflow steps

def _render_step_indicator(steps: List[Dict], current_step: int):
    """Render visual step indicator for guided mode"""
    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: {SPACING['xl']};
        padding: {SPACING['lg']};
        background: {COLORS['surface']};
        border-radius: 0.5rem;
    ">
    """, unsafe_allow_html=True)
    
    for i, step in enumerate(steps):
        # Step circle
        if i < current_step:
            circle_color = COLORS['success']
            circle_icon = "✓"
        elif i == current_step:
            circle_color = COLORS['primary']
            circle_icon = str(i + 1)
        else:
            circle_color = COLORS['border']
            circle_icon = str(i + 1)
        
        # Connection line (except for last step)
        line_html = ""
        if i < len(steps) - 1:
            line_color = COLORS['success'] if i < current_step else COLORS['border']
            line_html = f"""
            <div style="
                flex: 1;
                height: 2px;
                background: {line_color};
                margin: 0 {SPACING['sm']};
            "></div>
            """
        
        step_html = f"""
        <div style="text-align: center;">
            <div style="
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: {circle_color};
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                margin-bottom: {SPACING['xs']};
            ">{circle_icon}</div>
            <div style="
                font-size: {TYPOGRAPHY['body_small']['size']};
                color: {'#333' if i <= current_step else COLORS['text_muted']};
                font-weight: {'600' if i == current_step else '400'};
            ">{step['name']}</div>
        </div>
        {line_html}
        """
        
        st.markdown(step_html, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def _save_workflow_progress():
    """Save current workflow progress"""
    if st.session_state.active_workflow_id:
        workflow_engine.save_workflow_state(
            st.session_state.active_workflow_id,
            {
                'current_step': st.session_state.workflow_step,
                'data': st.session_state.workflow_data,
                'last_modified': datetime.now().isoformat()
            }
        )
        st.success("💾 Progress saved!")

def _undo_last_action():
    """Undo the last workflow action"""
    undo_stack = st.session_state.get('undo_stack', [])
    if undo_stack:
        last_state = undo_stack.pop()
        st.session_state.workflow_step = last_state.get('step', 0)
        st.session_state.workflow_data = last_state.get('data', {})
        st.success("↶ Action undone!")
        st.rerun()

def _exit_workflow_with_confirmation():
    """Exit workflow with save confirmation"""
    if st.session_state.get('workflow_data'):
        # Show confirmation dialog
        st.warning("⚠️ You have unsaved changes. Do you want to save before exiting?")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save & Exit"):
                _save_workflow_progress()
                _exit_workflow()
        
        with col2:
            if st.button("❌ Exit Without Saving"):
                _exit_workflow()
        
        with col3:
            if st.button("📝 Continue Working"):
                st.rerun()
    else:
        _exit_workflow()

def _exit_workflow():
    """Clean exit from workflow"""
    # Clear session state
    for key in ['active_workflow_id', 'workflow_mode', 'workflow_step', 'workflow_data']:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()

def _render_contextual_help(workflow_state: Dict):
    """Render contextual help panel"""
    mode = workflow_state.get('mode', 'unknown')
    current_step = workflow_state.get('current_step', 0)
    
    with st.container():
        st.markdown(f"""
        <div style="
            background: {COLORS['info_bg']};
            border: 1px solid {COLORS['info']};
            border-radius: 0.5rem;
            padding: {SPACING['lg']};
            margin-top: {SPACING['lg']};
        ">
            <h4 style="color: {COLORS['info']}; margin-bottom: {SPACING['md']};">🆘 Context-Sensitive Help</h4>
        """, unsafe_allow_html=True)
        
        # Mode-specific help
        if mode == 'quick_generate':
            st.markdown("""
            **Quick Generate Help:**
            - Upload CSV/Excel with student names and scores
            - File should have columns: 'name', 'score' (optional)
            - System will auto-detect column names
            - All students marked as 'Pass' by default
            """)
        elif mode == 'guided_mode':
            st.markdown(f"""
            **Guided Mode Help - Step {current_step + 1}:**
            - Follow the step-by-step process
            - Each step validates your input before proceeding
            - You can go back to previous steps anytime
            - Progress is automatically saved
            """)
        elif mode == 'advanced_mode':
            st.markdown("""
            **Advanced Mode Help:**
            - Full control over all certificate options
            - Bulk operations available
            - Custom template support
            - Advanced validation rules
            """)
        
        # Common keyboard shortcuts
        st.markdown("""
        **Keyboard Shortcuts:**
        - `Ctrl+S`: Save progress
        - `Ctrl+Z`: Undo last action
        - `Esc`: Exit workflow
        - `F1`: Toggle this help panel
        """)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Quick action implementations
def _quick_action_upload_file():
    """Quick action: Direct file upload"""
    st.session_state.quick_action = 'upload'
    _start_workflow(st.session_state.get('user_id', 'anonymous'), WorkflowMode.QUICK_GENERATE)

def _quick_action_use_template():
    """Quick action: Use existing template"""
    st.session_state.quick_action = 'template'
    _start_workflow(st.session_state.get('user_id', 'anonymous'), WorkflowMode.GUIDED_MODE)

def _quick_action_repeat_last():
    """Quick action: Repeat last generation"""
    # Implementation would load last workflow settings
    st.info("🔄 Repeating last certificate generation...")

def _quick_action_view_history():
    """Quick action: View generation history"""
    st.switch_page("pages/Certificate_History.py")

# Placeholder implementations for guided mode steps
def _render_guided_upload_step():
    """Render guided mode upload step"""
    st.markdown("### 📁 Step 1: Upload Your Data")
    # Implementation details...

def _render_guided_verify_step():
    """Render guided mode verification step"""
    st.markdown("### ✅ Step 2: Verify Your Data")
    # Implementation details...

def _render_guided_configure_step():
    """Render guided mode configuration step"""
    st.markdown("### ⚙️ Step 3: Configure Options")
    # Implementation details...

def _render_guided_preview_step():
    """Render guided mode preview step"""
    st.markdown("### 👀 Step 4: Preview Certificates")
    # Implementation details...

def _render_guided_generate_step():
    """Render guided mode generation step"""
    st.markdown("### 🚀 Step 5: Generate Certificates")
    # Implementation details...

def _render_guided_navigation(current_step: int, total_steps: int):
    """Render navigation for guided mode"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_step > 0:
            if create_prominent_button(
                "← Previous",
                button_type="secondary",
                size="medium",
                key="prev_step"
            ):
                st.session_state.workflow_step = current_step - 1
                st.rerun()
    
    with col3:
        if current_step < total_steps - 1:
            if create_prominent_button(
                "Next →",
                button_type="primary",
                size="medium",
                key="next_step"
            ):
                st.session_state.workflow_step = current_step + 1
                st.rerun()

# Placeholder implementations for advanced mode tabs
def _render_advanced_data_tab():
    """Render advanced mode data management tab"""
    st.markdown("Advanced data management options...")

def _render_advanced_design_tab():
    """Render advanced mode design customization tab"""
    st.markdown("Advanced design customization options...")

def _render_advanced_options_tab():
    """Render advanced mode options tab"""
    st.markdown("Advanced configuration options...")

def _render_advanced_generate_tab():
    """Render advanced mode generation tab"""
    st.markdown("Advanced generation options...")

def _create_download_zip(results: List[Dict]):
    """Create ZIP file for download"""
    # Implementation would create ZIP of certificate files
    st.info("📦 Creating ZIP file...")

def _email_certificates(results: List[Dict]):
    """Email certificates to recipients"""
    # Implementation would handle email sending
    st.info("📧 Preparing emails...")

# Main page entry point
if __name__ == "__main__":
    user_workflow_page()