"""
原始 JSON 配置标签页
"""
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QMessageBox
)
from PySide6.QtGui import QFont

from ..widgets.json_highlighter import JsonHighlighter


class RawConfigTab(QWidget):
    """原始 JSON 配置标签页"""

    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.highlighter = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)

        # 按钮栏
        button_layout = QHBoxLayout()
        reload_btn = QPushButton("重新加载")
        save_btn = QPushButton("保存配置")
        format_btn = QPushButton("格式化JSON")

        reload_btn.clicked.connect(self.reload_config)
        save_btn.clicked.connect(self.save_config)
        format_btn.clicked.connect(self.format_json)

        button_layout.addWidget(reload_btn)
        button_layout.addWidget(format_btn)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 10))
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        # 应用语法高亮
        self.highlighter = JsonHighlighter(self.text_edit.document())

        layout.addWidget(self.text_edit)

    def load_data(self, config_data):
        """加载数据"""
        json_str = json.dumps(config_data, indent=2, ensure_ascii=False)
        self.text_edit.setPlainText(json_str)

    def reload_config(self):
        """重新加载配置"""
        self.parent_window.load_config()

    def save_config(self):
        """保存配置"""
        try:
            json_text = self.text_edit.toPlainText()
            config_data = json.loads(json_text)

            self.parent_window.set_config_data(config_data)
            self.parent_window.save_config_to_file()

            # 刷新所有视图
            self.parent_window.refresh_all_views()

            QMessageBox.information(self, "成功", "配置已保存!")
            self.parent_window.statusBar().showMessage("配置已保存")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON 格式错误:\n{str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置失败:\n{str(e)}")

    def format_json(self):
        """格式化 JSON"""
        try:
            json_text = self.text_edit.toPlainText()
            data = json.loads(json_text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.text_edit.setPlainText(formatted)
            self.parent_window.statusBar().showMessage("JSON已格式化")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON 格式错误:\n{str(e)}")
