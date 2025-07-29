#!/bin/bash
# Script to clear Streamlit cache and restart the app

echo "=== Clearing Streamlit Cache and Restarting ==="

# Kill any existing Streamlit processes
echo "1. Stopping existing Streamlit processes..."
pkill -f "streamlit run" || echo "No Streamlit processes running"

# Clear Streamlit cache
echo "2. Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache/*
rm -rf .streamlit/cache/*

# Clear browser cache reminder
echo "3. IMPORTANT: Clear your browser cache!"
echo "   - Chrome/Firefox: Ctrl+Shift+Delete"
echo "   - Select 'Cached images and files'"
echo "   - Clear data for the last hour"

# Wait for user confirmation
echo ""
read -p "Press Enter after clearing browser cache..."

# Restart Streamlit with specific flags
echo "4. Starting Streamlit with fresh state..."
streamlit run app.py --server.runOnSave false --server.port 8502

echo ""
echo "=== App is running on http://localhost:8502 ==="
echo "Using port 8502 to avoid any cached content on port 8501"