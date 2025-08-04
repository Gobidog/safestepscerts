"""
Theme System for Modern Dashboard
Handles dark/light themes and visual customization
"""
import streamlit as st

class ThemeSystem:
    """Manages theme switching and visual customization"""
    
    def __init__(self):
        self.themes = {
            "light": {
                "name": "Light Theme",
                "primary": "#1976D2",
                "secondary": "#FFA726",
                "background": "#FFFFFF",
                "surface": "#F5F5F5",
                "text": "#212121",
                "text_secondary": "#757575",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "error": "#F44336",
                "border": "#E0E0E0"
            },
            "dark": {
                "name": "Dark Theme",
                "primary": "#2196F3",
                "secondary": "#FFB74D",
                "background": "#121212",
                "surface": "#1E1E1E",
                "text": "#FFFFFF",
                "text_secondary": "#B0B0B0",
                "success": "#66BB6A",
                "warning": "#FFA726",
                "error": "#EF5350",
                "border": "#333333"
            },
            "ocean": {
                "name": "Ocean Theme",
                "primary": "#006BA6",
                "secondary": "#0496FF",
                "background": "#E8F4FD",
                "surface": "#B8E0FF",
                "text": "#003459",
                "text_secondary": "#005A8D",
                "success": "#00C896",
                "warning": "#FFB800",
                "error": "#FF6B6B",
                "border": "#0496FF"
            }
        }
        
        # Initialize theme in session state
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
    
    def get_current_theme(self):
        """Get the current theme settings"""
        theme_name = st.session_state.get('theme', 'light')
        return self.themes.get(theme_name, self.themes['light'])
    
    def set_theme(self, theme_name):
        """Set the current theme"""
        if theme_name in self.themes:
            st.session_state.theme = theme_name
    
    def apply_theme(self):
        """Apply the current theme to the app"""
        theme = self.get_current_theme()
        
        # Create CSS based on theme
        theme_css = f"""
        <style>
        /* Theme Colors */
        :root {{
            --primary-color: {theme['primary']};
            --secondary-color: {theme['secondary']};
            --background-color: {theme['background']};
            --surface-color: {theme['surface']};
            --text-color: {theme['text']};
            --text-secondary-color: {theme['text_secondary']};
            --success-color: {theme['success']};
            --warning-color: {theme['warning']};
            --error-color: {theme['error']};
            --border-color: {theme['border']};
        }}
        
        /* Apply theme to Streamlit components */
        .stApp {{
            background-color: var(--background-color);
            color: var(--text-color);
        }}
        
        /* Cards and containers */
        .stContainer {{
            background-color: var(--surface-color);
            border-color: var(--border-color);
        }}
        
        /* Buttons */
        .stButton > button {{
            background-color: var(--primary-color);
            color: white;
            border: none;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: var(--secondary-color);
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        /* Metrics */
        [data-testid="metric-container"] {{
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        /* Progress bars */
        .stProgress > div > div {{
            background-color: var(--primary-color);
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .element-container {{
            animation: fadeIn 0.5s ease-out;
        }}
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {{
            .stContainer {{
                padding: 0.5rem;
            }}
            
            .stButton > button {{
                width: 100%;
                margin-bottom: 0.5rem;
            }}
        }}
        </style>
        """
        
        st.markdown(theme_css, unsafe_allow_html=True)
    
    def create_theme_toggle(self):
        """Create a theme toggle button"""
        current_theme = st.session_state.get('theme', 'light')
        
        # Determine next theme
        if current_theme == 'light':
            next_theme = 'dark'
            icon = '🌙'
        else:
            next_theme = 'light'
            icon = '☀️'
        
        if st.button(f"{icon} Switch to {next_theme.title()} Mode"):
            self.set_theme(next_theme)
            st.rerun()
    
    def get_chart_colors(self):
        """Get colors optimized for charts in current theme"""
        theme = self.get_current_theme()
        return {
            'primary': theme['primary'],
            'secondary': theme['secondary'],
            'success': theme['success'],
            'warning': theme['warning'],
            'error': theme['error'],
            'series': [
                theme['primary'],
                theme['secondary'],
                theme['success'],
                theme['warning'],
                '#9C27B0',  # Purple
                '#00BCD4',  # Cyan
                '#8BC34A',  # Light Green
                '#FF5722'   # Deep Orange
            ]
        }
    
    def apply_mobile_styles(self):
        """Apply mobile-specific styles"""
        mobile_css = """
        <style>
        @media (max-width: 768px) {
            /* Stack columns on mobile */
            .row-widget.stHorizontal {
                flex-direction: column !important;
            }
            
            /* Full width buttons */
            .stButton > button {
                width: 100% !important;
            }
            
            /* Smaller headers */
            h1 { font-size: 1.5rem !important; }
            h2 { font-size: 1.25rem !important; }
            h3 { font-size: 1.1rem !important; }
            
            /* Compact metrics */
            [data-testid="metric-container"] {
                padding: 0.5rem !important;
            }
            
            /* Hide sidebar on mobile by default */
            section[data-testid="stSidebar"] {
                transform: translateX(-100%);
            }
        }
        </style>
        """
        st.markdown(mobile_css, unsafe_allow_html=True)