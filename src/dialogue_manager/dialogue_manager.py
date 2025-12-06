#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对话管理系统模块
"""

import os
import sys
import logging
import sqlite3
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

from config.config import DialogueManagerConfig, SecurityConfig
from src.security.security_manager import get_security_manager

class DialogueManager:
    """对话管理器类"""
    
    def __init__(self):
        """初始化对话管理器"""
        # 对话历史保存路径
        self.history_path = DialogueManagerConfig.HISTORY_PATH
        
        # 最大对话历史长度
        self.max_history_length = DialogueManagerConfig.MAX_HISTORY_LENGTH
        
        # 默认回复
        self.default_responses = DialogueManagerConfig.DEFAULT_RESPONSES
        
        # 初始化安全管理器
        self.security_manager = get_security_manager()
        
        # 初始化对话历史数据库
        self._initialize_database()
        
        # 当前对话上下文 - 增强版，支持多轮对话和上下文理解
        self.current_context = {
            "user_id": "default",  # 未来可支持多用户
            "session_id": self._generate_session_id(),
            "last_intent": None,
            "last_entities": None,
            "last_response": None,
            "topic": None,
            "conversation_turns": 0,
            "pending_questions": [],
            "memory": {
                "preferred_city": None,
                "preferred_language": "zh-CN",
                "favorite_topics": [],
                "recent_queries": [],
                "user_name": None
            },
            "conversation_topic": None,
            "topic_turns": 0,
            "start_time": datetime.now()
        }
        
        # 上下文相关意图映射（扩展）
        self.contextual_intents = {
            "weather": ["温度", "天气", "下雨", "晴天", "多云", "预报", "温度", "风力", "湿度", "气候", "天气怎么样", "冷", "热"],
            "time": ["几点", "时间", "现在", "几时", "何时", "几点了"],
            "date": ["日期", "几号", "今天", "明天", "后天", "星期几", "几号了"],
            "search_internet": ["搜索", "查找", "查询", "了解", "更多", "详细", "信息", "资料"],
            "calculator": ["计算", "加", "减", "乘", "除", "等于", "结果", "多少"],
            "joke": ["笑话", "搞笑", "幽默", "哈哈", "开心"],
            "music": ["音乐", "歌曲", "播放", "听歌", "唱歌", "旋律"],
            "open_application": ["打开", "启动", "运行", "开启"],
            "open_folder": ["打开", "查看", "浏览", "文件夹"]
        }
        
        # 初始化NLP处理器
        from src.nlp.nlp_processor import NLPProcessor
        self.nlp_processor = NLPProcessor()
        
        # 定义意图处理函数映射
        self.intent_handlers = {
            "greeting": self.handle_greeting,
            "weather": self.handle_weather,
            "news": self.handle_news,
            "calculator": self.handle_calculator,
            "time": self.handle_time,
            "date": self.handle_date,
            "music": self.handle_music,
            "translation": self.handle_translation,
            "exit": self.handle_exit,
            "open_folder": self.handle_open_folder,
            "open_application": self.handle_open_application,
            "search_map": self.handle_search_map,
            "search_internet": self.handle_search_internet,
            "list_files": self.handle_list_files,
            "name": self.handle_name,
            "joke": self.handle_joke,
            "unknown": self.handle_unknown
        }
    
    def _initialize_database(self):
        """初始化对话历史数据库"""
        try:
            # 创建数据库目录（如果不存在）
            os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
            
            # 连接数据库
            conn = sqlite3.connect(self.history_path)
            cursor = conn.cursor()
            
            # 创建对话历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS dialogue_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_input TEXT,
                    intent TEXT,
                    entities TEXT,
                    response TEXT,
                    is_encrypted INTEGER DEFAULT 0
                )
            ''')
            
            # 确保is_encrypted列存在（如果表已经存在但没有这个列）
            try:
                cursor.execute("ALTER TABLE dialogue_history ADD COLUMN is_encrypted INTEGER DEFAULT 0")
                conn.commit()
            except sqlite3.OperationalError:
                # 如果列已经存在，忽略此错误
                pass
            
            conn.commit()
            conn.close()
            logger.info("对话历史数据库初始化成功")
            
        except Exception as e:
            logger.error(f"对话历史数据库初始化失败: {e}")
    
    def _generate_session_id(self):
        """生成会话ID"""
        import uuid
        return str(uuid.uuid4())
    
    def _update_context(self, user_input, intent, entities, response):
        """更新对话上下文"""
        # 更新基本上下文信息
        self.current_context["last_intent"] = intent
        self.current_context["last_entities"] = entities
        self.current_context["last_response"] = response
        self.current_context["conversation_turns"] += 1
        
        # 更新用户记忆
        self._update_user_memory(intent, entities, user_input)
        
        # 更新对话主题
        self._update_conversation_topic(intent)
        
        logger.info(f"更新后的对话上下文: {self.current_context}")
    
    def _update_user_memory(self, intent, entities, user_input):
        """更新用户记忆"""
        memory = self.current_context["memory"]
        
        # 更新用户偏好城市
        if intent == "weather":
            for entity_type, entity in entities:
                if entity_type == "city":
                    memory["preferred_city"] = entity
                    break
        
        # 记录最近查询
        if intent and intent != "unknown":
            if intent not in memory["recent_queries"]:
                memory["recent_queries"].append(intent)
            # 保持最近查询不超过5个
            if len(memory["recent_queries"]) > 5:
                memory["recent_queries"].pop(0)
        
        # 更新用户喜欢的话题
        if intent and intent not in memory["favorite_topics"]:
            # 如果同一意图出现多次，视为喜欢的话题
            from collections import Counter
            query_counts = Counter(memory["recent_queries"])
            if query_counts.get(intent, 0) >= 2:
                memory["favorite_topics"].append(intent)
        
        # 从实体中提取更多用户信息
        for entity_type, entity in entities:
            if entity_type == "person" and not memory["user_name"]:
                # 如果用户提到了自己的名字，记住它
                memory["user_name"] = entity
            elif entity_type == "language":
                memory["preferred_language"] = entity
    
    def _update_conversation_topic(self, intent):
        """更新对话主题"""
        if intent and intent != "unknown":
            if self.current_context["conversation_topic"] == intent:
                self.current_context["topic_turns"] += 1
            else:
                self.current_context["conversation_topic"] = intent
                self.current_context["topic_turns"] = 1
        else:
            # 如果当前意图未知，保持原有主题
            if self.current_context["topic_turns"] > 0:
                self.current_context["topic_turns"] += 1
    
    def _handle_contextual_conversation(self, user_input, intent, entities):
        """处理上下文相关的对话（增强版）"""
        # 如果当前没有明确意图，但有上下文，尝试基于上下文推断
        if (intent is None or intent == "unknown") and self.current_context["last_intent"]:
            # 检查用户输入是否与上一个意图相关
            last_intent = self.current_context["last_intent"]
            
            # 1. 基于上下文关键词的意图推断
            for ctx_intent, keywords in self.contextual_intents.items():
                if last_intent == ctx_intent:
                    for keyword in keywords:
                        if keyword in user_input:
                            intent = last_intent
                            break
            
            # 2. 基于对话主题的意图推断
            if (intent is None or intent == "unknown") and self.current_context["conversation_topic"]:
                topic = self.current_context["conversation_topic"]
                if topic in self.contextual_intents:
                    for keyword in self.contextual_intents[topic]:
                        if keyword in user_input:
                            intent = topic
                            break
            
            # 3. 基于疑问词的意图推断
            if intent is None or intent == "unknown":
                question_words = ["呢", "？", "怎么", "为什么", "哪里", "什么", "如何", "多少"]
                if any(word in user_input for word in question_words):
                    # 如果用户用疑问词追问，延续上一个意图
                    intent = last_intent
        
        # 扩展：处理天气查询的上下文信息
        if intent == "weather" or ((intent is None or intent == "unknown") and self.current_context["last_intent"] == "weather"):
            # 检查是否有城市实体
            has_city = any(entity_type == "city" for entity_type, entity in entities)
            
            # 如果没有城市实体，尝试从上下文获取
            if not has_city:
                # 1. 优先使用用户偏好城市
                if self.current_context["memory"]["preferred_city"]:
                    entities.append(("city", self.current_context["memory"]["preferred_city"]))
                # 2. 其次使用上次查询的城市
                elif self.current_context["last_intent"] == "weather" and self.current_context["last_entities"]:
                    for entity_type, entity in self.current_context["last_entities"]:
                        if entity_type == "city":
                            entities.append((entity_type, entity))
                            break
            
            # 如果用户只提供了时间信息或疑问词，仍然使用天气意图
            if intent is None or intent == "unknown":
                time_keywords = ["今天", "明天", "后天", "大后天", "周一", "周二", "周三", "周四", "周五", "周六", "周日", "早上", "下午", "晚上", "上午", "夜间", "凌晨"]
                if any(keyword in user_input for keyword in time_keywords) or "呢" in user_input:
                    intent = "weather"
        
        # 扩展：处理时间和日期查询的上下文信息
        if (intent == "time" or intent == "date") or ((intent is None or intent == "unknown") and 
                                                     (self.current_context["last_intent"] in ["time", "date"])):
            # 如果用户只是追问时间/日期相关信息，保持相同意图
            if intent is None or intent == "unknown":
                time_date_keywords = ["几点", "时间", "日期", "几号", "今天", "明天", "现在", "几时", "何时", "星期几"]
                if any(keyword in user_input for keyword in time_date_keywords) or "呢" in user_input:
                    intent = self.current_context["last_intent"]
        
        # 扩展：处理搜索查询的上下文信息
        if intent == "search_internet" or ((intent is None or intent == "unknown") and 
                                           self.current_context["last_intent"] == "search_internet"):
            # 如果用户追问更多信息，延续搜索意图
            if intent is None or intent == "unknown":
                search_keywords = ["更多", "详细", "信息", "资料", "了解", "然后呢"]
                if any(keyword in user_input for keyword in search_keywords) or "呢" in user_input:
                    intent = "search_internet"
                    # 如果有上次的搜索查询，作为当前查询的上下文
                    if self.current_context["last_entities"]:
                        for entity_type, entity in self.current_context["last_entities"]:
                            if entity_type == "query":
                                # 检查当前是否已有查询实体
                                has_query = any(e_type == "query" for e_type, e in entities)
                                if not has_query:
                                    entities.append(("query", entity))
                                break
        
        return intent, entities
    
    def process_user_input(self, user_input):
        """处理用户输入并返回NLP结果"""
        nlp_result = self.nlp_processor.process_text(user_input)
        return nlp_result["intent"], nlp_result["entities"]

    def generate_response(self, user_input, api_integrator, intent=None, entities=None):
        """根据用户输入生成响应"""
        try:
            logger.info(f"用户输入: {user_input}")
            
            # 如果没有提供intent和entities，则使用NLP处理器处理用户输入
            if intent is None or entities is None:
                # 使用NLP处理器处理用户输入
                intent, entities = self.process_user_input(user_input)
            
            # 处理上下文相关的对话
            intent, entities = self._handle_contextual_conversation(user_input, intent, entities)
            
            logger.info(f"生成响应 - 意图: {intent}, 实体: {entities}, 会话ID: {self.current_context['session_id']}")
            
            # 获取意图处理函数
            handler = self.intent_handlers.get(intent, self.handle_unknown)
            
            # 调用处理函数生成响应
            response = handler(user_input, intent, entities, api_integrator)
            
            # 更新对话上下文
            self._update_context(user_input, intent, entities, response)
            
            # 保存对话历史
            self._save_dialogue_history(user_input, intent, str(entities), response)
            
            logger.info(f"生成的响应: {response}")
            return response
            
        except Exception as e:
            logger.error(f"生成响应失败: {e}")
            return self._get_default_response()
    
    def handle_greeting(self, user_input, intent, entities, api_integrator):
        """处理问候意图"""
        greetings = ["你好！我是你的语音助手，有什么可以帮助你的吗？", 
                     "您好！很高兴为您服务。", 
                     "你好！需要我做什么吗？"]
        
        # 根据时间调整问候语
        now = datetime.now()
        hour = now.hour
        
        if hour < 12:
            greetings = ["早上好！有什么可以帮助你的吗？", 
                         "早安！很高兴为您服务。"]
        elif hour < 18:
            greetings = ["下午好！有什么可以帮助你的吗？", 
                         "午安！很高兴为您服务。"]
        else:
            greetings = ["晚上好！有什么可以帮助你的吗？", 
                         "晚安！很高兴为您服务。"]
        
        import random
        return random.choice(greetings)
    
    def handle_weather(self, user_input, intent, entities, api_integrator):
        """处理天气查询意图"""
        # 提取城市实体
        city = None
        for entity_type, entity in entities:
            if entity_type == "city":
                city = entity
                break
        
        # 直接检查用户输入中是否包含南宁
        # 解决Windows环境下实体提取可能失败的问题
        if not city and "南宁" in user_input:
            city = "南宁"
        
        # 如果没有提取到城市，尝试从上下文中获取
        if not city:
            # 1. 优先使用用户偏好城市
            if "preferred_city" in self.current_context["memory"]:
                city = self.current_context["memory"]["preferred_city"]
            # 2. 其次使用上次查询的城市
            elif self.current_context["last_intent"] == "weather" and self.current_context["last_entities"]:
                for entity_type, entity in self.current_context["last_entities"]:
                    if entity_type == "city":
                        city = entity
                        break
            # 3. 最后使用默认城市
            if not city:
                city = "北京"
        
        # 提取时间实体
        time = None
        for entity_type, entity in entities:
            if entity_type == "time":
                time = entity
                break
        
        try:
            # 调用API获取天气信息
            weather_info = api_integrator.get_weather(city, time)
            
            return weather_info
        except Exception as e:
            logger.error(f"获取天气信息失败: {e}")
            return f"抱歉，获取{city}的天气信息失败，请稍后重试"
    
    def handle_news(self, user_input, intent, entities, api_integrator):
        """处理新闻查询意图"""
        try:
            # 调用新闻API获取新闻信息
            news_info = api_integrator.get_news()
            return news_info
        except Exception as e:
            logger.error(f"获取新闻信息失败: {e}")
            return "抱歉，获取新闻信息失败，请稍后重试"
    
    def handle_calculator(self, user_input, intent, entities, api_integrator):
        """处理计算意图"""
        try:
            # 简单的数学表达式计算
            # 注意：这里使用eval存在安全风险，生产环境应使用更安全的方法
            import re
            
            # 提取数学表达式
            expression = re.search(r'[\d\+\-\*\/\(\)\.]+', user_input)
            if expression:
                expression = expression.group()
                # 安全检查：只允许数字和基本运算符
                if re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', expression):
                    result = eval(expression)
                    return f"计算结果是: {result}"
                else:
                    return "抱歉，我只能处理简单的数学计算"
            else:
                return "抱歉，我没有找到需要计算的数学表达式"
        except ZeroDivisionError:
            return "抱歉，除数不能为零"
        except Exception as e:
            logger.error(f"计算失败: {e}")
            return "抱歉，计算失败，请检查您的输入"
    
    def handle_time(self, user_input, intent, entities, api_integrator):
        """处理时间查询意图"""
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        return f"现在的时间是 {current_time}"
    
    def handle_date(self, user_input, intent, entities, api_integrator):
        """处理日期查询意图"""
        now = datetime.now()
        current_date = now.strftime("%Y年%m月%d日")
        
        # 获取星期几
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        weekday = weekdays[now.weekday()]
        
        return f"今天是 {current_date}，{weekday}"
    
    def handle_music(self, user_input, intent, entities, api_integrator):
        """处理音乐播放意图"""
        import re
        
        # 提取音乐名称
        music_name = None
        
        # 1. 从实体中提取
        for entity_type, entity in entities:
            if entity_type == "music_name":
                music_name = entity
                break
        
        # 2. 从用户输入中提取
        if not music_name:
            patterns = [
                r"播放\s*(.+?)(?:的歌|的音乐)?(?:吧|呗|啊)?$",
                r"听\s*(.+?)(?:的歌|的音乐)?(?:吧|呗|啊)?$",
                r"放\s*(.+?)(?:的歌|的音乐)?(?:吧|呗|啊)?$",
                r"来首\s*(.+?)(?:的歌|的音乐)?(?:吧|呗|啊)?$",
                r"我想听\s*(.+?)(?:的歌|的音乐)?(?:吧|呗|啊)?$",
                r"想听\s*(.+?)(?:的歌|的音乐)?$",
                r"播放的音乐是\s*(.+)$",
                r"想播放的音乐是\s*(.+)$"
            ]
            for pattern in patterns:
                match = re.search(pattern, user_input)
                if match:
                    music_name = match.group(1).strip()
                    # 去除语气词
                    music_name = re.sub(r'[吧呗啊哦了]+$', '', music_name).strip()
                    if music_name and music_name not in ["音乐", "歌", "歌曲"]:
                        break
                    else:
                        music_name = None
        
        # 3. 检查上下文中是否有音乐名
        if not music_name and self.current_context["last_intent"] == "music":
            # 用户可能在追问，直接使用当前输入作为音乐名
            clean_input = re.sub(r'^(播放|听|放|来首|我想听|想听)\s*', '', user_input)
            clean_input = re.sub(r'[吧呗啊哦了]+$', '', clean_input).strip()
            if clean_input and clean_input not in ["音乐", "歌", "歌曲", "什么"]:
                music_name = clean_input
        
        # 如果没有提取到音乐名称，返回提示
        if not music_name:
            return "请告诉我您想要播放的音乐名称，例如：播放周杰伦的歌、听稻香"
        
        logger.info(f"准备播放音乐: {music_name}")
        
        try:
            # 调用音乐播放API
            result = api_integrator.play_music(music_name)
            return result
        except Exception as e:
            logger.error(f"播放音乐失败: {e}")
            return f"抱歉，播放音乐时出错: {str(e)}"
    
    def handle_translation(self, user_input, intent, entities, api_integrator):
        """处理翻译意图"""
        return "抱歉，翻译功能正在开发中"
    
    def handle_name(self, user_input, intent, entities, api_integrator):
        """处理询问名字意图"""
        return "我是您的语音助手，很高兴为您服务！"
    
    def handle_joke(self, user_input, intent, entities, api_integrator):
        """处理讲笑话意图"""
        jokes = [
            "为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 == Dec 25！",
            "有一天，代码对程序员说：我有个 bug。程序员说：别担心，我来修复你。代码说：不，我是想说，我有个 bug，我很喜欢它。",
            "为什么计算机喜欢冬天？因为它们有 Windows！"
        ]
        import random
        return random.choice(jokes)
    
    def handle_exit(self, user_input, intent, entities, api_integrator):
        """处理退出意图"""
        return "感谢使用，再见！"
    
    def handle_open_folder(self, user_input, intent, entities, api_integrator):
        """处理打开文件夹意图"""
        import re
        
        # 提取文件夹路径
        folder_path = None
        
        # 1. 从实体中提取
        for entity_type, entity in entities:
            if entity_type == "file_path":
                folder_path = entity
                break
        
        # 2. 从用户输入中提取
        if not folder_path:
            # 常见文件夹关键词
            folder_keywords = {
                "桌面": "桌面",
                "文档": "文档",
                "下载": "下载",
                "图片": "图片",
                "音乐": "音乐",
                "视频": "视频",
                "我的文档": "文档",
                "我的桌面": "桌面",
                "我的下载": "下载",
                "我的图片": "图片",
                "我的音乐": "音乐",
                "我的视频": "视频",
                "文档文件夹": "文档",
                "下载文件夹": "下载",
                "图片文件夹": "图片"
            }
            
            for keyword, path in folder_keywords.items():
                if keyword in user_input:
                    folder_path = path
                    break
            
            # 尝试从"打开+路径"模式提取
            if not folder_path:
                patterns = [
                    r"打开\s*(.+?)(?:文件夹)?(?:吧|呗|啊)?$",
                    r"查看\s*(.+?)(?:文件夹)?(?:吧|呗|啊)?$",
                    r"浏览\s*(.+?)(?:文件夹)?(?:吧|呗|啊)?$"
                ]
                for pattern in patterns:
                    match = re.search(pattern, user_input)
                    if match:
                        candidate = match.group(1).strip()
                        # 检查是否是文件夹相关
                        if any(kw in candidate for kw in ["文件夹", "目录", "桌面", "文档", "下载", "图片", "音乐", "视频"]):
                            folder_path = candidate
                            break
        
        # 如果没有提取到文件夹路径，返回提示
        if not folder_path:
            return "请告诉我您想要打开的文件夹，例如：打开桌面、打开文档文件夹"
        
        logger.info(f"准备打开文件夹: {folder_path}")
        
        try:
            # 调用本地操作API打开文件夹
            result = api_integrator.open_folder(folder_path)
            return result
        except Exception as e:
            logger.error(f"打开文件夹失败: {e}")
            return f"抱歉，打开文件夹时出错: {str(e)}"
    
    def handle_open_application(self, user_input, intent, entities, api_integrator):
        """处理打开应用程序意图"""
        import re
        
        # 提取应用程序名称
        app_name = None
        
        # 1. 首先从实体中提取
        for entity_type, entity in entities:
            if entity_type == "app_name":
                app_name = entity
                break
        
        # 2. 如果没有从实体中提取到，尝试从用户输入中直接提取
        if not app_name:
            # 匹配"打开/启动/运行/开启 + 应用名"模式
            patterns = [
                r"打开\s*(.+?)(?:吧|呗|啊|哦|了)?$",
                r"启动\s*(.+?)(?:吧|呗|啊|哦|了)?$",
                r"运行\s*(.+?)(?:吧|呗|啊|哦|了)?$",
                r"开启\s*(.+?)(?:吧|呗|啊|哦|了)?$",
                r"帮我打开\s*(.+?)(?:吧|呗|啊|哦|了)?$",
                r"请打开\s*(.+?)(?:吧|呗|啊|哦|了)?$"
            ]
            for pattern in patterns:
                match = re.search(pattern, user_input)
                if match:
                    app_name = match.group(1).strip()
                    # 去除可能的语气词
                    app_name = re.sub(r'[吧呗啊哦了]+$', '', app_name).strip()
                    if app_name:
                        break
        
        # 3. 如果还是没有，检查是否直接说了应用名
        if not app_name:
            # 常见应用名列表
            common_apps = [
                "微信", "QQ", "浏览器", "Chrome", "Edge", "Firefox", "Word", "Excel", 
                "PowerPoint", "记事本", "计算器", "画图", "酷狗", "酷狗音乐", "网易云音乐",
                "QQ音乐", "B站", "哔哩哔哩", "抖音", "微博", "淘宝", "京东", "支付宝",
                "钉钉", "飞书", "企业微信", "腾讯会议", "Zoom", "VSCode", "PyCharm",
                "设置", "控制面板", "任务管理器", "命令提示符", "PowerShell"
            ]
            for app in common_apps:
                if app.lower() in user_input.lower():
                    app_name = app
                    break
        
        # 如果没有提取到应用程序名称，返回提示
        if not app_name:
            return "请告诉我您想要打开的应用程序名称，例如：打开微信、打开记事本"
        
        logger.info(f"准备打开应用: {app_name}")
        
        try:
            # 检查是否需要确认敏感操作
            if SecurityConfig.REQUIRE_CONFIRMATION_FOR_SENSITIVE_OPS:
                # 检查是否为敏感操作
                sensitive_apps = ["cmd", "命令提示符", "powershell", "终端", "bash", "注册表", "regedit"]
                if app_name.lower() in [app.lower() for app in sensitive_apps]:
                    # 记录需要确认的操作
                    self.current_context["pending_questions"].append({
                        "type": "confirmation",
                        "action": "open_application",
                        "params": {"app_name": app_name},
                        "message": f"确定要打开 {app_name} 吗？这是一个具有系统访问权限的应用程序。"
                    })
                    return f"确定要打开 {app_name} 吗？这是一个具有系统访问权限的应用程序。"
            
            # 调用本地操作API打开应用程序
            result = api_integrator.open_application(app_name)
            return result
        except Exception as e:
            logger.error(f"打开应用程序失败: {e}")
            return f"抱歉，打开应用程序时出错: {str(e)}"
    
    def handle_search_map(self, user_input, intent, entities, api_integrator):
        """处理地图搜索意图"""
        # 提取位置
        location = None
        for entity_type, entity in entities:
            if entity_type == "location":
                location = entity
                break
        
        # 如果没有提取到位置，返回提示
        if not location:
            return "请告诉我您想要搜索的位置"
        
        try:
            # 调用地图搜索API
            result = api_integrator.search_map(location)
            return result
        except Exception as e:
            logger.error(f"地图搜索失败: {e}")
            return f"抱歉，地图搜索时出错: {str(e)}"
    
    def handle_search_internet(self, user_input, intent, entities, api_integrator):
        """处理互联网搜索意图"""
        # 提取搜索查询
        query = None
        for entity_type, entity in entities:
            if entity_type == "query":
                query = entity
                break
        
        # 如果没有提取到查询，返回提示
        if not query:
            # 尝试从用户输入中提取查询
            import re
            query_match = re.search(r'搜索(.+)', user_input)
            if query_match:
                query = query_match.group(1)
            else:
                return "请告诉我您想要搜索的内容"
        
        try:
            # 调用互联网搜索API
            result = api_integrator.search_internet(query)
            return result
        except Exception as e:
            logger.error(f"互联网搜索失败: {e}")
            return f"抱歉，互联网搜索时出错: {str(e)}"
    
    def handle_list_files(self, user_input, intent, entities, api_integrator):
        """处理列出文件意图"""
        # 提取目录路径
        directory = None
        for entity_type, entity in entities:
            if entity_type == "file_path":
                directory = entity
                break
        
        # 如果没有提取到目录路径，返回提示
        if not directory:
            return "请告诉我您想要查看的目录路径"
        
        try:
            # 调用本地操作API列出文件
            result = api_integrator.list_files(directory)
            return result
        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return f"抱歉，列出文件时出错: {str(e)}"
    
    def handle_unknown(self, user_input, intent, entities, api_integrator):
        """处理未知意图"""
        return self._get_default_response()
    
    def _save_dialogue_history(self, user_input, intent, entities, response):
        """保存对话历史到数据库"""
        try:
            # 连接数据库
            conn = sqlite3.connect(self.history_path)
            cursor = conn.cursor()
            
            # 获取安全配置
            encrypt_data = SecurityConfig.ENCRYPT_USER_DATA
            
            # 加密敏感数据
            if encrypt_data:
                user_input = self.security_manager.encrypt(user_input)
                response = self.security_manager.encrypt(response)
                entities = self.security_manager.encrypt(str(entities))
                is_encrypted = 1
            else:
                entities = str(entities)
                is_encrypted = 0
            
            # 插入对话记录
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO dialogue_history (timestamp, user_input, intent, entities, response, is_encrypted)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, user_input, intent, entities, response, is_encrypted))
            
            conn.commit()
            conn.close()
            
            # 清理旧的对话历史
            self._cleanup_history()
            
        except Exception as e:
            logger.error(f"保存对话历史失败: {e}")
    
    def _cleanup_history(self):
        """清理旧的对话历史，只保留最近的记录"""
        try:
            conn = sqlite3.connect(self.history_path)
            cursor = conn.cursor()
            
            # 获取总记录数
            cursor.execute('SELECT COUNT(*) FROM dialogue_history')
            total_records = cursor.fetchone()[0]
            
            # 如果记录数超过最大值，删除最旧的记录
            if total_records > self.max_history_length:
                delete_count = total_records - self.max_history_length
                cursor.execute('''
                    DELETE FROM dialogue_history
                    WHERE id IN (
                        SELECT id FROM dialogue_history
                        ORDER BY timestamp ASC
                        LIMIT ?
                    )
                ''', (delete_count,))
                conn.commit()
                logger.info(f"已清理 {delete_count} 条旧对话历史记录")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"清理对话历史失败: {e}")
    
    def _get_default_response(self):
        """获取默认回复"""
        import random
        return random.choice(self.default_responses)
    
    def get_dialogue_history(self, limit=10):
        """获取最近的对话历史"""
        try:
            conn = sqlite3.connect(self.history_path)
            cursor = conn.cursor()
            
            # 查询最近的对话历史
            cursor.execute('''
                SELECT timestamp, user_input, response, is_encrypted
                FROM dialogue_history
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            history = cursor.fetchall()
            conn.close()
            
            # 解密数据
            decrypted_history = []
            for record in history:
                timestamp, user_input, response, is_encrypted = record
                
                if is_encrypted:
                    try:
                        user_input = self.security_manager.decrypt(user_input)
                        response = self.security_manager.decrypt(response)
                    except Exception as e:
                        logger.error(f"解密对话历史失败: {e}")
                        continue
                
                decrypted_history.append((timestamp, user_input, response))
            
            # 反转顺序，从旧到新
            return reversed(decrypted_history)
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    def clear_dialogue_history(self):
        """清空对话历史"""
        try:
            conn = sqlite3.connect(self.history_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM dialogue_history')
            conn.commit()
            conn.close()
            
            logger.info("对话历史已清空")
            return True
            
        except Exception as e:
            logger.error(f"清空对话历史失败: {e}")
            return False
