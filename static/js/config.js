// BotZXY - Configurazione Globale
const BotZXY = {
    theme: 'dark',
    language: 'it',
    translations: {},
    
    // Carica le impostazioni dal server
    load: function() {
        return fetch('/api/settings')
            .then(res => res.json())
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
            .then(res => res.json())
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
                'captures': 'Catture',
                'analytics': 'Analytics',
                'logs': 'Log',
                'settings': 'Impostazioni'
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
                'success': 'Success'
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
                el.style.background = t.card;
                el.style.borderColor = t.border;
            });
        
        // Salva in localStorage
        localStorage.setItem('botzxy_theme', theme);
    },
    
    // Applica la lingua a tutti gli elementi con data-i18n
    applyLanguage: function() {
        const t = this.translations;
        
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key]) {
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