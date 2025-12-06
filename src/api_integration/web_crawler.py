#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络爬虫模块
用于替代API调用，直接从网页获取天气、新闻等信息
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import logging
import re
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.nlp.nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)

class WebCrawler:
    """网络爬虫类，用于获取天气、新闻等信息"""
    
    def __init__(self):
        """初始化爬虫"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 初始化NLP处理器用于模糊搜索
        self.nlp_processor = NLPProcessor()
    
    def get_weather(self, city, time=None):
        """获取天气信息
        Args:
            city: 城市名称
            time: 时间信息（可选，如"明天"、"后天"、"周一"等）
        Returns:
            天气信息字符串
        """
        try:
            # 使用中国天气网获取天气信息
            url = f'http://www.weather.com.cn/weather/{self._get_city_code(city)}.shtml'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取天气信息
            weather_info = soup.find(class_='c7d')
            if not weather_info:
                return f"抱歉，无法获取{city}的天气信息"
            
            # 解析时间参数
            day_index = 0  # 默认今天
            if time:
                time = time.lower()
                if "明天" in time or "次日" in time:
                    day_index = 1
                elif "后天" in time or "后日" in time:
                    day_index = 2
                elif "大后天" in time:
                    day_index = 3
                elif "周" in time or "星期" in time:
                    # 简单处理星期查询，这里假设返回的是未来7天的天气
                    # 实际应用中需要更复杂的日期计算
                    pass
            
            # 获取指定天数的天气
            days = weather_info.find_all('li')
            if day_index < len(days):
                target_day = days[day_index]
                
                # 提取日期信息（从h1标签获取）
                date_tag = target_day.find('h1')
                date = date_tag.text.strip() if date_tag else ""
                
                # 提取天气信息
                wea_tags = target_day.find_all(class_='wea')
                day_wea = wea_tags[0].text.strip() if wea_tags else ""
                night_wea = wea_tags[1].text.strip() if len(wea_tags) > 1 else day_wea
                
                # 提取温度信息
                tem_tag = target_day.find(class_='tem')
                temp = tem_tag.text.strip() if tem_tag else ""
                
                # 提取风力信息
                win_tag = target_day.find(class_='win')
                wind = win_tag.text.strip() if win_tag else ""
                
                # 构建天气信息
                if date and day_wea and temp and wind:
                    # 根据时间参数调整返回信息
                    time_str = "今日" if day_index == 0 else time if time else f"{day_index}天后"
                    return f"{city}{time_str}{date}天气：{day_wea}，温度：{temp}，风力：{wind}"
                else:
                    return f"抱歉，无法解析{city}{time}的天气信息"
            else:
                return f"抱歉，无法获取{city}{time}的天气信息"
            
        except Exception as e:
            logger.error(f"获取天气信息失败: {e}")
            if time:
                return f"抱歉，获取{city}{time}的天气信息时出错"
            else:
                return f"抱歉，获取{city}的天气信息时出错"
    
    def _get_city_code(self, city):
        """获取城市代码（中国天气网）"""
        # 简单的城市代码映射
        city_codes = {
            '北京': '101010100',
            '上海': '101020100',
            '广州': '101280101',
            '深圳': '101280601',
            '杭州': '101210101',
            '成都': '101270101',
            '重庆': '101040100',
            '西安': '101110101',
            '武汉': '101200101',
            '南京': '101190101',
            '天津': '101030100',
            '苏州': '101190401',
            '郑州': '101180101',
            '长沙': '101250101',
            '沈阳': '101070101',
            '青岛': '101120201',
            '济南': '101120101',
            '大连': '101070201',
            '宁波': '101210401',
            '南宁': '101300101',
            '厦门': '101230201',
            '福州': '101230101',
            '长春': '101060101',
            '哈尔滨': '101050101',
            '合肥': '101220101',
            '南昌': '101240101',
            '昆明': '101290101',
            '贵阳': '101260101',
            '太原': '101100101',
            '石家庄': '101090101',
            '兰州': '101160101',
            '乌鲁木齐': '101130101',
            '呼和浩特': '101080101',
            '西宁': '101150101',
            '银川': '101170101',
            '拉萨': '101230201',
            '海口': '101310101',
            '三亚': '101310201',
            '香港': '101320101',
            '澳门': '101330101',
            '台北': '101340101'
        }
        return city_codes.get(city, '101010100')  # 默认北京
    
    def get_news(self):
        """获取最新新闻
        Returns:
            新闻列表
        """
        try:
            # 使用新浪新闻获取最新资讯
            url = 'https://news.sina.com.cn/china/'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取新闻标题和链接
            news_list = []
            # 查找主要新闻区域
            news_area = soup.find(class_='news-item')
            if news_area:
                items = news_area.find_all('li')[:5]  # 获取前5条新闻
                for item in items:
                    a_tag = item.find('a')
                    if a_tag:
                        title = a_tag.text.strip()
                        link = a_tag.get('href')
                        news_list.append(f"{title}")
            
            if not news_list:
                # 尝试其他新闻区域
                news_items = soup.find_all('a', class_='news-link')[:5]
                for item in news_items:
                    title = item.text.strip()
                    if title:
                        news_list.append(title)
            
            if news_list:
                return "\n".join([f"{i+1}. {news}" for i, news in enumerate(news_list)])
            else:
                return "抱歉，无法获取最新新闻"
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            return "抱歉，获取新闻时出错"
    
    def search_map(self, location):
        """搜索地图位置
        Args:
            location: 位置名称
        Returns:
            地图信息
        """
        try:
            # 使用百度地图搜索
            url = f'https://api.map.baidu.com/place/v2/search?query={location}&region=全国&output=html&ak=demo'
            return f"已为您搜索{location}的地图信息，您可以访问以下链接查看：\n{url}"
        except Exception as e:
            logger.error(f"地图搜索失败: {e}")
            return f"抱歉，搜索{location}的地图信息时出错"
    
    def search_internet(self, query, fuzzy=True, top_k=3):
        """搜索互联网
        Args:
            query: 搜索关键词
            fuzzy: 是否启用模糊搜索，默认为True
            top_k: 返回的搜索结果数量，默认为3
        Returns:
            搜索结果摘要
        """
        try:
            # 如果启用模糊搜索，扩展查询
            original_query = query
            if fuzzy:
                query = self.nlp_processor.expand_query_with_synonyms(query)
                logger.info(f"原始查询: {original_query}, 扩展后查询: {query}")
            
            # 使用Bing搜索
            url = f'https://cn.bing.com/search?q={query}'
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取搜索结果
            search_items = soup.find_all('li', class_='b_algo')
            
            # 处理搜索结果
            results = []
            for item in search_items[:10]:  # 获取前10条结果进行排序
                h2 = item.find('h2')
                if h2:
                    title = h2.text.strip()
                    desc_tag = item.find(class_='b_caption')
                    desc = desc_tag.find('p').text.strip() if desc_tag and desc_tag.find('p') else ""
                    
                    # 计算结果与原始查询的相关性
                    relevance = self._calculate_relevance(title + " " + desc, original_query)
                    
                    results.append({
                        'title': title,
                        'description': desc,
                        'relevance': relevance
                    })
            
            # 按相关性排序结果
            results.sort(key=lambda x: x['relevance'], reverse=True)
            
            # 格式化输出
            formatted_results = []
            for i, result in enumerate(results[:top_k]):
                formatted_results.append(f"{i+1}. {result['title']}\n{result['description']}")
            
            if formatted_results:
                return "\n\n".join(formatted_results)
            else:
                return f"抱歉，未找到关于{original_query}的搜索结果"
        except Exception as e:
            logger.error(f"互联网搜索失败: {e}")
            return f"抱歉，搜索{original_query}时出错"
    
    def _calculate_relevance(self, text, query):
        """计算文本与查询的相关性
        Args:
            text: 要评估的文本
            query: 查询关键词
        Returns:
            相关性分数（0-1）
        """
        # 使用NLPProcessor的模糊匹配功能计算相关性
        query_words = self.nlp_processor._segment(query)
        text_words = self.nlp_processor._segment(text)
        
        # 计算匹配的单词数量
        match_count = 0
        for q_word in query_words:
            for t_word in text_words:
                distance = self.nlp_processor.levenshtein_distance(q_word, t_word)
                max_length = max(len(q_word), len(t_word))
                similarity = 1 - (distance / max_length)
                
                if similarity > 0.7:  # 匹配阈值
                    match_count += 1
                    break
        
        # 计算相关性分数
        if not query_words:
            return 0
            
        # 考虑查询单词的覆盖率和文本长度
        coverage_score = match_count / len(query_words)
        # 较短的文本如果匹配度高，相关性更高
        length_penalty = 1 / (1 + len(text_words) / 100)
        
        return coverage_score * (0.8 + 0.2 * length_penalty)
    
    def get_current_time(self):
        """获取当前时间
        Returns:
            当前时间字符串
        """
        now = datetime.now()
        return f"当前时间是{now.strftime('%Y年%m月%d日 %H:%M:%S')}"
    
    def get_current_date(self):
        """获取当前日期
        Returns:
            当前日期字符串
        """
        today = datetime.now()
        return f"今天是{today.strftime('%Y年%m月%d日')}，星期{today.strftime('%A')}"
