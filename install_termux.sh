#!/bin/bash
# BotZXY - Installazione per Termux (Android)

echo "========================================"
echo "   BotZXY - Installazione Termux"
echo "========================================"

# Aggiorna Termux
pkg update -y && pkg upgrade -y

# Installa Python e dipendenze
pkg install -y python python-pip git termux-api

# Installa pacchetti Python
pip install requests pillow opencv-python numpy

# Crea struttura
mkdir -p ~/botzxy_builder
cd ~/botzxy_builder

# Scarica il builder
echo "Download botzxy_builder.py..."
curl -sSL https://raw.githubusercontent.com/davideusai913-gif/botzxy-c2/main/botzxy_builder.py -o botzxy_builder.py

echo ""
echo "========================================"
echo "   ✅ Installazione Termux completata!"
echo "========================================"
echo ""
echo "Avvia il builder con:"
echo "  cd ~/botzxy_builder && python botzxy_builder.py"
echo ""