"""
UI Mockup Implementation - Version 2: Modern Interactive
Contemporary design with engaging interactions and visual appeal
"""

import streamlit as st
from typing import Dict, List, Optional, Callable
import pandas as pd
import time
import random

# Color constants for V2 - Modern Interactive
MODERN_COLORS = {
    'gradient_primary': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'gradient_secondary': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'gradient_success': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'primary_purple': '#667eea',
    'primary_pink': '#f093fb', 
    'accent_blue': '#4facfe',
    'accent_green': '#00f2fe',
    'dark_bg': '#0f0f23',
    'dark_surface': '#16213e',
    'dark_text': '#e2e8f0'
}

def apply_modern_theme():
    """Apply modern interactive theme with animations"""
    st.markdown("""
    <style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global styles */
    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Modern header */
    .modern-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .modern-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        animation: shimmer 3s infinite;
    }
    
    .header-brand {
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    
    .brand-icon {
        font-size: 2.5rem;
        margin-right: 1rem;
        animation: pulse 2s infinite;
    }
    
    .brand-title {
        font-family: 'Poppins', sans-serif;
        font-size: 2.25rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .brand-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
        font-weight: 400;
    }
    
    .user-profile {
        display: flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.75rem 1rem;
        border-radius: 50px;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .user-profile:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    .profile-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        margin-right: 0.75rem;
        color: white;
    }
    
    /* Interactive progress flow */
    .progress-flow {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out 0.2s both;
    }
    
    .flow-background {
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 2px;
        transform: translateY(-50%);
    }
    
    .flow-line {
        height: 100%;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 1px;
        transition: width 1s ease-in-out;
    }
    
    .step-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 1;
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        max-width: 120px;
        text-align: center;
    }
    
    .step-circle {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        position: relative;
        transition: all 0.3s ease;
    }
    
    .step-inner {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 1.125rem;
        transition: all 0.3s ease;
    }
    
    .step.completed .step-circle {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        box-shadow: 0 4px 15px rgba(79, 172, 254, 0.4);
    }
    
    .step.completed .step-inner {
        background: white;
        color: #4facfe;
    }
    
    .step.active .step-circle {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .step.active .step-inner {
        background: white;
        color: #667eea;
        animation: pulse 2s infinite;
    }
    
    .step.active .step-pulse {
        position: absolute;
        top: -5px;
        left: -5px;
        right: -5px;
        bottom: -5px;
        border: 2px solid #667eea;
        border-radius: 50%;
        opacity: 0.6;
        animation: pulse 2s infinite;
    }
    
    .step.pending .step-circle {
        background: #f1f5f9;
        border: 2px solid #e2e8f0;
    }
    
    .step.pending .step-inner {
        color: #94a3b8;
    }
    
    .step-title {
        font-weight: 600;
        font-size: 0.875rem;
        color: #1e293b;
        margin: 0 0 0.25rem 0;
    }
    
    .step-description {
        font-size: 0.75rem;
        color: #64748b;
        margin: 0;
    }
    
    /* Dashboard cards */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .dashboard-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .dashboard-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
    
    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .dashboard-card.success::before {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    
    .dashboard-card.warning::before {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
    }
    
    .card-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-right: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .card-title h3 {
        font-family: 'Poppins', sans-serif;
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        margin: 0 0 0.25rem 0;
    }
    
    .card-title p {
        font-size: 0.875rem;
        color: #64748b;
        margin: 0;
    }
    
    .metric-display {
        text-align: center;
    }
    
    .metric-number {
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    .metric-trend {
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.5rem;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        display: inline-block;
    }
    
    .metric-trend.positive {
        background: #dcfce7;
        color: #166534;
    }
    
    .metric-trend.negative {
        background: #fef2f2;
        color: #dc2626;
    }
    
    /* Progress ring */
    .progress-ring {
        position: relative;
        width: 120px;
        height: 120px;
        margin: 0 auto;
    }
    
    .progress-value {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-family: 'Poppins', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
    }
    
    .progress-svg {
        width: 100%;
        height: 100%;
        transform: rotate(-90deg);
    }
    
    .progress-circle {
        fill: none;
        stroke: #e2e8f0;
        stroke-width: 8;
        stroke-linecap: round;
        transition: stroke-dasharray 1s ease-in-out;
    }
    
    .progress-circle.active {
        stroke: url(#progressGradient);
        stroke-dasharray: 283;
        stroke-dashoffset: 28.3;
        animation: rotate 2s linear infinite;
    }
    
    /* Interactive table */
    .interactive-table {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        animation: fadeInUp 0.6s ease-out 0.4s both;
    }
    
    .table-controls {
        padding: 1.5rem;
        background: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .search-container {
        position: relative;
        flex: 1;
        min-width: 250px;
    }
    
    .search-icon {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        color: #64748b;
        font-size: 1rem;
    }
    
    .search-input {
        width: 100%;
        padding: 0.75rem 1rem 0.75rem 2.5rem;
        border: 2px solid #e2e8f0;
        border-radius: 50px;
        font-size: 0.875rem;
        transition: all 0.3s ease;
        background: white;
    }
    
    .search-input:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .filter-chips {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    .chip {
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid #e2e8f0;
        background: white;
        color: #64748b;
    }
    
    .chip.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
    
    .chip:hover:not(.active) {
        border-color: #667eea;
        color: #667eea;
    }
    
    /* Modern table styling */
    .modern-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .modern-table th {
        background: #f8fafc;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.875rem;
        color: #374151;
        border-bottom: 1px solid #e5e7eb;
        white-space: nowrap;
    }
    
    .modern-table td {
        padding: 1rem;
        border-bottom: 1px solid #f3f4f6;
        font-size: 0.875rem;
        color: #374151;
    }
    
    .table-row {
        transition: all 0.2s ease;
        cursor: pointer;
    }
    
    .table-row:hover {
        background: #f8fafc;
        transform: scale(1.01);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .student-cell {
        display: flex;
        align-items: center;
    }
    
    .student-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 600;
        font-size: 0.75rem;
        margin-right: 0.75rem;
    }
    
    .student-name {
        font-weight: 500;
        color: #1f2937;
    }
    
    .student-id {
        font-size: 0.75rem;
        color: #6b7280;
    }
    
    .course-badge {
        background: #ddd6fe;
        color: #5b21b6;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.375rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-pill.success {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-pill.success .status-dot {
        background: #22c55e;
    }
    
    .status-pill.warning {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-pill.warning .status-dot {
        background: #f59e0b;
    }
    
    .status-pill.error {
        background: #fee2e2;
        color: #991b1b;
    }
    
    .status-pill.error .status-dot {
        background: #ef4444;
    }
    
    /* Floating Action Button */
    .fab-container {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        z-index: 1000;
    }
    
    .fab-main {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .fab-main:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Loading animations */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 3rem;
        text-align: center;
    }
    
    .loading-spinner {
        position: relative;
        width: 60px;
        height: 60px;
        margin-bottom: 1.5rem;
    }
    
    .spinner-ring {
        position: absolute;
        width: 100%;
        height: 100%;
        border: 4px solid transparent;
        border-radius: 50%;
        animation: rotate 1.5s linear infinite;
    }
    
    .spinner-ring:nth-child(1) {
        border-top-color: #667eea;
        animation-delay: 0s;
    }
    
    .spinner-ring:nth-child(2) {
        border-right-color: #764ba2;
        animation-delay: 0.3s;
    }
    
    .spinner-ring:nth-child(3) {
        border-bottom-color: #f093fb;
        animation-delay: 0.6s;
    }
    
    .loading-text h3 {
        font-family: 'Poppins', sans-serif;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .loading-text p {
        color: #64748b;
        margin: 0;
    }
    
    /* Theme toggle */
    .theme-toggle {
        position: fixed;
        top: 1rem;
        right: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        border-radius: 50px;
        padding: 0.75rem 1rem;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.875rem;
        font-weight: 500;
        z-index: 1000;
    }
    
    .theme-toggle:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .modern-header {
            padding: 1.5rem;
        }
        
        .brand-title {
            font-size: 1.75rem;
        }
        
        .progress-flow {
            padding: 1.5rem;
        }
        
        .step-container {
            flex-direction: column;
            gap: 1rem;
        }
        
        .dashboard-grid {
            grid-template-columns: 1fr;
        }
        
        .table-controls {
            flex-direction: column;
            align-items: stretch;
        }
        
        .search-container {
            min-width: auto;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_modern_header(user_name: str, user_role: str):
    """Create modern header with gradient background"""
    st.markdown(f"""
    <div class="modern-header">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="header-brand">
                <div class="brand-icon">🏆</div>
                <div>
                    <h1 class="brand-title">SafeSteps</h1>
                    <p class="brand-subtitle">Modern Certificate Generation Platform</p>
                </div>
            </div>
            <div class="user-profile">
                <div class="profile-avatar">{user_name[0]}{user_name.split()[1][0] if len(user_name.split()) > 1 else ''}</div>
                <div>
                    <div style="font-weight: 600; font-size: 0.875rem;">{user_name}</div>
                    <div style="font-size: 0.75rem; opacity: 0.8;">{user_role}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_modern_progress(current_step: int):
    """Create interactive progress flow"""
    steps = [
        ("📤", "Upload", "Upload your student data", 1),
        ("✅", "Validate", "Check data accuracy", 2),
        ("📄", "Template", "Choose certificate design", 3),
        ("🏆", "Generate", "Create certificates", 4),
        ("🎉", "Complete", "Download results", 5)
    ]
    
    # Calculate progress percentage
    progress_percent = ((current_step - 1) / (len(steps) - 1)) * 100
    
    progress_html = f"""
    <div class="progress-flow">
        <div class="flow-background">
            <div class="flow-line" style="width: {progress_percent}%;"></div>
        </div>
        <div class="step-container">
    """
    
    for icon, title, desc, step_num in steps:
        if step_num < current_step:
            step_class = "completed"
            step_icon = "✅"
        elif step_num == current_step:
            step_class = "active"
            step_icon = str(step_num)
            pulse_html = '<div class="step-pulse"></div>'
        else:
            step_class = "pending"
            step_icon = str(step_num)
            pulse_html = ""
        
        progress_html += f"""
        <div class="step {step_class}">
            <div class="step-circle">
                <div class="step-inner">{step_icon}</div>
                {pulse_html if step_class == "active" else ""}
            </div>
            <div>
                <h3 class="step-title">{title}</h3>
                <p class="step-description">{desc}</p>
            </div>
        </div>
        """
    
    progress_html += "</div></div>"
    st.markdown(progress_html, unsafe_allow_html=True)

def create_modern_dashboard_cards(metrics: Dict):
    """Create interactive dashboard cards"""
    st.markdown("""
    <div class="dashboard-grid">
    """, unsafe_allow_html=True)
    
    # Total Records Card
    st.markdown(f"""
    <div class="dashboard-card primary">
        <div class="card-header">
            <div class="card-icon">📊</div>
            <div class="card-title">
                <h3>Data Overview</h3>
                <p>{metrics.get('total', 0)} records processed</p>
            </div>
        </div>
        <div class="card-content">
            <div class="metric-display">
                <div class="metric-number">{metrics.get('total', 0)}</div>
                <div class="metric-label">Total Records</div>
                <div class="metric-trend positive">+{metrics.get('total_delta', 0)}%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Valid Records Card with Progress Ring
    valid_percent = int((metrics.get('valid', 0) / max(metrics.get('total', 1), 1)) * 100)
    st.markdown(f"""
    <div class="dashboard-card success">
        <div class="card-header">
            <div class="card-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">✅</div>
            <div class="card-title">
                <h3>Valid Records</h3>
                <p>Ready for processing</p>
            </div>
        </div>
        <div class="card-content">
            <div class="progress-ring">
                <div class="progress-value">{valid_percent}%</div>
                <svg class="progress-svg" viewBox="0 0 100 100">
                    <defs>
                        <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" style="stop-color:#4facfe"/>
                            <stop offset="100%" style="stop-color:#00f2fe"/>
                        </linearGradient>
                    </defs>
                    <circle class="progress-circle active" r="45" cx="50" cy="50" 
                            style="stroke-dasharray: 283; stroke-dashoffset: {283 - (283 * valid_percent / 100)};"></circle>
                </svg>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Warnings Card
    st.markdown(f"""
    <div class="dashboard-card warning">
        <div class="card-header">
            <div class="card-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">⚠️</div>
            <div class="card-title">
                <h3>Attention Needed</h3>
                <p>{metrics.get('warnings', 0)} warnings to review</p>
            </div>
        </div>
        <div class="card-content">
            <div class="metric-display">
                <div class="metric-number">{metrics.get('warnings', 0)}</div>
                <div class="metric-label">Warnings</div>
                <div class="metric-trend negative">Review Required</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def create_modern_data_table(df: pd.DataFrame, title: str = "Data Management"):
    """Create interactive modern data table"""
    st.markdown(f"""
    <div class="interactive-table">
        <div class="table-controls">
            <div class="search-container">
                <div class="search-icon">🔍</div>
                <input type="text" placeholder="Search students..." class="search-input" id="searchInput">
            </div>
            <div class="filter-chips">
                <div class="chip active" onclick="filterTable('All')">All ({len(df)})</div>
                <div class="chip" onclick="filterTable('Valid')">Valid ({len(df[df['status'] == 'Valid'])})</div>
                <div class="chip" onclick="filterTable('Warning')">Warnings ({len(df[df['status'] == 'Warning'])})</div>
                <div class="chip" onclick="filterTable('Error')">Errors ({len(df[df['status'] == 'Error'])})</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Convert dataframe to HTML table with modern styling
    table_html = '<div class="table-wrapper"><table class="modern-table"><thead><tr>'
    table_html += '<th><input type="checkbox" class="select-all"></th>'
    table_html += '<th class="sortable">Student Name <span class="sort-indicator">↕</span></th>'
    table_html += '<th class="sortable">Email <span class="sort-indicator">↕</span></th>'
    table_html += '<th>Course</th>'
    table_html += '<th>Status</th>'
    table_html += '<th>Actions</th>'
    table_html += '</tr></thead><tbody>'
    
    for idx, row in df.iterrows():
        # Generate initials for avatar
        name_parts = row['name'].split()
        initials = name_parts[0][0] + (name_parts[1][0] if len(name_parts) > 1 else '')
        
        # Determine status styling
        status_class = row['status'].lower()
        
        table_html += f'''
        <tr class="table-row hover-elevated">
            <td><input type="checkbox"></td>
            <td>
                <div class="student-cell">
                    <div class="student-avatar">{initials}</div>
                    <div class="student-info">
                        <div class="student-name">{row['name']}</div>
                        <div class="student-id">#STU{idx+1:03d}</div>
                    </div>
                </div>
            </td>
            <td>{row['email']}</td>
            <td>
                <span class="course-badge">{row['course']}</span>
            </td>
            <td>
                <div class="status-pill {status_class}">
                    <div class="status-dot"></div>
                    <span>{row['status']}</span>
                </div>
            </td>
            <td>
                <div class="action-menu">
                    <button class="action-btn">⋮</button>
                </div>
            </td>
        </tr>
        '''
    
    table_html += '</tbody></table></div></div>'
    st.markdown(table_html, unsafe_allow_html=True)

def create_loading_animation(text: str = "Processing your data..."):
    """Create modern loading animation"""
    st.markdown(f"""
    <div class="loading-container">
        <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
            <div class="spinner-ring"></div>
        </div>
        <div class="loading-text">
            <h3>{text}</h3>
            <p>This may take a few moments</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def create_floating_action_button():
    """Create floating action button"""
    st.markdown("""
    <div class="fab-container">
        <button class="fab-main" onclick="showFabMenu()">
            <span class="fab-icon">+</span>
        </button>
    </div>
    """, unsafe_allow_html=True)

def create_theme_toggle():
    """Create theme toggle button"""
    current_theme = st.session_state.get('theme', 'light')
    theme_icon = "🌙" if current_theme == 'light' else "☀️"
    theme_label = "Dark Mode" if current_theme == 'light' else "Light Mode"
    
    st.markdown(f"""
    <button class="theme-toggle" onclick="toggleTheme()">
        {theme_icon} {theme_label}
    </button>
    """, unsafe_allow_html=True)

def create_modern_action_bar(actions: List[Dict]):
    """Create modern action buttons with animations"""
    if not actions:
        return
    
    cols = st.columns(len(actions))
    
    for i, action in enumerate(actions):
        with cols[i]:
            button_type = "primary" if action.get('primary') else "secondary"
            
            # Add custom styling for modern buttons
            if action.get('primary'):
                st.markdown("""
                <style>
                .stButton > button[kind="primary"] {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    border-radius: 8px;
                    padding: 0.75rem 1.5rem;
                    font-weight: 600;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                }
                .stButton > button[kind="primary"]:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
                }
                </style>
                """, unsafe_allow_html=True)
            
            if st.button(
                action['label'],
                key=action.get('key', f'modern_action_{i}'),
                type=button_type,
                use_container_width=True,
                help=action.get('help')
            ):
                if action.get('callback'):
                    action['callback']()

def demo_modern_ui():
    """Demo of the modern interactive UI"""
    # Apply theme
    apply_modern_theme()
    
    # Theme toggle
    create_theme_toggle()
    
    # Header
    create_modern_header("Dr. Sarah Johnson", "Administrator")
    
    # Progress indicator
    create_modern_progress(2)  # Currently on step 2 (Validate)
    
    # Sample data
    sample_data = pd.DataFrame([
        {"name": "John Smith", "email": "john.smith@school.edu", "course": "Digital Safety", "status": "Valid"},
        {"name": "Jane Doe", "email": "jane.doe@school.edu", "course": "Internet Ethics", "status": "Valid"},
        {"name": "Bob Wilson", "email": "bob.wilson@school.edu", "course": "Digital Safety", "status": "Warning"},
        {"name": "Alice Brown", "email": "alice.brown@", "course": "Cybersecurity", "status": "Error"},
        {"name": "Charlie Davis", "email": "charlie.davis@school.edu", "course": "Digital Safety", "status": "Valid"},
        {"name": "Emma Rodriguez", "email": "emma.rodriguez@school.edu", "course": "Data Privacy", "status": "Valid"},
        {"name": "Michael Chen", "email": "michael.chen@school.edu", "course": "Digital Citizenship", "status": "Valid"},
        {"name": "Sarah Thompson", "email": "sarah.thompson@school.edu", "course": "Internet Ethics", "status": "Warning"},
    ])
    
    # Metrics with enhanced data
    metrics = {
        'total': 125,
        'valid': 118,
        'warnings': 5,
        'errors': 2,
        'total_delta': 15,
        'valid_delta': 12
    }
    
    # Dashboard cards
    create_modern_dashboard_cards(metrics)
    
    # Interactive data table
    create_modern_data_table(sample_data, "Student Data Management")
    
    # Action buttons
    actions = [
        {
            'label': '⬅️ Back to Upload',
            'key': 'modern_back_upload',
            'help': 'Return to upload step'
        },
        {
            'label': '🔧 Auto-Fix Issues',
            'key': 'modern_fix_errors',
            'help': 'Automatically resolve common issues'
        },
        {
            'label': '🎨 Continue to Templates ➡️',
            'key': 'modern_continue_template',
            'primary': True,
            'help': 'Proceed to certificate template selection'
        }
    ]
    
    create_modern_action_bar(actions)
    
    # Floating action button
    create_floating_action_button()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem; color: #64748b;">
        <p style="margin: 0; font-size: 0.875rem;">
            🏆 SafeSteps Certificate Generator v2.1 | Modern Interactive Theme
        </p>
        <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem;">
            Powered by Streamlit with love ❤️
        </p>
    </div>
    """, unsafe_allow_html=True)

# JavaScript for interactive features
def add_interactive_javascript():
    """Add JavaScript for enhanced interactivity"""
    st.markdown("""
    <script>
    function filterTable(status) {
        // Update chip active state
        document.querySelectorAll('.chip').forEach(chip => {
            chip.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Filter table rows (simplified for demo)
        console.log('Filtering by:', status);
    }
    
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', newTheme);
        
        // Update button text
        const button = document.querySelector('.theme-toggle');
        if (newTheme === 'dark') {
            button.innerHTML = '☀️ Light Mode';
        } else {
            button.innerHTML = '🌙 Dark Mode';
        }
    }
    
    function showFabMenu() {
        console.log('FAB clicked - would show menu');
    }
    
    // Add search functionality
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                console.log('Searching for:', e.target.value);
                // Search logic would go here
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    st.set_page_config(
        page_title="SafeSteps - Modern UI Demo",
        page_icon="🏆",
        layout="wide"
    )
    
    demo_modern_ui()
    add_interactive_javascript()