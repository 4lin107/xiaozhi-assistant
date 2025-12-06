# AI语音助手

一个功能强大的语音助手，可以实现语音识别、自然语言处理、联网搜索和本地操作等功能。

## 功能特点

### 1. 无需API的联网搜索
- **天气查询**：从中国天气网获取实时天气信息
- **新闻获取**：从新浪新闻获取最新资讯
- **地图搜索**：生成百度地图搜索链接
- **互联网搜索**：使用Bing搜索引擎获取信息

### 2. 本地操作功能
- **打开文件夹**：如"打开文档文件夹"
- **打开应用程序**：如"打开记事本"
- **运行命令**：执行简单的系统命令
- **列出文件**：查看指定目录的文件列表

### 3. 核心功能
- **语音识别**：将语音转换为文本
- **自然语言处理**：意图识别和实体提取
- **对话管理**：理解用户意图并生成响应
- **语音合成**：将文本转换为语音

## 安装依赖

```bash
pip install requests beautifulsoup4 jieba pyaudio speechrecognition pyttsx3 pillow
```

## 使用方法

### 运行主程序

```bash
python src/main.py
```

### 测试GUI界面

```bash
python test_gui.py
```

## 支持的命令示例

### 天气查询
- "北京的天气怎么样？"
- "上海明天会下雨吗？"

### 新闻获取
- "给我讲一下今天的新闻"
- "最新的新闻是什么？"

### 地图搜索
- "搜索天安门"
- "给我找一下附近的餐厅"

### 本地操作
- "打开文档文件夹"
- "打开记事本"
- "运行cmd"
- "列出当前目录的文件"

## 项目结构

```
AI/
├── src/
│   ├── api_integration/      # API集成和网络爬虫
│   │   ├── api_integrator.py
│   │   ├── local_operations.py
│   │   └── web_crawler.py
│   ├── dialogue_manager/     # 对话管理
│   │   └── dialogue_manager.py
│   ├── nlp/                  # 自然语言处理
│   │   └── nlp_processor.py
│   ├── speech_recognition/   # 语音识别
│   │   └── speech_recognizer.py
│   ├── tts/                  # 语音合成
│   │   └── tts_engine.py
│   ├── ui/                   # 用户界面
│   │   └── simple_gui.py
│   └── main.py               # 主程序
├── config/                   # 配置文件
│   └── config.py
├── test_gui.py               # GUI测试程序
└── README.md                 # 项目说明
```

## 开发说明

本项目使用了以下技术：
- **Python 3.7+**：主要开发语言
- **Requests**：HTTP请求
- **BeautifulSoup4**：网页解析
- **jieba**：中文分词
- **SpeechRecognition**：语音识别
- **pyttsx3**：语音合成
- **Tkinter**：GUI界面

## 注意事项

1. 网络爬虫功能依赖于第三方网站的结构，如网站结构变化可能导致功能失效
2. 本地操作功能需要适当的系统权限
3. 语音识别和合成功能可能需要麦克风和扬声器

## 更新日志

### v1.0.0
- 实现基本的语音助手功能
- 添加无需API的联网搜索
- 支持本地文件和应用操作

## 许可证

MIT License
