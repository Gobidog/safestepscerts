"""
Simple workflow engine test to debug behavior tracking
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.workflow_engine import FlexibleWorkflowEngine, WorkflowMode
import time

def test_behavior_tracking():
    """Test behavior tracking specifically"""
    
    print("Testing behavior tracking...")
    
    engine = FlexibleWorkflowEngine()
    user_id = "test_behavior_user"
    
    # Create workflow
    workflow_id = engine.create_workflow(user_id, WorkflowMode.QUICK_GENERATE)
    print(f"Created workflow: {workflow_id}")
    
    # Check if user behavior was initialized
    print(f"User behaviors: {list(engine.user_behaviors.keys())}")
    
    # Advance steps and track behavior
    engine.step_start_times['upload'] = time.time()
    time.sleep(0.1)  # Simulate work
    success = engine.advance_step(workflow_id, 'upload', {'test': 'data'})
    print(f"Advanced upload step: {success}")
    
    # Check behavior after step
    behavior = engine.user_behaviors.get(user_id)
    print(f"Behavior exists: {behavior is not None}")
    if behavior:
        print(f"Feature usage: {behavior.feature_usage}")
        print(f"Average step time: {behavior.average_step_time}")
        print(f"Successful completions: {behavior.successful_completions}")
    
    # Complete workflow
    engine.step_start_times['validate'] = time.time()
    time.sleep(0.1)
    engine.advance_step(workflow_id, 'validate', {'test': 'data'})
    
    engine.step_start_times['course_select'] = time.time()
    time.sleep(0.1)
    engine.advance_step(workflow_id, 'course_select', {'test': 'data'})
    
    engine.step_start_times['generate'] = time.time()
    time.sleep(0.1)
    engine.advance_step(workflow_id, 'generate', {'test': 'data'})
    
    # Check final behavior
    final_behavior = engine.user_behaviors.get(user_id)
    if final_behavior:
        print(f"Final completions: {final_behavior.successful_completions}")
        print(f"Final feature usage: {final_behavior.feature_usage}")
    
    return final_behavior is not None

if __name__ == "__main__":
    success = test_behavior_tracking()
    print(f"Behavior tracking test: {'PASSED' if success else 'FAILED'}")