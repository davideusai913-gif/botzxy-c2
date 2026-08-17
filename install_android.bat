@echo off
title BotZXY - Installa APK su Android
color 0A

echo ========================================
echo   BotZXY - Installa APK su Android
echo ========================================
echo.

REM Verifica ADB
echo [1/2] Verifica ADB...
adb version >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] ADB non trovato!
    echo Scarica Platform Tools da:
    echo https://developer.android.com/studio/releases/platform-tools
    echo.
    echo Dopo aver scaricato, estrai e aggiungi al PATH
    pause
    exit /b 1
)
echo [OK] ADB trovato

REM Verifica dispositivo
echo.
echo [2/2] Verifica dispositivo connesso...
adb devices
echo.
echo Assicurati che:
echo 1. Il telefono sia connesso via USB
echo 2. Il debug USB sia attivato
echo 3. La connessione sia autorizzata
echo.

if not exist "dist\*.apk" (
    echo [ERRORE] Nessun APK trovato in dist\
    echo Esegui prima build_android.bat
    pause
    exit /b 1
)

echo Installazione APK...
for %%f in ("dist\*.apk") do (
    adb install "%%f"
    if errorlevel 1 (
        echo [ERRORE] Installazione fallita!
        echo Prova a disinstallare la versione precedente:
        echo adb uninstall org.botzxy
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   APK installato con successo!
echo ========================================
echo Avvia l'app "BotZXY" dal telefono
pause