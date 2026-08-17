@echo off
title BotZXY - Installa APK su Android
color 0A

echo ========================================
echo   BotZXY - Installa APK su Android
echo ========================================
echo.

REM Verifica ADB
adb version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] ADB non trovato!
    echo.
    echo Scarica Platform Tools da:
    echo https://developer.android.com/studio/releases/platform-tools
    echo.
    echo Dopo aver scaricato, estrai e aggiungi al PATH
    pause
    exit /b 1
)

REM Verifica dispositivo
adb devices
echo.

if not exist "dist\*.apk" (
    echo [ERRORE] Nessun APK trovato in dist\
    pause
    exit /b 1
)

echo Installazione...
for %%f in ("dist\*.apk") do (
    adb install -r "%%f"
    if errorlevel 1 (
        echo [ERRORE] Installazione fallita!
        echo Prova: adb uninstall org.botzxy
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   APK installato con successo!
echo ========================================
pause