#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小智语音助手 - 移动端应用
基于Kivy/KivyMD，支持Android平台
"""

__version__ = "2.0.0"

import os
import sys
import logging

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
from kivy.metrics import dp
from kivy.properties import StringProperty

# 尝试导入KivyMD
try:
    from kivymd.app import MDApp
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.label import MDLabel
    from kivymd.uix.button import MDRaisedButton, MDIconButton
    from kivymd.uix.textfield import MDTextField
    from kivymd.uix.card import MDCard
    from kivymd.uix.toolbar import MDTopAppBar
    USE_KIVYMD = True
except ImportError:
    USE_KIVYMD = False
    print("KivyMD未安装，使用基础Kivy界面")

# 设置窗口大小（仅在桌面端有效）
Window.size = (400, 700)

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# KivyMD布局
KV_MD = '''
MDBoxLayout:
    orientation: 'vertical'
    
    MDTopAppBar:
        title: "小智语音助手"
        elevation: 4
        left_action_items: [["robot", lambda x: None]]
        right_action_items: [["cog", lambda x: app.show_settings()]]
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        # 状态标签
        MDLabel:
            id: status_label
            text: "正在初始化..."
            halign: 'center'
            size_hint_y: None
            height: dp(30)
            theme_text_color: "Secondary"
        
        # 聊天区域
        ScrollView:
            id: scroll_view
            size_hint_y: 1
            do_scroll_x: False
            
            MDBoxLayout:
                id: chat_layout
                orientation: 'vertical'
                spacing: dp(8)
                padding: dp(5)
                size_hint_y: None
                height: self.minimum_height
        
        # 输入区域
        MDBoxLayout:
            orientation: 'horizontal'
            spacing: dp(8)
            size_hint_y: None
            height: dp(56)
            
            MDTextField:
                id: input_field
                hint_text: "输入您的问题..."
                mode: "rectangle"
                size_hint_x: 0.75
                on_text_validate: app.send_message()
            
            MDRaisedButton:
                text: "发送"
                size_hint_x: 0.25
                on_release: app.send_message()
        
        # 语音按钮
        MDRaisedButton:
            id: voice_btn
            text: "🎤 按住说话"
            size_hint_y: None
            height: dp(50)
            md_bg_color: app.theme_cls.primary_color
            on_press: app.start_voice()
            on_release: app.stop_voice()
'''

# 基础Kivy布局（不使用KivyMD时）
KV_BASIC = '''
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
        text: "正在初始化..."
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
    
    Button:
        id: voice_btn
        text: "🎤 按住说话"
        size_hint_y: None
        height: 50
        on_press: app.start_voice()
        on_release: app.stop_voice()
'''


class MessageBubble(BoxLayout):
    """消息气泡组件"""
    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = [10, 5]
        
        # 创建标签
        label = Label(
            text=text,
            text_size=(Window.width * 0.7, None),
            size_hint=(None, None),
            halign='left' if not is_user else 'right',
            valign='middle',
            markup=True
        )
        label.bind(texture_size=label.setter('size'))
        
        # 设置背景色
        if is_user:
            label.color = (1, 1, 1, 1)
            self.canvas.before.clear()
            with self.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(0.2, 0.6, 1, 1)
        else:
            label.color = (0.2, 0.2, 0.2, 1)
        
        # 添加间距
        if is_user:
            self.add_widget(BoxLayout(size_hint_x=0.2))
            self.add_widget(label)
        else:
            self.add_widget(label)
            self.add_widget(BoxLayout(size_hint_x=0.2))
        
        self.height = label.height + 20


class VoiceAssistantApp(MDApp if USE_KIVYMD else App):
    """语音助手移动应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dialogue_manager = None
        self.api_integrator = None
        self.is_initialized = False
        self.is_recording = False
        
    def build(self):
        """构建应用界面"""
        if USE_KIVYMD:
            self.theme_cls.primary_palette = "Blue"
            self.theme_cls.theme_style = "Light"
            self.root = Builder.load_string(KV_MD)
        else:
            self.root = Builder.load_string(KV_BASIC)
        
        # 延迟初始化
        Clock.schedule_once(self.initialize_assistant, 0.5)
        
        return self.root
    
    def initialize_assistant(self, dt):
        """初始化语音助手"""
        try:
            self.update_status("正在初始化...")
            self.add_message("正在加载语音助手模块...", is_user=False)
            
            # 导入对话管理器和API集成器
            from src.dialogue_manager.dialogue_manager import DialogueManager
            from src.api_integration.api_integrator import APIIntegrator
            
            self.dialogue_manager = DialogueManager()
            self.api_integrator = APIIntegrator()
            self.is_initialized = True
            
            self.update_status("已就绪")
            self.add_message("你好！我是小智，您的智能语音助手~", is_user=False)
            self.add_message("您可以问我天气、时间、新闻，或让我讲笑话、讲故事等", is_user=False)
            
            logger.info("语音助手初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            self.update_status("初始化失败")
            self.add_message(f"初始化失败: {str(e)}", is_user=False)
            import traceback
            traceback.print_exc()
    
    def update_status(self, text):
        """更新状态标签"""
        if hasattr(self.root, 'ids') and 'status_label' in self.root.ids:
            self.root.ids.status_label.text = text
    
    def add_message(self, text, is_user=False):
        """添加消息到聊天界面"""
        chat_layout = self.root.ids.chat_layout
        
        if USE_KIVYMD:
            # 使用MDCard作为消息气泡
            card = MDCard(
                orientation='vertical',
                size_hint=(0.8, None),
                padding=dp(10),
                radius=[dp(10)],
                elevation=1
            )
            
            if is_user:
                card.md_bg_color = (0.2, 0.6, 1, 1)
                card.pos_hint = {'right': 1}
                text_color = (1, 1, 1, 1)
            else:
                card.md_bg_color = (0.95, 0.95, 0.95, 1)
                card.pos_hint = {'left': 1}
                text_color = (0.2, 0.2, 0.2, 1)
            
            label = MDLabel(
                text=text,
                size_hint_y=None,
                theme_text_color="Custom",
                text_color=text_color
            )
            label.bind(texture_size=lambda *x: setattr(label, 'height', label.texture_size[1]))
            card.add_widget(label)
            card.bind(minimum_height=card.setter('height'))
            
            chat_layout.add_widget(card)
        else:
            # 使用基础消息气泡
            bubble = MessageBubble(text, is_user=is_user)
            chat_layout.add_widget(bubble)
        
        # 滚动到底部
        Clock.schedule_once(self.scroll_to_bottom, 0.1)
    
    def scroll_to_bottom(self, dt):
        """滚动到底部"""
        self.root.ids.scroll_view.scroll_y = 0
    
    def send_message(self):
        """发送消息"""
        input_field = self.root.ids.input_field
        text = input_field.text.strip()
        
        if not text:
            return
        
        # 显示用户消息
        self.add_message(text, is_user=True)
        input_field.text = ''
        
        # 处理消息
        if self.is_initialized:
            self.update_status("正在思考...")
            Clock.schedule_once(lambda dt: self.process_message(text), 0.1)
        else:
            self.add_message("助手正在初始化，请稍候...", is_user=False)
    
    def process_message(self, text):
        """处理用户消息"""
        try:
            response = self.dialogue_manager.generate_response(text, self.api_integrator)
            self.add_message(response, is_user=False)
            self.update_status("已就绪")
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            self.add_message(f"处理失败: {str(e)}", is_user=False)
            self.update_status("已就绪")
    
    def start_voice(self):
        """开始语音识别"""
        if not self.is_initialized:
            self.add_message("助手正在初始化，请稍候...", is_user=False)
            return
        
        self.is_recording = True
        self.update_status("🎤 正在聆听...")
        self.root.ids.voice_btn.text = "🔴 松开结束"
        
        # 在Android上使用原生语音识别
        try:
            from plyer import stt
            stt.start()
        except Exception as e:
            logger.info(f"语音识别启动: {e}")
    
    def stop_voice(self):
        """停止语音识别"""
        if not self.is_recording:
            return
        
        self.is_recording = False
        self.root.ids.voice_btn.text = "🎤 按住说话"
        self.update_status("正在识别...")
        
        try:
            from plyer import stt
            stt.stop()
            # 获取识别结果
            result = stt.result
            if result:
                self.add_message(result, is_user=True)
                self.process_message(result)
            else:
                self.update_status("未识别到语音")
        except Exception as e:
            logger.info(f"语音识别: {e}")
            self.update_status("已就绪")
            # 模拟提示
            self.add_message("语音识别功能需要在Android设备上使用", is_user=False)
    
    def show_settings(self):
        """显示设置"""
        self.add_message("设置功能开发中...", is_user=False)


def main():
    """主函数"""
    try:
        app = VoiceAssistantApp()
        app.run()
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
