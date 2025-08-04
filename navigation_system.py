"""
SafeSteps Navigation System Implementation
Task-Oriented Information Architecture with Mobile-First Design

This module implements the consolidated navigation system that reduces
8 admin pages to 3 task-oriented areas: WORK, MANAGE, MONITOR
"""

import streamlit as st
from typing import Dict, List, Optional, Tuple
from enum import Enum
import json

class NavigationArea(Enum):
    """Primary navigation areas aligned with user tasks"""
    WORK = "work"          # Certificate Generation & Management
    MANAGE = "manage"      # Templates, Courses, Users
    MONITOR = "monitor"    # Analytics, Settings, System

class NavigationState:
    """Manages navigation state and URL routing"""
    
    def __init__(self):
        if 'navigation_state' not in st.session_state:
            st.session_state.navigation_state = {
                'current_area': NavigationArea.WORK.value,
                'current_tab': 'generate',
                'breadcrumb': ['SafeSteps', 'WORK', 'Generate'],
                'quick_actions': ['generate_certificate'],
                'is_mobile': self._detect_mobile(),
                'show_sidebar': True,
                'navigation_history': []
            }
    
    def _detect_mobile(self) -> bool:
        """Detect mobile device based on viewport width"""
        # In Streamlit, we use CSS media queries for responsive design
        # This is a placeholder for server-side mobile detection
        return False
    
    def get_current_area(self) -> str:
        """Get current navigation area"""
        return st.session_state.navigation_state['current_area']
    
    def get_current_tab(self) -> str:
        """Get current tab within area"""
        return st.session_state.navigation_state['current_tab']
    
    def set_navigation(self, area: str, tab: str = None) -> None:
        """Update navigation state and breadcrumb"""
        st.session_state.navigation_state['current_area'] = area
        if tab:
            st.session_state.navigation_state['current_tab'] = tab
        
        # Update breadcrumb
        area_name = area.upper()
        tab_name = tab.title() if tab else ""
        st.session_state.navigation_state['breadcrumb'] = [
            'SafeSteps', area_name, tab_name
        ] if tab else ['SafeSteps', area_name]
        
        # Add to navigation history
        history = st.session_state.navigation_state['navigation_history']
        current_location = f"{area}/{tab}" if tab else area
        if not history or history[-1] != current_location:
            history.append(current_location)
            # Keep only last 10 locations
            st.session_state.navigation_state['navigation_history'] = history[-10:]

class NavigationRenderer:
    """Renders navigation components with responsive design"""
    
    def __init__(self, nav_state: NavigationState):
        self.nav_state = nav_state
        self._inject_navigation_css()
    
    def _inject_navigation_css(self):
        """Inject CSS for navigation styling"""
        st.markdown("""
        <style>
        /* Primary Navigation Styling */
        .nav-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 0;
            margin: -1rem -1rem 2rem -1rem;
            border-radius: 0;
        }
        
        .nav-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 1rem 2rem;
            color: white;
        }
        
        .nav-logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
        }
        
        .nav-areas {
            display: flex;
            gap: 0;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 8px;
            padding: 4px;
        }
        
        .nav-area-btn {
            background: transparent;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 100px;
        }
        
        .nav-area-btn:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        .nav-area-btn.active {
            background: white;
            color: #667eea;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_primary_navigation(self) -> str:
        """Render main navigation areas with active state"""
        current_area = self.nav_state.get_current_area()
        
        # Use Streamlit buttons for actual navigation
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 WORK", key="nav_work", 
                        help="Certificate Generation & Management",
                        use_container_width=True):
                self.nav_state.set_navigation('work', 'generate')
                st.rerun()
        
        with col2:
            if st.button("⚙️ MANAGE", key="nav_manage", 
                        help="Templates, Courses, Users",
                        use_container_width=True):
                self.nav_state.set_navigation('manage', 'templates')
                st.rerun()
        
        with col3:
            if st.button("📊 MONITOR", key="nav_monitor", 
                        help="Analytics, Settings, System",
                        use_container_width=True):
                self.nav_state.set_navigation('monitor', 'analytics')
                st.rerun()
        
        return current_area

class NavigationManager:
    """Main navigation manager coordinating all navigation components"""
    
    def __init__(self):
        self.nav_state = NavigationState()
        self.renderer = NavigationRenderer(self.nav_state)
    
    def render_navigation(self) -> Tuple[str, str]:
        """Render complete navigation system and return current area/tab"""
        # Render primary navigation
        current_area = self.renderer.render_primary_navigation()
        current_tab = self.nav_state.get_current_tab()
        
        return current_area, current_tab
    
    def get_current_location(self) -> Dict[str, str]:
        """Get current navigation location"""
        return {
            'area': self.nav_state.get_current_area(),
            'tab': self.nav_state.get_current_tab(),
            'breadcrumb': st.session_state.navigation_state['breadcrumb']
        }

# Convenience functions for compatibility
def render_task_oriented_navigation() -> Tuple[str, str]:
    """Render complete task-oriented navigation system"""
    nav_manager = NavigationManager()
    return nav_manager.render_navigation()

def create_navigation_manager() -> NavigationManager:
    """Create and return navigation manager instance"""
    return NavigationManager()

def get_current_navigation() -> Dict[str, str]:
    """Get current navigation state"""
    nav_manager = NavigationManager()
    return nav_manager.get_current_location()