# -*- coding: utf-8 -*-
"""
区域模板功能模块
用于管理和应用用户定义的OCR识别区域模板
"""

import json
import os
from dataclasses import dataclass, field
from typing import List, Dict, Any
from PyQt5.QtCore import QRectF, QPointF
from .shape import Shape


@dataclass
class RegionTemplate:
    """单个区域模板的数据结构"""
    name: str
    regions: List[Dict[str, Any]] = field(default_factory=list)
    description: str = ""
    
    def add_region(self, shape: Shape, region_name: str = "") -> None:
        """从Shape对象添加区域"""
        region = {
            "name": region_name,
            "shape_type": shape.shape_type,
            "points": [(p.x(), p.y()) for p in shape.points]
        }
        self.regions.append(region)
    
    def get_shapes(self) -> List[Shape]:
        """将模板转换为Shape对象列表"""
        shapes = []
        for region in self.regions:
            shape = Shape()
            shape.shape_type = region["shape_type"]
            shape.points = [QPointF(x, y) for x, y in region["points"]]
            shapes.append(shape)
        return shapes
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "regions": self.regions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegionTemplate":
        """从字典创建RegionTemplate对象"""
        template = cls(
            name=data.get("name", "Untitled Template"),
            description=data.get("description", "")
        )
        template.regions = data.get("regions", [])
        return template


class TemplateManager:
    """模板管理器，负责模板的存储、加载和管理"""
    
    def __init__(self):
        self.templates: List[RegionTemplate] = []
    
    def add_template(self, template: RegionTemplate) -> None:
        """添加新模板"""
        self.templates.append(template)
    
    def remove_template(self, template_name: str) -> bool:
        """移除指定名称的模板"""
        for i, template in enumerate(self.templates):
            if template.name == template_name:
                del self.templates[i]
                return True
        return False
    
    def get_template(self, template_name: str) -> RegionTemplate:
        """获取指定名称的模板"""
        for template in self.templates:
            if template.name == template_name:
                return template
        return None
    
    def get_all_templates(self) -> List[RegionTemplate]:
        """获取所有模板"""
        return self.templates
    
    def get_templates(self) -> List[RegionTemplate]:
        """获取所有模板（别名方法）"""
        return self.get_all_templates()
    
    def delete_template(self, template_name: str) -> bool:
        """删除指定名称的模板（别名方法）"""
        return self.remove_template(template_name)
    
    def save_template(self, template_name: str, shapes: List[Shape], description: str = "") -> bool:
        """从形状列表保存为新模板"""
        template = RegionTemplate(name=template_name, description=description)
        for shape in shapes:
            template.add_region(shape)
        self.add_template(template)
        return True
    
    def save_templates(self, file_path: str) -> bool:
        """保存所有模板到文件"""
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                data = [template.to_dict() for template in self.templates]
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False
    
    def load_templates(self, file_path: str) -> bool:
        """从文件加载模板"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.templates = [RegionTemplate.from_dict(item) for item in data]
            return True
        except Exception as e:
            print(f"加载模板失败: {e}")
            return False
    
    def export_template(self, template_name: str, file_path: str) -> bool:
        """导出单个模板到文件"""
        template = self.get_template(template_name)
        if not template:
            return False
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(template.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"导出模板失败: {e}")
            return False
    
    def import_template(self, file_path: str) -> bool:
        """从文件导入单个模板"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                template = RegionTemplate.from_dict(data)
                self.add_template(template)
            return True
        except Exception as e:
            print(f"导入模板失败: {e}")
            return False