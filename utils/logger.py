import os
import json
import uuid
import sqlite3
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models

# ============ CONFIGURAZIONE ============
QDRANT_URL = os.environ.get('QDRANT_URL')
QDRANT_API_KEY = os.environ.get('QDRANT_API_KEY')
QDRANT_COLLECTION = os.environ.get('QDRANT_COLLECTION_NAME', 'botzxy_logs')
VECTOR_SIZE = 512  # Dimensione vettore (CLIP)
LOG_FILE = 'database/logs_backup.json'

# ============ INIZIALIZZAZIONE QDRANT ============
qdrant_client = None
if QDRANT_URL and QDRANT_API_KEY:
    try:
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=30
        )
        # Verifica se la collection esiste
        try:
            qdrant_client.get_collection(QDRANT_COLLECTION)
            print(f"[+] Collection '{QDRANT_COLLECTION}' trovata su Qdrant")
        except Exception:
            # Crea la collection se non esiste
            qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=models.VectorParams(
                    size=VECTOR_SIZE,
                    distance=models.Distance.COSINE
                )
            )
            print(f"[+] Collection '{QDRANT_COLLECTION}' creata su Qdrant (size={VECTOR_SIZE})")
    except Exception as e:
        print(f"[-] Qdrant init error: {e}")

# ============ SALVA SINGOLO LOG ============
def save_log_to_qdrant(device_id, action, details):
    """Salva un singolo log su Qdrant"""
    if not qdrant_client:
        return False
    
    try:
        payload = {
            "device_id": device_id or "system",
            "action": action or "unknown",
            "details": details or "",
            "timestamp": datetime.now().isoformat()
        }
        
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=[
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=[0.0] * VECTOR_SIZE,
                    payload=payload
                )
            ]
        )
        return True
    except Exception as e:
        print(f"[-] Qdrant save error: {e}")
        return False

# ============ BACKUP SU QDRANT ============
def backup_logs_to_qdrant():
    """Backup di tutti i log su Qdrant"""
    if not qdrant_client:
        return False
    
    try:
        conn = sqlite3.connect('database/botzxy_c2.db')
        conn.row_factory = sqlite3.Row
        logs = conn.execute('SELECT * FROM logs ORDER BY id DESC LIMIT 1000').fetchall()
        conn.close()
        
        if not logs:
            return True
        
        points = []
        for log in logs:
            points.append(
                models.PointStruct(
                    id=str(uuid.uuid4()),
                    vector=[0.0] * VECTOR_SIZE,
                    payload={
                        "device_id": log['device_id'] or 'system',
                        "action": log['action'] or 'unknown',
                        "details": log['details'] or '',
                        "timestamp": log['timestamp'] or datetime.now().isoformat()
                    }
                )
            )
        
        # Invia in batch (max 100 punti per volta)
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i+batch_size]
            qdrant_client.upsert(
                collection_name=QDRANT_COLLECTION,
                points=batch
            )
            print(f"[+] Qdrant: inviati {len(batch)} log (batch {i//batch_size + 1})")
        
        print(f"[+] Logs salvati su Qdrant: {len(points)} log totali")
        return True
    except Exception as e:
        print(f"[-] Qdrant backup error: {e}")
        return False

# ============ RIPRISTINO DA QDRANT ============
def restore_logs_from_qdrant():
    """Ripristina i log da Qdrant"""
    if not qdrant_client:
        return
    
    try:
        points = qdrant_client.scroll(
            collection_name=QDRANT_COLLECTION,
            limit=5000,
            with_payload=True
        )[0]
        
        if not points:
            print("[+] Nessun log da ripristinare da Qdrant")
            return
        
        conn = sqlite3.connect('database/botzxy_c2.db')
        cursor = conn.cursor()
        
        # Crea tabella se non esiste
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        count = 0
        for point in points:
            try:
                payload = point.payload
                cursor.execute('''
                    INSERT OR IGNORE INTO logs (device_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    payload.get('device_id', 'system'),
                    payload.get('action', 'unknown'),
                    payload.get('details', ''),
                    payload.get('timestamp', datetime.now().isoformat())
                ))
                count += 1
            except:
                pass
        
        conn.commit()
        conn.close()
        print(f"[+] Logs restored from Qdrant: {count} entries")
    except Exception as e:
        print(f"[-] Qdrant restore error: {e}")

# ============ BACKUP SU FILE JSON ============
def backup_logs_to_file():
    """Salva i log in un file JSON di backup"""
    try:
        if not os.path.exists('database'):
            os.makedirs('database', exist_ok=True)
        
        conn = sqlite3.connect('database/botzxy_c2.db')
        conn.row_factory = sqlite3.Row
        logs = conn.execute('SELECT * FROM logs ORDER BY id DESC LIMIT 5000').fetchall()
        conn.close()
        
        if not logs:
            return True
        
        with open(LOG_FILE, 'w') as f:
            json.dump([dict(l) for l in logs], f, default=str)
        print(f"[+] Logs backup su file: {len(logs)} log salvati")
        return True
    except Exception as e:
        print(f"[-] Backup file error: {e}")
        return False

def restore_logs_from_file():
    """Ripristina i log dal file di backup"""
    if not os.path.exists(LOG_FILE):
        return
    
    try:
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
        
        if not logs:
            return
        
        conn = sqlite3.connect('database/botzxy_c2.db')
        cursor = conn.cursor()
        
        # Crea tabella se non esiste
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        count = 0
        for log in logs:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO logs (device_id, action, details, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (
                    log.get('device_id', 'system'),
                    log.get('action', 'unknown'),
                    log.get('details', ''),
                    log.get('timestamp', datetime.now().isoformat())
                ))
                count += 1
            except:
                pass
        
        conn.commit()
        conn.close()
        print(f"[+] Logs restored from file: {count} entries")
    except Exception as e:
        print(f"[-] Restore file error: {e}")

# ============ FUNZIONI PRINCIPALI ============
def backup_logs():
    """Backup completo: Qdrant + file"""
    success = True
    
    # Backup su Qdrant
    if qdrant_client:
        if not backup_logs_to_qdrant():
            success = False
    
    # Backup su file JSON
    if not backup_logs_to_file():
        success = False
    
    return success

def restore_logs():
    """Ripristino completo: Qdrant + file"""
    # Prima prova da Qdrant
    if qdrant_client:
        restore_logs_from_qdrant()
    
    # Poi da file
    restore_logs_from_file()

# ============ TEST ============
if __name__ == "__main__":
    print("=" * 50)
    print("  BotZXY - Logger Test")
    print("=" * 50)
    
    # Test salvataggio
    print("\n[TEST] Salvataggio log...")
    save_log_to_qdrant("test_device", "test_action", "Questo è un log di test")
    backup_logs()
    
    # Test ripristino
    print("\n[TEST] Ripristino log...")
    restore_logs()
    
    print("\n[TEST] Completato!")