#!/usr/bin/env python3
"""
Wait for Streamlit Cloud app to be configured and working
"""
import time
import sys
from playwright.sync_api import sync_playwright

URL = "https://safestepscerts.streamlit.app/"

def check_app_status():
    """Check if the app is working"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # Navigate to the app
            page.goto(URL, wait_until='networkidle', timeout=30000)
            time.sleep(5)  # Wait for dynamic content
            
            # Get page content
            content = page.content()
            
            # Check status
            if "Missing required environment variables" in content:
                status = "error"
                message = "JWT_SECRET not configured"
            elif "SafeSteps Certificate Generator" in content and "Welcome" in content:
                status = "working"
                message = "App is working!"
            else:
                status = "unknown"
                message = "Unknown state"
                
            browser.close()
            return status, message, content
            
        except Exception as e:
            browser.close()
            return "error", str(e), ""

print("🔍 Monitoring Streamlit Cloud app...")
print(f"URL: {URL}")
print("Waiting for JWT_SECRET to be configured...")
print("Instructions:")
print("1. Go to https://share.streamlit.io")
print("2. Click on your app settings (⋮ menu → Settings)")
print("3. Navigate to 'Secrets' in the left sidebar")
print("4. Add: JWT_SECRET = \"your-generated-secret-here\"")
print("5. Save and the app will restart")
print("\nChecking every 30 seconds...\n")

check_count = 0
while True:
    check_count += 1
    print(f"Check #{check_count}...", end=" ", flush=True)
    
    status, message, content = check_app_status()
    
    if status == "working":
        print(f"✅ {message}")
        print("\n🎉 SUCCESS! The app is now fully functional!")
        print("You can now login with:")
        print("- Admin: admin / Admin@SafeSteps2024")
        print("- User: testuser / UserPass123")
        break
    else:
        print(f"❌ {message}")
        
    time.sleep(30)