from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QListWidget, QListWidgetItem, QTextEdit, 
                             QGroupBox, QFormLayout, QSpinBox, QMessageBox, QFileDialog)
from guiocr.template import TemplateManager, Template, RegionTemplate
import os

class TemplateManagerDialog(QDialog):
    """模板管理对话框"""
    
    templateApplied = QtCore.pyqtSignal(str)  # 模板应用信号
    
    def __init__(self, parent=None, template_manager: TemplateManager = None):
        super().__init__(parent)
        self.template_manager = template_manager or TemplateManager()
        self.setWindowTitle("模板管理")
        self.setMinimumSize(600, 400)
        self.current_template = None
        self.init_ui()
        self.load_templates()
        
    def init_ui(self):
        """初始化界面"""
        main_layout = QVBoxLayout(self)
        
        # 顶部布局：模板列表和操作按钮
        top_layout = QHBoxLayout()
        
        # 模板列表
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self.select_template)
        self.template_list.itemDoubleClicked.connect(self.edit_template)
        top_layout.addWidget(self.template_list, 1)
        
        # 模板操作按钮
        button_layout = QVBoxLayout()
        self.btn_add = QPushButton("新建模板")
        self.btn_add.clicked.connect(self.add_template)
        self.btn_edit = QPushButton("编辑模板")
        self.btn_edit.clicked.connect(self.edit_template)
        self.btn_delete = QPushButton("删除模板")
        self.btn_delete.clicked.connect(self.delete_template)
        self.btn_apply = QPushButton("应用模板")
        self.btn_apply.clicked.connect(self.apply_template)
        self.btn_import = QPushButton("导入模板")
        self.btn_import.clicked.connect(self.import_templates)
        self.btn_export = QPushButton("导出模板")
        self.btn_export.clicked.connect(self.export_templates)
        
        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_edit)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(self.btn_import)
        button_layout.addWidget(self.btn_export)
        button_layout.addStretch()
        
        top_layout.addLayout(button_layout)
        main_layout.addLayout(top_layout)
        
        # 模板详情
        detail_group = QGroupBox("模板详情")
        detail_layout = QFormLayout()
        
        self.template_name_edit = QLineEdit()
        self.template_desc_edit = QTextEdit()
        self.template_desc_edit.setMaximumHeight(80)
        
        detail_layout.addRow("模板名称:", self.template_name_edit)
        detail_layout.addRow("模板描述:", self.template_desc_edit)
        
        detail_group.setLayout(detail_layout)
        main_layout.addWidget(detail_group)
        
        # 区域列表
        region_group = QGroupBox("区域列表")
        region_layout = QVBoxLayout()
        
        self.region_list = QListWidget()
        region_layout.addWidget(self.region_list)
        
        region_button_layout = QHBoxLayout()
        self.btn_add_region = QPushButton("添加区域")
        self.btn_add_region.clicked.connect(self.add_region)
        self.btn_edit_region = QPushButton("编辑区域")
        self.btn_edit_region.clicked.connect(self.edit_region)
        self.btn_delete_region = QPushButton("删除区域")
        self.btn_delete_region.clicked.connect(self.delete_region)
        
        region_button_layout.addWidget(self.btn_add_region)
        region_button_layout.addWidget(self.btn_edit_region)
        region_button_layout.addWidget(self.btn_delete_region)
        region_layout.addLayout(region_button_layout)
        
        region_group.setLayout(region_layout)
        main_layout.addWidget(region_group)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        self.btn_ok = QPushButton("确定")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_ok)
        bottom_layout.addWidget(self.btn_cancel)
        main_layout.addLayout(bottom_layout)
        
    def load_templates(self):
        """加载模板列表"""
        self.template_list.clear()
        for template in self.template_manager.get_templates():
            item = QListWidgetItem(template.name)
            item.setData(QtCore.Qt.UserRole, template)
            self.template_list.addItem(item)
            
    def select_template(self, item):
        """选择模板"""
        self.current_template = item.data(QtCore.Qt.UserRole)
        self.template_name_edit.setText(self.current_template.name)
        self.template_desc_edit.setText(self.current_template.description)
        self.load_regions()
        
    def load_regions(self):
        """加载区域列表"""
        self.region_list.clear()
        if self.current_template:
            for region in self.current_template.regions:
                item = QListWidgetItem(f"{region.name} ({region.x}, {region.y}, {region.width}, {region.height})")
                item.setData(QtCore.Qt.UserRole, region)
                self.region_list.addItem(item)
                
    def add_template(self):
        """添加新模板"""
        template_name, ok = QtWidgets.QInputDialog.getText(self, "新建模板", "请输入模板名称:")
        if ok and template_name:
            if self.template_manager.get_template(template_name):
                QMessageBox.warning(self, "警告", "模板名称已存在")
                return
            
            template = Template(name=template_name)
            self.template_manager.add_template(template)
            self.load_templates()
            
    def edit_template(self):
        """编辑模板"""
        if not self.current_template:
            QMessageBox.warning(self, "警告", "请先选择一个模板")
            return
            
        new_name = self.template_name_edit.text().strip()
        if not new_name:
            QMessageBox.warning(self, "警告", "模板名称不能为空")
            return
            
        # 检查名称是否冲突
        existing = self.template_manager.get_template(new_name)
        if existing and existing != self.current_template:
            QMessageBox.warning(self, "警告", "模板名称已存在")
            return
            
        self.current_template.name = new_name
        self.current_template.description = self.template_desc_edit.toPlainText()
        self.load_templates()
        
    def delete_template(self):
        """删除模板"""
        if not self.current_template:
            QMessageBox.warning(self, "警告", "请先选择一个模板")
            return
            
        reply = QMessageBox.question(self, "确认删除", f"确定要删除模板 '{self.current_template.name}' 吗?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.template_manager.remove_template(self.current_template.name)
            self.current_template = None
            self.template_name_edit.clear()
            self.template_desc_edit.clear()
            self.region_list.clear()
            self.load_templates()
            
    def apply_template(self):
        """应用模板"""
        if not self.current_template:
            QMessageBox.warning(self, "警告", "请先选择一个模板")
            return
            
        self.templateApplied.emit(self.current_template.name)
        self.accept()
        
    def add_region(self):
        """添加区域"""
        if not self.current_template:
            QMessageBox.warning(self, "警告", "请先选择一个模板")
            return
            
        # 简单的区域添加对话框
        from PyQt5.QtWidgets import QDialog, QFormLayout, QSpinBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加区域")
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        name_edit.setText(f"区域{len(self.current_template.regions)+1}")
        
        x_spin = QSpinBox()
        x_spin.setRange(0, 10000)
        y_spin = QSpinBox()
        y_spin.setRange(0, 10000)
        width_spin = QSpinBox()
        width_spin.setRange(1, 10000)
        width_spin.setValue(200)
        height_spin = QSpinBox()
        height_spin.setRange(1, 10000)
        height_spin.setValue(100)
        
        layout.addRow("区域名称:", name_edit)
        layout.addRow("X坐标:", x_spin)
        layout.addRow("Y坐标:", y_spin)
        layout.addRow("宽度:", width_spin)
        layout.addRow("高度:", height_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            region = RegionTemplate(
                name=name_edit.text(),
                x=x_spin.value(),
                y=y_spin.value(),
                width=width_spin.value(),
                height=height_spin.value()
            )
            self.current_template.regions.append(region)
            self.load_regions()
            
    def edit_region(self):
        """编辑区域"""
        if not self.current_template:
            QMessageBox.warning(self, "警告", "请先选择一个模板")
            return
            
        selected_items = self.region_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个区域")
            return
            
        region = selected_items[0].data(QtCore.Qt.UserRole)
        
        from PyQt5.QtWidgets import QDialog, QFormLayout, QSpinBox, QDialogButtonBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑区域")
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        name_edit.setText(region.name)
        
        x_spin = QSpinBox()
        x_spin.setRange(0, 10000)
        x_spin.setValue(region.x)
        y_spin = QSpinBox()
        y_spin.setRange(0, 10000)
        y_spin.setValue(region.y)
        width_spin = QSpinBox()
        width_spin.setRange(1, 10000)
        width_spin.setValue(region.width)
        height_spin = QSpinBox()
        height_spin.setRange(1, 10000)
        height_spin.setValue(region.height)
        
        layout.addRow("区域名称:", name_edit)
        layout.addRow("X坐标:", x_spin)
        layout.addRow("Y坐标:", y_spin)
        layout.addRow("宽度:", width_spin)
        layout.addRow("高度:", height_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            region.name = name_edit.text()
            region.x = x_spin.value()
            region.y = y_spin.value()
            region.width = width_spin.value()
            region.height = height_spin.value()
            self.load_regions()
            
    def delete_region(self):
        """删除区域"""
        selected_items = self.region_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "警告", "请先选择一个区域")
            return
            
        region = selected_items[0].data(QtCore.Qt.UserRole)
        reply = QMessageBox.question(self, "确认删除", f"确定要删除区域 '{region.name}' 吗?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.current_template.regions.remove(region)
            self.load_regions()
            
    def import_templates(self):
        """导入模板"""
        file_path, _ = QFileDialog.getOpenFileName(self, "导入模板", "", "JSON文件 (*.json)")
        if file_path:
            if self.template_manager.import_templates(file_path):
                QMessageBox.information(self, "成功", "模板导入成功")
                self.load_templates()
            else:
                QMessageBox.error(self, "错误", "模板导入失败")
                
    def export_templates(self):
        """导出模板"""
        file_path, _ = QFileDialog.getSaveFileName(self, "导出模板", "", "JSON文件 (*.json)")
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            if self.template_manager.export_templates(file_path):
                QMessageBox.information(self, "成功", "模板导出成功")
            else:
                QMessageBox.error(self, "错误", "模板导出失败")
                
    def get_template_manager(self) -> TemplateManager:
        """获取模板管理器"""
        return self.template_manager