#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小智语音助手 - Android 入口文件
Buildozer 需要在根目录有 main.py 作为入口点
"""

import os
import sys

# 确保 src 目录在 Python 路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 导入并运行移动端应用
from mobile_app import VoiceAssistantApp

if __name__ == '__main__':
    VoiceAssistantApp().run()
