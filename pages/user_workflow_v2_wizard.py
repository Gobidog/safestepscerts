"""
User Workflow Version 2: User-Friendly Guidance
Interactive wizard with tutorials and contextual help
"""
import streamlit as st
from utils.help_system import HelpSystem
from utils.workflow_persistence import WorkflowPersistence
from utils.ui_components import create_progress_steps
from utils.validators import SpreadsheetValidator
from utils.pdf_generator import PDFGenerator
from utils.storage import StorageManager
from pathlib import Path
import time

def render_user_workflow_v2():
    """Render the guided user workflow"""
    
    # Initialize systems
    help_system = HelpSystem()
    workflow = WorkflowPersistence()
    storage = StorageManager()
    
    # Show tutorial on first visit
    if 'v2_tutorial_shown' not in st.session_state:
        help_system.show_welcome_tutorial()
        st.session_state.v2_tutorial_shown = True
    
    # Header with help button
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🎓 Guided Certificate Generation")
    with col2:
        if st.button("📚 Help", use_container_width=True):
            help_system.show_help_modal()
    with col3:
        if st.button("💾 Save Progress", use_container_width=True):
            workflow.save_progress(st.session_state)
            st.success("Progress saved!")
    
    # Check for saved progress
    if workflow.has_saved_progress():
        with st.info("💡 You have saved progress. Would you like to resume?"):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Resume", type="primary"):
                    workflow.load_progress(st.session_state)
            with col2:
                if st.button("Start Fresh"):
                    workflow.clear_progress()
    
    # Enhanced progress indicator
    current_step = st.session_state.get('wizard_step', 1)
    create_progress_steps(current_step, 5)
    
    # Step-by-step wizard
    if current_step == 1:
        render_step1_upload()
    elif current_step == 2:
        render_step2_validate()
    elif current_step == 3:
        render_step3_template()
    elif current_step == 4:
        render_step4_generate()
    elif current_step == 5:
        render_step5_complete()

def render_step1_upload():
    """Step 1: File Upload with guidance"""
    help_system = HelpSystem()
    
    st.header("Step 1: Upload Your Data")
    help_system.show_tooltip("upload_help", 
        "Upload a CSV or Excel file containing student names and course information")
    
    # Template preview
    with st.expander("📋 See Example Format", expanded=True):
        st.markdown("""
        Your file should have these columns:
        - **Name**: Student's full name
        - **Course**: Course name or code
        - **Date**: Completion date (optional)
        
        Example:
        | Name | Course | Date |
        |------|--------|------|
        | John Doe | Safety 101 | 2024-01-15 |
        | Jane Smith | First Aid | 2024-01-16 |
        """)
        
        if st.button("📥 Download Sample Template"):
            # Create sample file
            sample_data = """Name,Course,Date
John Doe,Safety 101,2024-01-15
Jane Smith,First Aid,2024-01-16"""
            st.download_button(
                "Download",
                sample_data,
                "sample_template.csv",
                "text/csv"
            )
    
    # File upload with preview
    uploaded_file = st.file_uploader(
        "Choose your file",
        type=['csv', 'xlsx'],
        help="Supported formats: CSV, Excel"
    )
    
    if uploaded_file:
        # Preview file
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show preview
        if st.checkbox("Preview file contents"):
            try:
                if uploaded_file.name.endswith('.csv'):
                    import pandas as pd
                    df = pd.read_csv(uploaded_file)
                    st.dataframe(df.head())
                st.info(f"File contains {len(df)} rows")
            except Exception as e:
                st.error(f"Preview error: {str(e)}")
        
        # Save and continue
        col1, col2 = st.columns(2)
        with col2:
            if st.button("Continue →", type="primary", use_container_width=True):
                st.session_state.wizard_uploaded_file = uploaded_file
                st.session_state.wizard_step = 2
                st.rerun()
    else:
        help_system.show_inline_help("No file uploaded yet. Click the upload button above to get started!")

def render_step2_validate():
    """Step 2: Data validation with error help"""
    st.header("Step 2: Validate Your Data")
    
    if 'wizard_uploaded_file' not in st.session_state:
        st.error("No file uploaded. Please complete Step 1.")
        if st.button("← Back to Step 1"):
            st.session_state.wizard_step = 1
            st.rerun()
        return
    
    # Validation with helpful error messages
    validator = SpreadsheetValidator()
    
    with st.spinner("Checking your data..."):
        time.sleep(1)  # Simulate processing
        
        # Mock validation for demo
        validation_results = {
            'valid': True,
            'total_rows': 25,
            'valid_rows': 23,
            'errors': [
                {'row': 5, 'issue': 'Missing course name'},
                {'row': 12, 'issue': 'Invalid date format'}
            ]
        }
    
    # Show results with guidance
    if validation_results['valid']:
        st.success(f"✅ Data validated! {validation_results['valid_rows']} valid entries found.")
    
    if validation_results['errors']:
        with st.warning("⚠️ Some issues found (but we can still proceed!)"):
            st.markdown("**Issues to review:**")
            for error in validation_results['errors']:
                st.markdown(f"- Row {error['row']}: {error['issue']}")
            
            help_system = HelpSystem()
            help_system.show_inline_help(
                "These rows will be skipped. You can fix them and re-upload, or continue with valid rows only."
            )
    
    # Options
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    with col2:
        if st.button("Fix & Re-upload", use_container_width=True):
            st.session_state.wizard_step = 1
            st.rerun()
    with col3:
        if st.button("Continue →", type="primary", use_container_width=True):
            st.session_state.wizard_validated_data = validation_results
            st.session_state.wizard_step = 3
            st.rerun()

