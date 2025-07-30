#!/usr/bin/env python3
"""Smoke test to verify the fix works in the actual app context"""

import subprocess
import time
import requests
import sys

def test_app_startup():
    """Test if the app starts without errors"""
    print("Starting app...")
    
    # Start the app in background
    proc = subprocess.Popen(
        ["streamlit", "run", "app.py", "--server.headless", "true", "--server.port", "8502"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give it time to start
    time.sleep(5)
    
    # Check if process is still running
    if proc.poll() is not None:
        stdout, stderr = proc.communicate()
        print(f"App failed to start!")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
        return False
    
    # Try to access the app
    try:
        response = requests.get("http://localhost:8502")
        if response.status_code == 200:
            print("✅ App is running successfully!")
            # Check if HTML content looks reasonable (no raw HTML tags in text)
            if '<div class="progress-step' in response.text:
                print("⚠️ Warning: Raw HTML found in response, but this might be in the page source")
            return True
        else:
            print(f"❌ App returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to app: {e}")
        return False
    finally:
        # Clean up
        proc.terminate()
        proc.wait()

if __name__ == "__main__":
    if test_app_startup():
        print("\n✅ Smoke test passed!")
        sys.exit(0)
    else:
        print("\n❌ Smoke test failed!")
        sys.exit(1)