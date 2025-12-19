# -*- coding: utf-8 -*-
"""
模板管理对话框
用于管理区域模板的增删改查
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QPushButton, QLabel, QLineEdit, QTextEdit, 
                             QMessageBox, QFileDialog)
from guiocr.template import RegionTemplate, TemplateManager


class TemplateManagerDialog(QDialog):
    """模板管理对话框"""
    
    templateApplied = QtCore.pyqtSignal(str)  # 模板应用信号
    
    def __init__(self, template_manager: TemplateManager, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.setWindowTitle("模板管理")
        self.setModal(True)
        self.resize(600, 400)
        self.current_template = None
        
        self.setup_ui()
        self.load_templates()
    
    def setup_ui(self):
        """设置界面布局"""
        main_layout = QVBoxLayout(self)
        
        # 模板列表和控制按钮
        list_layout = QHBoxLayout()
        
        self.template_list = QListWidget()
        self.template_list.itemSelectionChanged.connect(self.on_template_selected)
        list_layout.addWidget(self.template_list)
        
        button_layout = QVBoxLayout()
        self.btn_add = QPushButton("添加")
        self.btn_edit = QPushButton("编辑")
        self.btn_delete = QPushButton("删除")
        self.btn_apply = QPushButton("应用")
        self.btn_import = QPushButton("导入")
        self.btn_export = QPushButton("导出")
        
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_edit)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(self.btn_import)
        button_layout.addWidget(self.btn_export)
        button_layout.addStretch()
        
        list_layout.addLayout(button_layout)
        main_layout.addLayout(list_layout)
        
        # 模板详情
        detail_layout = QVBoxLayout()
        
        name_layout = QHBoxLayout()
        name_label = QLabel("模板名称:")
        self.name_edit = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        detail_layout.addLayout(name_layout)
        
        desc_layout = QHBoxLayout()
        desc_label = QLabel("描述:")
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        detail_layout.addLayout(desc_layout)
        
        main_layout.addLayout(detail_layout)
        
        # 连接按钮信号
        self.btn_add.clicked.connect(self.add_template)
        self.btn_edit.clicked.connect(self.edit_template)
        self.btn_delete.clicked.connect(self.delete_template)
        self.btn_apply.clicked.connect(self.apply_template)
        self.btn_import.clicked.connect(self.import_template)
        self.btn_export.clicked.connect(self.export_template)
        
        # 禁用初始不可用的按钮
        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)
        self.btn_apply.setEnabled(False)
        self.btn_export.setEnabled(False)
    
    def load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        for template in self.template_manager.get_all_templates():
            item = QtWidgets.QListWidgetItem(template.name)
            item.setData(QtCore.Qt.UserRole, template)
            self.template_list.addItem(item)
    
    def on_template_selected(self):
        """选择模板时更新详情"""
        if self.template_list.selectedItems():
            item = self.template_list.selectedItems()[0]
            self.current_template = item.data(QtCore.Qt.UserRole)
            self.name_edit.setText(self.current_template.name)
            self.desc_edit.setPlainText(self.current_template.description)
            
            self.btn_edit.setEnabled(True)
            self.btn_delete.setEnabled(True)
            self.btn_apply.setEnabled(True)
            self.btn_export.setEnabled(True)
        else:
            self.current_template = None
            self.name_edit.clear()
            self.desc_edit.clear()
            
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)
            self.btn_apply.setEnabled(False)
            self.btn_export.setEnabled(False)
    
    def add_template(self):
        """添加新模板"""
        name, ok = QtWidgets.QInputDialog.getText(self, "添加模板", "请输入模板名称:")
        if ok and name.strip():
            if self.template_manager.get_template(name.strip()):
                QMessageBox.warning(self, "警告", "模板名称已存在")
                return
            
            template = RegionTemplate(name=name.strip())
            self.template_manager.add_template(template)
            self.load_templates()
    
    def edit_template(self):
        """编辑当前选中的模板"""
        if not self.current_template:
            return
        
        new_name = self.name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(self, "警告", "模板名称不能为空")
            return
        
        existing = self.template_manager.get_template(new_name)
        if existing and existing != self.current_template:
            QMessageBox.warning(self, "警告", "模板名称已存在")
            return
        
        self.current_template.name = new_name
        self.current_template.description = self.desc_edit.toPlainText()
        self.load_templates()
    
    def delete_template(self):
        """删除当前选中的模板"""
        if not self.current_template:
            return
        
        reply = QMessageBox.question(self, "确认删除", f"确定要删除模板 '{self.current_template.name}' 吗?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.template_manager.remove_template(self.current_template.name)
            self.current_template = None
            self.load_templates()
            self.name_edit.clear()
            self.desc_edit.clear()
    
    def apply_template(self):
        """应用当前选中的模板"""
        if not self.current_template:
            return
        
        self.templateApplied.emit(self.current_template.name)
        self.accept()
    
    def import_template(self):
        """导入模板文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入模板", "", "JSON Files (*.json)"
        )
        
        if file_path:
            if self.template_manager.import_template(file_path):
                QMessageBox.information(self, "成功", "模板导入成功")
                self.load_templates()
            else:
                QMessageBox.error(self, "错误", "模板导入失败")
    
    def export_template(self):
        """导出当前选中的模板"""
        if not self.current_template:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出模板", self.current_template.name + ".json", "JSON Files (*.json)"
        )
        
        if file_path:
            if self.template_manager.export_template(self.current_template.name, file_path):
                QMessageBox.information(self, "成功", "模板导出成功")
            else:
                QMessageBox.error(self, "错误", "模板导出失败")