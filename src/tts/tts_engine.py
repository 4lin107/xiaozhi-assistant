#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音合成模块
"""

import os
import sys
import logging
import pyttsx3
import tempfile
from config.config import TTSConfig

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class TTSEngine:
    """语音合成引擎类"""
    
    def __init__(self):
        """初始化语音合成引擎"""
        # 设置使用的引擎
        self.engine = TTSConfig.ENGINE
        
        # 设置语音合成参数
        self.rate = TTSConfig.VOICE_RATE
        self.volume = TTSConfig.VOICE_VOLUME
        self.voice_id = TTSConfig.VOICE_ID
        
        # 扩展参数
        self.pitch = 5  # 语调 0-9
        self.voice_gender = "female"  # 语音性别
        
        # 初始化引擎
        self.tts_engine = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """初始化语音合成引擎"""
        try:
            if self.engine == "baidu":
                # 初始化百度语音合成引擎
                self._initialize_baidu_engine()
            else:  # 默认使用pyttsx3
                # 初始化pyttsx3引擎
                self.tts_engine = pyttsx3.init()
                self._configure_pyttsx3_engine()
                logger.info("pyttsx3语音合成引擎初始化成功")
        except Exception as e:
            logger.error(f"语音合成引擎初始化失败: {e}")
            # 回退到pyttsx3
            self.engine = "pyttsx3"
            self.tts_engine = pyttsx3.init()
            self._configure_pyttsx3_engine()
            logger.info("已回退到pyttsx3语音合成引擎")
    
    def _configure_pyttsx3_engine(self):
        """配置pyttsx3引擎参数"""
        # 设置语速
        self.tts_engine.setProperty('rate', self.rate)
        
        # 设置音量
        self.tts_engine.setProperty('volume', self.volume)
        
        # 设置语音（如果有多个语音可用）
        voices = self.tts_engine.getProperty('voices')
        voice_found = False
        
        # 优先根据性别选择语音
        if self.voice_gender:
            logger.info(f"尝试选择{self.voice_gender}性别的语音")
            for i, voice in enumerate(voices):
                if self.voice_gender in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    logger.info(f"已设置语音: {voice.name}")
                    voice_found = True
                    break
        
        # 如果根据性别未找到，使用指定的voice_id
        if not voice_found and len(voices) > self.voice_id:
            self.tts_engine.setProperty('voice', voices[self.voice_id].id)
            logger.info(f"已设置语音: {voices[self.voice_id].name}")
            voice_found = True
        
        if not voice_found:
            logger.warning("未找到匹配的语音，使用默认语音")
    
    def _initialize_baidu_engine(self):
        """初始化百度语音合成引擎"""
        try:
            # 从环境变量获取百度API密钥
            self.baidu_api_key = os.environ.get("BAIDU_TTS_API_KEY") or TTSConfig.BAIDU_API_KEY
            self.baidu_secret_key = os.environ.get("BAIDU_TTS_SECRET_KEY") or TTSConfig.BAIDU_SECRET_KEY
            
            if not all([self.baidu_api_key, self.baidu_secret_key]):
                raise ValueError("百度语音合成API密钥未配置")
            
            # 安装百度语音合成SDK
            try:
                from aip import AipSpeech
                self.aip_speech = AipSpeech(
                    "",  # app_id 可以留空
                    self.baidu_api_key,
                    self.baidu_secret_key
                )
                logger.info("百度语音合成引擎初始化成功")
            except ImportError:
                raise ImportError("请安装baidu-aip库: pip install baidu-aip")
        except Exception as e:
            logger.error(f"百度语音合成引擎初始化失败: {e}")
            raise
    
    def speak(self, text):
        """将文本转换为语音并播放"""
        if not text:
            return
        
        logger.info(f"正在合成语音: {text[:20]}...")
        
        try:
            if self.engine == "baidu":
                self._speak_baidu(text)
            else:
                self._speak_pyttsx3(text)
        except Exception as e:
            logger.error(f"语音合成失败: {e}")
            # 回退到pyttsx3
            if self.engine != "pyttsx3":
                logger.info("回退到pyttsx3语音合成引擎")
                self._speak_pyttsx3(text)
    
    def _speak_pyttsx3(self, text):
        """使用pyttsx3合成语音"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            logger.info("pyttsx3语音合成完成")
        except Exception as e:
            logger.error(f"pyttsx3语音合成失败: {e}")
            # 尝试重新初始化引擎
            logger.info("尝试重新初始化pyttsx3引擎")
            self._initialize_engine()
            # 再次尝试合成
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                logger.info("重新初始化后pyttsx3语音合成完成")
            except Exception as re:
                logger.error(f"重新初始化后pyttsx3语音合成仍失败: {re}")
                raise
    
    def _speak_baidu(self, text):
        """使用百度语音合成API"""
        try:
            # 根据性别选择发音人
            per_map = {
                "female": 0,  # 女声
                "male": 1,    # 男声
                "emotional_male": 3,  # 情感男声
                "emotional_female": 4  # 情感女声
            }
            per = per_map.get(self.voice_gender, 0)
            
            # 调用百度语音合成API
            result = self.aip_speech.synthesis(
                text,
                'zh',  # 语言
                1,  # 客户端类型
                {
                    'vol': int(self.volume * 15),  # 音量 0-15
                    'spd': max(0, min(9, int(self.rate / 10))),  # 语速 0-9
                    'pit': max(0, min(9, self.pitch)),  # 语调 0-9
                    'per': per,  # 发音人选择
                }
            )
            
            # 检查是否合成成功
            if not isinstance(result, dict):
                # 使用系统临时文件
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    temp_file.write(result)
                    temp_audio_file = temp_file.name
                
                try:
                    # 播放音频文件
                    import playsound
                    playsound.playsound(temp_audio_file)
                    logger.info("百度语音合成完成")
                finally:
                    # 删除临时文件
                    if os.path.exists(temp_audio_file):
                        os.remove(temp_audio_file)
            else:
                error_msg = result.get('err_msg', '未知错误')
                logger.error(f"百度语音合成失败: {error_msg}")
                raise Exception(f"百度语音合成失败: {error_msg}")
                
        except ImportError:
            logger.error("playsound库未安装")
            # 尝试使用另一种播放方式
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(result)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                logger.info("使用pygame播放百度语音完成")
            except Exception:
                raise ImportError("请安装playsound库: pip install playsound")
        except Exception as e:
            logger.error(f"百度语音合成失败: {e}")
            raise
    
    def save_to_file(self, text, file_path):
        """将文本转换为语音并保存到文件"""
        if not text or not file_path:
            return False
        
        logger.info(f"正在将文本合成语音并保存到文件: {file_path}")
        
        try:
            if self.engine == "baidu":
                return self._save_to_file_baidu(text, file_path)
            else:
                return self._save_to_file_pyttsx3(text, file_path)
        except Exception as e:
            logger.error(f"语音保存失败: {e}")
            return False
    
    def _save_to_file_pyttsx3(self, text, file_path):
        """使用pyttsx3将语音保存到文件"""
        try:
            self.tts_engine.save_to_file(text, file_path)
            self.tts_engine.runAndWait()
            logger.info(f"语音已保存到文件: {file_path}")
            return True
        except Exception as e:
            logger.error(f"pyttsx3语音保存失败: {e}")
            return False
    
    def _save_to_file_baidu(self, text, file_path):
        """使用百度语音合成API将语音保存到文件"""
        try:
            # 调用百度语音合成API
            result = self.aip_speech.synthesis(
                text,
                'zh',  # 语言
                1,  # 客户端类型
                {
                    'vol': int(self.volume * 15),  # 音量 0-15
                    'spd': int(self.rate / 10),  # 语速 0-9
                    'pit': 5,  # 语调 0-9
                    'per': 0,  # 发音人选择 0:女声 1:男声 3:情感男声 4:情感女声
                }
            )
            
            # 检查是否合成成功
            if not isinstance(result, dict):
                # 保存音频文件
                with open(file_path, "wb") as f:
                    f.write(result)
                
                logger.info(f"语音已保存到文件: {file_path}")
                return True
            else:
                logger.error(f"百度语音合成失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"百度语音保存失败: {e}")
            return False
    
    def speak_to_file(self, text, file_path):
        """将文本转换为语音并保存到文件（与save_to_file方法相同）"""
        return self.save_to_file(text, file_path)
    
    def set_rate(self, rate):
        """设置语速"""
        if 50 <= rate <= 300:
            self.rate = rate
            if self.tts_engine:
                self.tts_engine.setProperty('rate', rate)
            logger.info(f"语速已设置为: {rate}")
        else:
            logger.warning("语速必须在50-300之间")
    
    def set_volume(self, volume):
        """设置音量"""
        if 0.0 <= volume <= 1.0:
            self.volume = volume
            if self.tts_engine:
                self.tts_engine.setProperty('volume', volume)
            logger.info(f"音量已设置为: {volume}")
        else:
            logger.warning("音量必须在0.0-1.0之间")
    
    def set_pitch(self, pitch):
        """设置语调"""
        if 0 <= pitch <= 9:
            self.pitch = pitch
            logger.info(f"语调已设置为: {pitch}")
        else:
            logger.warning("语调必须在0-9之间")
    
    def set_voice_gender(self, gender):
        """设置语音性别"""
        valid_genders = ["female", "male", "emotional_male", "emotional_female"]
        if gender in valid_genders:
            self.voice_gender = gender
            # 重新配置语音
            if self.tts_engine:
                self._configure_pyttsx3_engine()
            logger.info(f"语音性别已设置为: {gender}")
        else:
            logger.warning(f"无效的语音性别，必须是: {', '.join(valid_genders)}")
    
    def get_available_voices(self):
        """获取可用的语音列表"""
        try:
            if self.tts_engine:
                voices = self.tts_engine.getProperty('voices')
                voice_list = []
                for i, voice in enumerate(voices):
                    voice_list.append({
                        'id': i,
                        'name': voice.name,
                        'lang': voice.languages[0] if voice.languages else 'unknown',
                        'gender': 'female' if 'female' in voice.name.lower() else 'male' if 'male' in voice.name.lower() else 'unknown'
                    })
                return voice_list
            return []
        except Exception as e:
            logger.error(f"获取可用语音列表失败: {e}")
            return []
