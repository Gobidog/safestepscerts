"""
Chart Components for Data Visualization
Provides visual charts and graphs for the modern dashboard
"""
import streamlit as st
import pandas as pd
import random

def create_mini_chart(title, values, labels):
    """Create a simple mini chart using Streamlit native components"""
    
    # Create a simple bar representation using columns
    st.markdown(f"**{title}**")
    
    # Calculate percentages
    total = sum(values)
    percentages = [v/total * 100 for v in values]
    
    # Create visual bars
    for i, (label, value, pct) in enumerate(zip(labels, values, percentages)):
        col1, col2, col3 = st.columns([2, 3, 1])
        
        with col1:
            st.text(label)
        
        with col2:
            # Create a progress bar to simulate a chart bar
            st.progress(pct/100)
        
        with col3:
            st.text(f"{value}")

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a visually appealing metric card"""
    with st.container(border=True):
        st.metric(title, value, delta, delta_color=delta_color)

def create_activity_chart():
    """Create an activity chart showing trends"""
    st.markdown("### Activity Trend")
    
    # Generate mock data
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    values = [random.randint(50, 200) for _ in range(30)]
    
    # Create a simple line chart using native Streamlit
    chart_data = pd.DataFrame({
        'Date': dates,
        'Certificates': values
    })
    
    st.line_chart(chart_data.set_index('Date'))

def create_distribution_chart(data_dict):
    """Create a distribution chart"""
    st.markdown("### Distribution")
    
    # Convert dict to dataframe
    df = pd.DataFrame(list(data_dict.items()), columns=['Category', 'Count'])
    
    # Create a bar chart
    st.bar_chart(df.set_index('Category'))

def create_sparkline(data, height=50):
    """Create a small sparkline chart"""
    # Use Streamlit's native line chart with custom height
    st.line_chart(data, height=height)

def create_gauge_chart(value, max_value=100, title="Progress"):
    """Create a gauge-like visualization using progress bar"""
    st.markdown(f"**{title}**")
    progress = value / max_value
    st.progress(progress)
    st.markdown(f"{value}/{max_value} ({progress*100:.0f}%)")

def create_comparison_chart(data1, data2, labels):
    """Create a comparison chart between two datasets"""
    st.markdown("### Comparison")
    
    # Create side-by-side metrics
    for i, label in enumerate(labels):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.text(label)
        with col2:
            st.metric("Previous", data1[i], delta_color="off")
        with col3:
            delta = data2[i] - data1[i]
            st.metric("Current", data2[i], delta)

def create_heatmap_simple(title, data):
    """Create a simple heatmap visualization"""
    st.markdown(f"### {title}")
    
    # Create a grid of colored boxes using columns
    rows = len(data)
    cols = len(data[0]) if rows > 0 else 0
    
    for row in data:
        columns = st.columns(cols)
        for i, value in enumerate(row):
            with columns[i]:
                # Color intensity based on value
                if value > 0.7:
                    st.success(f"{value:.1f}")
                elif value > 0.4:
                    st.warning(f"{value:.1f}")
                else:
                    st.error(f"{value:.1f}")

def create_timeline_chart(events):
    """Create a timeline visualization"""
    st.markdown("### Timeline")
    
    for event in events:
        with st.container(border=True):
            col1, col2 = st.columns([1, 4])
            with col1:
                st.caption(event['date'])
            with col2:
                st.markdown(f"**{event['title']}**")
                if 'description' in event:
                    st.caption(event['description'])

def create_stats_grid(stats):
    """Create a grid of statistics"""
    cols = st.columns(len(stats))
    
    for i, stat in enumerate(stats):
        with cols[i]:
            with st.container(border=True):
                st.metric(
                    stat['label'],
                    stat['value'],
                    stat.get('delta'),
                    delta_color=stat.get('delta_color', 'normal')
                )

def create_donut_chart_simple(title, values, labels):
    """Create a simple donut chart representation"""
    st.markdown(f"### {title}")
    
    total = sum(values)
    
    # Create a visual representation
    for label, value in zip(labels, values):
        percentage = (value / total) * 100
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.progress(percentage / 100)
        with col2:
            st.text(label)
        with col3:
            st.text(f"{percentage:.0f}%")

def create_radar_chart_simple(categories, values, title="Skills"):
    """Create a simple radar chart representation"""
    st.markdown(f"### {title}")
    
    # Normalize values to 0-1 range
    max_val = max(values) if values else 1
    normalized = [v/max_val for v in values]
    
    # Display as horizontal bars
    for cat, val, norm in zip(categories, values, normalized):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.text(cat)
        with col2:
            st.progress(norm)
            st.caption(f"{val}/{max_val}")

def create_funnel_chart(stages, values, title="Conversion Funnel"):
    """Create a funnel chart visualization"""
    st.markdown(f"### {title}")
    
    if not values:
        return
    
    max_value = values[0]  # First value is typically the largest
    
    for i, (stage, value) in enumerate(zip(stages, values)):
        # Calculate width percentage
        width_pct = (value / max_value) * 100
        
        # Create visual funnel effect with minimum padding
        min_padding = 5  # 5% minimum padding to avoid zero-width columns
        padding = max(min_padding, (100 - width_pct) / 2)
        adjusted_width = min(width_pct, 100 - (2 * min_padding))
        
        col1, col2, col3 = st.columns([padding/100, adjusted_width/100, padding/100])
        
        with col2:
            # Conversion rate from previous stage
            if i > 0:
                conversion = (value / values[i-1]) * 100
                st.progress(value / max_value)
                st.markdown(f"**{stage}**: {value} ({conversion:.0f}% conversion)")
            else:
                st.progress(1.0)
                st.markdown(f"**{stage}**: {value}")

def create_kpi_dashboard(kpis):
    """Create a KPI dashboard with multiple metrics"""
    st.markdown("### Key Performance Indicators")
    
    # Create a grid layout
    num_kpis = len(kpis)
    cols_per_row = min(4, num_kpis)
    
    for i in range(0, num_kpis, cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j in range(cols_per_row):
            if i + j < num_kpis:
                kpi = kpis[i + j]
                with cols[j]:
                    create_metric_card(
                        kpi['title'],
                        kpi['value'],
                        kpi.get('delta'),
                        kpi.get('delta_color', 'normal')
                    )