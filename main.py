#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小智语音助手 - Android 简化版
专为移动端优化，减少依赖
"""

import os
import sys
import logging
import random
from datetime import datetime

# 设置环境变量
os.environ['KIVY_LOG_LEVEL'] = 'info'

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.core.text import LabelBase

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 注册中文字体（Android 系统字体路径）
FONT_PATHS = [
    '/system/fonts/NotoSansCJK-Regular.ttc',
    '/system/fonts/DroidSansFallback.ttf',
    '/system/fonts/NotoSansSC-Regular.otf',
    '/system/fonts/Roboto-Regular.ttf',
]

CHINESE_FONT = None
for font_path in FONT_PATHS:
    if os.path.exists(font_path):
        try:
            LabelBase.register(name='ChineseFont', fn_regular=font_path)
            CHINESE_FONT = 'ChineseFont'
            logger.info(f"使用字体: {font_path}")
            break
        except Exception as e:
            logger.warning(f"字体注册失败 {font_path}: {e}")

# 如果没找到中文字体，使用默认
if not CHINESE_FONT:
    CHINESE_FONT = 'Roboto'
    logger.warning("未找到中文字体，使用默认字体")

# Kivy 布局 - 使用中文字体
KV = f'''
#:set chinese_font "{CHINESE_FONT}"

BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    canvas.before:
        Color:
            rgba: 0.95, 0.95, 0.95, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    Label:
        text: "Xiaozhi Assistant"
        font_name: chinese_font
        size_hint_y: None
        height: 50
        font_size: 22
        color: 0.2, 0.2, 0.2, 1
    
    Label:
        id: status_label
        text: "Ready"
        font_name: chinese_font
        size_hint_y: None
        height: 25
        font_size: 14
        color: 0.5, 0.5, 0.5, 1
    
    ScrollView:
        id: scroll_view
        size_hint_y: 1
        
        BoxLayout:
            id: chat_layout
            orientation: 'vertical'
            spacing: 8
            padding: 5
            size_hint_y: None
            height: self.minimum_height
    
    BoxLayout:
        orientation: 'horizontal'
        spacing: 8
        size_hint_y: None
        height: 50
        
        TextInput:
            id: input_field
            hint_text: "Type here..."
            font_name: chinese_font
            multiline: False
            size_hint_x: 0.75
            font_size: 16
            on_text_validate: app.send_message()
        
        Button:
            text: "Send"
            font_name: chinese_font
            size_hint_x: 0.25
            font_size: 16
            background_color: 0.2, 0.6, 1, 1
            on_release: app.send_message()
'''


class SimpleAssistant:
    """Simple chat assistant"""
    
    def __init__(self):
        pass
    
    def get_response(self, text):
        text = text.lower().strip()
        
        # Greetings
        if any(w in text for w in ['hi', 'hello', 'hey']):
            return "Hello! I'm Xiaozhi. How can I help you?"
        
        # Time
        if any(w in text for w in ['time', 'clock', 'hour']):
            now = datetime.now()
            return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Date
        if any(w in text for w in ['date', 'today', 'day']):
            now = datetime.now()
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return f"Today is {now.strftime('%Y-%m-%d')} {weekdays[now.weekday()]}"
        
        # Joke
        if any(w in text for w in ['joke', 'funny', 'laugh']):
            jokes = [
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "There are only 10 types of people: those who understand binary and those who don't.",
                "A SQL query walks into a bar, walks up to two tables and asks: Can I join you?",
            ]
            return random.choice(jokes)
        
        # Help
        if any(w in text for w in ['help', 'what can you do', 'feature']):
            return "I can:\n- Tell you time and date\n- Tell jokes\n- Chat with you\n\nTry: 'what time is it' or 'tell me a joke'"
        
        # Thanks
        if any(w in text for w in ['thank', 'thanks']):
            return "You're welcome!"
        
        # Bye
        if any(w in text for w in ['bye', 'goodbye', 'see you']):
            return "Goodbye! See you next time!"
        
        # Default
        return f"I heard: {text[:30]}...\nTry asking 'what time is it' or 'tell me a joke'"


class MessageBubble(BoxLayout):
    """Message bubble widget"""
    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.padding = [10, 5]
        
        label = Label(
            text=text,
            font_name=CHINESE_FONT,
            text_size=(Window.width * 0.65, None),
            size_hint=(0.8, None),
            halign='left' if not is_user else 'right',
            valign='middle',
            font_size=15,
        )
        label.bind(texture_size=lambda *x: setattr(label, 'height', max(40, label.texture_size[1] + 20)))
        label.bind(height=lambda *x: setattr(self, 'height', label.height + 10))
        
        if is_user:
            label.color = (0.2, 0.5, 0.9, 1)
            self.add_widget(BoxLayout(size_hint_x=0.2))
            self.add_widget(label)
        else:
            label.color = (0.2, 0.2, 0.2, 1)
            self.add_widget(label)
            self.add_widget(BoxLayout(size_hint_x=0.2))


class XiaozhiApp(App):
    """Xiaozhi Voice Assistant App"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.assistant = SimpleAssistant()
    
    def build(self):
        self.title = "Xiaozhi Assistant"
        self.root = Builder.load_string(KV)
        Clock.schedule_once(self.show_welcome, 0.5)
        return self.root
    
    def show_welcome(self, dt):
        self.add_message("Hello! I'm Xiaozhi, your assistant.", is_user=False)
        self.add_message("Try: 'what time is it' or 'tell me a joke'", is_user=False)
    
    def add_message(self, text, is_user=False):
        chat_layout = self.root.ids.chat_layout
        bubble = MessageBubble(text, is_user=is_user)
        chat_layout.add_widget(bubble)
        Clock.schedule_once(lambda dt: setattr(self.root.ids.scroll_view, 'scroll_y', 0), 0.1)
    
    def send_message(self):
        input_field = self.root.ids.input_field
        text = input_field.text.strip()
        
        if not text:
            return
        
        self.add_message(text, is_user=True)
        input_field.text = ''
        
        response = self.assistant.get_response(text)
        Clock.schedule_once(lambda dt: self.add_message(response, is_user=False), 0.3)


if __name__ == '__main__':
    XiaozhiApp().run()
