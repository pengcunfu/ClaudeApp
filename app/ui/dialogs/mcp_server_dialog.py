"""
MCP 服务器配置对话框
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QGroupBox, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView, QHBoxLayout
)
from PySide6.QtCore import Qt


class MCPServerDialog(QDialog):
    """MCP 服务器配置对话框"""

    def __init__(self, parent, name="", config=None):
        super().__init__(parent)
        self.name = name
        self.config = config or {}
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("MCP 服务器配置")
        self.setMinimumWidth(600)

        layout = QFormLayout(self)

        # 服务器名称
        self.name_edit = QLineEdit()
        layout.addRow("服务器名称:", self.name_edit)

        # 命令
        self.command_edit = QLineEdit()
        command_btn = QPushButton("浏览...")
        command_btn.clicked.connect(self.browse_command)
        cmd_layout = QHBoxLayout()
        cmd_layout.addWidget(self.command_edit)
        cmd_layout.addWidget(command_btn)
        layout.addRow("命令:", cmd_layout)

        # 参数
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText('用空格分隔参数,例如: --host localhost --port 3306')
        layout.addRow("参数:", self.args_edit)

        # 环境变量
        env_group = QGroupBox("环境变量 (可选)")
        env_layout = QVBoxLayout(env_group)

        self.env_table = QTableWidget()
        self.env_table.setColumnCount(2)
        self.env_table.setHorizontalHeaderLabels(["变量名", "值"])
        self.env_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.env_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        env_layout.addWidget(self.env_table)

        env_btn_layout = QHBoxLayout()
        add_env_btn = QPushButton("添加变量")
        remove_env_btn = QPushButton("删除变量")
        add_env_btn.clicked.connect(self.add_env_var)
        remove_env_btn.clicked.connect(self.remove_env_var)
        env_btn_layout.addWidget(add_env_btn)
        env_btn_layout.addWidget(remove_env_btn)
        env_btn_layout.addStretch()
        env_layout.addLayout(env_btn_layout)

        layout.addRow(env_group)

        # 按钮
        button_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.validate_and_accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)

    def load_data(self):
        """加载数据"""
        if self.config:
            self.name_edit.setText(self.name)
            self.command_edit.setText(self.config.get("command", ""))

            args = self.config.get("args", [])
            self.args_edit.setText(" ".join(args))

            env = self.config.get("env", {})
            for key, value in env.items():
                self.add_env_row(key, value)

    def browse_command(self):
        """浏览可执行文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择可执行文件",
            str(Path.home()),
            "可执行文件 (*.exe *.bat *.cmd);;所有文件 (*.*)"
        )
        if file_path:
            self.command_edit.setText(file_path)

    def add_env_var(self):
        """添加环境变量行"""
        self.add_env_row("", "")
        # 选中新行
        row = self.env_table.rowCount() - 1
        self.env_table.selectRow(row)

    def add_env_row(self, key, value):
        """添加环境变量行"""
        row = self.env_table.rowCount()
        self.env_table.insertRow(row)
        self.env_table.setItem(row, 0, QTableWidgetItem(key))
        self.env_table.setItem(row, 1, QTableWidgetItem(value))

    def remove_env_var(self):
        """删除环境变量"""
        selected_items = self.env_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            self.env_table.removeRow(row)

    def validate_and_accept(self):
        """验证并接受"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "服务器名称不能为空")
            return

        command = self.command_edit.text().strip()
        if not command:
            QMessageBox.warning(self, "警告", "命令不能为空")
            return

        self.accept()

    def get_server_data(self):
        """获取服务器数据"""
        name = self.name_edit.text().strip()
        command = self.command_edit.text().strip()

        # 解析参数
        args_text = self.args_edit.text().strip()
        args = []
        if args_text:
            import shlex
            try:
                args = shlex.split(args_text)
            except:
                args = args_text.split()

        # 获取环境变量
        env_vars = {}
        for row in range(self.env_table.rowCount()):
            key_item = self.env_table.item(row, 0)
            value_item = self.env_table.item(row, 1)

            if key_item and value_item:
                key = key_item.text().strip()
                value = value_item.text().strip()
                if key:
                    env_vars[key] = value

        return {
            "name": name,
            "command": command,
            "args": args,
            "env_vars": env_vars
        }
