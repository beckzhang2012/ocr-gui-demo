# -*- coding:utf-8 -*-
"""
纠错词典管理对话框
支持用户添加、删除、编辑自定义纠错词条

Author: ZhangSY
Created time:2025/05/20
"""
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QPushButton, QLineEdit, QLabel, QMessageBox)
from guiocr.utils.text_postprocessor import TextPostProcessor

class CorrectionDictDialog(QDialog):
    """纠错词典管理对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("纠错词典管理")
        self.setMinimumSize(500, 400)
        self.postprocessor = TextPostProcessor()
        self.init_ui()
        self.load_dict_items()
    
    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        
        # 输入区域
        input_layout = QHBoxLayout()
        
        self.error_edit = QLineEdit()
        self.error_edit.setPlaceholderText("错误词")
        input_layout.addWidget(self.error_edit)
        
        arrow_label = QLabel("→")
        arrow_label.setAlignment(QtCore.Qt.AlignCenter)
        input_layout.addWidget(arrow_label)
        
        self.correct_edit = QLineEdit()
        self.correct_edit.setPlaceholderText("正确词")
        input_layout.addWidget(self.correct_edit)
        
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self.add_entry)
        input_layout.addWidget(self.add_btn)
        
        main_layout.addLayout(input_layout)
        
        # 词典列表
        self.dict_list = QListWidget()
        main_layout.addWidget(self.dict_list)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        self.remove_btn = QPushButton("删除选中")
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("清空所有")
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(btn_layout)
    
    def load_dict_items(self):
        """加载词典条目到列表"""
        self.dict_list.clear()
        corrections = self.postprocessor.get_all_corrections()
        for error, correct in corrections.items():
            item_text = f"{error} → {correct}"
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(QtCore.Qt.UserRole, (error, correct))
            self.dict_list.addItem(item)
    
    def add_entry(self):
        """添加新的纠错条目"""
        error = self.error_edit.text().strip()
        correct = self.correct_edit.text().strip()
        
        if not error or not correct:
            QMessageBox.warning(self, "警告", "请输入错误词和正确词")
            return
        
        if error == correct:
            QMessageBox.warning(self, "警告", "错误词和正确词不能相同")
            return
        
        self.postprocessor.add_correction(error, correct)
        self.load_dict_items()
        self.error_edit.clear()
        self.correct_edit.clear()
    
    def remove_selected(self):
        """删除选中的条目"""
        selected_items = self.dict_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请选择要删除的条目")
            return
        
        for item in selected_items:
            error, _ = item.data(QtCore.Qt.UserRole)
            self.postprocessor.remove_correction(error)
        
        self.load_dict_items()
    
    def clear_all(self):
        """清空所有用户自定义条目"""
        reply = QMessageBox.question(self, "确认", "确定要清空所有自定义纠错条目吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.postprocessor.user_corrections.clear()
            self.postprocessor.save_user_dict()
            self.load_dict_items()
