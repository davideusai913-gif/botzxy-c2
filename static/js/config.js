// BotZXY - Configurazione Globale
const BotZXY = {
    theme: 'dark',
    language: 'it',
    translations: {},
    
    // Carica le impostazioni dal server
    load: function() {
        return fetch('/api/settings')
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok');
                return res.json();
            })
            .then(data => {
                this.theme = data.theme || 'dark';
                this.language = data.language || 'it';
                this.applyTheme();
                this.loadTranslations(this.language);
                return data;
            })
            .catch(() => {
                // Fallback: usa localStorage
                this.theme = localStorage.getItem('botzxy_theme') || 'dark';
                this.language = localStorage.getItem('botzxy_language') || 'it';
                this.applyTheme();
                this.loadTranslations(this.language);
            });
    },
    
    // Carica le traduzioni dal server
    loadTranslations: function(lang) {
        fetch('/api/translations?lang=' + lang)
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok');
                return res.json();
            })
            .then(data => {
                this.translations = data;
                this.applyLanguage();
            })
            .catch(() => {
                // Fallback: traduzioni di base
                this.translations = this.getFallbackTranslations(lang);
                this.applyLanguage();
            });
    },
    
    getFallbackTranslations: function(lang) {
        const fallbacks = {
            'it': {
                'dashboard': 'Dashboard',
                'devices': 'Dispositivi',
                'captures': 'Catture',
                'analytics': 'Analytics',
                'logs': 'Log',
                'settings': 'Impostazioni',
                'logout': 'Esci',
                'total_devices': 'Dispositivi totali',
                'online_bots': 'Bot online',
                'captures_count': 'Catture',
                'commands': 'Comandi',
                'system_active': 'Sistema attivo',
                'refresh': 'Aggiorna',
                'export': 'Esporta',
                'delete': 'Elimina',
                'save': 'Salva',
                'cancel': 'Annulla',
                'search': 'Cerca...',
                'no_data': 'Nessun dato disponibile',
                'loading': 'Caricamento...',
                'error': 'Errore',
                'success': 'Successo',
                'online': 'Online',
                'offline': 'Offline',
                'actions': 'Azioni',
                'platform': 'Piattaforma',
                'hostname': 'Nome host',
                'ip': 'Indirizzo IP',
                'status': 'Stato',
                'last_seen': 'Ultimo visto',
                'phone': 'Telefono',
                'id': 'ID',
                'device_id': 'ID dispositivo',
                'type': 'Tipo',
                'created_at': 'Creato il',
                'details': 'Dettagli',
                'timestamp': 'Data/ora',
                'device': 'Dispositivo',
                'action': 'Azione',
                'no_captures': 'Nessuna cattura trovata',
                'no_devices': 'Nessun dispositivo connesso',
                'no_logs': 'Nessun log disponibile',
                'theme': 'Tema',
                'language': 'Lingua',
                'notifications': 'Notifiche',
                'security': 'Sicurezza',
                'change_password': 'Cambia password',
                'logout_all': 'Disconnetti tutti i dispositivi',
                'save_settings': 'Salva impostazioni',
                'settings_saved': 'Impostazioni salvate!',
                'settings_error': 'Errore salvataggio',
                'password_changed': 'Password cambiata con successo!',
                'password_error': 'Password attuale errata',
                'password_mismatch': 'Le password non coincidono',
                'all_platforms': 'Tutte le piattaforme',
                'all_status': 'Tutti gli stati',
                'all_types': 'Tutti i tipi',
                'screenshot': 'Screenshot',
                'webcam': 'Webcam',
                'mic': 'Microfono',
                'keylog': 'Keylog',
                'passwords': 'Password',
                'clipboard': 'Clipboard',
                'wifi': 'WiFi',
                'location': 'Location',
                'screenshots_webcam': 'Screenshot, Webcam, Keylog, Password',
                'event_history': 'Cronologia eventi',
                'clear_all': 'Cancella tutto',
                'clear_confirm': 'Cancellare TUTTI i log? Questa operazione è irreversibile.',
                'logs_cleared': 'Log cancellati',
                'events': 'eventi',
                'date_time': 'Data/Ora',
                'event_log': 'Registro eventi',
                'advanced_settings': 'Personalizzazione avanzata',
                'reload': 'Ricarica',
                'dark': 'Scuro',
                'light': 'Chiaro',
                'blue': 'Blu',
                'green': 'Verde',
                'purple': 'Viola',
                'orange': 'Arancione',
                'cyber': 'Cyber',
                'matrix': 'Matrix',
                'theme_desc': 'Scegli il tema per l\'interfaccia',
                'language_desc': 'Lingua dell\'interfaccia',
                'notifications_desc': 'Seleziona le notifiche da ricevere',
                'security_desc': 'Gestisci la sicurezza del tuo account',
                'lang_it': 'Italiano',
                'lang_en': 'English',
                'lang_fr': 'Français',
                'lang_es': 'Español',
                'lang_de': 'Deutsch',
                'notif_new_device': 'Nuovi dispositivi',
                'notif_command': 'Comandi eseguiti',
                'notif_capture': 'Nuove catture',
                'notif_system': 'Eventi di sistema',
                'logout_all_confirm': 'Disconnettere TUTTI i dispositivi connessi?',
                'logout_all_done': 'Tutti i dispositivi disconnessi',
                'stats': 'Statistiche reali',
                'activity_7d': 'Attività dispositivi (7 giorni)',
                'platforms': 'Piattaforme',
                'capture_types': 'Tipi di cattura',
                'top_devices': 'Dispositivi più attivi',
                'active_bots': 'Bot attivi (oggi)',
                'connected_devices': 'Dispositivi connessi',
                'device_management': 'Gestione dispositivi',
                'send_command': 'Invia comando',
                'extract_data': 'Estrai dati',
                'remove': 'Rimuovi',
                'details': 'Dettagli',
                'delete_confirm': 'Eliminare?',
                'deleted': 'Eliminato',
                'live': 'LIVE',
                'activity_24h': 'Attività dispositivi (24h)',
                'botzxy_c2': 'BotZXY C2',
                'username': 'Username',
                'password': 'Password',
                'login_btn': 'ACCEDI AL DASHBOARD'
            },
            'en': {
                'dashboard': 'Dashboard',
                'devices': 'Devices',
                'captures': 'Captures',
                'analytics': 'Analytics',
                'logs': 'Logs',
                'settings': 'Settings',
                'logout': 'Logout',
                'total_devices': 'Total Devices',
                'online_bots': 'Online Bots',
                'captures_count': 'Captures',
                'commands': 'Commands',
                'system_active': 'System Active',
                'refresh': 'Refresh',
                'export': 'Export',
                'delete': 'Delete',
                'save': 'Save',
                'cancel': 'Cancel',
                'search': 'Search...',
                'no_data': 'No data available',
                'loading': 'Loading...',
                'error': 'Error',
                'success': 'Success',
                'online': 'Online',
                'offline': 'Offline',
                'actions': 'Actions',
                'platform': 'Platform',
                'hostname': 'Hostname',
                'ip': 'IP Address',
                'status': 'Status',
                'last_seen': 'Last Seen',
                'phone': 'Phone',
                'id': 'ID',
                'device_id': 'Device ID',
                'type': 'Type',
                'created_at': 'Created At',
                'details': 'Details',
                'timestamp': 'Date/Time',
                'device': 'Device',
                'action': 'Action',
                'no_captures': 'No captures found',
                'no_devices': 'No devices connected',
                'no_logs': 'No logs available',
                'theme': 'Theme',
                'language': 'Language',
                'notifications': 'Notifications',
                'security': 'Security',
                'change_password': 'Change Password',
                'logout_all': 'Logout all devices',
                'save_settings': 'Save Settings',
                'settings_saved': 'Settings saved!',
                'settings_error': 'Error saving',
                'password_changed': 'Password changed successfully!',
                'password_error': 'Current password is incorrect',
                'password_mismatch': 'Passwords do not match',
                'all_platforms': 'All platforms',
                'all_status': 'All statuses',
                'all_types': 'All types',
                'screenshot': 'Screenshot',
                'webcam': 'Webcam',
                'mic': 'Microphone',
                'keylog': 'Keylog',
                'passwords': 'Passwords',
                'clipboard': 'Clipboard',
                'wifi': 'WiFi',
                'location': 'Location',
                'screenshots_webcam': 'Screenshot, Webcam, Keylog, Password',
                'event_history': 'Event history',
                'clear_all': 'Clear all',
                'clear_confirm': 'Delete ALL logs? This operation is irreversible.',
                'logs_cleared': 'Logs cleared',
                'events': 'events',
                'date_time': 'Date/Time',
                'event_log': 'Event log',
                'advanced_settings': 'Advanced settings',
                'reload': 'Reload',
                'dark': 'Dark',
                'light': 'Light',
                'blue': 'Blue',
                'green': 'Green',
                'purple': 'Purple',
                'orange': 'Orange',
                'cyber': 'Cyber',
                'matrix': 'Matrix',
                'theme_desc': 'Choose the interface theme',
                'language_desc': 'Interface language',
                'notifications_desc': 'Select notifications to receive',
                'security_desc': 'Manage your account security',
                'lang_it': 'Italian',
                'lang_en': 'English',
                'lang_fr': 'French',
                'lang_es': 'Spanish',
                'lang_de': 'German',
                'notif_new_device': 'New devices',
                'notif_command': 'Commands executed',
                'notif_capture': 'New captures',
                'notif_system': 'System events',
                'logout_all_confirm': 'Disconnect ALL connected devices?',
                'logout_all_done': 'All devices disconnected',
                'stats': 'Real statistics',
                'activity_7d': 'Device activity (7 days)',
                'platforms': 'Platforms',
                'capture_types': 'Capture types',
                'top_devices': 'Most active devices',
                'active_bots': 'Active bots (today)',
                'connected_devices': 'Connected devices',
                'device_management': 'Device management',
                'send_command': 'Send command',
                'extract_data': 'Extract data',
                'remove': 'Remove',
                'details': 'Details',
                'delete_confirm': 'Delete?',
                'deleted': 'Deleted',
                'live': 'LIVE',
                'activity_24h': 'Device activity (24h)',
                'botzxy_c2': 'BotZXY C2',
                'username': 'Username',
                'password': 'Password',
                'login_btn': 'ACCESS DASHBOARD'
            }
        };
        return fallbacks[lang] || fallbacks['it'];
    },
    
    // Applica il tema a tutta la pagina
    applyTheme: function() {
        const theme = this.theme;
        const themes = {
            'dark': { bg: '#0b0b1a', text: '#e2e8f0', card: 'rgba(18,18,40,0.45)', border: 'rgba(255,255,255,0.04)' },
            'light': { bg: '#f1f5f9', text: '#0a0a1a', card: 'rgba(255,255,255,0.85)', border: 'rgba(0,0,0,0.08)' },
            'blue': { bg: '#0a1a3a', text: '#e2e8f0', card: 'rgba(10,26,58,0.7)', border: 'rgba(59,130,246,0.15)' },
            'green': { bg: '#0a1a0a', text: '#e2e8f0', card: 'rgba(10,26,10,0.7)', border: 'rgba(52,211,153,0.15)' },
            'purple': { bg: '#1a0a2a', text: '#e2e8f0', card: 'rgba(26,10,42,0.7)', border: 'rgba(139,92,246,0.15)' },
            'orange': { bg: '#2a1a0a', text: '#e2e8f0', card: 'rgba(42,26,10,0.7)', border: 'rgba(245,158,11,0.15)' },
            'cyber': { bg: '#0a0a0a', text: '#00ff88', card: 'rgba(0,0,0,0.7)', border: 'rgba(0,255,136,0.15)' },
            'matrix': { bg: '#0a0a0a', text: '#00ff00', card: 'rgba(0,0,0,0.7)', border: 'rgba(0,255,0,0.15)' }
        };
        
        const t = themes[theme] || themes['dark'];
        
        // Applica variabili CSS
        document.documentElement.style.setProperty('--bg-primary', t.bg);
        document.documentElement.style.setProperty('--text-primary', t.text);
        document.documentElement.style.setProperty('--bg-card', t.card);
        document.documentElement.style.setProperty('--border-color', t.border);
        
        // Applica direttamente al body
        document.body.style.background = t.bg;
        document.body.style.color = t.text;
        
        // Aggiorna tutti i card
        document.querySelectorAll('.card, .settings-card, .stat-card, .device-card, .capture-item, .stat-box, .chart-card, .table-card, .sidebar')
            .forEach(el => {
                if (el) {
                    el.style.background = t.card;
                    el.style.borderColor = t.border;
                }
            });
        
        // Salva in localStorage
        localStorage.setItem('botzxy_theme', theme);
    },
    
    // Applica la lingua a tutti gli elementi con data-i18n
    applyLanguage: function() {
        const t = this.translations;
        
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key] !== undefined && t[key] !== null) {
                el.textContent = t[key];
            }
        });
        
        // Salva in localStorage
        localStorage.setItem('botzxy_language', this.language);
    },
    
    // Traduce una singola chiave
    t: function(key) {
        return this.translations[key] || key;
    }
};

// Carica configurazione all'avvio
document.addEventListener('DOMContentLoaded', function() {
    BotZXY.load();
});

// Forza il caricamento immediato se la pagina è già pronta
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    BotZXY.load();
}