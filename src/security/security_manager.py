#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全加密模块（移动端简化版）
使用标准库实现基本安全功能
"""

import os
import logging
import base64
import hashlib
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from config.config import SecurityConfig
except ImportError:
    class SecurityConfig:
        ENCRYPTION_KEY = None

logger = logging.getLogger(__name__)


class SecurityManager:
    PERMISSION_LEVELS = {'guest': 0, 'user': 1, 'admin': 2, 'super_admin': 3}
    COMMAND_PERMISSIONS = {
        'hello': 'guest', 'help': 'guest', 'time': 'guest', 'weather': 'guest',
        'news': 'guest', 'joke': 'guest', 'open': 'user', 'play': 'user',
        'search': 'user', 'settings': 'admin', 'config': 'admin', 'restart': 'admin',
        'shutdown': 'super_admin', 'update': 'super_admin', 'install': 'super_admin'
    }
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.current_user_permission = 'user'
        self.user_roles = {'default_user': 'user', 'admin_user': 'admin'}
    
    def _get_encryption_key(self):
        try:
            key = os.environ.get('SECURITY_ENCRYPTION_KEY')
            if not key and hasattr(SecurityConfig, 'ENCRYPTION_KEY'):
                key = SecurityConfig.ENCRYPTION_KEY
            key = key or 'default_key'
            return hashlib.sha256(key.encode('utf-8')).digest()
        except:
            return hashlib.sha256(b'default_key').digest()
    
    def encrypt(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        encrypted = bytes([data[i] ^ self.encryption_key[i % 32] for i in range(len(data))])
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encrypted_data):
        data = base64.b64decode(encrypted_data)
        decrypted = bytes([data[i] ^ self.encryption_key[i % 32] for i in range(len(data))])
        return decrypted.decode('utf-8')
    
    def hash_data(self, data):
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def sanitize_input(self, input_data):
        if isinstance(input_data, str):
            for c in ['\x00', '\n', '\r', '\t']:
                input_data = input_data.replace(c, '')
        return input_data
    
    def clean_input(self, s, max_len=1000):
        return s.strip()[:max_len] if isinstance(s, str) else s
    
    def has_permission(self, cmd):
        if cmd not in self.COMMAND_PERMISSIONS:
            return True
        return self.PERMISSION_LEVELS[self.current_user_permission] >= self.PERMISSION_LEVELS[self.COMMAND_PERMISSIONS[cmd]]
    
    def set_user_permission(self, p):
        if p in self.PERMISSION_LEVELS:
            self.current_user_permission = p
            return True
        return False
    
    def get_user_permission(self):
        return self.current_user_permission
    
    def get_user_role(self, uid):
        return self.user_roles.get(uid, 'guest')


security_manager = None

def get_security_manager():
    global security_manager
    if not security_manager:
        security_manager = SecurityManager()
    return security_manager
