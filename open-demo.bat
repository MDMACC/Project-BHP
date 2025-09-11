@echo off
echo Opening Bluez PowerHouse Management System Demo...
echo.
echo This demo showcases:
echo - Dashboard with real-time statistics
echo - Parts inventory management
echo - Order tracking with countdown timers
echo - Contact management
echo - Scheduling system
echo - Shipping tracking
echo.
echo Opening in your default browser (new tab)...
REM Try to open in a new tab
start "" demo.html
REM Alternative method if the above doesn't work
REM start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --new-tab "%~dp0demo.html"
echo.
echo Demo opened successfully!
echo Press any key to exit...
pause >nul