def render_step3_template():
    """Step 3: Template selection with preview"""
    st.header("Step 3: Choose Your Template")
    
    # Template gallery with previews
    templates = [
        {
            'name': 'Professional Blue',
            'description': 'Clean, professional design with blue accents',
            'preview': '🔵'
        },
        {
            'name': 'Modern Green',
            'description': 'Contemporary design with nature-inspired colors',
            'preview': '🟢'
        },
        {
            'name': 'Classic Gold',
            'description': 'Traditional certificate with gold borders',
            'preview': '🟡'
        }
    ]
    
    st.markdown("### Available Templates")
    
    selected_template = None
    cols = st.columns(3)
    
    for idx, template in enumerate(templates):
        with cols[idx]:
            with st.container(border=True):
                st.markdown(f"### {template['preview']} {template['name']}")
                st.markdown(template['description'])
                
                if st.button(f"Preview", key=f"preview_{idx}"):
                    st.info("Template preview would appear here")
                
                if st.button(f"Select This", key=f"select_{idx}", type="primary", use_container_width=True):
                    selected_template = template['name']
                    st.session_state.wizard_selected_template = selected_template
    
    # Navigation
    if st.session_state.get('wizard_selected_template'):
        st.success(f"✅ Selected: {st.session_state.wizard_selected_template}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Continue →", type="primary", use_container_width=True):
                st.session_state.wizard_step = 4
                st.rerun()

def render_step4_generate():
    """Step 4: Generate certificates with preview"""
    st.header("Step 4: Generate Certificates")
    
    # Preview before generation
    st.markdown("### Preview")
    with st.container(border=True):
        st.markdown("**Sample Certificate Preview**")
        st.info("Certificate for: John Doe")
        st.info("Course: Safety 101")
        st.info("Template: " + st.session_state.get('wizard_selected_template', 'Professional Blue'))
    
    # Generation options
    st.markdown("### Options")
    col1, col2 = st.columns(2)
    with col1:
        add_date = st.checkbox("Add today's date", value=True)
    with col2:
        add_signature = st.checkbox("Add signature line", value=True)
    
    # Confirmation
    st.warning("⚠️ Please review the preview above before generating all certificates.")
    
    # Generate button
    if st.button("🎯 Generate All Certificates", type="primary", use_container_width=True):
        # Progress bar
        progress = st.progress(0)
        status = st.empty()
        
        for i in range(100):
            progress.progress(i + 1)
            if i < 30:
                status.text("Preparing templates...")
            elif i < 60:
                status.text("Generating certificates...")
            elif i < 90:
                status.text("Creating ZIP file...")
            else:
                status.text("Finalizing...")
            time.sleep(0.02)
        
        st.session_state.wizard_generated_files = True
        st.session_state.wizard_step = 5
        st.rerun()
    
    # Back button
    if st.button("← Back"):
        st.session_state.wizard_step = 3
        st.rerun()

def render_step5_complete():
    """Step 5: Completion with download"""
    st.balloons()
    st.header("🎉 Certificates Generated Successfully!")
    
    # Summary
    with st.success("All certificates have been generated!"):
        st.markdown("""
        **Summary:**
        - ✅ 23 certificates created
        - 📁 Packaged in ZIP file
        - 📥 Ready for download
        """)
    
    # Download button
    st.download_button(
        label="📥 Download All Certificates (ZIP)",
        data=b"Mock ZIP data",  # In real implementation, this would be actual ZIP
        file_name="certificates_batch.zip",
        mime="application/zip",
        use_container_width=True
    )
    
    # Additional options
    st.markdown("### What's Next?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Email Certificates", use_container_width=True):
            st.info("Email feature coming soon!")
    
    with col2:
        if st.button("📊 View Report", use_container_width=True):
            st.info("Report feature coming soon!")
    
    with col3:
        if st.button("🔄 Start New Batch", use_container_width=True):
            # Clear workflow
            for key in list(st.session_state.keys()):
                if key.startswith('wizard_'):
                    del st.session_state[key]
            st.session_state.wizard_step = 1
            st.rerun()
    
    # Help section
    with st.expander("❓ Need Help?"):
        st.markdown("""
        **Common Questions:**
        
        **Q: How do I print the certificates?**
        A: Open the ZIP file and print each PDF individually or use batch printing.
        
        **Q: Can I regenerate specific certificates?**
        A: Yes! Go back to Step 1 and upload a file with only the certificates you need.
        
        **Q: Where are my certificates stored?**
        A: They're in your Downloads folder after clicking the download button.
        """)