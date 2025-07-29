"""
UI Components and Design System for SafeSteps
Centralized UI components for consistent design and better user experience
"""
import streamlit as st
from typing import Optional, List, Dict, Tuple
import json

# SafeSteps Brand Colors
COLORS = {
    'primary': '#032A51',      # Navy Blue
    'accent': '#9ACA3C',       # Green
    'success': '#52C41A',      # Success Green
    'warning': '#FAAD14',      # Warning Orange
    'error': '#F5222D',        # Error Red
    'info': '#1890FF',         # Info Blue
    'background': '#F5F7FA',   # Light Gray
    'border': '#E1E8ED',       # Border Gray
    'text_primary': '#2D3748', # Dark Text
    'text_secondary': '#718096' # Secondary Text
}

# Typography Scale
TYPOGRAPHY = {
    'h1': {'size': '32px', 'weight': '700', 'line_height': '1.2'},
    'h2': {'size': '24px', 'weight': '600', 'line_height': '1.3'},
    'h3': {'size': '20px', 'weight': '600', 'line_height': '1.4'},
    'body': {'size': '16px', 'weight': '400', 'line_height': '1.6'},
    'caption': {'size': '14px', 'weight': '400', 'line_height': '1.5'},
    'small': {'size': '12px', 'weight': '400', 'line_height': '1.5'}
}

def apply_custom_css():
    """Apply enhanced custom CSS for better UI/UX"""
    st.markdown("""
    <style>
        /* Import Inter font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* CSS Variables */
        :root {
            --primary: #032A51;
            --accent: #9ACA3C;
            --success: #52C41A;
            --warning: #FAAD14;
            --error: #F5222D;
            --info: #1890FF;
            --background: #F5F7FA;
            --border: #E1E8ED;
            --text-primary: #2D3748;
            --text-secondary: #718096;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
            --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
            --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
            --transition: all 0.3s ease;
        }
        
        /* Global styles */
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stToolbar"] {visibility: hidden;}
        
        /* Main container */
        .main {
            padding: 0;
            background-color: var(--background);
            min-height: 100vh;
        }
        
        /* Enhanced Card Component */
        .ui-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: var(--shadow-sm);
            margin-bottom: 20px;
            border: 1px solid var(--border);
            transition: var(--transition);
        }
        
        .ui-card:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        /* Button Variants */
        .stButton > button {
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 500;
            border: none;
            transition: var(--transition);
            text-transform: none;
            font-size: 16px;
            min-height: 48px;
        }
        
        /* Primary Button */
        .stButton > button[kind="primary"] {
            background-color: var(--primary);
            color: white;
        }
        
        .stButton > button[kind="primary"]:hover {
            background-color: #021d36;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(3, 42, 81, 0.3);
        }
        
        /* Secondary Button */
        .stButton > button[kind="secondary"] {
            background-color: white;
            color: var(--primary);
            border: 2px solid var(--primary);
        }
        
        .stButton > button[kind="secondary"]:hover {
            background-color: var(--primary);
            color: white;
        }
        
        /* Success Button */
        .success-button > button {
            background-color: var(--accent);
            color: white;
        }
        
        .success-button > button:hover {
            background-color: #7fb12f;
            transform: translateY(-1px);
        }
        
        /* Form Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            border-radius: 8px;
            border: 2px solid var(--border);
            padding: 12px 16px;
            font-size: 16px;
            transition: var(--transition);
            background-color: white;
        }
        
        .stTextInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(3, 42, 81, 0.1);
            outline: none;
        }
        
        /* File Uploader Enhancement */
        .stFileUploader {
            border: 2px dashed var(--border);
            border-radius: 12px;
            padding: 40px;
            background-color: var(--background);
            transition: var(--transition);
        }
        
        .stFileUploader:hover {
            border-color: var(--primary);
            background-color: rgba(3, 42, 81, 0.05);
        }
        
        /* Progress Bar Override */
        .stProgress > div > div {
            background-color: var(--accent);
            height: 8px;
            border-radius: 4px;
        }
        
        /* Alert Messages */
        .stAlert {
            border-radius: 8px;
            padding: 16px;
            border: 1px solid;
            font-size: 14px;
        }
        
        .stAlert[data-baseweb="notification"][data-kind="info"] {
            background-color: rgba(24, 144, 255, 0.1);
            border-color: var(--info);
            color: var(--text-primary);
        }
        
        .stAlert[data-baseweb="notification"][data-kind="success"] {
            background-color: rgba(82, 196, 26, 0.1);
            border-color: var(--success);
            color: var(--text-primary);
        }
        
        .stAlert[data-baseweb="notification"][data-kind="warning"] {
            background-color: rgba(250, 173, 20, 0.1);
            border-color: var(--warning);
            color: var(--text-primary);
        }
        
        .stAlert[data-baseweb="notification"][data-kind="error"] {
            background-color: rgba(245, 34, 45, 0.1);
            border-color: var(--error);
            color: var(--text-primary);
        }
        
        /* Tabs Enhancement */
        .stTabs [data-baseweb="tab-list"] {
            background-color: var(--background);
            border-radius: 8px;
            padding: 4px;
            gap: 4px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 6px;
            padding: 8px 16px;
            background-color: transparent;
            color: var(--text-secondary);
            transition: var(--transition);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: white;
            color: var(--text-primary);
        }
        
        .stTabs [aria-selected="true"] {
            background-color: white;
            color: var(--primary);
            box-shadow: var(--shadow-sm);
        }
        
        /* Expander Enhancement */
        .streamlit-expanderHeader {
            background-color: var(--background);
            border-radius: 8px;
            border: 1px solid var(--border);
            font-weight: 500;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: white;
            border-color: var(--primary);
        }
        
        /* Metric Cards */
        [data-testid="metric-container"] {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-sm);
            transition: var(--transition);
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }
        
        /* Loading States */
        .stSpinner > div {
            border-color: var(--primary);
        }
        
        /* Mobile Responsive */
        @media (max-width: 768px) {
            .ui-card {
                padding: 16px;
                margin-bottom: 16px;
            }
            
            .stButton > button {
                padding: 10px 20px;
                font-size: 14px;
                min-height: 44px;
            }
        }
        
        /* Accessibility - Focus States */
        *:focus {
            outline: 2px solid var(--primary);
            outline-offset: 2px;
        }
        
        /* Skip to main content link */
        .skip-to-main {
            position: absolute;
            left: -9999px;
            z-index: 999;
            padding: 1em;
            background-color: var(--primary);
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        
        .skip-to-main:focus {
            left: 50%;
            transform: translateX(-50%);
            top: 10px;
        }
        
        /* Animation classes */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .pulse {
            animation: pulse 2s infinite;
        }
    </style>
    """, unsafe_allow_html=True)

