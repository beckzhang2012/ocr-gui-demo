#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试区域OCR识别功能
验证OCR_qt类的区域识别功能是否正常工作
"""

import sys
import os
import time
from PyQt5.QtCore import QCoreApplication, QThread
from guiocr.utils.ocr_utils import OCR_qt

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_region_ocr():
    """测试区域OCR识别功能"""
    print("测试区域OCR识别功能")
    print("==================================================")
    
    # 创建Qt应用
    app = QCoreApplication(sys.argv)
    
    # 创建OCR处理器
    ocr_processor = OCR_qt()
    
    # 定义结果处理函数
    def handle_results(results):
        print(f"\n3. OCR 识别完成")
        print(f"   ✓ 识别到 {len(results)} 个文本行")
        for i, line in enumerate(results):
            print(f"   ✓ 行 {i+1}: {line[1][0]}")
        
        # 退出应用
        app.quit()
    
    # 连接结果信号
    ocr_processor.sendResult.connect(handle_results)
    
    # 选择测试图片
    test_image = "guiocr/imgs/00006737.jpg"  # 使用项目中的示例图片
    
    if not os.path.exists(test_image):
        print(f"错误: 测试图片 {test_image} 不存在")
        return
    
    print(f"1. 使用测试图片: {test_image}")
    
    # 定义测试区域
    test_regions = [(100, 100, 400, 300), (500, 100, 800, 300)]  # 两个示例区域
    print(f"2. 测试区域: {test_regions}")
    
    # 设置任务
    ocr_processor.set_task(
        img_path=test_image,
        use_angle=True,
        cls=True,
        lan="ch",
        load=True,
        regions=test_regions
    )
    
    print("\n开始OCR识别...")
    
    # 启动识别
    ocr_processor.start()
    
    # 运行Qt事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    test_region_ocr()
