# SafeSteps Enhanced UI Components Usage Guide

## Overview

The enhanced UI components system provides WCAG 2.2 AA compliant, mobile-first design elements that address the core SafeSteps usability issues:

- **Button Visibility Crisis**: All buttons meet minimum 44px touch targets (48px+ for primary actions)
- **Poor Visual Hierarchy**: Clear distinction between primary, secondary, and tertiary actions
- **Mobile UX Failure**: Responsive design with touch-friendly interfaces
- **Accessibility Issues**: Full WCAG 2.2 compliance with proper contrast ratios and keyboard navigation

## Enhanced Button System

### Basic Usage

```python
import streamlit as st
from utils.ui_components import create_prominent_button, apply_custom_css

# Apply enhanced CSS (call once per page)
apply_custom_css()

# Primary Button - 52px height, prominent styling
if create_prominent_button(
    text="Generate Certificates",
    key="primary_action",
    button_type="primary",
    size="large",
    icon="🎓",
    help_text="Create certificates for selected students"
):
    st.success("Generating certificates...")

# Secondary Button - 48px height, outline style
if create_prominent_button(
    text="Preview Template",
    key="secondary_action", 
    button_type="secondary",
    size="medium",
    icon="👁️"
):
    st.info("Opening preview...")

# Action Button with Semantic Colors
if create_prominent_button(
    text="Delete Selected",
    key="delete_action",
    button_type="danger",
    size="medium",
    icon="🗑️",
    help_text="This action cannot be undone"
):
    st.error("Deleting items...")
```

### Button Groups

```python
from utils.ui_components import create_enhanced_button_group

# Horizontal button group
buttons = [
    {'key': 'save', 'text': 'Save Draft', 'type': 'secondary', 'icon': '💾'},
    {'key': 'preview', 'text': 'Preview', 'type': 'secondary', 'icon': '👁️'},
    {'key': 'publish', 'text': 'Publish', 'type': 'primary', 'icon': '🚀'}
]

results = create_enhanced_button_group(buttons, "workflow", layout="horizontal")

if results['save']:
    st.success("Draft saved!")
elif results['preview']:
    st.info("Opening preview...")
elif results['publish']:
    st.success("Published successfully!")
```

### Workflow Step Buttons

```python
from utils.ui_components import create_workflow_step_button

# Multi-step workflow with clear progress indication
steps = [
    ("Upload Data", 1, False, True),   # Completed
    ("Validate Records", 2, True, False),  # Active
    ("Generate Certificates", 3, False, False),  # Pending
    ("Download Results", 4, False, False)  # Pending
]

for text, step_num, is_active, is_completed in steps:
    if create_workflow_step_button(
        text=text,
        step_number=step_num,
        is_active=is_active,
        is_completed=is_completed,
        key=f"step_{step_num}"
    ):
        st.info(f"Processing step {step_num}: {text}")
```

## Enhanced Color System (WCAG 2.2 AA Compliant)

### Color Usage Examples

```python
from utils.ui_components import COLORS

# All colors meet accessibility standards
st.markdown(f"""
<div style="background-color: {COLORS['primary']}; color: {COLORS['text_inverse']}; padding: 16px;">
    Primary Brand Color (21:1 contrast ratio)
</div>
""", unsafe_allow_html=True)

# Success message with proper contrast
st.success("✅ Action completed successfully!")

# Warning with accessible color
st.warning("⚠️ Please review your data before proceeding")

# Error message with high contrast
st.error("❌ An error occurred during processing")
```

## Loading States & Feedback

### Enhanced Loading Animation

```python
from utils.ui_components import create_enhanced_loading_state

# Basic loading
create_enhanced_loading_state("Processing certificates...")

# Loading with progress bar
create_enhanced_loading_state(
    text="Generating certificates",
    show_progress=True,
    progress_value=75
)

# Loading without spinner (for subtle feedback)
create_enhanced_loading_state(
    text="Validating data",
    show_spinner=False
)
```

### User Feedback Messages

```python
from utils.ui_components import create_feedback_message, create_toast_notification

# Dismissible success message
create_feedback_message(
    message="Certificates generated successfully!",
    message_type="success",
    dismissible=True,
    key="cert_success"
)

# Auto-dismissing toast notification
create_toast_notification(
    message="Data uploaded successfully",
    toast_type="success",
    duration=5,  # 5 seconds
    key="upload_toast"
)

# Warning message with custom icon
create_feedback_message(
    message="Some records may have validation issues",
    message_type="warning",
    icon="🔍"
)
```

## Mobile-First Responsive Design

### Responsive Cards

```python
from utils.ui_components import create_mobile_card

# Mobile-optimized card with actions
actions = [
    {'key': 'edit', 'label': 'Edit', 'type': 'secondary', 'icon': '✏️'},
    {'key': 'delete', 'label': 'Delete', 'type': 'danger', 'icon': '🗑️'}
]

results = create_mobile_card(
    title="Digital Citizenship Course",
    content="A comprehensive course covering online safety, digital footprints, and responsible technology use.",
    actions=actions,
    icon="🎓",
    key_prefix="course_card"
)

if results.get('edit'):
    st.info("Opening editor...")
elif results.get('delete'):
    st.error("Deleting course...")
```

