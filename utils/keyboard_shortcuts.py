"""
Keyboard Shortcuts System for SafeSteps
Provides keyboard navigation and shortcuts for power users
"""
import streamlit as st
from typing import Dict, List, Callable, Any

class KeyboardShortcutManager:
    """Manages keyboard shortcuts for the application"""
    
    def __init__(self):
        self.shortcuts = {}
        self._initialize_default_shortcuts()
    
    def _initialize_default_shortcuts(self):
        """Initialize default keyboard shortcuts"""
        self.shortcuts = {
            # Navigation shortcuts
            'ctrl+1': {
                'action': 'navigate_dashboard',
                'description': 'Go to Dashboard',
                'category': 'Navigation',
                'callback': lambda: self._navigate_to('dashboard')
            },
            'ctrl+2': {
                'action': 'navigate_generate',
                'description': 'Go to Certificate Generation',
                'category': 'Navigation',
                'callback': lambda: self._navigate_to('generate')
            },
            'ctrl+3': {
                'action': 'navigate_admin',
                'description': 'Go to Admin Panel',
                'category': 'Navigation',
                'callback': lambda: self._navigate_to('admin')
            },
            'ctrl+4': {
                'action': 'navigate_users',
                'description': 'Go to User Management',
                'category': 'Navigation',
                'callback': lambda: self._navigate_to('users')
            },
            'ctrl+5': {
                'action': 'navigate_templates',
                'description': 'Go to Template Management',
                'category': 'Navigation',
                'callback': lambda: self._navigate_to('templates')
            },
            
            # Action shortcuts
            'ctrl+s': {
                'action': 'save_current',
                'description': 'Save Current State',
                'category': 'Actions',
                'callback': lambda: self._save_current_state()
            },
            'ctrl+n': {
                'action': 'new_item',
                'description': 'Create New Item',
                'category': 'Actions',
                'callback': lambda: self._create_new_item()
            },
            'ctrl+f': {
                'action': 'search',
                'description': 'Focus Search Box',
                'category': 'Actions',
                'callback': lambda: self._focus_search()
            },
            'ctrl+r': {
                'action': 'refresh',
                'description': 'Refresh Current View',
                'category': 'Actions',
                'callback': lambda: st.rerun()
            },
            
            # Help and utilities
            'ctrl+h': {
                'action': 'show_help',
                'description': 'Show Help Dialog',
                'category': 'Help',
                'callback': lambda: self._show_help()
            },
            'ctrl+shift+k': {
                'action': 'show_shortcuts',
                'description': 'Show Keyboard Shortcuts',
                'category': 'Help',
                'callback': lambda: self._show_shortcuts_modal()
            },
            'esc': {
                'action': 'close_modal',
                'description': 'Close Modal/Dialog',
                'category': 'Interface',
                'callback': lambda: self._close_modals()
            },
            
            # Workflow shortcuts
            'alt+1': {
                'action': 'workflow_step_1',
                'description': 'Go to Upload Step',
                'category': 'Workflow',
                'callback': lambda: self._set_workflow_step(1)
            },
            'alt+2': {
                'action': 'workflow_step_2',
                'description': 'Go to Validation Step',
                'category': 'Workflow',
                'callback': lambda: self._set_workflow_step(2)
            },
            'alt+3': {
                'action': 'workflow_step_3',
                'description': 'Go to Template Step',
                'category': 'Workflow',
                'callback': lambda: self._set_workflow_step(3)
            },
            'alt+4': {
                'action': 'workflow_step_4',
                'description': 'Go to Generation Step',
                'category': 'Workflow',
                'callback': lambda: self._set_workflow_step(4)
            },
            'alt+5': {
                'action': 'workflow_step_5',
                'description': 'Go to Complete Step',
                'category': 'Workflow',
                'callback': lambda: self._set_workflow_step(5)
            },
        }
    
    def register_shortcut(self, key_combination: str, action: str, description: str, 
                         category: str, callback: Callable):
        """Register a new keyboard shortcut"""
        self.shortcuts[key_combination] = {
            'action': action,
            'description': description,
            'category': category,
            'callback': callback
        }
    
    def handle_shortcut(self, key_combination: str):
        """Handle a keyboard shortcut"""
        if key_combination in self.shortcuts:
            try:
                self.shortcuts[key_combination]['callback']()
                return True
            except Exception as e:
                st.error(f"Error executing shortcut {key_combination}: {str(e)}")
                return False
        return False
    
    def get_shortcuts_by_category(self) -> Dict[str, List[Dict[str, str]]]:
        """Get shortcuts grouped by category"""
        categories = {}
        for key, shortcut in self.shortcuts.items():
            category = shortcut['category']
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'key': key,
                'description': shortcut['description'],
                'action': shortcut['action']
            })
        return categories
    
    def _navigate_to(self, page: str):
        """Navigate to a specific page"""
        st.session_state['navigation_target'] = page
        st.rerun()
    
    def _save_current_state(self):
        """Save current application state"""
        st.session_state['trigger_save'] = True
        # Show brief confirmation
        st.toast("State saved!", icon="💾")
    
    def _create_new_item(self):
        """Trigger create new item action"""
        st.session_state['trigger_new_item'] = True
    
    def _focus_search(self):
        """Focus on search input"""
        st.session_state['focus_search'] = True
    
    def _show_help(self):
        """Show help dialog"""
        st.session_state['show_help_modal'] = True
    
    def _show_shortcuts_modal(self):
        """Show keyboard shortcuts modal"""
        st.session_state['show_shortcuts_modal'] = True
    
    def _close_modals(self):
        """Close all open modals"""
        modal_keys = [
            'show_help_modal',
            'show_shortcuts_modal',
            'show_tutorial_modal',
            'show_confirmation_modal'
        ]
        for key in modal_keys:
            if key in st.session_state:
                st.session_state[key] = False
    
    def _set_workflow_step(self, step: int):
        """Set current workflow step"""
        st.session_state['current_workflow_step'] = step
        st.rerun()

