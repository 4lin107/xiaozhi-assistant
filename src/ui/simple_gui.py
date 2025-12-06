#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的语音助手GUI界面
使用Tkinter实现基本的用户交互界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import os
import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("voice_assistant_gui.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VoiceAssistantGUI:
    """语音助手GUI类"""
    
    def __init__(self, root):
        """初始化GUI"""
        self.root = root
        self.root.title("智能语音助手")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.root.configure(bg='#f5f7fa')
        
        # 设置主题色 (现代化配色方案)
        self.bg_color = "#f5f7fa"
        self.text_color = "#333333"
        self.primary_color = "#6366f1"  # 主色：靛蓝色
        self.secondary_color = "#8b5cf6"  # 辅助色：紫色
        self.success_color = "#10b981"  # 成功色：绿色
        self.warning_color = "#f59e0b"  # 警告色：橙色
        self.error_color = "#ef4444"    # 错误色：红色
        self.user_color = "#3b82f6"     # 用户消息色：蓝色
        self.assistant_color = "#10b981" # 助手消息色：绿色
        self.border_color = "#e2e8f0"    # 边框色：浅灰
        
        # 设置字体
        self.font_family = "微软雅黑"
        self.font_size = 11
        self.root.option_add("*Font", f"{self.font_family} {self.font_size}")
        
        # 初始化语音助手
        self.assistant = None
        self.is_running = False
        
        # 创建并配置样式
        self.setup_styles()
        
        # 创建界面元素
        self.create_widgets()
        
        # 初始化语音助手
        self.init_assistant()
    
    def setup_styles(self):
        """设置GUI样式"""
        style = ttk.Style()
        
        # 设置主题为clam以支持自定义样式
        style.theme_use('clam')
        
        # 设置框架样式
        style.configure('Status.TFrame', background='#f0f9ff', borderwidth=1, relief='solid')
        style.configure('Log.TFrame', background=self.bg_color, borderwidth=0)
        style.configure('Control.TFrame', background=self.bg_color, borderwidth=0)
        
        # 设置按钮样式
        style.configure('Primary.TButton', 
                       foreground='#ffffff', 
                       background=self.primary_color,
                       font=(self.font_family, self.font_size, 'bold'),
                       padding=(12, 6),
                       borderwidth=0,
                       relief='flat')
        style.map('Primary.TButton', 
                 background=[('active', self.secondary_color)],
                 foreground=[('active', '#ffffff')])
        
        style.configure('Secondary.TButton', 
                       foreground='#4b5563', 
                       background='#e5e7eb',
                       font=(self.font_family, self.font_size),
                       padding=(12, 6),
                       borderwidth=0,
                       relief='flat')
        style.map('Secondary.TButton', 
                 background=[('active', '#d1d5db')],
                 foreground=[('active', '#1f2937')])
        
        style.configure('Danger.TButton', 
                       foreground='#ffffff', 
                       background=self.error_color,
                       font=(self.font_family, self.font_size),
                       padding=(12, 6),
                       borderwidth=0,
                       bordercolor=self.error_color,
                       relief='flat')
        style.map('Danger.TButton', 
                 background=[('active', '#dc2626')],
                 foreground=[('active', '#ffffff')])
        
        style.configure('Send.TButton', 
                       foreground='#ffffff', 
                       background=self.success_color,
                       font=(self.font_family, self.font_size, 'bold'),
                       padding=(12, 6),
                       borderwidth=0,
                       bordercolor=self.success_color,
                       relief='flat')
        style.map('Send.TButton', 
                 background=[('active', '#059669')],
                 foreground=[('active', '#ffffff')])
        
        # 设置标签样式
        style.configure('Status.TLabel', font=(self.font_family, self.font_size), foreground='#4b5563')
        style.configure('Time.TLabel', font=(self.font_family, self.font_size-1), foreground='#9ca3af')
        
        # 设置输入框样式
        style.configure('Modern.TEntry', 
                       fieldbackground='#ffffff',
                       foreground='#1f2937',
                       font=(self.font_family, self.font_size),
                       padding=(10, 8),
                       borderwidth=1,
                       bordercolor=self.border_color,
                       relief='solid')
        style.map('Modern.TEntry', 
                 bordercolor=[('focus', self.primary_color)],
                 relief=[('focus', 'solid')])
    
    def create_widgets(self):
        """创建GUI组件"""
        # 创建主容器
        main_container = ttk.Frame(self.root, padding="8 8 8 8", style='Log.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建顶部状态栏
        status_frame = ttk.Frame(main_container, padding="10 8", style='Status.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="语音助手未初始化", foreground=self.error_color, style='Status.TLabel')
        self.status_label.pack(side=tk.LEFT, anchor=tk.CENTER)
        
        # 添加时间显示
        self.time_label = ttk.Label(status_frame, text="", style='Time.TLabel')
        self.time_label.pack(side=tk.RIGHT, anchor=tk.CENTER)
        self.update_time()
        
        # 创建日志显示区域容器
        log_container = ttk.Frame(main_container, style='Log.TFrame')
        log_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建日志显示区域（使用Frame替代LabelFrame以获得更好的样式控制）
        log_frame = ttk.Frame(log_container, padding="8", style='Log.TFrame', relief='solid', borderwidth=1)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 添加标题
        log_title = ttk.Label(log_frame, text="交互日志", font=(self.font_family, self.font_size+1, 'bold'), foreground='#1f2937')
        log_title.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        
        # 设置日志文本框样式
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=25,
                                                bg="#ffffff", fg=self.text_color,
                                                font=(self.font_family, self.font_size), relief=tk.FLAT,
                                                borderwidth=0, highlightthickness=0)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        self.log_text.config(state=tk.DISABLED)
        
        # 配置日志文本框的标签颜色和样式
        self.log_text.tag_configure("timestamp", foreground="#9ca3af", font=(self.font_family, self.font_size-1))
        
        # 用户消息样式 - 气泡效果
        self.log_text.tag_configure("user", foreground="#ffffff", font=(self.font_family, self.font_size, 'bold'))
        self.log_text.tag_configure("user_bubble", background=self.user_color, borderwidth=0, relief='flat')
        
        # 助手消息样式 - 气泡效果
        self.log_text.tag_configure("assistant", foreground="#ffffff", font=(self.font_family, self.font_size))
        self.log_text.tag_configure("assistant_bubble", background=self.assistant_color, borderwidth=0, relief='flat')
        
        # 系统消息样式
        self.log_text.tag_configure("system", foreground="#6b7280", font=(self.font_family, self.font_size-1, 'italic'))
        self.log_text.tag_configure("system_bubble", background="#f3f4f6", borderwidth=0, relief='flat')
        
        # 设置标签的边距
        self.log_text.tag_configure("user", lmargin1=10, lmargin2=10, rmargin=10, spacing3=10, spacing1=5)
        self.log_text.tag_configure("assistant", lmargin1=10, lmargin2=10, rmargin=10, spacing3=10, spacing1=5)
        self.log_text.tag_configure("system", lmargin1=10, lmargin2=10, rmargin=10, spacing3=10, spacing1=5)
        
        # 创建控制面板
        control_frame = ttk.Frame(main_container, padding="0", style='Control.TFrame')
        control_frame.pack(fill=tk.X, pady=(0, 0))
        
        # 文本输入框
        input_frame = ttk.Frame(control_frame, style='Control.TFrame')
        input_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # 创建输入框
        self.input_entry = ttk.Entry(input_frame, style='Modern.TEntry', width=70)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=0, pady=0)
        self.input_entry.bind("<Return>", self.on_input_submit)
        
        # 创建发送按钮
        send_btn = ttk.Button(input_frame, text="发送", command=self.on_input_submit, style='Send.TButton')
        send_btn.pack(side=tk.RIGHT, padx=(8, 0), pady=0, ipadx=10)
        
        # 控制按钮
        button_frame = ttk.Frame(control_frame, style='Control.TFrame')
        button_frame.pack(fill=tk.X, padx=0, pady=(10, 0))
        
        # 创建不同样式的按钮
        self.start_btn = ttk.Button(button_frame, text="🎤 开始语音交互", command=self.toggle_voice, style='Primary.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8), pady=0)
        
        clear_btn = ttk.Button(button_frame, text="🗑️ 清空日志", command=self.clear_log, style='Secondary.TButton')
        clear_btn.pack(side=tk.LEFT, padx=(0, 8), pady=0)
        
        # 快捷功能按钮
        weather_btn = ttk.Button(button_frame, text="🌤️ 天气", command=lambda: self.quick_command("今天天气怎么样"), style='Secondary.TButton')
        weather_btn.pack(side=tk.LEFT, padx=(0, 8), pady=0)
        
        joke_btn = ttk.Button(button_frame, text="😄 笑话", command=lambda: self.quick_command("讲个笑话"), style='Secondary.TButton')
        joke_btn.pack(side=tk.LEFT, padx=(0, 8), pady=0)
        
        news_btn = ttk.Button(button_frame, text="📰 新闻", command=lambda: self.quick_command("今日新闻"), style='Secondary.TButton')
        news_btn.pack(side=tk.LEFT, padx=(0, 8), pady=0)
        
        exit_btn = ttk.Button(button_frame, text="❌ 退出", command=self.on_exit, style='Danger.TButton')
        exit_btn.pack(side=tk.RIGHT, pady=0)
    
    def quick_command(self, command):
        """快捷命令"""
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, command)
        self.on_input_submit()
    
    def init_assistant(self):
        """初始化语音助手"""
        try:
            self.log_message("正在初始化语音助手...")
            
            # 导入并初始化对话管理器和API集成器
            from src.dialogue_manager.dialogue_manager import DialogueManager
            from src.api_integration.api_integrator import APIIntegrator
            
            self.dialogue_manager = DialogueManager()
            self.api_integrator = APIIntegrator()
            
            # 尝试初始化语音识别器
            self.speech_recognizer = None
            self.tts_engine = None
            voice_available = False
            
            try:
                from src.speech_recognition.speech_recognizer import SpeechRecognizer
                self.speech_recognizer = SpeechRecognizer()
                voice_available = True
                self.log_message("✅ 语音识别器初始化成功")
            except Exception as e:
                self.log_message(f"⚠️ 语音识别器初始化失败: {e}")
                self.log_message("   提示: pip install pyaudio speechrecognition")
            
            # 尝试初始化语音合成
            try:
                from src.tts.tts_engine import TTSEngine
                self.tts_engine = TTSEngine()
                self.log_message("✅ 语音合成器初始化成功")
            except Exception as e:
                self.log_message(f"⚠️ 语音合成器初始化失败: {e}")
            
            self.status_label.config(text="语音助手已初始化", foreground="green")
            self.log_message("语音助手初始化完成")
            self.log_message("")
            self.log_message("您好！我是小智，您的智能语音助手~")
            self.log_message("")
            self.log_message("📝 使用说明：")
            self.log_message("  • 文本输入：在下方输入框中输入文字，按回车发送")
            if voice_available:
                self.log_message("  • 语音交互：点击'🎤 开始语音交互'按钮进行语音对话")
            else:
                self.log_message("  • 语音交互：需要安装 pyaudio 才能使用")
            self.log_message("  • 快捷功能：点击天气、笑话、新闻按钮快速查询")
            
        except Exception as e:
            self.log_message(f"语音助手初始化失败: {e}")
            logger.error(f"语音助手初始化失败: {e}")
            import traceback
            traceback.print_exc()
    
    def log_message(self, message):
        """记录消息到日志框"""
        self.log_text.config(state=tk.NORMAL)
        
        # 添加时间戳
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 添加换行
        self.log_text.insert(tk.END, "\n", "system")
        
        # 根据消息类型设置不同样式和气泡效果
        if message.startswith("用户:") or message.startswith("用户(语音):"):
            # 提取消息内容
            content = message[3:].strip() if message.startswith("用户:") else message[6:].strip()
            
            # 添加时间戳
            self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # 添加用户标签
            self.log_text.insert(tk.END, "用户: ", "user")
            
            # 插入消息内容，应用气泡样式
            self.log_text.insert(tk.END, content + "\n", "user")
            
            # 获取当前插入位置
            pos = self.log_text.index(tk.END + "-2c linestart")
            line_end = self.log_text.index(tk.END + "-2c")
            
            # 应用气泡背景
            self.log_text.tag_add("user_bubble", pos, line_end)
            
            # 设置右对齐
            self.log_text.tag_configure("user", justify='right')
        
        elif message.startswith("助手:"):
            # 提取消息内容
            content = message[3:].strip()
            
            # 添加时间戳
            self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # 添加助手标签
            self.log_text.insert(tk.END, "助手: ", "assistant")
            
            # 插入消息内容，应用气泡样式
            self.log_text.insert(tk.END, content + "\n", "assistant")
            
            # 获取当前插入位置
            pos = self.log_text.index(tk.END + "-2c linestart")
            line_end = self.log_text.index(tk.END + "-2c")
            
            # 应用气泡背景
            self.log_text.tag_add("assistant_bubble", pos, line_end)
            
            # 设置左对齐
            self.log_text.tag_configure("assistant", justify='left')
        
        else:
            # 系统消息
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n", "system")
            
            # 获取当前插入位置
            pos = self.log_text.index(tk.END + "-2c linestart")
            line_end = self.log_text.index(tk.END + "-2c")
            
            # 应用气泡背景
            self.log_text.tag_add("system_bubble", pos, line_end)
            
            # 设置左对齐
            self.log_text.tag_configure("system", justify='left')
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def on_input_submit(self, event=None):
        """处理文本输入提交"""
        input_text = self.input_entry.get().strip()
        if not input_text:
            return
        
        self.log_message(f"用户: {input_text}")
        self.input_entry.delete(0, tk.END)
        
        try:
            self.status_label.config(text="正在处理...", foreground="#3498db")
            
            # 使用真正的对话管理器生成响应
            if hasattr(self, 'dialogue_manager') and self.dialogue_manager and hasattr(self, 'api_integrator') and self.api_integrator:
                response = self.dialogue_manager.generate_response(input_text, self.api_integrator)
            else:
                # 如果组件未初始化成功，使用模拟响应
                response = "抱歉，语音助手组件未完全初始化，无法处理请求。"
            
            self.log_message(f"助手: {response}")
            logger.info(f"用户输入: {input_text}, 助手响应: {response}")
            self.status_label.config(text="语音助手已初始化", foreground="green")
        except Exception as e:
            self.log_message(f"助手: 处理请求时出错")
            logger.error(f"处理用户输入时出错: {e}")
            import traceback
            traceback.print_exc()
            self.status_label.config(text="语音助手已初始化", foreground="green")
    
    def toggle_voice(self):
        """切换语音交互模式"""
        if self.is_running:
            # 停止语音交互
            self.is_running = False
            if hasattr(self, 'speech_recognizer') and self.speech_recognizer:
                self.speech_recognizer.stop_continuous_listening()
            self.start_btn.config(text="🎤 开始语音交互")
            self.status_label.config(text="语音交互已停止", foreground="orange")
            self.log_message("语音交互已停止")
        else:
            # 开始语音交互
            self.is_running = True
            self.start_btn.config(text="⏹️ 停止语音交互")
            self.status_label.config(text="语音交互中...", foreground="blue")
            self.log_message("开始语音交互，请说话...")
            
            # 启动语音识别线程
            import threading
            thread = threading.Thread(target=self.run_voice_recognition)
            thread.daemon = True
            thread.start()
    
    def run_voice_recognition(self):
        """运行语音识别"""
        try:
            # 尝试初始化语音识别器
            if not hasattr(self, 'speech_recognizer') or self.speech_recognizer is None:
                try:
                    from src.speech_recognition.speech_recognizer import SpeechRecognizer
                    self.speech_recognizer = SpeechRecognizer()
                    self.root.after(0, lambda: self.log_message("语音识别器初始化成功"))
                except Exception as e:
                    self.root.after(0, lambda: self.log_message(f"语音识别器初始化失败: {e}"))
                    self.root.after(0, lambda: self.log_message("请确保已安装 pyaudio 和 speechrecognition"))
                    self.root.after(0, lambda: self.log_message("安装命令: pip install pyaudio speechrecognition"))
                    self.root.after(0, self._stop_voice)
                    return
            
            # 持续监听
            while self.is_running:
                try:
                    self.root.after(0, lambda: self.status_label.config(text="🎤 正在监听...", foreground="blue"))
                    
                    # 识别语音
                    text = self.speech_recognizer.recognize(timeout=5, phrase_time_limit=10)
                    
                    if text and self.is_running:
                        # 在主线程中更新UI
                        self.root.after(0, lambda t=text: self._process_voice_input(t))
                        
                except Exception as e:
                    if self.is_running:
                        logger.error(f"语音识别错误: {e}")
                    import time
                    time.sleep(0.5)
                    
        except Exception as e:
            self.root.after(0, lambda: self.log_message(f"语音识别出错: {e}"))
            self.root.after(0, self._stop_voice)
    
    def _process_voice_input(self, text):
        """处理语音输入"""
        self.log_message(f"用户(语音): {text}")
        
        try:
            self.status_label.config(text="正在处理...", foreground="#3498db")
            
            if hasattr(self, 'dialogue_manager') and self.dialogue_manager:
                response = self.dialogue_manager.generate_response(text, self.api_integrator)
            else:
                response = "抱歉，语音助手组件未初始化"
            
            self.log_message(f"助手: {response}")
            
            # 语音播报响应
            self._speak_response(response)
            
            self.status_label.config(text="🎤 正在监听...", foreground="blue")
            
        except Exception as e:
            self.log_message(f"处理语音输入出错: {e}")
            logger.error(f"处理语音输入出错: {e}")
    
    def _speak_response(self, text):
        """语音播报响应"""
        try:
            if not hasattr(self, 'tts_engine') or self.tts_engine is None:
                try:
                    from src.tts.tts_engine import TTSEngine
                    self.tts_engine = TTSEngine()
                except Exception:
                    # TTS不可用，静默处理
                    return
            
            # 在后台线程中播报
            import threading
            def speak():
                try:
                    self.tts_engine.speak(text)
                except Exception:
                    pass
            
            thread = threading.Thread(target=speak)
            thread.daemon = True
            thread.start()
        except Exception:
            pass
    
    def _stop_voice(self):
        """停止语音交互"""
        self.is_running = False
        self.start_btn.config(text="🎤 开始语音交互")
        self.status_label.config(text="语音交互已停止", foreground="orange")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def on_exit(self):
        """处理退出"""
        self.is_running = False
        self.log_message("程序即将退出，感谢使用！")
        # 延迟关闭，让用户看到最后一条消息
        self.root.after(1000, self.root.destroy)
    
    def update_time(self):
        """更新时间显示"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        # 每秒更新一次
        self.root.after(1000, self.update_time)

def main():
    """主函数"""
    import sys
    import traceback
    logger.info("启动语音助手GUI")
    print("开始启动GUI...")
    try:
        root = tk.Tk()
        
        # 设置文本样式
        app = VoiceAssistantGUI(root)
        
        print("GUI初始化成功，开始运行...")
        root.mainloop()
    except Exception as e:
        logger.error(f"GUI启动失败: {e}")
        print(f"GUI启动失败: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
