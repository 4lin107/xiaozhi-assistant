#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全加密模块（移动端简化版）
使用标准库实现基本安全功能，避免依赖 cryptography
"""

import os
import logging
import base64
import hashlib
import hmac

# 修复导入路径问题
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

try:
    from config.config import SecurityConfig
except ImportError:
    class SecurityConfig:
        ENCRYPTION_KEY = None

logger = logging.getLogger(__name__)

class SecurityManager:
    """安全管理类，提供加密、解密、哈希、权限管理等安全功能"""
    
    PERMISSION_LEVELS = {
        'guest': 0,
        'user': 1,
        'admin': 2,
        'super_admin': 3
    }
    
    COMMAND_PERMISSIONS = {
        'hello': 'guest', 'help': 'guest', 'time': 'guest',
        'weather': 'guest', 'news': 'guest', 'joke': 'guest',
        'open': 'user', 'play': 'user', 'search': 'user',
        'settings': 'admin', 'config': 'admin', 'restart': 'admin',
        'shutdown': 'super_admin', 'update': 'super_admin', 'install': 'super_admin'
    }
    
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
        self.current_user_permission = 'user'
        self.user_roles = {}
        self._load_user_roles()

    def _get_encryption_key(self):
        """获取或生成加密密钥"""
        try:
            key = os.environ.get('SECURITY_ENCRYPTION_KEY')
            if key:
                key_bytes = key.encode('utf-8')
            elif hasattr(SecurityConfig, 'ENCRYPTION_KEY') and SecurityConfig.ENCRYPTION_KEY:
                key_bytes = SecurityConfig.ENCRYPTION_KEY.encode('utf-8')
            else:
                key_bytes = 'default_encryption_key_123456789012345678901234'.encode('utf-8')
            return hashlib.sha256(key_bytes).digest()
        except Exception as e:
            logger.error(f"获取加密密钥失败: {e}")
            return hashlib.sha256(b'default_key').digest()
    
    def encrypt(self, data):
        """简化加密（XOR + Base64）"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            key = self.encryption_key
            encrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"加密失败: {e}")
            raise
    
    def decrypt(self, encrypted_data):
        """简化解密"""
        try:
            data = base64.b64decode(encrypted_data)
            key = self.encryption_key
            decrypted = bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"解密失败: {e}")
            raise
    
    def hash_data(self, data):
        """计算SHA-256哈希"""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def generate_key(self, password):
        """从密码生成密钥"""
        return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt', 100000)
    
    def verify_password(self, password, hashed_password):
        """验证密码"""
        return self.hash_data(password) == hashed_password
    
    def sanitize_input(self, input_data):
        """清理用户输入"""
        if not isinstance(input_data, str):
            return input_data
        for char in ['\x00', '\n', '\r', '\t', '\b', '\f', "'"]:
            input_data = input_data.replace(char, '')
        return input_data
    
    def clean_input(self, input_str, max_length=1000):
        """清理输入字符串"""
        if not isinstance(input_str, str):
            return input_str
        cleaned = input_str.strip()
        return cleaned[:max_length] if len(cleaned) > max_length else cleaned
    
    def validate_input(self, input_str, allowed_types=None, max_length=None):
        """验证输入"""
        if allowed_types and not isinstance(input_str, tuple(allowed_types)):
            return False
        if max_length and isinstance(input_str, str) and len(input_str) > max_length:
            return False
        return True

    def obfuscate_data(self, data, keep_length=False):
        """模糊处理数据"""
        if not data or not isinstance(data, str):
            return '[obfuscated]' if data else data
        if keep_length:
            if len(data) <= 2:
                return '*' * len(data)
            return data[0] + '*' * (len(data) - 2) + data[-1]
        return '[obfuscated]'
    
    def mask_sensitive_data(self, data, keep_length=False, custom_patterns=None):
        """模糊处理敏感数据"""
        if not data or not isinstance(data, str):
            return data
        return self.obfuscate_data(data, keep_length)
    
    def is_secure_password(self, password):
        """检查密码安全性"""
        if not isinstance(password, str) or len(password) < 8:
            return False
        return (any(c.isupper() for c in password) and 
                any(c.islower() for c in password) and 
                any(c.isdigit() for c in password))
    
    def _load_user_roles(self):
        """加载用户角色"""
        self.user_roles = {'default_user': 'user', 'admin_user': 'admin'}
    
    def set_user_permission(self, permission):
        """设置用户权限"""
        if permission in self.PERMISSION_LEVELS:
            self.current_user_permission = permission
            return True
        return False
    
    def get_user_permission(self):
        """获取当前权限"""
        return self.current_user_permission
    
    def has_permission(self, command):
        """检查命令权限"""
        if command not in self.COMMAND_PERMISSIONS:
            return True
        required = self.COMMAND_PERMISSIONS[command]
        return self.PERMISSION_LEVELS[self.current_user_permission] >= self.PERMISSION_LEVELS[required]
    
    def check_permission_level(self, required_level):
        """检查权限级别"""
        if required_level not in self.PERMISSION_LEVELS:
            return True
        return self.PERMISSION_LEVELS[self.current_user_permission] >= self.PERMISSION_LEVELS[required_level]
    
    def add_user_role(self, user_id, role):
        """添加用户角色"""
        if role in self.PERMISSION_LEVELS:
            self.user_roles[user_id] = role
            return True
        return False
    
    def get_user_role(self, user_id):
        """获取用户角色"""
        return self.user_roles.get(user_id, 'guest')
    
    def remove_user_role(self, user_id):
        """移除用户角色"""
        if user_id in self.user_roles:
            del self.user_roles[user_id]
            return True
        return False
    
    def get_permission_info(self):
        """获取权限信息"""
        return {
            'current_permission': self.current_user_permission,
            'permission_levels': self.PERMISSION_LEVELS,
            'command_permissions': self.COMMAND_PERMISSIONS,
            'user_roles': self.user_roles
        }

# 全局实例
security_manager = None

def get_security_manager():
    """获取全局安全管理器"""
    global security_manager
    if security_manager is None:
        security_manager = SecurityManager()
    return security_manager
