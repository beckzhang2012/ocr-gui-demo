# -*- coding:utf-8 -*-
"""
批量OCR处理模块
支持多图片批量识别、进度报告、异常处理和结果统计

Author: ZhangSY
Created time:2024/08/20
"""
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from guiocr.utils.ocr_utils import OCR_qt
import os
import glob

class BatchOCRWorker(QObject):
    """批量OCR处理工作线程类"""
    # 信号定义
    progress_updated = pyqtSignal(int, int, str)  # 当前进度, 总任务数, 当前文件名
    batch_complete = pyqtSignal(list, dict)       # 识别结果列表, 统计信息
    error_occurred = pyqtSignal(str, str)         # 错误信息, 文件名
    
    def __init__(self, parent=None):
        super(BatchOCRWorker, self).__init__(parent)
        self.image_files = []
        self.language = "ch"
        self.ocr_processor = None
        
    def set_task(self, image_files, language="ch"):
        """设置批量处理任务"""
        self.image_files = image_files
        self.language = language
        
    def start(self):
        """开始批量处理"""
        self.ocr_processor = OCR_qt()
        
        # 加载模型
        self.ocr_processor.set_task(load=True, lan=self.language)
        
        results = []
        stats = {
            "total": len(self.image_files),
            "success": 0,
            "failed": 0,
            "unsupported": 0,
            "error_files": []
        }
        
        for idx, img_path in enumerate(self.image_files):
            current_progress = idx + 1
            self.progress_updated.emit(current_progress, len(self.image_files), os.path.basename(img_path))
            
            try:
                # 执行OCR识别
                result = self.ocr_processor.ocr(img_path, lan=self.language)
                
                # 保存结果
                results.append({
                    "filename": os.path.basename(img_path),
                    "full_path": img_path,
                    "result": self.ocr_processor.result,
                    "status": "success"
                })
                stats["success"] += 1
                
            except Exception as e:
                error_msg = str(e)
                self.error_occurred.emit(error_msg, img_path)
                
                results.append({
                    "filename": os.path.basename(img_path),
                    "full_path": img_path,
                    "result": None,
                    "status": "failed",
                    "error": error_msg
                })
                stats["failed"] += 1
                stats["error_files"].append(img_path)
        
        self.batch_complete.emit(results, stats)
        
    @staticmethod
    def get_supported_image_formats():
        """获取支持的图片格式"""
        return ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff", "*.tif"]
        
    @staticmethod
    def collect_image_files(folder_path):
        """从文件夹中收集所有支持的图片文件"""
        image_files = []
        for ext in BatchOCRWorker.get_supported_image_formats():
            image_files.extend(glob.glob(os.path.join(folder_path, ext), recursive=False))
        return sorted(image_files)
    
    @staticmethod
    def find_image_files(folder_path):
        """查找文件夹中的图片文件（别名方法）"""
        return BatchOCRWorker.collect_image_files(folder_path)
