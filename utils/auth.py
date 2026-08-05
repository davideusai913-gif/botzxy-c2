# BotZXY - Authentication Utilities

import hashlib
import secrets
import time
from functools import wraps
from flask import request, jsonify, current_app

def generate_token():
    return secrets.token_urlsafe(32)

def hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Verifica API key nel database
        import sqlite3
        conn = sqlite3.connect('database/botzxy_c2.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        user = cursor.execute('SELECT * FROM users WHERE api_key = ?', (api_key,)).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated

def rate_limit(limit=100, window=60):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Semplice rate limiting in memoria
            if not hasattr(current_app, 'rate_limits'):
                current_app.rate_limits = {}
            
            key = request.remote_addr
            now = time.time()
            
            if key not in current_app.rate_limits:
                current_app.rate_limits[key] = []
            
            # Rimuovi vecchi timestamp
            current_app.rate_limits[key] = [t for t in current_app.rate_limits[key] if t > now - window]
            
            if len(current_app.rate_limits[key]) >= limit:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            current_app.rate_limits[key].append(now)
            return f(*args, **kwargs)
        return decorated
    return decorator