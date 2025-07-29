import streamlit as st
from utils.ui_components import create_progress_steps

st.set_page_config(page_title="Progress Bar Test", layout="wide")

st.title("Progress Bar Rendering Test")

# Test the progress bar at different steps
for step in range(1, 6):
    st.subheader(f"Step {step}")
    steps = [
        ("Upload", "📤", 1),
        ("Validate", "✅", 2),
        ("Template", "📄", 3),
        ("Generate", "🏆", 4),
        ("Complete", "🎉", 5)
    ]
    create_progress_steps(steps, step)
    st.markdown("---")

st.info("If you see raw HTML above instead of styled progress bars, there's a rendering issue.")
