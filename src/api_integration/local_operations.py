#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地操作执行模块
用于执行本地文件系统和应用程序操作
"""

import os
import subprocess
import logging
import platform

logger = logging.getLogger(__name__)

class LocalOperations:
    """本地操作执行类"""
    
    def __init__(self):
        """初始化本地操作执行器"""
        self.system = platform.system()
    
    def open_folder(self, path):
        """打开指定文件夹
        Args:
            path: 文件夹路径
        Returns:
            操作结果字符串
        """
        try:
            # 处理特殊路径
            if path.lower() == '桌面' or path.lower() == '我的桌面':
                path = os.path.join(os.path.expanduser('~'), 'Desktop')
            elif path.lower() == '文档' or path.lower() == '我的文档':
                path = os.path.join(os.path.expanduser('~'), 'Documents')
            elif path.lower() == '下载' or path.lower() == '我的下载':
                path = os.path.join(os.path.expanduser('~'), 'Downloads')
            elif path.lower() == '音乐' or path.lower() == '我的音乐':
                path = os.path.join(os.path.expanduser('~'), 'Music')
            elif path.lower() == '图片' or path.lower() == '我的图片':
                path = os.path.join(os.path.expanduser('~'), 'Pictures')
            elif path.lower() == '视频' or path.lower() == '我的视频':
                path = os.path.join(os.path.expanduser('~'), 'Videos')
            
            # 检查路径是否存在
            if not os.path.exists(path):
                return f"抱歉，文件夹路径不存在：{path}"
            
            # 检查是否是文件夹
            if not os.path.isdir(path):
                return f"抱歉，{path} 不是一个文件夹"
            
            # 根据操作系统打开文件夹
            if self.system == 'Windows':
                os.startfile(path)
            elif self.system == 'Darwin':  # macOS
                subprocess.run(['open', path], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', path], check=True)
            
            return f"已成功打开文件夹：{path}"
        except Exception as e:
            logger.error(f"打开文件夹失败: {e}")
            return f"抱歉，打开文件夹时出错：{e}"
    
    def open_application(self, app_name):
        """打开指定应用程序
        Args:
            app_name: 应用程序名称
        Returns:
            操作结果字符串
        """
        try:
            # 应用程序路径映射
            app_paths = {
                '记事本': 'notepad.exe',
                '计算器': 'calc.exe',
                '画图': 'mspaint.exe',
                '浏览器': 'start "" https://www.baidu.com',
                'chrome': 'chrome.exe',
                'edge': 'msedge.exe',
                'firefox': 'firefox.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe',
                'powerpoint': 'powerpnt.exe',
                'vscode': 'code.exe',
                'pycharm': 'pycharm64.exe',
                '酷狗': 'start "" "KuGou"',
                '酷狗音乐': 'start "" "KuGou"',
                '支付宝': 'start "" https://www.alipay.com',
                '淘宝': 'start "" https://www.taobao.com',
                '京东': 'start "" https://www.jd.com',
                '抖音': 'start "" https://www.douyin.com',
                '快手': 'start "" https://www.kuaishou.com',
                '小红书': 'start "" https://www.xiaohongshu.com',
                '微博': 'start "" https://www.weibo.com',
                'B站': 'start "" https://www.bilibili.com',
                '哔哩哔哩': 'start "" https://www.bilibili.com',
                '腾讯视频': 'start "" https://v.qq.com',
                '爱奇艺': 'start "" https://www.iqiyi.com',
                '优酷': 'start "" https://www.youku.com',
                '网易云音乐': 'start "" https://music.163.com',
                'QQ音乐': 'start "" https://y.qq.com',
                '高德地图': 'start "" https://ditu.amap.com',
                '百度地图': 'start "" https://map.baidu.com',
                '滴滴出行': 'start "" https://www.didiglobal.com',
                '美团': 'start "" https://www.meituan.com',
                '饿了么': 'start "" https://www.ele.me',
                '相机': 'mspaint.exe',
                '相册': 'explorer.exe shell:My Pictures',
                '日历': 'explorer.exe shell:LocalAppData\Microsoft\Windows\Calendar',
                '闹钟': 'explorer.exe shell:LocalAppData\Microsoft\Windows\Alarms',
                '联系人': 'explorer.exe shell:LocalAppData\Microsoft\Windows\People',
                '短信': 'explorer.exe shell:LocalAppData\Microsoft\Windows\Messaging',
                '电话': 'start "" https://www.baidu.com/s?wd=网络电话',
                '设置': 'start ms-settings:',
                '蓝牙': 'start ms-settings:bluetooth',
                'WiFi': 'start ms-settings:network-wifi',
                '手电筒': 'start ms-settings:easeofaccess-keyboard',
                '备忘录': 'start "" https://www.onenote.com'
            }
            
            # 转换为小写进行匹配
            app_name_lower = app_name.lower()
            
            # 查找应用程序
            for key, value in app_paths.items():
                if key.lower() in app_name_lower:
                    app_path = value
                    break
            else:
                return f"抱歉，找不到应用程序：{app_name}"
            
            # 根据操作系统打开应用程序
            if self.system == 'Windows':
                if app_path.startswith('start'):
                    subprocess.run(app_path, shell=True, check=True)
                else:
                    subprocess.run(app_path, check=True)
            elif self.system == 'Darwin':  # macOS
                subprocess.run(['open', '-a', app_name], check=True)
            else:  # Linux
                subprocess.run([app_name], check=True)
            
            return f"已成功打开应用程序：{app_name}"
        except Exception as e:
            logger.error(f"打开应用程序失败: {e}")
            return f"抱歉，打开应用程序时出错：{e}"
    
    def run_command(self, command):
        """运行指定命令
        Args:
            command: 命令字符串
        Returns:
            操作结果字符串
        """
        try:
            # 简单的命令白名单
            allowed_commands = [
                'dir', 'ls', 'echo', 'date', 'time',
                'whoami', 'ipconfig', 'ping localhost'
            ]
            
            # 检查命令是否在白名单中
            command_lower = command.lower().strip()
            for allowed in allowed_commands:
                if command_lower.startswith(allowed):
                    break
            else:
                return "抱歉，该命令不允许执行"
            
            # 执行命令
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            output = result.stdout.strip()
            error = result.stderr.strip()
            
            if output:
                return f"命令执行结果：\n{output[:500]}..."  # 限制输出长度
            elif error:
                return f"命令执行错误：\n{error}"
            else:
                return "命令执行成功，但没有输出"
        except subprocess.TimeoutExpired:
            return "命令执行超时"
        except Exception as e:
            logger.error(f"执行命令失败: {e}")
            return f"抱歉，执行命令时出错：{e}"
    
    def create_file(self, file_path, content=""):
        """创建文件
        Args:
            file_path: 文件路径
            content: 文件内容
        Returns:
            操作结果字符串
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            # 创建文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"已成功创建文件：{file_path}"
        except Exception as e:
            logger.error(f"创建文件失败: {e}")
            return f"抱歉，创建文件时出错：{e}"
    
    def delete_file(self, file_path):
        """删除文件
        Args:
            file_path: 文件路径
        Returns:
            操作结果字符串
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return f"抱歉，文件不存在：{file_path}"
            
            # 检查是否是文件
            if not os.path.isfile(file_path):
                return f"抱歉，{file_path} 不是一个文件"
            
            # 删除文件
            os.remove(file_path)
            
            return f"已成功删除文件：{file_path}"
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return f"抱歉，删除文件时出错：{e}"
    
    def list_files(self, directory):
        """列出目录中的文件
        Args:
            directory: 目录路径
        Returns:
            操作结果字符串
        """
        try:
            # 处理特殊目录
            if directory.lower() == '当前目录' or directory.lower() == '这里':
                directory = '.'
            elif directory.lower() == '桌面' or directory.lower() == '我的桌面':
                directory = os.path.join(os.path.expanduser('~'), 'Desktop')
            elif directory.lower() == '文档' or directory.lower() == '我的文档':
                directory = os.path.join(os.path.expanduser('~'), 'Documents')
            
            # 检查目录是否存在
            if not os.path.exists(directory):
                return f"抱歉，目录不存在：{directory}"
            
            # 检查是否是目录
            if not os.path.isdir(directory):
                return f"抱歉，{directory} 不是一个目录"
            
            # 列出文件
            files = os.listdir(directory)
            if not files:
                return f"目录 {directory} 为空"
            
            # 格式化输出
            result = f"目录 {directory} 中的文件：\n"
            for file in sorted(files):
                file_path = os.path.join(directory, file)
                if os.path.isdir(file_path):
                    result += f"📁 {file}\n"
                else:
                    result += f"📄 {file}\n"
            
            return result
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return f"抱歉，列出文件时出错：{e}"
