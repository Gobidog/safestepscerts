import asyncio
import os
from playwright.async_api import async_playwright

async def test_authentication():
    """Test authentication with Playwright"""
    results = {
        "admin_login": False,
        "user_login": False,
        "wrong_password": False,
        "session_persistence": False,
        "errors": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        
        try:
            # Test 1: Admin login
            page = await context.new_page()
            await page.goto('http://localhost:8503')
            await page.wait_for_timeout(2000)
            
            # Check if login page loaded
            try:
                await page.wait_for_selector('input[type="text"]', timeout=5000)
                print("✅ Login page loaded successfully")
                
                # Try admin login
                await page.fill('input[type="text"]', 'admin')
                await page.fill('input[type="password"]', 'Admin@SafeSteps2024')
                await page.click('button:has-text("Login")')
                await page.wait_for_timeout(2000)
                
                # Check if logged in
                if await page.is_visible('text=Admin Dashboard') or await page.is_visible('text=Certificate Generator'):
                    results["admin_login"] = True
                    print("✅ Admin login successful")
                else:
                    print("❌ Admin login failed")
                    
            except Exception as e:
                results["errors"].append(f"Admin login error: {str(e)}")
                print(f"❌ Admin login error: {e}")
                
            # Test 2: Wrong password
            page2 = await context.new_page()
            await page2.goto('http://localhost:8503')
            await page2.wait_for_timeout(2000)
            
            try:
                await page2.fill('input[type="text"]', 'admin')
                await page2.fill('input[type="password"]', 'wrongpassword')
                await page2.click('button:has-text("Login")')
                await page2.wait_for_timeout(2000)
                
                if await page2.is_visible('text=Invalid username or password'):
                    results["wrong_password"] = True
                    print("✅ Wrong password correctly rejected")
                else:
                    print("❌ Wrong password not rejected properly")
                    
            except Exception as e:
                results["errors"].append(f"Wrong password test error: {str(e)}")
                print(f"❌ Wrong password test error: {e}")
                
        finally:
            await browser.close()
            
    return results

# Run the test
if __name__ == "__main__":
    results = asyncio.run(test_authentication())
    print("\n=== AUTHENTICATION TEST RESULTS ===")
    print(f"Admin Login: {'✅ PASS' if results['admin_login'] else '❌ FAIL'}")
    print(f"Wrong Password Rejection: {'✅ PASS' if results['wrong_password'] else '❌ FAIL'}")
    if results['errors']:
        print(f"Errors: {results['errors']}")