def create_header(title: str, subtitle: Optional[str] = None, user_info: Optional[Dict] = None):
    """Create a consistent header component"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.markdown(f"<h1 style='margin: 0; color: {COLORS['text_primary']};'>{title}</h1>", unsafe_allow_html=True)
        if subtitle:
            st.markdown(f"<p style='margin: 0; color: {COLORS['text_secondary']};'>{subtitle}</p>", unsafe_allow_html=True)
    
    with col2:
        if user_info:
            st.markdown(f"""
            <div style='text-align: right; padding: 10px;'>
                <p style='margin: 0; font-size: 14px; color: {COLORS['text_secondary']};'>
                    {user_info.get('username', 'User')}
                </p>
                <p style='margin: 0; font-size: 12px; color: {COLORS['text_secondary']};'>
                    {user_info.get('role', 'user').upper()}
                </p>
            </div>
            """, unsafe_allow_html=True)

def create_card(content: str, title: Optional[str] = None, icon: Optional[str] = None):
    """Create a card component"""
    card_html = '<div class="ui-card fade-in">'
    
    if title:
        icon_html = f"<span style='margin-right: 8px;'>{icon}</span>" if icon else ""
        card_html += f"<h3 style='margin-top: 0; color: {COLORS['text_primary']};'>{icon_html}{title}</h3>"
    
    card_html += content
    card_html += '</div>'
    
    st.markdown(card_html, unsafe_allow_html=True)

def create_metric_card(label: str, value: str, icon: str, color: str = 'primary'):
    """Create an enhanced metric card"""
    st.markdown(f"""
    <div class="ui-card" style="text-align: center; cursor: pointer;">
        <div style="font-size: 48px; color: {COLORS[color]}; margin-bottom: 10px;">{icon}</div>
        <div style="font-size: 36px; font-weight: 700; color: {COLORS[color]}; margin: 10px 0;">{value}</div>
        <div style="font-size: 14px; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def create_status_badge(status: str, type: str = 'default'):
    """Create a status badge"""
    colors = {
        'success': COLORS['success'],
        'warning': COLORS['warning'],
        'error': COLORS['error'],
        'info': COLORS['info'],
        'default': COLORS['text_secondary']
    }
    
    bg_colors = {
        'success': 'rgba(82, 196, 26, 0.1)',
        'warning': 'rgba(250, 173, 20, 0.1)',
        'error': 'rgba(245, 34, 45, 0.1)',
        'info': 'rgba(24, 144, 255, 0.1)',
        'default': 'rgba(113, 128, 150, 0.1)'
    }
    
    return f"""
    <span style="
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        color: {colors.get(type, colors['default'])};
        background-color: {bg_colors.get(type, bg_colors['default'])};
        border: 1px solid {colors.get(type, colors['default'])};
    ">{status}</span>
    """

