"""
UI Helper Functions for SafeSteps
Navigation and state management utilities for the enhanced UI system
"""
import streamlit as st
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

def get_greeting():
    """Get time-appropriate greeting"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Good evening"

def manage_navigation_state(version: str = "v1", page: str = "dashboard"):
    """Manage navigation state across the application"""
    if 'nav_state' not in st.session_state:
        st.session_state.nav_state = {
            'current_version': version,
            'current_page': page,
            'navigation_history': [],
            'breadcrumbs': []
        }
    
    return st.session_state.nav_state

def update_navigation(version: str, page: str, breadcrumbs: List[Dict[str, str]] = None):
    """Update navigation state and history"""
    nav_state = manage_navigation_state()
    
    # Add to history if it's a different page
    if nav_state['current_page'] != page:
        nav_state['navigation_history'].append({
            'version': nav_state['current_version'],
            'page': nav_state['current_page'],
            'timestamp': datetime.now().isoformat()
        })
    
    # Update current state
    nav_state['current_version'] = version
    nav_state['current_page'] = page
    
    if breadcrumbs:
        nav_state['breadcrumbs'] = breadcrumbs

def get_navigation_breadcrumbs():
    """Get current breadcrumbs for display"""
    nav_state = manage_navigation_state()
    return nav_state.get('breadcrumbs', [])

def manage_workflow_state(workflow_id: str, initial_state: Dict[str, Any] = None):
    """Manage workflow state with save/resume capabilities"""
    workflow_key = f"workflow_{workflow_id}"
    
    if workflow_key not in st.session_state:
        st.session_state[workflow_key] = initial_state or {
            'current_step': 1,
            'completed_steps': [],
            'form_data': {},
            'validation_results': {},
            'last_saved': None
        }
    
    return st.session_state[workflow_key]

def save_workflow_state(workflow_id: str, state: Dict[str, Any]):
    """Save workflow state with timestamp"""
    workflow_key = f"workflow_{workflow_id}"
    state['last_saved'] = datetime.now().isoformat()
    st.session_state[workflow_key] = state
    
    # Also save to persistent storage if needed
    saved_workflows_key = "saved_workflows"
    if saved_workflows_key not in st.session_state:
        st.session_state[saved_workflows_key] = {}
    
    st.session_state[saved_workflows_key][workflow_id] = state.copy()

def load_workflow_state(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Load saved workflow state"""
    saved_workflows_key = "saved_workflows"
    if saved_workflows_key in st.session_state:
        return st.session_state[saved_workflows_key].get(workflow_id)
    return None

def clear_workflow_state(workflow_id: str):
    """Clear workflow state"""
    workflow_key = f"workflow_{workflow_id}"
    if workflow_key in st.session_state:
        del st.session_state[workflow_key]

def manage_user_preferences():
    """Manage user UI preferences"""
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'preferred_version': 'v1',
            'theme': 'light',
            'show_tutorials': True,
            'sidebar_collapsed': False,
            'dashboard_layout': 'grid',
            'table_page_size': 10,
            'auto_save': True
        }
    
    return st.session_state.user_preferences

def update_user_preference(key: str, value: Any):
    """Update a single user preference"""
    prefs = manage_user_preferences()
    prefs[key] = value

def get_user_preference(key: str, default: Any = None):
    """Get a user preference value"""
    prefs = manage_user_preferences()
    return prefs.get(key, default)

def create_keyboard_shortcuts_handler():
    """Handle keyboard shortcuts (simulated with session state)"""
    shortcuts = {
        'ctrl+1': {'action': 'navigate_dashboard', 'description': 'Go to Dashboard'},
        'ctrl+2': {'action': 'navigate_generate', 'description': 'Go to Certificate Generation'},
        'ctrl+3': {'action': 'navigate_admin', 'description': 'Go to Admin Panel'},
        'ctrl+s': {'action': 'save_current', 'description': 'Save Current State'},
        'ctrl+h': {'action': 'show_help', 'description': 'Show Help'},
        'esc': {'action': 'close_modal', 'description': 'Close Modal/Dialog'}
    }
    
    return shortcuts

def handle_keyboard_shortcut(shortcut: str):
    """Handle keyboard shortcut actions"""
    shortcuts = create_keyboard_shortcuts_handler()
    
    if shortcut in shortcuts:
        action = shortcuts[shortcut]['action']
        
        if action == 'navigate_dashboard':
            update_navigation('current', 'dashboard')
        elif action == 'navigate_generate':
            update_navigation('current', 'generate')
        elif action == 'navigate_admin':
            update_navigation('current', 'admin')
        elif action == 'save_current':
            # Trigger save for current workflow
            st.session_state['trigger_save'] = True
        elif action == 'show_help':
            st.session_state['show_help_modal'] = True
        elif action == 'close_modal':
            # Close any open modals
            for key in ['show_help_modal', 'show_tutorial_modal']:
                if key in st.session_state:
                    st.session_state[key] = False

def create_responsive_layout(mobile_breakpoint: int = 768):
    """Create responsive layout utilities"""
    # Simulate responsive behavior with session state
    if 'layout_info' not in st.session_state:
        st.session_state.layout_info = {
            'is_mobile': False,
            'screen_width': 1200,  # Default desktop width
            'columns': 3
        }
    
    layout = st.session_state.layout_info
    
    # Adjust columns based on simulated screen width
    if layout['screen_width'] < mobile_breakpoint:
        layout['is_mobile'] = True
        layout['columns'] = 1
    elif layout['screen_width'] < 1024:
        layout['is_mobile'] = False
        layout['columns'] = 2
    else:
        layout['is_mobile'] = False
        layout['columns'] = 3
    
    return layout

