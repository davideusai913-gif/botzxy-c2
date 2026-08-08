#!/bin/bash
# BotZXY Builder - Installazione rapida

echo "========================================"
echo "   BotZXY - Installazione Builder"
echo "========================================"

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRORE] Python3 non trovato!"
    echo "Installa Python3 dal sito ufficiale"
    exit 1
fi

# Installa pip
python3 -m ensurepip --upgrade

# Installa dipendenze
echo "[1/4] Installazione pacchetti Python..."
python3 -m pip install requests pyinstaller pillow opencv-python pyautogui keyboard numpy

# Installa buildozer per Android
echo "[2/4] Installazione buildozer..."
python3 -m pip install buildozer

# Crea struttura cartelle
echo "[3/4] Creazione struttura..."
mkdir -p payloads dist

# Download payloads se non esistono
echo "[4/4] Download payloads..."

echo ""
echo "========================================"
echo "   ✅ Installazione completata!"
echo "========================================"
echo ""
echo "Avvia il builder con:"
echo "  python3 botzxy_builder.py"
echo ""
echo "Per Termux:"
echo "  bash install_builder.sh"
echo ""