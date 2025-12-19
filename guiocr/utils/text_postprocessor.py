# -*- coding:utf-8 -*-
"""
文本智能后处理模块
实现OCR识别结果的自动分段、去噪、常见错别字纠正等功能
支持用户自定义纠错词典

Author: ZhangSY
Created time:2025/05/20
"""
import re
import json
import os

class TextPostProcessor:
    """文本智能后处理类"""
    
    def __init__(self, dict_path=None):
        self.default_corrections = {
            # 常见错别字映射
            "机率": "几率",
            "部份": "部分",
            "身分": "身份",
            "藉口": "借口",
            "其它": "其他",
            "身分证": "身份证",
            "再接再励": "再接再厉",
            "按装": "安装",
            "甘败下风": "甘拜下风",
            "一股作气": "一鼓作气",
            "自抱自弃": "自暴自弃"
        }
        self.user_corrections = {}
        self.dict_path = dict_path or os.path.join(os.path.dirname(__file__), "correction_dict.json")
        self.load_user_dict()
    
    def load_user_dict(self):
        """加载用户自定义纠错词典"""
        if os.path.exists(self.dict_path):
            try:
                with open(self.dict_path, 'r', encoding='utf-8') as f:
                    self.user_corrections = json.load(f)
            except:
                self.user_corrections = {}
    
    def save_user_dict(self):
        """保存用户自定义纠错词典"""
        with open(self.dict_path, 'w', encoding='utf-8') as f:
            json.dump(self.user_corrections, f, ensure_ascii=False, indent=4)
    
    def add_correction(self, error, correct):
        """添加纠错词条"""
        self.user_corrections[error] = correct
        self.save_user_dict()
    
    def remove_correction(self, error):
        """移除纠错词条"""
        if error in self.user_corrections:
            del self.user_corrections[error]
            self.save_user_dict()
    
    def get_all_corrections(self):
        """获取所有纠错词条"""
        all_corrections = {}
        all_corrections.update(self.default_corrections)
        all_corrections.update(self.user_corrections)
        return all_corrections
    
    def denoise_text(self, text):
        """文本去噪：移除多余空格、特殊字符等"""
        # 移除连续的空格
        text = re.sub(r'\s+', ' ', text)
        # 移除首尾空格
        text = text.strip()
        # 移除常见的噪声字符
        noise_chars = ['\u0000-\u001F', '\u007F-\u009F', '\\r', '\\n']
        for char in noise_chars:
            text = re.sub(char, '', text)
        return text
    
    def correct_text(self, text):
        """错别字纠正"""
        corrections = self.get_all_corrections()
        for error, correct in corrections.items():
            text = text.replace(error, correct)
        return text
    
    def auto_segment(self, text):
        """自动分段：根据标点符号和内容结构分段"""
        # 在句号、感叹号、问号后添加换行
        text = re.sub(r'([。！？])\s*', r'\1\n', text)
        # 在多个换行符处保持一个换行
        text = re.sub(r'\n+', '\n', text)
        return text
    
    def process(self, text):
        """完整处理流程：去噪 -> 纠错 -> 分段"""
        text = self.denoise_text(text)
        text = self.correct_text(text)
        text = self.auto_segment(text)
        return text
    
    def batch_process(self, text_list):
        """批量处理文本列表"""
        return [self.process(text) for text in text_list]