def manage_tutorial_state(tutorial_id: str):
    """Manage tutorial progression state"""
    tutorial_key = f"tutorial_{tutorial_id}"
    
    if tutorial_key not in st.session_state:
        st.session_state[tutorial_key] = {
            'current_step': 1,
            'completed_steps': [],
            'skipped': False,
            'started_at': datetime.now().isoformat(),
            'completed_at': None
        }
    
    return st.session_state[tutorial_key]

def advance_tutorial_step(tutorial_id: str):
    """Advance tutorial to next step"""
    tutorial_state = manage_tutorial_state(tutorial_id)
    tutorial_state['completed_steps'].append(tutorial_state['current_step'])
    tutorial_state['current_step'] += 1

def complete_tutorial(tutorial_id: str):
    """Mark tutorial as completed"""
    tutorial_state = manage_tutorial_state(tutorial_id)
    tutorial_state['completed_at'] = datetime.now().isoformat()

def skip_tutorial(tutorial_id: str):
    """Mark tutorial as skipped"""
    tutorial_state = manage_tutorial_state(tutorial_id)
    tutorial_state['skipped'] = True
    tutorial_state['completed_at'] = datetime.now().isoformat()

def is_tutorial_completed(tutorial_id: str) -> bool:
    """Check if tutorial is completed or skipped"""
    tutorial_state = manage_tutorial_state(tutorial_id)
    return tutorial_state.get('completed_at') is not None

def manage_form_validation_state(form_id: str):
    """Manage form validation state"""
    validation_key = f"validation_{form_id}"
    
    if validation_key not in st.session_state:
        st.session_state[validation_key] = {
            'field_validations': {},
            'form_valid': False,
            'last_validated': None,
            'error_messages': []
        }
    
    return st.session_state[validation_key]

def validate_form_field(form_id: str, field_name: str, value: Any, validator_func: callable):
    """Validate a single form field"""
    validation_state = manage_form_validation_state(form_id)
    
    try:
        is_valid = validator_func(value)
        validation_state['field_validations'][field_name] = {
            'valid': is_valid,
            'value': value,
            'error': None if is_valid else f"Invalid {field_name}"
        }
    except Exception as e:
        validation_state['field_validations'][field_name] = {
            'valid': False,
            'value': value,
            'error': str(e)
        }
    
    # Update overall form validity
    validation_state['form_valid'] = all(
        field['valid'] for field in validation_state['field_validations'].values()
    )
    validation_state['last_validated'] = datetime.now().isoformat()
    
    return validation_state['field_validations'][field_name]['valid']

def get_form_validation_errors(form_id: str) -> List[str]:
    """Get all validation errors for a form"""
    validation_state = manage_form_validation_state(form_id)
    
    errors = []
    for field_name, field_validation in validation_state['field_validations'].items():
        if not field_validation['valid'] and field_validation['error']:
            errors.append(field_validation['error'])
    
    return errors

def create_version_selector():
    """Create version selector for switching between UI versions"""
    versions = {
        'v1': {
            'name': 'Streamlined Efficiency',
            'description': 'Power user interface with consolidated views',
            'icon': '⚡',
            'target_users': 'Power Users, Frequent Admin Users'
        },
        'v2': {
            'name': 'User-Friendly Guidance',
            'description': 'Guided interface with tutorials and help',
            'icon': '🎓',
            'target_users': 'Beginners, Occasional Users'
        },
        'v3': {
            'name': 'Modern Dashboard',
            'description': 'Visual interface with modern design',
            'icon': '🎨',
            'target_users': 'Users Who Value Visual Appeal'
        }
    }
    
    current_version = get_user_preference('preferred_version', 'v1')
    
    with st.sidebar:
        st.divider()
        st.subheader("🔧 Interface Version")
        
        version_options = [f"{v['icon']} {v['name']}" for v in versions.values()]
        version_keys = list(versions.keys())
        
        current_index = version_keys.index(current_version) if current_version in version_keys else 0
        
        selected_option = st.selectbox(
            "Choose Interface Style",
            version_options,
            index=current_index,
            help="Select the interface style that best fits your needs"
        )
        
        # Get selected version key
        selected_index = version_options.index(selected_option)
        selected_version = version_keys[selected_index]
        
        if selected_version != current_version:
            update_user_preference('preferred_version', selected_version)
            st.rerun()
        
        # Show version info
        version_info = versions[selected_version]
        with st.expander("ℹ️ About This Version", expanded=False):
            st.markdown(f"**Target Users:** {version_info['target_users']}")
            st.markdown(f"**Description:** {version_info['description']}")
    
    return selected_version, versions[selected_version]

def create_mobile_detection():
    """Create mobile device detection (simulated)"""
    # In a real app, this would use JavaScript to detect screen size
    # For now, we'll use a toggle in the sidebar for testing
    with st.sidebar:
        st.divider()
        mobile_mode = st.toggle("📱 Mobile View", value=get_user_preference('mobile_mode', False))
        update_user_preference('mobile_mode', mobile_mode)
        
        if mobile_mode:
            st.session_state.layout_info = {
                'is_mobile': True,
                'screen_width': 375,
                'columns': 1
            }
        else:
            st.session_state.layout_info = {
                'is_mobile': False,
                'screen_width': 1200,
                'columns': 3
            }
    
    return mobile_mode