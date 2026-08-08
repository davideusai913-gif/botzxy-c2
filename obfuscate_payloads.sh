#!/bin/bash
# BotZXY - Offusca tutti i payload

echo "========================================"
echo "   BotZXY - Obfuscate Payloads"
echo "========================================"

# Offusca Windows
python obfuscator.py payloads/windows_client.py payloads/windows_client_obf.py

# Offusca Android
python obfuscator.py payloads/android_client.py payloads/android_client_obf.py

# Offusca iOS
python obfuscator.py payloads/ios_client.py payloads/ios_client_obf.py

echo ""
echo "========================================"
echo "   Offuscamento completato!"
echo "   File generati:"
echo "   - payloads/windows_client_obf.py"
echo "   - payloads/android_client_obf.py"
echo "   - payloads/ios_client_obf.py"
echo "========================================"