# BotZXY - Cryptographic Utilities

import hashlib
import hmac
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class BotZXYCrypto:
    def __init__(self, secret_key=None):
        if secret_key is None:
            secret_key = os.environ.get('BOTZXY_SECRET', 'change_this_in_production')
        self.secret_key = secret_key.encode()
        self._fernet = None
        self._init_fernet()
    
    def _init_fernet(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'botzxy_salt_2026',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key))
        self._fernet = Fernet(key)
    
    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self._fernet.encrypt(data).decode()
    
    def decrypt(self, data):
        if isinstance(data, str):
            data = data.encode()
        return self._fernet.decrypt(data).decode()
    
    def hash_password(self, password):
        salt = b'botzxy_salt_2026'
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000).hex()
    
    def generate_api_key(self):
        return hashlib.sha256(os.urandom(32)).hexdigest()
    
    def verify_hmac(self, data, signature):
        expected = hmac.new(self.secret_key, data.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    
    def sign(self, data):
        return hmac.new(self.secret_key, data.encode(), hashlib.sha256).hexdigest()

# Singleton
crypto = BotZXYCrypto()