# Global instance
keyboard_manager = KeyboardShortcutManager()

def create_shortcut_display():
    """Create a display of available keyboard shortcuts"""
    categories = keyboard_manager.get_shortcuts_by_category()
    
    with st.expander("⌨️ Keyboard Shortcuts", expanded=False):
        for category, shortcuts in categories.items():
            st.subheader(f"{category} Shortcuts")
            
            for shortcut in shortcuts:
                col1, col2 = st.columns([1, 2])
                with col1:
                    # Format key combination for display
                    key_display = shortcut['key'].replace('ctrl', 'Ctrl').replace('alt', 'Alt').replace('shift', 'Shift')
                    st.code(key_display)
                with col2:
                    st.text(shortcut['description'])
            
            st.divider()

def create_shortcuts_modal():
    """Create a modal dialog showing keyboard shortcuts"""
    if st.session_state.get('show_shortcuts_modal', False):
        categories = keyboard_manager.get_shortcuts_by_category()
        
        with st.container(border=True):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.subheader("⌨️ Keyboard Shortcuts")
                
                for category, shortcuts in categories.items():
                    st.markdown(f"**{category}**")
                    
                    for shortcut in shortcuts:
                        key_display = shortcut['key'].replace('ctrl', 'Ctrl').replace('alt', 'Alt').replace('shift', 'Shift')
                        st.markdown(f"`{key_display}` - {shortcut['description']}")
                    
                    st.markdown("")
                
                if st.button("Close", key="close_shortcuts_modal", use_container_width=True):
                    st.session_state['show_shortcuts_modal'] = False
                    st.rerun()

def handle_keyboard_input():
    """Handle keyboard input from session state"""
    # Check for keyboard shortcut triggers in session state
    shortcut_triggers = [
        'trigger_save',
        'trigger_new_item',
        'focus_search',
        'navigation_target'
    ]
    
    for trigger in shortcut_triggers:
        if st.session_state.get(trigger):
            # Handle the trigger
            if trigger == 'trigger_save':
                # Implement save logic
                pass
            elif trigger == 'trigger_new_item':
                # Implement new item logic
                pass
            elif trigger == 'focus_search':
                # Implement search focus logic
                pass
            elif trigger == 'navigation_target':
                # Handle navigation
                target = st.session_state[trigger]
                # Implementation depends on app structure
                pass
            
            # Clear the trigger
            del st.session_state[trigger]

def create_shortcut_hint(shortcut_key: str, description: str):
    """Create a small hint showing available shortcut"""
    key_display = shortcut_key.replace('ctrl', 'Ctrl').replace('alt', 'Alt').replace('shift', 'Shift')
    st.caption(f"💡 Tip: Press `{key_display}` to {description.lower()}")

def register_page_shortcuts(page_shortcuts: Dict[str, Dict[str, Any]]):
    """Register page-specific shortcuts"""
    for key, shortcut_config in page_shortcuts.items():
        keyboard_manager.register_shortcut(
            key,
            shortcut_config['action'],
            shortcut_config['description'],
            shortcut_config.get('category', 'Page'),
            shortcut_config['callback']
        )