def create_progress_steps(steps: List[Tuple[str, str, int]], current_step: int):
    """Create an enhanced progress indicator"""
    cols = st.columns(len(steps))
    
    for idx, (label, icon, step_num) in enumerate(steps):
        with cols[idx]:
            # Determine status
            if step_num < current_step:
                status = 'completed'
                color = COLORS['success']
                bg_color = 'rgba(82, 196, 26, 0.1)'
            elif step_num == current_step:
                status = 'active'
                color = COLORS['primary']
                bg_color = 'rgba(3, 42, 81, 0.1)'
            else:
                status = 'pending'
                color = COLORS['border']
                bg_color = COLORS['background']
            
            # Create step
            st.markdown(f"""
            <div style="text-align: center;" class="fade-in">
                <div style="
                    padding: 16px;
                    border-radius: 12px;
                    background-color: {bg_color};
                    border: 2px solid {color};
                    margin-bottom: 10px;
                    {'transform: scale(1.05);' if status == 'active' else ''}
                ">
                    <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
                    <div style="
                        width: 48px;
                        height: 48px;
                        border-radius: 50%;
                        background-color: {color};
                        color: white;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 12px;
                        font-weight: bold;
                        font-size: 18px;
                        {'animation: pulse 2s infinite;' if status == 'active' else ''}
                    ">
                        {'✓' if status == 'completed' else step_num}
                    </div>
                    <div style="font-size: 14px; font-weight: 600; color: {color};">{label}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def create_loading_animation(text: str = "Loading..."):
    """Create a custom loading animation"""
    st.markdown(f"""
    <div style="text-align: center; padding: 40px;">
        <div style="
            width: 60px;
            height: 60px;
            border: 4px solid {COLORS['background']};
            border-top: 4px solid {COLORS['primary']};
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        "></div>
        <p style="color: {COLORS['text_secondary']}; font-size: 16px;">{text}</p>
    </div>
    <style>
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    """, unsafe_allow_html=True)

def show_toast(message: str, type: str = 'info', duration: int = 3):
    """Show a toast notification"""
    colors = {
        'success': COLORS['success'],
        'error': COLORS['error'],
        'warning': COLORS['warning'],
        'info': COLORS['info']
    }
    
    icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    
    placeholder = st.empty()
    placeholder.markdown(f"""
    <div style="
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: white;
        border: 1px solid {colors.get(type, COLORS['info'])};
        border-radius: 8px;
        padding: 16px 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    ">
        <span style="margin-right: 8px; font-size: 20px;">{icons.get(type, '📢')}</span>
        <span style="color: {COLORS['text_primary']};">{message}</span>
    </div>
    <style>
        @keyframes slideIn {{
            from {{ transform: translateX(100%); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
    </style>
    """, unsafe_allow_html=True)
    
    import time
    time.sleep(duration)
    placeholder.empty()

def create_empty_state(
    icon: str, 
    title: str, 
    description: str, 
    action_label: Optional[str] = None,
    action_callback: Optional[callable] = None
):
    """Create an empty state component"""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 60px 20px;
        background-color: {COLORS['background']};
        border-radius: 12px;
        border: 2px dashed {COLORS['border']};
    ">
        <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.5;">{icon}</div>
        <h3 style="color: {COLORS['text_primary']}; margin-bottom: 10px;">{title}</h3>
        <p style="color: {COLORS['text_secondary']}; max-width: 400px; margin: 0 auto 20px;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, type="primary", use_container_width=True):
                action_callback()

def create_breadcrumb(items: List[Dict[str, str]]):
    """Create a breadcrumb navigation"""
    breadcrumb_html = '<div style="display: flex; align-items: center; margin-bottom: 20px;">'
    
    for idx, item in enumerate(items):
        if idx > 0:
            breadcrumb_html += f'<span style="margin: 0 10px; color: {COLORS["text_secondary"]};">›</span>'
        
        is_active = idx == len(items) - 1
        breadcrumb_html += f'''
        <a href="{item.get('url', '#')}" style="
            color: {COLORS['primary'] if not is_active else COLORS['text_secondary']};
            text-decoration: none;
            font-weight: {500 if is_active else 400};
            {'pointer-events: none;' if is_active else ''}
        ">{item['label']}</a>
        '''
    
    breadcrumb_html += '</div>'
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

def create_search_bar(placeholder: str = "Search...", key: str = "search"):
    """Create a styled search bar"""
    search_html = f"""
    <div style="position: relative; margin-bottom: 20px;">
        <span style="
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: {COLORS['text_secondary']};
            font-size: 18px;
        ">🔍</span>
    </div>
    """
    st.markdown(search_html, unsafe_allow_html=True)
    
    return st.text_input(
        label="Search",
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed",
        help="Search for items..."
    )

def create_table_header(columns: List[Dict[str, str]]):
    """Create a styled table header"""
    cols = st.columns([col.get('width', 1) for col in columns])
    
    for idx, col in enumerate(columns):
        with cols[idx]:
            st.markdown(f"""
            <div style="
                font-weight: 600;
                color: {COLORS['text_secondary']};
                text-transform: uppercase;
                font-size: 12px;
                letter-spacing: 0.5px;
                padding-bottom: 8px;
                border-bottom: 2px solid {COLORS['border']};
            ">{col['label']}</div>
            """, unsafe_allow_html=True)

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