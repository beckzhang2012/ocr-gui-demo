#!/usr/bin/env python3
"""测试模板功能的核心部分"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from guiocr.template import RegionTemplate, TemplateManager
from guiocr.shape import Shape
from PyQt5.QtCore import QPointF

print("测试区域模板功能")
print("=" * 50)

# 测试 1: 创建模板
print("\n1. 测试创建模板")
manager = TemplateManager()

# 创建一些测试形状
shapes = []
shape1 = Shape(label="区域1", shape_type="rectangle")
shape1.addPoint(QPointF(100, 100))
shape1.addPoint(QPointF(200, 200))
shapes.append(shape1)

shape2 = Shape(label="区域2", shape_type="rectangle")
shape2.addPoint(QPointF(300, 300))
shape2.addPoint(QPointF(400, 400))
shapes.append(shape2)

# 保存为模板
manager.save_template("测试模板1", shapes)
print(f"  ✓ 创建模板 '测试模板1'，包含 {len(shapes)} 个区域")

# 测试 2: 列出模板
print("\n2. 测试列出模板")
templates = manager.get_templates()
print(f"  ✓ 找到 {len(templates)} 个模板")
for template in templates:
    print(f"    - {template.name}: {len(template.regions)} 个区域")

# 测试 3: 导出模板
print("\n3. 测试导出模板")
export_path = "test_template.json"
if manager.export_template(templates[0].name, export_path):
    print(f"  ✓ 模板导出成功: {export_path}")
    print(f"  ✓ 导出文件大小: {os.path.getsize(export_path)} 字节")

# 测试 4: 导入模板
print("\n4. 测试导入模板")
if manager.import_template(export_path):
    print(f"  ✓ 模板导入成功")
    print(f"  ✓ 导入后模板总数: {len(manager.get_templates())}")

# 测试 5: 删除模板
print("\n5. 测试删除模板")
if manager.delete_template("测试模板1"):
    print(f"  ✓ 删除模板 '测试模板1' 成功")
    print(f"  ✓ 删除后模板总数: {len(manager.get_templates())}")

# 清理测试文件
if os.path.exists(export_path):
    os.remove(export_path)

print("\n" + "=" * 50)
print("所有测试完成！")
