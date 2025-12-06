# 语音助手配置文件

# 语音识别配置
class SpeechRecognitionConfig:
    # 使用的语音识别引擎："google" 或 "baidu"
    ENGINE = "google"
    
    # 百度语音识别API配置（如果使用百度引擎）
    BAIDU_API_KEY = "your_baidu_api_key"
    BAIDU_SECRET_KEY = "your_baidu_secret_key"
    BAIDU_APP_ID = "your_baidu_app_id"
    
    # 语音识别语言
    LANGUAGE = "zh-CN"
    
    # 音频参数
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    
    # 唤醒词
    WAKE_UP_WORDS = ["小爱同学", "小助手", "语音助手"]

# 自然语言处理配置
class NLPConfig:
    # 分词工具："jieba" 或 "spacy"
    SEGMENTER = "jieba"
    
    # spaCy模型路径（如果使用spacy）
    SPACY_MODEL = "zh_core_web_sm"
    
    # 意图识别模型路径
    INTENT_MODEL_PATH = "models/intent_model.pkl"
    
    # 实体识别模型路径
    ENTITY_MODEL_PATH = "models/entity_model.pkl"

# 语音合成配置
class TTSConfig:
    # 使用的语音合成引擎："pyttsx3" 或 "baidu"
    ENGINE = "pyttsx3"
    
    # 百度语音合成API配置（如果使用百度引擎）
    BAIDU_API_KEY = "your_baidu_api_key"
    BAIDU_SECRET_KEY = "your_baidu_secret_key"
    
    # 语音合成参数
    VOICE_RATE = 150  # 语速
    VOICE_VOLUME = 1.0  # 音量 (0.0-1.0)
    VOICE_ID = 0  # 语音ID（不同引擎有不同的语音选择）

# 对话管理配置
class DialogueManagerConfig:
    # 对话历史保存路径
    HISTORY_PATH = "data/dialogue_history.db"
    
    # 最大对话历史长度
    MAX_HISTORY_LENGTH = 10
    
    # 默认回复
    DEFAULT_RESPONSES = [
        "抱歉，我不太理解您的意思。",
        "能请您再说一遍吗？",
        "我还在学习中，这个问题有点难倒我了。"
    ]

# API集成配置
class APIConfig:
    # 天气API配置
    WEATHER_API_KEY = "your_weather_api_key"
    WEATHER_API_URL = "https://devapi.qweather.com/v7/weather/now"
    WEATHER_BASE_URL = "https://devapi.qweather.com/v7/weather/now"
    
    # 新闻API配置
    NEWS_API_KEY = "your_news_api_key"
    NEWS_API_URL = "https://api.baidu.com/news"
    NEWS_BASE_URL = "https://api.baidu.com/news"
    
    # 翻译API配置
    TRANSLATION_API_KEY = "your_translation_api_key"
    
    # 地图API配置
    MAP_API_KEY = "your_map_api_key"
    MAP_API_URL = "https://restapi.amap.com/v3/geocode/geo"
    
    # 请求配置
    REQUEST_TIMEOUT = 10

# 安全配置
class SecurityConfig:
    # 数据加密配置
    ENCRYPTION_KEY = "your_secure_encryption_key_here"  # 生产环境需替换为强密钥
    
    # 隐私保护配置
    ENCRYPT_USER_DATA = True  # 是否加密存储用户数据
    OBFUSCATE_LOGS = True  # 是否模糊处理日志中的敏感信息
    
    # 对话历史保留策略
    RETAIN_HISTORY_DAYS = 30  # 对话历史保留天数
    
    # 权限控制
    REQUIRE_CONFIRMATION_FOR_SENSITIVE_OPS = True  # 敏感操作是否需要确认
    SENSITIVE_OPERATIONS = ["delete", "format", "shutdown", "restart"]  # 敏感操作列表

# 全局配置
class GlobalConfig:
    # 项目根目录
    PROJECT_ROOT = "c:/Users/Ln/Documents/trae_projects/AI"
    
    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "data/assistant.log"
    
    # 调试模式
    DEBUG = True
