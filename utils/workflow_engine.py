"""
Flexible Workflow Engine for SafeSteps
Supports multiple user paths: Quick Generate, Guided Mode, Advanced Mode
Implements save/resume functionality and adaptive interfaces
"""
import streamlit as st
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import threading
from collections import defaultdict

class WorkflowMode(Enum):
    """Supported workflow modes"""
    QUICK_GENERATE = "quick_generate"
    GUIDED_MODE = "guided_mode"
    ADVANCED_MODE = "advanced_mode"

class StepStatus(Enum):
    """Step completion status"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    ERROR = "error"

@dataclass
class WorkflowStep:
    """Individual workflow step definition"""
    id: str
    name: str
    description: str
    required: bool = True
    depends_on: List[str] = field(default_factory=list)
    validation_func: Optional[Callable] = None
    render_func: Optional[Callable] = None
    quick_mode_enabled: bool = True
    guided_mode_enabled: bool = True
    advanced_mode_enabled: bool = True
    keyboard_shortcut: Optional[str] = None
    estimated_time: int = 60  # seconds
    help_text: Optional[str] = None

@dataclass
class WorkflowState:
    """Current workflow state"""
    workflow_id: str
    user_id: str
    mode: WorkflowMode
    current_step: Optional[str] = None
    step_statuses: Dict[str, StepStatus] = field(default_factory=dict)
    step_data: Dict[str, Any] = field(default_factory=dict)
    form_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    auto_save_enabled: bool = True
    shortcuts_enabled: bool = True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        # Convert enums to strings
        result['mode'] = self.mode.value
        result['step_statuses'] = {k: v.value for k, v in self.step_statuses.items()}
        # Convert datetime objects
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'WorkflowState':
        """Create from dictionary"""
        # Convert string enums back
        data['mode'] = WorkflowMode(data['mode'])
        data['step_statuses'] = {k: StepStatus(v) for k, v in data.get('step_statuses', {}).items()}
        # Convert datetime strings
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('completed_at'):
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)

@dataclass
class UserBehaviorData:
    """Track user behavior for adaptive interfaces"""
    user_id: str
    feature_usage: Dict[str, int] = field(default_factory=dict)
    common_shortcuts: List[str] = field(default_factory=list)
    preferred_mode: Optional[WorkflowMode] = None
    average_step_time: Dict[str, float] = field(default_factory=dict)
    error_patterns: List[str] = field(default_factory=list)
    successful_completions: int = 0
    last_updated: datetime = field(default_factory=datetime.now)

class FlexibleWorkflowEngine:
    """
    Flexible workflow engine supporting multiple user paths and adaptive interfaces
    """
    
    def __init__(self):
        self.storage_dir = Path.home() / '.safesteps' / 'workflows_v2' 
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.behavior_storage_dir = Path.home() / '.safesteps' / 'behavior'
        self.behavior_storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.steps: Dict[str, WorkflowStep] = {}
        self.workflows: Dict[str, WorkflowState] = {}
        self.user_behaviors: Dict[str, UserBehaviorData] = {}
        
        # Auto-save configuration
        self.auto_save_interval = 30  # seconds
        self.last_auto_save = {}
        
        # Performance tracking
        self.step_start_times = {}
        
        # Initialize default certificate generation workflow
        self._init_certificate_workflow()
        
        # Load existing user behavior data
        self._load_user_behaviors()
    
    def _init_certificate_workflow(self):
        """Initialize the default certificate generation workflow"""
        
        # Step 1: Upload
        self.add_step(WorkflowStep(
            id="upload",
            name="Upload Data",
            description="Upload student data file (CSV/Excel)",
            required=True,
            keyboard_shortcut="Alt+1",
            estimated_time=30,
            help_text="Upload a CSV or Excel file containing student information. Required columns: name, email"
        ))
        
        # Step 2: Validation
        self.add_step(WorkflowStep(
            id="validate",
            name="Validate Data", 
            description="Validate uploaded data format and content",
            required=True,
            depends_on=["upload"],
            keyboard_shortcut="Alt+2",
            estimated_time=15,
            help_text="Automatic validation of your data. We'll check for required columns and data integrity"
        ))
        
        # Step 3: Course Selection
        self.add_step(WorkflowStep(
            id="course_select",
            name="Select Course",
            description="Choose course template for certificates",
            required=True,
            depends_on=["validate"],
            keyboard_shortcut="Alt+3", 
            estimated_time=45,
            help_text="Select the appropriate course template for your certificates"
        ))
        
        # Step 4: Template Customization (Advanced only)
        self.add_step(WorkflowStep(
            id="customize",
            name="Customize Template",
            description="Customize certificate template and options",
            required=False,
            depends_on=["course_select"],
            quick_mode_enabled=False,
            guided_mode_enabled=True,
            advanced_mode_enabled=True,
            keyboard_shortcut="Alt+4",
            estimated_time=120,
            help_text="Customize your certificate template with logos, colors, and messaging"
        ))
        
        # Step 5: Preview (Guided and Advanced)
        self.add_step(WorkflowStep(
            id="preview",
            name="Preview Certificates",
            description="Preview generated certificates before final generation",
            required=False,
            depends_on=["course_select"],
            quick_mode_enabled=False,
            guided_mode_enabled=True,
            advanced_mode_enabled=True,
            keyboard_shortcut="Alt+5",
            estimated_time=30,
            help_text="Preview how your certificates will look before generating the full batch"
        ))
        
        # Step 6: Generation
        self.add_step(WorkflowStep(
            id="generate",
            name="Generate Certificates",
            description="Generate and download certificate files",
            required=True,
            depends_on=["course_select"],
            keyboard_shortcut="Ctrl+G",
            estimated_time=60,
            help_text="Generate all certificates and create downloadable ZIP file"
        ))
    
    def add_step(self, step: WorkflowStep):
        """Add a workflow step"""
        self.steps[step.id] = step
    
    def create_workflow(self, user_id: str, mode: WorkflowMode) -> str:
        """Create a new workflow instance"""
        workflow_id = str(uuid.uuid4())
        
        workflow_state = WorkflowState(
            workflow_id=workflow_id,
            user_id=user_id,
            mode=mode
        )
        
        # Initialize step statuses based on mode
        for step_id, step in self.steps.items():
            if (mode == WorkflowMode.QUICK_GENERATE and step.quick_mode_enabled) or \
               (mode == WorkflowMode.GUIDED_MODE and step.guided_mode_enabled) or \
               (mode == WorkflowMode.ADVANCED_MODE and step.advanced_mode_enabled):
                workflow_state.step_statuses[step_id] = StepStatus.PENDING
        
        # Set first available step as current
        available_steps = self._get_available_steps(workflow_state)
        if available_steps:
            workflow_state.current_step = available_steps[0]
            workflow_state.step_statuses[available_steps[0]] = StepStatus.ACTIVE
        
        self.workflows[workflow_id] = workflow_state
        self._auto_save_workflow(workflow_id)
        
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """Get workflow by ID"""
        if workflow_id in self.workflows:
            return self.workflows[workflow_id]
        
        # Try to load from storage
        return self._load_workflow(workflow_id)
    
    def save_workflow(self, workflow_id: str) -> bool:
        """Manually save workflow state"""
        if workflow_id not in self.workflows:
            return False
        
        try:
            workflow = self.workflows[workflow_id]
            workflow.updated_at = datetime.now()
            
            filepath = self.storage_dir / f"workflow_{workflow_id}.json"
            with open(filepath, 'w') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            # Also save as latest for user
            latest_path = self.storage_dir / f"latest_{workflow.user_id}.json"
            with open(latest_path, 'w') as f:
                json.dump(workflow.to_dict(), f, indent=2)
            
            return True
            
        except Exception as e:
            st.error(f"Failed to save workflow: {str(e)}")
            return False
    
    def _load_workflow(self, workflow_id: str) -> Optional[WorkflowState]:
        """Load workflow from storage"""
        try:
            filepath = self.storage_dir / f"workflow_{workflow_id}.json"
            if not filepath.exists():
                return None
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            workflow = WorkflowState.from_dict(data)
            self.workflows[workflow_id] = workflow
            return workflow
            
        except Exception as e:
            st.error(f"Failed to load workflow: {str(e)}")
            return None
    
    def resume_latest_workflow(self, user_id: str) -> Optional[str]:
        """Resume user's latest workflow"""
        try:
            latest_path = self.storage_dir / f"latest_{user_id}.json"
            if not latest_path.exists():
                return None
            
            with open(latest_path, 'r') as f:
                data = json.load(f)
            
            workflow = WorkflowState.from_dict(data)
            self.workflows[workflow.workflow_id] = workflow
            return workflow.workflow_id
            
        except Exception as e:
            st.error(f"Failed to resume workflow: {str(e)}")
            return None
    
    def list_user_workflows(self, user_id: str) -> List[Dict]:
        """List all workflows for a user"""
        workflows = []
        
        try:
            for filepath in self.storage_dir.glob(f"workflow_*.json"):
                if 'latest_' in filepath.name:
                    continue
                
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                if data.get('user_id') == user_id:
                    # Calculate progress
                    total_steps = len([s for s, status in data.get('step_statuses', {}).items() if status != 'skipped'])
                    completed_steps = len([s for s, status in data.get('step_statuses', {}).items() if status == 'completed'])
                    progress = (completed_steps / total_steps * 100) if total_steps > 0 else 0
                    
                    workflows.append({
                        'workflow_id': data['workflow_id'],
                        'mode': data['mode'],
                        'created_at': data['created_at'],
                        'updated_at': data['updated_at'],
                        'progress': progress,
                        'current_step': data.get('current_step'),
                        'completed': data.get('completed_at') is not None
                    })
            
            # Sort by updated_at, newest first
            workflows.sort(key=lambda x: x['updated_at'], reverse=True)
            return workflows
            
        except Exception as e:
            st.error(f"Failed to list workflows: {str(e)}")
            return []
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            # Remove from memory
            if workflow_id in self.workflows:
                del self.workflows[workflow_id]
            
            # Remove from storage
            filepath = self.storage_dir / f"workflow_{workflow_id}.json"
            if filepath.exists():
                filepath.unlink()
            
            return True
            
        except Exception as e:
            st.error(f"Failed to delete workflow: {str(e)}")
            return False
    
    def advance_step(self, workflow_id: str, step_id: str, step_data: Dict = None) -> bool:
        """Advance to next step after completing current step"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False
        
        # Update step data
        if step_data:
            workflow.step_data[step_id] = step_data
            workflow.form_data.update(step_data)
        
        # Mark current step as completed
        workflow.step_statuses[step_id] = StepStatus.COMPLETED
        
        # Track step completion time for behavior analysis
        if step_id in self.step_start_times:
            completion_time = time.time() - self.step_start_times[step_id]
            self._update_user_behavior(workflow.user_id, step_id, completion_time)
        
        # Find next available step
        next_steps = self._get_available_steps(workflow)
        if next_steps:
            workflow.current_step = next_steps[0]
            workflow.step_statuses[next_steps[0]] = StepStatus.ACTIVE
            self.step_start_times[next_steps[0]] = time.time()
        else:
            # Workflow completed
            workflow.current_step = None
            workflow.completed_at = datetime.now()
            self._update_user_behavior(workflow.user_id, "workflow_completed")
        
        workflow.updated_at = datetime.now()
        self._auto_save_workflow(workflow_id)
        return True
    
    def jump_to_step(self, workflow_id: str, step_id: str) -> bool:
        """Jump directly to a specific step (if dependencies are met)"""
        workflow = self.get_workflow(workflow_id)
        if not workflow or step_id not in self.steps:
            return False
        
        step = self.steps[step_id]
        
        # Check if step is enabled for current mode
        if not self._is_step_enabled_for_mode(step, workflow.mode):
            return False
        
        # Check dependencies
        for dep in step.depends_on:
            if workflow.step_statuses.get(dep) != StepStatus.COMPLETED:
                return False
        
        # Mark previous current step as pending (if it was active)
        if workflow.current_step and workflow.step_statuses.get(workflow.current_step) == StepStatus.ACTIVE:
            workflow.step_statuses[workflow.current_step] = StepStatus.PENDING
        
        # Set new current step
        workflow.current_step = step_id
        workflow.step_statuses[step_id] = StepStatus.ACTIVE
        workflow.updated_at = datetime.now()
        
        # Track jump behavior
        self._update_user_behavior(workflow.user_id, f"jump_to_{step_id}")
        self.step_start_times[step_id] = time.time()
        
        self._auto_save_workflow(workflow_id)
        return True
    
    def skip_step(self, workflow_id: str, step_id: str) -> bool:
        """Skip an optional step"""
        workflow = self.get_workflow(workflow_id)
        if not workflow or step_id not in self.steps:
            return False
        
        step = self.steps[step_id]
        if step.required:
            return False
        
        workflow.step_statuses[step_id] = StepStatus.SKIPPED
        
        # If this was the current step, advance to next
        if workflow.current_step == step_id:
            next_steps = self._get_available_steps(workflow)
            if next_steps:
                workflow.current_step = next_steps[0] 
                workflow.step_statuses[next_steps[0]] = StepStatus.ACTIVE
                self.step_start_times[next_steps[0]] = time.time()
            else:
                workflow.current_step = None
        
        workflow.updated_at = datetime.now()
        self._auto_save_workflow(workflow_id)
        return True
    
    def get_workflow_progress(self, workflow_id: str) -> Dict:
        """Get workflow progress information"""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return {}
        
        enabled_steps = [s for s_id, s in self.steps.items() 
                        if self._is_step_enabled_for_mode(s, workflow.mode)]
        
        total_steps = len(enabled_steps)
        completed_steps = len([s for s, status in workflow.step_statuses.items() 
                              if status == StepStatus.COMPLETED])
        pending_steps = len([s for s, status in workflow.step_statuses.items() 
                           if status == StepStatus.PENDING])
        
        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'pending_steps': pending_steps,
            'current_step': workflow.current_step,
            'progress_percentage': progress_percentage,
            'is_completed': workflow.completed_at is not None,
            'estimated_time_remaining': self._estimate_remaining_time(workflow)
        }
    
    def _get_available_steps(self, workflow: WorkflowState) -> List[str]:
        """Get list of steps that can be executed next"""
        available = []
        
        for step_id, step in self.steps.items():
            # Skip if not enabled for current mode
            if not self._is_step_enabled_for_mode(step, workflow.mode):
                continue
            
            # Skip if already completed or currently active
            if workflow.step_statuses.get(step_id) in [StepStatus.COMPLETED, StepStatus.ACTIVE]:
                continue
            
            # Check dependencies
            deps_met = True
            for dep in step.depends_on:
                if workflow.step_statuses.get(dep) != StepStatus.COMPLETED:
                    deps_met = False
                    break
            
            if deps_met:
                available.append(step_id)
        
        return available
    
    def _is_step_enabled_for_mode(self, step: WorkflowStep, mode: WorkflowMode) -> bool:
        """Check if step is enabled for the given workflow mode"""
        if mode == WorkflowMode.QUICK_GENERATE:
            return step.quick_mode_enabled
        elif mode == WorkflowMode.GUIDED_MODE:
            return step.guided_mode_enabled
        elif mode == WorkflowMode.ADVANCED_MODE:
            return step.advanced_mode_enabled
        return False
    
    def _auto_save_workflow(self, workflow_id: str):
        """Auto-save workflow if enabled and interval passed"""
        workflow = self.workflows.get(workflow_id)
        if not workflow or not workflow.auto_save_enabled:
            return
        
        now = time.time()
        last_save = self.last_auto_save.get(workflow_id, 0)
        
        if now - last_save >= self.auto_save_interval:
            self.save_workflow(workflow_id)
            self.last_auto_save[workflow_id] = now
    
    def _estimate_remaining_time(self, workflow: WorkflowState) -> int:
        """Estimate remaining completion time in seconds"""
        remaining_steps = [s_id for s_id, s in self.steps.items() 
                          if self._is_step_enabled_for_mode(s, workflow.mode) and 
                          workflow.step_statuses.get(s_id) not in [StepStatus.COMPLETED, StepStatus.SKIPPED]]
        
        total_time = 0
        user_behavior = self.user_behaviors.get(workflow.user_id)
        
        for step_id in remaining_steps:
            step = self.steps[step_id]
            # Use user's historical time if available, otherwise use estimate
            if user_behavior and step_id in user_behavior.average_step_time:
                total_time += user_behavior.average_step_time[step_id]
            else:
                total_time += step.estimated_time
        
        return int(total_time)
    
    def _update_user_behavior(self, user_id: str, action: str, completion_time: float = None):
        """Update user behavior data for adaptive interfaces"""
        if user_id not in self.user_behaviors:
            self.user_behaviors[user_id] = UserBehaviorData(user_id=user_id)
        
        behavior = self.user_behaviors[user_id]
        behavior.feature_usage[action] = behavior.feature_usage.get(action, 0) + 1
        
        if completion_time and action in self.steps:
            # Update average step time with exponential moving average
            if action in behavior.average_step_time:
                behavior.average_step_time[action] = (behavior.average_step_time[action] * 0.7 + completion_time * 0.3)
            else:
                behavior.average_step_time[action] = completion_time
        
        if action == "workflow_completed":
            behavior.successful_completions += 1
        
        behavior.last_updated = datetime.now()
        self._save_user_behavior(user_id)
    
    def _load_user_behaviors(self):
        """Load user behavior data from storage"""
        try:
            for filepath in self.behavior_storage_dir.glob("behavior_*.json"):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                behavior = UserBehaviorData(**data)
                self.user_behaviors[behavior.user_id] = behavior
        except Exception as e:
            # Silent fail - behavior data is not critical
            pass
    
    def _save_user_behavior(self, user_id: str):
        """Save user behavior data"""
        try:
            if user_id not in self.user_behaviors:
                return
            
            behavior = self.user_behaviors[user_id]
            filepath = self.behavior_storage_dir / f"behavior_{user_id}.json"
            
            # Convert to dict, handling datetime
            data = asdict(behavior)
            data['last_updated'] = behavior.last_updated.isoformat()
            if behavior.preferred_mode:
                data['preferred_mode'] = behavior.preferred_mode.value
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Silent fail - behavior data is not critical
            pass
    
    def get_smart_suggestions(self, user_id: str) -> Dict:
        """Get smart suggestions based on user behavior"""
        behavior = self.user_behaviors.get(user_id)
        if not behavior:
            return {}
        
        suggestions = {}
        
        # Suggest preferred mode
        if behavior.successful_completions >= 3:
            mode_usage = {}
            for action, count in behavior.feature_usage.items():
                if "quick_generate" in action:
                    mode_usage[WorkflowMode.QUICK_GENERATE] = mode_usage.get(WorkflowMode.QUICK_GENERATE, 0) + count
                elif "guided_mode" in action:
                    mode_usage[WorkflowMode.GUIDED_MODE] = mode_usage.get(WorkflowMode.GUIDED_MODE, 0) + count
                elif "advanced_mode" in action:
                    mode_usage[WorkflowMode.ADVANCED_MODE] = mode_usage.get(WorkflowMode.ADVANCED_MODE, 0) + count
            
            if mode_usage:
                preferred_mode = max(mode_usage, key=mode_usage.get)
                suggestions['preferred_mode'] = preferred_mode
        
        # Suggest shortcuts for commonly used features
        common_actions = sorted(behavior.feature_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        suggestions['common_shortcuts'] = [action for action, _ in common_actions if action.startswith('jump_to_')]
        
        # Suggest quick templates based on usage
        template_usage = {k: v for k, v in behavior.feature_usage.items() if 'template' in k.lower()}
        if template_usage:
            suggestions['quick_templates'] = list(template_usage.keys())[:3]
        
        return suggestions
    
    def get_dashboard_widgets(self, user_id: str) -> List[Dict]:
        """Get personalized dashboard widgets based on user behavior"""
        behavior = self.user_behaviors.get(user_id)
        widgets = []
        
        # Always include recent workflows
        recent_workflows = self.list_user_workflows(user_id)[:3]
        if recent_workflows:
            widgets.append({
                'type': 'recent_workflows',
                'title': 'Recent Workflows',
                'data': recent_workflows,
                'priority': 1
            })
        
        if behavior:
            # Quick actions widget for power users
            if behavior.successful_completions >= 5:
                common_actions = sorted(behavior.feature_usage.items(), key=lambda x: x[1], reverse=True)[:4]
                widgets.append({
                    'type': 'quick_actions',
                    'title': 'Quick Actions',
                    'data': common_actions,
                    'priority': 2
                })
            
            # Performance stats widget
            if behavior.average_step_time:
                avg_completion = sum(behavior.average_step_time.values()) / len(behavior.average_step_time)
                widgets.append({
                    'type': 'performance_stats',
                    'title': 'Your Performance',
                    'data': {
                        'avg_completion_time': avg_completion,
                        'successful_completions': behavior.successful_completions,
                        'efficiency_score': min(100, max(0, 100 - (avg_completion / 300) * 100))  # Based on 5min benchmark
                    },
                    'priority': 3
                })
        
        # Sort by priority
        widgets.sort(key=lambda x: x['priority'])
        return widgets

# Global workflow engine instance
workflow_engine = FlexibleWorkflowEngine()

# Convenience functions for Streamlit integration
def create_workflow(user_id: str, mode: str) -> str:
    """Create a new workflow - Streamlit friendly"""
    mode_enum = WorkflowMode(mode)
    return workflow_engine.create_workflow(user_id, mode_enum)

def get_workflow_state(workflow_id: str) -> Optional[Dict]:
    """Get workflow state as dict - Streamlit friendly"""
    workflow = workflow_engine.get_workflow(workflow_id)
    return workflow.to_dict() if workflow else None

def advance_workflow_step(workflow_id: str, step_id: str, step_data: Dict = None) -> bool:
    """Advance workflow step - Streamlit friendly"""
    return workflow_engine.advance_step(workflow_id, step_id, step_data)

def jump_to_workflow_step(workflow_id: str, step_id: str) -> bool:
    """Jump to workflow step - Streamlit friendly"""
    return workflow_engine.jump_to_step(workflow_id, step_id)

def save_workflow_state(workflow_id: str) -> bool:
    """Save workflow state - Streamlit friendly"""
    return workflow_engine.save_workflow(workflow_id)

def get_workflow_progress(workflow_id: str) -> Dict:
    """Get workflow progress - Streamlit friendly"""
    return workflow_engine.get_workflow_progress(workflow_id)

def get_user_suggestions(user_id: str) -> Dict:
    """Get smart suggestions for user - Streamlit friendly"""
    return workflow_engine.get_smart_suggestions(user_id)

def get_user_dashboard_widgets(user_id: str) -> List[Dict]:
    """Get personalized dashboard widgets - Streamlit friendly"""
    return workflow_engine.get_dashboard_widgets(user_id)

def list_user_workflows(user_id: str) -> List[Dict]:
    """List user workflows - Streamlit friendly"""
    return workflow_engine.list_user_workflows(user_id)

def resume_latest_workflow(user_id: str) -> Optional[str]:
    """Resume latest workflow - Streamlit friendly"""
    return workflow_engine.resume_latest_workflow(user_id)

def register_keyboard_shortcut(workflow_id: str, key: str, callback: Callable):
    """Register keyboard shortcut for workflow"""
    # Store shortcut in session state for the UI to handle
    if 'workflow_shortcuts' not in st.session_state:
        st.session_state.workflow_shortcuts = {}
    
    if workflow_id not in st.session_state.workflow_shortcuts:
        st.session_state.workflow_shortcuts[workflow_id] = {}
    
    st.session_state.workflow_shortcuts[workflow_id][key] = callback