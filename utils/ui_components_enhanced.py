# ================================
# ENHANCED BUTTON SYSTEM - WCAG 2.2 COMPLIANT
# ================================

def create_prominent_button(
    text: str, 
    key: str,
    button_type: str = "primary",
    size: str = "medium",
    icon: Optional[str] = None,
    disabled: bool = False,
    use_container_width: bool = True,
    help_text: Optional[str] = None
) -> bool:
    """Create prominent, accessible buttons with proper sizing and visual hierarchy
    
    Args:
        text: Button text
        key: Unique key for the button
        button_type: 'primary', 'secondary', 'success', 'warning', 'danger'
        size: 'small' (44px), 'medium' (48px), 'large' (56px)
        icon: Optional emoji/icon to prefix the text
        disabled: Whether button is disabled
        use_container_width: Whether to use full container width
        help_text: Tooltip/help text
        
    Returns:
        bool: True if button was clicked
    """
    # Add CSS classes based on button type and size
    css_classes = []
    if button_type in ['success', 'warning', 'danger']:
        css_classes.append(button_type)
    if size != 'medium':
        css_classes.append(size)
    
    # Apply CSS classes if any
    if css_classes:
        # Create a container with CSS classes
        container_class = ' '.join(css_classes)
        st.markdown(f'<div class="stButton {container_class}">', unsafe_allow_html=True)
    
    # Create button text with optional icon
    button_text = f"{icon} {text}" if icon else text
    
    # Determine Streamlit button type
    if button_type == 'primary':
        st_type = 'primary'
    elif button_type == 'secondary':
        st_type = 'secondary'
    else:
        st_type = 'secondary'  # Custom styled via CSS
    
    # Create the button
    clicked = st.button(
        button_text,
        key=key,
        type=st_type,
        disabled=disabled,
        use_container_width=use_container_width,
        help=help_text
    )
    
    # Close CSS container if opened
    if css_classes:
        st.markdown('</div>', unsafe_allow_html=True)
    
    return clicked

def create_button_group(
    buttons: List[Dict[str, any]], 
    key_prefix: str,
    layout: str = "horizontal"
) -> Dict[str, bool]:
    """Create a group of related buttons with consistent styling
    
    Args:
        buttons: List of button configurations
        key_prefix: Prefix for button keys
        layout: 'horizontal' or 'vertical'
        
    Returns:
        Dict mapping button keys to clicked status
    """
    results = {}
    
    if layout == "horizontal":
        cols = st.columns(len(buttons))
        for idx, button_config in enumerate(buttons):
            with cols[idx]:
                button_key = f"{key_prefix}_{button_config['key']}"
                clicked = create_prominent_button(
                    text=button_config['text'],
                    key=button_key,
                    button_type=button_config.get('type', 'secondary'),
                    size=button_config.get('size', 'medium'),
                    icon=button_config.get('icon'),
                    disabled=button_config.get('disabled', False),
                    help_text=button_config.get('help')
                )
                results[button_config['key']] = clicked
    else:
        for button_config in buttons:
            button_key = f"{key_prefix}_{button_config['key']}"
            clicked = create_prominent_button(
                text=button_config['text'],
                key=button_key,
                button_type=button_config.get('type', 'secondary'),
                size=button_config.get('size', 'medium'),
                icon=button_config.get('icon'),
                disabled=button_config.get('disabled', False),
                help_text=button_config.get('help')
            )
            results[button_config['key']] = clicked
    
    return results

def create_workflow_step_button(
    text: str,
    step_number: int,
    is_active: bool,
    is_completed: bool,
    key: str,
    icon: Optional[str] = None
) -> bool:
    """Create workflow step buttons with clear status indication"""
    if is_completed:
        display_icon = "✅"
        button_type = "success"
        status_text = "Completed"
    elif is_active:
        display_icon = f"🔄"
        button_type = "primary"
        status_text = "Current Step"
    else:
        display_icon = f"{step_number}"
        button_type = "secondary"
        status_text = "Pending"
    
    # Override icon if provided
    if icon:
        display_icon = icon
    
    button_text = f"{display_icon} {text}"
    help_text = f"Step {step_number}: {status_text}"
    
    return create_prominent_button(
        text=button_text,
        key=key,
        button_type=button_type,
        size="large" if is_active else "medium",
        disabled=not is_active and not is_completed,
        help_text=help_text
    )

