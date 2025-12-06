#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查加密密钥长度
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.config import SecurityConfig

print(f'ENCRYPTION_KEY: {SecurityConfig.ENCRYPTION_KEY}')
print(f'字符长度: {len(SecurityConfig.ENCRYPTION_KEY)}')
print(f'字节长度: {len(SecurityConfig.ENCRYPTION_KEY.encode("utf-8"))}')
