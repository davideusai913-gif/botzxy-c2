// BotZXY - Configurazione condivisa
const BotZXYConfig = {
    theme: 'dark',
    language: 'it',
    
    // Carica le impostazioni dal server
    load: function() {
        return fetch('/api/settings')
            .then(res => res.json())
            .then(data => {
                this.theme = data.theme || 'dark';
                this.language = data.language || 'it';
                this.applyTheme();
                this.applyLanguage();
                return data;
            })
            .catch(() => {
                console.log('[BotZXY] Usando impostazioni di default');
                this.applyTheme();
                this.applyLanguage();
            });
    },
    
    // Applica il tema a tutta la pagina
    applyTheme: function() {
        const theme = this.theme;
        const body = document.body;
        
        // Rimuovi tutte le classi tema
        body.classList.remove('theme-dark', 'theme-light', 'theme-blue', 'theme-green', 'theme-purple', 'theme-orange', 'theme-cyber', 'theme-matrix');
        body.classList.add('theme-' + theme);
        
        // Applica stili CSS personalizzati
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
        body.style.background = t.bg;
        body.style.color = t.text;
        
        // Aggiorna tutti i card
        document.querySelectorAll('.card, .settings-card, .stat-card, .device-card, .capture-item, .stat-box, .chart-card, .table-card')
            .forEach(el => {
                el.style.background = t.card;
                el.style.borderColor = t.border;
            });
        
        // Aggiorna sidebar
        document.querySelectorAll('.sidebar')
            .forEach(el => {
                el.style.background = t.card;
                el.style.borderColor = t.border;
            });
        
        // Salva in localStorage
        localStorage.setItem('botzxy_theme', theme);
    },
    
    // Applica la lingua
    applyLanguage: function() {
        const lang = this.language;
        const translations = {
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
                'success': 'Successo'
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
            },
            'fr': {
                'dashboard': 'Tableau de bord',
                'devices': 'Appareils',
                'captures': 'Captures',
                'analytics': 'Analytique',
                'logs': 'Journaux',
                'settings': 'Paramètres',
                'logout': 'Déconnexion',
                'total_devices': 'Appareils total',
                'online_bots': 'Bots en ligne',
                'commands': 'Commandes',
                'system_active': 'Système actif',
                'refresh': 'Rafraîchir',
                'export': 'Exporter',
                'delete': 'Supprimer',
                'save': 'Enregistrer',
                'cancel': 'Annuler',
                'search': 'Rechercher...',
                'no_data': 'Aucune donnée disponible',
                'loading': 'Chargement...',
                'error': 'Erreur',
                'success': 'Succès'
            },
            'es': {
                'dashboard': 'Panel de control',
                'devices': 'Dispositivos',
                'captures': 'Capturas',
                'analytics': 'Analítica',
                'logs': 'Registros',
                'settings': 'Configuración',
                'logout': 'Cerrar sesión',
                'total_devices': 'Dispositivos totales',
                'online_bots': 'Bots en línea',
                'commands': 'Comandos',
                'system_active': 'Sistema activo',
                'refresh': 'Actualizar',
                'export': 'Exportar',
                'delete': 'Eliminar',
                'save': 'Guardar',
                'cancel': 'Cancelar',
                'search': 'Buscar...',
                'no_data': 'No hay datos disponibles',
                'loading': 'Cargando...',
                'error': 'Error',
                'success': 'Éxito'
            },
            'de': {
                'dashboard': 'Dashboard',
                'devices': 'Geräte',
                'captures': 'Aufnahmen',
                'analytics': 'Analyse',
                'logs': 'Protokolle',
                'settings': 'Einstellungen',
                'logout': 'Abmelden',
                'total_devices': 'Geräte insgesamt',
                'online_bots': 'Online-Bots',
                'commands': 'Befehle',
                'system_active': 'System aktiv',
                'refresh': 'Aktualisieren',
                'export': 'Exportieren',
                'delete': 'Löschen',
                'save': 'Speichern',
                'cancel': 'Abbrechen',
                'search': 'Suchen...',
                'no_data': 'Keine Daten verfügbar',
                'loading': 'Laden...',
                'error': 'Fehler',
                'success': 'Erfolg'
            }
        };
        
        const t = translations[lang] || translations['it'];
        
        // Applica traduzioni agli elementi con data-i18n
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (t[key]) {
                el.textContent = t[key];
            }
        });
        
        // Salva in localStorage
        localStorage.setItem('botzxy_language', lang);
    }
};

// Carica configurazione all'avvio
document.addEventListener('DOMContentLoaded', function() {
    BotZXYConfig.load();
});