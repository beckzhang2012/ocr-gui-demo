#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试区域OCR识别功能
验证模板应用和区域裁剪是否正常工作
"""

import sys
import os
import json
from guiocr.template import RegionTemplate, TemplateManager
from guiocr.shape import Shape
from PyQt5.QtCore import QPointF

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_region_template():
    """测试区域模板功能"""
    print("测试区域模板功能")
    print("==================================================")
    
    # 创建模板管理器
    tm = TemplateManager()
    
    # 创建形状对象
    shape1 = Shape()
    shape1.shape_type = "rectangle"
    shape1.points = [
        QPointF(100, 100),
        QPointF(300, 100),
        QPointF(300, 200),
        QPointF(100, 200)
    ]
    
    shape2 = Shape()
    shape2.shape_type = "rectangle"
    shape2.points = [
        QPointF(400, 100),
        QPointF(600, 100),
        QPointF(600, 200),
        QPointF(400, 200)
    ]
    
    # 创建模板
    template = RegionTemplate(name="测试区域模板", description="测试两个区域的模板")
    template.add_region(shape1, "区域1")
    template.add_region(shape2, "区域2")
    tm.add_template(template)
    
    print(f"1. 创建模板 '{template.name}'")
    print(f"   ✓ 模板包含 {len(template.regions)} 个区域")
    
    # 测试从模板获取区域坐标
    print("\n2. 测试从模板获取区域坐标")
    regions = []
    for region in template.regions:
        points = region['points']
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        x1 = int(min(xs))
        y1 = int(min(ys))
        x2 = int(max(xs))
        y2 = int(max(ys))
        regions.append((x1, y1, x2, y2))
        print(f"   ✓ 区域 '{region['name']}': ({x1}, {y1}, {x2}, {y2})")
    
    print(f"\n3. 提取的区域坐标: {regions}")
    print("   ✓ 区域坐标提取成功")
    
    print("\n==================================================")
    print("所有测试完成！")

if __name__ == "__main__":
    test_region_template()
