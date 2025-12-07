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

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 简化版 Kivy 布局
KV = '''
BoxLayout:
    orientation: 'vertical'
    padding: 10
    spacing: 10
    
    Label:
        text: "小智语音助手"
        size_hint_y: None
        height: 50
        font_size: 24
        bold: True
    
    Label:
        id: status_label
        text: "已就绪"
        size_hint_y: None
        height: 30
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
            hint_text: "输入您的问题..."
            multiline: False
            size_hint_x: 0.75
            on_text_validate: app.send_message()
        
        Button:
            text: "发送"
            size_hint_x: 0.25
            on_release: app.send_message()
'''


class SimpleAssistant:
    """简化版对话助手 - 无外部依赖"""
    
    def __init__(self):
        self.greetings = ["你好！", "您好！", "嗨！", "很高兴见到你！"]
        self.jokes = [
            "为什么程序员总是分不清万圣节和圣诞节？因为 Oct 31 = Dec 25",
            "程序员最讨厌什么？别人说他的代码有bug，更讨厌别人说他的代码没有bug",
            "世界上最遥远的距离不是生与死，而是你写的代码在我电脑上跑不起来",
            "为什么程序员喜欢黑暗模式？因为光明会吸引bug",
        ]
        self.stories = [
            "从前有座山，山里有座庙，庙里有个老和尚在给小和尚讲故事...",
            "很久很久以前，有一个勤劳的农夫，他每天都辛勤地耕作...",
        ]
    
    def get_response(self, text):
        """根据用户输入生成回复"""
        text = text.lower().strip()
        
        # 问候
        if any(w in text for w in ['你好', '您好', '嗨', 'hi', 'hello']):
            return random.choice(self.greetings) + "我是小智，有什么可以帮你的吗？"
        
        # 时间
        if any(w in text for w in ['时间', '几点', '现在']):
            now = datetime.now()
            return f"现在是 {now.strftime('%Y年%m月%d日 %H:%M:%S')}"
        
        # 日期
        if any(w in text for w in ['日期', '今天', '星期']):
            now = datetime.now()
            weekdays = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
            return f"今天是 {now.strftime('%Y年%m月%d日')} {weekdays[now.weekday()]}"
        
        # 笑话
        if any(w in text for w in ['笑话', '搞笑', '开心']):
            return random.choice(self.jokes)
        
        # 故事
        if any(w in text for w in ['故事', '讲个']):
            return random.choice(self.stories)
        
        # 天气（简化回复）
        if any(w in text for w in ['天气', '温度', '下雨']):
            return "抱歉，天气查询功能需要网络支持。请确保网络连接正常后重试。"
        
        # 帮助
        if any(w in text for w in ['帮助', '功能', '能做什么', 'help']):
            return "我可以：\n• 告诉你时间和日期\n• 讲笑话\n• 讲故事\n• 和你聊天"
        
        # 感谢
        if any(w in text for w in ['谢谢', '感谢', 'thanks']):
            return "不客气！很高兴能帮到你~"
        
        # 再见
        if any(w in text for w in ['再见', '拜拜', 'bye']):
            return "再见！期待下次和你聊天~"
        
        # 默认回复
        defaults = [
            "我理解你说的是：" + text[:20] + "...\n你可以问我时间、让我讲笑话或故事哦~",
            "嗯，我在听。你可以试试问我'现在几点'或者'讲个笑话'",
            "有什么我可以帮你的吗？试试说'帮助'看看我能做什么~",
        ]
        return random.choice(defaults)


class MessageBubble(BoxLayout):
    """消息气泡"""
    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 60
        self.padding = [10, 5]
        
        label = Label(
            text=text,
            text_size=(Window.width * 0.7, None),
            size_hint=(0.8, None),
            halign='left' if not is_user else 'right',
            valign='middle',
        )
        label.bind(texture_size=lambda *x: setattr(label, 'height', max(40, label.texture_size[1] + 20)))
        label.bind(height=lambda *x: setattr(self, 'height', label.height + 10))
        
        if is_user:
            label.color = (0.2, 0.6, 1, 1)
            self.add_widget(BoxLayout(size_hint_x=0.2))
            self.add_widget(label)
        else:
            label.color = (0.3, 0.3, 0.3, 1)
            self.add_widget(label)
            self.add_widget(BoxLayout(size_hint_x=0.2))


class XiaozhiApp(App):
    """小智语音助手 App"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.assistant = SimpleAssistant()
    
    def build(self):
        self.title = "小智语音助手"
        self.root = Builder.load_string(KV)
        Clock.schedule_once(self.show_welcome, 0.5)
        return self.root
    
    def show_welcome(self, dt):
        self.add_message("你好！我是小智，您的智能助手~", is_user=False)
        self.add_message("你可以问我时间、让我讲笑话，或者说'帮助'看看我能做什么", is_user=False)
    
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
        
        # 获取回复
        response = self.assistant.get_response(text)
        Clock.schedule_once(lambda dt: self.add_message(response, is_user=False), 0.3)


if __name__ == '__main__':
    XiaozhiApp().run()