def create_enhanced_bulk_action_toolbar(
    actions: List[Dict[str, any]], 
    selected_count: int,
    key_prefix: str = "bulk"
) -> Dict[str, bool]:
    """Create toolbar for bulk operations with prominent buttons"""
    if selected_count == 0:
        return {}
    
    # Show selection count
    st.info(f"📋 {selected_count} item{'s' if selected_count != 1 else ''} selected")
    
    # Create action buttons
    button_configs = []
    for action in actions:
        button_configs.append({
            'key': action['key'],
            'text': action['label'],
            'type': action.get('type', 'secondary'),
            'icon': action.get('icon'),
            'help': action.get('help'),
            'size': 'medium'
        })
    
    return create_button_group(button_configs, key_prefix, layout="horizontal")

# ================================
# LOADING STATES & FEEDBACK SYSTEM
# ================================

def create_enhanced_loading_state(
    text: str = "Loading...",
    show_progress: bool = False,
    progress_value: Optional[int] = None,
    show_spinner: bool = True
):
    """Create enhanced loading states with progress indication"""
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if show_progress and progress_value is not None:
                st.progress(progress_value / 100)
                st.caption(f"{text} ({progress_value}%)")
            elif show_spinner:
                with st.spinner(text):
                    import time
                    time.sleep(0.1)  # Brief pause to show spinner
            else:
                st.info(f"⏳ {text}")

def create_feedback_message(
    message: str,
    message_type: str = "info",
    icon: Optional[str] = None,
    dismissible: bool = False,
    key: Optional[str] = None
):
    """Create user feedback messages with consistent styling"""
    # Default icons for each message type
    default_icons = {
        'success': '✅',
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌'
    }
    
    display_icon = icon or default_icons.get(message_type, '📢')
    display_message = f"{display_icon} {message}"
    
    # Create dismissible container if needed
    if dismissible and key:
        dismiss_key = f"dismiss_{key}"
        if dismiss_key not in st.session_state:
            st.session_state[dismiss_key] = False
        
        if not st.session_state[dismiss_key]:
            container = st.container()
            with container:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if message_type == 'success':
                        st.success(display_message)
                    elif message_type == 'warning':
                        st.warning(display_message)
                    elif message_type == 'error':
                        st.error(display_message)
                    else:
                        st.info(display_message)
                
                with col2:
                    if st.button("✕", key=dismiss_key):
                        st.session_state[dismiss_key] = True
                        st.rerun()
    else:
        # Non-dismissible message
        if message_type == 'success':
            st.success(display_message)
        elif message_type == 'warning':
            st.warning(display_message)
        elif message_type == 'error':
            st.error(display_message)
        else:
            st.info(display_message)

def create_toast_notification(
    message: str,
    toast_type: str = "info",
    duration: int = 5,
    key: Optional[str] = None
):
    """Create toast-style notifications that auto-dismiss"""
    import time
    
    if key is None:
        key = f"toast_{int(time.time() * 1000)}"
    
    # Store toast timestamp
    toast_key = f"toast_time_{key}"
    if toast_key not in st.session_state:
        st.session_state[toast_key] = time.time()
    
    # Check if toast should still be visible
    if time.time() - st.session_state[toast_key] < duration:
        create_feedback_message(
            message=message,
            message_type=toast_type,
            dismissible=True,
            key=key
        )
    else:
        # Clean up expired toast
        if toast_key in st.session_state:
            del st.session_state[toast_key]

# ================================
# RESPONSIVE LAYOUT COMPONENTS
# ================================

