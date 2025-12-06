#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全加密模块
用于实现数据加密、解密、哈希计算等安全功能
"""

import os
import logging
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# 修复导入路径问题
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from config.config import SecurityConfig

logger = logging.getLogger(__name__)

class SecurityManager:
    """安全管理类，提供加密、解密、哈希、权限管理等安全功能"""
    
    # 权限级别定义
    PERMISSION_LEVELS = {
        'guest': 0,      # 访客：仅能使用基本功能
        'user': 1,       # 普通用户：可以使用大部分功能
        'admin': 2,      # 管理员：可以使用所有功能
        'super_admin': 3 # 超级管理员：可以修改系统配置
    }
    
    # 命令权限映射
    COMMAND_PERMISSIONS = {
        # 基本命令
        'hello': 'guest',
        'help': 'guest',
        'time': 'guest',
        'weather': 'guest',
        'news': 'guest',
        'joke': 'guest',
        
        # 用户命令
        'open': 'user',
        'play': 'user',
        'search': 'user',
        
        # 管理员命令
        'settings': 'admin',
        'config': 'admin',
        'restart': 'admin',
        
        # 超级管理员命令
        'shutdown': 'super_admin',
        'update': 'super_admin',
        'install': 'super_admin'
    }
    
    def __init__(self):
        """初始化安全管理器"""
        # 从配置获取加密密钥
        self.encryption_key = self._get_encryption_key()
        self.salt = b'your_salt_here'  # 用于密钥派生的盐值
        self.iterations = 100000  # PBKDF2迭代次数
        
        # 权限管理相关
        self.current_user_permission = 'user'  # 默认用户权限
        self.user_roles = {}  # 存储用户角色信息
        self._load_user_roles()
        
    def _get_encryption_key(self):
        """获取或生成加密密钥"""
        try:
            # 优先从环境变量获取密钥
            key = os.environ.get('SECURITY_ENCRYPTION_KEY')
            if key:
                key_bytes = key.encode('utf-8')
            
            # 其次从配置文件获取密钥
            elif hasattr(SecurityConfig, 'ENCRYPTION_KEY') and SecurityConfig.ENCRYPTION_KEY:
                key_bytes = SecurityConfig.ENCRYPTION_KEY.encode('utf-8')
            
            # 如果都没有，生成一个默认密钥（仅用于开发环境）
            else:
                default_key = 'default_encryption_key_123456789012345678901234'
                logger.warning("使用默认加密密钥，建议在生产环境配置安全的密钥")
                key_bytes = default_key.encode('utf-8')
            
            # 使用SHA-256哈希确保密钥始终是32字节
            return hashlib.sha256(key_bytes).digest()
            
        except Exception as e:
            logger.error(f"获取加密密钥失败: {e}")
            # 返回默认密钥的哈希值以确保系统可用性
            return hashlib.sha256('default_encryption_key_123456789012345678901234'.encode('utf-8')).digest()
    
    def encrypt(self, data):
        """加密数据
        
        Args:
            data: 要加密的数据（字符串或字节）
            
        Returns:
            加密后的数据（Base64编码的字符串）
        """
        try:
            # 确保数据是字节类型
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # 生成随机IV
            iv = os.urandom(16)
            
            # 使用PKCS7填充数据
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(data) + padder.finalize()
            
            # 确保密钥长度为32字节（AES-256要求）
            key = self.encryption_key[:32]
            
            # 创建AES-256-CBC密码器
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # 加密数据
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # 组合IV和加密数据，并进行Base64编码
            result = base64.b64encode(iv + encrypted_data).decode('utf-8')
            return result
            
        except Exception as e:
            logger.error(f"数据加密失败: {e}")
            raise
    
    def decrypt(self, encrypted_data):
        """解密数据
        
        Args:
            encrypted_data: 加密后的数据（Base64编码的字符串）
            
        Returns:
            解密后的数据（字符串）
        """
        try:
            # 解码Base64数据
            data = base64.b64decode(encrypted_data)
            
            # 提取IV（前16字节）和加密数据
            iv = data[:16]
            encrypted_content = data[16:]
            
            # 确保密钥长度为32字节（AES-256要求）
            key = self.encryption_key[:32]
            
            # 创建AES-256-CBC密码器
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=default_backend()
            )
            
            # 解密数据
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_content) + decryptor.finalize()
            
            # 移除PKCS7填充
            unpadder = padding.PKCS7(128).unpadder()
            unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
            
            return unpadded_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"数据解密失败: {e}")
            raise
    
    def hash_data(self, data):
        """计算数据的哈希值
        
        Args:
            data: 要哈希的数据（字符串）
            
        Returns:
            哈希值（十六进制字符串）
        """
        try:
            hasher = hashlib.sha256()
            hasher.update(data.encode('utf-8'))
            return hasher.hexdigest()
            
        except Exception as e:
            logger.error(f"哈希计算失败: {e}")
            raise
    
    def generate_key(self, password):
        """从密码生成加密密钥
        
        Args:
            password: 用户密码（字符串）
            
        Returns:
            加密密钥（字节）
        """
        try:
            # 使用PBKDF2从密码派生密钥
            kdf = PBKDF2HMAC(
                algorithm=hashlib.sha256(),
                length=32,  # AES-256需要32字节密钥
                salt=self.salt,
                iterations=self.iterations,
                backend=default_backend()
            )
            return kdf.derive(password.encode('utf-8'))
            
        except Exception as e:
            logger.error(f"密钥生成失败: {e}")
            raise
    
    def verify_password(self, password, hashed_password):
        """验证密码与哈希值是否匹配
        
        Args:
            password: 原始密码
            hashed_password: 哈希后的密码
            
        Returns:
            是否匹配（布尔值）
        """
        try:
            return self.hash_data(password) == hashed_password
            
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    def obfuscate_data(self, data, keep_length=False):
        """对数据进行模糊处理
        
        Args:
            data: 要模糊处理的数据
            keep_length: 是否保持数据长度
            
        Returns:
            模糊处理后的数据
        """
        try:
            if not data:
                return data
            
            if isinstance(data, str):
                if keep_length:
                    # 只保留首字符和尾字符，中间用*替代
                    if len(data) <= 2:
                        return '*' * len(data)
                    return data[0] + '*' * (len(data) - 2) + data[-1]
                else:
                    return '[obfuscated]'
            else:
                return '[obfuscated]'
                
        except Exception as e:
            logger.error(f"数据模糊处理失败: {e}")
            return data
    
    def sanitize_input(self, input_data):
        """清理用户输入，防止注入攻击
        
        Args:
            input_data: 用户输入数据
            
        Returns:
            清理后的数据
        """
        try:
            if not isinstance(input_data, str):
                return input_data
            
            # 移除潜在的危险字符
            dangerous_chars = ['\x00', '\n', '\r', '\t', '\b', '\f', "'"]
            for char in dangerous_chars:
                input_data = input_data.replace(char, '')
            
            return input_data
            
        except Exception as e:
            logger.error(f"输入清理失败: {e}")
            return input_data
    
    def clean_input(self, input_str, max_length=1000):
        """清理输入字符串，防止注入攻击"""
        if not isinstance(input_str, str):
            return input_str
        
        # 去除首尾空白字符
        cleaned = input_str.strip()
        
        # 限制长度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
            logger.warning(f"输入长度超过限制，已截断为{max_length}字符")
        
        return cleaned
    
    def validate_input(self, input_str, allowed_types=None, max_length=None):
        """验证输入的合法性"""
        if allowed_types is not None and not isinstance(input_str, tuple(allowed_types)):
            logger.error(f"输入类型不合法，期望{allowed_types}，实际得到{type(input_str)}")
            return False
        
        if max_length is not None and isinstance(input_str, str) and len(input_str) > max_length:
            logger.error(f"输入长度超过限制{max_length}字符")
            return False
        
        return True
    
    def mask_sensitive_data(self, data, keep_length=False, custom_patterns=None):
        """模糊处理敏感数据
        
        Args:
            data: 需要模糊处理的数据
            keep_length: 是否保持原始数据长度
            custom_patterns: 自定义敏感数据正则表达式
            
        Returns:
            模糊处理后的数据
        """
        try:
            if not data:
                return data
            
            if not isinstance(data, str):
                return data
                
            # 定义敏感数据模式
            sensitive_patterns = {
                # 用户输入和响应
                r"用户输入.*?:.*?": lambda match: f"用户输入: [obfuscated]",
                r"助手响应.*?:.*?": lambda match: f"助手响应: [obfuscated]",
                r"语音输入.*?:.*?": lambda match: f"语音输入: [obfuscated]",
                
                # API密钥和凭证
                r"api[_-]?key.*?:.*?": lambda match: f"api_key: [REDACTED]",
                r"secret.*?:.*?": lambda match: f"secret: [REDACTED]",
                r"key.*?:.*?": lambda match: f"key: [REDACTED]",
                
                # 个人信息
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}": lambda match: "[email]@[domain].com",
                r"1[3-9]\d{9}": lambda match: f"{match.group()[:3]}****{match.group()[-4:]}",
                r"\d{17}[\dXx]": lambda match: "[ID_CARD]",
                
                # 文件路径
                r"[Cc]:\\.*?\\.*?\\": lambda match: f"{match.group()[:2]}\\...\\",
                
                # 命令执行
                r"命令.*?:.*?": lambda match: f"命令: [REDACTED]",
                r"运行命令.*?:.*?": lambda match: f"运行命令: [REDACTED]",
                
                # 其他敏感信息
                r"密码.*?:.*?": lambda match: f"密码: [REDACTED]",
                r"passwd.*?:.*?": lambda match: f"passwd: [REDACTED]",
            }
            
            # 添加自定义模式
            if custom_patterns:
                sensitive_patterns.update(custom_patterns)
            
            import re
            masked_data = data
            for pattern, replacer in sensitive_patterns.items():
                masked_data = re.sub(pattern, replacer, masked_data, flags=re.IGNORECASE)
            
            return masked_data
                
        except Exception as e:
            logger.error(f"数据模糊处理失败: {e}")
            return data
    
    def is_secure_password(self, password):
        """检查密码是否安全
        
        Args:
            password: 要检查的密码
            
        Returns:
            密码是否安全（布尔值）
        """
        if not isinstance(password, str):
            return False
        
        # 密码长度至少8位
        if len(password) < 8:
            return False
        
        # 包含大小写字母
        if not any(c.isupper() for c in password) or not any(c.islower() for c in password):
            return False
        
        # 包含数字
        if not any(c.isdigit() for c in password):
            return False
        
        return True

    def _load_user_roles(self):
        """加载用户角色信息"""
        try:
            # 从配置或数据库加载用户角色信息
            # 这里使用默认配置，实际应用中可以从数据库或配置文件加载
            self.user_roles = {
                'default_user': 'user',
                'admin_user': 'admin',
                'super_admin_user': 'super_admin'
            }
            logger.info("用户角色信息加载完成")
        except Exception as e:
            logger.error(f"加载用户角色信息失败: {e}")
            self.user_roles = {}  # 使用空字典确保系统可用性
    
    def set_user_permission(self, permission):
        """设置当前用户权限
        
        Args:
            permission: 权限级别（'guest', 'user', 'admin', 'super_admin'）
            
        Returns:
            bool: 设置是否成功
        """
        try:
            if permission in self.PERMISSION_LEVELS:
                self.current_user_permission = permission
                logger.info(f"当前用户权限已设置为: {permission}")
                return True
            else:
                logger.warning(f"无效的权限级别: {permission}")
                return False
        except Exception as e:
            logger.error(f"设置用户权限失败: {e}")
            return False
    
    def get_user_permission(self):
        """获取当前用户权限
        
        Returns:
            str: 当前用户权限级别
        """
        return self.current_user_permission
    
    def has_permission(self, command):
        """检查用户是否有权限执行某个命令
        
        Args:
            command: 要执行的命令名称
            
        Returns:
            bool: 是否有权限执行该命令
        """
        try:
            # 检查命令是否需要特定权限
            if command in self.COMMAND_PERMISSIONS:
                required_permission = self.COMMAND_PERMISSIONS[command]
                current_level = self.PERMISSION_LEVELS[self.current_user_permission]
                required_level = self.PERMISSION_LEVELS[required_permission]
                
                result = current_level >= required_level
                if not result:
                    logger.warning(f"权限不足: 当前权限{self.current_user_permission}，命令{command}需要{required_permission}")
                return result
            else:
                # 对于未定义的命令，默认允许执行
                logger.info(f"命令{command}未定义权限，默认允许执行")
                return True
        except Exception as e:
            logger.error(f"检查权限失败: {e}")
            # 出错时默认允许执行，确保系统可用性
            return True
    
    def check_permission_level(self, required_level):
        """检查用户权限级别是否足够
        
        Args:
            required_level: 所需的权限级别
            
        Returns:
            bool: 权限级别是否足够
        """
        try:
            current_level = self.PERMISSION_LEVELS[self.current_user_permission]
            required_level_value = self.PERMISSION_LEVELS[required_level]
            
            result = current_level >= required_level_value
            if not result:
                logger.warning(f"权限级别不足: 当前{self.current_user_permission}，需要{required_level}")
            return result
        except Exception as e:
            logger.error(f"检查权限级别失败: {e}")
            # 出错时默认允许，确保系统可用性
            return True
    
    def add_user_role(self, user_id, role):
        """添加用户角色
        
        Args:
            user_id: 用户ID
            role: 角色名称
            
        Returns:
            bool: 添加是否成功
        """
        try:
            if role in self.PERMISSION_LEVELS:
                self.user_roles[user_id] = role
                logger.info(f"已为用户{user_id}添加角色: {role}")
                return True
            else:
                logger.warning(f"无效的角色名称: {role}")
                return False
        except Exception as e:
            logger.error(f"添加用户角色失败: {e}")
            return False
    
    def get_user_role(self, user_id):
        """获取用户角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            str: 用户角色，若不存在返回默认角色'guest'
        """
        try:
            return self.user_roles.get(user_id, 'guest')
        except Exception as e:
            logger.error(f"获取用户角色失败: {e}")
            return 'guest'
    
    def remove_user_role(self, user_id):
        """移除用户角色
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 移除是否成功
        """
        try:
            if user_id in self.user_roles:
                del self.user_roles[user_id]
                logger.info(f"已移除用户{user_id}的角色")
                return True
            else:
                logger.warning(f"用户{user_id}不存在")
                return False
        except Exception as e:
            logger.error(f"移除用户角色失败: {e}")
            return False
    
    def get_permission_info(self):
        """获取权限信息
        
        Returns:
            dict: 包含当前权限、权限级别和命令权限的信息
        """
        return {
            'current_permission': self.current_user_permission,
            'permission_levels': self.PERMISSION_LEVELS,
            'command_permissions': self.COMMAND_PERMISSIONS,
            'user_roles': self.user_roles
        }

# 全局安全管理器实例
security_manager = None

def get_security_manager():
    """获取全局安全管理器实例
    
    Returns:
        SecurityManager实例
    """
    global security_manager
    if security_manager is None:
        security_manager = SecurityManager()
    return security_manager