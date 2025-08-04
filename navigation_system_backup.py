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
        
        /* Tab Navigation Styling */
        .tab-container {
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 2rem;
            overflow-x: auto;
        }
        
        .tab-nav {
            display: flex;
            gap: 0;
            min-width: fit-content;
        }
        
        .tab-btn {
            background: none;
            border: none;
            padding: 12px 20px;
            font-weight: 500;
            color: #666;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
            min-width: 120px;
        }
        
        .tab-btn:hover {
            color: #333;
            background: #f5f5f5;
        }
        
        .tab-btn.active {
            color: #667eea;
            border-bottom-color: #667eea;
            background: #f8f9ff;
        }
        
        /* Breadcrumb Styling */
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 1rem;
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }
        
        .breadcrumb-item {
            color: #666;
        }
        
        .breadcrumb-item.active {
            color: #333;
            font-weight: 600;
        }
        
        .breadcrumb-separator {
            color: #999;
        }
        
        /* Quick Actions */
        .quick-actions {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
        }
        
        .fab {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .nav-header {
                padding: 1rem;
                flex-direction: column;
                gap: 1rem;
            }
            
            .nav-areas {
                width: 100%;
                justify-content: center;
            }
            
            .nav-area-btn {
                flex: 1;
                min-width: auto;
                padding: 10px 12px;
                font-size: 0.9rem;
            }
            
            .tab-container {
                margin: 0 -1rem 2rem -1rem;
                padding: 0 1rem;
                background: #f8f9fa;
                border-bottom: none;
                border-top: 1px solid #eee;
            }
            
            .tab-nav {
                justify-content: flex-start;
                padding: 8px 0;
            }
            
            .tab-btn {
                min-width: 100px;
                padding: 8px 16px;
                font-size: 0.9rem;
            }
            
            .quick-actions {
                bottom: 1rem;
                right: 1rem;
            }
            
            .fab {
                width: 48px;
                height: 48px;
                font-size: 1.2rem;
            }
        }
        
        /* Touch Target Accessibility */
        .touch-target {
            min-width: 44px;
            min-height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        /* Focus Indicators for Accessibility */
        .nav-area-btn:focus,
        .tab-btn:focus,
        .fab:focus {
            outline: 2px solid #667eea;
            outline-offset: 2px;
        }
        
        /* High Contrast Mode Support */
        @media (prefers-contrast: high) {
            .nav-area-btn.active {
                border: 2px solid currentColor;
            }
            
            .tab-btn.active {
                border-bottom-width: 4px;
            }
        }
        
        /* Reduced Motion Support */
        @media (prefers-reduced-motion: reduce) {
            .nav-area-btn,
            .tab-btn,
            .fab {
                transition: none;
            }
        }
        </style>
        """, unsafe_allow_html=True)
    
    def render_primary_navigation(self) -> str:
        """Render main navigation areas with active state"""
        current_area = self.nav_state.get_current_area()
        
        # Create navigation HTML
        nav_html = f"""
        <div class="nav-container">
            <div class="nav-header">
                <div class="nav-logo">🛡️ SafeSteps</div>
                <div class="nav-areas">
                    <button class="nav-area-btn {'active' if current_area == 'work' else ''}" 
                            onclick="selectArea('work')">
                        📋 WORK
                    </button>
                    <button class="nav-area-btn {'active' if current_area == 'manage' else ''}" 
                            onclick="selectArea('manage')">
                        ⚙️ MANAGE
                    </button>
                    <button class="nav-area-btn {'active' if current_area == 'monitor' else ''}" 
                            onclick="selectArea('monitor')">
                        📊 MONITOR
                    </button>
                </div>
            </div>
        </div>
        
        <script>
        function selectArea(area) {
            // This would trigger Streamlit rerun with new area
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: area
            }, '*');
        }
        </script>
        """
        
        st.markdown(nav_html, unsafe_allow_html=True)
        
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
    
    def render_tab_navigation(self, area: str) -> str:
        """Render tab navigation for current area"""
        current_tab = self.nav_state.get_current_tab()
        
        # Define tabs for each area
        area_tabs = {
            'work': {
                'generate': '🚀 Generate',
                'batch': '📚 Batch',
                'manage': '📋 Manage',
                'results': '👥 Results'
            },
            'manage': {
                'templates': '🎨 Templates',
                'courses': '📖 Courses',
                'users': '👤 Users',
                'content': '📁 Content'
            },
            'monitor': {
                'analytics': '📈 Analytics',
                'settings': '⚙️ Settings',
                'health': '❤️ Health',
                'security': '🔒 Security'
            }
        }
        
        if area not in area_tabs:
            return current_tab
        
        tabs = area_tabs[area]
        tab_keys = list(tabs.keys())
        tab_labels = list(tabs.values())
        
        # Create tab columns
        cols = st.columns(len(tab_keys))
        
        for i, (tab_key, tab_label) in enumerate(zip(tab_keys, tab_labels)):
            with cols[i]:
                if st.button(tab_label, key=f"tab_{area}_{tab_key}",
                           help=f"Navigate to {tab_label.split(' ', 1)[1]}",
                           use_container_width=True):
                    self.nav_state.set_navigation(area, tab_key)
                    st.rerun()
        
        return current_tab
    
    def render_breadcrumb(self) -> None:
        """Render breadcrumb navigation"""
        breadcrumb = st.session_state.navigation_state['breadcrumb']
        
        if len(breadcrumb) > 1:
            breadcrumb_text = " → ".join(breadcrumb)
            st.markdown(f"""
            <div class="breadcrumb">
                <span class="breadcrumb-item">🏠</span>
                <span class="breadcrumb-separator">→</span>
                {" <span class='breadcrumb-separator'>→</span> ".join([
                    f"<span class='breadcrumb-item {'active' if i == len(breadcrumb)-1 else ''}'>{item}</span>"
                    for i, item in enumerate(breadcrumb[1:], 1)
                ])}
            </div>
            """, unsafe_allow_html=True)
    
    def render_quick_actions(self, area: str, tab: str) -> None:
        """Render context-sensitive quick actions"""
        # Define quick actions for each context
        quick_actions = {
            ('work', 'generate'): ('🚀', 'Generate Certificate', 'generate_cert'),
            ('work', 'batch'): ('📤', 'Upload CSV', 'upload_csv'),
            ('work', 'manage'): ('🔍', 'Search Certificates', 'search_certs'),
            ('work', 'results'): ('➕', 'Add Student', 'add_student'),
            ('manage', 'templates'): ('🎨', 'New Template', 'new_template'),
            ('manage', 'courses'): ('📖', 'New Course', 'new_course'),
            ('manage', 'users'): ('👤', 'Add User', 'add_user'),
            ('manage', 'content'): ('📁', 'Upload Content', 'upload_content'),
            ('monitor', 'analytics'): ('📊', 'Generate Report', 'generate_report'),
            ('monitor', 'settings'): ('⚙️', 'Edit Settings', 'edit_settings'),
            ('monitor', 'health'): ('🔄', 'Run Diagnostics', 'run_diagnostics'),
            ('monitor', 'security'): ('🔒', 'Security Scan', 'security_scan'),
        }
        
        action = quick_actions.get((area, tab))
        if action:
            icon, label, action_key = action
            
            # Create floating action button in sidebar
            with st.sidebar:
                st.markdown("### Quick Actions")
                if st.button(f"{icon} {label}", key=f"quick_{action_key}",
                           help=f"Quick access to {label}",
                           use_container_width=True):
                    # Handle quick action
                    st.session_state[f'quick_action_{action_key}'] = True
                    st.rerun()

class NavigationManager:
    """Main navigation manager coordinating all navigation components"""
    
    def __init__(self):
        self.nav_state = NavigationState()
        self.renderer = NavigationRenderer(self.nav_state)
    
    def render_navigation(self) -> Tuple[str, str]:
        """Render complete navigation system and return current area/tab"""
        # Render primary navigation
        current_area = self.renderer.render_primary_navigation()
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Render breadcrumb
        self.renderer.render_breadcrumb()
        
        # Render tab navigation
        current_tab = self.renderer.render_tab_navigation(current_area)
        
        # Render quick actions
        self.renderer.render_quick_actions(current_area, current_tab)
        
        return current_area, current_tab
    
    def get_current_location(self) -> Dict[str, str]:
        """Get current navigation location"""
        return {
            'area': self.nav_state.get_current_area(),
            'tab': self.nav_state.get_current_tab(),
            'breadcrumb': st.session_state.navigation_state['breadcrumb']
        }
    
    def navigate_to(self, area: str, tab: str = None) -> None:
        """Programmatically navigate to specific location"""
        self.nav_state.set_navigation(area, tab)
    
    def get_navigation_history(self) -> List[str]:
        """Get navigation history for back button functionality"""
        return st.session_state.navigation_state['navigation_history']

# Convenience functions for common navigation patterns

def create_navigation_manager() -> NavigationManager:
    """Create and return navigation manager instance"""
    return NavigationManager()

def render_task_oriented_navigation() -> Tuple[str, str]:
    """Render complete task-oriented navigation system"""
    nav_manager = create_navigation_manager()
    return nav_manager.render_navigation()

def get_current_navigation() -> Dict[str, str]:
    """Get current navigation state"""
    nav_manager = NavigationManager()
    return nav_manager.get_current_location()

# Content routing functions

def route_work_content(tab: str):
    """Route content for WORK area based on tab"""
    if tab == 'generate':
        return render_certificate_generation()
    elif tab == 'batch':
        return render_batch_operations()
    elif tab == 'manage':
        return render_certificate_management()
    elif tab == 'results':
        return render_student_results()
    else:
        st.error(f"Unknown WORK tab: {tab}")

def route_manage_content(tab: str):
    """Route content for MANAGE area based on tab"""
    if tab == 'templates':
        return render_template_management()
    elif tab == 'courses':
        return render_course_management()
    elif tab == 'users':
        return render_user_management()
    elif tab == 'content':
        return render_content_management()
    else:
        st.error(f"Unknown MANAGE tab: {tab}")

def route_monitor_content(tab: str):
    """Route content for MONITOR area based on tab"""
    if tab == 'analytics':
        return render_analytics_dashboard()
    elif tab == 'settings':
        return render_system_settings()
    elif tab == 'health':
        return render_system_health()
    elif tab == 'security':
        return render_security_compliance()
    else:
        st.error(f"Unknown MONITOR tab: {tab}")

# Placeholder content functions (to be implemented by other modules)

def render_certificate_generation():
    st.subheader("🚀 Certificate Generation")
    st.info("Primary certificate generation interface - enhanced with large buttons and clear workflow")

def render_batch_operations():  
    st.subheader("📚 Batch Operations")
    st.info("Bulk certificate processing with CSV upload and progress tracking")

def render_certificate_management():
    st.subheader("📋 Certificate Management")
    st.info("Search, edit, and manage existing certificates")

def render_student_results():
    st.subheader("👥 Student Results")
    st.info("Manage student records and assessment results")

def render_template_management():
    st.subheader("🎨 Template Management")
    st.info("Design and manage certificate templates")

def render_course_management():
    st.subheader("📖 Course Management")
    st.info("Configure courses and educational content")

def render_user_management():
    st.subheader("👤 User Management")
    st.info("Administer user accounts and permissions")

def render_content_management():
    st.subheader("📁 Content Management")
    st.info("Manage media files and educational resources")

def render_analytics_dashboard():
    st.subheader("📈 Analytics Dashboard")
    st.info("Usage metrics and performance analytics")

def render_system_settings():
    st.subheader("⚙️ System Settings")
    st.info("Configure application settings and preferences")

def render_system_health():
    st.subheader("❤️ System Health")
    st.info("Monitor system performance and diagnostics")

def render_security_compliance():
    st.subheader("🔒 Security & Compliance")
    st.info("Security logs and compliance monitoring")

# Main integration function
def integrate_with_main_app():
    """
    Integration guide for main app.py:
    
    1. Import: from navigation_system import render_task_oriented_navigation, route_work_content, route_manage_content, route_monitor_content
    
    2. In main():
        # Render navigation and get current location
        current_area, current_tab = render_task_oriented_navigation()
        
        # Route content based on navigation
        if current_area == 'work':
            route_work_content(current_tab)
        elif current_area == 'manage':
            route_manage_content(current_tab)
        elif current_area == 'monitor':
            route_monitor_content(current_tab)
    
    3. Replace existing admin/system page logic with this navigation system
    """
    pass

if __name__ == "__main__":
    # Demo of navigation system
    st.set_page_config(
        page_title="SafeSteps Navigation Demo",
        page_icon="🛡️",
        layout="wide"
    )
    
    st.title("SafeSteps Navigation System Demo")
    
    # Render navigation
    current_area, current_tab = render_task_oriented_navigation()
    
    # Show current location
    st.markdown("---")
    st.write(f"**Current Location:** {current_area.upper()} → {current_tab.title()}")
    
    # Route content
    if current_area == 'work':
        route_work_content(current_tab)
    elif current_area == 'manage':
        route_manage_content(current_tab)
    elif current_area == 'monitor':
        route_monitor_content(current_tab)