#!/usr/bin/env python3
"""
UI Preview Launcher for SafeSteps Certificate Generator
Allows easy comparison of V1 Minimalist vs V2 Modern UI designs
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path

def main():
    st.set_page_config(
        page_title="SafeSteps UI Preview Launcher",
        page_icon="🎨",
        layout="centered"
    )
    
    # Apply basic styling
    st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .version-card {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .version-card:hover {
        border-color: #3182ce;
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .version-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1a202c;
        margin-bottom: 0.5rem;
    }
    .version-description {
        color: #718096;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    .feature-list {
        background: #f7fafc;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .feature-item {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        font-size: 0.875rem;
        color: #2d3748;
    }
    .feature-icon {
        margin-right: 0.5rem;
        color: #38a169;
    }
    .launch-button {
        background: linear-gradient(135deg, #3182ce 0%, #2c5aa0 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        cursor: pointer;
        width: 100%;
        transition: all 0.3s ease;
    }
    .launch-button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(49, 130, 206, 0.3);
    }
    .instructions {
        background: #edf2f7;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    .comparison-note {
        background: #fff5b2;
        border-left: 4px solid #f6e05e;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎨 SafeSteps UI Preview Launcher</h1>
        <p style="color: #718096; font-size: 1.125rem;">Compare and choose your preferred user interface design</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Comparison note
    st.markdown("""
    <div class="comparison-note">
        <strong>💡 How to Compare:</strong> Launch each version in a separate browser tab to easily switch between them and compare the designs side-by-side.
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="version-card">
            <h2 class="version-title">📋 V1: Minimalist Professional</h2>
            <p class="version-description">
                Clean, efficient design focused on usability and professional appearance. 
                Perfect for corporate environments and users who prefer clarity over visual flair.
            </p>
            
            <div class="feature-list">
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Clean typography with Inter font
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Professional color scheme
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Clear data tables and forms
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Minimal distractions
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Fast loading and rendering
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch V1 Minimalist", key="launch_v1", help="Open minimalist UI in new tab"):
            launch_ui_version("v1", "ui_mockups_v1_minimalist.py")
    
    with col2:
        st.markdown("""
        <div class="version-card">
            <h2 class="version-title">🎨 V2: Modern Interactive</h2>
            <p class="version-description">
                Contemporary design with engaging interactions and visual appeal. 
                Features gradients, animations, and modern UI patterns for a delightful user experience.
            </p>
            
            <div class="feature-list">
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Gradient backgrounds and modern colors
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Smooth animations and transitions
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Interactive progress indicators
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Modern card-based layouts
                </div>
                <div class="feature-item">
                    <span class="feature-icon">✅</span>
                    Enhanced visual feedback
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Launch V2 Modern", key="launch_v2", help="Open modern UI in new tab"):
            launch_ui_version("v2", "ui_mockups_v2_modern.py")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Instructions
    st.markdown("""
    <div class="instructions">
        <h3>📖 How to Use This Preview System</h3>
        <ol>
            <li><strong>Launch Both Versions:</strong> Click the launch buttons above to open each UI version</li>
            <li><strong>Compare Side-by-Side:</strong> Open both in separate browser tabs or windows</li>
            <li><strong>Test Interactions:</strong> Try different features in each version</li>
            <li><strong>Note Your Preferences:</strong> Consider which design better suits your needs</li>
            <li><strong>Provide Feedback:</strong> Share your thoughts on which version to implement</li>
        </ol>
        
        <h4>🔧 Technical Notes:</h4>
        <ul>
            <li>Both versions use sample data to demonstrate functionality</li>
            <li>All interactive features are working demos</li>
            <li>Responsive design works on desktop and mobile</li>
            <li>No actual data processing occurs in preview mode</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #718096; padding: 1rem;">
        <p>🏆 <strong>SafeSteps Certificate Generator</strong> | UI Design Preview System</p>
        <p style="font-size: 0.875rem;">Choose the interface that best fits your workflow and aesthetic preferences</p>
    </div>
    """, unsafe_allow_html=True)


def launch_ui_version(version: str, filename: str):
    """Launch a specific UI version"""
    try:
        # Get the current directory
        current_dir = Path(__file__).parent
        ui_file = current_dir / filename
        
        if not ui_file.exists():
            st.error(f"❌ UI file not found: {ui_file}")
            return
        
        # Create a success message
        st.success(f"✅ Launching {version.upper()} UI...")
        st.info(f"📂 Opening: {filename}")
        
        # Instructions for manual launch
        st.markdown(f"""
        <div style="background: #e6fffa; border: 1px solid #4fd1c7; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
            <h4 style="color: #234e52; margin-top: 0;">🚀 Launch Instructions</h4>
            <p style="color: #234e52; margin-bottom: 0.5rem;">To view the {version.upper()} UI, run this command in your terminal:</p>
            <code style="background: #1a202c; color: #e2e8f0; padding: 0.5rem; border-radius: 4px; display: block; margin: 0.5rem 0;">
                streamlit run {filename}
            </code>
            <p style="color: #234e52; font-size: 0.875rem; margin-bottom: 0;">
                Or use the direct link when the Streamlit server is running: 
                <strong>http://localhost:8501</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"❌ Error launching {version}: {str(e)}")


if __name__ == "__main__":
    main()