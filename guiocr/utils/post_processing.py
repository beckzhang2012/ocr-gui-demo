# -*- coding:utf-8 -*-
"""
OCR识别结果智能后处理模块
包含自动分段、去噪、常见错别字纠正、自定义词典等功能
"""
import re
import json
import os

class OCRPostProcessor:
    """OCR识别结果智能后处理类"""
    
    def __init__(self):
        self.default_corrections = {
            "青晰": "清晰",
            "象": "像",
            "即然": "既然",
            "在次": "再次",
            "已后": "以后",
            "原則": "原则",
            "按排": "安排",
            "拔打": "拨打",
            "部份": "部分",
            "车箱": "车厢"
        }
        self.custom_corrections = {}
        self.load_custom_dictionary()
    
    def load_custom_dictionary(self, dict_path="custom_corrections.json"):
        """加载自定义纠错词典"""
        if os.path.exists(dict_path):
            try:
                with open(dict_path, "r", encoding="utf-8") as f:
                    self.custom_corrections = json.load(f)
            except:
                self.custom_corrections = {}
    
    def save_custom_dictionary(self, dict_path="custom_corrections.json"):
        """保存自定义纠错词典"""
        with open(dict_path, "w", encoding="utf-8") as f:
            json.dump(self.custom_corrections, f, ensure_ascii=False, indent=4)
    
    def add_custom_correction(self, original, corrected):
        """添加自定义纠错条目"""
        self.custom_corrections[original] = corrected
        self.save_custom_dictionary()
    
    def remove_custom_correction(self, original):
        """移除自定义纠错条目"""
        if original in self.custom_corrections:
            del self.custom_corrections[original]
            self.save_custom_dictionary()
    
    def get_custom_corrections(self):
        """获取自定义纠错词典"""
        return self.custom_corrections
    
    def clean_text(self, text):
        """文本去噪：移除多余空格、特殊字符等"""
        # 移除连续空格
        text = re.sub(r'\s+', ' ', text).strip()
        # 移除特殊字符，但保留中文、英文、数字、标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？；：,.!?;:()（）《》<>【】\[\]"\'\-]', '', text)
        return text
    
    def correct_text(self, text):
        """错别字纠正：先应用默认纠错，再应用自定义纠错"""
        # 应用默认纠错
        for original, corrected in self.default_corrections.items():
            text = text.replace(original, corrected)
        # 应用自定义纠错
        for original, corrected in self.custom_corrections.items():
            text = text.replace(original, corrected)
        return text
    
    def auto_segment(self, lines):
        """自动分段：根据文本内容和逻辑关系进行分段"""
        paragraphs = []
        current_paragraph = ""
        
        for line in lines:
            if not line:
                continue
            
            # 简单的分段逻辑：根据句号、感叹号、问号等结束符分段
            sentences = re.split(r'([。！？])', line)
            for sentence in sentences:
                if sentence:
                    current_paragraph += sentence
                    # 如果遇到结束符，结束当前段落
                    if sentence in ['。', '！', '？']:
                        if current_paragraph.strip():
                            paragraphs.append(current_paragraph.strip())
                            current_paragraph = ""
        
        # 添加最后一个段落
        if current_paragraph.strip():
            paragraphs.append(current_paragraph.strip())
        
        return paragraphs
    
    def process(self, ocr_result):
        """完整后处理流程：处理OCR识别结果"""
        processed_result = []
        
        for line in ocr_result:
            if line:
                box = line[0]
                text = line[1][0]
                confidence = line[1][1]
                
                # 去噪
                cleaned_text = self.clean_text(text)
                # 纠错
                corrected_text = self.correct_text(cleaned_text)
                
                processed_result.append({
                    "box": box,
                    "original_text": text,
                    "cleaned_text": cleaned_text,
                    "corrected_text": corrected_text,
                    "confidence": confidence
                })
        
        return processed_result
    
    def get_full_text(self, processed_result, text_type="corrected"):
        """获取完整文本"""
        full_text = ""
        for item in processed_result:
            if text_type == "original":
                full_text += item["original_text"] + "\n"
            elif text_type == "cleaned":
                full_text += item["cleaned_text"] + "\n"
            else:
                full_text += item["corrected_text"] + "\n"
        return full_text.strip()
    
    def batch_process(self, batch_results):
        """批量处理多个OCR结果"""
        processed_batch = {}
        for img_path, data in batch_results.items():
            processed = self.process(data["result"])
            processed_batch[img_path] = {
                "result": processed,
                "confidence": data["confidence"]
            }
        return processed_batch
