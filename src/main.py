#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音助手主程序
"""

import os
import sys
import logging
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置和安全管理器
from config.config import GlobalConfig, APIConfig, SecurityConfig
from security.security_manager import SecurityManager

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

class VoiceAssistant:
    """语音助手主类"""
    
    def __init__(self):
        """初始化语音助手"""
        logger.info("正在初始化语音助手...")
        
        # 初始化各个模块
        self.speech_recognizer = None
        self.nlp_processor = None
        self.tts_engine = None
        self.dialogue_manager = None
        self.api_integrator = None
        self.ui = None
        
        self._initialize_modules()
    
    def _initialize_modules(self):
        """初始化各个功能模块"""
        try:
            # 初始化安全管理器
            from src.security.security_manager import get_security_manager
            self.security_manager = get_security_manager()
            logger.info("安全管理器初始化成功")
            
            # 导入并初始化语音识别模块
            from src.speech_recognition.speech_recognizer import SpeechRecognizer
            self.speech_recognizer = SpeechRecognizer()
            logger.info("语音识别模块初始化成功")
            
            # 导入并初始化NLP模块
            from src.nlp.nlp_processor import NLPProcessor
            self.nlp_processor = NLPProcessor()
            logger.info("NLP模块初始化成功")
            
            # 导入并初始化语音合成模块
            from src.tts.tts_engine import TTSEngine
            self.tts_engine = TTSEngine()
            logger.info("语音合成模块初始化成功")
            
            # 导入并初始化对话管理模块
            from src.dialogue_manager.dialogue_manager import DialogueManager
            self.dialogue_manager = DialogueManager()
            logger.info("对话管理模块初始化成功")
            
            # 导入并初始化API集成模块
            from src.api_integration.api_integrator import APIIntegrator
            self.api_integrator = APIIntegrator()
            logger.info("API集成模块初始化成功")
            
            # 导入并初始化UI模块（可选）
            try:
                from src.ui.main_window import MainWindow
                self.ui = MainWindow()
                logger.info("UI模块初始化成功")
            except ImportError:
                logger.info("未初始化UI模块")
                self.ui = None
                
        except Exception as e:
            logger.error(f"模块初始化失败: {e}")
            raise
    
    def run(self):
        """启动语音助手"""
        logger.info("语音助手启动成功")
        self.tts_engine.speak("语音助手已启动，您可以开始说话了")
        
        try:
            while True:
                # 等待用户语音输入
                logger.info("等待用户语音输入...")
                user_input = self.speech_recognizer.recognize()
                
                if user_input:
                    logger.info(self.security_manager.mask_sensitive_data(f"用户输入: {user_input}"))
                    
                    # 处理用户输入
                    response = self.process_input(user_input)
                    
                    # 输出响应
                    logger.info(self.security_manager.mask_sensitive_data(f"助手响应: {response}"))
                    self.tts_engine.speak(response)
                    
                    # 如果是退出命令，结束程序
                    if self._is_exit_command(user_input):
                        logger.info("用户发出退出命令，程序即将关闭")
                        self.tts_engine.speak("再见，期待与您再次交流")
                        break
                        
        except KeyboardInterrupt:
            logger.info("用户中断程序")
            self.tts_engine.speak("程序已关闭")
        except Exception as e:
            logger.error(f"程序运行出错: {e}")
            self.tts_engine.speak("程序运行出错，请检查日志")
    
    def process_input(self, user_input):
        """处理用户输入"""
        try:
            logger.info(f"用户输入: {user_input}")
            
            # 直接通过DialogueManager生成响应
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
        # 打印当前Python版本和路径
        print(f"Python版本: {sys.version}")
        print(f"Python路径: {sys.executable}")
        
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        logger.error(f"语音助手启动失败: {e}", exc_info=True)
        print(f"语音助手启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
