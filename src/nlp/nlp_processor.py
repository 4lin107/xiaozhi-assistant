#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自然语言处理模块 - 增强版
支持更智能的意图识别、实体提取、情感分析和上下文理解
"""

import os
import sys
import re
import logging
import jieba
import jieba.posseg as pseg
from collections import OrderedDict
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import NLPConfig

logger = logging.getLogger(__name__)


class NLPProcessor:
    """增强版NLP处理器类"""

    def __init__(self):
        """初始化NLP处理器"""
        self.config = NLPConfig
        self._initialize_jieba()
        self._initialize_intent_rules()
        self._initialize_entity_types()
        self._initialize_synonyms()
        self._initialize_ml_models()

        # 停用词
        self.STOP_WORDS = set([
            "的", "了", "和", "是", "在", "我", "你", "他", "她", "它",
            "我们", "你们", "他们", "这个", "那个", "这里", "那里",
            "吧", "呢", "啊", "哦", "嗯", "呀", "哈", "吗", "么"
        ])

        # 情感词典
        self.POSITIVE_WORDS = set([
            "好", "棒", "优秀", "完美", "开心", "快乐", "喜欢", "满意", "厉害",
            "不错", "很好", "太好了", "真棒", "赞", "牛", "强", "爱", "感谢",
            "谢谢", "漂亮", "美丽", "帅", "酷", "精彩", "成功", "顺利"
        ])
        self.NEGATIVE_WORDS = set([
            "坏", "差", "糟糕", "讨厌", "难过", "悲伤", "不满意", "失败",
            "错误", "问题", "麻烦", "烦", "累", "困", "难", "慢", "卡",
            "崩溃", "无聊", "生气", "愤怒", "伤心", "痛苦"
        ])

        logger.info("增强版NLP处理器初始化成功")

    def _initialize_jieba(self):
        """初始化jieba分词"""
        try:
            # 添加自定义词汇
            custom_words = [
                "酷狗音乐", "网易云音乐", "QQ音乐", "哔哩哔哩", "腾讯视频",
                "爱奇艺", "优酷视频", "芒果TV", "微信", "支付宝", "淘宝",
                "京东", "拼多多", "美团", "饿了么", "滴滴出行", "高德地图",
                "百度地图", "腾讯地图", "钉钉", "飞书", "企业微信", "腾讯会议",
                "小红书", "抖音", "快手", "微博", "知乎", "豆瓣", "B站",
                "VSCode", "PyCharm", "Visual Studio", "记事本", "计算器",
                "控制面板", "任务管理器", "命令提示符", "PowerShell"
            ]
            for word in custom_words:
                jieba.add_word(word)

            # 加载自定义词典
            custom_dict_path = os.path.join(os.path.dirname(__file__), "custom_dict.txt")
            if os.path.exists(custom_dict_path):
                jieba.load_userdict(custom_dict_path)
        except Exception as e:
            logger.error(f"初始化jieba分词失败: {e}")

    def _initialize_intent_rules(self):
        """初始化意图识别规则"""
        self.INTENT_RULES = OrderedDict([
            # 最高优先级：明确的操作指令
            ("open_application", [
                r"打开\s*.+", r"启动\s*.+", r"运行\s*.+软件", r"开启\s*.+",
                r"帮我打开", r"请打开", r"能打开"
            ]),
            ("open_folder", [
                r"打开.*文件夹", r"打开桌面", r"打开文档", r"打开下载",
                r"打开图片", r"打开音乐", r"打开视频", r"查看.*目录"
            ]),

            # 高优先级：具体功能查询
            ("weather", [
                r"天气", r"气温", r"温度", r"下雨", r"下雪", r"晴天", r"阴天",
                r"多云", r"雾霾", r"空气质量", r"紫外线", r"穿什么", r"带伞"
            ]),
            ("time", [
                r"几点了", r"几点钟", r"现在时间", r"现在几点", r"报时",
                r"什么时候", r"多长时间"
            ]),
            ("date", [
                r"几号", r"星期几", r"什么日期", r"今天日期", r"农历",
                r"阳历", r"节日", r"放假"
            ]),
            ("alarm", [
                r"闹钟", r"提醒我", r"定时", r"倒计时", r"计时器",
                r".*点.*叫我", r".*分钟后.*提醒"
            ]),
            ("calculator", [
                r"计算", r"算一下", r"\d+\s*[+\-*/×÷]\s*\d+", r"等于多少",
                r"多少钱", r"汇率", r"换算", r"平方", r"开方", r"百分之"
            ]),
            ("translation", [
                r"翻译", r"怎么说", r"什么意思", r"英语", r"日语", r"韩语",
                r"法语", r"德语", r"俄语", r"西班牙语"
            ]),

            # 中优先级：信息查询
            ("news", [r"新闻", r"资讯", r"时事", r"头条", r"热点", r"热搜"]),
            ("stock", [r"股票", r"股价", r"大盘", r"涨跌", r"基金", r"理财"]),
            ("sports", [r"比分", r"比赛", r"球赛", r"足球", r"篮球", r"赛程"]),
            ("movie", [r"电影", r"影片", r"上映", r"票房", r"评分"]),
            ("music", [
                r"播放.*歌", r"听.*歌", r"放首歌", r"来首歌", r"播放音乐",
                r"唱.*歌", r"来一首"
            ]),
            ("video", [r"播放.*视频", r"看.*视频", r"放.*视频"]),

            # 搜索和导航
            ("search", [
                r"搜索", r"搜一下", r"查一下", r"百度", r"谷歌",
                r"帮我查", r"了解一下", r"是什么"
            ]),
            ("map", [
                r"地图", r"导航", r"怎么走", r"在哪里", r"路线", r"距离",
                r"多远", r"附近", r"周边"
            ]),

            # 系统控制
            ("volume", [
                r"音量", r"声音", r"大声", r"小声", r"静音",
                r"调高音量", r"调低音量", r"开声音", r"关声音"
            ]),
            ("brightness", [r"亮度", r"屏幕亮", r"调亮", r"调暗"]),
            ("wifi", [r"wifi", r"无线网", r"网络连接", r"断网"]),
            ("bluetooth", [r"蓝牙", r"连接设备", r"配对"]),
            ("screenshot", [r"截图", r"截屏", r"屏幕截图"]),
            ("system_info", [
                r"系统信息", r"电脑信息", r"内存", r"CPU", r"硬盘",
                r"电量", r"存储空间"
            ]),

            # 文件操作
            ("list_files", [r"列出文件", r"文件列表", r"显示文件", r"有什么文件"]),
            ("create_file", [r"创建文件", r"新建文件", r"写入文件"]),
            ("delete_file", [r"删除文件", r"移除文件"]),

            # 日常对话
            ("joke", [r"笑话", r"讲个笑话", r"说个笑话", r"逗我笑", r"开心一下"]),
            ("story", [r"讲故事", r"说故事", r"听故事"]),
            ("riddle", [r"猜谜", r"谜语", r"脑筋急转弯"]),
            ("poetry", [r"诗", r"古诗", r"诗词", r"念首诗"]),
            ("greeting", [
                r"你好", r"您好", r"嗨", r"哈喽", r"早上好", r"晚上好",
                r"下午好", r"早安", r"晚安", r"中午好"
            ]),
            ("farewell", [r"再见", r"拜拜", r"回见", r"下次见", r"晚安"]),
            ("thanks", [r"谢谢", r"感谢", r"多谢", r"辛苦了"]),
            ("praise", [r"厉害", r"真棒", r"不错", r"很好", r"太强了"]),
            ("name", [r"你叫什么", r"你是谁", r"你的名字", r"介绍.*自己"]),
            ("age", [r"你多大", r"你几岁", r"你的年龄"]),
            ("ability", [r"你能做什么", r"你会什么", r"有什么功能", r"帮助"]),
            ("mood", [r"你开心吗", r"你心情", r"你怎么样"]),
            ("creator", [r"谁创造", r"谁开发", r"谁做的", r"作者是谁"]),

            # 智能家居（预留）
            ("smart_home", [
                r"开灯", r"关灯", r"空调", r"电视", r"窗帘",
                r"扫地机器人", r"智能家居"
            ]),

            # 生活服务
            ("weather_dress", [r"穿什么", r"怎么穿", r"穿衣建议"]),
            ("food", [r"吃什么", r"美食", r"餐厅", r"外卖", r"菜谱", r"做法"]),
            ("health", [r"健康", r"养生", r"运动", r"减肥", r"睡眠"]),
            ("horoscope", [r"星座", r"运势", r"今日运势"]),

            # 退出
            ("exit", [r"退出", r"关闭助手", r"结束对话", r"停止"])
        ])


    def _initialize_entity_types(self):
        """初始化实体类型"""
        self.ENTITY_TYPES = {
            "city": [
                # 直辖市
                r"北京", r"上海", r"天津", r"重庆",
                # 省会城市
                r"广州", r"深圳", r"杭州", r"成都", r"西安", r"武汉", r"南京",
                r"郑州", r"长沙", r"沈阳", r"济南", r"南宁", r"福州", r"长春",
                r"哈尔滨", r"合肥", r"南昌", r"昆明", r"贵阳", r"太原", r"石家庄",
                r"兰州", r"乌鲁木齐", r"呼和浩特", r"西宁", r"银川", r"拉萨", r"海口",
                # 重要城市
                r"苏州", r"青岛", r"大连", r"宁波", r"厦门", r"三亚", r"东莞",
                r"佛山", r"无锡", r"温州", r"珠海", r"中山", r"惠州", r"烟台",
                r"常州", r"徐州", r"潍坊", r"绍兴", r"嘉兴", r"泉州", r"漳州",
                r"南通", r"扬州", r"镇江", r"盐城", r"连云港", r"淮安", r"泰州",
                r"桂林", r"柳州", r"北海", r"梧州", r"玉林", r"贵港", r"百色",
                # 特别行政区
                r"香港", r"澳门", r"台北", r"高雄", r"台中"
            ],
            "time_word": [
                r"今天", r"明天", r"后天", r"大后天", r"昨天", r"前天",
                r"上周", r"下周", r"本周", r"这周", r"本月", r"下月", r"上个月",
                r"今年", r"明年", r"去年", r"早上", r"上午", r"中午", r"下午",
                r"晚上", r"凌晨", r"傍晚", r"深夜", r"半夜",
                r"周一", r"周二", r"周三", r"周四", r"周五", r"周六", r"周日",
                r"星期一", r"星期二", r"星期三", r"星期四", r"星期五", r"星期六", r"星期日"
            ],
            "number": [r"\d+\.?\d*"],
            "duration": [
                r"\d+秒", r"\d+分钟", r"\d+小时", r"\d+天", r"\d+周",
                r"\d+个月", r"\d+年", r"半小时", r"一刻钟"
            ],
            "app_name": [
                # 系统工具
                r"记事本", r"计算器", r"画图", r"写字板", r"任务管理器",
                r"控制面板", r"资源管理器", r"截图工具", r"命令提示符",
                r"cmd", r"powershell", r"终端", r"设置",
                # 浏览器
                r"浏览器", r"Chrome", r"谷歌浏览器", r"Edge", r"微软浏览器",
                r"Firefox", r"火狐浏览器", r"Safari", r"Opera",
                # Office
                r"Word", r"Excel", r"PowerPoint", r"PPT", r"Outlook",
                r"OneNote", r"WPS", r"Access",
                # 开发工具
                r"VSCode", r"Visual Studio Code", r"Visual Studio",
                r"PyCharm", r"IDEA", r"IntelliJ", r"Sublime", r"Notepad\+\+",
                r"Git", r"GitHub Desktop", r"Postman",
                # 社交通讯
                r"微信", r"QQ", r"钉钉", r"飞书", r"企业微信", r"腾讯会议",
                r"Zoom", r"Teams", r"Skype", r"Discord", r"Telegram",
                # 音乐应用
                r"酷狗", r"酷狗音乐", r"网易云音乐", r"QQ音乐", r"酷我音乐",
                r"Spotify", r"Apple Music",
                # 视频应用
                r"B站", r"哔哩哔哩", r"腾讯视频", r"爱奇艺", r"优酷",
                r"芒果TV", r"抖音", r"快手", r"西瓜视频", r"YouTube",
                # 购物应用
                r"淘宝", r"京东", r"拼多多", r"支付宝", r"美团", r"饿了么",
                r"天猫", r"唯品会", r"苏宁易购",
                # 地图导航
                r"高德地图", r"百度地图", r"腾讯地图", r"Google地图",
                # 社交媒体
                r"微博", r"小红书", r"知乎", r"豆瓣", r"贴吧",
                # 游戏平台
                r"Steam", r"Epic", r"WeGame", r"Origin", r"Uplay",
                # 其他
                r"滴滴出行", r"相机", r"相册", r"日历", r"闹钟",
                r"蓝牙", r"WiFi", r"备忘录", r"便签"
            ],
            "file_path": [
                r"[a-zA-Z]:\\[\w\.\s\-\\]+",
                r"桌面", r"文档", r"下载", r"图片", r"音乐", r"视频",
                r"我的文档", r"我的桌面", r"我的下载"
            ],
            "language": [
                r"英语", r"日语", r"韩语", r"法语", r"德语", r"俄语",
                r"西班牙语", r"葡萄牙语", r"意大利语", r"阿拉伯语",
                r"中文", r"英文", r"日文", r"韩文"
            ],
            "person": [
                r"周杰伦", r"林俊杰", r"陈奕迅", r"邓紫棋", r"薛之谦",
                r"李荣浩", r"毛不易", r"华晨宇", r"张学友", r"刘德华"
            ],
            "song": [
                r"稻香", r"晴天", r"七里香", r"青花瓷", r"告白气球",
                r"夜曲", r"简单爱", r"双截棍", r"东风破", r"菊花台"
            ]
        }

    def _initialize_synonyms(self):
        """初始化同义词映射"""
        self.SYNONYMS = {
            # 动作同义词
            "打开": ["启动", "运行", "开启", "启动一下", "帮我打开", "请打开"],
            "关闭": ["关掉", "退出", "停止", "结束", "关上"],
            "播放": ["放", "听", "来一首", "唱"],
            "搜索": ["查找", "查询", "了解", "找一下", "搜一下", "检索", "百度"],

            # 应用同义词
            "酷狗音乐": ["酷狗", "kugou"],
            "网易云音乐": ["网易云", "云音乐"],
            "QQ音乐": ["qq音乐"],
            "哔哩哔哩": ["B站", "b站", "bilibili"],
            "微信": ["wx", "weixin"],

            # 功能同义词
            "天气": ["气象", "气候", "气温", "温度"],
            "新闻": ["资讯", "时事", "头条", "消息"],
            "时间": ["时刻", "钟头", "现在几点"],
            "日期": ["日子", "几号", "星期几"],

            # 问候同义词
            "你好": ["您好", "嗨", "哈喽", "hello", "hi"],
            "再见": ["拜拜", "回见", "下次见", "bye"],
            "谢谢": ["感谢", "多谢", "thanks"]
        }

    def _initialize_ml_models(self):
        """初始化机器学习模型"""
        self.intent_model = None
        self.entity_model = None
        self.use_ml = True

        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            class SimpleIntentModel:
                def __init__(self, intent_rules):
                    self.intent_rules = intent_rules
                    self.intent_examples = []
                    self.intent_list = []

                    for intent, patterns in intent_rules.items():
                        for pattern in patterns:
                            clean_pattern = re.sub(r'[.+*?^${}()|[\]\\]', '', pattern)
                            if clean_pattern:
                                self.intent_examples.append(clean_pattern)
                                self.intent_list.append(intent)

                    self.vectorizer = TfidfVectorizer()
                    if self.intent_examples:
                        self.tfidf_matrix = self.vectorizer.fit_transform(self.intent_examples)

                def predict(self, text):
                    if not self.intent_examples:
                        return None
                    text_vector = self.vectorizer.transform([text])
                    similarities = cosine_similarity(text_vector, self.tfidf_matrix)

                    intent_similarities = {}
                    for i, intent in enumerate(self.intent_list):
                        if intent not in intent_similarities or similarities[0, i] > intent_similarities[intent]:
                            intent_similarities[intent] = similarities[0, i]

                    if not intent_similarities:
                        return None

                    max_intent = max(intent_similarities, key=intent_similarities.get)
                    max_similarity = intent_similarities[max_intent]

                    if max_similarity > 0.15:
                        return max_intent
                    return None

            self.intent_model = SimpleIntentModel(self.INTENT_RULES)
            logger.info("机器学习模型初始化成功")
        except Exception as e:
            logger.error(f"初始化机器学习模型失败: {e}")
            self.use_ml = False

    def process(self, text):
        """处理文本并返回NLP结果"""
        return self._process_internal(text)

    def process_text(self, text):
        """处理文本并返回NLP结果（字典格式）"""
        try:
            intent, entities = self._process_internal(text)
            return {
                "text": self._preprocess_text(text),
                "intent": intent,
                "entities": entities,
                "sentiment": self.sentiment_analysis(text)
            }
        except Exception as e:
            logger.error(f"处理文本失败: {e}")
            return {"text": text, "intent": None, "entities": [], "sentiment": "neutral"}

    def _process_internal(self, text):
        """内部处理文本"""
        try:
            processed_text = self._preprocess_text(text)
            intent = self.recognize_intent(processed_text)
            entities = self.extract_entities(processed_text)
            return intent, entities
        except Exception as e:
            logger.error(f"处理文本失败: {e}")
            return None, []

    def _preprocess_text(self, text):
        """文本预处理"""
        text = re.sub(r"\s+", " ", text.strip())
        text = text.lower()
        # 标准化标点符号
        text = text.replace("？", "?").replace("！", "!").replace("，", ",")
        return text


    def _segment(self, text):
        """分词"""
        return list(jieba.cut(text))

    def _pos_tag(self, words):
        """词性标注"""
        return [(word, pos) for word, pos in pseg.cut(" ".join(words))]

    def recognize_intent(self, text):
        """智能意图识别"""
        # 1. 最高优先级：检测"打开+应用名"模式
        open_patterns = [
            (r"打开\s*(.+)", "open"),
            (r"启动\s*(.+)", "open"),
            (r"运行\s*(.+)", "open"),
            (r"开启\s*(.+)", "open")
        ]

        for pattern, action in open_patterns:
            match = re.search(pattern, text)
            if match:
                target = match.group(1).strip()
                # 去除语气词
                target = re.sub(r'[吧呗啊哦了呢]+$', '', target).strip()

                # 检查是否是应用
                for app_pattern in self.ENTITY_TYPES.get("app_name", []):
                    if re.search(app_pattern, target, re.IGNORECASE):
                        return "open_application"

                # 检查是否是文件夹
                folder_keywords = ["文件夹", "目录", "桌面", "文档", "下载", "图片", "音乐", "视频"]
                if any(kw in target for kw in folder_keywords):
                    return "open_folder"

                # 默认尝试打开应用
                if target and len(target) <= 20:
                    return "open_application"

        # 2. 规则匹配
        for intent, patterns in self.INTENT_RULES.items():
            for pattern in patterns:
                try:
                    if re.search(pattern, text, re.IGNORECASE):
                        return intent
                except re.error:
                    if pattern in text:
                        return intent

        # 3. 机器学习模型
        if self.use_ml and self.intent_model:
            intent = self.intent_model.predict(text)
            if intent:
                return intent

        return None

    def extract_entities(self, text):
        """实体提取"""
        entities = []

        for entity_type, patterns in self.ENTITY_TYPES.items():
            for pattern in patterns:
                try:
                    flags = re.IGNORECASE if entity_type == "app_name" else 0
                    matches = re.findall(pattern, text, flags)
                    for match in matches:
                        match_str = match.strip() if isinstance(match, str) else str(match)
                        if match_str and (entity_type, match_str) not in entities:
                            entities.append((entity_type, match_str))
                except re.error:
                    if pattern.lower() in text.lower():
                        entities.append((entity_type, pattern))

        # 提取时间表达式
        time_entities = self._extract_time_entities(text)
        entities.extend(time_entities)

        return entities

    def _extract_time_entities(self, text):
        """提取时间实体"""
        entities = []

        # 具体时间点
        time_patterns = [
            (r"(\d{1,2})[点时](\d{1,2})?分?", "time_point"),
            (r"(\d{1,2}):(\d{2})", "time_point"),
            (r"(早上|上午|中午|下午|晚上|凌晨)(\d{1,2})[点时]", "time_point")
        ]

        for pattern, entity_type in time_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    time_str = "".join(str(m) for m in match if m)
                else:
                    time_str = match
                if time_str and (entity_type, time_str) not in entities:
                    entities.append((entity_type, time_str))

        return entities

    def sentiment_analysis(self, text):
        """情感分析"""
        words = self._segment(text)
        positive_count = sum(1 for w in words if w in self.POSITIVE_WORDS)
        negative_count = sum(1 for w in words if w in self.NEGATIVE_WORDS)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"

    def get_synonyms(self, word):
        """获取同义词"""
        return self.SYNONYMS.get(word, [])

    def expand_query_with_synonyms(self, query):
        """使用同义词扩展查询"""
        words = self._segment(query)
        expanded = set(words)
        for word in words:
            expanded.update(self.get_synonyms(word))
        return " ".join(expanded)

    def levenshtein_distance(self, s1, s2):
        """计算编辑距离"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    def fuzzy_match(self, word, candidates, threshold=0.7):
        """模糊匹配"""
        best_match = None
        highest_similarity = 0

        for candidate in candidates:
            distance = self.levenshtein_distance(word, candidate)
            max_length = max(len(word), len(candidate))
            similarity = 1 - (distance / max_length) if max_length > 0 else 0

            if similarity > highest_similarity and similarity >= threshold:
                highest_similarity = similarity
                best_match = candidate

        return (best_match, highest_similarity) if best_match else None

    def extract_keywords(self, text, top_k=5):
        """提取关键词"""
        words = self._segment(text)
        # 过滤停用词和短词
        keywords = [w for w in words if w not in self.STOP_WORDS and len(w) > 1]
        # 简单的词频统计
        from collections import Counter
        word_counts = Counter(keywords)
        return word_counts.most_common(top_k)

    def parse_math_expression(self, text):
        """解析数学表达式"""
        # 中文数字转阿拉伯数字
        cn_nums = {
            '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
            '五': '5', '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
        }
        for cn, num in cn_nums.items():
            text = text.replace(cn, num)

        # 中文运算符转换
        text = text.replace('加', '+').replace('减', '-')
        text = text.replace('乘', '*').replace('乘以', '*')
        text = text.replace('除', '/').replace('除以', '/')
        text = text.replace('×', '*').replace('÷', '/')

        # 提取数学表达式
        match = re.search(r'[\d\+\-\*\/\(\)\.\s]+', text)
        if match:
            expr = match.group().strip()
            # 安全检查
            if re.match(r'^[\d\+\-\*\/\(\)\.\s]+$', expr):
                return expr
        return None

    def parse_time_expression(self, text):
        """解析时间表达式，返回datetime对象"""
        now = datetime.now()

        # 相对时间
        if "今天" in text:
            return now
        elif "明天" in text:
            return now + timedelta(days=1)
        elif "后天" in text:
            return now + timedelta(days=2)
        elif "大后天" in text:
            return now + timedelta(days=3)
        elif "昨天" in text:
            return now - timedelta(days=1)
        elif "前天" in text:
            return now - timedelta(days=2)

        # 具体时间点
        time_match = re.search(r'(\d{1,2})[点时](\d{1,2})?分?', text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0

            # 处理上午/下午
            if "下午" in text or "晚上" in text:
                if hour < 12:
                    hour += 12
            elif "凌晨" in text and hour == 12:
                hour = 0

            return now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # 相对时间（分钟/小时后）
        minute_match = re.search(r'(\d+)\s*分钟后', text)
        if minute_match:
            minutes = int(minute_match.group(1))
            return now + timedelta(minutes=minutes)

        hour_match = re.search(r'(\d+)\s*小时后', text)
        if hour_match:
            hours = int(hour_match.group(1))
            return now + timedelta(hours=hours)

        return None
