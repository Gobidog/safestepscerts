"""
Mobile Optimization Demo Page
Demonstrates all mobile optimization features in SafeSteps
"""
import streamlit as st
from utils.mobile_optimization import (
    apply_global_mobile_optimizations, create_mobile_button, 
    get_device_info, is_mobile, create_responsive_columns,
    MobileOptimizer, TouchTargetOptimizer, MobileNavigation
)
from utils.ui_components import create_card, create_metric_card, apply_custom_css
from utils.auth import get_current_user

def render_mobile_demo():
    """Render mobile optimization demo page"""
    
    # Apply optimizations
    apply_custom_css()
    mobile_optimizer = apply_global_mobile_optimizations()
    
    # Get device info
    device_info = get_device_info()
    current_user = get_current_user()
    
    # Page header with responsive layout
    st.title("📱 Mobile Optimization Demo")
    st.markdown("**Experience SafeSteps optimized for your device**")
    
    # Device information card
    with st.container():
        st.subheader("🔍 Device Detection")
        
        cols = st.columns(create_responsive_columns([1], [1, 1], [1, 1, 1]))
        
        with cols[0]:
            device_type = "📱 Mobile" if device_info['is_mobile'] else "📱 Tablet" if device_info['is_tablet'] else "🖥️ Desktop"
            st.metric("Device Type", device_type)
        
        if len(cols) > 1:
            with cols[1]:
                st.metric("Browser", device_info['browser'])
        
        if len(cols) > 2:
            with cols[2]:
                st.metric("Operating System", device_info['os'])
    
    st.divider()
    
    # Touch Target Demo
    st.subheader("👆 Touch Target Optimization")
    st.markdown("All buttons meet WCAG 2.2 accessibility standards with minimum 44px touch targets.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Primary Actions (Large - 56px+)**")
        if create_mobile_button("Generate Certificate", "demo_primary", button_type="primary", size="large", icon="🏆"):
            st.success("✅ Primary action triggered!")
        
        if create_mobile_button("Upload Students", "demo_upload", button_type="secondary", size="large", icon="📤"):
            st.info("📁 File upload action!")
    
    with col2:
        st.markdown("**Secondary Actions (Standard - 48px+)**")
        if create_mobile_button("Save Draft", "demo_save", button_type="success", size="medium", icon="💾"):
            st.success("💾 Draft saved!")
        
        if create_mobile_button("Preview", "demo_preview", button_type="secondary", size="medium", icon="👁️"):
            st.info("👁️ Preview opened!")
    
    st.divider()
    
    # Form Optimization Demo
    st.subheader("📝 Mobile-Optimized Forms")
    st.markdown("Large touch targets and mobile-friendly input methods.")\n    \n    # Create a mobile-optimized form\n    form_fields = [\n        {\n            'type': 'text',\n            'key': 'student_name',\n            'label': 'Student Name',\n            'required': True,\n            'placeholder': 'Enter full name',\n            'help': 'First and last name of the student'\n        },\n        {\n            'type': 'email',\n            'key': 'student_email',\n            'label': 'Email Address',\n            'required': True,\n            'placeholder': 'student@example.com'\n        },\n        {\n            'type': 'select',\n            'key': 'course_name',\n            'label': 'Course Completed',\n            'required': True,\n            'options': ['Workplace Safety', 'Fire Safety', 'First Aid', 'Manual Handling'],\n            'help': 'Select the completed course'\n        },\n        {\n            'type': 'date',\n            'key': 'completion_date',\n            'label': 'Completion Date',\n            'required': True,\n            'help': 'Date when the course was completed'\n        },\n        {\n            'type': 'select',\n            'key': 'result',\n            'label': 'Result',\n            'required': True,\n            'options': ['Pass', 'Fail', 'Distinction'],\n            'default_index': 0\n        }\n    ]\n    \n    form_data = mobile_optimizer.create_mobile_optimized_form(form_fields)\n    \n    if form_data:\n        st.success("🎉 Form submitted successfully!")\n        st.json(form_data)\n    \n    st.divider()\n    \n    # Navigation Demo\n    st.subheader("🧭 Mobile Navigation")\n    \n    if device_info['is_mobile']:\n        st.markdown("**Bottom Navigation Bar** (Mobile Only)")\n        st.markdown("Below you would see a bottom navigation bar with thumb-friendly buttons.")\n        \n        # Demo bottom navigation HTML\n        nav = MobileNavigation()\n        nav_items = [\n            {'key': 'home', 'label': 'Home', 'icon': '🏠', 'active': True},\n            {'key': 'generate', 'label': 'Generate', 'icon': '🏆'},\n            {'key': 'manage', 'label': 'Manage', 'icon': '📋'},\n            {'key': 'account', 'label': 'Account', 'icon': '👤'}\n        ]\n        \n        bottom_nav_html = nav.create_bottom_nav(nav_items)\n        st.markdown(bottom_nav_html, unsafe_allow_html=True)\n        \n        st.markdown("**Floating Action Button**")\n        fab_html = nav.create_floating_action_button("⚡", "Quick Generate", "bottom-right")\n        st.markdown(fab_html, unsafe_allow_html=True)\n        \n    else:\n        st.info("📱 Mobile navigation features are automatically enabled on mobile devices.")\n    \n    st.divider()\n    \n    # Responsive Layout Demo\n    st.subheader("📐 Responsive Layout System")\n    \n    layout_config = mobile_optimizer.get_responsive_layout('dashboard')\n    st.markdown(f"**Current Layout Configuration:** `{layout_config}`")\n    \n    # Demo metrics with responsive columns\n    st.markdown("**Responsive Metrics Grid**")\n    \n    cols = st.columns(create_responsive_columns([1], [1, 1], [1, 1, 1, 1]))\n    \n    metrics_data = [\n        ("Total Certificates", "1,234", "📜"),\n        ("Active Courses", "12", "📚"),\n        ("Students Enrolled", "456", "🎓"),\n        ("Success Rate", "98%", "✅")\n    ]\n    \n    for i, (label, value, icon) in enumerate(metrics_data):\n        if i < len(cols):\n            with cols[i]:\n                st.metric(f"{icon} {label}", value)\n    \n    st.divider()\n    \n    # Accessibility Features\n    st.subheader("♿ Accessibility Features")\n    \n    accessibility_features = [\n        "✅ **WCAG 2.2 Level AA Compliance** - All interactive elements meet accessibility standards",\n        "✅ **44px+ Touch Targets** - Comfortable finger tapping on all buttons",\n        "✅ **High Contrast Colors** - 4.5:1+ contrast ratios for text readability",\n        "✅ **Focus Indicators** - Clear visual focus for keyboard navigation",\n        "✅ **Screen Reader Support** - Proper ARIA labels and semantic HTML",\n        "✅ **Reduced Motion Support** - Respects user's motion preferences",\n        "✅ **Scalable Text** - Works with browser zoom up to 200%"\n    ]\n    \n    for feature in accessibility_features:\n        st.markdown(feature)\n    \n    st.divider()\n    \n    # Performance Information\n    st.subheader("⚡ Performance Optimizations")\n    \n    perf_info = [\n        "🚀 **Mobile-First CSS** - Optimized styles load faster on mobile",\n        "📱 **Touch-Optimized Interactions** - Reduced cognitive load",\n        "🎯 **Progressive Enhancement** - Works without JavaScript",\n        "📊 **Efficient Layouts** - CSS Grid and Flexbox for responsive design",\n        "⚡ **Minimal JavaScript** - Core functionality in Python/Streamlit",\n        "🔧 **Optimized Forms** - Proper input types for mobile keyboards"\n    ]\n    \n    for info in perf_info:\n        st.markdown(info)\n    \n    # User feedback section\n    st.divider()\n    st.subheader("💬 User Experience Feedback")\n    \n    col1, col2 = st.columns(2)\n    \n    with col1:\n        if create_mobile_button("👍 Great Experience", "feedback_good", button_type="success", size="medium"):\n            st.balloons()\n            st.success("Thank you for your feedback!")\n    \n    with col2:\n        if create_mobile_button("👎 Needs Improvement", "feedback_bad", button_type="warning", size="medium"):\n            st.info("We appreciate your feedback and are working to improve!")\n    \n    # Footer with app info\n    st.divider()\n    st.caption(f"SafeSteps Mobile-Optimized | User: {current_user.get('username', 'Unknown')} | Device: {device_info['device']}")\n    \n    # Add gesture instructions for mobile\n    if device_info['is_mobile']:\n        st.info("💡 **Mobile Tip:** Swipe left/right to navigate between pages, pull down to refresh!")\n        \n        # Enable swipe gestures\n        from utils.mobile_optimization import MobileGestures\n        gestures = MobileGestures()\n        swipe_script = gestures.enable_swipe_navigation(['home', 'generate', 'account'])\n        st.markdown(swipe_script, unsafe_allow_html=True)

if __name__ == "__main__":\n    render_mobile_demo()