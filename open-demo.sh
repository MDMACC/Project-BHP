#!/bin/bash

echo "Opening Bluez PowerHouse Management System Demo..."
echo ""
echo "This demo showcases:"
echo "- Dashboard with real-time statistics"
echo "- Parts inventory management"
echo "- Order tracking with countdown timers"
echo "- Contact management"
echo "- Scheduling system"
echo "- Shipping tracking"
echo ""
echo "Opening in your default browser..."

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Open the HTML file in the default browser (new tab)
if command -v open &> /dev/null; then
    # macOS - open in new tab
    open -n "$DIR/demo.html"
elif command -v xdg-open &> /dev/null; then
    # Linux - open in new tab
    xdg-open "$DIR/demo.html" &
elif command -v google-chrome &> /dev/null; then
    # Chrome fallback
    google-chrome --new-tab "$DIR/demo.html" &
elif command -v firefox &> /dev/null; then
    # Firefox fallback
    firefox --new-tab "$DIR/demo.html" &
else
    # Final fallback
    echo "Please open demo.html in your web browser"
    exit 1
fi

echo ""
echo "Demo opened successfully!"
echo "Press any key to exit..."
read -n 1 -s
