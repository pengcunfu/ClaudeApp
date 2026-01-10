"""
GitHub 仓库对话框
"""
from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QMessageBox, QHBoxLayout


class RepoDialog(QDialog):
    """GitHub 仓库对话框"""

    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("添加 GitHub 仓库")
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        self.repo_edit = QLineEdit()
        self.repo_edit.setPlaceholderText("例如: username/repo-name")
        layout.addRow("仓库名称:", self.repo_edit)

        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def validate_and_accept(self):
        """验证并接受"""
        repo_name = self.repo_edit.text().strip()
        if not repo_name:
            QMessageBox.warning(self, "警告", "仓库名称不能为空")
            return
        if "/" not in repo_name:
            QMessageBox.warning(self, "警告", "仓库名称格式应为: username/repo-name")
            return
        self.accept()

    def get_repo_name(self):
        """获取仓库名称"""
        return self.repo_edit.text().strip()
