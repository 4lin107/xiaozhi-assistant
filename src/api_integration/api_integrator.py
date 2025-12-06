#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API集成模块 - 用于与第三方服务交互和执行本地操作
"""

import os
import sys
import logging
import random
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

from config.config import APIConfig, SecurityConfig
from src.api_integration.web_crawler import WebCrawler
from src.api_integration.local_operations import LocalOperations
from src.security.security_manager import get_security_manager

logger = logging.getLogger(__name__)

class APIIntegrator:
    """API集成器类，负责与第三方服务交互和执行本地操作"""
    
    def __init__(self):
        """初始化API集成器"""
        # 初始化安全管理器
        self.security_manager = get_security_manager()
        
        # 从配置获取API密钥并解密（如果需要）
        self.weather_api_key = self._get_decrypted_api_key(APIConfig.WEATHER_API_KEY)
        self.news_api_key = self._get_decrypted_api_key(APIConfig.NEWS_API_KEY)
        self.translation_api_key = self._get_decrypted_api_key(APIConfig.TRANSLATION_API_KEY)
        self.map_api_key = self._get_decrypted_api_key(APIConfig.MAP_API_KEY)
        
        # API基础URL（保留以便将来使用真实API）
        self.weather_base_url = APIConfig.WEATHER_BASE_URL
        self.news_base_url = APIConfig.NEWS_BASE_URL
        self.map_api_url = APIConfig.MAP_API_URL
        
        # 请求超时时间
        self.request_timeout = APIConfig.REQUEST_TIMEOUT
        
        # 初始化网络爬虫和本地操作器
        self.crawler = WebCrawler()
        self.local_ops = LocalOperations()
    
    def get_weather(self, city, time=None):
        """获取指定城市的天气信息"""
        try:
            logger.info(f"获取天气信息 - 城市: {city}, 时间: {time}")
            
            # 使用网络爬虫获取天气信息
            return self.crawler.get_weather(city, time)
            
        except Exception as e:
            logger.error(f"处理天气信息失败: {e}")
            if time:
                return f"抱歉，获取{city}{time}的天气信息失败"
            else:
                return f"抱歉，获取{city}的天气信息失败"
    
    def get_news(self, category="top", count=5):
        """获取新闻信息"""
        try:
            logger.info(f"获取新闻信息 - 分类: {category}, 数量: {count}")
            
            # 使用网络爬虫获取新闻信息
            return self.crawler.get_news()
            
        except Exception as e:
            logger.error(f"处理新闻信息失败: {e}")
            return "抱歉，获取新闻信息失败"
    
    def get_translation(self, text, from_lang="zh", to_lang="en"):
        """获取翻译结果"""
        try:
            logger.info(f"获取翻译结果 - 文本: {text}, 源语言: {from_lang}, 目标语言: {to_lang}")
            
            # 使用网络爬虫获取翻译结果
            return self.crawler.search_internet(f"{text} 的{to_lang}翻译")
            
        except Exception as e:
            logger.error(f"处理翻译结果失败: {e}")
            return f"抱歉，无法翻译 '{text}'"
    
    def play_music(self, song_name):
        """播放音乐"""
        try:
            logger.info(f"播放音乐 - 歌曲名称: {song_name}")
            
            # 使用网络爬虫搜索音乐
            return self.crawler.search_internet(f"{song_name} 在线播放")
            
        except Exception as e:
            logger.error(f"播放音乐失败: {e}")
            return "抱歉，播放音乐失败"
    
    def get_stock_info(self, stock_code):
        """获取股票信息"""
        try:
            logger.info(f"获取股票信息 - 股票代码: {stock_code}")
            
            # 使用网络爬虫获取股票信息
            return self.crawler.search_internet(f"{stock_code} 股票行情")
            
        except Exception as e:
            logger.error(f"获取股票信息失败: {e}")
            return "抱歉，获取股票信息失败"
    
    def _get_decrypted_api_key(self, api_key):
        """获取解密后的API密钥"""
        if not api_key or api_key.startswith("your_"):
            return api_key
        
        try:
            # 检查密钥是否已加密
            if api_key.startswith(self.security_manager.ENCRYPTION_PREFIX):
                return self.security_manager.decrypt(api_key)
            return api_key
        except Exception as e:
            logger.error(f"解密API密钥失败: {e}")
            return api_key
    
    def calculate(self, expression):
        """计算数学表达式"""
        try:
            logger.info(f"计算数学表达式 - 表达式: {expression}")
            
            # 简单的数学计算（实际项目中可以使用更复杂的表达式解析库）
            # 只允许基本的四则运算，确保安全
            allowed_chars = "0123456789+-*/(). "
            if all(c in allowed_chars for c in expression):
                result = eval(expression)
                return f"计算结果：{result}"
            else:
                return "抱歉，表达式包含不允许的字符"
                
        except Exception as e:
            logger.error(f"计算失败: {e}")
            return "抱歉，计算失败"
    
    def get_current_time(self):
        """获取当前时间"""
        try:
            return self.crawler.get_current_time()
        except Exception as e:
            logger.error(f"获取当前时间失败: {e}")
            return "抱歉，获取当前时间失败"
    
    def get_current_date(self):
        """获取当前日期"""
        try:
            return self.crawler.get_current_date()
        except Exception as e:
            logger.error(f"获取当前日期失败: {e}")
            return "抱歉，获取当前日期失败"
    
    def open_folder(self, path):
        """打开指定文件夹"""
        try:
            logger.info(f"打开文件夹 - 路径: {path}")
            
            # 检查用户权限
            if not self.security_manager.has_permission("open_folder"):
                current_permission = self.security_manager.get_user_permission()
                return f"抱歉，您当前的权限级别({current_permission})不足以执行该命令"
                
            return self.local_ops.open_folder(path)
        except Exception as e:
            logger.error(f"打开文件夹失败: {e}")
            return f"抱歉，打开文件夹时出错"
    
    def open_application(self, app_name):
        """打开指定应用程序"""
        try:
            logger.info(f"打开应用程序 - 名称: {app_name}")
            
            # 检查用户权限
            if not self.security_manager.has_permission("open_application"):
                current_permission = self.security_manager.get_user_permission()
                return f"抱歉，您当前的权限级别({current_permission})不足以执行该命令"
                
            return self.local_ops.open_application(app_name)
        except Exception as e:
            logger.error(f"打开应用程序失败: {e}")
            return f"抱歉，打开应用程序时出错"
    
    def run_command(self, command):
        """运行指定命令"""
        try:
            logger.info(f"运行命令 - 命令: {command}")
            
            # 检查用户权限
            from src.security.security_manager import get_security_manager
            security_manager = get_security_manager()
            
            # 检查是否有权限执行命令
            if not security_manager.has_permission("run_command"):
                current_permission = security_manager.get_user_permission()
                return f"抱歉，您当前的权限级别({current_permission})不足以执行该命令"
            
            # 增强命令执行的安全性检查
            if SecurityConfig.REQUIRE_CONFIRMATION_FOR_SENSITIVE_OPS:
                # 检查是否为敏感命令
                sensitive_commands = ["rm", "del", "format", "shutdown", "restart", "reboot"]
                cmd_lower = command.lower()
                if any(sensitive_cmd in cmd_lower for sensitive_cmd in sensitive_commands):
                    return f"抱歉，该命令 '{command}' 被标记为敏感操作，需要额外确认"
            
            return self.local_ops.run_command(command)
        except Exception as e:
            logger.error(f"运行命令失败: {e}")
            return f"抱歉，运行命令时出错"
    
    def search_map(self, location):
        """搜索地图位置"""
        try:
            logger.info(f"搜索地图位置 - 位置: {location}")
            return self.crawler.search_map(location)
        except Exception as e:
            logger.error(f"搜索地图位置失败: {e}")
            return f"抱歉，搜索地图位置时出错"
    
    def search_internet(self, query, fuzzy=True, top_k=3):
        """搜索互联网
        Args:
            query: 搜索关键词
            fuzzy: 是否启用模糊搜索，默认为True
            top_k: 返回的搜索结果数量，默认为3
        """
        try:
            logger.info(f"搜索互联网 - 查询: {query}, 模糊搜索: {fuzzy}, 结果数量: {top_k}")
            return self.crawler.search_internet(query, fuzzy=fuzzy, top_k=top_k)
        except Exception as e:
            logger.error(f"搜索互联网失败: {e}")
            return f"抱歉，搜索互联网时出错"
    
    def list_files(self, directory):
        """列出目录中的文件"""
        try:
            logger.info(f"列出目录文件 - 目录: {directory}")
            
            # 检查用户权限
            if not self.security_manager.has_permission("list_files"):
                current_permission = self.security_manager.get_user_permission()
                return f"抱歉，您当前的权限级别({current_permission})不足以执行该命令"
                
            # 增强目录访问的安全性检查
            if SecurityConfig.REQUIRE_CONFIRMATION_FOR_SENSITIVE_OPS:
                # 检查是否为敏感目录
                sensitive_dirs = ["c:\\", "c:/", "system32", "windows", "win32"]
                dir_lower = directory.lower()
                if any(sensitive_dir in dir_lower for sensitive_dir in sensitive_dirs):
                    return f"抱歉，访问目录 '{directory}' 需要额外确认"
            
            return self.local_ops.list_files(directory)
        except Exception as e:
            logger.error(f"列出目录文件失败: {e}")
            return f"抱歉，列出目录文件时出错"
    
    def _get_mock_weather(self, city):
        """获取模拟天气数据（保留以便将来使用）"""
        weathers = ["晴", "多云", "阴", "小雨", "中雨", "大雨", "雷阵雨"]
        temperatures = [15, 18, 20, 22, 25, 28, 30]
        
        weather = random.choice(weathers)
        temperature = random.choice(temperatures)
        
        return f"{city}今天的天气是{weather}，温度{temperature}℃"
    
    def _get_mock_news(self, category="top", count=5):
        """获取模拟新闻数据（保留以便将来使用）"""
        news_list = [
            "今日全国多地气温回升，春暖花开",
            "科技巨头发布最新人工智能产品，引起行业关注",
            "体育赛事：中国队在国际比赛中取得优异成绩",
            "健康提示：春季是过敏高发期，请注意防护",
            "财经新闻：股市今日小幅上涨，市场信心增强"
        ]
        
        return "\n".join([f"{i+1}. {news}" for i, news in enumerate(news_list[:count])])
    
    def _format_weather_response(self, weather_data):
        """格式化天气API响应（保留以便将来使用真实API）"""
        pass
    
    def _format_news_response(self, news_data):
        """格式化新闻API响应（保留以便将来使用真实API）"""
        pass
