from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, 
    QLineEdit, QLabel, QMessageBox, QGridLayout
)
from PyQt5.QtCore import Qt

class DictionaryManagerDialog(QDialog):
    """自定义词典管理对话框"""
    
    def __init__(self, post_processor, parent=None):
        super().__init__(parent)
        self.post_processor = post_processor
        self.setWindowTitle("自定义词典管理")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.initUI()
        self.loadDictionary()
    
    def initUI(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 词典条目列表
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        # 输入区域
        input_layout = QGridLayout()
        
        input_layout.addWidget(QLabel("错误词:"), 0, 0)
        self.error_input = QLineEdit()
        input_layout.addWidget(self.error_input, 0, 1)
        
        input_layout.addWidget(QLabel("正确词:"), 1, 0)
        self.correct_input = QLineEdit()
        input_layout.addWidget(self.correct_input, 1, 1)
        
        layout.addLayout(input_layout)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加")
        self.add_btn.clicked.connect(self.addEntry)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("编辑")
        self.edit_btn.clicked.connect(self.editEntry)
        button_layout.addWidget(self.edit_btn)
        
        self.remove_btn = QPushButton("删除")
        self.remove_btn.clicked.connect(self.removeEntry)
        button_layout.addWidget(self.remove_btn)
        
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.saveDictionary)
        button_layout.addWidget(self.save_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def loadDictionary(self):
        """加载词典条目到列表"""
        self.list_widget.clear()
        for error, correct in self.post_processor.custom_dict.items():
            self.list_widget.addItem(f"{error} → {correct}")
    
    def addEntry(self):
        """添加新的词典条目"""
        error = self.error_input.text().strip()
        correct = self.correct_input.text().strip()
        
        if not error or not correct:
            QMessageBox.warning(self, "警告", "请输入完整的错误词和正确词")
            return
        
        if error in self.post_processor.custom_dict:
            QMessageBox.warning(self, "警告", "该错误词已存在于词典中")
            return
        
        self.post_processor.add_custom_word(error, correct)
        self.loadDictionary()
        self.error_input.clear()
        self.correct_input.clear()
    
    def editEntry(self):
        """编辑选中的词典条目"""
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要编辑的条目")
            return
        
        item_text = current_item.text()
        if "→" in item_text:
            error, correct = item_text.split("→", 1)
            error = error.strip()
            correct = correct.strip()
            
            self.error_input.setText(error)
            self.correct_input.setText(correct)
            
            # 先移除旧条目
            del self.post_processor.custom_dict[error]
            self.loadDictionary()
    
    def removeEntry(self):
        """删除选中的词典条目"""
        current_item = self.list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请选择要删除的条目")
            return
        
        item_text = current_item.text()
        if "→" in item_text:
            error = item_text.split("→", 1)[0].strip()
            
            if error in self.post_processor.custom_dict:
                del self.post_processor.custom_dict[error]
                self.loadDictionary()
    
    def saveDictionary(self):
        """保存词典到文件"""
        self.post_processor.save_custom_dict()
        QMessageBox.information(self, "信息", "词典已保存")
