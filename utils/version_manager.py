"""
Version Manager for UI Version Selection
Handles switching between different UI versions
"""
import streamlit as st
from datetime import datetime
import json
from pathlib import Path

class VersionManager:
    """Manages UI version selection and persistence"""
    
    def __init__(self):
        self.versions = {
            "Version 1": {
                "name": "Streamlined Efficiency",
                "description": "Power user interface with keyboard shortcuts, single-page dashboard, and bulk operations",
                "icon": "⚡",
                "target_users": "Frequent users, administrators",
                "key_features": [
                    "Single-page dashboard",
                    "Keyboard shortcuts (Ctrl+1-9)",
                    "Bulk operations",
                    "Real-time metrics",
                    "Express workflow"
                ]
            },
            "Version 2": {
                "name": "User-Friendly Guidance",
                "description": "Beginner-friendly interface with tutorials, contextual help, and save/resume functionality",
                "icon": "🎓",
                "target_users": "New users, occasional users",
                "key_features": [
                    "Interactive tutorials",
                    "Step-by-step guidance",
                    "Save/resume workflow",
                    "Contextual help",
                    "Error prevention"
                ]
            },
            "Version 3": {
                "name": "Modern Dashboard",
                "description": "Visually appealing interface with data visualizations, mobile-responsive design, and themes",
                "icon": "🎨",
                "target_users": "Visual learners, mobile users",
                "key_features": [
                    "Card-based interface",
                    "Data visualizations",
                    "Mobile-responsive",
                    "Dark/light themes",
                    "Drag-and-drop feel"
                ]
            }
        }
        
        # Initialize version preference
        if 'ui_version' not in st.session_state:
            st.session_state.ui_version = self.load_preference()
    
    def get_version_info(self, version_key):
        """Get information about a specific version"""
        return self.versions.get(version_key, None)
    
    def get_current_version(self):
        """Get the currently selected version"""
        return st.session_state.get('ui_version', 'Current')
    
    def set_version(self, version):
        """Set the current UI version"""
        st.session_state.ui_version = version
        self.save_preference(version)
    
    def save_preference(self, version):
        """Save version preference to local storage"""
        try:
            prefs_file = Path.home() / '.safesteps' / 'ui_preferences.json'
            prefs_file.parent.mkdir(exist_ok=True)
            
            prefs = {
                'ui_version': version,
                'last_updated': datetime.now().isoformat(),
                'user': st.session_state.get('username', 'unknown')
            }
            
            with open(prefs_file, 'w') as f:
                json.dump(prefs, f)
        except Exception as e:
            # Fail silently - preferences are optional
            pass
    
    def load_preference(self):
        """Load saved version preference"""
        try:
            prefs_file = Path.home() / '.safesteps' / 'ui_preferences.json'
            if prefs_file.exists():
                with open(prefs_file, 'r') as f:
                    prefs = json.load(f)
                    return prefs.get('ui_version', 'Current')
        except Exception:
            pass
        return 'Current'
    
    def get_version_metrics(self):
        """Get usage metrics for versions (mock data for demo)"""
        return {
            "Version 1": {"users": 234, "satisfaction": 4.2},
            "Version 2": {"users": 567, "satisfaction": 4.6},
            "Version 3": {"users": 189, "satisfaction": 4.4}
        }
    
    def recommend_version(self, user_profile):
        """Recommend a version based on user profile"""
        # Simple recommendation logic
        if user_profile.get('experience_level') == 'beginner':
            return "Version 2"
        elif user_profile.get('prefers_visual'):
            return "Version 3"
        elif user_profile.get('power_user'):
            return "Version 1"
        return "Current"
    
    def show_version_selector(self):
        """Display version selector widget"""
        with st.expander("🎨 UI Version Settings", expanded=False):
            current = self.get_current_version()
            
            # Version comparison table
            st.markdown("### Compare Versions")
            
            comparison_data = []
            for key, info in self.versions.items():
                comparison_data.append({
                    "Version": f"{info['icon']} {info['name']}",
                    "Best For": info['target_users'],
                    "Key Feature": info['key_features'][0]
                })
            
            st.table(comparison_data)
            
            # Metrics
            metrics = self.get_version_metrics()
            cols = st.columns(3)
            for idx, (version, data) in enumerate(metrics.items()):
                with cols[idx]:
                    st.metric(
                        version,
                        f"{data['users']} users",
                        f"⭐ {data['satisfaction']}/5"
                    )
            
            # Reset option
            if st.button("Reset to Default UI"):
                self.set_version("Current")
                st.rerun()
    
    def track_version_usage(self, version, action):
        """Track how users interact with different versions"""
        # In a real implementation, this would log to analytics
        usage_data = {
            "version": version,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "user": st.session_state.get('username', 'unknown')
        }
        # For now, just store in session state
        if 'version_usage' not in st.session_state:
            st.session_state.version_usage = []
        st.session_state.version_usage.append(usage_data)