"""
Workflow Persistence for Save/Resume Functionality
Allows users to save and resume their certificate generation progress
"""
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import pickle

class WorkflowPersistence:
    """Manages saving and loading workflow state"""
    
    def __init__(self):
        self.storage_dir = Path.home() / '.safesteps' / 'workflows'
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_progress(self, session_state):
        """Save current workflow progress"""
        try:
            # Extract workflow-related state
            workflow_data = {
                'timestamp': datetime.now().isoformat(),
                'user': session_state.get('username', 'unknown'),
                'step': session_state.get('wizard_step', 1),
                'data': {}
            }
            
            # Save relevant session state items
            workflow_keys = [
                'wizard_step', 'wizard_uploaded_file', 'wizard_validated_data',
                'wizard_selected_template', 'wizard_generated_files',
                'visual_step', 'visual_uploaded_file', 'visual_selected_template'
            ]
            
            for key in workflow_keys:
                if key in session_state:
                    # Handle file objects specially
                    if 'file' in key and session_state[key] is not None:
                        workflow_data['data'][key] = {
                            'name': session_state[key].name,
                            'size': session_state[key].size
                        }
                    else:
                        workflow_data['data'][key] = session_state[key]
            
            # Generate filename
            username = session_state.get('username', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"workflow_{username}_{timestamp}.json"
            filepath = self.storage_dir / filename
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            
            # Also save as "latest" for easy access
            latest_path = self.storage_dir / f"workflow_{username}_latest.json"
            with open(latest_path, 'w') as f:
                json.dump(workflow_data, f, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to save progress: {str(e)}")
            return False
    
    def load_progress(self, session_state):
        """Load saved workflow progress"""
        try:
            username = session_state.get('username', 'unknown')
            latest_path = self.storage_dir / f"workflow_{username}_latest.json"
            
            if not latest_path.exists():
                return False
            
            with open(latest_path, 'r') as f:
                workflow_data = json.load(f)
            
            # Restore session state
            for key, value in workflow_data['data'].items():
                # Skip file objects - user will need to re-upload
                if 'file' not in key:
                    session_state[key] = value
            
            st.success(f"Progress restored from {workflow_data['timestamp']}")
            return True
            
        except Exception as e:
            st.error(f"Failed to load progress: {str(e)}")
            return False
    
    def has_saved_progress(self):
        """Check if user has saved progress"""
        try:
            username = st.session_state.get('username', 'unknown')
            latest_path = self.storage_dir / f"workflow_{username}_latest.json"
            return latest_path.exists()
        except:
            return False
    
    def list_saved_workflows(self, username=None):
        """List all saved workflows for a user"""
        try:
            if username is None:
                username = st.session_state.get('username', 'unknown')
            
            workflows = []
            for filepath in self.storage_dir.glob(f"workflow_{username}_*.json"):
                if 'latest' not in filepath.name:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        workflows.append({
                            'filename': filepath.name,
                            'timestamp': data['timestamp'],
                            'step': data.get('step', 1),
                            'path': filepath
                        })
            
            # Sort by timestamp, newest first
            workflows.sort(key=lambda x: x['timestamp'], reverse=True)
            return workflows
            
        except Exception as e:
            st.error(f"Failed to list workflows: {str(e)}")
            return []
    
    def delete_workflow(self, filepath):
        """Delete a saved workflow"""
        try:
            if isinstance(filepath, str):
                filepath = Path(filepath)
            
            if filepath.exists():
                filepath.unlink()
                return True
            return False
            
        except Exception as e:
            st.error(f"Failed to delete workflow: {str(e)}")
            return False
    
    def clear_progress(self):
        """Clear the current user's latest saved progress"""
        try:
            username = st.session_state.get('username', 'unknown')
            latest_path = self.storage_dir / f"workflow_{username}_latest.json"
            
            if latest_path.exists():
                latest_path.unlink()
            
            # Clear workflow-related session state
            workflow_keys = [
                'wizard_step', 'wizard_uploaded_file', 'wizard_validated_data',
                'wizard_selected_template', 'wizard_generated_files',
                'visual_step', 'visual_uploaded_file', 'visual_selected_template'
            ]
            
            for key in workflow_keys:
                if key in st.session_state:
                    del st.session_state[key]
            
            return True
            
        except Exception as e:
            st.error(f"Failed to clear progress: {str(e)}")
            return False
    
    def export_workflow(self, workflow_path):
        """Export a workflow for sharing"""
        try:
            with open(workflow_path, 'r') as f:
                data = json.load(f)
            
            # Remove sensitive information
            data.pop('user', None)
            
            return json.dumps(data, indent=2)
            
        except Exception as e:
            st.error(f"Failed to export workflow: {str(e)}")
            return None
    
    def import_workflow(self, workflow_json):
        """Import a shared workflow"""
        try:
            data = json.loads(workflow_json)
            
            # Add current user info
            data['user'] = st.session_state.get('username', 'unknown')
            data['timestamp'] = datetime.now().isoformat()
            
            # Save as new workflow
            username = st.session_state.get('username', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"workflow_{username}_imported_{timestamp}.json"
            filepath = self.storage_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to import workflow: {str(e)}")
            return False

# Global instance
workflow_persistence = WorkflowPersistence()

def save_workflow_checkpoint(session_state=None):
    """Save workflow checkpoint using global instance"""
    if session_state is None:
        session_state = st.session_state
    return workflow_persistence.save_progress(session_state)

def load_workflow_checkpoint(filename):
    """Load workflow checkpoint using global instance"""
    return workflow_persistence.load_progress(filename)