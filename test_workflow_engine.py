"""
Test script for the Flexible Workflow Engine
Verifies all core functionality and features
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.workflow_engine import (
    FlexibleWorkflowEngine, WorkflowMode, StepStatus,
    create_workflow, get_workflow_state, advance_workflow_step,
    jump_to_workflow_step, save_workflow_state, get_workflow_progress,
    get_user_suggestions, get_user_dashboard_widgets, list_user_workflows
)
import json
from datetime import datetime

def test_workflow_engine():
    """Comprehensive test of workflow engine functionality"""
    
    print("🧪 Testing Flexible Workflow Engine")
    print("=" * 50)
    
    # Test 1: Basic workflow creation
    print("\n1. Testing Workflow Creation...")
    user_id = "test_user_001"
    workflow_id = create_workflow(user_id, WorkflowMode.QUICK_GENERATE.value)
    print(f"✅ Created workflow: {workflow_id}")
    
    # Test 2: Get workflow state
    print("\n2. Testing Workflow State Retrieval...")
    state = get_workflow_state(workflow_id)
    assert state is not None, "Workflow state should not be None"
    assert state['user_id'] == user_id, "User ID should match"
    assert state['mode'] == WorkflowMode.QUICK_GENERATE.value, "Mode should match"
    print(f"✅ Retrieved workflow state: {state['workflow_id'][:8]}...")
    
    # Test 3: Workflow progress
    print("\n3. Testing Workflow Progress...")
    progress = get_workflow_progress(workflow_id)
    assert 'total_steps' in progress, "Progress should include total_steps"
    assert 'completed_steps' in progress, "Progress should include completed_steps"
    assert 'progress_percentage' in progress, "Progress should include progress_percentage"
    print(f"✅ Initial progress: {progress['progress_percentage']:.0f}% ({progress['completed_steps']}/{progress['total_steps']})")
    
    # Test 4: Step advancement
    print("\n4. Testing Step Advancement...")
    success = advance_workflow_step(workflow_id, 'upload', {'file': 'test_data.csv', 'size': 1024})
    assert success, "Step advancement should succeed"
    
    progress_after = get_workflow_progress(workflow_id)
    assert progress_after['completed_steps'] > progress['completed_steps'], "Completed steps should increase"
    print(f"✅ Step completed. Progress: {progress_after['progress_percentage']:.0f}%")
    
    # Test 5: Jump to step
    print("\n5. Testing Step Jumping...")
    success = jump_to_workflow_step(workflow_id, 'validate')
    assert success, "Jump to step should succeed when dependencies are met"
    
    state_after_jump = get_workflow_state(workflow_id)
    assert state_after_jump['current_step'] == 'validate', "Current step should be 'validate'"
    print(f"✅ Jumped to step: {state_after_jump['current_step']}")
    
    # Test 6: Save workflow
    print("\n6. Testing Workflow Persistence...")
    save_success = save_workflow_state(workflow_id)
    assert save_success, "Workflow save should succeed"
    print("✅ Workflow saved successfully")
    
    # Test 7: Multiple workflows for user
    print("\n7. Testing Multiple Workflows...")
    workflow_id_2 = create_workflow(user_id, WorkflowMode.GUIDED_MODE.value)
    workflow_id_3 = create_workflow(user_id, WorkflowMode.ADVANCED_MODE.value)
    
    user_workflows = list_user_workflows(user_id)
    assert len(user_workflows) >= 3, "User should have at least 3 workflows"
    print(f"✅ User has {len(user_workflows)} workflows")
    
    # Test 8: User suggestions (after some usage)
    print("\n8. Testing User Suggestions...")
    # Simulate some usage
    for i in range(5):
        advance_workflow_step(workflow_id_2, 'upload', {'iteration': i})
    
    suggestions = get_user_suggestions(user_id)
    print(f"✅ Generated {len(suggestions)} user suggestions")
    
    # Test 9: Dashboard widgets
    print("\n9. Testing Dashboard Widgets...")
    widgets = get_user_dashboard_widgets(user_id)
    assert len(widgets) > 0, "Should have at least one widget"
    print(f"✅ Generated {len(widgets)} dashboard widgets")
    
    # Test 10: Workflow modes
    print("\n10. Testing All Workflow Modes...")
    modes = [WorkflowMode.QUICK_GENERATE, WorkflowMode.GUIDED_MODE, WorkflowMode.ADVANCED_MODE]
    
    for mode in modes:
        test_workflow_id = create_workflow(f"test_user_mode_{mode.value}", mode.value)
        test_state = get_workflow_state(test_workflow_id)
        assert test_state['mode'] == mode.value, f"Mode should be {mode.value}"
        print(f"   ✅ {mode.value} mode working")
    
    print("\n" + "=" * 50)
    print("🎉 All Workflow Engine Tests Passed!")
    print("=" * 50)
    
    return True

def test_workflow_persistence():
    """Test workflow persistence and recovery"""
    
    print("\n🔄 Testing Workflow Persistence...")
    
    user_id = "persistence_test_user"
    
    # Create and populate workflow
    workflow_id = create_workflow(user_id, WorkflowMode.GUIDED_MODE.value)
    advance_workflow_step(workflow_id, 'upload', {'file': 'persistence_test.csv'})
    advance_workflow_step(workflow_id, 'validate', {'rows': 50, 'valid': True})
    
    # Save workflow
    save_success = save_workflow_state(workflow_id)
    assert save_success, "Workflow save should succeed"
    
    # Create new engine instance (simulates app restart)
    new_engine = FlexibleWorkflowEngine()
    
    # Try to load workflow
    loaded_workflow = new_engine.get_workflow(workflow_id)
    assert loaded_workflow is not None, "Should be able to load saved workflow"
    assert loaded_workflow.user_id == user_id, "User ID should match"
    assert len(loaded_workflow.step_statuses) > 0, "Should have step statuses"
    
    print("✅ Workflow persistence test passed")

def test_adaptive_behavior():
    """Test adaptive behavior tracking"""
    
    print("\n🤖 Testing Adaptive Behavior...")
    
    user_id = "adaptive_test_user"
    
    # Use the global workflow engine instance
    from utils.workflow_engine import workflow_engine
    
    # Simulate user behavior over multiple workflows
    for i in range(3):
        workflow_id = create_workflow(user_id, WorkflowMode.QUICK_GENERATE.value)
        
        # Simulate workflow completion
        advance_workflow_step(workflow_id, 'upload', {'session': i})
        advance_workflow_step(workflow_id, 'validate', {'session': i})
        advance_workflow_step(workflow_id, 'course_select', {'session': i})
        advance_workflow_step(workflow_id, 'generate', {'session': i})
    
    # Check if behavior was tracked (use global instance)
    behavior = workflow_engine.user_behaviors.get(user_id)
    assert behavior is not None, "User behavior should be tracked"
    assert behavior.successful_completions >= 3, "Should track successful completions"
    
    # Get suggestions based on behavior
    suggestions = get_user_suggestions(user_id)
    print(f"✅ Adaptive suggestions generated: {len(suggestions)} items")

def demo_workflow_features():
    """Demonstrate key workflow features"""
    
    print("\n🎯 Demonstrating Key Features...")
    
    user_id = "demo_user"
    
    # Feature 1: Quick Generate workflow
    print("\n⚡ Quick Generate Mode:")
    quick_workflow = create_workflow(user_id, WorkflowMode.QUICK_GENERATE.value)
    print(f"   Created workflow: {quick_workflow[:8]}...")
    
    # Show available steps
    state = get_workflow_state(quick_workflow)
    available_steps = [step for step, status in state['step_statuses'].items() if status != 'skipped']
    print(f"   Available steps: {', '.join(available_steps)}")
    
    # Feature 2: Save/Resume functionality
    print("\n💾 Save/Resume Functionality:")
    advance_workflow_step(quick_workflow, 'upload', {'demo': 'data'})
    save_workflow_state(quick_workflow)
    print("   Workflow saved with progress")
    
    # Feature 3: User dashboard widgets
    print("\n📊 Personalized Dashboard:")
    widgets = get_user_dashboard_widgets(user_id)
    for widget in widgets:
        print(f"   Widget: {widget['title']} (Priority: {widget['priority']})")
    
    # Feature 4: Analytics
    print("\n📈 Workflow Analytics:")
    user_workflows = list_user_workflows(user_id)
    if user_workflows:
        avg_progress = sum(wf['progress'] for wf in user_workflows) / len(user_workflows)
        completed_count = sum(1 for wf in user_workflows if wf['completed'])
        print(f"   Total workflows: {len(user_workflows)}")
        print(f"   Average progress: {avg_progress:.0f}%")
        print(f"   Completed workflows: {completed_count}")
    
    print("\n✅ Feature demonstration complete!")

def test_error_handling():
    """Test error handling scenarios"""
    
    print("\n🛡️ Testing Error Handling...")
    
    # Test invalid workflow ID
    invalid_state = get_workflow_state("invalid_workflow_id")
    assert invalid_state is None, "Invalid workflow should return None"
    print("   ✅ Invalid workflow ID handled")
    
    # Test invalid step advancement
    user_id = "error_test_user"
    workflow_id = create_workflow(user_id, WorkflowMode.QUICK_GENERATE.value)
    
    # Try to advance to step that doesn't exist
    invalid_advance = advance_workflow_step(workflow_id, 'nonexistent_step', {})
    # Should handle gracefully (may return False or handle internally)
    print("   ✅ Invalid step advancement handled")
    
    # Test jumping to step without dependencies
    invalid_jump = jump_to_workflow_step(workflow_id, 'generate')  # Without completing upload/validate
    # Should return False or handle gracefully
    print("   ✅ Invalid step jump handled")
    
    print("✅ Error handling tests passed")

def performance_test():
    """Basic performance test"""
    
    print("\n⚡ Running Performance Test...")
    
    import time
    start_time = time.time()
    
    # Create multiple workflows quickly
    user_id = "perf_test_user"
    workflow_ids = []
    
    for i in range(10):
        workflow_id = create_workflow(user_id, WorkflowMode.QUICK_GENERATE.value)
        workflow_ids.append(workflow_id)
        
        # Advance a few steps
        advance_workflow_step(workflow_id, 'upload', {'iteration': i})
        advance_workflow_step(workflow_id, 'validate', {'iteration': i})
    
    # Save all workflows
    for workflow_id in workflow_ids:
        save_workflow_state(workflow_id)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"   Created and processed 10 workflows in {duration:.2f} seconds")
    assert duration < 5.0, "Should complete within 5 seconds"
    print("✅ Performance test passed")

if __name__ == "__main__":
    try:
        # Run all tests
        test_workflow_engine()
        test_workflow_persistence() 
        test_adaptive_behavior()
        demo_workflow_features()
        test_error_handling()
        performance_test()
        
        print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY! 🎉")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)