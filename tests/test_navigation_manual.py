"""
Manual navigation test using Playwright
Tests the navigation issues reported by the user
"""
import asyncio
from playwright.async_api import async_playwright
import time

async def test_navigation():
    """Test navigation flows to verify no unexpected logouts"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("=== NAVIGATION TEST STARTED ===")
        
        # Test 1: Load the app
        print("\n1. Testing app load...")
        await page.goto("http://localhost:8501")
        await page.wait_for_load_state("networkidle")
        print("✓ App loaded successfully")
        
        # Test 2: Check for login form
        print("\n2. Checking login page...")
        try:
            # Look for password input which indicates login page
            password_input = await page.wait_for_selector('input[type="password"]', timeout=5000)
            if password_input:
                print("✓ Login page displayed correctly")
        except:
            print("✗ Login page not found\!")
            
        # Test 3: Try logging in as user
        print("\n3. Testing user login...")
        try:
            # Enter password
            await page.fill('input[type="password"]', 'safeSteps2024\!user')
            # Click login button
            login_button = await page.query_selector('button:has-text("Login")')
            if login_button:
                await login_button.click()
                await page.wait_for_load_state("networkidle")
                print("✓ Login button clicked")
                
                # Check if we're logged in
                await page.wait_for_timeout(2000)
                content = await page.content()
                if "Welcome" in content or "Certificate" in content:
                    print("✓ Successfully logged in")
                else:
                    print("✗ Login may have failed")
        except Exception as e:
            print(f"✗ Login test error: {e}")
            
        # Test 4: Navigate to different pages
        print("\n4. Testing navigation between pages...")
        try:
            # Check current URL
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Try navigating to pages
            await page.goto("http://localhost:8501/1_login")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1000)
            login_url = page.url
            print(f"After login navigation: {login_url}")
            
            await page.goto("http://localhost:8501/2_generate")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1000)
            generate_url = page.url
            print(f"After generate navigation: {generate_url}")
            
            await page.goto("http://localhost:8501/3_admin")
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(1000)
            admin_url = page.url
            print(f"After admin navigation: {admin_url}")
            
        except Exception as e:
            print(f"✗ Navigation test error: {e}")
            
        # Take screenshots
        print("\n5. Taking screenshots...")
        await page.screenshot(path="/home/marsh/coding/Safesteps/evidence/system_verification_agent_20250728_083719/final_state.png")
        print("✓ Screenshot saved")
        
        await browser.close()
        print("\n=== NAVIGATION TEST COMPLETED ===")

if __name__ == "__main__":
    asyncio.run(test_navigation())
