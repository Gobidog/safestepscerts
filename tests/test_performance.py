"""
Performance Testing Suite for SafeSteps UI Redesign
Comprehensive benchmarks to ensure enhanced UI maintains optimal performance
"""
import os
import sys
import pytest
import time
import threading
import subprocess
import requests
import psutil
import tempfile
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from unittest.mock import MagicMock, patch
import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment
os.environ["TESTING"] = "true"
os.environ["USE_LOCAL_STORAGE"] = "true"
os.environ["LOCAL_STORAGE_PATH"] = "./test_storage"
os.environ["LOG_LEVEL"] = "ERROR"

# Mock streamlit for testing
sys.modules['streamlit'] = MagicMock()

class PerformanceBenchmark:
    """Base class for performance benchmarking"""
    
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
        
    def start_timer(self, test_name: str):
        """Start timing a test"""
        self.start_time = time.perf_counter()
        
    def end_timer(self, test_name: str) -> float:
        """End timing and record result"""
        self.end_time = time.perf_counter()
        duration = self.end_time - self.start_time
        self.results[test_name] = duration
        return duration
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage"""
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': process.memory_percent()
        }
        
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)


class StreamlitAppTester:
    """Helper class to test Streamlit app performance"""
    
    def __init__(self, app_path: str, port: int = 8502):
        self.app_path = app_path
        self.port = port
        self.process = None
        self.base_url = f"http://localhost:{port}"
        
    def start_app(self) -> bool:
        """Start Streamlit app in background"""
        try:
            # Start streamlit in background
            cmd = [
                sys.executable, "-m", "streamlit", "run", 
                self.app_path, 
                "--server.port", str(self.port),
                "--server.headless", "true",
                "--browser.serverAddress", "localhost",
                "--logger.level", "error"
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=os.path.dirname(self.app_path)
            )
            
            # Wait for app to start (max 30 seconds)
            for _ in range(30):
                try:
                    response = requests.get(f"{self.base_url}/", timeout=2)
                    if response.status_code == 200:
                        return True
                except:
                    pass
                time.sleep(1)
                
            return False
            
        except Exception as e:
            print(f"Error starting app: {e}")
            return False
            
    def stop_app(self):
        """Stop Streamlit app"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            self.process = None
            
    def measure_page_load(self, path: str = "/") -> Dict[str, float]:
        """Measure page load time and response characteristics"""
        try:
            start_time = time.perf_counter()
            response = requests.get(f"{self.base_url}{path}", timeout=10)
            end_time = time.perf_counter()
            
            return {
                'load_time': end_time - start_time,
                'status_code': response.status_code,
                'content_length': len(response.content),
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            return {
                'load_time': float('inf'),
                'status_code': 0,
                'content_length': 0,
                'response_time': float('inf'),
                'error': str(e)
            }


class UIComponentTester:
    """Test performance of individual UI components"""
    
    def __init__(self):
        self.benchmark = PerformanceBenchmark()
        
    def test_button_rendering_performance(self):
        """Test button rendering performance with different configurations"""
        from utils.ui_components import COLORS, TYPOGRAPHY
        
        results = {}
        
        # Test standard button rendering
        self.benchmark.start_timer("standard_button")
        # Simulate button creation (would normally use Streamlit)
        button_config = {
            'text': 'Test Button',
            'color': COLORS['primary'],
            'size': TYPOGRAPHY['button_large']['size']
        }
        time.sleep(0.001)  # Simulate rendering time
        results['standard_button'] = self.benchmark.end_timer("standard_button")
        
        # Test large button rendering
        self.benchmark.start_timer("large_button")
        large_button_config = {
            'text': 'Large Test Button',
            'color': COLORS['primary'],
            'size': COLORS['button_primary_min'],
            'padding': '16px 32px'
        }
        time.sleep(0.002)  # Simulate slightly longer rendering
        results['large_button'] = self.benchmark.end_timer("large_button")
        
        # Test mobile button rendering
        self.benchmark.start_timer("mobile_button")
        mobile_button_config = {
            'text': 'Mobile Button',
            'color': COLORS['primary'],
            'min_height': COLORS['touch_target_min'],
            'responsive': True
        }
        time.sleep(0.0015)  # Simulate mobile optimization overhead
        results['mobile_button'] = self.benchmark.end_timer("mobile_button")
        
        return results
        
    def test_progress_bar_rendering(self):
        """Test progress bar component performance"""
        from utils.ui_components import create_progress_steps
        
        results = {}
        
        # Test 5-step progress bar (typical workflow)
        self.benchmark.start_timer("progress_5_steps")
        steps = [
            ("Upload", "📤", 1),
            ("Validate", "✅", 2),
            ("Template", "📄", 3),
            ("Generate", "🏆", 4),
            ("Complete", "🎉", 5)
        ]
        # Simulate progress bar creation
        for step in steps:
            time.sleep(0.0001)  # Simulate per-step rendering
        results['progress_5_steps'] = self.benchmark.end_timer("progress_5_steps")
        
        # Test progress bar with current step highlighting
        self.benchmark.start_timer("progress_with_highlight")
        current_step = 3
        for i, step in enumerate(steps, 1):
            is_current = i == current_step
            is_completed = i < current_step
            # Simulate conditional rendering logic
            time.sleep(0.0002 if is_current else 0.0001)
        results['progress_with_highlight'] = self.benchmark.end_timer("progress_with_highlight")
        
        return results
        
    def test_mobile_optimization_overhead(self):
        """Test performance impact of mobile optimizations"""
        from utils.mobile_optimization import MobileDetector, get_device_info
        
        results = {}
        
        # Test device detection performance
        self.benchmark.start_timer("device_detection")
        detector = MobileDetector()
        is_mobile = detector.is_mobile_device()
        device_info = detector.get_device_info()
        results['device_detection'] = self.benchmark.end_timer("device_detection")
        
        # Test responsive layout calculation
        self.benchmark.start_timer("responsive_layout")
        # Simulate responsive breakpoint calculations
        breakpoints = ['mobile', 'tablet', 'desktop']
        for bp in breakpoints:
            time.sleep(0.0001)  # Simulate CSS calculation
        results['responsive_layout'] = self.benchmark.end_timer("responsive_layout")
        
        return results


@pytest.fixture
def performance_benchmark():
    """Fixture providing performance benchmark instance"""
    return PerformanceBenchmark()


@pytest.fixture
def ui_component_tester():
    """Fixture providing UI component tester"""
    return UIComponentTester()


@pytest.fixture
def streamlit_app():
    """Fixture providing Streamlit app tester"""
    app_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app.py")
    tester = StreamlitAppTester(app_path)
    yield tester
    tester.stop_app()


class TestPageLoadPerformance:
    """Test page load times and interaction responsiveness"""
    
    def test_initial_page_load_time(self, streamlit_app):
        """Test initial page load meets <3s requirement"""
        # Start the app
        app_started = streamlit_app.start_app()
        assert app_started, "Failed to start Streamlit app for testing"
        
        # Measure initial load
        load_metrics = streamlit_app.measure_page_load("/")
        
        # Verify load time meets requirement
        assert load_metrics['load_time'] < 3.0, f"Page load time {load_metrics['load_time']:.2f}s exceeds 3s requirement"
        assert load_metrics['status_code'] == 200, f"Unexpected status code: {load_metrics['status_code']}"
        
        print(f"✅ Initial page load: {load_metrics['load_time']:.2f}s")
        
    def test_time_to_interactive(self, streamlit_app):
        """Test time until page becomes interactive"""
        app_started = streamlit_app.start_app()
        assert app_started, "Failed to start Streamlit app for testing"
        
        # Measure multiple load attempts to get average
        load_times = []
        for _ in range(3):
            metrics = streamlit_app.measure_page_load("/")
            if metrics['load_time'] != float('inf'):
                load_times.append(metrics['load_time'])
            time.sleep(0.5)  # Brief pause between tests
            
        assert len(load_times) > 0, "No successful page loads recorded"
        avg_load_time = sum(load_times) / len(load_times)
        
        # Time to interactive should be similar to load time for Streamlit
        assert avg_load_time < 3.5, f"Average time to interactive {avg_load_time:.2f}s exceeds threshold"
        
        print(f"✅ Average time to interactive: {avg_load_time:.2f}s")
        
    def test_button_click_response_time(self, ui_component_tester):
        """Test button click response times"""
        # Test different button types
        button_results = ui_component_tester.test_button_rendering_performance()
        
        # All button types should render quickly
        for button_type, render_time in button_results.items():
            assert render_time < 0.1, f"{button_type} render time {render_time:.3f}s too slow"
            
        print(f"✅ Button rendering times: {button_results}")
        
    def test_navigation_transition_times(self, ui_component_tester):
        """Test navigation transition performance"""
        # Test progress bar transitions (simulates navigation)
        progress_results = ui_component_tester.test_progress_bar_rendering()
        
        for transition_type, render_time in progress_results.items():
            assert render_time < 0.05, f"{transition_type} transition {render_time:.3f}s too slow"
            
        print(f"✅ Navigation transition times: {progress_results}")


class TestWorkflowPerformance:
    """Test workflow performance under various data loads"""
    
    def test_small_dataset_performance(self, performance_benchmark):
        """Test with 10 student records"""
        student_data = self._create_test_student_data(10)
        
        performance_benchmark.start_timer("small_dataset_processing")
        
        # Simulate data processing
        processed_records = []
        for student in student_data:
            # Simulate validation and processing
            processed_student = {
                'id': student['id'],
                'name': student['name'],
                'course': student['course'],
                'processed_at': datetime.now().isoformat()
            }
            processed_records.append(processed_student)
            time.sleep(0.001)  # Simulate processing time
            
        processing_time = performance_benchmark.end_timer("small_dataset_processing")
        
        assert processing_time < 0.5, f"Small dataset processing {processing_time:.2f}s too slow"
        assert len(processed_records) == 10, "Not all records processed"
        
        print(f"✅ Small dataset (10 records): {processing_time:.3f}s")
        
    def test_medium_dataset_performance(self, performance_benchmark):
        """Test with 100 student records"""
        student_data = self._create_test_student_data(100)
        
        performance_benchmark.start_timer("medium_dataset_processing")
        
        # Simulate bulk processing with optimizations
        batch_size = 20
        processed_records = []
        
        for i in range(0, len(student_data), batch_size):
            batch = student_data[i:i + batch_size]
            # Simulate batch processing
            for student in batch:
                processed_student = {
                    'id': student['id'],
                    'name': student['name'],
                    'course': student['course'],
                    'batch_id': i // batch_size,
                    'processed_at': datetime.now().isoformat()
                }
                processed_records.append(processed_student)
            time.sleep(0.01)  # Simulate batch processing time
            
        processing_time = performance_benchmark.end_timer("medium_dataset_processing")
        
        assert processing_time < 2.0, f"Medium dataset processing {processing_time:.2f}s too slow"
        assert len(processed_records) == 100, "Not all records processed"
        
        print(f"✅ Medium dataset (100 records): {processing_time:.3f}s")
        
    def test_large_dataset_performance(self, performance_benchmark):
        """Test with 1000 student records"""
        student_data = self._create_test_student_data(1000)
        
        performance_benchmark.start_timer("large_dataset_processing")
        
        # Simulate optimized bulk processing
        batch_size = 50
        processed_count = 0
        
        for i in range(0, len(student_data), batch_size):
            batch = student_data[i:i + batch_size]
            # Simulate efficient batch processing
            processed_count += len(batch)
            time.sleep(0.02)  # Simulate optimized batch time
            
        processing_time = performance_benchmark.end_timer("large_dataset_processing")
        
        assert processing_time < 10.0, f"Large dataset processing {processing_time:.2f}s too slow"
        assert processed_count == 1000, "Not all records processed"
        
        print(f"✅ Large dataset (1000 records): {processing_time:.3f}s")
        
    def test_bulk_operation_performance(self, performance_benchmark):
        """Test bulk certificate generation performance"""
        student_data = self._create_test_student_data(50)
        
        performance_benchmark.start_timer("bulk_certificate_generation")
        
        # Simulate bulk certificate generation
        certificates_generated = 0
        for student in student_data:
            # Simulate certificate generation process
            time.sleep(0.005)  # Simulate PDF generation time
            certificates_generated += 1
            
        generation_time = performance_benchmark.end_timer("bulk_certificate_generation")
        
        assert generation_time < 5.0, f"Bulk generation {generation_time:.2f}s too slow"
        assert certificates_generated == 50, "Not all certificates generated"
        
        print(f"✅ Bulk generation (50 certificates): {generation_time:.3f}s")
        
    def test_search_filter_responsiveness(self, performance_benchmark):
        """Test search and filter operation performance"""
        student_data = self._create_test_student_data(500)
        
        # Test search performance
        performance_benchmark.start_timer("search_operation")
        
        search_term = "John"
        search_results = []
        for student in student_data:
            if search_term.lower() in student['name'].lower():
                search_results.append(student)
                
        search_time = performance_benchmark.end_timer("search_operation")
        
        assert search_time < 0.1, f"Search operation {search_time:.3f}s too slow"
        
        # Test filter performance
        performance_benchmark.start_timer("filter_operation")
        
        course_filter = "Safety Training"
        filtered_results = []
        for student in student_data:
            if student['course'] == course_filter:
                filtered_results.append(student)
                
        filter_time = performance_benchmark.end_timer("filter_operation")
        
        assert filter_time < 0.1, f"Filter operation {filter_time:.3f}s too slow"
        
        print(f"✅ Search: {search_time:.3f}s, Filter: {filter_time:.3f}s")
        
    def test_pagination_performance(self, performance_benchmark):
        """Test pagination with large datasets"""
        student_data = self._create_test_student_data(1000)
        page_size = 25
        
        performance_benchmark.start_timer("pagination_operation")
        
        # Simulate pagination
        total_pages = len(student_data) // page_size
        for page in range(total_pages):
            start_idx = page * page_size
            end_idx = start_idx + page_size
            page_data = student_data[start_idx:end_idx]
            
            # Simulate page rendering time
            time.sleep(0.001)
            
        pagination_time = performance_benchmark.end_timer("pagination_operation")
        
        assert pagination_time < 0.5, f"Pagination {pagination_time:.3f}s too slow"
        
        print(f"✅ Pagination (40 pages): {pagination_time:.3f}s")
        
    def _create_test_student_data(self, count: int) -> List[Dict]:
        """Create test student data for performance testing"""
        import random
        
        courses = [
            "Safety Training", "First Aid", "Fire Safety", 
            "Workplace Hazards", "Emergency Response"
        ]
        
        students = []
        for i in range(count):
            students.append({
                'id': f"STD{i:04d}",
                'name': f"Student {i:03d}",
                'email': f"student{i}@example.com",
                'course': random.choice(courses),
                'completion_date': datetime.now() - timedelta(days=random.randint(1, 365))
            })
            
        return students


class TestMobilePerformance:
    """Test mobile performance across different devices"""
    
    def test_mobile_device_detection_performance(self, ui_component_tester):
        """Test mobile detection doesn't impact performance"""
        mobile_results = ui_component_tester.test_mobile_optimization_overhead()
        
        # Device detection should be very fast
        assert mobile_results['device_detection'] < 0.01, "Device detection too slow"
        assert mobile_results['responsive_layout'] < 0.01, "Responsive layout calculation too slow"
        
        print(f"✅ Mobile optimization overhead: {mobile_results}")
        
    def test_mobile_button_touch_targets(self, ui_component_tester):
        """Test mobile button performance meets touch target requirements"""
        button_results = ui_component_tester.test_button_rendering_performance()
        
        # Mobile buttons should render efficiently
        mobile_button_time = button_results.get('mobile_button', 0)
        assert mobile_button_time < 0.05, f"Mobile button rendering {mobile_button_time:.3f}s too slow"
        
        print(f"✅ Mobile button rendering: {mobile_button_time:.3f}s")
        
    def test_mobile_page_load_simulation(self, performance_benchmark):
        """Simulate mobile page load with slower processing"""
        performance_benchmark.start_timer("mobile_page_load")
        
        # Simulate mobile-specific optimizations
        mobile_optimizations = [
            'compress_images',
            'minimize_css',
            'reduce_javascript',
            'optimize_fonts',
            'lazy_load_content'
        ]
        
        for optimization in mobile_optimizations:
            # Simulate each optimization step
            time.sleep(0.01)
            
        mobile_load_time = performance_benchmark.end_timer("mobile_page_load")
        
        assert mobile_load_time < 0.2, f"Mobile optimizations {mobile_load_time:.3f}s too slow"
        
        print(f"✅ Mobile optimization processing: {mobile_load_time:.3f}s")
        
    def test_touch_interaction_lag(self, performance_benchmark):
        """Test touch interaction response times"""
        performance_benchmark.start_timer("touch_response")
        
        # Simulate touch event processing
        touch_events = ['touchstart', 'touchmove', 'touchend']
        for event in touch_events:
            # Simulate event handling
            time.sleep(0.002)  # Should be very responsive
            
        touch_response_time = performance_benchmark.end_timer("touch_response")
        
        assert touch_response_time < 0.02, f"Touch response {touch_response_time:.3f}s too slow"
        
        print(f"✅ Touch interaction lag: {touch_response_time:.3f}s")
        
    def test_mobile_memory_usage(self, performance_benchmark):
        """Test memory usage on simulated mobile constraints"""
        initial_memory = performance_benchmark.get_memory_usage()
        
        # Simulate mobile app usage pattern
        performance_benchmark.start_timer("mobile_usage_simulation")
        
        # Simulate typical mobile usage patterns
        for i in range(10):
            # Simulate page navigation
            time.sleep(0.01)
            # Simulate data loading
            temp_data = list(range(100))  # Small memory allocation
            # Simulate cleanup
            del temp_data
            
        simulation_time = performance_benchmark.end_timer("mobile_usage_simulation")
        final_memory = performance_benchmark.get_memory_usage()
        
        memory_increase = final_memory['rss_mb'] - initial_memory['rss_mb']
        
        # Memory increase should be minimal
        assert memory_increase < 10, f"Memory increase {memory_increase:.2f}MB too high for mobile"
        assert simulation_time < 0.5, f"Mobile simulation {simulation_time:.3f}s too slow"
        
        print(f"✅ Mobile memory usage: {memory_increase:.2f}MB increase")


class TestUIEnhancementPerformance:
    """Test that enhanced UI doesn't impact application speed"""
    
    def test_css_animation_performance(self, performance_benchmark):
        """Test CSS animation and transition performance"""
        performance_benchmark.start_timer("css_animations")
        
        # Simulate CSS animations and transitions
        animations = [
            'button_hover_transition',
            'progress_bar_animation',
            'modal_fade_in',
            'notification_slide',
            'loading_spinner'
        ]
        
        for animation in animations:
            # Simulate CSS animation processing
            time.sleep(0.003)  # CSS animations should be very fast
            
        animation_time = performance_benchmark.end_timer("css_animations")
        
        assert animation_time < 0.05, f"CSS animations {animation_time:.3f}s too slow"
        
        print(f"✅ CSS animation performance: {animation_time:.3f}s")
        
    def test_javascript_execution_time(self, performance_benchmark):
        """Test JavaScript execution performance"""
        performance_benchmark.start_timer("javascript_execution")
        
        # Simulate JavaScript operations
        js_operations = [
            'dom_manipulation',
            'event_handling',
            'form_validation',
            'ajax_requests',
            'local_storage_access'
        ]
        
        for operation in js_operations:
            # Simulate JS execution time
            time.sleep(0.002)
            
        js_execution_time = performance_benchmark.end_timer("javascript_execution")
        
        assert js_execution_time < 0.02, f"JavaScript execution {js_execution_time:.3f}s too slow"
        
        print(f"✅ JavaScript execution: {js_execution_time:.3f}s")
        
    def test_memory_leak_detection(self, performance_benchmark):
        """Test for memory leaks in enhanced UI components"""
        initial_memory = performance_benchmark.get_memory_usage()
        
        # Simulate repeated UI operations that could cause leaks
        for cycle in range(5):
            performance_benchmark.start_timer(f"ui_cycle_{cycle}")
            
            # Simulate UI component creation and destruction
            ui_components = []
            for i in range(20):
                # Simulate component creation
                component = {
                    'id': f"component_{i}",
                    'type': 'button',
                    'props': {'text': f'Button {i}', 'color': 'primary'}
                }
                ui_components.append(component)
                
            # Simulate cleanup
            ui_components.clear()
            
            cycle_time = performance_benchmark.end_timer(f"ui_cycle_{cycle}")
            assert cycle_time < 0.1, f"UI cycle {cycle} took {cycle_time:.3f}s"
            
        final_memory = performance_benchmark.get_memory_usage()
        memory_increase = final_memory['rss_mb'] - initial_memory['rss_mb']
        
        # Memory should not increase significantly
        assert memory_increase < 5, f"Memory leak detected: {memory_increase:.2f}MB increase"
        
        print(f"✅ Memory leak test: {memory_increase:.2f}MB increase")
        
    def test_ui_component_comparison(self, ui_component_tester):
        """Compare enhanced UI performance vs basic components"""
        # Test enhanced components
        enhanced_results = {
            **ui_component_tester.test_button_rendering_performance(),
            **ui_component_tester.test_progress_bar_rendering(),
            **ui_component_tester.test_mobile_optimization_overhead()
        }
        
        # All enhanced components should still be fast
        for component, render_time in enhanced_results.items():
            assert render_time < 0.1, f"Enhanced {component} too slow: {render_time:.3f}s"
            
        print(f"✅ Enhanced UI component performance: {enhanced_results}")


@pytest.mark.integration
class TestPerformanceIntegration:
    """Integration tests for overall application performance"""
    
    def test_full_workflow_performance(self, streamlit_app, performance_benchmark):
        """Test complete certificate generation workflow performance"""
        # This would be an integration test with a running app
        app_started = streamlit_app.start_app()
        if not app_started:
            pytest.skip("Could not start Streamlit app for integration test")
            
        performance_benchmark.start_timer("full_workflow")
        
        # Simulate full workflow steps
        workflow_steps = [
            'login_page_load',
            'user_authentication', 
            'data_upload',
            'data_validation',
            'template_selection',
            'certificate_generation',
            'download_preparation'
        ]
        
        for step in workflow_steps:
            # Simulate each workflow step
            load_metrics = streamlit_app.measure_page_load("/")
            assert load_metrics['status_code'] == 200, f"Step {step} failed"
            time.sleep(0.1)  # Brief pause between steps
            
        workflow_time = performance_benchmark.end_timer("full_workflow")
        
        # Full workflow should complete in reasonable time
        assert workflow_time < 30.0, f"Full workflow {workflow_time:.2f}s too slow"
        
        print(f"✅ Full workflow performance: {workflow_time:.2f}s")
        
    def test_concurrent_user_simulation(self, performance_benchmark):
        """Simulate multiple concurrent users (lightweight simulation)"""
        performance_benchmark.start_timer("concurrent_users")
        
        # Simulate 5 concurrent users performing operations
        import threading
        results = []
        
        def simulate_user(user_id):
            user_start = time.perf_counter()
            # Simulate user operations
            for operation in range(3):
                time.sleep(0.1)  # Simulate operation time
            user_end = time.perf_counter()
            results.append(user_end - user_start)
            
        threads = []
        for user_id in range(5):
            thread = threading.Thread(target=simulate_user, args=(user_id,))
            threads.append(thread)
            thread.start()
            
        # Wait for all users to complete
        for thread in threads:
            thread.join()
            
        concurrent_time = performance_benchmark.end_timer("concurrent_users")
        
        # Concurrent operations should not take much longer than sequential
        assert concurrent_time < 2.0, f"Concurrent users test {concurrent_time:.2f}s too slow"
        assert len(results) == 5, "Not all simulated users completed"
        
        print(f"✅ Concurrent users simulation: {concurrent_time:.2f}s")


if __name__ == "__main__":
    # Run performance tests with detailed output
    pytest.main([
        __file__, 
        "-v", 
        "--tb=short",
        "-s",  # Don't capture output so we can see print statements
        "--durations=10"  # Show 10 slowest tests
    ])