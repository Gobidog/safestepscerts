"""
Mobile Optimization System for SafeSteps
Comprehensive mobile-first design with responsive layouts and touch-friendly interactions
"""
import streamlit as st
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from utils.ui_components import COLORS, TYPOGRAPHY, SPACING, BREAKPOINTS

class MobileDetector:
    """Detect mobile devices and screen characteristics"""
    
    @staticmethod
    def is_mobile_device() -> bool:
        """Detect if user is on mobile device using simple user agent parsing"""
        try:
            # Try to get user agent from session state or headers
            user_agent_string = st.session_state.get('user_agent', '')
            if not user_agent_string:
                # Default to mobile-first approach if detection fails
                return True
            
            # Simple mobile detection using user agent string
            user_agent_lower = user_agent_string.lower()
            mobile_keywords = ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone']
            return any(keyword in user_agent_lower for keyword in mobile_keywords)
        except:
            # Default to mobile-first approach if detection fails
            return True
    
    @staticmethod
    def get_device_info() -> Dict[str, Any]:
        """Get comprehensive device information using simple parsing"""
        try:
            user_agent_string = st.session_state.get('user_agent', '')
            if user_agent_string:
                user_agent_lower = user_agent_string.lower()
                
                # Simple mobile detection
                mobile_keywords = ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']
                tablet_keywords = ['ipad', 'tablet', 'kindle']
                
                is_mobile = any(keyword in user_agent_lower for keyword in mobile_keywords)
                is_tablet = any(keyword in user_agent_lower for keyword in tablet_keywords)
                is_desktop = not (is_mobile or is_tablet)
                
                # Simple browser detection
                browser = 'Unknown'
                if 'chrome' in user_agent_lower:
                    browser = 'Chrome'
                elif 'firefox' in user_agent_lower:
                    browser = 'Firefox'
                elif 'safari' in user_agent_lower:
                    browser = 'Safari'
                elif 'edge' in user_agent_lower:
                    browser = 'Edge'
                
                # Simple OS detection
                os_name = 'Unknown'
                if 'windows' in user_agent_lower:
                    os_name = 'Windows'
                elif 'mac' in user_agent_lower or 'ios' in user_agent_lower:
                    os_name = 'macOS/iOS'
                elif 'android' in user_agent_lower:
                    os_name = 'Android'
                elif 'linux' in user_agent_lower:
                    os_name = 'Linux'
                
                return {
                    'is_mobile': is_mobile,
                    'is_tablet': is_tablet,
                    'is_desktop': is_desktop,
                    'browser': browser,
                    'os': os_name,
                    'device': 'Mobile' if is_mobile else 'Tablet' if is_tablet else 'Desktop'
                }
        except:
            pass
        
        return {
            'is_mobile': True,  # Default to mobile-first
            'is_tablet': False,
            'is_desktop': False,
            'browser': 'Unknown',
            'os': 'Unknown',
            'device': 'Unknown'
        }

    @staticmethod
    def inject_device_detection():
        """Inject JavaScript to detect device characteristics"""
        detection_script = """
        <script>
        // Device detection and viewport info
        if (typeof window !== 'undefined') {
            const deviceInfo = {
                userAgent: navigator.userAgent,
                screenWidth: window.screen.width,
                screenHeight: window.screen.height,
                viewportWidth: window.innerWidth,
                viewportHeight: window.innerHeight,
                devicePixelRatio: window.devicePixelRatio || 1,
                isTouchDevice: 'ontouchstart' in window || navigator.maxTouchPoints > 0
            };
            
            // Send to Streamlit
            if (window.parent && window.parent.postMessage) {
                window.parent.postMessage({
                    type: 'streamlit:deviceInfo',
                    data: deviceInfo
                }, '*');
            }
        }
        </script>
        """
        st.markdown(detection_script, unsafe_allow_html=True)

class ResponsiveLayout:
    """Manage responsive layouts across different screen sizes"""
    
    @staticmethod
    def get_responsive_columns(mobile_cols: List[int], tablet_cols: List[int], desktop_cols: List[int]) -> List[int]:
        """Get responsive column configuration based on device"""
        device_info = MobileDetector.get_device_info()
        
        if device_info['is_mobile']:
            return mobile_cols
        elif device_info['is_tablet']:
            return tablet_cols
        else:
            return desktop_cols
    
    @staticmethod
    def create_responsive_container(content_func, mobile_class: str = "", tablet_class: str = "", desktop_class: str = ""):
        """Create a responsive container with device-specific styling"""
        device_info = MobileDetector.get_device_info()
        
        css_class = ""
        if device_info['is_mobile'] and mobile_class:
            css_class = mobile_class
        elif device_info['is_tablet'] and tablet_class:
            css_class = tablet_class
        elif device_info['is_desktop'] and desktop_class:
            css_class = desktop_class
        
        container = st.container()
        with container:
            if css_class:
                st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            content_func()
            if css_class:
                st.markdown('</div>', unsafe_allow_html=True)

