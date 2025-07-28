#!/usr/bin/env python3
"""
Monitor Streamlit Cloud app until it's working
"""
import time
import requests
from datetime import datetime

URL = "https://safestepscerts.streamlit.app/"

print("🔍 Monitoring Streamlit Cloud app...")
print(f"URL: {URL}")
print("Waiting for JWT_SECRET to be configured...\n")

while True:
    try:
        # Check if the app is responding
        response = requests.get(URL, timeout=10)
        
        # Check if error message is still present
        if "Missing required environment variables" in response.text:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Still showing configuration error - JWT_SECRET not set")
        elif "SafeSteps Certificate Generator" in response.text and "Login" in response.text:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ APP IS WORKING! Login page is accessible!")
            print("The app is now ready to use!")
            break
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ App content changed - checking...")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 App may be restarting: {str(e)}")
    
    # Wait 30 seconds before next check
    time.sleep(30)

print("\n✅ Success! The app is now fully functional!")
print("You can now login with:")
print("- Admin: admin / Admin@SafeSteps2024")
print("- User: testuser / UserPass123")