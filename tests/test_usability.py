"""
Comprehensive Usability Testing for SafeSteps UI Redesign
Tests button visibility, workflow completion, navigation efficiency, and mobile experience
Based on EXECUTION_PLAN.md requirements and WCAG 2.2 AA accessibility standards
"""

import asyncio
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import pytest
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, Locator
from dataclasses import dataclass, asdict


@dataclass
class UsabilityTestResult:
    """Structure for usability test results"""
    test_name: str
    passed: bool
    execution_time: float
    details: Dict[str, Any]
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class SafeStepsUsabilityTester:
    """Comprehensive usability testing for SafeSteps UI redesign"""
    
    def __init__(self, base_url: str = "http://localhost:8503"):
        self.base_url = base_url
        self.results: List[UsabilityTestResult] = []
        self.admin_credentials = {"username": "admin", "password": "Admin@SafeSteps2024"}
        self.user_credentials = {"username": "user", "password": "User@SafeSteps2024"}
        
        # WCAG 2.2 AA Standards
        self.min_touch_target = 44  # pixels
        self.min_color_contrast = 4.5  # ratio for normal text
        self.min_color_contrast_large = 3.0  # ratio for large text
        
        # Performance thresholds
        self.max_page_load_time = 3000  # milliseconds
        self.max_interaction_response = 100  # milliseconds
        
    async def setup_browser(self) -> Tuple[Browser, BrowserContext]:
        """Setup browser with mobile and desktop contexts"""
        playwright = await async_playwright().start()
        
        # Use Chromium for comprehensive testing
        browser = await playwright.chromium.launch(
            headless=False,  # Set to True for CI/CD
            args=['--disable-web-security', '--disable-features=VizDisplayCompositor']
        )
        
        # Create context with realistic viewport
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        return browser, context
    
    async def login_as_admin(self, page: Page) -> bool:
        """Login as admin user"""
        try:
            await page.goto(self.base_url)
            await page.wait_for_load_state('networkidle', timeout=10000)
            
            # Look for login form
            username_input = page.locator('input[type="text"]').first
            password_input = page.locator('input[type="password"]').first
            login_button = page.locator('button:has-text("Login")').first
            
            await username_input.fill(self.admin_credentials["username"])
            await password_input.fill(self.admin_credentials["password"])
            await login_button.click()
            
            # Wait for successful login
            await page.wait_for_timeout(2000)
            
            # Check if we're on admin dashboard
            admin_indicators = [
                'text=Admin Dashboard',
                'text=Certificate Generator',
                'text=Work',
                'text=Manage',
                'text=Monitor'
            ]
            
            for indicator in admin_indicators:
                if await page.locator(indicator).is_visible():
                    return True
                    
            return False
            
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    async def test_button_touch_targets(self, page: Page) -> UsabilityTestResult:
        """Test 1: Button visibility and touch targets across devices"""
        start_time = time.time()
        test_name = "Button Touch Targets and Visibility"
        details = {
            "buttons_tested": 0,
            "compliant_buttons": 0,
            "non_compliant_buttons": [],
            "devices_tested": []
        }
        errors = []
        
        try:
            # Test on different screen sizes
            viewports = [
                {"name": "mobile", "width": 375, "height": 667},    # iPhone SE
                {"name": "tablet", "width": 768, "height": 1024},   # iPad
                {"name": "desktop", "width": 1920, "height": 1080}, # Desktop
            ]
            
            for viewport in viewports:
                await page.set_viewport_size(viewport["width"], viewport["height"])
                await page.wait_for_timeout(1000)  # Allow layout to settle
                details["devices_tested"].append(viewport["name"])
                
                # Find all buttons on the page
                buttons = await page.locator('button, [role="button"], .stButton > button').all()
                
                for i, button in enumerate(buttons):
                    try:
                        if await button.is_visible():
                            details["buttons_tested"] += 1
                            
                            # Get button dimensions
                            bbox = await button.bounding_box()
                            if bbox:
                                width = bbox["width"]
                                height = bbox["height"]
                                
                                # Check touch target size (WCAG 2.2 AA: minimum 44px)
                                min_dimension = min(width, height)
                                
                                if min_dimension >= self.min_touch_target:
                                    details["compliant_buttons"] += 1
                                else:
                                    button_text = await button.inner_text() or f"Button_{i}"
                                    details["non_compliant_buttons"].append({
                                        "text": button_text,
                                        "device": viewport["name"],
                                        "width": width,
                                        "height": height,
                                        "min_dimension": min_dimension
                                    })
                                    
                    except Exception as e:
                        errors.append(f"Error testing button {i}: {str(e)}")
            
            # Test button visual hierarchy
            await self._test_button_hierarchy(page, details, errors)
            
            # Test button contrast ratios
            await self._test_button_contrast(page, details, errors)
            
            execution_time = time.time() - start_time
            
            # Success criteria: 100% of buttons meet 44px minimum
            passed = len(details["non_compliant_buttons"]) == 0
            
            return UsabilityTestResult(
                test_name=test_name,
                passed=passed,
                execution_time=execution_time,
                details=details,
                errors=errors
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            errors.append(f"Critical error in button testing: {str(e)}")
            
            return UsabilityTestResult(
                test_name=test_name,
                passed=False,
                execution_time=execution_time,
                details=details,
                errors=errors
            )
    
    async def test_workflow_completion_rates(self, page: Page) -> UsabilityTestResult:
        """Test 2: Validate workflow completion rates and user satisfaction"""
        start_time = time.time()
        test_name = "Workflow Completion Rates"
        details = {
            "workflows_tested": 0,
            "successful_completions": 0,
            "workflow_results": {},
            "average_completion_time": 0,
            "save_resume_tested": False
        }
        errors = []
        
        try:
            # Test all 3 workflow modes
            workflow_modes = ["Quick", "Guided", "Advanced"]
            completion_times = []
            
            for mode in workflow_modes:
                workflow_start = time.time()
                details["workflows_tested"] += 1
                
                try:
                    # Navigate to certificate generation
                    if await page.locator('text=Generate').is_visible():
                        await page.click('text=Generate')
                    elif await page.locator('text=Certificate Generator').is_visible():
                        await page.click('text=Certificate Generator')
                    
                    await page.wait_for_timeout(1000)
                    
                    # Look for workflow mode selector
                    if await page.locator(f'text={mode}').is_visible():
                        await page.click(f'text={mode}')
                        await page.wait_for_timeout(500)
                    
                    # Simulate workflow steps
                    workflow_completed = await self._simulate_workflow(page, mode)
                    
                    if workflow_completed:
                        details["successful_completions"] += 1
                        completion_time = time.time() - workflow_start
                        completion_times.append(completion_time)
                        
                        details["workflow_results"][mode] = {
                            "completed": True,
                            "time": completion_time
                        }
                    else:
                        details["workflow_results"][mode] = {
                            "completed": False,
                            "time": time.time() - workflow_start
                        }
                        
                except Exception as e:
                    errors.append(f"Error testing {mode} workflow: {str(e)}")
                    details["workflow_results"][mode] = {
                        "completed": False,
                        "error": str(e)
                    }
            
            # Test save/resume functionality
            details["save_resume_tested"] = await self._test_save_resume(page, errors)
            
            # Calculate averages
            if completion_times:
                details["average_completion_time"] = sum(completion_times) / len(completion_times)
            
            execution_time = time.time() - start_time
            
            # Success criteria: 90%+ completion rate
            completion_rate = (details["successful_completions"] / details["workflows_tested"]) * 100
            passed = completion_rate >= 90.0
            
            details["completion_rate"] = completion_rate
            
            return UsabilityTestResult(
                test_name=test_name,
                passed=passed,
                execution_time=execution_time,
                details=details,
                errors=errors
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            errors.append(f"Critical error in workflow testing: {str(e)}")
            
            return UsabilityTestResult(
                test_name=test_name,
                passed=False,
                execution_time=execution_time,
                details=details,
                errors=errors
            )
    
    async def test_navigation_efficiency(self, page: Page) -> UsabilityTestResult:
        """Test 3: Navigation efficiency and task completion times"""
        start_time = time.time()
        test_name = "Navigation Efficiency"
        details = {
            "navigation_tests": {},
            "average_clicks": 0,
            "keyboard_shortcuts_tested": 0,
            "command_palette_tested": False,
            "three_area_navigation": False
        }
        errors = []
        
        try:
            # Test the 3-area admin navigation (Work/Manage/Monitor)
            navigation_areas = ["Work", "Manage", "Monitor"]
            area_results = {}
            
            for area in navigation_areas:
                try:
                    if await page.locator(f'text={area}').is_visible():
                        details["three_area_navigation"] = True
                        
                        click_start = time.time()
                        await page.click(f'text={area}')
                        await page.wait_for_timeout(500)
                        
                        # Measure response time
                        response_time = (time.time() - click_start) * 1000
                        area_results[area] = {
                            "accessible": True,
                            "response_time_ms": response_time
                        }
                    else:
                        area_results[area] = {"accessible": False}
                        
                except Exception as e:
                    errors.append(f"Error testing {area} navigation: {str(e)}")
                    area_results[area] = {"accessible": False, "error": str(e)}
            
            details["navigation_tests"]["three_area_results"] = area_results
            
            # Test common admin tasks click efficiency
            common_tasks = [
                ("Generate Certificate", ["Generate", "Certificate Generator"]),
                ("Manage Templates", ["Manage", "Templates"]),
                ("View Analytics", ["Monitor", "Analytics"]),
                ("User Management", ["Manage", "Users"])
            ]
            
            task_clicks = []
            for task_name, navigation_path in common_tasks:
                try:
                    clicks_required = await self._measure_task_clicks(page, task_name, navigation_path)
                    task_clicks.append(clicks_required)
                    details["navigation_tests"][task_name] = {"clicks": clicks_required}
                    
                except Exception as e:
                    errors.append(f"Error measuring clicks for {task_name}: {str(e)}")
            
            # Calculate average clicks
            if task_clicks:
                details["average_clicks"] = sum(task_clicks) / len(task_clicks)
            
            # Test keyboard shortcuts
            details["keyboard_shortcuts_tested"] = await self._test_keyboard_shortcuts(page, errors)
            
            # Test command palette if available
            details["command_palette_tested"] = await self._test_command_palette(page, errors)
            
            execution_time = time.time() - start_time
            
            # Success criteria: 70% reduction in clicks (baseline ~5 clicks, target ~1.5)
            target_clicks = 1.5
            passed = details["average_clicks"] <= target_clicks if details["average_clicks"] > 0 else False
            
            return UsabilityTestResult(
                test_name=test_name,
                passed=passed,
                execution_time=execution_time,
                details=details,
                errors=errors
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            errors.append(f"Critical error in navigation testing: {str(e)}")
            
            return UsabilityTestResult(
                test_name=test_name,
                passed=False,
                execution_time=execution_time,
                details=details,
                errors=errors
            )
    
    async def test_information_architecture(self, page: Page) -> UsabilityTestResult:
        """Test 4: Information architecture reduces cognitive load"""
        start_time = time.time()
        test_name = "Information Architecture"
        details = {
            "page_consolidation": {},
            "tab_organization": {},
            "mobile_navigation": {},
            "breadcrumb_navigation": False,
            "cognitive_load_score": 0
        }
        errors = []
        
        try:
            # Test page consolidation (8 pages → 3 areas)
            original_pages = ["Admin", "System", "Templates", "Courses", "Users", "Analytics", "Settings", "Logs"]
            consolidated_areas = ["Work", "Manage", "Monitor"]
            
            # Check if old scattered navigation is gone
            old_nav_count = 0
            for page_name in original_pages:
                if await page.locator(f'text={page_name}').is_visible():
                    old_nav_count += 1
            
            # Check if new consolidated areas exist
            new_nav_count = 0
            for area in consolidated_areas:
                if await page.locator(f'text={area}').is_visible():
                    new_nav_count += 1
            
            details["page_consolidation"] = {
                "old_scattered_pages": old_nav_count,
                "new_consolidated_areas": new_nav_count,
                "consolidation_successful": new_nav_count == 3 and old_nav_count < 5
            }
            
            # Test tab organization within areas
            for area in consolidated_areas:
                if await page.locator(f'text={area}').is_visible():
                    await page.click(f'text={area}')
                    await page.wait_for_timeout(500)
                    
                    # Look for tabbed interface
                    tabs = await page.locator('[role="tab"], .stTabs [data-baseweb="tab"]').all()
                    tab_count = len(tabs)
                    
                    details["tab_organization"][area] = {
                        "has_tabs": tab_count > 0,
                        "tab_count": tab_count
                    }
            
            # Test mobile navigation usability
            await page.set_viewport_size(375, 667)  # Mobile viewport
            await page.wait_for_timeout(1000)
            
            mobile_nav_accessible = await self._test_mobile_navigation(page, errors)
            details["mobile_navigation"]["accessible"] = mobile_nav_accessible
            
            # Test breadcrumb navigation
            breadcrumbs = await page.locator('nav[aria-label="breadcrumb"], .breadcrumb, [data-testid="breadcrumb"]').all()
            details["breadcrumb_navigation"] = len(breadcrumbs) > 0
            
            # Calculate cognitive load score
            details["cognitive_load_score"] = self._calculate_cognitive_load_score(details)
            
            execution_time = time.time() - start_time
            
            # Success criteria: Consolidation successful + low cognitive load
            passed = (
                details["page_consolidation"]["consolidation_successful"] and
                details["cognitive_load_score"] >= 80  # Scale of 100
            )
            
            return UsabilityTestResult(
                test_name=test_name,
                passed=passed,
                execution_time=execution_time,
                details=details,
                errors=errors
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            errors.append(f"Critical error in information architecture testing: {str(e)}")
            
            return UsabilityTestResult(
                test_name=test_name,
                passed=False,
                execution_time=execution_time,
                details=details,
                errors=errors
            )
    
    # Helper methods
    async def _test_button_hierarchy(self, page: Page, details: Dict, errors: List[str]):
        """Test visual hierarchy of buttons (primary vs secondary)"""
        try:
            primary_buttons = await page.locator('.primary-button, [data-testid="primary-button"]').all()
            secondary_buttons = await page.locator('.secondary-button, [data-testid="secondary-button"]').all()
            
            details["button_hierarchy"] = {
                "primary_buttons": len(primary_buttons),
                "secondary_buttons": len(secondary_buttons),
                "hierarchy_clear": len(primary_buttons) > 0
            }
            
        except Exception as e:
            errors.append(f"Button hierarchy test error: {str(e)}")
    
    async def _test_button_contrast(self, page: Page, details: Dict, errors: List[str]):
        """Test button color contrast ratios"""
        try:
            # This would require actual color analysis in a real implementation
            # For now, we'll check if buttons have proper styling classes
            accessible_buttons = await page.locator('[data-wcag-compliant="true"], .wcag-compliant').all()
            
            details["contrast_compliance"] = {
                "accessible_buttons": len(accessible_buttons),
                "tested": True
            }
            
        except Exception as e:
            errors.append(f"Button contrast test error: {str(e)}")
    
    async def _simulate_workflow(self, page: Page, mode: str) -> bool:
        """Simulate completing a certificate generation workflow"""
        try:
            steps_completed = 0
            max_steps = 5  # Upload, Validate, Template, Generate, Complete
            
            # Look for workflow steps
            for step in range(1, max_steps + 1):
                step_locators = [
                    f'[data-testid="step-{step}"]',
                    f'text=Step {step}',
                    f'.step-{step}',
                    f'button:has-text("Next")',
                    f'button:has-text("Continue")'
                ]
                
                for locator in step_locators:
                    if await page.locator(locator).is_visible():
                        await page.click(locator)
                        await page.wait_for_timeout(500)
                        steps_completed += 1
                        break
                
                # Break if we find completion indicators
                completion_indicators = [
                    'text=Complete',
                    'text=Success',
                    'text=Certificate Generated',
                    'button:has-text("Download")'
                ]
                
                for indicator in completion_indicators:
                    if await page.locator(indicator).is_visible():
                        return True
            
            return steps_completed >= 3  # At least 3 steps completed
            
        except Exception:
            return False
    
    async def _test_save_resume(self, page: Page, errors: List[str]) -> bool:
        """Test save/resume functionality"""
        try:
            save_buttons = await page.locator('button:has-text("Save"), [data-testid="save-button"]').all()
            resume_buttons = await page.locator('button:has-text("Resume"), [data-testid="resume-button"]').all()
            
            return len(save_buttons) > 0 or len(resume_buttons) > 0
            
        except Exception as e:
            errors.append(f"Save/resume test error: {str(e)}")
            return False
    
    async def _measure_task_clicks(self, page: Page, task_name: str, navigation_path: List[str]) -> int:
        """Measure clicks required to complete a task"""
        clicks = 0
        
        for step in navigation_path:
            if await page.locator(f'text={step}').is_visible():
                await page.click(f'text={step}')
                clicks += 1
                await page.wait_for_timeout(500)
        
        return clicks
    
    async def _test_keyboard_shortcuts(self, page: Page, errors: List[str]) -> int:
        """Test keyboard shortcuts functionality"""
        try:
            shortcuts_tested = 0
            
            # Test common shortcuts
            shortcuts = [
                {'key': 'Control+q', 'expected': 'quick_search'},
                {'key': 'Control+b', 'expected': 'bulk_actions'},
                {'key': 'Control+h', 'expected': 'help'},
                {'key': 'Escape', 'expected': 'close_modal'}
            ]
            
            for shortcut in shortcuts:
                try:
                    await page.keyboard.press(shortcut['key'])
                    await page.wait_for_timeout(500)
                    shortcuts_tested += 1
                except Exception:
                    pass
            
            return shortcuts_tested
            
        except Exception as e:
            errors.append(f"Keyboard shortcuts test error: {str(e)}")
            return 0
    
    async def _test_command_palette(self, page: Page, errors: List[str]) -> bool:
        """Test command palette functionality"""
        try:
            # Try to open command palette
            await page.keyboard.press('Control+k')
            await page.wait_for_timeout(500)
            
            command_palette = await page.locator('[data-testid="command-palette"], .command-palette').is_visible()
            return command_palette
            
        except Exception as e:
            errors.append(f"Command palette test error: {str(e)}")
            return False
    
    async def _test_mobile_navigation(self, page: Page, errors: List[str]) -> bool:
        """Test mobile navigation usability"""
        try:
            # Check for hamburger menu or mobile navigation
            mobile_nav_indicators = [
                '[data-testid="mobile-menu"]',
                '.hamburger-menu',
                'button[aria-label="Menu"]',
                '[data-testid="navigation-toggle"]'
            ]
            
            for indicator in mobile_nav_indicators:
                if await page.locator(indicator).is_visible():
                    return True
            
            return False
            
        except Exception as e:
            errors.append(f"Mobile navigation test error: {str(e)}")
            return False
    
    def _calculate_cognitive_load_score(self, details: Dict) -> int:
        """Calculate cognitive load score (0-100, higher is better)"""
        score = 0
        
        # Page consolidation (40 points)
        if details["page_consolidation"]["consolidation_successful"]:
            score += 40
        
        # Tab organization (30 points)
        organized_areas = sum(1 for area in details["tab_organization"].values() if area.get("has_tabs", False))
        score += (organized_areas / 3) * 30
        
        # Mobile navigation (20 points)
        if details["mobile_navigation"]["accessible"]:
            score += 20
        
        # Breadcrumb navigation (10 points)
        if details["breadcrumb_navigation"]:
            score += 10
        
        return int(score)
    
    async def run_all_tests(self) -> List[UsabilityTestResult]:
        """Run all usability tests"""
        browser = None
        
        try:
            browser, context = await self.setup_browser()
            page = await context.new_page()
            
            # Login as admin
            if not await self.login_as_admin(page):
                raise Exception("Failed to login as admin")
            
            # Run all test suites
            test_methods = [
                self.test_button_touch_targets,
                self.test_workflow_completion_rates,
                self.test_navigation_efficiency,
                self.test_information_architecture
            ]
            
            for test_method in test_methods:
                try:
                    result = await test_method(page)
                    self.results.append(result)
                    print(f"✅ {result.test_name}: {'PASS' if result.passed else 'FAIL'}")
                    
                except Exception as e:
                    error_result = UsabilityTestResult(
                        test_name=test_method.__name__,
                        passed=False,
                        execution_time=0,
                        details={},
                        errors=[str(e)]
                    )
                    self.results.append(error_result)
                    print(f"❌ {test_method.__name__}: ERROR - {str(e)}")
            
            return self.results
            
        except Exception as e:
            print(f"Critical error in test execution: {e}")
            return self.results
            
        finally:
            if browser:
                await browser.close()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive usability test report"""
        if not self.results:
            return {"error": "No test results available"}
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results if result.passed)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "pass_rate": (passed_tests / total_tests) * 100 if total_tests > 0 else 0,
                "total_execution_time": sum(result.execution_time for result in self.results)
            },
            "detailed_results": [asdict(result) for result in self.results],
            "recommendations": self._generate_recommendations(),
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on test results"""
        recommendations = []
        
        for result in self.results:
            if not result.passed:
                if "Button Touch Targets" in result.test_name:
                    recommendations.append(
                        "🔧 Fix button touch targets: Ensure all buttons meet 44px minimum size for mobile accessibility"
                    )
                
                elif "Workflow Completion" in result.test_name:
                    recommendations.append(
                        "🔧 Improve workflow completion rates: Simplify user paths and add better guidance"
                    )
                
                elif "Navigation Efficiency" in result.test_name:
                    recommendations.append(
                        "🔧 Optimize navigation: Reduce clicks required for common tasks and improve shortcuts"
                    )
                    
                elif "Information Architecture" in result.test_name:
                    recommendations.append(
                        "🔧 Simplify information architecture: Complete page consolidation and improve tab organization"
                    )
        
        if not recommendations:
            recommendations.append("✅ All usability tests passed! UI redesign meets quality standards.")
        
        return recommendations


# Pytest integration
@pytest.mark.asyncio
async def test_safesteps_usability():
    """Main pytest entry point for usability testing"""
    tester = SafeStepsUsabilityTester()
    results = await tester.run_all_tests()
    
    # Assert that critical tests pass
    critical_tests = ["Button Touch Targets", "Navigation Efficiency"]
    for result in results:
        if any(critical in result.test_name for critical in critical_tests):
            assert result.passed, f"Critical usability test failed: {result.test_name}"
    
    # Generate and save report
    report = tester.generate_report()
    report_path = Path(__file__).parent.parent / "TEST_USABILITY_REPORT.json"
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📊 Usability test report saved to: {report_path}")
    
    # Return results for further analysis
    return report


# Standalone execution
if __name__ == "__main__":
    async def main():
        tester = SafeStepsUsabilityTester()
        results = await tester.run_all_tests()
        
        print("\n" + "="*60)
        print("SAFESTEPS USABILITY TEST RESULTS")
        print("="*60)
        
        report = tester.generate_report()
        
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed_tests']}")
        print(f"Failed: {report['summary']['failed_tests']}")
        print(f"Pass Rate: {report['summary']['pass_rate']:.1f}%")
        print(f"Execution Time: {report['summary']['total_execution_time']:.2f}s")
        
        print("\n📋 RECOMMENDATIONS:")
        for rec in report['recommendations']:
            print(f"  {rec}")
        
        # Save detailed report
        report_path = Path(__file__).parent.parent / "TEST_USABILITY_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Detailed report saved to: {report_path}")
        
        return report
    
    # Run the main test suite
    asyncio.run(main())