import json
import os
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any

@dataclass
class RegionTemplate:
    """单个区域模板的定义"""
    name: str
    x: int
    y: int
    width: int
    height: int
    description: str = ""
    ocr_language: str = "ch"

@dataclass
class Template:
    """完整模板的定义"""
    name: str
    description: str = ""
    regions: List[RegionTemplate] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

class TemplateManager:
    """模板管理类，负责模板的增删改查、导入导出"""
    
    def __init__(self):
        self.templates: List[Template] = []
        
    def add_template(self, template: Template) -> None:
        """添加新模板"""
        self.templates.append(template)
        
    def remove_template(self, template_name: str) -> bool:
        """删除模板，返回是否成功"""
        for idx, template in enumerate(self.templates):
            if template.name == template_name:
                del self.templates[idx]
                return True
        return False
        
    def get_template(self, template_name: str) -> Template:
        """获取模板"""
        for template in self.templates:
            if template.name == template_name:
                return template
        return None
        
    def get_templates(self) -> List[Template]:
        """获取所有模板"""
        return self.templates
        
    def save_template(self, template: Template, file_path: str) -> bool:
        """保存单个模板到文件"""
        try:
            template_data = asdict(template)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False
            
    def load_template(self, file_path: str) -> Template:
        """从文件加载单个模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            regions = []
            for region_data in template_data.get('regions', []):
                regions.append(RegionTemplate(**region_data))
            
            template = Template(
                name=template_data['name'],
                description=template_data.get('description', ''),
                regions=regions,
                created_at=template_data.get('created_at', ''),
                updated_at=template_data.get('updated_at', '')
            )
            
            return template
        except Exception as e:
            print(f"加载模板失败: {e}")
            return None
            
    def export_templates(self, file_path: str) -> bool:
        """导出所有模板到单个文件"""
        try:
            templates_data = []
            for template in self.templates:
                templates_data.append(asdict(template))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"导出模板失败: {e}")
            return False
            
    def import_templates(self, file_path: str) -> bool:
        """从文件导入模板"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                templates_data = json.load(f)
            
            for template_data in templates_data:
                regions = []
                for region_data in template_data.get('regions', []):
                    regions.append(RegionTemplate(**region_data))
                
                template = Template(
                    name=template_data['name'],
                    description=template_data.get('description', ''),
                    regions=regions,
                    created_at=template_data.get('created_at', ''),
                    updated_at=template_data.get('updated_at', '')
                )
                
                # 检查是否已存在同名模板
                existing = self.get_template(template.name)
                if not existing:
                    self.add_template(template)
            
            return True
        except Exception as e:
            print(f"导入模板失败: {e}")
            return False