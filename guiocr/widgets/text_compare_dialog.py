# -*- coding:utf-8 -*-
"""
文本对比查看对话框
支持对比原始OCR结果和纠错后的结果，支持一键应用或还原

Author: ZhangSY
Created time:2025/05/20
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                             QPushButton, QLabel, QSplitter)
from guiocr.utils.text_postprocessor import TextPostProcessor

class TextCompareDialog(QDialog):
    """文本对比查看对话框"""
    
    def __init__(self, original_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文本对比查看")
        self.setMinimumSize(800, 500)
        self.original_text = original_text
        self.processed_text = ""
        self.postprocessor = TextPostProcessor()
        self.init_ui()
        self.process_text()
    
    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        
        # 标题标签
        title_layout = QHBoxLayout()
        original_label = QLabel("原始文本")
        original_label.setAlignment(QtCore.Qt.AlignCenter)
        title_layout.addWidget(original_label)
        
        processed_label = QLabel("纠错后文本")
        processed_label.setAlignment(QtCore.Qt.AlignCenter)
        title_layout.addWidget(processed_label)
        main_layout.addLayout(title_layout)
        
        # 文本对比区域
        self.splitter = QSplitter(QtCore.Qt.Horizontal)
        
        self.original_edit = QTextEdit()
        self.original_edit.setReadOnly(True)
        self.original_edit.setPlaceholderText("原始OCR识别结果")
        self.splitter.addWidget(self.original_edit)
        
        self.processed_edit = QTextEdit()
        self.processed_edit.setPlaceholderText("纠错后的文本")
        self.splitter.addWidget(self.processed_edit)
        
        self.splitter.setSizes([400, 400])
        main_layout.addWidget(self.splitter)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.process_btn = QPushButton("重新处理")
        self.process_btn.clicked.connect(self.process_text)
        btn_layout.addWidget(self.process_btn)
        
        self.apply_btn = QPushButton("应用纠错结果")
        self.apply_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.apply_btn)
        
        self.reset_btn = QPushButton("还原原始结果")
        self.reset_btn.clicked.connect(self.reset_text)
        btn_layout.addWidget(self.reset_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(btn_layout)
    
    def process_text(self):
        """处理文本并显示结果"""
        self.processed_text = self.postprocessor.process(self.original_text)
        self.original_edit.setPlainText(self.original_text)
        self.processed_edit.setPlainText(self.processed_text)
    
    def reset_text(self):
        """还原为原始文本"""
        self.processed_edit.setPlainText(self.original_text)
        self.processed_text = self.original_text
    
    def get_processed_text(self):
        """获取处理后的文本"""
        return self.processed_edit.toPlainText()