def create_responsive_columns(
    column_configs: List[Dict[str, any]],
    mobile_stack: bool = True
) -> List:
    """Create responsive columns that stack on mobile
    
    Args:
        column_configs: List of column configurations with 'ratio' and optional 'mobile_ratio'
        mobile_stack: Whether to stack columns on mobile
        
    Returns:
        List of column objects
    """
    # For now, use standard Streamlit columns
    # In future, could add JavaScript to detect screen size
    ratios = [config.get('ratio', 1) for config in column_configs]
    return st.columns(ratios)

def create_mobile_card(
    title: str,
    content: str,
    actions: Optional[List[Dict[str, any]]] = None,
    icon: Optional[str] = None,
    key_prefix: str = "mobile_card"
):
    """Create mobile-optimized card component"""
    with st.container(border=True):
        # Card header
        if icon or title:
            header_text = f"{icon} {title}" if icon else title
            st.subheader(header_text)
        
        # Card content
        if content:
            st.markdown(content)
        
        # Card actions
        if actions:
            st.divider()
            action_buttons = []
            for action in actions:
                action_buttons.append({
                    'key': action['key'],
                    'text': action['label'],
                    'type': action.get('type', 'secondary'),
                    'icon': action.get('icon'),
                    'size': 'medium'
                })
            
            return create_button_group(action_buttons, key_prefix, layout="horizontal")
    return {}

def create_mobile_nav_drawer(nav_items: List[Dict[str, str]], current_page: str):
    """Create mobile navigation drawer"""
    with st.sidebar:
        st.title("📱 Navigation")
        
        for item in nav_items:
            is_current = item['key'] == current_page
            button_type = 'primary' if is_current else 'secondary'
            
            if create_prominent_button(
                text=item['label'],
                key=f"nav_{item['key']}",
                button_type=button_type,
                icon=item.get('icon'),
                use_container_width=True
            ):
                # Return selected page key
                st.session_state['selected_page'] = item['key']
                st.rerun()
        
        return st.session_state.get('selected_page', current_page)

# ================================
# ACCESSIBILITY HELPERS
# ================================

def create_accessible_form_field(
    field_type: str,
    label: str,
    key: str,
    required: bool = False,
    help_text: Optional[str] = None,
    **kwargs
) -> any:
    """Create accessible form fields with proper labeling and help text"""
    # Add required indicator to label
    display_label = f"{label} *" if required else label
    
    # Create form field based on type
    if field_type == "text":
        return st.text_input(
            label=display_label,
            key=key,
            help=help_text,
            **kwargs
        )
    elif field_type == "textarea":
        return st.text_area(
            label=display_label,
            key=key,
            help=help_text,
            **kwargs
        )
    elif field_type == "select":
        return st.selectbox(
            label=display_label,
            key=key,
            help=help_text,
            **kwargs
        )
    elif field_type == "multiselect":
        return st.multiselect(
            label=display_label,
            key=key,
            help=help_text,
            **kwargs
        )
    elif field_type == "number":
        return st.number_input(
            label=display_label,
            key=key,
            help=help_text,
            **kwargs
        )
    elif field_type == "date":
        return st.date_input(
            label=display_label,
            key=key,
            help=help_text,
            **kwargs
        )
    elif field_type == "file":
        return st.file_uploader(
            label=display_label,
            key=key,
            help=help_text,
            **kwargs
        )
    else:
        st.error(f"Unsupported field type: {field_type}")
        return None

def create_skip_link(target_id: str, text: str = "Skip to main content"):
    """Create skip navigation link for accessibility"""
    st.markdown(f"""
    <a href="#{target_id}" class="sr-only sr-only-focusable" style="
        position: absolute;
        left: -10000px;
        top: auto;
        width: 1px;
        height: 1px;
        overflow: hidden;
    ">{text}</a>
    """, unsafe_allow_html=True)

def announce_to_screen_reader(message: str):
    """Announce messages to screen readers"""
    st.markdown(f"""
    <div aria-live="polite" aria-atomic="true" class="sr-only">
        {message}
    </div>
    """, unsafe_allow_html=True)