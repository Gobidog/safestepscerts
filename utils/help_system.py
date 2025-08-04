"""
Help System for User-Friendly Guidance
Provides interactive tutorials and contextual help
"""
import streamlit as st

class HelpSystem:
    """Interactive help and tutorial system"""
    
    def __init__(self):
        self.help_topics = {
            "upload_help": {
                "title": "File Upload Help",
                "content": """
                **Uploading Your Data File**
                
                ✅ **Supported Formats**: CSV, Excel (.xlsx)
                
                📋 **Required Columns**:
                - Name: Student's full name
                - Course: Course name or code
                - Date: Completion date (optional)
                
                💡 **Tips**:
                - Ensure no empty rows in your file
                - Check that names don't contain special characters
                - Dates should be in YYYY-MM-DD format
                """
            },
            "validation_help": {
                "title": "Data Validation Help",
                "content": """
                **Understanding Validation Results**
                
                🟢 **Valid Entries**: Ready for certificate generation
                🟡 **Warnings**: Minor issues that won't prevent generation
                🔴 **Errors**: Must be fixed before proceeding
                
                **Common Issues**:
                - Missing required fields
                - Invalid date formats
                - Duplicate entries
                """
            },
            "template_help": {
                "title": "Template Selection Help",
                "content": """
                **Choosing the Right Template**
                
                Consider:
                - Your organization's branding
                - The formality of the course
                - Print vs. digital distribution
                
                All templates are professionally designed and customizable.
                """
            }
        }
    
    def show_tooltip(self, topic_key, text):
        """Show a help tooltip"""
        if st.button("ℹ️", key=f"help_{topic_key}", help=text):
            self.show_help_modal(topic_key)
    
    def show_help_modal(self, topic_key=None):
        """Show help in a modal-like expander"""
        if topic_key and topic_key in self.help_topics:
            topic = self.help_topics[topic_key]
            with st.expander(f"📚 {topic['title']}", expanded=True):
                st.markdown(topic['content'])
        else:
            # Show general help
            with st.expander("📚 Help Center", expanded=True):
                st.markdown("""
                ### Welcome to SafeSteps Help
                
                **Quick Links:**
                - [Getting Started](#getting-started)
                - [File Formats](#file-formats)
                - [Troubleshooting](#troubleshooting)
                - [Contact Support](#contact-support)
                
                ---
                
                #### Getting Started
                1. Upload your student data file
                2. Review validation results
                3. Choose a certificate template
                4. Generate certificates
                5. Download your certificates
                
                #### File Formats
                We support CSV and Excel files with these columns:
                - **Name** (required)
                - **Course** (required)
                - **Date** (optional)
                
                #### Troubleshooting
                **Q: My file won't upload**
                A: Check that it's under 10MB and in CSV/Excel format
                
                **Q: Validation shows errors**
                A: Download the error report to see specific issues
                
                #### Contact Support
                📧 support@safesteps.com
                📞 1-800-SAFESTEP
                """)
    
    def show_welcome_tutorial(self):
        """Show welcome tutorial for first-time users"""
        with st.info("👋 Welcome to SafeSteps Certificate Generator!"):
            st.markdown("""
            This guided workflow will help you create professional certificates in just 5 easy steps:
            
            1️⃣ **Upload** - Import your student data
            2️⃣ **Validate** - We'll check for any issues
            3️⃣ **Design** - Choose from beautiful templates
            4️⃣ **Generate** - Create all certificates at once
            5️⃣ **Download** - Get your certificates
            
            **Need help at any step?** Look for the ℹ️ icons or click the Help button!
            """)
            
            if st.button("Let's Get Started! 🚀", type="primary"):
                st.session_state.tutorial_completed = True
                st.rerun()
    
    def show_inline_help(self, message, type="info"):
        """Show inline help message"""
        if type == "info":
            st.info(f"💡 {message}")
        elif type == "warning":
            st.warning(f"⚠️ {message}")
        elif type == "error":
            st.error(f"❌ {message}")
        elif type == "success":
            st.success(f"✅ {message}")
    
    def create_step_guide(self, step_number, total_steps):
        """Create a step-by-step guide"""
        guides = {
            1: "Start by clicking the upload button and selecting your data file",
            2: "Review the validation results and fix any errors if needed",
            3: "Browse templates and preview them before making your selection",
            4: "Configure any additional options and start the generation process",
            5: "Download your certificates and share them with students"
        }
        
        return guides.get(step_number, "Follow the on-screen instructions")

def create_contextual_help(content: str, position: str = "top"):
    """Create contextual help tooltip"""
    help_id = f"help_{hash(content)}"
    
    if position == "top":
        st.info(f"ℹ️ {content}")
    elif position == "sidebar":
        with st.sidebar:
            st.info(f"ℹ️ {content}")
    else:
        st.caption(f"💡 {content}")

def show_help_modal():
    """Show help modal dialog"""
    if st.session_state.get('show_help_modal', False):
        with st.container(border=True):
            st.markdown("### 📚 Help Center")
            
            help_tabs = st.tabs(["Getting Started", "Features", "FAQ", "Contact"])
            
            with help_tabs[0]:
                st.markdown("""
                **Welcome to SafeSteps!**
                
                Here's how to get started:
                1. Navigate to Certificate Generation
                2. Upload your student data (CSV or Excel)
                3. Select a certificate template
                4. Generate and download certificates
                """)
            
            with help_tabs[1]:
                st.markdown("""
                **Key Features:**
                - 🏆 Bulk certificate generation
                - 📄 Custom templates
                - 👥 User management
                - 📊 Analytics and reporting
                - 🔐 Secure authentication
                """)
            
            with help_tabs[2]:
                st.markdown("""
                **Frequently Asked Questions:**
                
                **Q: What file formats are supported?**
                A: CSV and Excel (.xlsx) files
                
                **Q: How many certificates can I generate?**
                A: There's no limit!
                
                **Q: Can I customize templates?**
                A: Yes, you can upload custom templates.
                """)
            
            with help_tabs[3]:
                st.markdown("""
                **Need Help?**
                
                - 📧 Email: support@safesteps.local
                - 📱 Phone: 1-800-SAFESTEP
                - 💬 Chat: Available 9am-5pm EST
                """)
            
            if st.button("Close Help", key="close_help_modal"):
                st.session_state['show_help_modal'] = False
                st.rerun()

def create_guided_tour(tour_id: str, steps: list):
    """Create a guided tour for onboarding"""
    if not st.session_state.get(f'tour_{tour_id}_completed', False):
        current_step = st.session_state.get(f'tour_{tour_id}_step', 0)
        
        if current_step < len(steps):
            step = steps[current_step]
            
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### {step['title']}")
                    st.markdown(step['content'])
                
                with col2:
                    st.markdown(f"Step {current_step + 1} of {len(steps)}")
                    
                    if st.button("Next →", key=f"tour_{tour_id}_next"):
                        st.session_state[f'tour_{tour_id}_step'] = current_step + 1
                        if current_step + 1 >= len(steps):
                            st.session_state[f'tour_{tour_id}_completed'] = True
                        st.rerun()
                    
                    if st.button("Skip Tour", key=f"tour_{tour_id}_skip"):
                        st.session_state[f'tour_{tour_id}_completed'] = True
                        st.rerun()