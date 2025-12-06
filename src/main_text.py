#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音助手主程序（文本输入版）
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from config.config import GlobalConfig

# 配置日志
logging.basicConfig(
    level=getattr(logging, GlobalConfig.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(GlobalConfig.LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class VoiceAssistantText:
    """语音助手主类（文本输入版）"""
    
    def __init__(self):
        """初始化语音助手"""
        logger.info("正在初始化语音助手...")
        
        # 初始化各个模块
        self.nlp_processor = None
        self.tts_engine = None
        self.dialogue_manager = None
        self.api_integrator = None
        
        self._initialize_modules()
    
    def _initialize_modules(self):
        """初始化各个功能模块"""
        try:
            # 导入并初始化NLP模块
            from src.nlp.nlp_processor import NLPProcessor
            self.nlp_processor = NLPProcessor()
            logger.info("NLP模块初始化成功")
            
            # 导入并初始化语音合成模块
            try:
                from src.tts.tts_engine import TTSEngine
                self.tts_engine = TTSEngine()
                logger.info("语音合成模块初始化成功")
            except Exception as e:
                logger.warning(f"语音合成模块初始化失败: {e}")
                self.tts_engine = None
            
            # 导入并初始化对话管理模块
            from src.dialogue_manager.dialogue_manager import DialogueManager
            self.dialogue_manager = DialogueManager()
            logger.info("对话管理模块初始化成功")
            
            # 导入并初始化API集成模块
            from src.api_integration.api_integrator import APIIntegrator
            self.api_integrator = APIIntegrator()
            logger.info("API集成模块初始化成功")
            
        except Exception as e:
            logger.error(f"模块初始化失败: {e}")
            raise
    
    def run(self):
        """启动语音助手"""
        logger.info("语音助手（文本版）启动成功")
        if self.tts_engine:
            try:
                self.tts_engine.speak("语音助手已启动，您可以开始输入了")
            except Exception as e:
                logger.warning(f"语音合成失败: {e}")
        print("语音助手已启动，您可以开始输入了（输入'退出'结束程序）:")
        
        try:
            while True:
                # 获取用户文本输入
                user_input = input("\n用户: ")
                
                if user_input.strip():
                    logger.info(f"用户输入: {user_input}")
                    
                    # 如果是退出命令，结束程序
                    if self._is_exit_command(user_input):
                        logger.info("用户发出退出命令，程序即将关闭")
                        if self.tts_engine:
                            try:
                                self.tts_engine.speak("再见，期待与您再次交流")
                            except Exception as e:
                                logger.warning(f"语音合成失败: {e}")
                        print("再见，期待与您再次交流")
                        break
                    
                    # 处理用户输入
                    response = self.process_input(user_input)
                    
                    # 输出响应
                    logger.info(f"助手响应: {response}")
                    if self.tts_engine:
                        try:
                            self.tts_engine.speak(response)
                        except Exception as e:
                            logger.warning(f"语音合成失败: {e}")
                    print(f"助手: {response}")
                    
        except KeyboardInterrupt:
            logger.info("用户中断程序")
            if self.tts_engine:
                try:
                    self.tts_engine.speak("程序已关闭")
                except Exception as e:
                    logger.warning(f"语音合成失败: {e}")
        except Exception as e:
            logger.error(f"程序运行出错: {e}")
            if self.tts_engine:
                try:
                    self.tts_engine.speak("程序运行出错，请检查日志")
                except Exception as e:
                    logger.warning(f"语音合成失败: {e}")
    
    def process_input(self, user_input):
        """处理用户输入"""
        try:
            # 生成响应
            response = self.dialogue_manager.generate_response(
                user_input, self.api_integrator
            )
            
            return response
            
        except Exception as e:
            logger.error(f"处理用户输入出错: {e}")
            return "抱歉，处理您的请求时出错了"
    
    def _is_exit_command(self, user_input):
        """判断是否为退出命令"""
        exit_commands = ["退出", "关闭", "再见", "停止", "结束"]
        for cmd in exit_commands:
            if cmd in user_input:
                return True
        return False

if __name__ == "__main__":
    try:
        assistant = VoiceAssistantText()
        assistant.run()
    except Exception as e:
        logger.error(f"语音助手启动失败: {e}")
        print(f"语音助手启动失败: {e}")
        sys.exit(1)
