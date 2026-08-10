// BotZXY - Configurazione Globale
const BotZXY = {
    theme: 'dark',
    language: 'it',
    translations: {},
    
    load: function() {
        return fetch('/api/settings')
            .then(res => {
                if (!res.ok) throw new Error('Network error');
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
                this.theme = localStorage.getItem('botzxy_theme') || 'dark';
                this.language = localStorage.getItem('botzxy_language') || 'it';
                this.applyTheme();
                this.loadTranslations(this.language);
            });
    },
    
    loadTranslations: function(lang) {
        fetch('/api/translations?lang=' + lang)
            .then(res => {
                if (!res.ok) throw new Error('Network error');
                return res.json();
            })
            .then(data => {
                this.translations = data;
                this.applyLanguage();
            })
            .catch(() => {
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
                'loading': 'Caricamento...',
                'error': 'Errore',
                'no_data': 'Nessun dato disponibile',
                'refresh': 'Aggiorna',
                'total_devices': 'Dispositivi totali',
                'online_bots': 'Bot online',
                'commands': 'Comandi',
                'system_active': 'Sistema attivo',
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
                'type': 'Tipo',
                'created_at': 'Creato il',
                'details': 'Dettagli',
                'timestamp': 'Data/ora',
                'device': 'Dispositivo',
                'action': 'Azione',
                'no_devices': 'Nessun dispositivo connesso',
                'no_captures': 'Nessuna cattura trovata',
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
                'capture_types': 'Tipi di cattura',
                'top_devices': 'Dispositivi più attivi',
                'activity_7d': 'Attività dispositivi (7 giorni)',
                'platforms': 'Piattaforme',
                'stats': 'Statistiche reali',
                'active_bots': 'Bot attivi (oggi)',
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
                'loading': 'Loading...',
                'error': 'Error',
                'no_data': 'No data available',
                'refresh': 'Refresh',
                'total_devices': 'Total Devices',
                'online_bots': 'Online Bots',
                'commands': 'Commands',
                'system_active': 'System Active',
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
                'type': 'Type',
                'created_at': 'Created At',
                'details': 'Details',
                'timestamp': 'Date/Time',
                'device': 'Device',
                'action': 'Action',
                'no_devices': 'No devices connected',
                'no_captures': 'No captures found',
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
                'capture_types': 'Capture types',
                'top_devices': 'Top devices',
                'activity_7d': 'Device activity (7 days)',
                'platforms': 'Platforms',
                'stats': 'Real statistics',
                'active_bots': 'Active bots (today)',
                'username': 'Username',
                'password': 'Password',
                'login_btn': 'ACCESS DASHBOARD'
            }
        };
        return fallbacks[lang] || fallbacks['it'];
    },
    
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
        
        // Applica al body
        if (document.body) {
            document.body.style.background = t.bg;
            document.body.style.color = t.text;
        }
        
        // Aggiorna elementi esistenti (solo se esistono)
        const selectors = ['.card', '.settings-card', '.stat-card', '.device-card', '.capture-item', '.stat-box', '.chart-card', '.table-card', '.sidebar'];
        selectors.forEach(selector => {
            document.querySelectorAll(selector).forEach(el => {
                if (el) {
                    el.style.background = t.card;
                    el.style.borderColor = t.border;
                }
            });
        });
        
        localStorage.setItem('botzxy_theme', theme);
    },
    
    applyLanguage: function() {
        const t = this.translations;
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key] !== undefined && t[key] !== null) {
                el.textContent = t[key];
            }
        });
        localStorage.setItem('botzxy_language', this.language);
    },
    
    t: function(key) {
        return this.translations[key] || key;
    }
};

// Carica configurazione all'avvio
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(function() {
        BotZXY.load();
    }, 100);
} else {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            BotZXY.load();
        }, 100);
    });
}