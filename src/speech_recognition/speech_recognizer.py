#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
语音识别模块
"""

import os
import sys
import time
import logging
import threading
import pyaudio
import speech_recognition as sr
from config.config import SpeechRecognitionConfig

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    """语音识别类"""
    
    def __init__(self):
        """初始化语音识别器"""
        # 创建语音识别器对象
        self.recognizer = sr.Recognizer()
        
        # 设置音频参数
        self.sample_rate = SpeechRecognitionConfig.SAMPLE_RATE
        self.chunk_size = SpeechRecognitionConfig.CHUNK_SIZE
        
        # 设置识别语言
        self.language = SpeechRecognitionConfig.LANGUAGE
        
        # 设置唤醒词
        self.wake_up_words = SpeechRecognitionConfig.WAKE_UP_WORDS
        self.wake_word_sensitivity = 0.5  # 唤醒词灵敏度 0.0-1.0
        
        # 设置使用的引擎
        self.engine = SpeechRecognitionConfig.ENGINE
        
        # 扩展识别参数
        self.energy_threshold = 300  # 语音检测能量阈值
        self.dynamic_energy_threshold = True  # 动态阈值
        self.pause_threshold = 0.8  # 语音暂停时间阈值
        self.phrase_time_limit = 10  # 最大语音长度
        
        # 状态标志
        self.is_listening = False
        self.is_recording = False
        
        # 回调函数
        self.on_voice_detected = None
        self.on_speech_recognized = None
        
        # 初始化麦克风
        self.microphone = None
        self._initialize_microphone()
    
    def _initialize_microphone(self):
        """初始化麦克风"""
        try:
            self.microphone = sr.Microphone(sample_rate=self.sample_rate)
            logger.info("麦克风初始化成功")
            
            # 校准麦克风，适应环境噪音
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                self.energy_threshold = self.recognizer.energy_threshold
            logger.info(f"麦克风噪音校准完成，当前能量阈值: {self.energy_threshold}")
            
        except Exception as e:
            logger.error(f"麦克风初始化失败: {e}")
            raise
    
    def recognize(self, timeout=10, phrase_time_limit=None):
        """识别用户语音输入"""
        try:
            with self.microphone as source:
                # 设置识别器参数
                self.recognizer.energy_threshold = self.energy_threshold
                self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
                self.recognizer.pause_threshold = self.pause_threshold
                
                logger.info("正在监听用户语音...")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit or self.phrase_time_limit
                )
            
            logger.info("语音输入已捕获，正在识别...")
            
            # 调用语音检测回调
            if self.on_voice_detected:
                threading.Thread(target=self.on_voice_detected, args=(audio,)).start()
            
            # 尝试使用多个识别引擎
            text = None
            engines_tried = []
            
            # 首先尝试配置的引擎
            if self.engine == "baidu":
                engines_tried.append("baidu")
                text = self._recognize_baidu(audio)
            else:  # 默认使用Google
                engines_tried.append("google")
                text = self._recognize_google(audio)
            
            # 如果当前引擎失败，尝试备用引擎
            if not text:
                if "google" not in engines_tried:
                    engines_tried.append("google")
                    logger.info("百度引擎识别失败，尝试Google语音识别")
                    text = self._recognize_google(audio)
                elif "baidu" not in engines_tried:
                    engines_tried.append("baidu")
                    logger.info("Google引擎识别失败，尝试百度语音识别")
                    text = self._recognize_baidu(audio)
            
            # 调用识别完成回调
            if text and self.on_speech_recognized:
                self.on_speech_recognized(text)
            
            return text.strip() if text else None
            
        except sr.WaitTimeoutError:
            logger.info("语音输入超时")
            return None
        except sr.UnknownValueError:
            logger.info("无法识别语音")
            return None
        except sr.RequestError as e:
            logger.error(f"语音识别服务请求失败: {e}")
            # 网络连接问题，不尝试重新识别
            return None
        except Exception as e:
            logger.error(f"语音识别过程中发生错误: {e}")
            return None
    
    def _recognize_google(self, audio):
        """使用Google语音识别引擎"""
        try:
            return self.recognizer.recognize_google(
                audio, 
                language=self.language
            )
        except Exception as e:
            logger.error(f"Google语音识别失败: {e}")
            raise
    
    def _recognize_baidu(self, audio):
        """使用百度语音识别引擎"""
        try:
            # 从环境变量获取百度API密钥
            api_key = os.environ.get("BAIDU_ASR_API_KEY") or SpeechRecognitionConfig.BAIDU_API_KEY
            secret_key = os.environ.get("BAIDU_ASR_SECRET_KEY") or SpeechRecognitionConfig.BAIDU_SECRET_KEY
            app_id = os.environ.get("BAIDU_ASR_APP_ID") or SpeechRecognitionConfig.BAIDU_APP_ID
            
            if not all([api_key, secret_key, app_id]):
                logger.warning("百度语音识别API密钥未配置，回退到Google")
                return self._recognize_google(audio)
            
            try:
                # 尝试使用SpeechRecognition的百度识别方法
                return self.recognizer.recognize_baidu(
                    audio, 
                    app_id=app_id,
                    api_key=api_key,
                    secret_key=secret_key,
                    language=self.language
                )
            except AttributeError:
                # 如果SpeechRecognition库没有baidu识别方法，使用直接调用方式
                logger.info("使用直接调用方式访问百度语音识别API")
                try:
                    from aip import AipSpeech
                    client = AipSpeech(app_id, api_key, secret_key)
                    
                    # 转换音频数据
                    audio_data = audio.get_raw_data(convert_rate=16000, convert_width=2)
                    
                    # 调用百度语音识别API
                    result = client.asr(audio_data, 'pcm', 16000, {
                        'dev_pid': 1537,  # 中文普通话
                    })
                    
                    if result['err_no'] == 0:
                        return result['result'][0]
                    else:
                        logger.error(f"百度语音识别API失败: {result['err_msg']}")
                        return self._recognize_google(audio)
                except ImportError:
                    logger.error("百度语音识别依赖未安装，回退到Google")
                    return self._recognize_google(audio)
        except Exception as e:
            logger.error(f"百度语音识别失败: {e}")
            # 回退到Google语音识别
            return self._recognize_google(audio)
    
    def check_wake_up_word(self, text):
        """检查文本中是否包含唤醒词"""
        if not text:
            return False, ""
        
        for word in self.wake_up_words:
            if word in text:
                # 移除唤醒词，只保留实际命令
                text = text.replace(word, "").strip()
                return True, text
        
        return False, text
    
    def listen_for_wake_up(self, timeout=60):
        """监听唤醒词"""
        logger.info(f"正在监听唤醒词: {', '.join(self.wake_up_words)}")
        logger.info(f"唤醒词灵敏度: {self.wake_word_sensitivity}")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            text = self.recognize()
            
            if text:
                logger.info(f"检测到语音: {text}")
                is_wake_up, command = self.check_wake_up_word(text)
                
                if is_wake_up:
                    logger.info(f"唤醒词检测成功，命令: {command}")
                    return command
        
        logger.info("唤醒词监听超时")
        return None
    
    def calibrate_microphone(self, duration=2):
        """校准麦克风，适应环境噪音"""
        logger.info(f"正在校准麦克风，持续{duration}秒...")
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                self.energy_threshold = self.recognizer.energy_threshold
            logger.info(f"麦克风校准完成，当前能量阈值: {self.energy_threshold}")
            return True
        except Exception as e:
            logger.error(f"麦克风校准失败: {e}")
            return False
    
    def start_continuous_listening(self):
        """开始持续监听模式"""
        logger.info("开始持续监听模式...")
        
        self.is_listening = True
        
        def listen_thread():
            while self.is_listening:
                try:
                    text = self.recognize()
                    if text:
                        logger.info(f"持续监听识别到: {text}")
                        if self.on_speech_recognized:
                            self.on_speech_recognized(text)
                except Exception as e:
                    logger.error(f"持续监听错误: {e}")
                    time.sleep(1)
        
        threading.Thread(target=listen_thread).daemon=True
        threading.Thread(target=listen_thread).start()
    
    def stop_continuous_listening(self):
        """停止持续监听模式"""
        logger.info("停止持续监听模式")
        self.is_listening = False
    
    def set_energy_threshold(self, threshold):
        """设置语音检测能量阈值"""
        if threshold > 0:
            self.energy_threshold = threshold
            logger.info(f"语音检测能量阈值已设置为: {threshold}")
        else:
            logger.warning("能量阈值必须大于0")
    
    def set_wake_word_sensitivity(self, sensitivity):
        """设置唤醒词灵敏度"""
        if 0.0 <= sensitivity <= 1.0:
            self.wake_word_sensitivity = sensitivity
            # 根据灵敏度调整能量阈值
            self.energy_threshold = int(300 * (1 - sensitivity) + 50)
            logger.info(f"唤醒词灵敏度已设置为: {sensitivity}, 能量阈值: {self.energy_threshold}")
        else:
            logger.warning("灵敏度必须在0.0-1.0之间")
    
    def get_available_devices(self):
        """获取可用的音频输入设备列表"""
        devices = []
        try:
            p = pyaudio.PyAudio()
            info = p.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            for i in range(0, num_devices):
                if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    devices.append({
                        'id': i,
                        'name': p.get_device_info_by_host_api_device_index(0, i).get('name')
                    })
            
            p.terminate()
            logger.info(f"找到{len(devices)}个音频输入设备")
            return devices
        except Exception as e:
            logger.error(f"获取音频设备列表失败: {e}")
            return []
    
    def set_recognition_engine(self, engine):
        """设置语音识别引擎"""
        valid_engines = ["google", "baidu"]
        if engine in valid_engines:
            self.engine = engine
            logger.info(f"语音识别引擎已设置为: {engine}")
            return True
        else:
            logger.warning(f"无效的识别引擎，必须是: {', '.join(valid_engines)}")
            return False