class TouchTargetOptimizer:
    """Ensure all interactive elements meet WCAG 2.2 touch target requirements"""
    
    MIN_TOUCH_TARGET = 44  # WCAG 2.2 minimum in pixels
    RECOMMENDED_TARGET = 48  # Recommended size for primary actions
    LARGE_TARGET = 56  # Large buttons for important actions
    
    @staticmethod
    def create_touch_button(
        text: str, 
        key: Optional[str] = None,
        button_type: str = "primary",
        size: str = "medium",
        disabled: bool = False,
        help_text: Optional[str] = None,
        icon: Optional[str] = None
    ) -> bool:
        """Create touch-optimized button with proper sizing"""
        # Determine button class based on type and size
        classes = ["touch-button"]
        
        if button_type == "primary":
            classes.append("touch-primary")
        elif button_type == "secondary":
            classes.append("touch-secondary")
        elif button_type == "success":
            classes.append("touch-success")
        elif button_type == "warning":
            classes.append("touch-warning")
        elif button_type == "danger":
            classes.append("touch-danger")
        
        if size == "large":
            classes.append("touch-large")
        elif size == "small":
            classes.append("touch-small")
        
        # Add icon if provided
        display_text = f"{icon} {text}" if icon else text
        
        # Create button with custom styling
        with st.container():
            st.markdown(f'<div class="{" ".join(classes)}">', unsafe_allow_html=True)
            result = st.button(
                display_text,
                key=key,
                disabled=disabled,
                help=help_text,
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
        return result
    
    @staticmethod
    def create_touch_form_elements():
        """Apply touch-friendly styling to form elements"""
        form_css = f"""
        <style>
        /* Touch-optimized form elements */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div,
        .stMultiSelect > div > div > div,
        .stDateInput > div > div > input,
        .stTimeInput > div > div > input,
        .stNumberInput > div > div > input {{
            min-height: {TouchTargetOptimizer.MIN_TOUCH_TARGET}px !important;
            font-size: 16px !important;
            padding: 12px 16px !important;
            border-radius: 8px !important;
            border: 2px solid {COLORS['border']} !important;
            transition: all 0.2s ease !important;
        }}
        
        /* Focus states for accessibility */
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus,
        .stSelectbox > div > div > div:focus,
        .stDateInput > div > div > input:focus {{
            border-color: {COLORS['border_focus']} !important;
            outline: 2px solid {COLORS['border_focus']} !important;
            outline-offset: 2px !important;
        }}
        
        /* Touch targets for mobile */
        @media (max-width: 768px) {{
            .stTextInput > div > div > input,
            .stTextArea > div > div > textarea,
            .stSelectbox > div > div > div,
            .stMultiSelect > div > div > div {{
                min-height: {TouchTargetOptimizer.RECOMMENDED_TARGET}px !important;
                font-size: 18px !important;
                padding: 16px !important;
            }}
        }}
        </style>
        """
        st.markdown(form_css, unsafe_allow_html=True)

class MobileNavigation:
    """Mobile-optimized navigation patterns"""
    
    @staticmethod
    def create_bottom_nav(nav_items: List[Dict[str, Any]]) -> str:
        """Create bottom navigation for mobile devices"""
        device_info = MobileDetector.get_device_info()
        
        if not device_info['is_mobile']:
            return ""
        
        # Create bottom navigation
        nav_html = """
        <div class="bottom-nav">
        """
        
        for item in nav_items:
            active_class = "active" if item.get('active', False) else ""
            nav_html += f"""
            <div class="nav-item {active_class}" data-page="{item['key']}">
                <div class="nav-icon">{item.get('icon', '•')}</div>
                <div class="nav-label">{item['label']}</div>
            </div>
            """
        
        nav_html += "</div>"
        return nav_html
    
    @staticmethod
    def create_floating_action_button(
        icon: str = "➕",
        tooltip: str = "Quick Action",
        position: str = "bottom-right"
    ) -> str:
        """Create floating action button for mobile"""
        position_class = f"fab-{position.replace('-', '_')}"
        
        fab_html = f"""
        <div class="floating-action-button {position_class}" title="{tooltip}">
            <span class="fab-icon">{icon}</span>
        </div>
        """
        return fab_html
    
    @staticmethod
    def create_hamburger_menu(menu_items: List[Dict[str, Any]]) -> str:
        """Create hamburger menu for secondary navigation"""
        menu_html = """
        <div class="hamburger-menu">
            <div class="hamburger-icon">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div class="hamburger-dropdown">
        """
        
        for item in menu_items:
            menu_html += f"""
            <div class="menu-item" data-action="{item['action']}">
                <span class="menu-icon">{item.get('icon', '•')}</span>
                <span class="menu-text">{item['label']}</span>
            </div>
            """
        
        menu_html += """
            </div>
        </div>
        """
        return menu_html

class MobileGestures:
    """Handle mobile gesture interactions"""
    
    @staticmethod
    def enable_swipe_navigation(pages: List[str]) -> str:
        """Enable swipe gestures for navigation between pages"""
        swipe_script = f"""
        <script>
        (function() {{
            let startX = 0;
            let startY = 0;
            let currentPageIndex = 0;
            const pages = {json.dumps(pages)};
            
            document.addEventListener('touchstart', function(e) {{
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
            }}, false);
            
            document.addEventListener('touchend', function(e) {{
                if (!startX || !startY) return;
                
                const endX = e.changedTouches[0].clientX;
                const endY = e.changedTouches[0].clientY;
                
                const deltaX = startX - endX;
                const deltaY = startY - endY;
                
                // Horizontal swipe threshold
                if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 50) {{
                    if (deltaX > 0) {{
                        // Swipe left - next page
                        if (currentPageIndex < pages.length - 1) {{
                            window.parent.postMessage({{
                                type: 'streamlit:navigate',
                                page: pages[currentPageIndex + 1]
                            }}, '*');
                        }}
                    }} else {{
                        // Swipe right - previous page
                        if (currentPageIndex > 0) {{
                            window.parent.postMessage({{
                                type: 'streamlit:navigate',
                                page: pages[currentPageIndex - 1]
                            }}, '*');
                        }}
                    }}
                }}
                
                startX = 0;
                startY = 0;
            }}, false);
        }})();
        </script>
        """
        return swipe_script
    
    @staticmethod
    def enable_pull_to_refresh() -> str:
        """Enable pull-to-refresh gesture"""
        refresh_script = """
        <script>
        (function() {
            let startY = 0;
            let pullDistance = 0;
            const threshold = 100;
            
            document.addEventListener('touchstart', function(e) {
                if (window.scrollY === 0) {
                    startY = e.touches[0].clientY;
                }
            }, false);
            
            document.addEventListener('touchmove', function(e) {
                if (startY && window.scrollY === 0) {
                    pullDistance = e.touches[0].clientY - startY;
                    if (pullDistance > 0) {
                        e.preventDefault();
                        // Visual feedback for pull distance
                        const opacity = Math.min(pullDistance / threshold, 1);
                        document.body.style.transform = `translateY(${Math.min(pullDistance * 0.5, 50)}px)`;
                        document.body.style.opacity = 1 - (opacity * 0.2);
                    }
                }
            }, false);
            
            document.addEventListener('touchend', function(e) {
                if (pullDistance > threshold) {
                    window.parent.postMessage({
                        type: 'streamlit:refresh'
                    }, '*');
                }
                
                document.body.style.transform = '';
                document.body.style.opacity = '';
                startY = 0;
                pullDistance = 0;
            }, false);
        })();
        </script>
        """
        return refresh_script

class MobileOptimizer:
    """Main mobile optimization coordinator"""
    
    def __init__(self):
        self.detector = MobileDetector()
        self.layout = ResponsiveLayout()
        self.touch_optimizer = TouchTargetOptimizer()
        self.navigation = MobileNavigation()
        self.gestures = MobileGestures()
    
    def apply_mobile_optimizations(self):
        """Apply comprehensive mobile optimizations"""
        # Inject device detection
        self.detector.inject_device_detection()
        
        # Apply mobile-specific CSS
        self._apply_mobile_css()
        
        # Optimize form elements
        self.touch_optimizer.create_touch_form_elements()
    
    def _apply_mobile_css(self):
        """Apply comprehensive mobile CSS optimizations"""
        mobile_css = f"""
        <style>
        /* Mobile-First Base Styles */
        .main .block-container {{
            padding: 1rem 0.5rem !important;
            max-width: 100% !important;
        }}
        
        /* Touch Target Optimization */
        .touch-button {{
            margin: 8px 0 !important;
        }}
        
        .touch-button .stButton > button {{
            min-height: {TouchTargetOptimizer.MIN_TOUCH_TARGET}px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 12px 24px !important;
            border: 2px solid transparent !important;
            transition: all 0.2s ease !important;
            width: 100% !important;
        }}
        
        .touch-primary .stButton > button {{
            background-color: {COLORS['primary']} !important;
            color: {COLORS['text_inverse']} !important;
            min-height: {TouchTargetOptimizer.RECOMMENDED_TARGET}px !important;
            font-size: 18px !important;
            box-shadow: 0 4px 12px rgba(3, 42, 81, 0.25) !important;
        }}
        
        .touch-primary .stButton > button:hover {{
            background-color: {COLORS['primary_dark']} !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 16px rgba(3, 42, 81, 0.35) !important;
        }}
        
        .touch-large .stButton > button {{
            min-height: {TouchTargetOptimizer.LARGE_TARGET}px !important;
            font-size: 20px !important;
            padding: 18px 32px !important;
        }}
        
        .touch-small .stButton > button {{
            min-height: {TouchTargetOptimizer.MIN_TOUCH_TARGET}px !important;
            font-size: 14px !important;
            padding: 10px 16px !important;
        }}
        
        /* Secondary button styling */
        .touch-secondary .stButton > button {{
            background-color: {COLORS['background']} !important;
            color: {COLORS['primary']} !important;
            border: 2px solid {COLORS['primary']} !important;
        }}
        
        .touch-secondary .stButton > button:hover {{
            background-color: {COLORS['surface']} !important;
            border-color: {COLORS['primary_dark']} !important;
        }}
        
        /* Success button styling */
        .touch-success .stButton > button {{
            background-color: {COLORS['success']} !important;
            color: {COLORS['text_inverse']} !important;
        }}
        
        /* Warning button styling */
        .touch-warning .stButton > button {{
            background-color: {COLORS['warning']} !important;
            color: {COLORS['text_inverse']} !important;
        }}
        
        /* Danger button styling */
        .touch-danger .stButton > button {{
            background-color: {COLORS['error']} !important;
            color: {COLORS['text_inverse']} !important;
        }}
        
        /* Bottom Navigation */
        .bottom-nav {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: {COLORS['background']};
            border-top: 1px solid {COLORS['border']};
            display: flex;
            justify-content: space-around;
            padding: 8px 0;
            z-index: 1000;
            box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.1);
        }}
        
        .nav-item {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 8px 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            min-width: {TouchTargetOptimizer.MIN_TOUCH_TARGET}px;
            min-height: {TouchTargetOptimizer.MIN_TOUCH_TARGET}px;
            justify-content: center;
        }}
        
        .nav-item:hover {{
            background-color: {COLORS['hover_overlay']};
        }}
        
        .nav-item.active {{
            color: {COLORS['primary']};
        }}
        
        .nav-icon {{
            font-size: 20px;
            margin-bottom: 4px;
        }}
        
        .nav-label {{
            font-size: 10px;
            font-weight: 500;
        }}
        
        /* Floating Action Button */
        .floating-action-button {{
            position: fixed;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background-color: {COLORS['accent']};
            color: {COLORS['text_inverse']};
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            cursor: pointer;
            transition: all 0.3s ease;
            z-index: 999;
        }}
        
        .fab-bottom_right {{
            bottom: 80px;
            right: 16px;
        }}
        
        .fab-bottom_left {{
            bottom: 80px;
            left: 16px;
        }}
        
        .floating-action-button:hover {{
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.35);
        }}
        
        .fab-icon {{
            font-size: 24px;
        }}
        
        /* Hamburger Menu */
        .hamburger-menu {{
            position: relative;
            display: inline-block;
        }}
        
        .hamburger-icon {{
            width: {TouchTargetOptimizer.MIN_TOUCH_TARGET}px;
            height: {TouchTargetOptimizer.MIN_TOUCH_TARGET}px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            cursor: pointer;
            padding: 8px;
        }}
        
        .hamburger-icon span {{
            width: 20px;
            height: 2px;
            background-color: {COLORS['text_primary']};
            margin: 2px 0;
            transition: 0.3s;
        }}
        
        .hamburger-dropdown {{
            position: absolute;
            top: 100%;
            right: 0;
            background: {COLORS['background']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            min-width: 200px;
            display: none;
            z-index: 1000;
        }}
        
        .hamburger-menu:hover .hamburger-dropdown {{
            display: block;
        }}
        
        .menu-item {{
            display: flex;
            align-items: center;
            padding: 12px 16px;
            cursor: pointer;
            transition: background-color 0.2s ease;
            min-height: {TouchTargetOptimizer.MIN_TOUCH_TARGET}px;
        }}
        
        .menu-item:hover {{
            background-color: {COLORS['hover_overlay']};
        }}
        
        .menu-icon {{
            margin-right: 12px;
            font-size: 16px;
        }}
        
        /* Mobile Responsive Adjustments */
        @media (max-width: 768px) {{
            /* Hide sidebar on mobile */
            section[data-testid="stSidebar"] {{
                display: none;
            }}
            
            /* Full width main content */
            .main .block-container {{
                padding: 1rem 0.75rem 80px 0.75rem !important;
            }}
            
            /* Stack columns vertically */
            .row-widget.stHorizontal {{
                flex-direction: column !important;
            }}
            
            /* Full width elements */
            .element-container {{
                width: 100% !important;
                margin-bottom: 16px !important;
            }}
            
            /* Larger touch targets */
            .stSelectbox > div > div,
            .stMultiSelect > div > div,
            .stDateInput > div > div,
            .stTimeInput > div > div {{
                min-height: {TouchTargetOptimizer.RECOMMENDED_TARGET}px !important;
            }}
            
            /* Mobile-friendly metrics */
            [data-testid="metric-container"] {{
                background: {COLORS['surface']};
                padding: 16px !important;
                border-radius: 12px;
                margin-bottom: 16px !important;
                border: 1px solid {COLORS['border']};
            }}
            
            /* Mobile typography adjustments */
            h1 {{
                font-size: 1.75rem !important;
            }}
            
            h2 {{
                font-size: 1.5rem !important;
            }}
            
            h3 {{
                font-size: 1.25rem !important;
            }}
        }}
        
        /* Tablet optimizations */
        @media (min-width: 769px) and (max-width: 1024px) {{
            .main .block-container {{
                padding: 1.5rem 1rem !important;
            }}
            
            /* Two-column layout for tablets */
            .tablet-two-col {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
            }}
        }}
        
        /* Desktop optimizations */
        @media (min-width: 1025px) {{
            .main .block-container {{
                padding: 2rem 1.5rem !important;
            }}
            
            /* Hide mobile-specific elements */
            .bottom-nav,
            .floating-action-button {{
                display: none;
            }}
        }}
        
        /* Accessibility improvements */
        @media (prefers-reduced-motion: reduce) {{
            * {{
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }}
        }}
        
        /* High contrast mode support */
        @media (prefers-contrast: high) {{
            .touch-button .stButton > button {{
                border-width: 3px !important;
            }}
        }}
        
        /* Focus indicators for keyboard navigation */
        .touch-button .stButton > button:focus,
        .nav-item:focus,
        .menu-item:focus {{
            outline: 3px solid {COLORS['border_focus']} !important;
            outline-offset: 2px !important;
        }}
        </style>
        """
        st.markdown(mobile_css, unsafe_allow_html=True)
    
    def get_responsive_layout(self, page_type: str = "default") -> Dict[str, Any]:
        """Get responsive layout configuration for different page types"""
        device_info = self.detector.get_device_info()
        
        layouts = {
            "dashboard": {
                "mobile": {"columns": [1], "sidebar": False, "bottom_nav": True},
                "tablet": {"columns": [1, 1], "sidebar": True, "bottom_nav": False},
                "desktop": {"columns": [1, 1, 1], "sidebar": True, "bottom_nav": False}
            },
            "form": {
                "mobile": {"columns": [1], "sidebar": False, "single_column": True},
                "tablet": {"columns": [2, 1], "sidebar": True, "single_column": False},
                "desktop": {"columns": [2, 1], "sidebar": True, "single_column": False}
            },
            "workflow": {
                "mobile": {"columns": [1], "sidebar": False, "stepper": "vertical"},
                "tablet": {"columns": [1], "sidebar": True, "stepper": "horizontal"},
                "desktop": {"columns": [1], "sidebar": True, "stepper": "horizontal"}
            }
        }
        
        layout_config = layouts.get(page_type, layouts["dashboard"])
        
        if device_info['is_mobile']:
            return layout_config["mobile"]
        elif device_info['is_tablet']:
            return layout_config["tablet"]
        else:
            return layout_config["desktop"]
    
    def create_mobile_optimized_form(self, form_fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create mobile-optimized form with proper touch targets"""
        device_info = self.detector.get_device_info()
        form_values = {}
        
        with st.form("mobile_optimized_form"):
            for field in form_fields:
                field_type = field.get('type', 'text')
                field_key = field['key']
                field_label = field['label']
                field_required = field.get('required', False)
                
                # Add required indicator
                if field_required:
                    field_label += " *"
                
                if field_type == 'text':
                    form_values[field_key] = st.text_input(
                        field_label,
                        value=field.get('default', ''),
                        placeholder=field.get('placeholder', ''),
                        help=field.get('help', None)
                    )
                elif field_type == 'email':
                    form_values[field_key] = st.text_input(
                        field_label,
                        value=field.get('default', ''),
                        placeholder=field.get('placeholder', 'example@domain.com'),
                        help=field.get('help', None)
                    )
                elif field_type == 'textarea':
                    form_values[field_key] = st.text_area(
                        field_label,
                        value=field.get('default', ''),
                        placeholder=field.get('placeholder', ''),
                        height=field.get('height', 100),
                        help=field.get('help', None)
                    )
                elif field_type == 'select':
                    form_values[field_key] = st.selectbox(
                        field_label,
                        options=field.get('options', []),
                        index=field.get('default_index', 0),
                        help=field.get('help', None)
                    )
                elif field_type == 'multiselect':
                    form_values[field_key] = st.multiselect(
                        field_label,
                        options=field.get('options', []),
                        default=field.get('default', []),
                        help=field.get('help', None)
                    )
                elif field_type == 'file':
                    form_values[field_key] = st.file_uploader(
                        field_label,
                        type=field.get('allowed_types', None),
                        accept_multiple_files=field.get('multiple', False),
                        help=field.get('help', None)
                    )
                elif field_type == 'date':
                    form_values[field_key] = st.date_input(
                        field_label,
                        value=field.get('default', None),
                        help=field.get('help', None)
                    )
                elif field_type == 'number':
                    form_values[field_key] = st.number_input(
                        field_label,
                        min_value=field.get('min_value', None),
                        max_value=field.get('max_value', None),
                        value=field.get('default', 0),
                        step=field.get('step', 1),
                        help=field.get('help', None)
                    )
                elif field_type == 'checkbox':
                    form_values[field_key] = st.checkbox(
                        field_label,
                        value=field.get('default', False),
                        help=field.get('help', None)
                    )
            
            # Mobile-optimized submit button
            submitted = self.touch_optimizer.create_touch_button(
                text="Submit",
                key="submit_form",
                button_type="primary",
                size="large" if device_info['is_mobile'] else "medium"
            )
            
            if submitted:
                return form_values
        
        return {}

def apply_global_mobile_optimizations():
    """Apply mobile optimizations globally to the Streamlit app"""
    optimizer = MobileOptimizer()
    optimizer.apply_mobile_optimizations()
    
    # Set up session state for mobile preferences
    if 'mobile_preferences' not in st.session_state:
        st.session_state.mobile_preferences = {
            'gesture_navigation': True,
            'bottom_nav_enabled': True,
            'auto_hide_sidebar': True,
            'large_touch_targets': True
        }
    
    return optimizer

# Convenience functions for easy integration
def create_mobile_button(text: str, key: Optional[str] = None, **kwargs) -> bool:
    """Convenience function to create mobile-optimized button"""
    optimizer = TouchTargetOptimizer()
    return optimizer.create_touch_button(text, key, **kwargs)

def get_device_info() -> Dict[str, Any]:
    """Convenience function to get device information"""
    detector = MobileDetector()
    return detector.get_device_info()

def is_mobile() -> bool:
    """Convenience function to check if user is on mobile"""
    detector = MobileDetector()
    return detector.get_device_info()['is_mobile']

def create_responsive_columns(*args) -> List[int]:
    """Convenience function to create responsive columns"""
    layout = ResponsiveLayout()
    if len(args) == 3:
        return layout.get_responsive_columns(args[0], args[1], args[2])
    else:
        # Default responsive pattern
        return layout.get_responsive_columns([1], [1, 1], [1, 1, 1])