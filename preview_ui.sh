#!/bin/bash
# SafeSteps UI Preview Launcher Script

echo "🎨 SafeSteps UI Preview System"
echo "=============================="
echo ""

# Check if streamlit is available
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Please install it with: pip install streamlit"
    exit 1
fi

# Check if UI files exist
if [ ! -f "ui_mockups_v1_minimalist.py" ]; then
    echo "❌ V1 mockup file not found: ui_mockups_v1_minimalist.py"
    exit 1
fi

if [ ! -f "ui_mockups_v2_modern.py" ]; then
    echo "❌ V2 mockup file not found: ui_mockups_v2_modern.py"
    exit 1
fi

if [ ! -f "ui_preview_launcher.py" ]; then
    echo "❌ Preview launcher not found: ui_preview_launcher.py"
    exit 1
fi

echo "Select an option:"
echo "1) Preview Launcher (Compare both versions)"
echo "2) V1: Minimalist Professional"
echo "3) V2: Modern Interactive"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Launching Preview Launcher..."
        streamlit run ui_preview_launcher.py
        ;;
    2)
        echo "🚀 Launching V1: Minimalist Professional..."
        streamlit run ui_mockups_v1_minimalist.py
        ;;
    3)
        echo "🚀 Launching V2: Modern Interactive..."
        streamlit run ui_mockups_v2_modern.py
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac