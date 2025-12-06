#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习模型模块 - 用于训练和使用NLP模型
"""

import os
import sys
import logging
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from transformers import BertTokenizer, BertForSequenceClassification, BertForTokenClassification
import torch
from torch.utils.data import Dataset, DataLoader

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.config import NLPConfig
from src.nlp.nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)

class IntentRecognitionModel:
    """意图识别模型类"""
    
    def __init__(self):
        """初始化意图识别模型"""
        self.model_path = NLPConfig.INTENT_MODEL_PATH
        self.vectorizer = None
        self.model = None
        self.intent_labels = None
        
        # 检查模型文件是否存在
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.train_model()
    
    def load_data(self):
        """加载训练数据"""
        # 模拟训练数据
        texts = [
            "今天天气怎么样", "北京的天气", "上海明天天气预报",
            "新闻有什么", "最新新闻", "科技新闻",
            "帮我计算1+2", "3乘以5等于多少", "10减5加3",
            "现在几点了", "时间", "今天日期",
            "讲个笑话", "笑话", "搞笑的事",
            "翻译我爱你", "translate hello", "把中文翻译成英文",
            "播放音乐", "放首歌", "音乐",
            "你好", "嗨", "哈喽",
            "你叫什么名字", "名字", "你的名称",
            "退出", "关闭", "结束"
        ]
        
        intents = [
            "weather", "weather", "weather",
            "news", "news", "news",
            "calculator", "calculator", "calculator",
            "time", "time", "time",
            "joke", "joke", "joke",
            "translation", "translation", "translation",
            "music", "music", "music",
            "greeting", "greeting", "greeting",
            "name", "name", "name",
            "exit", "exit", "exit"
        ]
        
        return texts, intents
    
    def train_model(self):
        """训练意图识别模型"""
        logger.info("开始训练意图识别模型")
        
        # 加载数据
        texts, intents = self.load_data()
        
        # 创建意图标签映射
        unique_intents = list(set(intents))
        self.intent_labels = {intent: idx for idx, intent in enumerate(unique_intents)}
        intents_idx = [self.intent_labels[intent] for intent in intents]
        
        # 文本向量化
        self.vectorizer = TfidfVectorizer(max_features=1000)
        X = self.vectorizer.fit_transform(texts)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(X, intents_idx, test_size=0.2, random_state=42)
        
        # 训练模型
        self.model = MultinomialNB()
        self.model.fit(X_train, y_train)
        
        # 评估模型
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"意图识别模型准确率: {accuracy:.2f}")
        logger.info(f"分类报告: {classification_report(y_test, y_pred)}")
        
        # 保存模型
        self.save_model()
        
        logger.info("意图识别模型训练完成")
    
    def predict(self, text):
        """预测文本的意图"""
        if self.model is None or self.vectorizer is None:
            return None
        
        try:
            # 文本向量化
            X = self.vectorizer.transform([text])
            
            # 预测
            y_pred = self.model.predict(X)[0]
            
            # 转换为意图标签
            for intent, idx in self.intent_labels.items():
                if idx == y_pred:
                    return intent
            
            return None
        except Exception as e:
            logger.error(f"意图识别预测失败: {e}")
            return None
    
    def save_model(self):
        """保存模型"""
        # 确保模型目录存在
        model_dir = os.path.dirname(self.model_path)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        # 保存模型和向量化器
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'intent_labels': self.intent_labels
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"意图识别模型已保存到 {self.model_path}")
    
    def load_model(self):
        """加载模型"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.vectorizer = model_data['vectorizer']
            self.model = model_data['model']
            self.intent_labels = model_data['intent_labels']
            
            logger.info(f"意图识别模型已从 {self.model_path} 加载")
        except Exception as e:
            logger.error(f"加载意图识别模型失败: {e}")
            self.train_model()

class EntityExtractionModel:
    """实体提取模型类"""
    
    def __init__(self):
        """初始化实体提取模型"""
        self.model_path = NLPConfig.ENTITY_MODEL_PATH
        self.bert_model = None
        self.tokenizer = None
        self.entity_labels = None
        
        # 检查模型文件是否存在
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.train_model()
    
    def load_data(self):
        """加载训练数据"""
        # 模拟训练数据
        texts = [
            "今天北京天气怎么样",
            "上海明天天气预报",
            "广州的气温是多少",
            "计算1+2",
            "3乘以5等于多少",
            "10减5加3"
        ]
        
        entities = [
            [0, 0, 0, 1, 1, 0, 0, 0],  # 北京
            [0, 1, 1, 0, 0, 0, 0, 0],  # 上海
            [0, 1, 1, 0, 0, 0, 0, 0],  # 广州
            [0, 2, 0, 2, 0, 2],        # 1, +, 2
            [0, 2, 0, 0, 2, 0, 0, 0],   # 3, 5
            [0, 2, 0, 2, 0, 2]          # 10, 5, 3
        ]
        
        return texts, entities
    
    def train_model(self):
        """训练实体提取模型"""
        logger.info("开始训练实体提取模型")
        
        # 加载数据
        texts, entities = self.load_data()
        
        # 初始化BERT tokenizer
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
        
        # 创建实体标签映射
        self.entity_labels = {0: 'O', 1: 'B-LOC', 2: 'B-NUM'}
        
        # 准备训练数据
        tokenized_inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        labels = torch.tensor(entities, dtype=torch.long)
        
        # 初始化BERT模型
        self.bert_model = BertForTokenClassification.from_pretrained(
            'bert-base-chinese', 
            num_labels=len(self.entity_labels)
        )
        
        # 训练模型
        optimizer = torch.optim.AdamW(self.bert_model.parameters(), lr=5e-5)
        
        self.bert_model.train()
        for epoch in range(3):  # 简单训练3个epoch
            outputs = self.bert_model(**tokenized_inputs, labels=labels)
            loss = outputs.loss
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            logger.info(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")
        
        # 保存模型
        self.save_model()
        
        logger.info("实体提取模型训练完成")
    
    def extract_entities(self, text):
        """提取文本中的实体"""
        if self.bert_model is None or self.tokenizer is None:
            return []
        
        try:
            #  tokenize输入文本
            inputs = self.tokenizer(text, return_tensors='pt')
            
            # 预测
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
            
            # 获取预测结果
            predictions = torch.argmax(outputs.logits, dim=2)
            
            # 转换为实体标签
            entities = []
            tokens = self.tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
            
            for i, pred in enumerate(predictions[0]):
                if self.entity_labels[pred.item()] != 'O':
                    entities.append((tokens[i], self.entity_labels[pred.item()]))
            
            return entities
        except Exception as e:
            logger.error(f"实体提取失败: {e}")
            return []
    
    def save_model(self):
        """保存模型"""
        # 确保模型目录存在
        model_dir = os.path.dirname(self.model_path)
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        # 保存模型
        model_data = {
            'bert_model': self.bert_model,
            'tokenizer': self.tokenizer,
            'entity_labels': self.entity_labels
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"实体提取模型已保存到 {self.model_path}")
    
    def load_model(self):
        """加载模型"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.bert_model = model_data['bert_model']
            self.tokenizer = model_data['tokenizer']
            self.entity_labels = model_data['entity_labels']
            
            logger.info(f"实体提取模型已从 {self.model_path} 加载")
        except Exception as e:
            logger.error(f"加载实体提取模型失败: {e}")
            self.train_model()

if __name__ == "__main__":
    # 测试意图识别模型
    logger.info("测试意图识别模型")
    intent_model = IntentRecognitionModel()
    test_texts = ["今天天气怎么样", "帮我计算1+2", "退出"]
    for text in test_texts:
        intent = intent_model.predict(text)
        logger.info(f"文本: {text}, 意图: {intent}")
    
    # 测试实体提取模型
    logger.info("测试实体提取模型")
    entity_model = EntityExtractionModel()
    test_text = "今天北京天气怎么样"
    entities = entity_model.extract_entities(test_text)
    logger.info(f"文本: {test_text}, 实体: {entities}")