### Mobile Navigation

```python
from utils.ui_components import create_mobile_nav_drawer

nav_items = [
    {'key': 'dashboard', 'label': 'Dashboard', 'icon': '📊'},
    {'key': 'certificates', 'label': 'Certificates', 'icon': '🎓'},
    {'key': 'templates', 'label': 'Templates', 'icon': '📄'},
    {'key': 'users', 'label': 'Users', 'icon': '👥'}
]

current_page = create_mobile_nav_drawer(nav_items, st.session_state.get('current_page', 'dashboard'))
```

## Accessibility Features

### Accessible Form Fields

```python
from utils.ui_components import create_accessible_form_field

# Text input with proper labeling
student_name = create_accessible_form_field(
    field_type="text",
    label="Student Name",
    key="student_name",
    required=True,
    help_text="Enter the full name as it should appear on the certificate",
    placeholder="e.g., John Smith"
)

# Dropdown with accessibility support
course_selection = create_accessible_form_field(
    field_type="select",
    label="Course Template",
    key="course_template",
    required=True,
    help_text="Choose the appropriate certificate template",
    options=["Digital Citizenship", "Online Safety", "Technology Skills"]
)

# File upload with proper labeling
uploaded_file = create_accessible_form_field(
    field_type="file",
    label="Student Data File",
    key="student_data",
    required=True,
    help_text="Upload a CSV file with student information",
    type=['csv', 'xlsx']
)
```

### Screen Reader Support

```python
from utils.ui_components import announce_to_screen_reader, create_skip_link

# Skip navigation for accessibility
create_skip_link("main-content", "Skip to certificate generation")

# Announce status changes to screen readers
if st.button("Generate Certificates"):
    announce_to_screen_reader("Certificate generation started")
    # ... processing logic ...
    announce_to_screen_reader("25 certificates generated successfully")
```

## Implementation Examples

### Complete Workflow Page

```python
import streamlit as st
from utils.ui_components import (
    apply_custom_css, create_prominent_button, create_enhanced_button_group,
    create_workflow_step_button, create_enhanced_loading_state,
    create_feedback_message, COLORS
)

# Apply enhanced styling
apply_custom_css()

st.title("🎓 Certificate Generation Workflow")

# Current step tracking
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# Workflow steps
steps = [
    "Upload Student Data",
    "Select Certificate Template", 
    "Preview & Validate",
    "Generate Certificates",
    "Download Results"
]

# Display workflow progress
st.subheader("Progress")
cols = st.columns(len(steps))
for idx, step in enumerate(steps):
    with cols[idx]:
        step_num = idx + 1
        is_active = step_num == st.session_state.current_step
        is_completed = step_num < st.session_state.current_step
        
        if create_workflow_step_button(
            text=step,
            step_number=step_num,
            is_active=is_active,
            is_completed=is_completed,
            key=f"workflow_step_{step_num}"
        ):
            if is_completed:
                st.session_state.current_step = step_num

st.divider()

# Step content based on current step
if st.session_state.current_step == 1:
    st.subheader("📤 Upload Student Data")
    
    uploaded_file = st.file_uploader(
        "Choose student data file",
        type=['csv', 'xlsx'],
        help="Upload a CSV or Excel file with student information"
    )
    
    if uploaded_file:
        if create_prominent_button(
            text="Validate Data",
            key="validate_data",
            button_type="primary",
            icon="✅",
            help_text="Check data format and completeness"
        ):
            create_enhanced_loading_state("Validating student data...")
            # Validation logic here
            st.session_state.current_step = 2
            st.rerun()

elif st.session_state.current_step == 2:
    st.subheader("📄 Select Certificate Template")
    
    template = st.selectbox(
        "Certificate Template",
        ["Digital Citizenship", "Online Safety", "Technology Skills"],
        help="Choose the appropriate certificate template"
    )
    
    # Navigation buttons
    nav_buttons = [
        {'key': 'back', 'text': 'Back', 'type': 'secondary', 'icon': '⬅️'},
        {'key': 'continue', 'text': 'Continue', 'type': 'primary', 'icon': '➡️'}
    ]
    
    results = create_enhanced_button_group(nav_buttons, "step2_nav")
    
    if results['back']:
        st.session_state.current_step = 1
        st.rerun()
    elif results['continue']:
        st.session_state.current_step = 3
        st.rerun()

# Add more steps as needed...

# Success message example
if st.session_state.current_step >= 5:
    create_feedback_message(
        message="🎉 All certificates generated successfully!",
        message_type="success",
        dismissible=True,
        key="completion_message"
    )
```

This enhanced UI components system transforms SafeSteps from a difficult-to-use application into an accessible, mobile-friendly, and visually appealing platform that meets modern usability standards.